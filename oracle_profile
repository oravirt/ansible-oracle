#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_profile
short_description: Manage profiles in an Oracle database
description:
    - Manage profiles in an Oracle database
version_added: "2.4.1.0"
options:
    name:
        description:
            - The name of the profile
        required: true
        default: None
        aliases: ['profile']
    state:
        description:
            - The intended state of the profile.
        default: present
        choices: ['present','absent']
    attribute_name:
        description:
            - The attribute name (e.g PASSWORD_REUSE_TIME)
        default: None
        aliases: ['an']
    attribute_value:
        description:
            - The attribute value (e.g 10)
        default: None
        aliases: ['av']
    username:
        description:
            - The DB username
        required: false
        default: sys
        aliases: ['un']
    password:
        description:
            - The password for the DB user
        required: false
        default: None
        aliases: ['pw']
    service_name:
        description:
            - The profile_name to connect to the database.
        required: false
        aliases: ['sn']
    hostname:
        description:
            - The host of the database if using dbms_profile
        required: false
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port to connect to the database if using dbms_profile
        required: false
        default: 1521
    oracle_home:
        description:
            - The GI ORACLE_HOME
        required: false
        default: None
        aliases: ['oh']



notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Create a profile
- hosts: dbserver
  vars:
      oracle_home: /u01/app/oracle/12.2.0.1/db1
      hostname: "{{ inventory_hostname }}"
      service_name: orclpdb
      user: system
      password: Oracle_123
      oracle_env:
             ORACLE_HOME: "{{ oracle_home }}"
             LD_LIBRARY_PATH: "{{ oracle_home }}/lib"
      profiles:
               - name: profile1
                 attribute_name:
                            - password_reuse_max
                            - password_reuse_time
                            - sessions_per_user
                 attribute_value:
                            - 6
                            - 20
                            - 5
                 state: present
  tasks:
  - name: Manage profiles
    oracle_profile:
            name={{ item.name }}
            attribute_name={{ item.attribute_name}}
            attribute_value={{ item.attribute_value}}
            state={{ item.state }}
            hostname={{ hostname }}
            service_name={{ service_name }}
            user={{ user }}
            password={{ password }}
    environment: "{{oracle_env}}"
    with_items: "{{ profiles }}"

'''
import os

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


# Check if the profile exists
def check_profile_exists(cursor, module, msg, name):

    sql = 'select count(*) from dba_profiles where lower (profile) = \'%s\'' % (name.lower())
    result = execute_sql_get(module, msg, cursor, sql)

    if result[0][0] > 0:
        return True
    else:
        return False

def create_profile(cursor, module, msg, oracle_home, name, attribute_name, attribute_value):

    add_attr = False
    if not any(x == 'None' for x in attribute_name):
        add_attr = True
    if not any(x == None for x in attribute_name):
        add_attr = True

    if add_attr:
        attributes =' '.join([''+str(n)+' '+ str(v) + '' for n,v in zip(attribute_name,attribute_value)])


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

def ensure_profile_state(cursor, module, msg, name, state, attribute_name, attribute_value):
    #pass

    total_sql   = []
    profile_sql    = 'alter profile %s ' % (name.upper())

    # Deal with attribute differences
    if (attribute_name and attribute_value):
        # Make sure attributes are lower case
        attribute_name =  [x.lower() for x in attribute_name]
        attribute_value =  [str(y).lower() for y in attribute_value]
        wanted_attributes = zip(attribute_name,attribute_value)

        # Check the current attributes
        attribute_names_ =','.join(['\''+n[0]+'\'' for n in (wanted_attributes)])
        if len(attribute_names_) != 0:
            current_attributes = get_current_attributes (cursor, module, msg, name, attribute_names_)

            # Convert to dict and compare current with wanted
            if cmp(dict(current_attributes),dict(wanted_attributes)) is not 0:
                for i in wanted_attributes:
                    total_sql.append("alter profile %s limit %s %s " % (name, i[0], i[1]))

    # module.exit_json(msg=total_sql, changed=True)
    if len(total_sql) > 0:
        if ensure_profile_state_sql(module,msg,cursor,total_sql):
            msg = 'profile %s has been put in the intended state' % (name)
            module.exit_json(msg=msg, changed=True)
        else:
            return False
    else:
        msg = 'Nothing to do'
        module.exit_json(msg=msg, changed=False)

def ensure_profile_state_sql(module,msg,cursor,total_sql):

    for sql in total_sql:
        execute_sql(module, msg, cursor, sql)
    return True


def get_current_attributes(cursor, module, msg, name,attribute_names_):


    sql = 'select lower(resource_name),lower(limit) '
    sql += 'from dba_profiles '
    sql += 'where lower(profile) = \'%s\' ' % (name.lower())
    sql += 'and lower(resource_name) in (%s) ' % (attribute_names_.lower())

    result = execute_sql_get(module, msg, cursor, sql)

    return result

def execute_sql_get(module, msg, cursor, sql):

    try:
        cursor.execute(sql)
        result = (cursor.fetchall())
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while executing sql_get - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)
        return False


    return result


def execute_sql(module, msg, cursor, sql):

    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)
        return False
    return True



def main():

    msg = ['']
    cursor = None

    module = AnsibleModule(
        argument_spec = dict(
            name                = dict(required=True, aliases = ['profile']),
            attribute_name      = dict(required=True, type='list', aliases=['an']),
            attribute_value     = dict(required=True, type='list', aliases=['av']),
            state               = dict(default="present", choices = ["present", "absent"]),
            user                = dict(required=False, aliases = ['un','username']),
            password            = dict(required=False, no_log=True, aliases = ['pw']),
            mode                = dict(default='normal', choices=["normal","sysdba"]),
            hostname            = dict(required=False, default = 'localhost', aliases = ['host']),
            port                = dict(required=False, default = 1521),
            service_name        = dict(required=False, aliases = ['sn']),
            oracle_home         = dict(required=False, aliases = ['oh']),



        ),

    )

    name                = module.params["name"]
    attribute_name      = module.params["attribute_name"]
    attribute_value     = module.params["attribute_value"]
    state               = module.params["state"]
    user                = module.params["user"]
    password            = module.params["password"]
    mode                = module.params["mode"]
    hostname            = module.params["hostname"]
    port                = module.params["port"]
    service_name        = module.params["service_name"]
    oracle_home         = module.params["oracle_home"]


    if not cx_oracle_exists:
        msg = "The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set"
        module.fail_json(msg=msg)

    wallet_connect = '/@%s' % service_name
    try:
        if (not user and not password) : # If neither user or password is supplied, the use of an oracle wallet is assumed
            connect = wallet_connect
            if mode == 'sysdba':
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
            else:
                conn = cx_Oracle.connect(wallet_connect)
        elif (user and password):
            dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
            connect = dsn
            if mode == 'sysdba':
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
            else:
                conn = cx_Oracle.connect(user, password, dsn)
        elif (not(user) or not(password)):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Could not connect to DB: %s, connect descriptor: %s, username: %s, pass: %s' % (error.message, connect,user,password)
        module.fail_json(msg=msg, changed=False)

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
             if create_profile(cursor, module, msg, oracle_home, name, attribute_name, attribute_value):
                 msg = 'Successfully created profile %s ' % (name)
                 module.exit_json(msg=msg, changed=True)
             else:
                 module.fail_json(msg=msg, changed=False)
        else:
            ensure_profile_state(cursor, module, msg, name, state, attribute_name, attribute_value)

    elif state == 'absent' :
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




from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
