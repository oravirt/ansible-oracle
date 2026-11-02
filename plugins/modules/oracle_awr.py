#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import timedelta
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_awr
short_description: Manage AWR snapshot settings in an Oracle database
description:
    - Sets the AWR snapshot interval and retention of the connected database with
      C(DBMS_WORKLOAD_REPOSITORY.MODIFY_SNAPSHOT_SETTINGS).
    - The current settings are read from C(DBA_HIST_WR_CONTROL) for the DBID of
      C(V$DATABASE). The settings are only changed (C(changed=true)) when interval
      or retention differ from the requested values.
    - In check mode the module connects to the database and returns C(changed=false)
      without comparing the settings.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
    - Can be run locally on the control machine or on a remote host.
version_added: "2.2.1"
options:
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
    user:
        description:
            - The Oracle user name to connect to the database.
            - The user needs privileges to read C(DBA_HIST_WR_CONTROL) and to execute
              C(DBMS_WORKLOAD_REPOSITORY), for example the DBA role.
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
    snapshot_interval_min:
        description:
            - AWR snapshot interval in minutes.
            - Valid values are V(0) and V(10) to V(1000).
            - V(0) disables automatic snapshots (Oracle then reports an interval of
              40150 days).
        type: int
        required: false
        default: 60
        aliases:
            - interval
    snapshot_retention_days:
        description:
            - AWR snapshot retention time in days. Must be greater than V(0).
            - Passed to the database in minutes (O(snapshot_retention_days) * 1440).
        type: int
        required: false
        default: 8
        aliases:
            - retention
notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
requirements: [ "cx_Oracle" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Set AWR snapshot interval to 30 minutes and retention to 40 days
  opitzconsulting.ansible_oracle.oracle_awr:
    hostname: dbhost
    port: 1521
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    interval: 30
    retention: 40
  environment:
    ORACLE_HOME: /usr/lib/oracle/12.1/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib

- name: Disable automatic AWR snapshots (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_awr:
    service_name: orcl
    mode: sysdba
    snapshot_interval_min: 0
    snapshot_retention_days: 8
'''

RETURN = '''
msg:
    description:
        - Message of the module. Currently always an empty string.
    returned: when not running in check mode
    type: str
    sample: ""
'''


try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def query_existing():
    c = conn.cursor()
    c.execute(
        "select c.snap_interval, c.retention "
        "from dba_hist_wr_control c "
        "join v$database d on c.dbid = d.dbid"
    )
    result = c.fetchone()
    if c.rowcount > 0:
        return {"exists": True, "snap_interval": result[0], "retention": result[1]}
    else:
        return {"exists": False}


# Ansible code
def main():
    global conn
    global msg
    global module
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521, type='int'),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            snapshot_interval_min=dict(default=60, type='int', aliases=['interval']),
            snapshot_retention_days=dict(default=8, type='int', aliases=['retention']),
        ),
        supports_check_mode=True,
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(
            msg=(
                "The cx_Oracle module is required. "
                "'pip install cx_Oracle' should do the trick. "
                "If cx_Oracle is installed, make sure ORACLE_HOME "
                "& LD_LIBRARY_PATH is set"
            )
        )
    # Check input parameters
    if (
        module.params['snapshot_interval_min'] < 10
        and module.params['snapshot_interval_min'] != 0
    ):
        module.fail_json(msg="Snapshot interval must be >= 10 or 0", changed=False)
    if module.params['snapshot_interval_min'] > 1000:
        module.fail_json(
            msg="You probably entered incorrect snapshot interval time", changed=False
        )
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
        msg[0] = 'Could not connect to database - %s, connect descriptor: %s' % (
            error.message,
            connect,
        )
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
        if (
            (
                snap_interval > timedelta(minutes=0)
                and snap_interval != result['snap_interval']
            )
            or (
                snap_interval == timedelta(minutes=0)
                and result['snap_interval'] != timedelta(days=40150)
            )
            or (snap_retention != result['retention'])
        ):
            c = conn.cursor()
            c.execute(
                "CALL DBMS_WORKLOAD_REPOSITORY.MODIFY_SNAPSHOT_SETTINGS"
                "(retention=>:retention, interval=>:interval)",
                {
                    'retention': (module.params['snapshot_retention_days'] * 1440),
                    'interval': module.params['snapshot_interval_min'],
                },
            )
            result_changed = True
    else:
        module.fail_json(msg="Should not be here, something went wrong", changed=False)

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


if __name__ == '__main__':
    main()
