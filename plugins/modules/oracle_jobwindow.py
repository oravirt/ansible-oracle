#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import timedelta
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_jobwindow
short_description: Manage DBMS_SCHEDULER job windows in an Oracle database
description:
    - Creates, changes, enables, disables and drops DBMS_SCHEDULER windows in an
      Oracle database.
    - Windows are always owned by C(SYS). The existence is checked in
      C(ALL_SCHEDULER_WINDOWS), so the connecting user must be able to see the
      windows of C(SYS) (e.g. DBA privilege).
    - The window name is converted to uppercase.
    - For an existing window, O(comments), O(repeat_interval), O(resource_plan),
      O(window_priority) and the duration are compared with the database. If one of
      them differs, all attributes are set again with C(DBMS_SCHEDULER.SET_ATTRIBUTE)
      and the window is enabled or disabled according to O(state). Otherwise only
      the enabled/disabled state is changed if needed.
    - O(repeat_interval) is compared as an exact string with the stored value.
    - Either O(duration_min) or O(duration_hour) must be given, also for
      O(state=absent).
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
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
            - When connecting with an Oracle wallet, this is the TNS alias of the wallet
              entry.
        type: str
        required: true
    user:
        description:
            - The Oracle user name to connect to the database, must have DBA privilege.
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
    state:
        description:
            - V(enabled) - the window is created or changed and enabled.
            - V(disabled) - the window is created or changed and disabled.
            - V(absent) - the window is dropped.
        type: str
        required: false
        default: enabled
        choices: ['enabled', 'disabled', 'absent']
    name:
        description:
            - The name of the scheduler window (without the C(SYS.) prefix).
        type: str
        required: true
        aliases: ['window_name']
    repeat_interval:
        description:
            - The window repeat interval using DBMS_SCHEDULER calendaring syntax.
            - Required also for O(state=absent).
        type: str
        required: true
        aliases: ['interval']
    comments:
        description:
            - A comment about the window.
            - If omitted, an existing comment is removed.
        type: str
        required: false
    resource_plan:
        description:
            - The resource manager plan that is activated when the window opens.
            - If omitted, a change of the resource plan in the database is not
              detected, but the resource plan is removed when other attributes are
              changed.
        type: str
        required: false
    window_priority:
        description:
            - The priority of the window.
        type: str
        required: false
        default: low
        choices: ['low', 'high']
        aliases: ['priority']
    duration_min:
        description:
            - The total window duration in minutes.
            - Mutually exclusive with O(duration_hour). One of both is required.
        type: int
        required: false
    duration_hour:
        description:
            - The total window duration in hours.
            - Mutually exclusive with O(duration_min). One of both is required.
        type: int
        required: false
notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
    - In check mode, the module exits with C(changed=false) without checking
      the database.
requirements: [ "cx_Oracle", "datetime" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Create and enable the window SUNDAY_WINDOW
  opitzconsulting.ansible_oracle.oracle_jobwindow:
    hostname: dbhost
    port: 1521
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    state: enabled
    name: SUNDAY_WINDOW
    interval: freq=daily;byday=SUN;byhour=6;byminute=0;bysecond=0
    comments: Sunday window for maintenance tasks
    duration_hour: 12
    resource_plan: DEFAULT_MAINTENANCE_PLAN
  environment:
    ORACLE_HOME: /usr/lib/oracle/12.1/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib

- name: Drop the window SUNDAY_WINDOW (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_jobwindow:
    service_name: orcl
    state: absent
    name: SUNDAY_WINDOW
    interval: freq=daily;byday=SUN;byhour=6;byminute=0;bysecond=0
    duration_hour: 12
'''

RETURN = '''
msg:
    description:
        - Message of the module. Currently always an empty string.
        - Not returned in check mode.
    returned: success
    type: str
    sample: ""
'''


try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def query_existing(name):
    c = conn.cursor()
    c.execute(
        "SELECT resource_plan, duration, window_priority, enabled, "
        "repeat_interval, comments "
        "FROM all_scheduler_windows "
        "WHERE owner = 'SYS' AND window_name = :name",
        {"name": name},
    )
    result = c.fetchone()
    if c.rowcount > 0:
        return {
            "exists": True,
            "resource_plan": result[0],
            "duration": result[1],
            "window_priority": result[2],
            "enabled": (result[3] == "TRUE"),
            "repeat_interval": result[4],
            "comments": result[5],
        }
    else:
        return {"exists": False}


# Ansible code
def main():
    global conn, msg, module
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521, type='int'),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            state=dict(default="enabled", choices=["absent", "enabled", "disabled"]),
            name=dict(required=True, aliases=["window_name"]),
            resource_plan=dict(required=False),
            repeat_interval=dict(required=True, aliases=['interval']),
            window_priority=dict(
                default="low", choices=["low", "high"], aliases=['priority']
            ),
            duration_min=dict(required=False, type='int'),
            duration_hour=dict(required=False, type='int'),
            comments=dict(required=False),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['duration_min', 'duration_hour']],
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
    job_fullname = module.params['name'].upper()
    if module.params['duration_min'] is None and module.params['duration_hour'] is None:
        module.fail_json(
            msg='Either duration_min or duration_hour must be specified', changed=False
        )
    new_duration_min = (
        module.params['duration_min']
        if module.params['duration_min']
        else (module.params['duration_hour'] * 60)
    )
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
    # c = conn.cursor()
    result_changed = False
    result = query_existing(job_fullname)
    if (
        result['exists']
        and module.params['state'] != "absent"
        and (
            (result['comments'] != module.params['comments'])
            or (result['repeat_interval'] != module.params['repeat_interval'])
            or (
                result['resource_plan'] != module.params['resource_plan'].upper()
                if module.params['resource_plan']
                else None
            )
            or (result['window_priority'] != module.params['window_priority'].upper())
            or (result['duration'] != new_duration)
        )
    ):
        c = conn.cursor()
        c.execute(
            """
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
            DBMS_SCHEDULER.SET_ATTRIBUTE(
                v_name, 'duration', numtodsinterval(v_duration, 'MINUTE')
                );
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
        """,
            {
                "name": job_fullname,
                "interval": module.params['repeat_interval'],
                "comments": module.params['comments'],
                "plan": module.params['resource_plan'],
                "duration": new_duration_min,
                "priority": module.params['window_priority'].upper(),
                "state": module.params['state'],
            },
        )
        result_changed = True
    elif (
        result['exists'] and result['enabled'] and module.params['state'] == "disabled"
    ):
        c = conn.cursor()
        c.execute(
            "BEGIN DBMS_SCHEDULER.DISABLE('SYS.'||:name); END;", {"name": job_fullname}
        )
        result_changed = True
    elif (
        result['exists']
        and not result['enabled']
        and module.params['state'] == "enabled"
    ):
        c = conn.cursor()
        c.execute(
            "BEGIN DBMS_SCHEDULER.ENABLE('SYS.'||:name); END;", {"name": job_fullname}
        )
        result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop window
        c = conn.cursor()
        c.execute(
            "BEGIN DBMS_SCHEDULER.DROP_WINDOW(window_name=>:name); END;",
            {"name": job_fullname},
        )
        result_changed = True
    elif not result['exists'] and module.params['state'] in ("enabled", "disabled"):
        # Create window
        c = conn.cursor()
        c.execute(
            """
        DECLARE
            v_name all_scheduler_windows.window_name%type;
        BEGIN
            v_name:= :name;
            DBMS_SCHEDULER.CREATE_WINDOW(
                window_name=>v_name,
                repeat_interval=>:interval,
                comments=>:comments,
                resource_plan=>:plan,
                duration=>numtodsinterval(:duration, 'MINUTE'),
                window_priority=>:priority
                );
            IF :state = 'enabled' THEN
                DBMS_SCHEDULER.ENABLE('SYS.'||v_name);
            ELSE
                DBMS_SCHEDULER.DISABLE('SYS.'||v_name);
            END IF;
        END;""",
            {
                "name": job_fullname,
                "interval": module.params['repeat_interval'],
                "comments": module.params['comments'],
                "plan": module.params['resource_plan'],
                "duration": new_duration_min,
                "priority": module.params['window_priority'].upper(),
                "state": module.params['state'],
            },
        )
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


if __name__ == '__main__':
    main()
