#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_facts
short_description: Returns some facts about Oracle DB
description:
    - Returns some facts about Oracle DB
version_added: "2.2.1"
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
            - The Oracle user name to connect to the database, must have DBA privilege
        required: False
    password:
        description:
            - The Oracle user password for 'user'
        required: False
    mode:
        description:
            - The mode with which to connect to the database
        required: false
        default: normal
        choices:
            - normal
            - sysdba
notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
requirements: [ "cx_Oracle" ]
author: Ilmar Kerm, ilmar.kerm@gmail.com, @ilmarkerm
'''

EXAMPLES = '''
- hosts: localhost
  vars:
    oraclehost: 192.168.56.101
    oracleport: 1521
    oracleservice: orcl
    oracleuser: system
    oraclepassword: oracle
    oracle_env:
      ORACLE_HOME: /usr/lib/oracle/12.1/client64
      LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib
  tasks:
    - name: gather database facts
      oracle_facts:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
      register: dbfacts
    - debug:
        var: dbfacts
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]

def query_result(query):
    c = conn.cursor()
    c.execute(query)
    res = rows_to_dict_list(c)
    c.close()
    return res

def star_query(rowsource):
    return query_result("SELECT * FROM %s" % rowsource)

# Ansible code
def main():
    global conn
    msg = ['']
    module = AnsibleModule(
        argument_spec = dict(
            hostname      = dict(default='localhost'),
            port          = dict(default=1521, type='int'),
            service_name  = dict(required=True),
            user          = dict(required=False),
            password      = dict(required=False),
            mode          = dict(default='normal', choices=["normal","sysdba"])
        ),
        supports_check_mode=True
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    # Connect to database
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
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
    if conn.version < "10.2":
        module.fail_json(msg="Database version must be 10gR2 or greater", changed=False)
    #
    if module.check_mode:
        module.exit_json(changed=False)
    #
    facts = { 'version': conn.version }
    # Execute PL/SQL to return some additional facts
    database = star_query('v$database')[0]
    instance = star_query('v$instance')[0]
    if 'CDB' not in database:
        database.update({'CDB': 'NO'})
    #
    try:
        rac = query_result("SELECT inst_id, instance_name, host_name, startup_time FROM gv$instance ORDER BY inst_id")
    except:
        rac = []
    try:
        if database['CDB'] == 'YES':
            pdb = query_result("SELECT con_id, rawtohex(guid) guid_hex, name, open_mode FROM v$pdbs ORDER BY name")
        else:
            pdb = []
    except:
        pdb = []
    if conn.version >= '12.1':
        tablespace = query_result("select ts.con_id, ts.name, ts.bigfile, round(sum(bytes)/1024/1024) size_mb, count(*) datafiles# from v$tablespace ts join v$datafile df on df.ts#=ts.ts# and df.con_id=ts.con_id group by ts.name, ts.bigfile, ts.con_id order by 1,2")
        temp_tablespace = query_result("select ts.con_id, ts.name, ts.bigfile, round(sum(bytes)/1024/1024) size_mb, count(*) tempfiles# from v$tablespace ts join v$tempfile df on df.ts#=ts.ts# and df.con_id=ts.con_id group by ts.name, ts.bigfile, ts.con_id order by 1,2")
    else:
        tablespace = query_result("select 0 con_id, ts.name, ts.bigfile, round(sum(bytes)/1024/1024) size_mb, count(*) datafiles# from v$tablespace ts join v$datafile df on df.ts#=ts.ts# group by ts.name, ts.bigfile order by 1,2")
        temp_tablespace = query_result("select 0 con_id, ts.name, ts.bigfile, round(sum(bytes)/1024/1024) size_mb, count(*) tempfiles# from v$tablespace ts join v$tempfile df on df.ts#=ts.ts# group by ts.name, ts.bigfile order by 1,2")
    redolog = query_result("select group#, thread#, sequence#, round(bytes/1024/1024) mb, blocksize, archived, status from v$log order by thread#,group#")
    option = star_query("v$option")
    parameter = {}
    for param in query_result("select name, value, isdefault from v$parameter order by 1"):
      parameter[param['NAME']] = { 'isdefault': param['ISDEFAULT'], 'value': param['VALUE'] }
    # USERENV
    sql = "SELECT sys_context('USERENV','CURRENT_USER') current_user, sys_context('USERENV','DATABASE_ROLE') database_role, sys_context('USERENV','ISDBA') isdba, sys_context('USERENV','ORACLE_HOME') oracle_home"
    if conn.version >= '12.1':
        sql+= ", to_number(sys_context('USERENV','CON_ID')) con_id, sys_context('USERENV','CON_NAME') con_name"
    if conn.version >= '11.1':
        sql+= ", to_number(sys_context('USERENV','CURRENT_EDITION_ID')) CURRENT_EDITION_ID, sys_context('USERENV','CURRENT_EDITION_NAME') CURRENT_EDITION_NAME"
    sql+= " FROM DUAL"
    userenv = query_result(sql)[0]
    #
    facts.update({'database': database, 'instance': instance, 'rac': rac, 'pdb': pdb, 'tablespace': tablespace, 'temp_tablespace': temp_tablespace, 'userenv': userenv, 'redolog': redolog, 'option': option, 'parameter': parameter})
    #
    module.exit_json(msg=msg[0], changed=False, ansible_facts=facts)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
