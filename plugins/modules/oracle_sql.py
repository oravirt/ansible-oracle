#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_sql
short_description: Execute SQL statements or SQL scripts in an Oracle database
description:
    - Executes a single SQL statement or PL/SQL block (O(sql)) or all statements of a
      SQL script file (O(script)) in an Oracle database.
    - The module is not idempotent. Every run executes the SQL and reports
      C(changed=true), except for a single C(SELECT) statement in O(sql).
    - Every executed statement is followed by a C(COMMIT).
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "2.1.0.0"
options:
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
        choices: ['normal', 'sysdba', 'sysasm']
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
    sql:
        description:
            - A single SQL statement or PL/SQL block to execute.
            - A statement starting with C(begin ) (case-insensitive) is executed as
              PL/SQL block unchanged.
            - For all other statements trailing C(;) characters are removed.
            - A statement starting with C(select ) (case-insensitive) is executed as
              query, the result rows are returned in RV(msg) and C(changed=false) is
              reported.
            - Any other statement is executed and C(changed=true) is reported.
            - Mutually exclusive with O(script). One of O(sql) or O(script) is required
              in practice, although not enforced by the argument spec.
        type: str
        required: false
    script:
        description:
            - Path to a SQL script file on the managed node whose statements are
              executed one after another.
            - Empty lines and leading/trailing whitespace are removed from the script.
            - The statement delimiter is C(/) if the script ends with C(/) or contains
              C(create or replace) anywhere (case-insensitive), otherwise C(;).
              Delimiters inside single or double quotes are ignored.
            - Results of C(SELECT) statements in the script are not returned.
            - The module fails if the file is empty.
            - Mutually exclusive with O(sql).
        type: str
        required: false
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Oracle client libraries need to be installed along with ORACLE_HOME and
      LD_LIBRARY_PATH settings.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Query the database users
  opitzconsulting.ansible_oracle.oracle_sql:
    user: system
    password: "{{ system_password }}"
    hostname: dbhost
    service_name: orclpdb
    sql: select username from dba_users
  register: users

- name: Execute a PL/SQL block as SYSDBA
  opitzconsulting.ansible_oracle.oracle_sql:
    user: sys
    password: "{{ sys_password }}"
    mode: sysdba
    service_name: orclpdb
    sql: "begin dbms_stats.gather_schema_stats('APP'); end;"

- name: Execute a SQL script (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_sql:
    service_name: orclpdb
    script: /u01/scripts/create-tables-and-insert-default-values.sql

- name: Execute a script with PL/SQL objects delimited by /
  opitzconsulting.ansible_oracle.oracle_sql:
    user: app
    password: "{{ app_password }}"
    service_name: orclpdb
    script: /u01/scripts/create-all-the-procedures.sql
'''

RETURN = '''
msg:
    description:
        - For a C(SELECT) statement in O(sql), the list of result rows (each row
          is a list of column values).
        - Otherwise a message with the executed statement or the script name and
          the cleaned script contents.
    returned: always
    type: raw
    sample: [["SYS"], ["SYSTEM"]]
'''


def execute_sql_get(module, cursor, sql):
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


def execute_sql(module, cursor, conn, sql):
    if 'insert' or 'delete' or 'update' in sql.lower():
        docommit = True
    else:
        docommit = False

    try:
        # module.exit_json(msg=sql.strip())
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (
            error.message,
            sql,
        )
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
        mutually_exclusive=[['sql', 'script']],
    )

    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    service_name = module.params["service_name"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    sql = module.params["sql"]
    script = module.params["script"]

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
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

            # fixed problems with quoted sqldelim using
            # https://stackoverflow.com/questions/2785755/how-to-split-but-ignore-separators-in-quoted-strings-in-python
            PATTERN = re.compile(
                r'''((?:[^''' + sqldelim + r'''"']|"[^"]*"|'[^']*')+)'''
            )
            sqlfile = sqlfile.strip(sqldelim)
            sql = PATTERN.split(sqlfile)[1::2]

            for q in sql:
                execute_sql(module, cursor, conn, q)
            msg = 'Finished running script %s \nContents: \n%s' % (script, sqlfile)
            module.exit_json(msg=msg, changed=True)
        else:
            module.fail_json(msg='SQL file seems to be empty')

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
