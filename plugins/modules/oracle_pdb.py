#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_pdb
short_description: Manage pluggable databases in Oracle
description:
    - Creates, plugs in, opens, closes, unplugs and drops pluggable databases (PDB)
      in an Oracle container database (CDB).
    - The module must connect to the root container of the CDB.
    - The existence of a PDB is checked in C(DBA_PDBS), its open mode in C(V$PDBS).
    - The PDB name is not quoted in the SQL statements, so it is always stored in
      uppercase.
    - A new PDB is created with C(CREATE PLUGGABLE DATABASE), opened on all
      instances (C(OPEN INSTANCES=ALL)) and, with O(save_state=true), its state is
      saved (C(SAVE STATE INSTANCES=ALL)). Afterwards O(state) is enforced.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "2.1.0.0"
options:
    name:
        description:
            - The name of the PDB.
        type: str
        required: true
        aliases: ['pdb', 'pdb_name']
    oracle_home:
        description:
            - The ORACLE_HOME to use. Sets the environment variable E(ORACLE_HOME)
              for the module.
            - The module fails if neither O(oracle_home) nor the environment variable
              E(ORACLE_HOME) is set.
        type: str
        required: false
        aliases: ['oh']
    sourcedb:
        description:
            - The name of the container database that houses the PDB.
            - Only used as default for O(service_name).
        type: str
        required: true
        aliases: ['db', 'container', 'cdb']
    state:
        description:
            - The intended state of the PDB. The PDB is created if it does not exist
              for all states except V(absent), V(unplugged) and V(status).
            - V(present), V(open), V(read_write) - the PDB is opened read write
              (C(OPEN FORCE)).
            - V(closed) - the PDB is closed (C(CLOSE IMMEDIATE)).
            - V(read_only) - the PDB is opened read only (C(OPEN READ ONLY FORCE)).
            - V(restricted) - the PDB is opened in restricted mode
              (C(OPEN RESTRICTED FORCE)).
            - For an existing PDB, the open mode and restricted flag in C(V$PDBS) are
              compared with the intended state. The C(ALTER PLUGGABLE DATABASE)
              statement is only executed on a difference and affects the current
              instance only.
            - V(absent) - the PDB is closed on all instances and dropped
              C(INCLUDING DATAFILES).
            - V(unplugged) - the PDB is closed on all instances, unplugged into the
              XML file O(unplug_dest) and dropped C(KEEP DATAFILES).
            - V(status) - nothing is changed. The PDB status is queried.
        type: str
        required: false
        default: present
        choices: ['present', 'absent', 'open', 'closed', 'read_write', 'read_only',
                  'restricted', 'status', 'unplugged']
    save_state:
        description:
            - Save the open state of a newly created PDB with
              C(ALTER PLUGGABLE DATABASE ... SAVE STATE INSTANCES=ALL).
            - Only used when the PDB is created.
        type: bool
        required: false
        default: true
    pdb_admin_username:
        description:
            - The name of the PDB admin user (C(ADMIN USER)) of a new PDB.
            - Not used when the PDB is plugged in with O(unplug_dest).
        type: str
        required: false
        default: pdb_admin
        aliases: ['pdbadmun']
    pdb_admin_password:
        description:
            - The password of the PDB admin user O(pdb_admin_username).
        type: str
        required: false
        default: pdb_admin
        aliases: ['pdbadmpw']
    datafile_dest:
        description:
            - The directory or ASM disk group for the datafiles of a new PDB
              (C(CREATE_FILE_DEST)).
        type: str
        required: false
        aliases: ['dfd', 'create_file_dest']
    unplug_dest:
        description:
            - The path of the XML file the PDB is unplugged into with
              O(state=unplugged).
            - When set while a PDB is created, the PDB is plugged in from this XML
              file (C(USING '<unplug_dest>' TEMPFILE REUSE)) instead of being created
              from the seed.
            - Required in practice for O(state=unplugged), although not enforced by
              the argument spec.
        type: str
        required: false
        aliases: ['plug_dest', 'upd', 'pd']
    file_name_convert:
        description:
            - Comma separated list of file name pairs for C(FILE_NAME_CONVERT)
              when a PDB is created, e.g. V(/u02/oradata/pdbseed/,/u02/oradata/pdb1/).
            - Together with O(unplug_dest), the datafiles are copied (C(COPY)).
        type: str
        required: false
        aliases: ['fnc']
    service_name_convert:
        description:
            - Not implemented. The option is accepted but ignored by the module.
        type: str
        required: false
        aliases: ['snc']
    default_tablespace_type:
        description:
            - Not implemented. The option is accepted but ignored by the module.
        type: str
        required: false
        default: smallfile
        choices: ['smallfile', 'bigfile']
    default_tablespace:
        description:
            - Not implemented. The option is accepted but ignored by the module.
        type: str
        required: false
    default_temp_tablespace:
        description:
            - Not implemented. The option is accepted but ignored by the module.
        type: str
        required: false
    timezone:
        description:
            - Not implemented. The option is accepted but ignored by the module.
        type: str
        required: false
    user:
        description:
            - The Oracle user name to connect to the database.
            - Omit O(user) and O(password) to connect with an Oracle wallet.
        type: str
        required: false
        aliases: ['un', 'username']
    password:
        description:
            - The Oracle user password for O(user).
        type: str
        required: false
        aliases: ['pw']
    mode:
        description:
            - The mode with which to connect to the database.
        type: str
        required: false
        default: normal
        choices: ['normal', 'sysdba']
    service_name:
        description:
            - The database service name to connect to. Defaults to O(sourcedb).
            - When connecting with an Oracle wallet, this is the TNS alias of the
              wallet entry.
        type: str
        required: false
        aliases: ['sn']
    hostname:
        description:
            - The Oracle database host.
            - Ignored when connecting with an Oracle wallet.
        type: str
        required: false
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port number on the host.
            - Ignored when connecting with an Oracle wallet.
        type: int
        required: false
        default: 1521
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - O(datafile_dest) and O(file_name_convert) are mutually exclusive.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Create a PDB with its datafiles in a different location
  opitzconsulting.ansible_oracle.oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    datafile_dest: /u02/oradata/pdb1
    pdb_admin_password: "{{ pdb_admin_password }}"
    state: present
    user: sys
    password: "{{ sys_password }}"
    mode: sysdba
    oracle_home: /u01/app/oracle/product/19/db

- name: Close a PDB
  opitzconsulting.ansible_oracle.oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    state: closed
    user: sys
    password: "{{ sys_password }}"
    mode: sysdba
    oracle_home: /u01/app/oracle/product/19/db

- name: Check the status of a PDB (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    state: status
    mode: sysdba
    oracle_home: /u01/app/oracle/product/19/db

- name: Unplug a PDB
  opitzconsulting.ansible_oracle.oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    unplug_dest: /tmp/unplugged-pdb.xml
    state: unplugged
    user: sys
    password: "{{ sys_password }}"
    mode: sysdba
    oracle_home: /u01/app/oracle/product/19/db

- name: Plug in a PDB into another CDB
  opitzconsulting.ansible_oracle.oracle_pdb:
    name: plug1
    sourcedb: cdb2
    unplug_dest: /tmp/unplugged-pdb.xml
    state: present
    user: sys
    password: "{{ sys_password }}"
    mode: sysdba
    oracle_home: /u01/app/oracle/product/19/db

- name: Remove a PDB
  opitzconsulting.ansible_oracle.oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    state: absent
    user: sys
    password: "{{ sys_password }}"
    mode: sysdba
    oracle_home: /u01/app/oracle/product/19/db
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
    returned: always
    type: str
    sample: "Pluggable database pdb1 already in the intended state"
'''


# Check if the pdb exists
def check_pdb_exists(cursor, module, msg, name):
    global newpdb
    sql = (
        'select lower(pdb_name) '
        'from dba_pdbs '
        'where lower (pdb_name) = \'%s\'' % (name.lower())
    )

    result = execute_sql_get(module, msg, cursor, sql)
    if len(result) > 0:
        newpdb = False
        return True
    else:
        newpdb = True
        return False


def quote_string(item):
    if len(item) > 0:
        return "'%s'" % (item)
    else:
        return item


def create_pdb(
    cursor,
    module,
    msg,
    oracle_home,
    name,
    sourcedb,
    pdb_admin_username,
    pdb_admin_password,
    datafile_dest,
    save_state,
    unplug_dest,
    file_name_convert,
):
    run_sql = []
    opensql = 'alter pluggable database %s open instances=all' % (name)
    createsql = 'create pluggable database %s ' % (name)

    if unplug_dest is not None:
        createsql += ' using \'%s\' ' % (unplug_dest)
        createsql += ' tempfile reuse'

    if unplug_dest is None:
        createsql += ' admin user %s identified by \"%s\" ' % (
            pdb_admin_username,
            pdb_admin_password,
        )

    if datafile_dest is not None:
        createsql += ' create_file_dest = \'%s\'' % (datafile_dest)

    if file_name_convert is not None and unplug_dest is not None:
        quoted = ",".join("'" + p + "'" for p in file_name_convert.split(","))
        createsql += ' file_name_convert = (%s) copy' % (quoted)

    if file_name_convert is not None and unplug_dest is None:
        quoted = ",".join("'" + p + "'" for p in file_name_convert.split(","))
        createsql += ' file_name_convert = (%s)' % (quoted)

    run_sql.append(createsql)
    run_sql.append(opensql)
    # module.exit_json(msg=run_sql, changed=False)
    for a in run_sql:
        execute_sql(module, msg, cursor, a)
    if save_state:
        sql = 'alter pluggable database %s save state instances=all' % (name)
        execute_sql(module, msg, cursor, sql)
        return True  # <-- all is well


def unplug_pdb(cursor, module, msg, oracle_home, name, unplug_dest):
    run_sql = []
    close_sql = 'alter pluggable database %s close immediate instances=all' % (name)
    unplug_sql = 'alter pluggable database %s unplug into \'%s\'' % (name, unplug_dest)
    drop_sql = 'drop pluggable database %s keep datafiles ' % (name)

    run_sql.append(close_sql)
    run_sql.append(unplug_sql)
    run_sql.append(drop_sql)
    for a in run_sql:
        execute_sql(module, msg, cursor, a)
    return True  # <-- all is well


def remove_pdb(cursor, module, msg, oracle_home, name, sourcedb):
    run_sql = []
    close_sql = 'alter pluggable database %s close immediate instances=all' % (name)
    dropsql = 'drop pluggable database %s including datafiles' % (name)

    run_sql.append(close_sql)
    run_sql.append(dropsql)
    for a in run_sql:
        execute_sql(module, msg, cursor, a)
    return True


def check_pdb_status(cursor, module, msg, name):
    sql = (
        'select name, con_id, con_uid, '
        'open_mode, restricted, to_char(open_time,\'HH24:MI:SS YYYY-MM-DD\'), '
        'recovery_status '
        'from v$pdbs '
        'where lower(name) = \'%s\'' % (name)
    )
    result = execute_sql_get(module, msg, cursor, sql)
    if len(result) > 0:
        for a in result:
            msg = (
                'pdb name: %s, con_id: %s, con_uid: %s, open_mode: %s, restricted: %s, '
                'open_time: %s' % (a[0].lower(), a[1], a[2], a[3], a[4], a[5])
            )


def ensure_pdb_state(
    cursor,
    module,
    msg,
    name,
    state,
    newpdb,
    default_tablespace,
    default_tablespace_type,
    default_temp_tablespace,
    timezone,
):
    wanted_state = []
    sql = (
        'select lower(open_mode), lower(restricted) '
        'from v$pdbs '
        'where lower(name) = \'%s\'' % (name.lower())
    )
    propsql = (
        "select lower(property_value) "
        "from database_properties "
        "where property_name in ('DEFAULT_TBS_TYPE', 'DEFAULT_PERMANENT_TABLESPACE', "
        "                        'DEFAULT_TEMP_TABLESPACE') "
        "order by 1"
    )
    tzsql = (
        "select lower(property_value) "
        "from database_properties "
        "where property_name = 'DBTIMEZONE'"
    )

    state_now = execute_sql_get(module, msg, cursor, sql)
    curr_time_zone = execute_sql_get(module, msg, cursor, tzsql)  # noqa F841
    def_tbs_type, def_tbs, def_temp_tbs = execute_sql_get(module, msg, cursor, propsql)

    ensure_sql = 'alter pluggable database %s ' % (name)

    if state in ('present', 'open', 'read_write'):
        wanted_state = [('read write', 'no')]
        ensure_sql += ' open force'
    elif state == 'closed':
        wanted_state = [('mounted', None)]
        ensure_sql += ' close immediate'
    elif state == 'read_only':
        wanted_state = [('read only', 'no')]
        ensure_sql += 'open read only force'
    elif state == 'restricted':
        wanted_state = [('read write', 'yes')]
        ensure_sql += 'open restricted force'

    # if def_tbs_type[0] != default_tablespace_type:
    #   deftbstypesql = 'alter database set default %s tablespace'
    #       % (default_tablespace_type)
    #   change_db_sql.append(deftbstypesql)
    #
    # if default_tablespace is not None and def_tbs[0] != default_tablespace:
    #   deftbssql = 'alter database default tablespace %s' % (default_tablespace)
    #   change_db_sql.append(deftbssql)
    #
    # if default_temp_tablespace is not None
    #       and def_temp_tbs[0] != default_temp_tablespace:
    #   deftempsql = 'alter database default temporary tablespace %s'
    #       % (default_temp_tablespace)
    #   change_db_sql.append(deftempsql)
    #
    # if timezone is not None and curr_time_zone[0][0] != timezone:
    #   deftzsql = 'alter database set time_zone = \'%s\'' % (timezone)
    #   change_db_sql.append(deftzsql)
    #
    # if len(change_db_sql) > 0 :
    # 	total_sql.append(change_db_sql)
    # 	for sql in total_sql:
    # 		execute_sql(module, msg, cursor, sql)
    #     dbchange = True

    if wanted_state == state_now:
        if newpdb:
            msg = 'Successfully created pluggable database %s ' % (name)
            module.exit_json(msg=msg, changed=True)
        msg = 'Pluggable database %s already in the intended state' % (name)
        module.exit_json(msg=msg, changed=False)

    #   if len(ensure_sql) > 0:
    #       total_sql.append(ensure_sql)
    #   module.exit_json(msg=total_sql, changed=True)
    #   for sql in total_sql:
    #       execute_sql(module, msg, cursor, sql)
    #   msg = 'Pluggable database %s has been put in the intended state: %s'
    #       % (name, state)
    #   module.exit_json(msg=msg, changed=True)
    # else:
    #   msg = 'Pluggable database %s already in the intended state' % (name)
    #   module.exit_json(msg=msg, changed=False)
    if execute_sql(module, msg, cursor, ensure_sql):
        msg = 'Pluggable database %s has been put in the intended state: %s' % (
            name,
            state,
        )
        module.exit_json(msg=msg, changed=True)
    else:
        return False

        # return False


def execute_sql_get(module, msg, cursor, sql):
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql_get - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
        return False
    return result


def execute_sql(module, msg, cursor, sql):
    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
        return False
    return True


def main():
    global msg
    msg = ['']

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['pdb', 'pdb_name']),
            oracle_home=dict(default=None, aliases=['oh']),
            sourcedb=dict(required=True, aliases=['db', 'container', 'cdb']),
            state=dict(
                default="present",
                choices=[
                    "present",
                    "absent",
                    "open",
                    "closed",
                    "read_write",
                    "read_only",
                    "restricted",
                    "status",
                    "unplugged",
                ],
            ),
            save_state=dict(default=True, type='bool'),
            pdb_admin_username=dict(
                required=False, default='pdb_admin', aliases=['pdbadmun']
            ),
            pdb_admin_password=dict(
                required=False, no_log=True, default='pdb_admin', aliases=['pdbadmpw']
            ),
            datafile_dest=dict(required=False, aliases=['dfd', 'create_file_dest']),
            unplug_dest=dict(required=False, aliases=['plug_dest', 'upd', 'pd']),
            file_name_convert=dict(required=False, aliases=['fnc']),
            service_name_convert=dict(required=False, aliases=['snc']),
            default_tablespace_type=dict(
                default='smallfile', choices=['smallfile', 'bigfile']
            ),
            default_tablespace=dict(required=False),
            default_temp_tablespace=dict(required=False),
            timezone=dict(required=False),
            user=dict(required=False, aliases=['un', 'username']),
            password=dict(required=False, no_log=True, aliases=['pw']),
            mode=dict(default="normal", choices=["sysdba", "normal"]),
            service_name=dict(required=False, aliases=['sn']),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            port=dict(required=False, default=1521),
        ),
        mutually_exclusive=[['datafile_dest', 'file_name_convert']],
    )

    name = module.params["name"]
    oracle_home = module.params["oracle_home"]
    sourcedb = module.params["sourcedb"]
    state = module.params["state"]
    save_state = module.params["save_state"]
    pdb_admin_username = module.params["pdb_admin_username"]
    pdb_admin_password = module.params["pdb_admin_password"]
    datafile_dest = module.params["datafile_dest"]
    unplug_dest = module.params["unplug_dest"]
    file_name_convert = module.params["file_name_convert"]
    # service_name_convert = module.params["service_name_convert"]
    default_tablespace_type = module.params["default_tablespace_type"]
    default_tablespace = module.params["default_tablespace"]
    default_temp_tablespace = module.params["default_temp_tablespace"]
    timezone = module.params["timezone"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    service_name = module.params["service_name"]
    hostname = module.params["hostname"]
    port = module.params["port"]

    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg, changed=False)

    if service_name is None:
        service_name = sourcedb

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    cursor = conn.cursor()

    if state in ('present', 'closed', 'open', 'restricted', 'read_only', 'read_write'):
        if not check_pdb_exists(cursor, module, msg, name):
            if create_pdb(
                cursor,
                module,
                msg,
                oracle_home,
                name,
                sourcedb,
                pdb_admin_username,
                pdb_admin_password,
                datafile_dest,
                save_state,
                unplug_dest,
                file_name_convert,
            ):
                ensure_pdb_state(
                    cursor,
                    module,
                    msg,
                    name,
                    state,
                    newpdb,
                    default_tablespace,
                    default_tablespace_type,
                    default_temp_tablespace,
                    timezone,
                )
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            ensure_pdb_state(
                cursor,
                module,
                msg,
                name,
                state,
                newpdb,
                default_tablespace,
                default_tablespace_type,
                default_temp_tablespace,
                timezone,
            )

    elif state == 'absent':
        if check_pdb_exists(cursor, module, msg, name):
            if remove_pdb(cursor, module, msg, oracle_home, name, sourcedb):
                msg = 'Pluggable database %s successfully removed' % (name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            msg = 'Pluggable database %s doesn\'t exist' % (name)
            module.exit_json(msg=msg, changed=False)

    elif state == 'unplugged':
        if check_pdb_exists(cursor, module, msg, name):
            if unplug_pdb(cursor, module, msg, oracle_home, name, unplug_dest):
                msg = 'Pluggable database %s successfully unplugged into \'%s\'' % (
                    name,
                    unplug_dest,
                )
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            msg = 'Pluggable database %s doesn\'t exist' % (name)
            module.exit_json(msg=msg, changed=False)

    elif state == 'status':
        if check_pdb_exists(cursor, module, msg, name):
            check_pdb_status(cursor, module, msg, name)
            module.exit_json(msg=msg, changed=False)
        else:
            msg = 'Pluggable database %s doesn\'t exist' % (name)
            module.exit_json(msg=msg, changed=False)

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
