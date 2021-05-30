#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_jobclass
short_description: Manage DBMS_SCHEDULER job classes in Oracle database
description:
    - Manage DBMS_SCHEDULER job classes in Oracle database
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
            - If present, job class is created if absent then job class is removed
        required: true
        choices: ['present','absent']
    name:
        description:
            - Job class name
        required: True
    resource_group:
        description:
            - Resource manager resource consumer group the class is associated with
        required: False
    service:
        description:
            - Database service under what jobs run as
        required: False
    logging:
        description:
            - How much information is logged
        default: failed runs
        choices: ["off","runs","failed runs","full"]
    history:
        description:
            - Number of days the logs for this job class are retained
            - If set to 0, no logs will be kept
        required: False
        type: int
    comments:
        description:
            - Comment about the class
        required: False

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
    oracleservice: orcl
    oracleuser: system
    oraclepassword: oracle
    oracle_env:
      ORACLE_HOME: /usr/lib/oracle/12.1/client64
      LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib
  tasks:
    - name: job class
      oracle_jobclass:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
        state: present
        name: testclass
        logging: failed runs
        history: 14
      environment: "{{ oracle_env }}"
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

def query_existing(job_class_name):
    c = conn.cursor()
    c.execute("SELECT resource_consumer_group, service, logging_level, log_history, comments FROM all_scheduler_job_classes WHERE owner = 'SYS' AND job_class_name = :jobclass",
        {"jobclass": job_class_name.upper()})
    result = c.fetchone()
    if c.rowcount > 0:
        return {"exists": True, "resource_group": result[0], "service": result[1], "logging": result[2], "history": result[3], "comments": result[4]}
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
            state         = dict(default="present", choices=["present", "absent"]),
            name          = dict(required=True),
            resource_group= dict(required=False),
            service       = dict(required=False),
            logging       = dict(default="failed runs", choices=["off","runs","failed runs","full"]),
            history       = dict(required=False, type='int'),
            comments      = dict(required=False)
        ),
        supports_check_mode=True
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    # Check input parameters
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
    result = query_existing(module.params['name'])
    if result['exists'] and module.params['state'] == "present":
        # Check attributes and modify if needed
        if (result['comments'] != module.params['comments']) or (result['resource_group'] != module.params['resource_group']) or (result['service'] != module.params['service']) or (result['history'] != module.params['history']) or (result['logging'] != module.params['logging'].upper()):
            c = conn.cursor()
            c.execute("""
            DECLARE
                v_name VARCHAR2(100);
                v_service VARCHAR2(100);
                v_logging PLS_INTEGER;
                v_history PLS_INTEGER;
                v_resource VARCHAR2(100);
                v_comments VARCHAR2(4000);
            BEGIN
                v_logging:= CASE :logging WHEN 'off' THEN DBMS_SCHEDULER.LOGGING_OFF
                                          WHEN 'runs' THEN DBMS_SCHEDULER.LOGGING_RUNS
                                          WHEN 'failed runs' THEN DBMS_SCHEDULER.LOGGING_FAILED_RUNS
                                          WHEN 'full' THEN DBMS_SCHEDULER.LOGGING_FULL
                            END;
                v_name:= 'SYS.'||:name;
                v_resource:= :resource;
                v_service:= :service;
                v_history:= :history;
                v_comments:= :comments;
                DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'logging_level', v_logging);
                IF v_resource IS NOT NULL THEN
                    DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'resource_consumer_group', v_resource);
                ELSE
                    DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'resource_consumer_group');
                END IF;
                IF v_service IS NOT NULL THEN
                    DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'service', v_service);
                ELSE
                    DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'service');
                END IF;
                IF v_history IS NOT NULL THEN
                    DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'log_history', v_history);
                ELSE
                    DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'log_history');
                END IF;
                IF v_comments IS NOT NULL THEN
                    DBMS_SCHEDULER.SET_ATTRIBUTE(v_name, 'comments', v_comments);
                ELSE
                    DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(v_name, 'comments');
                END IF;
            END;
            """, {
                "logging": module.params['logging'],
                "name": module.params['name'].upper(),
                "resource": module.params['resource_group'],
                "service": module.params['service'],
                "history": module.params['history'],
                "comments": module.params['comments']
            })
            result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop job class
        c = conn.cursor()
        c.execute("BEGIN DBMS_SCHEDULER.DROP_JOB_CLASS(:name); END;", {"name": module.params['name'].upper()})
        result_changed = True
    elif not result['exists'] and module.params['state'] == "present":
        # Create job class
        c = conn.cursor()
        c.execute("""
        DECLARE
            v_logging PLS_INTEGER;
        BEGIN
            v_logging:= CASE :logging WHEN 'off' THEN DBMS_SCHEDULER.LOGGING_OFF
                                      WHEN 'runs' THEN DBMS_SCHEDULER.LOGGING_RUNS
                                      WHEN 'failed runs' THEN DBMS_SCHEDULER.LOGGING_FAILED_RUNS
                                      WHEN 'full' THEN DBMS_SCHEDULER.LOGGING_FULL
                        END;
            DBMS_SCHEDULER.CREATE_JOB_CLASS(job_class_name=>:name, resource_consumer_group=>:resource, service=>:service,
                logging_level=>v_logging, log_history=>:history, comments=>:comments);
        END;""", {
            "logging": module.params['logging'],
            "name": module.params['name'].upper(),
            "resource": module.params['resource_group'],
            "service": module.params['service'],
            "history": module.params['history'],
            "comments": module.params['comments']
        })
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
