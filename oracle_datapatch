#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_datapatch
short_description: Manage datapatch functionality
description:
    - Create/delete a database using dbca
    - If a responsefile is available, that will be used. If initparams is defined, those will be attached to the createDatabase command
    - If no responsefile is created, the database will be created based on all other parameters
version_added: "2.4.0.0"
options:
    oracle_home:
        description:
            - The home where the database will be created
        required: False
        aliases: ['oh']
    db_name:
        description:
            - The name of the database
        required: True
        default: None
        aliases: ['db','database_name','name']
    sid:
        description:
            - The instance name
        required: False
        default: None
    db_unique_name:
        description:
            - The database db_unique_name
        required: False
        default: None
        aliases: ['dbunqn','unique_name']
    output:
        description:
            - The type of output you want.
            - Verbose: stdout of the command
            - short: Pre-defined message
        required: False
        default: short
        aliases: ['db','database_name','name']
    fail_on_db_not_exist:
        description:
            - Fail the task if the db does not exist
            - If False, continues the play (changed=False)
        required: False
        default: True
        choices: ['True','False']
    user:
        description:
            - Password for the DB user
        default: sys
        aliases: ['un']
    password:
        description:
            - Password for the DB user
        required: True
        default: None
        aliases: ['pw','password']
    hostname:
        description:
            - The host of the database
        required: false
        default: localhost
        aliases: ['host']
    service_name:
        description:
            - The service_name to connect to (will default to db_name if empty)
        required: false
        aliases: ['sn']
    port:
        description:
            - The listener port to connect to the database
        required: false
        default: 1521
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
'''
import os

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def get_version(module, msg, oracle_home):
    command = '%s/bin/sqlplus -V' % (oracle_home)
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
        module.fail_json(msg=msg, changed=False)
    else:
        return stdout.split(' ')[2][0:4]

# Check if the database exists
def check_db_exists(module, msg, oracle_home, db_name, sid, db_unique_name ):

    if gimanaged:
        if db_unique_name != None:
            checkdb = db_unique_name
        else:
            checkdb = db_name
        command = "%s/bin/srvctl config database -d %s " % (oracle_home, checkdb)
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            if '%s' % (db_name) in stdout: #<-- db doesn't exist
                return False
            else:
                msg = 'Error: command is  %s. stdout is %s' % (command, stdout)
                return False
        elif 'Database name: %s' % (db_name) in stdout: #<-- Database already exist
            return True
    else:
        existingdbs = []
        oratabfile = '/etc/oratab'
        if os.path.exists(oratabfile):
            with open(oratabfile) as oratab:
                for line in oratab:
                    if line.startswith('#') or line.startswith(' '):
                        continue
                    elif re.search('^%s:' % db_name, line) or (sid is not None and re.search('^%s:' % sid, line)):
                        existingdbs.append(line)

        if not existingdbs: #<-- db doesn't exist
            return False
        else:
            for dbs in existingdbs:
                if sid != '':
                    if '%s:' % db_name in dbs or '%s:' % sid in dbs:
                        if dbs.split(':')[1] != oracle_home.rstrip('/'): #<-- DB is created, but with a different ORACLE_HOME
                            msg = 'Database %s already exists in a different ORACLE_HOME (%s)' % (db_name, dbs.split(':')[1])
                            module.fail_json(msg=msg, changed=False)
                        elif dbs.split(':')[1] == oracle_home.rstrip('/'):  #<-- Database already exist
                            return True
                    else:
                        if '%s:' % db_name in dbs:
                            if dbs.split(':')[1]!= oracle_home.rstrip('/'): #<-- DB is created, but with a different ORACLE_HOME
                                msg = 'Database %s already exists in a different ORACLE_HOME (%s)' % (db_name, dbs.split(':')[1])
                                module.fail_json(msg=msg, changed=False)
                        elif dbs.split(':')[1] == oracle_home.rstrip('/'):  #<-- Database already exist
                            return True


def run_datapatch(module, msg, hostname, oracle_home, db_name, sid):

    if major_version > '11.2':
        if sid is not None:
            os.environ['ORACLE_SID'] = sid
        else:
            os.environ['ORACLE_SID'] = db_name

        command = '%s/OPatch/datapatch -verbose' % (oracle_home)
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
            module.fail_json(msg=msg, changed=False)
        else:
            checks = ['Patch installation complete' in stdout]
            if any(checks):
                if output == 'short':
                    return True
                else:
                    msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
                    module.exit_json(msg=msg, changed=True)
            else:
                msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
                module.exit_json(msg=msg, changed=False)

    else:
        # check_outcome_sql = 'select count(*) from registry$history'
        # before = execute_sql_get(module,msg,cursor,check_outcome_sql)

        datapatch_sql = '''
        connect / as sysdba
        @?/rdbms/admin/catbundle.sql psu apply
        exit
        '''
        sqlplus_bin = '%s/bin/sqlplus' % (oracle_home)
        p = subprocess.Popen([sqlplus_bin,'/nolog'],stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (stdout,stderr) = p.communicate(datapatch_sql.encode('utf-8'))
        rc = p.returncode
        if rc != 0:
            msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, datapatch_sql)
            module.fail_json(msg=msg, changed=False)
        else:
            return True
            # after = execute_sql_get(module,msg,cursor,check_outcome_sql)
            # if after[0][0] != before[0][0]:
            #     if output == 'short':
            #         return True
            #     else:
            #         msg = 'STDOUT: %s, sql: %s' % (stdout, datapatch_sql)
            #         module.exit_json(msg=msg, changed=True)
            # else:
            #     msg = 'No changes applied'
            #     module.exit_json(msg=msg, changed=False)




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

# def execute_sql(module, msg, cursor, sql):
#
#     try:
#         cursor.execute(sql)
#     except cx_Oracle.DatabaseError as exc:
#         error, = exc.args
#         msg = 'Something went wrong while executing sql - %s sql: %s' % (error.message, sql)
#         module.fail_json(msg=msg, changed=False)
#         return False
#     return True

def getconn(module,msg, hostname):

    if not hostname:
        hostname = os.uname()[1]
    wallet_connect = '/@%s' % service_name
    try:
        if (not user and not password ): # If neither user or password is supplied, the use of an oracle wallet is assumed
            connect = wallet_connect
            conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
        elif (user and password ):
            dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name, )
            connect = dsn
            conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
        elif (not(user) or not(password)):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            msg = 'Could not connect to database - %s, connect descriptor: %s' % (error.message, connect)
            module.fail_json(msg=msg, changed=False)

    cursor = conn.cursor()
    return cursor



def main():

    msg = ['']
    cursor = None
    global gimanaged
    global major_version
    global user
    global password
    global service_name
    global hostname
    global port
    global output

    module = AnsibleModule(
        argument_spec = dict(
            oracle_home         = dict(default=None, aliases = ['oh']),
            db_name             = dict(required=True, aliases = ['db','database_name','name']),
            sid                 = dict(required=False),
            db_unique_name      = dict(required=False, aliases = ['dbunqn','unique_name']),
            fail_on_db_not_exist = dict(default=True, type='bool'),
            output              = dict(default="short", choices = ["short","verbose"]),
            user                = dict(default='sys', aliases = ['un']),
            password            = dict(required=True, no_log=True, aliases = ['pw','password']),
            hostname            = dict(required=False, default = 'localhost', aliases = ['host']),
            service_name        = dict(required=False, aliases = ['sn']),
            port                = dict(required=False, default = 1521),



        ),
    )

    oracle_home         = module.params["oracle_home"]
    db_name             = module.params["db_name"]
    sid                 = module.params["sid"]
    db_unique_name      = module.params["db_unique_name"]
    fail_on_db_not_exist  = module.params["fail_on_db_not_exist"]
    output              = module.params["output"]
    user                = module.params["user"]
    password            = module.params["password"]
    hostname            = module.params["hostname"]
    service_name        = module.params["service_name"]
    port                = module.params["port"]


    #ld_library_path = '%s/lib' % (oracle_home)
    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
        #os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home     = os.environ['ORACLE_HOME']
        #ld_library_path = os.environ['LD_LIBRARY_PATH']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg, changed=False)


    # Decide whether to use srvctl or sqlplus
    if os.path.exists('/etc/oracle/olr.loc'):
        gimanaged = True
    else:
        gimanaged = False

    if not cx_oracle_exists:
        msg = "The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set"
        module.fail_json(msg=msg)

    # Connection details for database
    if service_name is not None:
        service_name = service_name
    elif db_unique_name is not None:
        service_name = db_unique_name
    else:
        service_name = db_name
    # Get the Oracle version
    major_version = get_version(module,msg,oracle_home)
    if check_db_exists(module,msg,oracle_home,db_name,sid,db_unique_name):
        if run_datapatch(module,msg,hostname,oracle_home,db_name,sid):
            msg = 'Datapatch run successfully for database: %s' % (db_name)
            module.exit_json(msg=msg, changed=True)
        else:
            module.fail_json(msg='datapatch failed in a unhandled way')
    else:
        if fail_on_db_not_exist:
            msg = 'Database %s does not exist' % (db_name)
            module.fail_json(msg=msg)
        else:
            msg = 'Database %s does not exist (so datapatch can not run, obviously), but continuing anyway' % (db_name)
            module.exit_json(msg=msg, changed=False)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
