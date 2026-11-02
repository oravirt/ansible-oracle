#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_datapatch
short_description: Run datapatch for an Oracle database
description:
    - Runs C(datapatch) (or C(catbundle.sql) for Oracle 11.2 and older) to apply the
      SQL part of patches to an existing database.
    - The Oracle version is determined with C(sqlplus -V) from O(oracle_home).
    - For versions newer than 11.2, C($ORACLE_HOME/OPatch/datapatch -verbose) is run
      with E(ORACLE_SID) set to O(sid) (or O(db_name) if O(sid) is not set).
    - For version 11.2 and older, C(@?/rdbms/admin/catbundle.sql psu apply) is run
      in C(sqlplus / as sysdba). E(ORACLE_SID) and O(script_env) are not set by the
      module in this case.
    - The existence of the database is checked before. If C(/etc/oracle/olr.loc)
      exists (Grid Infrastructure), C(srvctl config database) is used with
      O(db_unique_name) (or O(db_name)). In a cluster (C(local_only=false) in
      C(/etc/oracle/ocr.loc)), the database must also be running on the local host
      (C(srvctl status database)). Without Grid Infrastructure, C(/etc/oratab) is
      searched for O(db_name) or O(sid) with the ORACLE_HOME O(oracle_home).
    - The module does not connect to the database with a user and password; the
      connection options O(user), O(password), O(hostname), O(port) and
      O(service_name) are currently not used.
    - The module has no idempotency check of its own, see RV(msg) for when
      C(changed=true) is returned.
version_added: "2.4.0.0"
options:
    oracle_home:
        description:
            - The ORACLE_HOME of the database.
            - If not set, the environment variable E(ORACLE_HOME) is used. The module
              fails if neither is set.
        type: str
        required: false
        aliases: ['oh']
    db_name:
        description:
            - The name of the database.
            - Used as E(ORACLE_SID) if O(sid) is not set.
        type: str
        required: true
        aliases: ['db', 'database_name', 'name']
    sid:
        description:
            - The instance name (E(ORACLE_SID)).
        type: str
        required: false
    db_unique_name:
        description:
            - The C(db_unique_name) of the database.
            - Used for the existence check with C(srvctl) instead of O(db_name).
        type: str
        required: false
        aliases: ['dbunqn', 'unique_name']
    fail_on_db_not_exist:
        description:
            - Fail the task if the database does not exist.
            - If V(false), the task returns C(changed=false) instead.
        type: bool
        required: false
        default: true
    output:
        description:
            - The type of output for versions newer than 11.2.
            - V(short) - a pre-defined message is returned.
            - V(verbose) - the stdout of C(datapatch) is returned.
        type: str
        required: false
        default: short
        choices: ['short', 'verbose']
    user:
        description:
            - The database user.
            - Currently not used by the module.
        type: str
        required: false
        default: sys
        aliases: ['un']
    password:
        description:
            - The password for O(user).
            - Currently not used by the module, but required by the argument spec.
        type: str
        required: true
        aliases: ['pw']
    hostname:
        description:
            - The host of the database.
            - Currently not used by the module.
        type: str
        required: false
        default: localhost
        aliases: ['host']
    service_name:
        description:
            - The service name of the database. Defaults to O(db_unique_name) or
              O(db_name) if not set.
            - Currently not used by the module.
        type: str
        required: false
        aliases: ['sn']
    port:
        description:
            - The listener port number on the host.
            - Currently not used by the module.
        type: int
        required: false
        default: 1521
    script_env:
        description:
            - Dictionary of environment variables passed to C(sqlplus -V) and
              C(datapatch).
        type: dict
        required: false
        default: {}
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Run datapatch for database orcl
  opitzconsulting.ansible_oracle.oracle_datapatch:
    oracle_home: /u01/app/oracle/product/19.0.0/dbhome_1
    db_name: orcl
    db_unique_name: orcl_site1
    sid: orcl1
    password: "{{ sys_password }}"
    output: verbose

- name: Run datapatch, do not fail if the database does not exist
  opitzconsulting.ansible_oracle.oracle_datapatch:
    oracle_home: /u01/app/oracle/product/19.0.0/dbhome_1
    db_name: orcl
    password: "{{ sys_password }}"
    fail_on_db_not_exist: false
    script_env:
      ORACLE_BASE: /u01/app/oracle
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
        - For versions newer than 11.2, C(changed=true) is returned if the stdout
          of C(datapatch) contains C(Patch installation complete). With
          O(output=verbose), or if that text is not found (C(changed=false)), the
          stdout and the command are returned.
        - For version 11.2 and older, C(changed=true) is always returned after a
          successful run of C(catbundle.sql).
    returned: always
    type: str
    sample: "Datapatch run successfully for database: orcl"
'''

# try:
#     import cx_Oracle
# except ImportError:
#     cx_oracle_exists = False
# else:
#     cx_oracle_exists = True


def get_version(module, msg, oracle_home, script_env):
    command = '%s/bin/sqlplus -V' % (oracle_home)
    (rc, stdout, stderr) = module.run_command(command, environ_update=script_env)
    if rc != 0:
        msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
        module.fail_json(msg=msg, changed=False)
    else:
        return stdout.split(' ')[2][0:4]


# Check if the database exists
def check_db_exists(module, msg, oracle_home, db_name, sid, db_unique_name):
    if gimanaged:
        if db_unique_name is not None:
            checkdb = db_unique_name
        else:
            checkdb = db_name
        if is_cluster:
            # for cluster, assume SEHA and check if database is up at the local host
            # (otherwise we can't datapatch it)
            command = (
                "%(oracle_home)s/bin/srvctl config database -d %(checkdb)s && \
                %(oracle_home)s/bin/srvctl status database -d %(checkdb)s | \
                grep -q %(shortname)s"
                % {
                    'oracle_home': oracle_home,
                    'checkdb': checkdb,
                    'shortname': os.uname()[1].split('.')[0],
                }
            )
        else:
            command = "%s/bin/srvctl config database -d %s" % (oracle_home, checkdb)

        # cluster check command needs a shell, because we run multiple commands and pipe
        (rc, stdout, stderr) = module.run_command(command, use_unsafe_shell=is_cluster)

        if rc != 0:
            if '%s' % (db_name) in stdout:  # <-- db doesn't exist
                return False
            else:
                msg = 'Error: command is  %s. stdout is %s' % (command, stdout)
                return False
        else:
            return True
    else:
        existingdbs = []
        oratabfile = '/etc/oratab'
        if os.path.exists(oratabfile):
            with open(oratabfile) as oratab:
                for line in oratab:
                    if line.startswith('#') or line.startswith(' '):
                        continue
                    elif re.search('^%s:' % db_name, line) or (
                        sid is not None and re.search('^%s:' % sid, line)
                    ):
                        existingdbs.append(line)

        if not existingdbs:  # <-- db doesn't exist
            return False
        else:
            for dbs in existingdbs:
                if sid != '':
                    if '%s:' % db_name in dbs or '%s:' % sid in dbs:
                        if dbs.split(':')[1] != oracle_home.rstrip(
                            '/'
                        ):  # <-- DB is created, but with a different ORACLE_HOME
                            msg = (
                                'Database %s already exists in a different '
                                'ORACLE_HOME (%s)' % (db_name, dbs.split(':')[1])
                            )
                            module.fail_json(msg=msg, changed=False)
                        elif dbs.split(':')[1] == oracle_home.rstrip(
                            '/'
                        ):  # <-- Database already exist
                            return True
                    else:
                        if '%s:' % db_name in dbs:
                            if dbs.split(':')[1] != oracle_home.rstrip(
                                '/'
                            ):  # <-- DB is created, but with a different ORACLE_HOME
                                msg = (
                                    'Database %s already exists in a different'
                                    ' ORACLE_HOME (%s)' % (db_name, dbs.split(':')[1])
                                )
                                module.fail_json(msg=msg, changed=False)
                        elif dbs.split(':')[1] == oracle_home.rstrip(
                            '/'
                        ):  # <-- Database already exist
                            return True


def run_datapatch(module, msg, hostname, oracle_home, db_name, sid, script_env):
    if major_version > '11.2':
        if sid is not None:
            os.environ['ORACLE_SID'] = sid
        else:
            os.environ['ORACLE_SID'] = db_name

        command = '%s/OPatch/datapatch -verbose' % (oracle_home)
        (rc, stdout, stderr) = module.run_command(command, environ_update=script_env)
        if rc != 0:
            msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                command,
            )
            module.fail_json(msg=msg, changed=False)
        else:
            checks = ['Patch installation complete' in stdout]
            if any(checks):
                if output == 'short':
                    return True
                else:
                    msg = 'STDOUT: %s, COMMAND: %s' % (stdout, command)
                    module.exit_json(msg=msg, changed=True)
            else:
                msg = 'STDOUT: %s, COMMAND: %s' % (stdout, command)
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
        p = subprocess.Popen(
            [sqlplus_bin, '/nolog'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (stdout, stderr) = p.communicate(datapatch_sql.encode('utf-8'))
        rc = p.returncode
        if rc != 0:
            msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                datapatch_sql,
            )
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


# def execute_sql_get(module, msg, cursor, sql):
#     try:
#         cursor.execute(sql)
#         result = cursor.fetchall()
#     except cx_Oracle.DatabaseError as exc:
#         (error,) = exc.args
#         msg = 'Something went wrong while executing sql_get - %s sql: %s' % (
#             error.message,
#             sql,
#         )
#         module.fail_json(msg=msg, changed=False)
#         return False
#     return result


# def execute_sql(module, msg, cursor, sql):
#
#     try:
#         cursor.execute(sql)
#     except cx_Oracle.DatabaseError as exc:
#         error, = exc.args
#         msg = 'Something went wrong while executing sql - %s sql: %s'
# % (error.message, sql)
#         module.fail_json(msg=msg, changed=False)
#         return False
#     return True


# def getconn(module, msg, hostname):
#     if not hostname:
#         hostname = os.uname()[1]
#     wallet_connect = '/@%s' % service_name
#     try:
#         if not user and not password:
#             # If neither user or password is supplied, the use of
#             # an oracle wallet is assumed
#             connect = wallet_connect
#             conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
#         elif user and password:
#             dsn = cx_Oracle.makedsn(
#                 host=hostname,
#                 port=port,
#                 service_name=service_name,
#             )
#             connect = dsn
#             conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
#         elif not (user) or not (password):
#             module.fail_json(msg='Missing username or password for cx_Oracle')

#     except cx_Oracle.DatabaseError as exc:
#         (error,) = exc.args
#         msg = 'Could not connect to database - %s, connect descriptor: %s' % (
#             error.message,
#             connect,
#         )
#         module.fail_json(msg=msg, changed=False)

#     cursor = conn.cursor()
#     return cursor


def main():
    msg = ['']
    global gimanaged
    global major_version
    global user
    global password
    global service_name
    global hostname
    global port
    global output
    global cursor
    global is_cluster

    cursor = None

    module = AnsibleModule(
        argument_spec=dict(
            oracle_home=dict(default=None, aliases=['oh']),
            db_name=dict(required=True, aliases=['db', 'database_name', 'name']),
            sid=dict(required=False),
            db_unique_name=dict(required=False, aliases=['dbunqn', 'unique_name']),
            fail_on_db_not_exist=dict(default=True, type='bool'),
            output=dict(default="short", choices=["short", "verbose"]),
            user=dict(default='sys', aliases=['un']),
            password=dict(required=True, no_log=True, aliases=['pw']),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            service_name=dict(required=False, aliases=['sn']),
            port=dict(required=False, default=1521),
            script_env=dict(required=False, type='dict', default={}),
        ),
    )

    oracle_home = module.params["oracle_home"]
    db_name = module.params["db_name"]
    sid = module.params["sid"]
    db_unique_name = module.params["db_unique_name"]
    fail_on_db_not_exist = module.params["fail_on_db_not_exist"]
    output = module.params["output"]
    user = module.params["user"]
    password = module.params["password"]
    hostname = module.params["hostname"]
    service_name = module.params["service_name"]
    port = module.params["port"]
    script_env = module.params["script_env"]

    # ld_library_path = '%s/lib' % (oracle_home)
    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
        # os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']
        # ld_library_path = os.environ['LD_LIBRARY_PATH']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg, changed=False)

    # Decide whether to use srvctl or sqlplus
    if os.path.exists('/etc/oracle/olr.loc'):
        gimanaged = True
    else:
        gimanaged = False

    # If gimanaged, check whether it's Oracle Restart or Oracle Clusterware
    is_cluster = False
    ocr_loc = '/etc/oracle/ocr.loc'
    if gimanaged and os.path.exists(ocr_loc):
        ocr_grep = subprocess.run(
            ['grep', '-Piq', '^\\s*local_only\\s*=\\s*false', ocr_loc]
        )
        is_cluster = not bool(ocr_grep.returncode)

    # if not cx_oracle_exists:
    #     msg = (
    #         "The cx_Oracle module is required. "
    #         "'pip install cx_Oracle' should do the trick. "
    #         "If cx_Oracle is installed, make sure "
    #         "ORACLE_HOME & LD_LIBRARY_PATH is set"
    #     )
    #     module.fail_json(msg=msg)

    # Connection details for database
    if service_name is not None:
        service_name = service_name
    elif db_unique_name is not None:
        service_name = db_unique_name
    else:
        service_name = db_name
    # Get the Oracle version
    major_version = get_version(module, msg, oracle_home, script_env)
    if check_db_exists(module, msg, oracle_home, db_name, sid, db_unique_name):
        if run_datapatch(module, msg, hostname, oracle_home, db_name, sid, script_env):
            msg = 'Datapatch run successfully for database: %s' % (db_name)
            module.exit_json(msg=msg, changed=True)
        else:
            module.fail_json(msg='datapatch failed in a unhandled way')
    else:
        if fail_on_db_not_exist:
            msg = 'Database %s does not exist' % (db_name)
            module.fail_json(msg=msg)
        else:
            msg = (
                'Database %s does not exist (so datapatch can not run, obviously), '
                'but continuing anyway' % (db_name)
            )
            module.exit_json(msg=msg, changed=False)


if __name__ == '__main__':
    main()
