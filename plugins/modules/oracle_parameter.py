#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_parameter
short_description: Manage parameters in an Oracle database
description:
    - Manage init parameters in an Oracle database

version_added: "1.9.1"
options:
    hostname:
        description: The Oracle database host
        required: false
        default: localhost
    port:
        description: The listener port number on the host
        required: false
        default: 1521
    service_name:
        description: The database service name to connect to
        required: true
    user:
        description: The Oracle user name to connect to the database
        required: true
    password:
        description: The Oracle user password for 'user'
        required: true
    mode:
        description: >
            The mode with which to connect to the database
        required: true
        default: normal
        choices: ['normal','sysdba']
    name:
        description: The parameter that is being changed
        required: false
        default: null
    value:
        description: The value of the parameter
        required: false
        default: null
    state:
        description: >
            The intended state of the parameter (present means set to value,
            absent/reset means the value is reset to its default value).
        default: present
        choices: ['present','absent','reset']
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle","re" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Set the value of db_recovery_file_dest
oracle_parameter:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: manager
    name: db_recovery_file_dest
    value: '+FRA'
    state: present
    scope: both
    sid: '*'

# Set the value of db_recovery_file_dest_size
oracle_parameter:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: manager
    name: db_recovery_file_dest_size
    value: 100G
    state: present
    scope: both

# Reset the value of open_cursors
oracle_parameter:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: manager
    name: db_recovery_file_dest_size
    state: reset
    scope: spfile


'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


# Check if the parameter exists
def check_parameter_exists(module, mode, msg, cursor, name):
    if not (name):
        module.fail_json(msg='Error: Missing parameter name', changed=False)
        return False

    if name.startswith('_') and mode != 'sysdba':
        module.fail_json(
            msg='You need sysdba privs to verify underscore parameters (%s), mode: (%s)'
            % (name, mode),
            changed=False,
        )

    elif name.startswith('_') and mode == 'sysdba':
        sql = (
            'select lower(ksppinm) from sys.x$ksppi where ksppinm = lower(\'%s\')'
            % name
        )

    else:
        sql = 'select lower(name) from v$parameter where name = lower(\'%s\')' % name

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + 'sql: ' + sql
        return False

    if result:
        return True
    else:
        msg = 'The parameter (%s) doesn\'t exist' % name  # noqa F841
        return False


def modify_parameter(module, mode, msg, cursor, name, value, comment, scope, sid):
    contains = re.compile(r'[?*$%#()!\s,._/=+-]')
    starters = ('+', '_', '"', '"_', '/')

    if not (name) or not (value) or name is None or value is None:
        module.fail_json(
            msg=(
                'Error: Missing parameter name or value. (If value is supposed to be '
                'an empty string, make sure it\'s quoted)'
            ),
            changed=False,
        )
        return False

    currval = get_curr_value(module, mode, msg, cursor, name, scope)

    if currval == value.lower() or not currval and value == "''":
        module.exit_json(
            msg='The parameter (%s) is already set to %s' % (name, value), changed=False
        )
        return True

    if module.check_mode:
        msg = '%s will be changed, new: %s, old: %s' % (name, value, currval.upper())
        module.exit_json(msg=msg, changed=True)

    if name.startswith(starters):
        name = quote_name(name)

    if contains.search(value):
        value = quote_value(value)

    sql = 'alter system set %s=%s ' % (name, value)
    if comment is not None:
        sql += ' comment=\'%s\'' % (comment)
    # module.fail_json(msg=sql)
    sql += 'scope=%s sid=\'%s\'' % (scope, sid)
    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Blergh, something went wrong while changing the value - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)

    name = clean_string(name)
    msg = 'The parameter (%s) has been changed successfully, new: %s, old: %s' % (
        name,
        value,
        currval,
    )
    module.exit_json(msg=msg, changed=True)
    return True


def quote_value(value):
    if len(value) > 0:
        return "'%s'" % (value)
    else:
        return value


def quote_name(name):
    if len(name) > 0:
        return '"%s"' % (name)
    else:
        return name


def clean_string(item):
    item = item.replace("""\"""", "")

    return item


def reset_parameter(module, mode, msg, cursor, name, value, comment, scope, sid):
    starters = ('+', '_', '"', '"_')
    if not (name):
        module.fail_json(msg='Error: Missing parameter name', changed=False)
        return False

    if module.check_mode:
        module.exit_json(changed=True)

    if name.startswith(starters):
        name = quote_name(name)

    sql = 'alter system reset %s scope=%s sid=\'%s\'' % (name, scope, sid)

    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        if error.code == 32010:
            name = clean_string(name)
            msg = 'The parameter (%s) is already set to its default value' % (name)
            module.exit_json(msg=msg, changed=False)
            return True

        msg = (
            'Blergh, something went wrong while resetting the parameter - %s sql: %s'
            % (error.message, sql)
        )
        return False

    name = clean_string(name)
    msg = 'The parameter (%s) has been reset to its default value' % (name)
    return True


def get_curr_value(module, mode, msg, cursor, name, scope):
    name = clean_string(name)

    if scope == 'spfile':
        parameter_source = 'v$spparameter'
    else:
        parameter_source = 'v$parameter'

    if mode == 'sysdba':
        if scope == 'spfile':
            sql = (
                'select lower(KSPSPFFTCTXSPDVALUE) '
                'from x$kspspfile '
                'where lower(KSPSPFFTCTXSPNAME) = lower(\'%s\')' % (name)
            )
        else:
            sql = (
                'select lower(y.ksppstdvl) '
                'from sys.x$ksppi x, sys.x$ksppcv y '
                'where x.indx = y.indx '
                '  and x.ksppinm = lower(\'%s\')' % (name)
            )
    else:
        sql = 'select lower(display_value) from %s where name = lower(\'%s\')' % (
            parameter_source,
            name,
        )

    try:
        cursor.execute(sql)
        result = cursor.fetchall()[0][0]

    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = (
            'Blergh, something went wrong while getting current value - %s sql: %s'
            % (error.message, sql)
        )
        module.fail_json(msg=msg, changed=False)

    return result


def main():
    global msg
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            name=dict(default=None, aliases=['parameter']),
            value=dict(default=None),
            comment=dict(default=None),
            state=dict(default="present", choices=["present", "absent", "reset"]),
            scope=dict(default="both", choices=["both", "spfile", "memory"]),
            sid=dict(default="*"),
        ),
        supports_check_mode=True,
    )

    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    name = module.params["name"]
    value = module.params["value"]
    comment = module.params["comment"]
    state = module.params["state"]
    scope = module.params["scope"]
    sid = module.params["sid"]

    if not cx_oracle_exists:
        module.fail_json(
            msg=(
                "The cx_Oracle module is required. "
                "'pip install cx_Oracle' should do the trick. "
                "If cx_Oracle is installed, make sure "
                "ORACLE_HOME & LD_LIBRARY_PATH is set"
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
        if check_parameter_exists(module, mode, msg, cursor, name):
            if modify_parameter(
                module, mode, msg, cursor, name, value, comment, scope, sid
            ):
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            module.fail_json(msg=msg, changed=False)

    elif state == 'reset' or state == 'absent':
        if check_parameter_exists(module, mode, msg, cursor, name):
            if reset_parameter(
                module, mode, msg, cursor, name, value, comment, scope, sid
            ):
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            module.fail_json(msg=msg, changed=False)

    module.exit_json(msg=msg, changed=False)


if __name__ == '__main__':
    main()
