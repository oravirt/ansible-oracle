#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_parameter
short_description: Manage initialization parameters in an Oracle database
description:
    - Sets or resets initialization parameters with C(ALTER SYSTEM SET) and
      C(ALTER SYSTEM RESET).
    - The parameter must exist (C(V$PARAMETER), or C(SYS.X$KSPPI) for underscore
      parameters), otherwise the module fails.
    - Underscore (hidden) parameters can only be handled with O(mode=sysdba).
    - With O(state=present), the current value is read and compared (case-insensitive)
      with O(value). The parameter is only changed when the values differ.
    - Size parameters (C(V$PARAMETER.TYPE=6), e.g. V(sga_target) or
      V(pga_aggregate_target)) are compared in bytes, O(value) can have the units
      V(K), V(M), V(G), V(T) or V(P). The memory value of SGA components (e.g.
      V(sga_target), V(shared_pool_size), V(db_cache_size)) is rounded up to the
      granule size by Oracle, so it is unchanged when it is at most one granule
      (C(V$SGAINFO)) larger than O(value). The spfile value is compared exactly.
      With O(scope=both), the memory and the spfile value for O(sid) are compared. If
      only the spfile value differs, the parameter is set with C(SCOPE=SPFILE).
    - With O(scope=spfile), the current value is read from C(V$SPPARAMETER), otherwise
      from C(V$PARAMETER). With O(mode=sysdba), the C(X$) tables are used instead.
      O(sid) is not considered when reading the current value.
    - With O(state=reset) or O(state=absent), C(ALTER SYSTEM RESET) is executed when the
      parameter is set in the spfile (C(V$SPPARAMETER.ISSPECIFIED) for O(sid), with
      O(scope=spfile) or O(scope=both)) or modified in memory
      (C(V$PARAMETER.ISMODIFIED), with O(scope=memory) or O(scope=both)).
      Otherwise the module returns C(changed=false).
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
            - When connecting with an Oracle wallet, this is the TNS alias of the wallet
              entry.
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
            - V(sysdba) is required for underscore parameters.
        type: str
        required: false
        default: normal
        choices: ['normal', 'sysdba']
    name:
        description:
            - The name of the parameter.
            - Required in practice, although not enforced by the argument spec.
            - Names starting with V(_), V(+), V(/) or a double quote are enclosed in
              double quotes in the SQL statement.
        type: str
        required: false
        aliases: ['parameter']
    value:
        description:
            - The new value of the parameter.
            - Required in practice for O(state=present).
            - A value containing whitespace or one of the characters
              C(?*$%#()!,._/=+-) is enclosed in single quotes, so lists of values
              (like V('a','b')) are not supported.
            - Use V('') (quoted) to set an empty value.
            - Ignored for O(state=reset) and O(state=absent).
        type: str
        required: false
    comment:
        description:
            - A comment added to the C(ALTER SYSTEM SET) statement.
            - Used with O(state=present) only.
        type: str
        required: false
    scope:
        description:
            - The C(SCOPE) clause of the C(ALTER SYSTEM) statement.
            - Also determines where the current value is read from (see description).
        type: str
        required: false
        default: both
        choices: ['both', 'spfile', 'memory']
    sid:
        description:
            - The C(SID) clause of the C(ALTER SYSTEM) statement.
            - V(*) means all instances.
        type: str
        required: false
        default: '*'
    state:
        description:
            - V(present) - the parameter is set to O(value).
            - V(reset) or V(absent) - the parameter is reset to its default value.
        type: str
        required: false
        default: present
        choices: ['present', 'absent', 'reset']
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Check mode is supported. With O(state=reset) or O(state=absent), check mode
      always reports C(changed=true).
requirements: [ "python-oracledb", "re" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Set db_recovery_file_dest
  opitzconsulting.ansible_oracle.oracle_parameter:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    name: db_recovery_file_dest
    value: '+FRA'
    state: present
    scope: both
    sid: '*'

- name: Set db_recovery_file_dest_size in the spfile only
  opitzconsulting.ansible_oracle.oracle_parameter:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    name: db_recovery_file_dest_size
    value: 100G
    comment: Changed by Ansible
    scope: spfile

- name: Reset open_cursors to its default value
  opitzconsulting.ansible_oracle.oracle_parameter:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    name: open_cursors
    state: reset
    scope: spfile

- name: Set an underscore parameter (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_parameter:
    service_name: orcl
    mode: sysdba
    name: _optimizer_adaptive_cursor_sharing
    value: 'false'
    scope: spfile
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
        - Not returned for O(state=reset) in check mode. After a successful reset, the
          value is a list with an empty string.
    returned: success
    type: str
    sample: "The parameter (open_cursors) is already set to 300"
'''


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
    except oracledb.DatabaseError as exc:
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

    size_scope = get_size_parameter_scope(module, cursor, name, value, scope, sid)
    currval = get_curr_value(module, mode, msg, cursor, name, scope)

    if size_scope is None:
        is_set = currval == value.lower() or not currval and value == "''"
    else:
        is_set = size_scope == ''
        scope = size_scope or scope

    if is_set:
        module.exit_json(
            msg='The parameter (%s) is already set to %s' % (name, value), changed=False
        )
        return True

    if module.check_mode:
        # currval is None for a parameter that is not set in the spfile
        msg = '%s will be changed, new: %s, old: %s' % (
            name,
            value,
            (currval or '').upper(),
        )
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
    except oracledb.DatabaseError as exc:
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


# SGA components: the memory value is rounded up to the granule size
GRANULE_PARAMETERS = (
    'sga_target',
    'sga_max_size',
    'memory_target',
    'memory_max_target',
    'shared_pool_size',
    'large_pool_size',
    'java_pool_size',
    'streams_pool_size',
    'db_cache_size',
    'db_keep_cache_size',
    'db_recycle_cache_size',
)

SIZE_UNITS = {
    '': 1,
    'k': 1024,
    'm': 1024**2,
    'g': 1024**3,
    't': 1024**4,
    'p': 1024**5,
}


def size_to_bytes(value):
    match = re.match(r'^\s*(\d+)\s*([kmgtp]?)\s*$', str(value).lower())
    if not match:
        return None
    return int(match.group(1)) * SIZE_UNITS[match.group(2)]


def execute_sql_get(module, cursor, sql, binds):
    try:
        cursor.execute(sql, binds)
        return cursor.fetchall()
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        module.fail_json(
            msg='Something went wrong while getting current value - %s sql: %s'
            % (error.message, sql),
            changed=False,
        )


def get_size_parameter_scope(module, cursor, name, value, scope, sid):
    """Compare a size parameter in bytes.

    Returns None if the parameter is no size parameter or value is no size,
    '' if nothing has to be changed, otherwise the scope for ALTER SYSTEM SET.
    """
    name = clean_string(name).lower()
    wanted = size_to_bytes(value)
    if name.startswith('_') or wanted is None:
        return None

    result = execute_sql_get(
        module,
        cursor,
        'select type, value from v$parameter where name = :name',
        {'name': name},
    )
    if not result or result[0][0] != 6:
        return None

    memory_ok = True
    if scope in ('memory', 'both'):
        current = int(result[0][1] or 0)
        granule = 1
        if name in GRANULE_PARAMETERS or re.match(r'^db_\d+k_cache_size$', name):
            granule_result = execute_sql_get(
                module,
                cursor,
                'select bytes from v$sgainfo where name = \'Granule Size\'',
                {},
            )
            if granule_result:
                granule = max(int(granule_result[0][0]), 1)
        memory_ok = wanted <= current < wanted + granule

    spfile_ok = True
    if scope in ('spfile', 'both'):
        result = execute_sql_get(
            module,
            cursor,
            'select value from v$spparameter '
            'where name = :name and sid = :sid and isspecified = \'TRUE\'',
            {'name': name, 'sid': sid},
        )
        spfile_ok = bool(result) and size_to_bytes(result[0][0]) == wanted

    if memory_ok and spfile_ok:
        return ''
    if memory_ok:
        # ALTER SYSTEM SET ... SCOPE=BOTH does not write the spfile, when the memory
        # value is not changed
        return 'spfile'
    return scope


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


def parameter_is_set(module, cursor, name, scope, sid):
    # ALTER SYSTEM RESET ... SCOPE=BOTH does not raise ORA-32010 any more (23ai and
    # newer), when the parameter is not set => check the spfile and the memory first
    name = clean_string(name).lower()
    checks = []
    if scope in ('spfile', 'both'):
        checks.append(
            (
                'select count(*) from v$spparameter '
                'where name = :name and sid = :sid and isspecified = \'TRUE\'',
                {'name': name, 'sid': sid},
            )
        )
    if scope in ('memory', 'both'):
        checks.append(
            (
                'select count(*) from v$parameter '
                'where name = :name and ismodified <> \'FALSE\'',
                {'name': name},
            )
        )

    for sql, binds in checks:
        try:
            cursor.execute(sql, binds)
            if cursor.fetchone()[0] > 0:
                return True
        except oracledb.DatabaseError as exc:
            (error,) = exc.args
            module.fail_json(
                msg='Something went wrong while checking the parameter - %s sql: %s'
                % (error.message, sql),
                changed=False,
            )
    return False


def reset_parameter(module, mode, msg, cursor, name, value, comment, scope, sid):
    starters = ('+', '_', '"', '"_')
    if not (name):
        module.fail_json(msg='Error: Missing parameter name', changed=False)
        return False

    msg_default = 'The parameter (%s) is already set to its default value' % (
        clean_string(name)
    )
    if not parameter_is_set(module, cursor, name, scope, sid):
        module.exit_json(msg=msg_default, changed=False)

    msg = 'The parameter (%s) has been reset to its default value' % (
        clean_string(name)
    )
    if module.check_mode:
        module.exit_json(msg=msg, changed=True)

    if name.startswith(starters):
        name = quote_name(name)

    sql = 'alter system reset %s scope=%s sid=\'%s\'' % (name, scope, sid)

    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        # ORA-32010: not in the spfile, ORA-32012: memory value not modified
        if error.code in (32010, 32012):
            module.exit_json(msg=msg_default, changed=False)

        module.fail_json(
            msg='Something went wrong while resetting the parameter - %s sql: %s'
            % (error.message, sql),
            changed=False,
        )

    module.exit_json(msg=msg, changed=True)
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

    except oracledb.DatabaseError as exc:
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

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
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
