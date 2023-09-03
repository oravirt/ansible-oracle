#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_pdb
short_description: Manage pluggable databases in Oracle
description:
    - Manage pluggable databases in Oracle.
version_added: "2.1.0.0"
options:
    name:
        description: The name of the pdb
        required: True
        default: None
    oracle_home:
        description: The ORACLE_HOME to use
        required: False
        default: None
    sourcedb:
        description: >
            The container database which will house the pdb
        required: True
        default: None
        aliases: ['db']
    state:
        description: >
            The intended state of the pdb.
            'status' will just show the status of the pdb
        default: present
        choices: ['present','absent', 'status']
    pdb_admin_username:
        description: >
            The username for the pdb admin user
        required: false
        default: pdb_admin
        aliases: ['un']
    pdb_admin_password:
        description: The password for the pdb admin user
        required: false
        default: pdb_admin
        aliases: ['pw']
    datafile_dest:
        description: The path where the datafiles will be placed
        required: false
        default: None
        aliases: ['dfd']
    unplug_dest:
        description: >
            The path where the 'unplug' xml-file will be placed.
            Also used when plugging in a pdb
        required: false
        default: None
        aliases: ['plug_dest','upd','pd']
    username:
        description: The database username to connect to the database
        required: false
        default: None
        aliases: ['un']
    password:
        description: The password to connect to the database
        required: false
        default: None
        aliases: ['pw']
    service_name:
        description: The service_name to connect to the database
        required: false
        default: database_name
        aliases: ['sn']
    hostname:
        description: The host of the database
        required: false
        default: localhost
        aliases: ['host']
    port:
        description: The listener port to connect to the database
        required: false
        default: 1521

notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Creates a pdb on a different filesystem
oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    dfd: /u02/oradata/pdb1
    state: present
    un: system
    pw: Oracle123
    oracle_home=/u01/app/oracle/12.2.0.1/db

# Remove a pdb
oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    state: absent
    un: system
    pw: Oracle123
    oracle_home: /u01/app/oracle/12.2.0.1/db

# Check the status for a pdb
oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    state: status
    un: system
    pw: Oracle123
    oracle_home: /u01/app/oracle/12.2.0.1/db


# Unplug a pdb
oracle_pdb:
    name: pdb1
    sourcedb: cdb1
    unplug_dest: /tmp/unplugged-pdb.xml
    state: unplugged
    un: sys
    pw: Oracle123
    mode: sysdba
    sn: cdb1
    oracle_home: /u01/app/oracle/12.2.0.1/db1

# plug in a pdb
oracle_pdb:
    name: plug1
    sourcedb: cdb2
    plug_dest: /tmp/unplugged-pdb.xml
    state: present
    un: sys
    pw: Oracle123
    mode: sysdba
    sn: cdb1
    oracle_home: /u01/app/oracle/12.2.0.1/db2
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


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
    if len(value) > 0:
        return "'%s'" % (value)
    else:
        return value


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
    except cx_Oracle.DatabaseError as exc:
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
    except cx_Oracle.DatabaseError as exc:
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
    global value
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

    if not cx_oracle_exists:
        msg = (
            "The cx_Oracle module is required. "
            "'pip install cx_Oracle' should do the trick. "
            "If cx_Oracle is installed, make sure ORACLE_HOME "
            "& LD_LIBRARY_PATH is set"
        )
        module.fail_json(msg=msg)

    if service_name is None:
        service_name = sourcedb

    wallet_connect = '/@%s' % service_name
    try:
        if not user and not password:
            # If neither user or password is supplied, the use of an
            # oracle wallet is assumed
            if mode == 'sysdba':
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
            else:
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect)

        elif user and password:
            if mode == 'sysdba':
                dsn = cx_Oracle.makedsn(
                    host=hostname, port=port, service_name=service_name
                )
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
            else:
                dsn = cx_Oracle.makedsn(
                    host=hostname, port=port, service_name=service_name
                )
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn)

        elif not (user) or not (password):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Could not connect to database - %s, connect descriptor: %s' % (
            error.message,
            connect,
        )
        module.fail_json(msg=msg, changed=False)

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
