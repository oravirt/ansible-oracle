#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_awr
short_description: Manage AWR configuration
description:
    - Manage AWR configuration
    - Can be run locally on the controlmachine or on a remote host
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
        required: true
        default: normal
        choices: ['normal','sysdba']
    snapshot_interval_min:
        description:
            - AWR snapshot interval in minutes; 0 disables
        default: 60
        type: int
        aliases:
            - interval
    snapshot_retention_days:
        description:
            - AWR snapshot retention time in days
        default: 8
        type: int
        aliases:
            - retention
notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
requirements: [ "cx_Oracle" ]
author: Ilmar Kerm, ilmar.kerm@gmail.com, @ilmarkerm
'''

EXAMPLES = '''
---
- hosts: localhost
  vars:
    oraclehost: 192.168.56.101
    oracleport: 1521
    oracleservice: orcl12c
    oracleuser: system
    oraclepassword: oracle
    oracle_env:
      ORACLE_HOME: /usr/lib/oracle/12.1/client64
      LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib
  tasks:
    - name: set AWR settings
      oracle_awr:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
        interval: 30
        retention: 40
      environment: "{{ oracle_env }}"
'''

from datetime import timedelta

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

def query_existing():
    c = conn.cursor()
    c.execute("select c.snap_interval, c.retention from dba_hist_wr_control c join v$database d on c.dbid = d.dbid")
    result = c.fetchone()
    if c.rowcount > 0:
        return {"exists": True, "snap_interval": result[0], "retention": result[1]}
    else:
        return {"exists": False}

# Ansible code
def main():
    global lconn, conn, msg, module
    msg = ['']
    module = AnsibleModule(
        argument_spec = dict(
            hostname      = dict(default='localhost'),
            port          = dict(default=1521, type='int'),
            service_name  = dict(required=True),
            user          = dict(required=False),
            password      = dict(required=False),
            mode          = dict(default='normal', choices=["normal","sysdba"]),
            snapshot_interval_min = dict(default=60, type='int', aliases=['interval']),
            snapshot_retention_days = dict(default=8, type='int', aliases=['retention'])
        ),
        supports_check_mode=True
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    # Check input parameters
    if module.params['snapshot_interval_min'] < 10 and module.params['snapshot_interval_min'] != 0:
        module.fail_json(msg="Snapshot interval must be >= 10 or 0", changed=False)
    if module.params['snapshot_interval_min'] > 1000:
        module.fail_json(msg="You probably entered incorrect snapshot interval time", changed=False)
    if module.params['snapshot_retention_days'] <= 0:
        module.fail_json(msg="Snapshot retention must be > 0", changed=False)
    snap_interval = timedelta(minutes=module.params['snapshot_interval_min'])
    snap_retention = timedelta(days=module.params['snapshot_retention_days'])
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
    result_changed = False
    result = query_existing()
    if result['exists']:
        if (snap_interval > timedelta(minutes=0) and snap_interval != result['snap_interval']) or (snap_interval == timedelta(minutes=0) and result['snap_interval'] != timedelta(days=40150)) or (snap_retention != result['retention']):
            c = conn.cursor()
            c.execute("CALL DBMS_WORKLOAD_REPOSITORY.MODIFY_SNAPSHOT_SETTINGS(retention=>:retention, interval=>:interval)",
                {'retention': (module.params['snapshot_retention_days']*1440), 'interval': module.params['snapshot_interval_min']})
            result_changed = True
    else:
        module.fail_json(msg="Should not be here, something went wrong", changed=False)

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
