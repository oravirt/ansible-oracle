#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_jobschedule
short_description: Manage DBMS_SCHEDULER job schedules in Oracle database
description:
    - Creates, changes and drops C(DBMS_SCHEDULER) schedules in an Oracle database.
    - The existence and attributes of a schedule are read from
      C(ALL_SCHEDULER_SCHEDULES).
    - An existing schedule is changed with C(DBMS_SCHEDULER.SET_ATTRIBUTE) if
      O(repeat_interval) or O(comments) differ. The values are compared as strings.
    - In check mode, the module only connects to the database. It does not check
      the schedule and always returns C(changed=false).
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
            - When connecting with an Oracle wallet, this is the TNS alias of the
              wallet entry.
        type: str
        required: true
    user:
        description:
            - The Oracle user name to connect to the database.
            - The user needs privileges to manage schedules in the schema of the
              schedule, e.g. C(CREATE ANY JOB).
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
            - V(present) - the schedule is created or changed.
            - V(absent) - the schedule is dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
    name:
        description:
            - The name of the schedule, including the owner schema in the form
              V(OWNER.SCHEDULE_NAME).
            - Allowed characters are letters, digits, V(_), V($) and V(#).
        type: str
        required: true
    repeat_interval:
        description:
            - The repeat interval of the schedule in C(DBMS_SCHEDULER) calendaring
              syntax, e.g. V(FREQ=HOURLY;INTERVAL=1).
            - Also required with O(state=absent), although it is not used there.
        type: str
        required: true
        aliases: ['interval']
    comments:
        description:
            - Comments for the schedule.
            - If not set, existing comments are removed.
        type: str
        required: false
    convert_to_upper:
        description:
            - Whether O(name) is converted to uppercase.
            - With V(false), the schedule name is used case sensitive (quoted).
        type: bool
        required: false
        default: true
notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
requirements: [ "cx_Oracle", "re" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Create hourly job schedule
  opitzconsulting.ansible_oracle.oracle_jobschedule:
    hostname: dbhost
    port: 1521
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    state: present
    name: hr.hourly_schedule
    repeat_interval: FREQ=HOURLY; INTERVAL=1
    comments: Just for testing

- name: Drop job schedule (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_jobschedule:
    service_name: orclpdb
    state: absent
    name: hr.hourly_schedule
    repeat_interval: FREQ=HOURLY; INTERVAL=1
'''

RETURN = '''
msg:
    description:
        - Always an empty string, the module sets no message.
    returned: success, when not in check mode
    type: str
    sample: ""
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def query_existing(owner, name):
    c = conn.cursor()
    c.execute(
        "SELECT repeat_interval, comments "
        "FROM all_scheduler_schedules "
        "WHERE owner = :owner AND schedule_name = :name",
        {"owner": owner, "name": name},
    )
    result = c.fetchone()
    if c.rowcount > 0:
        return {"exists": True, "repeat_interval": result[0], "comments": result[1]}
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
            state=dict(default="present", choices=["present", "absent"]),
            name=dict(required=True),
            repeat_interval=dict(required=True, aliases=['interval']),
            comments=dict(required=False),
            convert_to_upper=dict(default=True, type='bool'),
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
    re_name = re.compile("^[A-Za-z0-9_\$#]+\.[A-Za-z0-9_\$#]+$")  # noqa W605
    if not re_name.match(module.params['name']):
        module.fail_json(msg="Invalid schedule name")
    job_fullname = (
        module.params['name'].upper()
        if module.params['convert_to_upper']
        else module.params['name']
    )
    job_parts = job_fullname.split(".")
    job_owner = job_parts[0]
    job_name = job_parts[1]
    job_fullname = "\"%s\".\"%s\"" % (job_owner, job_name)
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
    result = query_existing(job_owner, job_name)
    if result['exists'] and module.params['state'] == "present":
        # Check attributes and modify if needed
        if (result['comments'] != module.params['comments']) or (
            result['repeat_interval'] != module.params['repeat_interval']
        ):
            c = conn.cursor()
            c.execute(
                """
            DECLARE
                v_name VARCHAR2(100);
                v_interval VARCHAR2(1000);
                v_comments VARCHAR2(4000);
            BEGIN
                v_name:= :name;
                v_interval:= :interval;
                v_comments:= :comments;
                DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'repeat_interval', v_interval);
                IF v_comments IS NOT NULL THEN
                    DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'comments', v_comments);
                ELSE
                    DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'comments');
                END IF;
            END;
            """,
                {
                    "name": job_fullname,
                    "interval": module.params['repeat_interval'],
                    "comments": module.params['comments'],
                },
            )
            result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop job class
        c = conn.cursor()
        c.execute(
            "BEGIN DBMS_SCHEDULER.DROP_SCHEDULE(:name); END;", {"name": job_fullname}
        )
        result_changed = True
    elif not result['exists'] and module.params['state'] == "present":
        # Create job class
        c = conn.cursor()
        c.execute(
            """
        BEGIN
            DBMS_SCHEDULER.CREATE_SCHEDULE(
                schedule_name=>:name,
                repeat_interval=>:interval,
                comments=>:comments
                );
        END;""",
            {
                "name": job_fullname,
                "interval": module.params['repeat_interval'],
                "comments": module.params['comments'],
            },
        )
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


if __name__ == '__main__':
    main()
