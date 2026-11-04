#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_role
short_description: Manage roles in an Oracle database
description:
    - Creates, changes and drops roles (C(CREATE ROLE)) in an Oracle database.
    - The module does not manage privileges granted to a role, use
      M(opitzconsulting.ansible_oracle.oracle_grants) for that.
    - The existence of a role is checked in C(DBA_ROLES). The role name is not quoted
      in the SQL statements, so it is always stored in uppercase.
    - For an existing role, the authentication type (C(DBA_ROLES.AUTHENTICATION_TYPE))
      is compared with O(auth). The role is only altered when they differ, so a
      changed password or package in O(auth_conf) is not detected.
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
        type: str
        required: false
        default: normal
        choices: ['normal', 'sysdba']
    role:
        description:
            - The name of the role.
            - Required in practice, although not enforced by the argument spec.
        type: str
        required: false
    auth:
        description:
            - The authentication type of the role.
            - V(none) - C(NOT IDENTIFIED).
            - V(password) - C(IDENTIFIED BY <auth_conf>).
            - V(application) - C(IDENTIFIED USING <auth_conf>).
            - V(external) - C(IDENTIFIED EXTERNALLY).
            - V(global) - C(IDENTIFIED GLOBALLY).
            - Used with O(state=present) only.
        type: str
        required: false
        default: none
        choices: ['none', 'password', 'external', 'global', 'application']
    auth_conf:
        description:
            - The password for O(auth=password) or the authentication package
              (C(schema.package)) for O(auth=application).
            - Required for O(auth=password) and O(auth=application), ignored otherwise.
        type: str
        required: false
    state:
        description:
            - V(present) - the role is created, or its authentication type is changed
              (see O(auth)).
            - V(absent) - the role is dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Check mode is not supported.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Create role MYROLE
  opitzconsulting.ansible_oracle.oracle_role:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    role: myrole
    state: present

- name: Create password protected role MYPWROLE
  opitzconsulting.ansible_oracle.oracle_role:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    role: mypwrole
    auth: password
    auth_conf: "{{ role_password }}"

- name: Drop role MYROLE (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_role:
    service_name: orcl
    role: myrole
    state: absent
'''

RETURN = '''
msg:
    description: Message describing the action that was executed.
    returned: always
    type: str
    sample: "The role (myrole) has been created successfully, authentication: none"
'''


def clean_string(item):
    item = (
        item.replace("'", "")
        .replace(", ", ",")
        .lstrip(" ")
        .rstrip(",")
        .replace("[", "")
        .replace("]", "")
    )

    return item


def clean_list(item):
    item = [
        p.replace("'", "")
        .replace(", ", ",")
        .lstrip(" ")
        .rstrip(",")
        .replace("[", "")
        .replace("]", "")
        for p in item
    ]

    return item


# Check if the user/role exists
def check_role_exists(module, msg, cursor, role, auth):
    if not (role):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    role = clean_string(role)
    sql = 'select count(*) ' 'from dba_roles ' 'where role = upper(\'%s\')' % role

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg[0] = error.message + 'sql: ' + sql
        return False

    if result[0] > 0:
        msg[0] = 'The role (%s) already exists' % role
        return True

    return False


# Create the role
def create_role(module, msg, cursor, role, auth, auth_conf):
    if not (role) or not (auth):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    # This is the default role creation
    sql = 'create role %s ' % role

    if auth == 'password':
        if not auth_conf:
            module.fail_json(msg='Missing password', changed=False)
            return False
        else:
            sql += 'identified by %s' % auth_conf

    if auth == 'application':
        if not (auth_conf):
            module.fail_json(
                msg='Missing authentication package (schema.name)', changed=False
            )
            return False
        else:
            sql += 'identified using %s' % auth_conf

    if auth == 'external':
        sql += 'identified externally '

    if auth == 'global':
        sql += 'identified globally'

    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg[0] = 'Blergh, something went wrong while creating the role - %s sql: %s' % (
            error.message,
            sql,
        )
        return False

    msg[0] = 'The role (%s) has been created successfully, authentication: %s' % (
        role,
        auth,
    )
    return True


def modify_role(module, msg, cursor, role, auth, auth_conf):
    if not (role) or not (auth):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    sql = 'alter role %s ' % (role)

    currauth = get_role_specs(module, msg, cursor, role)

    if currauth.lower() == auth.lower():
        module.exit_json(msg='The role (%s) already exists' % role, changed=False)

    else:
        if auth == 'none':
            sql += ' not identified '

        if auth == 'password':
            if not auth_conf:
                module.fail_json(
                    msg='Missing password for authentication_type %s' % (auth),
                    changed=False,
                )
                return False
            else:
                sql += ' identified by %s' % auth_conf

        if auth == 'application':
            if not (auth_conf):
                module.fail_json(
                    msg='Missing authentication package (schema.name)', changed=False
                )
                return False
            else:
                sql += 'identified using %s' % auth_conf

        if auth == 'external':
            sql += 'identified externally '

        if auth == 'global':
            sql += 'identified globally'

        try:
            cursor.execute(sql)
        except oracledb.DatabaseError as exc:
            (error,) = exc.args
            msg[0] = (
                'Blergh, something went wrong while altering the role - %s sql: %s'
                % (
                    error.message,
                    sql,
                )
            )
            return False

        msg[0] = (
            'The role (%s) has been changed successfully, authentication: %s, '
            'previous: %s' % (role, auth, currauth)
        )
    return True


def get_role_specs(module, msg, cursor, role):
    sql = (
        'select lower(authentication_type) from dba_roles where role = upper(\'%s\')'
        % role
    )

    try:
        cursor.execute(sql)
        result = cursor.fetchall()[0][0]
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg[0] = (
            'Blergh, something went wrong while getting the role auth scheme '
            ' - %s sql: %s' % (error.message, sql)
        )
        module.fail_json(msg=msg[0], changed=False)
        return False

    # module.exit_json(msg='Result: %s, sql: %s' % (result, sql), changed=False)
    return result


# Create the role
def drop_role(module, msg, cursor, role):
    if not (role):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    sql = 'drop role %s' % role

    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg[0] = 'Blergh, something went wrong while dropping the role - %s sql: %s' % (
            error.message,
            sql,
        )
        return False

    msg[0] = 'The role (%s) has been successfully dropped' % role
    return True


def main():
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            role=dict(default=None),
            state=dict(default="present", choices=["present", "absent"]),
            auth=dict(
                default='none',
                choices=["none", "password", "external", "global", "application"],
            ),
            auth_conf=dict(default=None),
        ),
    )

    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    role = module.params["role"]
    state = module.params["state"]
    auth = module.params["auth"]
    auth_conf = module.params["auth_conf"]

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    cursor = conn.cursor()

    if state == 'present':
        if not check_role_exists(module, msg, cursor, role, auth):
            if create_role(module, msg, cursor, role, auth, auth_conf):
                module.exit_json(msg=msg[0], changed=True)
            else:
                module.fail_json(msg=msg[0], changed=False)

        elif modify_role(module, msg, cursor, role, auth, auth_conf):
            module.exit_json(msg=msg[0], changed=True)

        else:
            module.fail_json(msg=msg[0], changed=False)

    elif state == 'absent':
        if check_role_exists(module, msg, cursor, role, auth):
            if drop_role(module, msg, cursor, role):
                module.exit_json(msg=msg[0], changed=True)
        else:
            module.exit_json(msg='The role (%s) doesn\'t exist' % role, changed=False)

    module.exit_json(msg=msg[0], changed=False)


if __name__ == '__main__':
    main()
