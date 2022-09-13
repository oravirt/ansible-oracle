#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_jobwindow
short_description: Manage DBMS_SCHEDULER job windows in Oracle database
description:
    - Manage DBMS_SCHEDULER job windows in Oracle database
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
    state:
        description:
            - If absent then window is dropped, if enabled or disabled then window is created at the requested state
        required: true
        choices: ['enabled','disabled','absent']
    name:
        description:
            - Scheduler window name
        required: True
    repeat_interval:
        description:
            - Window repeat interval using DBMS_SCHEDULER calendaring syntax
        required: True
        aliases:
            - interval
    comments:
        description:
            - Comment about the window
        required: False
    resource_plan:
        description:
            - Comment about the window
        required: False
    window_priority:
        description:
            - Window priority
        default: low
        choices:
            - low
            - high
        aliases:
            - priority
    duration_min:
        description:
            - Total window duration in minutes
        required: False
        type: int
    duration_hour:
        description:
            - Total window duration in hours
        required: False
        type: int

notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
requirements: [ "cx_Oracle", "datetime" ]
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
    - name: job window
      oracle_jobwindow:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
        state: enabled
        name: SUNDAY_WINDOW
        interval: freq=daily;byday=SUN;byhour=6;byminute=0; bysecond=0
        comments: Sunday window for maintenance tasks
        duration_hour: 12
        resource_plan: DEFAULT_MAINTENANCE_PLAN
      environment: "{{ oracle_env }}"
'''

from datetime import timedelta

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

def query_existing(name):
    c = conn.cursor()
    c.execute("SELECT resource_plan, duration, window_priority, enabled, repeat_interval, comments FROM all_scheduler_windows WHERE owner = 'SYS' AND window_name = :name",
        {"name": name})
    result = c.fetchone()
    if c.rowcount > 0:
        return {"exists": True, "resource_plan": result[0], "duration": result[1], "window_priority": result[2], "enabled": (result[3] == "TRUE"),
            "repeat_interval": result[4], "comments": result[5]}
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
            state         = dict(default="enabled", choices=["absent","enabled","disabled"]),
            name          = dict(required=True, aliases=["window_name"]),
            resource_plan = dict(required=False),
            repeat_interval = dict(required=True, aliases=['interval']),
            window_priority = dict(default="low", choices=["low","high"], aliases=['priority']),
            duration_min  = dict(required=False, type='int'),
            duration_hour = dict(required=False, type='int'),
            comments      = dict(required=False)
        ),
        supports_check_mode=True,
        mutually_exclusive=[['duration_min','duration_hour']]
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    # Check input parameters
    job_fullname = module.params['name'].upper()
    if module.params['duration_min'] is None and module.params['duration_hour'] is None:
        module.fail_json(msg='Either duration_min or duration_hour must be specified', changed=False)
    new_duration_min = module.params['duration_min'] if module.params['duration_min'] else (module.params['duration_hour']*60)
    new_duration = timedelta(minutes=new_duration_min)
    if new_duration_min < 1:
        module.fail_json(msg='Invalid window duration', changed=False)
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
    #c = conn.cursor()
    result_changed = False
    result = query_existing(job_fullname)
    if (result['exists'] and module.params['state'] != "absent" and (
            (result['comments'] != module.params['comments']) or
            (result['repeat_interval'] != module.params['repeat_interval']) or
            (result['resource_plan'] != module.params['resource_plan'].upper() if module.params['resource_plan'] else None) or
            (result['window_priority'] != module.params['window_priority'].upper()) or
            (result['duration'] != new_duration))):
        c = conn.cursor()
        c.execute("""
        DECLARE
            v_name all_scheduler_windows.window_name%type;
            v_interval VARCHAR2(1000);
            v_comments VARCHAR2(1000);
            v_plan VARCHAR2(200);
            v_duration NUMBER;
            v_priority VARCHAR2(10);
            v_state VARCHAR2(10);
        BEGIN
            v_name:= 'SYS.'||:name;
            v_interval:= :interval;
            v_comments:= :comments;
            v_plan:= :plan;
            v_duration:= :duration;
            v_priority:= :priority;
            v_state:= :state;
            DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'repeat_interval', v_interval);
            DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'window_priority', v_priority);
            DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'duration', numtodsinterval(v_duration, 'MINUTE'));
            IF v_comments IS NOT NULL THEN
                DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'comments', v_comments);
            ELSE
                DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'comments');
            END IF;
            IF v_plan IS NOT NULL THEN
                DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'resource_plan', v_plan);
            ELSE
                DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'resource_plan');
            END IF;
            IF v_state = 'enabled' THEN
                DBMS_SCHEDULER.ENABLE(v_name);
            ELSE
                DBMS_SCHEDULER.DISABLE(v_name);
            END IF;
        END;
        """, {
            "name": job_fullname,
            "interval": module.params['repeat_interval'],
            "comments": module.params['comments'],
            "plan": module.params['resource_plan'],
            "duration": new_duration_min,
            "priority": module.params['window_priority'].upper(),
            "state": module.params['state']
        })
        result_changed = True
    elif result['exists'] and result['enabled'] and module.params['state'] == "disabled":
        c = conn.cursor()
        c.execute("BEGIN DBMS_SCHEDULER.DISABLE('SYS.'||:name); END;", {"name": job_fullname})
        result_changed = True
    elif result['exists'] and not result['enabled'] and module.params['state'] == "enabled":
        c = conn.cursor()
        c.execute("BEGIN DBMS_SCHEDULER.ENABLE('SYS.'||:name); END;", {"name": job_fullname})
        result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop window
        c = conn.cursor()
        c.execute("BEGIN DBMS_SCHEDULER.DROP_WINDOW(window_name=>:name); END;", {"name": job_fullname})
        result_changed = True
    elif not result['exists'] and module.params['state'] in ("enabled","disabled"):
        # Create window
        c = conn.cursor()
        c.execute("""
        DECLARE
            v_name all_scheduler_windows.window_name%type;
        BEGIN
            v_name:= :name;
            DBMS_SCHEDULER.CREATE_WINDOW(window_name=>v_name, repeat_interval=>:interval, comments=>:comments, resource_plan=>:plan,
                duration=>numtodsinterval(:duration, 'MINUTE'), window_priority=>:priority);
            IF :state = 'enabled' THEN
                DBMS_SCHEDULER.ENABLE('SYS.'||v_name);
            ELSE
                DBMS_SCHEDULER.DISABLE('SYS.'||v_name);
            END IF;
        END;""", {
            "name": job_fullname,
            "interval": module.params['repeat_interval'],
            "comments": module.params['comments'],
            "plan": module.params['resource_plan'],
            "duration": new_duration_min,
            "priority": module.params['window_priority'].upper(),
            "state": module.params['state']
        })
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
