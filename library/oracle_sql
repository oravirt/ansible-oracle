#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_sql
short_description: Execute arbitrary sql
description:
    - Execute arbitrary sql against an Oracle database
version_added: "2.1.0.0"
options:
    username:
        description:
            - The database username to connect to the database
        required: false
        default: None
        aliases: ['un']
    password:
        description:
            - The password to connect to the database
        required: false
        default: None
        aliases: ['pw']
    service_name:
        description:
            - The service_name to connect to the database
        required: false
        default: database_name
        aliases: ['sn']
    hostname:
        description:
            - The host of the database
        required: false
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port to connect to the database
        required: false
        default: 1521
    sql:
        description:
            - The sql you want to execute
        required: false
    script:
        description:
            - The script you want to execute. Doesn't handle selects
        required: false
notes:
    - cx_Oracle needs to be installed
    - Oracle client libraries need to be installed along with ORACLE_HOME and LD_LIBRARY_PATH settings.
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Execute arbitrary sql
- oracle_sql:
    username: "{{ user }}"
    password: "{{ password }}"
    service_name: one.world
    sql: 'select username from dba_users'
# Execute arbitrary script1
- oracle_sql:
    username: "{{ user }}"
    password: "{{ password }}"
    service_name: one.world
    script: /u01/scripts/create-all-the-procedures.sql
# Execute arbitrary script2
- oracle_sql:
    username: "{{ user }}"
    password: "{{ password }}"
    service_name: one.world
    script: /u01/scripts/create-tables-and-insert-default-values.sql
'''
import os
from ansible.module_utils.basic import AnsibleModule

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def execute_sql_get(module, cursor, sql):
    try:
        cursor.execute(sql)
        result = (cursor.fetchall())
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while executing sql_get - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)
        return False
    return result


def execute_sql(module, cursor, conn, sql):
    if 'insert' or 'delete' or 'update' in sql.lower():
        docommit = True
    else:
        docommit = False

    try:
        # module.exit_json(msg=sql.strip())
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (error.message, sql)
        module.fail_json(msg=msg, changed=False)
        return False
    if docommit:
        conn.commit()
    return True


def read_file(module, script):
    try:
        f = open(script, 'r')
        sqlfile = f.read()
        f.close()
        return sqlfile
    except IOError as e:
        msg = 'Couldn\'t open/read file: %s' % (e)
        module.fail_json(msg=msg, changed=False)
    return


def clean_sqlfile(sqlfile):
    sqlfile = sqlfile.strip()
    sqlfile = sqlfile.lstrip()
    sqlfile = sqlfile.lstrip()
    sqlfile = os.linesep.join([s for s in sqlfile.splitlines() if s])
    return sqlfile


def main():

    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=False, aliases=['un', 'username']),
            password=dict(required=False, no_log=True, aliases=['pw']),
            mode=dict(default="normal", choices=["sysasm", "sysdba", "normal"]),
            service_name=dict(required=False, aliases=['sn']),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            port=dict(required=False, default=1521),
            sql=dict(required=False),
            script=dict(required=False),

        ),
        mutually_exclusive=[['sql', 'script']]
    )

    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    service_name = module.params["service_name"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    sql = module.params["sql"]
    script = module.params["script"]

    if not cx_oracle_exists:
        msg = "The cx_Oracle module is required. Also set LD_LIBRARY_PATH & ORACLE_HOME"
        module.fail_json(msg=msg)

    wallet_connect = '/@%s' % service_name

    try:
        if not user and not password:  # If neither user or password is supplied, the use of an oracle wallet is assumed
            if mode == 'sysdba':
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
            elif mode == 'sysasm':
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSASM)
            else:
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect)

        elif user and password:
            if mode == 'sysdba':
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
            elif mode == 'sysasm':
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSASM)
            else:
                dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn)

        elif not user or not password:
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        msg = 'Could not connect to database - %s, connect descriptor: %s' % (error.message, connect)
        module.fail_json(msg=msg, changed=False)

    cursor = conn.cursor()

    if sql:
        if sql.lower().startswith('begin '):
            execute_sql(module, cursor, conn, sql)
            msg = 'SQL executed: %s' % (sql)
            module.exit_json(msg=msg, changed=True)

        else:
            sql = sql.rstrip(';')
            if sql.lower().startswith('select '):
                result = execute_sql_get(module, cursor, sql)
                module.exit_json(msg=result, changed=False)
            else:
                execute_sql(module, cursor, conn, sql)
                msg = 'SQL executed: %s' % (sql)
                module.exit_json(msg=msg, changed=True)
    else:
        sqlfile = read_file(module, script)
        if len(sqlfile) > 0:
            sqlfile = clean_sqlfile(sqlfile)
            
            if sqlfile.endswith('/') or ('create or replace') in sqlfile.lower():
                sqldelim = '/'
            else:
                sqldelim = ';'
            
            sqlfile = sqlfile.strip(sqldelim)
            sql = sqlfile.split(sqldelim)
            
            for q in sql:
                execute_sql(module, cursor, conn, q)
            msg = 'Finished running script %s \nContents: \n%s' % (script, sqlfile)
            module.exit_json(msg=msg, changed=True)
        else:
            module.fail_json(msg='SQL file seems to be empty')

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
