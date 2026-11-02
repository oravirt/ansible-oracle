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
module: oracle_profile
short_description: Manage profiles in an Oracle database
description:
    - Creates, changes and drops profiles (C(CREATE PROFILE)) in an Oracle database.
    - The existence of a profile is checked in C(DBA_PROFILES). The profile name is
      not quoted in the SQL statements, so it is always stored in uppercase.
    - O(attribute_name) and O(attribute_value) are matched by position, i.e. the
      first name gets the first value and so on.
    - A new profile is created with all given attributes in one
      C(CREATE PROFILE ... LIMIT) statement.
    - For an existing profile, the given attributes are compared with
      C(DBA_PROFILES.LIMIT) (case-insensitive). If they differ, an
      C(ALTER PROFILE ... LIMIT) statement is executed for every given attribute.
      Attributes that are not given are not changed.
    - Due to a bug in the comparison, the C(ALTER PROFILE) statements are currently
      executed on every run for an existing profile and C(changed=true) is returned.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "2.4.1.0"
options:
    name:
        description:
            - The name of the profile.
        type: str
        required: true
        aliases: ['profile']
    state:
        description:
            - V(present) - the profile is created or its attributes are changed.
            - V(absent) - the profile is dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
    attribute_name:
        description:
            - The list of resource or password parameters of the profile
              (e.g. V(password_reuse_time)).
            - Required also for O(state=absent).
        type: list
        elements: str
        required: true
        aliases: ['an']
    attribute_value:
        description:
            - The list of values for the attributes in O(attribute_name), in the
              same order (e.g. V(10), V(unlimited) or V(default)).
            - Required also for O(state=absent).
        type: list
        elements: str
        required: true
        aliases: ['av']
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
            - The database service name to connect to.
            - When connecting with an Oracle wallet, this is the TNS alias of the wallet
              entry.
            - Required in practice, although not enforced by the argument spec.
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
    oracle_home:
        description:
            - The ORACLE_HOME. It is set as environment variable C(ORACLE_HOME) after
              the database connection has been established.
            - If omitted, the environment variable C(ORACLE_HOME) must be set,
              otherwise the module fails.
        type: str
        required: false
        aliases: ['oh']
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
- name: Create profile PROFILE1
  opitzconsulting.ansible_oracle.oracle_profile:
    hostname: dbhost
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    name: profile1
    attribute_name:
      - password_reuse_max
      - password_reuse_time
      - sessions_per_user
    attribute_value:
      - 6
      - 20
      - 5
    state: present
  environment:
    ORACLE_HOME: /u01/app/oracle/12.2.0.1/db1
    LD_LIBRARY_PATH: /u01/app/oracle/12.2.0.1/db1/lib

- name: Drop profile PROFILE1 (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_profile:
    service_name: orclpdb
    oracle_home: /u01/app/oracle/12.2.0.1/db1
    name: profile1
    attribute_name: []
    attribute_value: []
    state: absent
'''

RETURN = '''
msg:
    description: Message describing the action that was executed.
    returned: always
    type: str
    sample: "Successfully created profile profile1 "
'''


# Check if the profile exists
def check_profile_exists(cursor, module, msg, name):
    sql = 'select count(*) from dba_profiles where lower (profile) = \'%s\'' % (
        name.lower()
    )
    result = execute_sql_get(module, msg, cursor, sql)

    if result[0][0] > 0:
        return True
    else:
        return False


def create_profile(
    cursor, module, msg, oracle_home, name, attribute_name, attribute_value
):
    add_attr = False
    if not any(x == 'None' for x in attribute_name):
        add_attr = True
    if not any(x is None for x in attribute_name):
        add_attr = True

    if add_attr:
        attributes = ' '.join(
            [
                '' + str(n) + ' ' + str(v) + ''
                for n, v in zip(attribute_name, attribute_value)
            ]
        )

    sql = 'create profile %s limit ' % (name)
    if add_attr:
        sql += ' %s' % (attributes.lower())

    if execute_sql(module, msg, cursor, sql):
        return True
    else:
        return False


def remove_profile(cursor, module, msg, oracle_home, name):
    dropsql = 'drop profile %s' % (name)
    if execute_sql(module, msg, cursor, dropsql):
        return True
    else:
        return False


def ensure_profile_state(
    cursor, module, msg, name, state, attribute_name, attribute_value
):
    # pass

    total_sql = []

    # Deal with attribute differences
    if attribute_name and attribute_value:
        # Make sure attributes are lower case
        attribute_name = [x.lower() for x in attribute_name]
        attribute_value = [str(y).lower() for y in attribute_value]
        wanted_attributes = zip(attribute_name, attribute_value)

        # Check the current attributes
        attribute_names_ = ','.join(['\'' + n[0] + '\'' for n in (wanted_attributes)])
        if len(attribute_names_) != 0:
            current_attributes = get_current_attributes(
                cursor, module, msg, name, attribute_names_
            )

            # Convert to dict and compare current with wanted
            if dict(current_attributes) != dict(wanted_attributes):
                for i, v in zip(attribute_name, attribute_value):
                    total_sql.append("alter profile %s limit %s %s " % (name, i, v))

    # module.exit_json(msg=total_sql, changed=True)
    if len(total_sql) > 0:
        if ensure_profile_state_sql(module, msg, cursor, total_sql):
            msg = 'profile %s has been put in the intended state' % (name)
            module.exit_json(msg=msg, changed=True)
        else:
            return False
    else:
        msg = 'Nothing to do'
        module.exit_json(msg=msg, changed=False)


def ensure_profile_state_sql(module, msg, cursor, total_sql):
    for sql in total_sql:
        execute_sql(module, msg, cursor, sql)
    return True


def get_current_attributes(cursor, module, msg, name, attribute_names_):
    sql = 'select lower(resource_name),lower(limit) '
    sql += 'from dba_profiles '
    sql += 'where lower(profile) = \'%s\' ' % (name.lower())
    sql += 'and lower(resource_name) in (%s) ' % (attribute_names_.lower())

    result = execute_sql_get(module, msg, cursor, sql)

    return result


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
    msg = ['']
    cursor = None

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['profile']),
            attribute_name=dict(required=True, type='list', aliases=['an']),
            attribute_value=dict(required=True, type='list', aliases=['av']),
            state=dict(default="present", choices=["present", "absent"]),
            user=dict(required=False, aliases=['un', 'username']),
            password=dict(required=False, no_log=True, aliases=['pw']),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            port=dict(required=False, default=1521),
            service_name=dict(required=False, aliases=['sn']),
            oracle_home=dict(required=False, aliases=['oh']),
        ),
    )

    name = module.params["name"]
    attribute_name = module.params["attribute_name"]
    attribute_value = module.params["attribute_value"]
    state = module.params["state"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    oracle_home = module.params["oracle_home"]

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    cursor = conn.cursor()

    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg, changed=False)

    if state == 'present':
        if not check_profile_exists(cursor, module, msg, name):
            if create_profile(
                cursor, module, msg, oracle_home, name, attribute_name, attribute_value
            ):
                msg = 'Successfully created profile %s ' % (name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            ensure_profile_state(
                cursor, module, msg, name, state, attribute_name, attribute_value
            )

    elif state == 'absent':
        if check_profile_exists(cursor, module, msg, name):
            if remove_profile(cursor, module, msg, oracle_home, name):
                msg = 'Profile %s successfully removed' % (name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.exit_json(msg=msg, changed=False)
        else:
            msg = 'Profile %s doesn\'t exist' % (name)
            module.exit_json(msg=msg, changed=False)

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
