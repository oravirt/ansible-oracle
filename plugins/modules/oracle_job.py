#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_job
short_description: Manage DBMS_SCHEDULER jobs in Oracle database
description:
    - Creates, changes and drops C(DBMS_SCHEDULER) jobs in an Oracle database.
    - The existence and attributes of a job are read from C(ALL_SCHEDULER_JOBS) and
      C(ALL_SCHEDULER_JOB_ARGS).
    - A new job is created with C(DBMS_SCHEDULER.CREATE_JOB). Afterwards
      O(restartable), O(logging_level) and O(job_arguments) are set, and the job is
      enabled if O(enabled=true).
    - An existing job is compared with all options. If any attribute differs, the
      job is dropped and created again.
    - In check mode, the module only connects to the database. It does not check
      the job and always returns C(changed=false).
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
            - The user needs privileges to create and drop jobs in the schema of the
              job, e.g. C(CREATE ANY JOB).
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
            - V(present) - the job is created, or dropped and created again if any
              attribute differs.
            - V(absent) - the job is dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
    enabled:
        description:
            - Whether the job is enabled.
        type: bool
        required: false
        default: true
    job_name:
        description:
            - The name of the job, including the owner schema in the form
              V(OWNER.JOB_NAME).
            - Allowed characters are letters, digits, V(_), V($) and V(#).
        type: str
        required: true
        aliases: ['name']
    job_class:
        description:
            - The job class of the job.
            - Must be given in uppercase, as it is compared case sensitive with
              C(ALL_SCHEDULER_JOBS).
        type: str
        required: false
        default: DEFAULT_JOB_CLASS
        aliases: ['class']
    job_type:
        description:
            - The type of the job action.
            - Not used when the job is created with O(program_name).
        type: str
        required: false
        default: plsql_block
        choices: ['plsql_block', 'stored_procedure', 'executable', 'external_script',
                  'sql_script', 'backup_script']
        aliases: ['type']
    job_action:
        description:
            - The action executed by the job, e.g. a PL/SQL block or the name of a
              stored procedure, depending on O(job_type).
            - O(job_action) or O(program_name) is required with O(state=present).
        type: str
        required: false
        aliases: ['action']
    job_arguments:
        description:
            - List of argument values passed to the job. Only positional arguments
              are supported.
            - The number of arguments of the job is set to the number of list
              elements.
        type: list
        elements: str
        required: false
        aliases: ['arguments']
    lightweight:
        description:
            - Whether the job is created as lightweight job (C(job_style=LIGHTWEIGHT)).
            - Lightweight jobs require O(program_name) and cannot be restartable.
        type: bool
        required: false
        default: false
    credential:
        description:
            - The name of the credential used by the job.
            - If no owner schema is given, the owner of the job is assumed.
        type: str
        required: false
    destination:
        description:
            - The name of the destination of the job.
            - If no owner schema is given, the owner of the job is assumed.
        type: str
        required: false
    restartable:
        description:
            - Whether the job is restartable.
        type: bool
        required: false
        default: false
    repeat_interval:
        description:
            - The repeat interval of the job in C(DBMS_SCHEDULER) calendaring syntax,
              e.g. V(FREQ=HOURLY;INTERVAL=3).
            - Mutually exclusive with O(schedule_name).
        type: str
        required: false
    logging_level:
        description:
            - The logging level of the job.
            - If not set, the default logging level of the job class is used.
        type: str
        required: false
        choices: ['off', 'runs', 'failed runs', 'full']
    program_name:
        description:
            - The C(DBMS_SCHEDULER) program executed by the job, in the form
              V(OWNER.PROGRAM_NAME).
            - Mutually exclusive with O(job_action).
        type: str
        required: false
    schedule_name:
        description:
            - The C(DBMS_SCHEDULER) schedule used by the job, in the form
              V(OWNER.SCHEDULE_NAME).
            - Mutually exclusive with O(repeat_interval).
        type: str
        required: false
    comments:
        description:
            - Comments for the job.
        type: str
        required: false
    auto_drop:
        description:
            - Whether the job is automatically dropped after its last execution.
        type: bool
        required: false
        default: false
    convert_to_upper:
        description:
            - Whether O(job_name) is converted to uppercase.
            - With V(false), the job name is used case sensitive (quoted).
        type: bool
        required: false
        default: true
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Oracle RDBMS 10gR2 or later required
requirements: [ "python-oracledb", "re" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Drop job
  opitzconsulting.ansible_oracle.oracle_job:
    hostname: dbhost
    port: 1521
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    state: absent
    job_name: hr.j1

- name: Create job
  opitzconsulting.ansible_oracle.oracle_job:
    hostname: dbhost
    port: 1521
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    state: present
    job_name: hr.j1
    job_action: begin null; null; end;
    logging_level: runs
    comments: This job is just for testing something
    repeat_interval: FREQ=HOURLY;INTERVAL=3
    enabled: false
    lightweight: false
    restartable: true

- name: Create job calling a stored procedure with a schedule (Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_job:
    service_name: orclpdb
    job_name: hr.purge_log
    job_type: stored_procedure
    job_action: hr.log_pkg.purge
    job_arguments:
      - "30"
    schedule_name: hr.daily_schedule
    logging_level: failed runs
'''

RETURN = '''
msg:
    description:
        - Always an empty string, the module sets no message.
    returned: success, when not in check mode
    type: str
    sample: ""
'''


def query_existing(job_owner, job_name):
    c = conn.cursor()
    c.execute(
        """SELECT job_style, program_owner, program_name, job_type, job_action,
            number_of_arguments, schedule_owner, schedule_name, schedule_type,
            repeat_interval, job_class, enabled, restartable, state, logging_level,
            instance_stickiness, destination_owner, destination, credential_owner,
            credential_name, comments, auto_drop
           FROM all_scheduler_jobs j
           WHERE owner = :owner
           AND job_name = :name""",
        {"owner": job_owner.upper(), "name": job_name.upper()},
    )
    result = c.fetchone()
    if c.rowcount > 0:
        args = []
        if result[5] > 0:
            c.execute(
                "SELECT value "
                "FROM all_scheduler_job_args "
                "WHERE owner = :owner AND job_name = :name "
                "ORDER BY argument_position",
                {"owner": job_owner.upper(), "name": job_name.upper()},
            )
            res = c.fetchall()
            for row in res:
                args.append(row[0])
        return {
            "exists": True,
            "lightweight": True if result[0] == 'LIGHTWEIGHT' else False,
            "program_name": "%s.%s" % (result[1], result[2]) if result[1] else None,
            "job_type": result[3],
            "job_action": result[4],
            "number_of_arguments": result[5],
            "schedule_name": "%s.%s" % (result[6], result[7]) if result[6] else None,
            "schedule_type": result[8],
            "repeat_interval": result[9],
            "job_class": result[10],
            "enabled": True if result[11] == 'TRUE' else False,
            "restartable": True if result[12] == 'TRUE' else False,
            "state": result[13],
            "logging_level": result[14],
            "instance_stickiness": True if result[15] == 'TRUE' else False,
            "destination": "%s.%s" % (result[16], result[17]) if result[16] else None,
            "credential": "%s.%s" % (result[18], result[19]) if result[18] else None,
            "comments": result[20],
            "auto_drop": True if result[21] == 'TRUE' else False,
            "job_arguments": args,
        }
    else:
        return {"exists": False}


def create_job():
    c = conn.cursor()
    var_args = c.arrayvar(
        oracledb.STRING,
        []
        if module.params['job_arguments'] is None
        else module.params['job_arguments'],
    )
    # Bild the right CREATE_JOB command
    job_sql = "job_name=>v_name,comments=>v_comments,auto_drop=>v_auto_drop"
    if module.params['job_class']:
        job_sql += ",job_class=>v_job_class"
    if module.params['program_name']:
        job_sql += ",program_name=>v_program_name"
        if module.params['lightweight']:
            job_sql += ",job_style=>v_job_style"
    else:
        job_sql += (
            ",job_type=>v_job_type,"
            "job_action=>v_job_action,"
            "number_of_arguments=>v_num_args"
        )
    if module.params['schedule_name']:
        job_sql += ",schedule_name=>v_schedule_name"
    else:
        job_sql += ",repeat_interval=>v_repeat_interval"
    if module.params['credential']:
        job_sql += ",credential_name=>v_cred"
    if module.params['destination']:
        job_sql += ",destination_name=>v_dest"
    c.execute(
        """
        DECLARE
            TYPE str_array IS TABLE OF VARCHAR2(200) INDEX BY BINARY_INTEGER;
            v_args str_array;
            v_name VARCHAR2(100);
            v_num_args NUMBER;
            v_comments VARCHAR2(4000);
            v_job_class VARCHAR2(100);
            v_auto_drop BOOLEAN;
            v_restartable BOOLEAN;
            v_enabled BOOLEAN;
            v_program_name VARCHAR2(100);
            v_job_style VARCHAR2(10);
            v_job_type VARCHAR2(20);
            v_job_action VARCHAR2(4000);
            v_schedule_name VARCHAR2(100);
            v_repeat_interval VARCHAR2(100);
            v_cred VARCHAR2(100);
            v_dest VARCHAR2(100);
            v_logging_level PLS_INTEGER;
        BEGIN
            -- Assign input
            v_name:= :var_name;
            v_job_type:= :var_job_type;
            v_job_action:= :var_job_action;
            v_job_style:= :var_job_style;
            v_job_class:= :var_job_class;
            v_cred:= :var_credential;
            v_dest:= :var_destination;
            v_restartable:= :var_restartable = 1;
            v_repeat_interval:= :var_repeat_interval;
            v_logging_level:= CASE :var_logging_level
                WHEN 'off' THEN DBMS_SCHEDULER.LOGGING_OFF
                WHEN 'runs' THEN DBMS_SCHEDULER.LOGGING_RUNS
                WHEN 'failed runs' THEN DBMS_SCHEDULER.LOGGING_FAILED_RUNS
                WHEN 'full' THEN DBMS_SCHEDULER.LOGGING_FULL
            END;
            v_program_name:= :var_program_name;
            v_schedule_name:= :var_schedule_name;
            v_comments:= :var_comments;
            v_enabled:= :var_enabled = 1;
            v_auto_drop:= :var_auto_drop = 1;
            v_args:= :var_args;
            v_num_args:= v_args.COUNT;
            -- Execute CREATE_JOB
            DBMS_SCHEDULER.CREATE_JOB(%s);
            -- Set parameters
            DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'restartable', v_restartable);
            IF v_logging_level IS NOT NULL THEN
                DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'logging_level', v_logging_level);
            END IF;
            IF v_num_args > 0 THEN
                FOR i IN v_args.FIRST..v_args.LAST LOOP
                    DBMS_SCHEDULER.SET_JOB_ARGUMENT_VALUE(
                        job_name=>v_name,
                        argument_position=>i,
                        argument_value=>v_args(i)
                        );
                END LOOP;
            END IF;
            --
            IF v_enabled THEN
                DBMS_SCHEDULER.ENABLE(v_name);
            END IF;
        END;"""
        % job_sql,
        {
            "var_name": job_fullname,
            "var_job_type": module.params['job_type'],
            "var_job_action": module.params['job_action'],
            "var_job_style": 'LIGHTWEIGHT'
            if module.params['lightweight']
            else 'REGULAR',
            "var_job_class": module.params['job_class'],
            "var_credential": module.params['credential'],
            "var_destination": module.params['destination'],
            "var_restartable": 1 if module.params['restartable'] else 0,
            "var_repeat_interval": module.params['repeat_interval'],
            "var_logging_level": module.params['logging_level'],
            "var_program_name": module.params['program_name'],
            "var_schedule_name": module.params['schedule_name'],
            "var_comments": module.params['comments'],
            "var_enabled": 1 if module.params['enabled'] else 0,
            "var_auto_drop": 1 if module.params['auto_drop'] else 0,
            "var_args": var_args,
        },
    )


def drop_job(job_fullname):
    c = conn.cursor()
    c.execute("BEGIN DBMS_SCHEDULER.DROP_JOB(:name); END;", {"name": job_fullname})


def compare_with_owner(value1, value2, owner):
    if value1 is None or value2 is None:
        return value1 != value2
    else:
        return value1 != value2.upper() and value1 != "%s.%s" % (owner, value2.upper())


# Ansible code
def main():
    global conn, module, job_fullname
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
            enabled=dict(default=True, type='bool'),
            job_name=dict(required=True, aliases=["name"]),
            job_class=dict(default='DEFAULT_JOB_CLASS', aliases=["class"]),
            job_type=dict(
                default="plsql_block",
                choices=[
                    "plsql_block",
                    "stored_procedure",
                    "executable",
                    "external_script",
                    "sql_script",
                    "backup_script",
                ],
                aliases=["type"],
            ),
            job_action=dict(required=False, aliases=["action"]),
            job_arguments=dict(required=False, type='list', aliases=["arguments"]),
            lightweight=dict(default=False, type='bool'),
            credential=dict(required=False),
            destination=dict(required=False),
            restartable=dict(default=False, type='bool'),
            repeat_interval=dict(required=False),
            logging_level=dict(
                required=False, choices=["off", "runs", "failed runs", "full"]
            ),
            program_name=dict(required=False),
            schedule_name=dict(required=False),
            comments=dict(required=False),
            auto_drop=dict(default=False, type='bool'),
            convert_to_upper=dict(default=True, type='bool'),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['schedule_name', 'repeat_interval'],
            ['program_name', 'job_action'],
        ],
    )
    # Check input parameters
    re_name = re.compile(r"^[A-Za-z0-9_\$#]+\.[A-Za-z0-9_\$#]+$")
    if not re_name.match(module.params['job_name']):
        module.fail_json(msg="Invalid job name")
    job_fullname = (
        module.params['job_name'].upper()
        if module.params['convert_to_upper']
        else module.params['job_name']
    )
    job_parts = job_fullname.split(".")
    job_owner = job_parts[0]
    job_name = job_parts[1]
    job_fullname = "\"%s\".\"%s\"" % (job_owner, job_name)
    if module.params['lightweight'] and not module.params['program_name']:
        module.fail_json(msg="Lightweight jobs can only be created with program_name")
    if module.params['lightweight'] and module.params['restartable']:
        module.fail_json(msg="Lightweight jobs can't be restartable")
    if (
        module.params['state'] == 'present'
        and not module.params['job_action']
        and not module.params['program_name']
    ):
        module.fail_json(msg="Either job_action or program name must be set")
    if module.params['program_name'] and not re_name.match(
        module.params['program_name']
    ):
        module.fail_json(msg="Invalid program name, must be SCHEMANAME.PROGRAM_NAME")
    if module.params['schedule_name'] and not re_name.match(
        module.params['schedule_name']
    ):
        module.fail_json(msg="Invalid schedule name, must be SCHEMANAME.SCHEDULE_NAME")
    # Connect to database
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    if conn.version < "10.2":
        module.fail_json(msg="Database version must be 10gR2 or greater", changed=False)
    #
    if module.check_mode:
        module.exit_json(changed=False)
    #
    result = query_existing(job_owner, job_name)
    #
    changed = False
    if not result['exists'] and module.params['state'] == 'present':
        # Add job
        create_job()
        changed = True
    elif result['exists'] and module.params['state'] == 'absent':
        # Drop job
        drop_job(job_fullname)
        changed = True
    elif result['exists'] and module.params['state'] == 'present':
        # Modify job
        if (
            result['job_class'] != module.params['job_class']
            or result['job_type'] != module.params['job_type'].upper()
            or result['job_action'] != module.params['job_action']
            or result['repeat_interval'] != module.params['repeat_interval']
            or result['restartable'] != module.params['restartable']
            or result['logging_level'] != module.params['logging_level'].upper()
            or result['comments'] != module.params['comments']
            or result['auto_drop'] != module.params['auto_drop']
            or result['job_arguments'] != (module.params['job_arguments'] or [])
            or result['lightweight'] != module.params['lightweight']
            or result['enabled'] != module.params['enabled']
            or compare_with_owner(
                result['destination'], module.params['destination'], job_owner
            )
            or compare_with_owner(
                result['program_name'], module.params['program_name'], job_owner
            )
            or compare_with_owner(
                result['schedule_name'], module.params['schedule_name'], job_owner
            )
            or compare_with_owner(
                result['credential'], module.params['credential'], job_owner
            )
        ):
            # Actually drop the job and recreate it
            drop_job(job_fullname)
            create_job()
            changed = True

    module.exit_json(msg=msg[0], changed=changed)


if __name__ == '__main__':
    main()
