#!/usr/bin/env bash
set -euo pipefail

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
    echo "Connect with / as sysdba not possible or pluggable database not existing!"
    exit 11
  fi
}

function spdrop {
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

  if ! echo "${sqlcmd}" | "${SQLPLUS}" -S -L > /dev/null 2>&1 ; then
    echo "User is not existing. Nothing to do."
    exit 0
  else

sqlcmd="
conn / as sysdba

whenever oserror exit 1 rollback
begin
  if '${PDB}' <> '_' then
    execute immediate 'alter session set container = ${PDB}';
  end if;
end;
/

@?/rdbms/admin/spdrop
exit
"

  if echo "${sqlcmd}" | "${SQLPLUS}" -S -L /nolog ; then
    echo "Statspack dropped"
  else
    echo "Failure during statspack drop."
    exit 12
  fi

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

sqlplus_login
spdrop
