#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_role
short_description: Manage users/roles in an Oracle database
description:
    - Manage grants/privileges in an Oracle database
    - Handles role/sys privileges at the moment.
    - It is possible to add object privileges as well, but they are not considered when removing privs at the moment.
version_added: "1.9.1"
options:
    hostname:
        description:
            - The Oracle database host
        required: false
        default: localhost
    port:
        description:
            - The listener port number on the host
        required: false
        default: 1521
    service_name:
        description:
            - The database service name to connect to
        required: true
    user:
        description:
            - The Oracle user name to connect to the database
        required: true
    password:
        description:
            - The Oracle user password for 'user'
        required: true
    mode:
        description:
            - The mode with which to connect to the database
        required: true
        default: normal
        choices: ['normal','sysdba']
    role:
        description:
            - The role that should get grants added/removed
        required: false
        default: null
    grants:
        description:
            - The privileges granted to the new role. Can be a string or a list
        required: false
        default: null
    state:
        description:
            - The intended state of the priv (present=added to the user, absent=removed from the user). REMOVEALL will remove ALL role/sys privileges
        default: present
        choices: ['present','absent','REMOVEALL']
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Add grants to the user
oracle_role: hostname=remote-db-server service_name=orcl user=system password=manager role=myrole state=present grants='create session','create any table',connect,resource

# Revoke the 'create any table' grant
oracle_role: hostname=localhost service_name=orcl user=system password=manager role=myrole state=absent grants='create any table'

# Remove all grants from a user
oracle_role: hostname=localhost service_name=orcl user=system password=manager role=myrole state=REMOVEALL grants=


'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def clean_string(item):
    item = item.replace("'","").replace(", ",",").lstrip(" ").rstrip(",").replace("[","").replace("]","")

    return item

def clean_list(item):
    item = [p.replace("'","").replace(", ",",").lstrip(" ").rstrip(",").replace("[","").replace("]","") for p in item]

    return item



# Check if the user/role exists
def check_role_exists(module, msg, cursor, role, auth):

    if not(role):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    role = clean_string(role)
    #sql = 'select count(*) from dba_roles where role = upper(\'%s\')' % role
    sql = 'select lower(role), lower(authentication_type) from dba_roles where role = upper(\'%s\')' % role


    try:
            cursor.execute(sql)
            result = (cursor.fetchone())
    except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            msg[0] = error.message+ 'sql: ' + sql
            return False

    if result > 0:

        msg[0] = 'The role (%s) already exists' % role
        return True


# Create the role
def create_role(module, msg, cursor, role, auth, auth_conf):

    if not(role) or not (auth):
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
            module.fail_json(msg='Missing authentication package (schema.name)', changed=False)
            return False
        else:
            sql += 'identified using %s' % auth_conf

    if auth == 'external':
        sql += 'identified externally '

    if auth == 'global':
        sql += 'identified globally'




    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg[0] = 'Blergh, something went wrong while creating the role - %s sql: %s' % (error.message, sql)
        return False

    msg[0] = 'The role (%s) has been created successfully, authentication: %s' % (role, auth)
    return True


def modify_role(module, msg, cursor, role, auth, auth_conf):

    if not(role) or not (auth):
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
                module.fail_json(msg='Missing password for authentication_type %s' % (auth), changed=False)
                return False
            else:
                sql += ' identified by %s' % auth_conf

        if auth == 'application':
            if not (auth_conf):
                module.fail_json(msg='Missing authentication package (schema.name)', changed=False)
                return False
            else:
                sql += 'identified using %s' % auth_conf

        if auth == 'external':
            sql += 'identified externally '

        if auth == 'global':
            sql += 'identified globally'


        try:
            cursor.execute(sql)
        except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            msg[0] = 'Blergh, something went wrong while altering the role - %s sql: %s' % (error.message, sql)
            return False

        msg[0] = 'The role (%s) has been changed successfully, authentication: %s, previous: %s' % (role, auth, currauth)
    return True



def get_role_specs(module, msg, cursor, role):

    sql = 'select lower(authentication_type) from dba_roles where role = upper(\'%s\')' % role


    try:
        cursor.execute(sql)
        result = (cursor.fetchall()[0][0])
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg[0] = 'Blergh, something went wrong while getting the role auth scheme - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg[0], changed=False)
        return False

    #module.exit_json(msg='Result: %s, sql: %s' % (result, sql), changed=False)
    return result


# Create the role
def drop_role(module, msg, cursor, role):

    if not(role):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False


    sql = 'drop role %s' % role

    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg[0] = 'Blergh, something went wrong while dropping the role - %s sql: %s' % (error.message, sql)
        return False

    msg[0] = 'The role (%s) has been successfully dropped' % role
    return True


def main():

    msg = ['']
    module = AnsibleModule(
        argument_spec = dict(
            hostname      = dict(default='localhost'),
            port          = dict(default=1521),
            service_name  = dict(required=True),
            user          = dict(required=False),
            password      = dict(required=False, no_log=True),
            mode          = dict(default='normal', choices=["normal","sysdba"]),
            role          = dict(default=None),
            state         = dict(default="present", choices=["present", "absent"]),
            auth          = dict(default='none', choices=["none", "password", "external", "global", "application"]),
            auth_conf     = dict(default=None)

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



    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")

    wallet_connect = '/@%s' % service_name
    try:
        if (not user and not password ): # If neither user or password is supplied, the use of an oracle wallet is assumed
            if mode == 'sysdba':
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
            else:
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect)

        elif (user and password ):
            if mode == 'sysdba':
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
            else:
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn)

        elif (not(user) or not(password)):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg[0] = 'Could not connect to database - %s, connect descriptor: %s' % (error.message, connect)
        module.fail_json(msg=msg[0], changed=False)

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






from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
