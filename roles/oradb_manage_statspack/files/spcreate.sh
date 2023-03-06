#!/usr/bin/env bash
#
# List of return codes:
# 10 Error during spcreate
# 11 Login with / as sysdba not possible

set -euo pipefail

function check_sqlplus_exec {
  echo "Check sqlplus executable"
  test -x "${SQLPLUS}"
}

function execute_spcreate {
echo "Starting sqlplus"

"${SQLPLUS}" -S -L /nolog <<EOF
conn / as sysdba

define perfstat_password=${perfstat_password:?}
define temporary_tablespace=${temporary_tablespace:?}
define default_tablespace=${default_tablespace:?}
define purgedates=${purgedates:?}
define snaplevel=${snaplevel:?}

whenever sqlerror exit 1 rollback
whenever oserror exit 99 rollback

begin
  if '${PDB}' <> '_' then
    execute immediate 'alter session set container = ${PDB}';
  end if;
end;
/

@?/rdbms/admin/spcreate

set echo on
alter session set current_schema=perfstat;

PROMPT Fixup for idle Events (old stupid bug from Oracle...)
-- Re-fill STATS\$IDLE_EVENT with latest idle events that Oracle regularly forgets to update.
delete from perfstat.STATS\$IDLE_EVENT;
insert into perfstat.STATS\$IDLE_EVENT select name from V\$EVENT_NAME where wait_class='Idle';
commit;

PROMPT Create custom index for selecting sql_id from STATS\$SQLTEXT
create index perfstat.STATS\$SQLTEXT_UK1 on STATS\$SQLTEXT(sql_id, piece);

exit
EOF
}

function spcreate {
  echo ""
  echo "Check for existing PERFSTAT user"
  sqlcmd="conn / as sysdba
whenever sqlerror exit 10

begin
  if '${PDB}' <> '_' then
    execute immediate 'alter session set container = ${PDB}';
  end if;
end;
/

declare
  v_username varchar2(20);
begin
  select username
  into v_username
  from dba_users
  where username = 'PERFSTAT';
end;
/
"

  if echo "${sqlcmd}" | "${SQLPLUS}" -S -L > /dev/null 2>&1 ; then
    echo "User is existing. Skip installation of Statspack!"
  else
    execute_spcreate
    echo "Installation of Statspack completed."
  fi
}

function sqlplus_login {

  echo ""
  echo "Check for Login into Oracle Instance"

  sqlcmd="conn / as sysdba
whenever sqlerror exit 11
begin
  if '${PDB}' <> '_' then
    execute immediate 'alter session set container = ${PDB}';
  end if;
end;
/
"

  if ! echo "${sqlcmd}" | "${SQLPLUS}" -S -L /nolog > /dev/null 2>&1 ; then
    echo "Connect wint / as sysdba not possible or pluggable database not existing!"
    exit 11
  fi
}

###########################
###########################
cd "$HOME"

PDB=${pdb_name:-"_"}

echo ""
env | grep ^ORACLE | sort
echo ""
if [[ "${PDB}" == "_" ]] ; then
  echo "Target: CDB"
else
  echo "Target: PDB: ${PDB}"
fi
echo ""

SQLPLUS="${ORACLE_HOME}/bin/sqlplus"

check_sqlplus_exec
sqlplus_login
spcreate
