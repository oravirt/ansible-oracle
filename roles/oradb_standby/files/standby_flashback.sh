#!/usr/bin/env bash
#
# Flashback Database of a physical standby database (tasks/standby_flashback.yml).
#
# Environment (task):
#   ORACLE_HOME, ORACLE_SID   local standby database
#   WANTED                    YES | NO (flashback_on)
#   DB_UNIQUE_NAME            db_unique_name of the standby (Data Guard Broker)
#   RETRIES, DELAY            attempts and seconds between two attempts
#   PRIMARY_CI                connect identifier of the primary database (empty: no log switch)
#   ORADB_STANDBY_PW          SYS password for the log switch on the primary database
#
# Output: a line 'CHANGED: ...' when flashback_on was changed, 'UNCHANGED: ...' otherwise.
#
# Steps (main at the end of the file):
#   1. check_flashback_state     nothing to do when the state is the wanted state
#   2. detect_apply_mode         broker or manual Redo Apply, is Redo Apply wanted
#   3. wait_for_primary_redo     FLASHBACK ON: log switch on the primary, wait until applied
#   4. change_flashback          stop Redo Apply, ALTER DATABASE FLASHBACK ON/OFF, start Redo Apply
set -u
set -o pipefail

# state of the script
current=""          # flashback_on of v$database
broker=0            # 1: Redo Apply is controlled by the Data Guard Broker
apply_wanted=0      # 1: Redo Apply is wanted (running / intended state APPLY-ON)
apply_stopped=0     # 1: Redo Apply was stopped by this script

# ---------------------------------------------------------------------------
# SQL*Plus / DGMGRL
# ---------------------------------------------------------------------------

# SQL on the local (standby) database: sql "<statements>"
sql() {
  "${ORACLE_HOME}/bin/sqlplus" -S -L /nolog <<EOF
connect / as sysdba
whenever sqlerror exit failure
set heading off feedback off pagesize 0 linesize 200
$1
EOF
}

# SQL on the primary database: pri "<statements>"
pri() {
  "${ORACLE_HOME}/bin/sqlplus" -S -L /nolog <<EOF
connect sys/"${ORADB_STANDBY_PW}"@${PRIMARY_CI} as sysdba
whenever sqlerror exit failure
set heading off feedback off pagesize 0 linesize 200
$1
EOF
}

# dgmgrl command: dg "<command>"
# dgmgrl returns 0 for failed commands => check the output
dg() {
  local out
  out=$("${ORACLE_HOME}/bin/dgmgrl" -silent / "$1" 2>&1) || return 1
  echo "${out}"
  if echo "${out}" | grep -qE '^(Error:|ORA-|Syntax error)' ; then return 1 ; fi
}

# ---------------------------------------------------------------------------
# 1. current state
# ---------------------------------------------------------------------------

check_flashback_state() {
  current=$(sql "select flashback_on from v\$database;" | tr -d '[:space:]')
  if [ -z "${current}" ] ; then
    echo "flashback_on of v\$database could not be read"
    exit 1
  fi
  if [ "${current}" = "${WANTED}" ] ; then
    echo "UNCHANGED: flashback_on=${current}"
    exit 0
  fi
}

# ---------------------------------------------------------------------------
# 2. Redo Apply: broker or manual
# ---------------------------------------------------------------------------

# broker configuration: Redo Apply is controlled by the broker (intended state of the member)
# without broker: Redo Apply is running, when MRP0 exists
detect_apply_mode() {
  local show
  if show=$(dg "show database '${DB_UNIQUE_NAME}'") && echo "${show}" | grep -q 'Intended State:' ; then
    broker=1
    echo "${show}" | grep -q 'Intended State: *APPLY-ON' && apply_wanted=1 || apply_wanted=0
  else
    [ "$(sql "select count(*) from v\$dataguard_process where name like 'MRP%';" | tr -d '[:space:]')" != "0" ] \
      && apply_wanted=1 || apply_wanted=0
  fi
}

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

# ---------------------------------------------------------------------------
# 3. FLASHBACK ON: redo of the primary has to be applied (ORA-38788)
# ---------------------------------------------------------------------------

# Log switch on the primary, result: last log of each thread as 'thread:sequence' (blank separated)
primary_log_switch() {
  local out
  if ! out=$(pri "alter system archive log current;
select thread#||':'||max(sequence#) from v\$log_history where resetlogs_change# = (select resetlogs_change# from v\$database) group by thread#;") ; then
    echo "WARNING: log switch on the primary database failed: ${out}" >&2
    return 1
  fi
  echo "${out}" | tr -d '[:blank:]' | grep -E '^[0-9]+:[0-9]+$' | tr '\n' ' '
}

# 0: the standby has applied the log <thread> <sequence> completely.
# v$archived_log.applied is not usable: with real-time apply the flag of a log is set late
# (e.g. when Redo Apply is stopped). Redo Apply works on a later log (MRP0) => the log is applied.
standby_applied() {
  local n
  n=$(sql "select count(*) from v\$managed_standby where process like 'MRP%' and thread# = $1 and sequence# > $2;" | tr -d '[:space:]')
  [ "${n:-0}" != "0" ]
}

# Log switch on the primary and wait until the standby has applied this log (Redo Apply is running)
wait_for_primary_redo() {
  local targets t all attempt=1
  targets=$(primary_log_switch) || { echo "WARNING: log switch on the primary database failed"; return 0; }
  [ -n "${targets}" ] || { echo "WARNING: no log history of the primary database"; return 0; }
  echo "Log switch on the primary database, last log (thread:sequence): ${targets}"
  while : ; do
    all=1
    for t in ${targets} ; do
      standby_applied "${t%%:*}" "${t##*:}" || all=0
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

# ---------------------------------------------------------------------------
# 4. ALTER DATABASE FLASHBACK ON/OFF
# ---------------------------------------------------------------------------

# Redo Apply is stopped for each attempt (ORA-01153) and started again after it.
# ORA-38788: repeat the statement after DELAY seconds, RETRIES times.
change_flashback() {
  local statement out rc attempt=1
  if [ "${WANTED}" = "YES" ] ; then statement="alter database flashback on;" ; else statement="alter database flashback off;" ; fi
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
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

check_flashback_state
detect_apply_mode

if [ "${WANTED}" = "YES" ] && [ "${apply_wanted}" = "1" ] && [ -n "${PRIMARY_CI}" ] ; then
  wait_for_primary_redo
fi

# Redo Apply is started again in every case (also after an error or exit)
trap 'start_apply || echo "WARNING: Redo Apply could not be started"' EXIT

change_flashback
