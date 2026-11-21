#!/usr/bin/env bash
#
# Flashback Database of a physical standby database (tasks/standby_flashback.yml).
# Environment (task): ORACLE_HOME, ORACLE_SID, WANTED (YES|NO), DB_UNIQUE_NAME, RETRIES, DELAY,
#                     PRIMARY_CI, ORADB_STANDBY_PW (log switch on the primary database)
# Output: a line 'CHANGED: ...' when flashback_on was changed, 'UNCHANGED: ...' otherwise.
set -u
set -o pipefail
sql() {
  "${ORACLE_HOME}/bin/sqlplus" -S -L /nolog <<EOF
connect / as sysdba
whenever sqlerror exit failure
set heading off feedback off pagesize 0 linesize 200
$1
EOF
}
# dgmgrl returns 0 for failed commands => check the output
dg() {
  local out
  out=$("${ORACLE_HOME}/bin/dgmgrl" -silent / "$1" 2>&1) || return 1
  echo "${out}"
  if echo "${out}" | grep -qE '^(Error:|ORA-|Syntax error)' ; then return 1 ; fi
}

current=$(sql "select flashback_on from v\$database;" | tr -d '[:space:]')
if [ -z "${current}" ] ; then
  echo "flashback_on of v\$database could not be read"
  exit 1
fi
if [ "${current}" = "${WANTED}" ] ; then
  echo "UNCHANGED: flashback_on=${current}"
  exit 0
fi

# broker configuration: Redo Apply is controlled by the broker (intended state of the member)
apply_stopped=0
broker=0
if show=$(dg "show database '${DB_UNIQUE_NAME}'") && echo "${show}" | grep -q 'Intended State:' ; then
  broker=1
  echo "${show}" | grep -q 'Intended State: *APPLY-ON' && apply_wanted=1 || apply_wanted=0
else
  # without broker: Redo Apply is running, when MRP0 exists
  [ "$(sql "select count(*) from v\$dataguard_process where name like 'MRP%';" | tr -d '[:space:]')" != "0" ] \
    && apply_wanted=1 || apply_wanted=0
fi

# query on the primary database (log switch), only for FLASHBACK ON
pri() {
  "${ORACLE_HOME}/bin/sqlplus" -S -L /nolog <<EOF
connect sys/"${ORADB_STANDBY_PW}"@${PRIMARY_CI} as sysdba
whenever sqlerror exit failure
set heading off feedback off pagesize 0 linesize 200
$1
EOF
}
# Log switch on the primary and wait until the standby has applied this log (Redo Apply is running)
wait_for_primary_redo() {
  local targets t thr seq n all attempt=1
  if ! targets=$(pri "alter system archive log current;
select thread#||':'||max(sequence#) from v\$log_history where resetlogs_change# = (select resetlogs_change# from v\$database) group by thread#;") ; then
    echo "WARNING: log switch on the primary database failed: ${targets}"
    return 0
  fi
  targets=$(echo "${targets}" | tr -d '[:blank:]' | grep -E '^[0-9]+:[0-9]+$' | tr '\n' ' ')
  [ -n "${targets}" ] || { echo "WARNING: no log history of the primary database"; return 0; }
  echo "Log switch on the primary database, last log (thread:sequence): ${targets}"
  while : ; do
    all=1
    for t in ${targets} ; do
      thr=${t%%:*}
      seq=${t##*:}
      n=$(sql "select count(*) from v\$archived_log where thread# = ${thr} and sequence# >= ${seq} and applied = 'YES' and resetlogs_change# = (select resetlogs_change# from v\$database);" | tr -d '[:space:]')
      [ "${n:-0}" != "0" ] || all=0
    done
    if [ "${all}" = "1" ] ; then
      echo "Redo of the log switch applied on the standby database"
      return 0
    fi
    if [ "${attempt}" -ge "${RETRIES}" ] ; then
      echo "WARNING: redo of the log switch not applied after $((attempt * DELAY)) seconds"
      return 0
    fi
    attempt=$((attempt + 1))
    sleep "${DELAY}"
  done
}
if [ "${WANTED}" = "YES" ] && [ "${apply_wanted}" = "1" ] && [ -n "${PRIMARY_CI}" ] ; then
  wait_for_primary_redo
fi

stop_apply() {
  [ "${apply_wanted}" = "1" ] || return 0
  if [ "${broker}" = "1" ] ; then
    dg "edit database '${DB_UNIQUE_NAME}' set state='apply-off'" > /dev/null || return 1
  else
    sql "alter database recover managed standby database cancel;" > /dev/null || return 1
  fi
  apply_stopped=1
  echo "Redo Apply stopped"
}
start_apply() {
  [ "${apply_stopped}" = "1" ] || return 0
  if [ "${broker}" = "1" ] ; then
    dg "edit database '${DB_UNIQUE_NAME}' set state='apply-on'" > /dev/null || return 1
  else
    sql "alter database recover managed standby database disconnect from session;" > /dev/null || return 1
  fi
  apply_stopped=0
  echo "Redo Apply started"
}
# Redo Apply is started again in every case (also after an error or exit)
trap 'start_apply || echo "WARNING: Redo Apply could not be started"' EXIT

if [ "${WANTED}" = "YES" ] ; then statement="alter database flashback on;" ; else statement="alter database flashback off;" ; fi
attempt=1
while : ; do
  stop_apply || { echo "Redo Apply could not be stopped"; exit 1; }
  if out=$(sql "${statement}" 2>&1) ; then rc=0 ; else rc=1 ; fi
  start_apply || echo "WARNING: Redo Apply could not be started"
  if [ "${rc}" = "0" ] ; then
    echo "CHANGED: flashback_on ${current} => ${WANTED}"
    exit 0
  fi
  if echo "${out}" | grep -q 'ORA-38788' && [ "${attempt}" -lt "${RETRIES}" ] ; then
    echo "ORA-38788: more redo has to be applied (attempt ${attempt}/${RETRIES}), next attempt in ${DELAY} seconds"
    attempt=$((attempt + 1))
    sleep "${DELAY}"
    continue
  fi
  echo "${out}"
  exit 1
done
