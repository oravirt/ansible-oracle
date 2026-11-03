#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import os
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)
from binascii import unhexlify

DOCUMENTATION = '''
---
module: oracle_user
short_description: Manage users/schemas in an Oracle database
description:
    - Creates, changes, locks, unlocks, expires and drops users (schemas) in an
      Oracle database.
    - The existence of a user is checked in C(DBA_USERS).
    - User names, tablespaces and profiles are not quoted in the SQL statements,
      so they are always stored in uppercase.
    - Existing users are compared with C(DBA_USERS) (account status, authentication
      type, default and temporary tablespace, profile). If any of these differs,
      one C(ALTER USER) statement with all given attributes is executed.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "1.9.1"
options:
    oracle_home:
        description:
            - The ORACLE_HOME to use. Sets the environment variable E(ORACLE_HOME)
              for the module.
        type: str
        required: false
        aliases: ['oh']
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
            - When connecting with an Oracle wallet, this is the TNS alias of the
              wallet entry.
        type: str
        required: true
        aliases: ['tns']
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
    schema:
        description:
            - The name of the user/schema to manage.
        type: str
        required: true
        aliases: ['name']
    schema_password:
        description:
            - The password of the user (C(IDENTIFIED BY "<password>")).
            - O(schema_password) or O(schema_password_hash) is required when a user
              with O(authentication_type=password) is created.
            - For an existing user, the password is checked against the C(S:) hash in
              C(SYS.USER$.SPARE4). If no C(S:) hash exists, the password is reset on
              every run.
        type: str
        required: false
    schema_password_hash:
        description:
            - The password hash of the user (C(IDENTIFIED BY VALUES '<hash>')).
            - For an existing user, it is compared with the complete content of
              C(SYS.USER$.SPARE4).
        type: str
        required: false
    default_tablespace:
        description:
            - The default tablespace of the user. The tablespace must exist.
            - The user always gets C(QUOTA UNLIMITED) on this tablespace.
        type: str
        required: false
    default_temp_tablespace:
        description:
            - The temporary tablespace of the user. The tablespace must exist.
        type: str
        required: false
    update_password:
        description:
            - V(always) - the password (or the authentication type for
              O(authentication_type=external) or O(authentication_type=global))
              of an existing user is changed if it differs.
            - V(on_create) - the password and authentication type are only set when
              the user is created.
        type: str
        required: false
        default: always
        choices: ['always', 'on_create']
    authentication_type:
        description:
            - The type of authentication for the user.
            - V(password) - C(IDENTIFIED BY), see O(schema_password) and
              O(schema_password_hash).
            - V(external) - C(IDENTIFIED EXTERNALLY).
            - V(global) - C(IDENTIFIED GLOBALLY).
        type: str
        required: false
        default: password
        choices: ['password', 'external', 'global']
    profile:
        description:
            - The profile of the user. The profile must exist.
        type: str
        required: false
    container:
        description:
            - Adds C(CONTAINER=<container>) to the C(CREATE USER) statement,
              e.g. V(all) for a common user in a CDB.
            - Used only when the user is created.
        type: str
        required: false
    container_data:
        description:
            - If set, C(ALTER USER <schema> SET CONTAINER_DATA=<container>
              CONTAINER=CURRENT) is executed after the user has been created.
            - Note that the value of O(container) is used in the statement, not the
              value of this option.
            - Used only when the user is created.
        type: str
        required: false
    grants:
        description:
            - Not implemented. The option is accepted but ignored by the module.
            - Use M(opitzconsulting.ansible_oracle.oracle_grants) to manage
              privileges.
        type: list
        elements: str
        required: false
    state:
        description:
            - V(present) - the user is created if missing. An existing locked user is
              unlocked (C(ACCOUNT UNLOCK)). An expired password stays expired.
            - V(unlocked) - same as V(present).
            - V(locked) - the user is created or changed with C(ACCOUNT LOCK).
              An expired password stays expired.
            - V(expired) - the user is created or changed with C(PASSWORD EXPIRE).
              A lock is not changed.
            - V(expired & locked) - the user is created or changed with
              C(ACCOUNT LOCK PASSWORD EXPIRE).
            - Only the part of C(DBA_USERS.ACCOUNT_STATUS) that belongs to O(state)
              (lock and/or password expiry) is compared. A timed lock after failed
              logins (C(LOCKED(TIMED))) is unlocked by V(present) and replaced by a
              permanent lock with V(locked).
            - V(absent) - the user is dropped with C(DROP USER ... CASCADE). The users
              C(SYS), C(SYSTEM) and C(DBSNMP) are never dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent', 'locked', 'unlocked', 'expired',
                  'expired & locked']
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - The connecting user needs C(SELECT) on C(SYS.USER$) to compare passwords of
      existing users.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Create a schema on a remote database
  opitzconsulting.ansible_oracle.oracle_user:
    hostname: remote-db-server
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    schema: myschema
    schema_password: "{{ myschema_password }}"
    default_tablespace: users
    default_temp_tablespace: temp
    profile: default
    state: present

- name: Create a schema with a password hash, keep the password of existing users
  opitzconsulting.ansible_oracle.oracle_user:
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    schema: myschema
    schema_password_hash: "S:0123456789ABCDEF...;T:0123456789ABCDEF..."
    update_password: on_create

- name: Create a common user in the CDB (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_user:
    service_name: orcl
    mode: sysdba
    schema: c##monitor
    schema_password: "{{ monitor_password }}"
    container: all

- name: Lock a schema
  opitzconsulting.ansible_oracle.oracle_user:
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    schema: myschema
    state: locked

- name: Drop a schema
  opitzconsulting.ansible_oracle.oracle_user:
    hostname: localhost
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    schema: myschema
    state: absent
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
        - When an existing user has been altered, the message contains the executed
          C(ALTER USER) statement.
    returned: always
    type: str
    sample: "The schema myschema has been created successfully"
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


# Check if the user/schema exists
def check_user_exists(module, msg, cursor, schema):
    sql = 'select count(*) from dba_users where username = upper(\'%s\')' % schema

    try:
        cursor.execute(sql)
        result = cursor.fetchone()[0]
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + 'sql: ' + sql
        module.fail_json(msg=msg)

    if result > 0:
        msg = 'The schema (%s) already exists' % schema
        return True


# Create the user/schema
def create_user(
    module,
    cursor,
    schema,
    schema_password,
    schema_password_hash,
    default_tablespace,
    default_temp_tablespace,
    profile,
    authentication_type,
    state,
    container,
    container_data,
    grants,
):
    # grants_list = []
    total_sql = []
    if not (schema):
        msg = 'Error: Missing schema name'
        return False

    if not (schema_password) and authentication_type == 'password':
        if not (schema_password_hash):
            msg = 'Error: Missing schema password or password hash'
            module.fail_json(msg=msg, Changed=False)

    if authentication_type == 'password':
        if schema_password_hash:
            sql = 'create user %s identified by values \'%s\' ' % (
                schema,
                schema_password_hash,
            )
        else:
            sql = 'create user %s identified by \"%s\" ' % (schema, schema_password)
    elif authentication_type == 'global':
        sql = 'create user %s identified globally ' % (schema)
    elif authentication_type == 'external':
        sql = 'create user %s identified externally ' % (schema)

    if default_tablespace:
        sql += 'default tablespace %s ' % default_tablespace
        sql += 'quota unlimited on %s ' % default_tablespace

    if default_temp_tablespace:
        sql += 'temporary tablespace %s ' % default_temp_tablespace

    if profile:
        sql += ' profile %s' % profile

    if container:
        sql += ' container=%s' % (container)

    if state == 'locked':
        sql += ' account lock'

    if state == 'expired':
        sql += ' password expire'

    if state == 'expired & locked':
        sql += ' account lock password expire'

    total_sql.append(sql)

    if container_data:
        altersql = 'alter user %s set container_data=%s container=current' % (
            schema,
            container,
        )
        total_sql.append(altersql)

    # module.exit_json(msg=total_sql, changed=True)
    for a in total_sql:
        execute_sql(module, cursor, a)

    return True


# Get the current password hash for the user
def get_user_password_hash(module, cursor, schema):
    sql = 'select spare4 from sys.user$ where name = upper(\'%s\')' % schema
    try:
        cursor.execute(sql)
        pwhashresult = cursor.fetchone()[0]
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + ': sql: ' + sql
        module.fail_json(msg=msg)

    return pwhashresult


# Check plaintext password against retrieved hash
# currently works with S: hashes only, returns true otherwise
def password_matches_hash(password, password_hash):
    # S: style hash
    if 'S:' in password_hash:
        for ch in password_hash.split('S:')[1][:60].upper():
            if (ch < '0' or ch > '9') and (ch < 'A' or ch > 'F'):
                return (
                    False  # not a valid hex string character found, should not happen
                )
        hash = password_hash.split('S:')[1][:40]
        salt = password_hash.split('S:')[1][40:60]
        sha1 = hashlib.sha1()
        sha1.update(password.encode('utf-8'))
        sha1.update(unhexlify(salt))
        return hash.upper() == sha1.hexdigest().upper()

    # no supported hashes found
    return False


# Modify the user/schema
def modify_user(
    module,
    cursor,
    schema,
    schema_password,
    schema_password_hash,
    default_tablespace,
    default_temp_tablespace,
    update_password,
    profile,
    authentication_type,
    state,
    container_data,
):
    sql_get_curr_def = 'select lower(account_status)'
    sql = 'alter user %s' % schema
    pw_change_needed = False

    if update_password == 'always':
        if authentication_type == 'password':
            old_pw_hash = get_user_password_hash(module, cursor, schema)
            if schema_password_hash and (old_pw_hash != schema_password_hash):
                pw_change_needed = True
                sql += ' identified by values \'%s\'' % (schema_password_hash)
            elif schema_password and not password_matches_hash(
                schema_password, old_pw_hash
            ):
                pw_change_needed = True
                sql += ' identified by \"%s\" ' % (schema_password)
        elif authentication_type == 'external':
            sql += ' identified externally '
            sql_get_curr_def += ' ,lower(authentication_type)'
        elif authentication_type == 'global':
            sql += ' identified globally '
            sql_get_curr_def += ' ,lower(authentication_type)'

    if default_tablespace:
        sql += ' default tablespace %s' % default_tablespace
        sql += ' quota unlimited on %s ' % default_tablespace
        sql_get_curr_def += ' ,lower(default_tablespace)'

    if default_temp_tablespace:
        sql += ' temporary tablespace %s ' % default_temp_tablespace
        sql_get_curr_def += ' ,lower(temporary_tablespace)'

    if profile:
        sql += ' profile %s ' % profile
        sql_get_curr_def += ' ,lower(profile)'

    if state == 'present' or state == 'unlocked':
        sql += ' account unlock'

    elif state == 'locked':
        sql += ' account lock'

    elif state == 'expired':
        sql += ' password expire'

    elif state == 'expired & locked':
        sql += ' account lock password expire'

    wanted_list = []

    if authentication_type != 'password' and update_password == 'always':
        wanted_list.append(authentication_type)

    if default_tablespace:
        wanted_list.append(default_tablespace)

    if default_temp_tablespace:
        wanted_list.append(default_temp_tablespace)

    if profile:
        wanted_list.append(profile)

    sql_get_curr_def += ' from dba_users where username = upper(\'%s\')' % schema

    wanted_list = [x.lower() for x in wanted_list]
    curr_defaults = execute_sql_get(module, cursor, sql_get_curr_def)
    curr_defaults = [list(t) for t in curr_defaults]

    # the first column is the account status, it is compared separately
    if (
        curr_defaults
        and account_status_matches(state, curr_defaults[0][0])
        and (wanted_list == curr_defaults[0][1:])
    ):
        if update_password == 'always' and pw_change_needed:
            execute_sql(module, cursor, sql)
            module.exit_json(
                msg='Successfully altered the user password (%s)' % (schema),
                changed=True,
            )
        else:
            module.exit_json(
                msg='The schema (%s) is in the intented state' % (schema), changed=False
            )
    else:
        # do the complete change -> exit with change=True
        # module.exit_json(msg=sql)
        execute_sql(module, cursor, sql)
        module.exit_json(
            msg='Successfully altered the user (%s, %s)' % (schema, sql), changed=True
        )

    return True


def account_status_matches(state, account_status):
    # account_status: DBA_USERS.ACCOUNT_STATUS in lower case, e.g. 'open',
    # 'expired & locked', 'locked(timed)', 'expired(grace)', 'open & in rollover'
    parts = [p.strip() for p in account_status.split('&')]
    locked = 'locked' in parts
    timed_locked = any(p.startswith('locked(') for p in parts)
    expired = 'expired' in parts

    if state in ('present', 'unlocked'):
        return not locked and not timed_locked
    if state == 'locked':
        return locked
    if state == 'expired':
        return expired
    if state == 'expired & locked':
        return expired and locked
    return True


# Run the actual modification
def execute_sql(module, cursor, sql):
    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Blergh, something went wrong while executing sql - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)

    return True


def execute_sql_get(module, cursor, sql):
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + ': sql: ' + sql
        module.fail_json(msg=msg)

    return result


# Drop the user
def drop_user(module, cursor, schema):
    black_list = ['sys', 'system', 'dbsnmp']
    if schema.lower() in black_list:
        msg = 'Trying to drop an internal user: %s. Not allowed' % schema
        return False

    sql = 'drop user %s cascade' % schema

    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Blergh, something went wrong while dropping the schema - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg)

    return True


def main():
    msg = ['']

    module = AnsibleModule(
        argument_spec=dict(
            oracle_home=dict(required=False, aliases=['oh']),
            hostname=dict(default='localhost'),
            port=dict(default=1521),
            service_name=dict(required=True, aliases=['tns']),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            schema=dict(required=True, aliases=['name']),
            schema_password=dict(default=None, no_log=True),
            schema_password_hash=dict(default=None, no_log=True),
            state=dict(
                default="present",
                choices=[
                    "present",
                    "absent",
                    "locked",
                    "unlocked",
                    "expired",
                    "expired & locked",
                ],
            ),
            default_tablespace=dict(default=None),
            default_temp_tablespace=dict(default=None),
            update_password=dict(
                default='always', choices=['on_create', 'always'], no_log=False
            ),
            profile=dict(default=None),
            authentication_type=dict(
                default='password', choices=['password', 'external', 'global']
            ),
            container=dict(default=None),
            container_data=dict(default=None),
            grants=dict(default=None, type="list"),
        ),
        mutually_exclusive=[['schema_password', 'schema_password_hash']],
    )

    oracle_home = module.params["oracle_home"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    schema = module.params["schema"]
    schema_password = module.params["schema_password"]
    schema_password_hash = module.params["schema_password_hash"]
    state = module.params["state"]
    default_tablespace = module.params["default_tablespace"]
    default_temp_tablespace = module.params["default_temp_tablespace"]
    update_password = module.params["update_password"]
    profile = module.params["profile"]
    authentication_type = module.params["authentication_type"]
    container = module.params["container"]
    container_data = module.params["container_data"]
    grants = module.params["grants"]

    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home.rstrip('/')
        # os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    cursor = conn.cursor()

    if state not in ('absent'):
        if not check_user_exists(module, msg, cursor, schema):
            if create_user(
                module,
                cursor,
                schema,
                schema_password,
                schema_password_hash,
                default_tablespace,
                default_temp_tablespace,
                profile,
                authentication_type,
                state,
                container,
                container_data,
                grants,
            ):
                msg = 'The schema %s has been created successfully' % (schema)
                module.exit_json(msg=msg, changed=True)
        else:
            modify_user(
                module,
                cursor,
                schema,
                schema_password,
                schema_password_hash,
                default_tablespace,
                default_temp_tablespace,
                update_password,
                profile,
                authentication_type,
                state,
                container_data,
            )

    # elif state in ('unlocked','locked', ''):
    # 	if not check_user_exists(module, msg, cursor, schema):
    # 		# if create_user(module, cursor, schema, schema_password, schema_password_hash,
    #       # default_tablespace, default_temp_tablespace, profile,
    #       # authentication_type, state, container, grants):
    # 		msg = 'The schema %s doesn\'t exist' % schema
    # 		module.fail_json(msg=msg, changed=False)
    # 	else:
    # 		modify_user(
    #           module, cursor, schema, schema_password, schema_password_hash,
    #           default_tablespace, default_temp_tablespace, update_password, profile,
    #           authentication_type, state)

    elif state == 'absent':
        if check_user_exists(module, msg, cursor, schema):
            if drop_user(module, cursor, schema):
                msg = 'The schema (%s) has been dropped successfully' % schema
                module.exit_json(msg=msg, changed=True)
        else:
            module.exit_json(
                msg='The schema (%s) doesn\'t exist' % schema, changed=False
            )

    module.exit_json(msg='Undhandled exit', changed=False)


if __name__ == '__main__':
    main()
