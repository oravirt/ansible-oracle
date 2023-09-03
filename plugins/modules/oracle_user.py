#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import os
from ansible.module_utils.basic import AnsibleModule
from binascii import unhexlify

DOCUMENTATION = '''
---
module: oracle_user
short_description: Manage users/schemas in an Oracle database
description:
    - Manage users/schemas in an Oracle database
    - Can be run locally on the controlmachine or on a remote host
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
        required: false
    password:
        description: The Oracle user password for 'user'
        required: false
    mode:
        description: The mode with which to connect to the database
        required: false
        default: normal
        choices: ['normal','sysdba']
    schema:
        description: The schema that you want to manage
        required: false
        default: None
    schema_password:
        description: The password for the new schema. i.e '..identified by password'
        required: false
        default: null
    schema_password_hash:
        description: >
            The password hash for the new schema.
            i.e '..identified by values 'XXXXXXX'
        required: false
        default: None
    default_tablespace:
        description: >
            The default tablespace for the new schema. The tablespace must exist
        required: false
        default: None
    default_temp_tablespace:
        description: >
            The default tablespace for the new schema. The tablespace must exist
        required: false
        default: None
    update_password:
        description: >
            always will update passwords if they differ. on_create will only set the
            password for newly created users.
        required: false
        default: always
        choices: ['always','on_create']
    authentication_type:
        description: The type of authentication for the user.
        required: false
        default: password
        choices: ['password','external','global']
    profile:
        description: The profile for the user
        required: false
        default: None
    grants:
        description: The privileges granted to the new schema
        required: false
        default: None
    state:
        description: >
            Whether the user should exist. Absent removes the user, locked/unlocked
            locks or unlocks the user
        required: False
        default: present
        choices: ['present','absent','locked','unlocked']
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Create a new schema on a remote db by running the module on the controlmachine
# (i.e: delegate_to: localhost)
oracle_user:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: manager
    schema: myschema
    schema_password: mypass
    default_tablespace: test
    state: present
    grants: "'create session', create any table'"

# Create a new schema on a remote db
oracle_user:
    hostname: localhost
    service_name: orcl
    user: system
    password: manager
    schema: myschema
    schema_password: mypass
    default_tablespace: test
    state: present
    grants: dba

# Drop a schema on a remote db
oracle_user:
    hostname: localhost
    service_name: orcl
    user: system
    password: manager
    schema: myschema
    state: absent
'''


try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


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
    except cx_Oracle.DatabaseError as exc:
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
    except cx_Oracle.DatabaseError as exc:
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

    want_account_status = ''
    if state == 'present' or state == 'unlocked':
        want_account_status = 'open'
        sql += ' account unlock'

    elif state == 'locked':
        want_account_status = state
        sql += ' account lock'

    elif state == 'expired':
        want_account_status = state
        sql += ' password expire'

    elif state == 'expired & locked':
        want_account_status = state
        sql += ' account lock password expire'

    wanted_list = []
    wanted_list.append(want_account_status)

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

    if wanted_list in curr_defaults:
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


# Run the actual modification
def execute_sql(module, cursor, sql):
    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
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
    except cx_Oracle.DatabaseError as exc:
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
    except cx_Oracle.DatabaseError as exc:
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
            schema=dict(default=None, aliases=['name']),
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

    if not cx_oracle_exists:
        module.fail_json(
            msg=(
                "The cx_Oracle module is required. "
                "'pip install cx_Oracle' should do the trick. "
                "If cx_Oracle is installed, make sure ORACLE_HOME "
                "& LD_LIBRARY_PATH is set"
            )
        )

    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home.rstrip('/')
        # os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']

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
