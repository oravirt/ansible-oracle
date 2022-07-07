#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_job
short_description: Manage DBMS_SCHEDULER jobs in Oracle database
description:
    - Manage DBMS_SCHEDULER jobs in an Oracle database
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
        required: false
        default: normal
        choices:
            - normal
            - sysdba
    state:
        description:
            - If present, then job is created, if absent then job is dropped
        required: true
        choices:
            - present
            - absent
    enabled:
        description:
            - Is job enabled
        required: false
        default: true
        type: bool
    job_name:
        description:
            - Job name, can be specified with owner schema name
        required: True
        aliases:
            - name
    job_class:
        description:
            - Job class
        required: false
        default: DEFAULT_JOB_CLASS
        aliases:
            - class
    job_type:
        description:
            - Job type
        required: false
        default: plsql_block
        choices:
            - plsql_block
            - stored_procedure
            - executable
            - external_script
            - sql_script
            - backup_script
        aliases:
            - type
    job_action:
        description:
            - Job action (what is executed)
        required: false
        aliases:
            - action
    job_arguments:
        description:
            - List of arguments passed to job, only positional arguments supported
        required: false
        type: list
        aliases:
            - arguments
    lightweight:
        description:
            - Is it lightweight job
        required: false
        default: False
        type: bool
    credential:
        description:
            - Credential name
        required: false
    destination:
        description:
            - Destination name
        required: false
    restartable:
        description:
            - Is job restartable
        required: false
        default: False
        type: bool
    repeat_interval:
        description:
            - Job repeat interval
        required: false
    logging_level:
        description:
            - Job logging level
        required: false
        choices:
            - off
            - runs
            - failed runs
            - full
    program_name:
        description:
            - Associated DBMS_SCHEDULER program name
        required: false
    schedule_name:
        description:
            - Associated DBMS_SCHEDULER schedule name
        required: false
    comments:
        description:
            - Job comments
        required: false
    auto_drop:
        description:
            - Is job automatically dropped after execution
        required: false
        default: False
        type: bool
    convert_to_upper:
        description:
            - Job name automatically converted to upper case
        required: false
        default: True
        type: bool
notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 10gR2 or later required
requirements: [ "cx_Oracle", "re" ]
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
    - name: drop job
      oracle_job:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
        state: absent
        name: hr.j1
      environment: "{{ oracle_env }}"
    - name: create job
      oracle_job:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
        state: present
        name: hr.j1
        action: begin null; null; end;
        logging_level: runs
        comments: This job is just for testing something
        repeat_interval: FREQ=HOURLY;interval=3
        enabled: False
        lightweight: False
        restartable: True
      environment: "{{ oracle_env }}"
'''

import re

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

def query_existing(job_owner, job_name):
    c = conn.cursor()
    c.execute("""SELECT job_style, program_owner, program_name, job_type, job_action, number_of_arguments, schedule_owner, schedule_name, schedule_type,
        repeat_interval, job_class, enabled, restartable, state, logging_level, instance_stickiness, destination_owner, destination, credential_owner,
        credential_name, comments, auto_drop
        FROM all_scheduler_jobs j WHERE owner = :owner AND job_name = :name""",
        {"owner": job_owner.upper(), "name": job_name.upper()})
    result = c.fetchone()
    if c.rowcount > 0:
        args = []
        if result[5] > 0:
            c.execute("SELECT value FROM all_scheduler_job_args WHERE owner = :owner AND job_name = :name ORDER BY argument_position", {"owner": job_owner.upper(), "name": job_name.upper()})
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
            "job_arguments": args}
    else:
        return {"exists": False}

def create_job():
    c = conn.cursor()
    var_args = c.arrayvar(cx_Oracle.STRING, [] if module.params['job_arguments'] is None else module.params['job_arguments'])
    # Bild the right CREATE_JOB command
    job_sql = "job_name=>v_name,comments=>v_comments,auto_drop=>v_auto_drop"
    if module.params['job_class']:
        job_sql+= ",job_class=>v_job_class"
    if module.params['program_name']:
        job_sql+= ",program_name=>v_program_name"
        if module.params['lightweight']:
            job_sql+= ",job_style=>v_job_style"
    else:
        job_sql+= ",job_type=>v_job_type,job_action=>v_job_action,number_of_arguments=>v_num_args"
    if module.params['schedule_name']:
        job_sql+= ",schedule_name=>v_schedule_name"
    else:
        job_sql+= ",repeat_interval=>v_repeat_interval"
    if module.params['credential']:
        job_sql+= ",credential_name=>v_cred"
    if module.params['destination']:
        job_sql+= ",destination_name=>v_dest"
    c.execute("""
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
                    DBMS_SCHEDULER.SET_JOB_ARGUMENT_VALUE(job_name=>v_name, argument_position=>i, argument_value=>v_args(i));
                END LOOP;
            END IF;
            --
            IF v_enabled THEN
                DBMS_SCHEDULER.ENABLE(v_name);
            END IF;
        END;""" % job_sql, {
            "var_name": job_fullname,
            "var_job_type": module.params['job_type'],
            "var_job_action": module.params['job_action'],
            "var_job_style": 'LIGHTWEIGHT' if module.params['lightweight'] else 'REGULAR',
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
            "var_args": var_args
        })

def drop_job(job_fullname):
    c = conn.cursor()
    c.execute("BEGIN DBMS_SCHEDULER.DROP_JOB(:name); END;", {"name": job_fullname})

def compare_with_owner(value1, value2, owner):
    if value1 is None or value2 is None:
        return value1 != value2
    else:
        return (value1 != value2.upper() and value1 != "%s.%s" % (owner, value2.upper()))

# Ansible code
def main():
    global lconn, conn, lparam, module, job_fullname
    msg = ['']
    module = AnsibleModule(
        argument_spec = dict(
            hostname      = dict(default='localhost'),
            port          = dict(default=1521, type='int'),
            service_name  = dict(required=True),
            user          = dict(required=False),
            password      = dict(required=False),
            mode          = dict(default='normal', choices=["normal","sysdba"]),
            state         = dict(default="present", choices=["present", "absent"]),
            enabled       = dict(default=True, type='bool'),
            job_name      = dict(required=True, aliases=["name"]),
            job_class     = dict(default='DEFAULT_JOB_CLASS', aliases=["class"]),
            job_type      = dict(default="plsql_block", choices=["plsql_block","stored_procedure","executable","external_script","sql_script","backup_script"], aliases=["type"]),
            job_action    = dict(required=False, aliases=["action"]),
            job_arguments = dict(required=False, type='list', aliases=["arguments"]),
            lightweight   = dict(default=False, type='bool'),
            credential    = dict(required=False),
            destination   = dict(required=False),
            restartable   = dict(default=False, type='bool'),
            repeat_interval = dict(required=False),
            logging_level = dict(required=False, choices=["off","runs","failed runs","full"]),
            program_name  = dict(required=False),
            schedule_name = dict(required=False),
            comments      = dict(required=False),
            auto_drop     = dict(default=False, type='bool'),
            convert_to_upper = dict(default=True, type='bool')
        ),
        supports_check_mode=True,
        mutually_exclusive=[['schedule_name','repeat_interval'],['program_name','job_action']]
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    # Check input parameters
    re_name = re.compile("^[A-Za-z0-9_\$#]+\.[A-Za-z0-9_\$#]+$")
    if not re_name.match(module.params['job_name']):
        module.fail_json(msg="Invalid job name")
    job_fullname = module.params['job_name'].upper() if module.params['convert_to_upper'] else module.params['job_name']
    job_parts = job_fullname.split(".")
    job_owner = job_parts[0]
    job_name = job_parts[1]
    job_fullname = "\"%s\".\"%s\"" % (job_owner, job_name)
    if module.params['lightweight'] and not module.params['program_name']:
        module.fail_json(msg="Lightweight jobs can only be created with program_name")
    if module.params['lightweight'] and module.params['restartable']:
        module.fail_json(msg="Lightweight jobs can't be restartable")
    if module.params['state'] == 'present' and not module.params['job_action'] and not module.params['program_name']:
        module.fail_json(msg="Either job_action or program name must be set")
    if module.params['program_name'] and not re_name.match(module.params['program_name']):
        module.fail_json(msg="Invalid program name, must be SCHEMANAME.PROGRAM_NAME")
    if module.params['schedule_name'] and not re_name.match(module.params['schedule_name']):
        module.fail_json(msg="Invalid schedule name, must be SCHEMANAME.SCHEDULE_NAME")
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
        if (    result['job_class'] != module.params['job_class'] or
                result['job_type'] != module.params['job_type'].upper() or
                result['job_action'] != module.params['job_action'] or
                result['repeat_interval'] != module.params['repeat_interval'] or
                result['restartable'] != module.params['restartable'] or
                result['logging_level'] != module.params['logging_level'].upper() or
                result['comments'] != module.params['comments'] or
                result['auto_drop'] != module.params['auto_drop'] or
                result['job_arguments'] != (module.params['job_arguments'] or []) or
                result['lightweight'] != module.params['lightweight'] or
                result['enabled'] != module.params['enabled'] or
                compare_with_owner(result['destination'], module.params['destination'], job_owner) or
                compare_with_owner(result['program_name'], module.params['program_name'], job_owner) or
                compare_with_owner(result['schedule_name'], module.params['schedule_name'], job_owner) or
                compare_with_owner(result['credential'], module.params['credential'], job_owner) ):
            # Actually drop the job and recreate it
            drop_job(job_fullname)
            create_job()
            changed = True

    module.exit_json(msg=msg[0], changed=changed)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
