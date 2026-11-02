#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_directory
short_description: Manage directory objects in an Oracle database
description:
    - Creates, changes and drops directory objects (C(CREATE DIRECTORY))
      in an Oracle database.
    - The existence of a directory is checked in C(DBA_DIRECTORIES).
    - The directory name is not quoted in the SQL statements, so it is always
      stored in uppercase.
    - The module does not check or create the path on the database server.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "1.9.1"
options:
    hostname:
        description:
            - The Oracle database host.
            - Ignored when connecting with an Oracle wallet.
        type: str
        required: false
        default: localhost
    port:
        description:
            - The listener port number on the host.
            - Ignored when connecting with an Oracle wallet.
        type: int
        required: false
        default: 1521
    service_name:
        description:
            - The database service name to connect to.
            - When connecting with an Oracle wallet, this is the TNS alias
              of the wallet entry.
        type: str
        required: true
    user:
        description:
            - The Oracle user name to connect to the database.
            - Omit O(user) and O(password) to connect with an Oracle wallet.
        type: str
        required: false
    password:
        description:
            - The Oracle user password for O(user).
        type: str
        required: false
    mode:
        description:
            - The mode with which to connect to the database.
        type: str
        required: false
        default: normal
        choices: ['normal', 'sysdba']
    directory_name:
        description:
            - The name of the directory object.
            - Required in practice, although not enforced by the argument spec.
        type: str
        required: false
    directory_path:
        description:
            - The path on the database server the directory object points to.
            - Used with O(state=present) only.
        type: str
        required: false
    directory_mode:
        description:
            - How to handle an existing directory with a different path.
            - V(enforce) - the directory is recreated with
              C(CREATE OR REPLACE DIRECTORY) to point to O(directory_path).
            - V(normal) - the path of an existing directory is not changed.
        type: str
        required: false
        default: enforce
        choices: ['normal', 'enforce']
    state:
        description:
            - V(present) - the directory is created or its path is changed
              (see O(directory_mode)).
            - V(absent) - the directory is dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Create directory DATA_PUMP_DIR2
  opitzconsulting.ansible_oracle.oracle_directory:
    hostname: dbhost
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    directory_name: data_pump_dir2
    directory_path: /u01/app/oracle/dpdump2
    state: present

- name: Drop directory DATA_PUMP_DIR2 (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_directory:
    service_name: orclpdb
    directory_name: data_pump_dir2
    state: absent
'''

RETURN = '''
msg:
    description: Message describing the action that was executed.
    returned: always
    type: str
    sample: "Directory: data_pump_dir2, created with path: /u01/app/oracle/dpdump2"
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


# Check if the directory exists
def check_directory_exists(module, msg, cursor, directory_name):
    if not (directory_name):
        module.fail_json(msg='Error: Missing directory name', changed=False)
        return False

    sql = (
        'select count(*) '
        'from dba_directories '
        'where directory_name= upper(\'%s\')' % directory_name
    )

    try:
        cursor.execute(sql)
        result = cursor.fetchone()[0]
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        module.fail_json(msg=error.message + ' sql: ' + sql, changed=False)
        return False

    if result > 0:
        return True
    else:
        return False


def ensure_directory(
    module, msg, cursor, directory_name, directory_path, directory_mode
):
    if check_directory_exists(module, msg, cursor, directory_name):
        check_path_sql = (
            'select directory_path '
            'from dba_directories '
            'where directory_name = upper(\'%s\')' % directory_name
        )
        _curr_path = execute_sql_get(module, msg, cursor, check_path_sql)

        if _curr_path[0][0] != directory_path:
            if directory_mode == 'enforce':
                directory_sql = 'create or replace directory %s as \'%s\'' % (
                    directory_name,
                    directory_path,
                )
                if execute_sql(module, msg, cursor, directory_sql):
                    module.exit_json(
                        msg='Directory %s, changed to path: %s (old path: %s)'
                        % (directory_name, directory_path, _curr_path[0][0]),
                        changed=True,
                    )
        else:
            module.exit_json(
                msg='Directory %s already exists (%s)'
                % (directory_name, directory_path),
                changed=False,
            )
    else:
        directory_sql = 'create directory %s as \'%s\'' % (
            directory_name,
            directory_path,
        )

        if execute_sql(module, msg, cursor, directory_sql):
            msg = 'Directory: %s, created with path: %s' % (
                directory_name,
                directory_path,
            )
            module.exit_json(msg=msg, changed=True)


def drop_directory(module, msg, cursor, directory_name):
    drop_sql = 'drop directory %s' % (directory_name)

    if execute_sql(module, msg, cursor, drop_sql):
        module.exit_json(
            msg='Directory %s successfully dropped' % (directory_name), changed=True
        )


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


def main():
    global msg
    global state
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            directory_name=dict(default=None),
            directory_path=dict(default=None),
            directory_mode=dict(default="enforce", choices=["normal", "enforce"]),
            state=dict(default="present", choices=["present", "absent"]),
        )
    )

    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    directory_name = module.params["directory_name"]
    directory_path = module.params["directory_path"]
    directory_mode = module.params["directory_mode"]
    state = module.params["state"]

    if not cx_oracle_exists:
        module.fail_json(
            msg=(
                "The cx_Oracle module is required. "
                "'pip install cx_Oracle' should do the trick. "
                "If cx_Oracle is installed, make sure ORACLE_HOME "
                "& LD_LIBRARY_PATH is set"
            )
        )

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

    if state == 'present':
        ensure_directory(
            module, msg, cursor, directory_name, directory_path, directory_mode
        )
    elif state == 'absent':
        if check_directory_exists(module, msg, cursor, directory_name):
            drop_directory(module, msg, cursor, directory_name)

        else:
            msg = 'Directory %s doesn\'t exist' % (directory_name)
            module.exit_json(msg=msg, changed=False)

    else:
        module.fail_json(msg='Unhandled exit', changed=False)


if __name__ == '__main__':
    main()
