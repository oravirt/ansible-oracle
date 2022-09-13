#!/usr/bin/bash
set -euo pipefail

cd $HOME

env | grep ^ORACLE | sort

PDB=${pdb_name:-"_"}

${ORACLE_HOME}/bin/sqlplus -S -L /nolog <<EOF
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
EOF