#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_jobclass
short_description: Manage DBMS_SCHEDULER job classes in an Oracle database
description:
    - Creates, changes and drops DBMS_SCHEDULER job classes in an Oracle database.
    - Job classes are always owned by C(SYS). The existence is checked in
      C(ALL_SCHEDULER_JOB_CLASSES), so the connecting user must be able to see the
      job classes of C(SYS) (e.g. DBA privilege).
    - The job class name is converted to uppercase.
    - For an existing job class, O(comments), O(resource_group), O(service),
      O(history) and O(logging) are compared with the database. If one of them
      differs, all attributes are set again with C(DBMS_SCHEDULER.SET_ATTRIBUTE).
      Omitted optional attributes are set to NULL.
    - O(resource_group) and O(service) are compared case-sensitively with the stored
      (usually uppercase) values.
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
            - V(present) - the job class is created or its attributes are changed.
            - V(absent) - the job class is dropped.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
    name:
        description:
            - The name of the job class (without the C(SYS.) prefix).
        type: str
        required: true
    resource_group:
        description:
            - The resource manager consumer group the job class is associated with.
        type: str
        required: false
    service:
        description:
            - The database service the jobs of this class run under.
        type: str
        required: false
    logging:
        description:
            - How much information is logged for jobs of this class.
        type: str
        required: false
        default: failed runs
        choices: ['off', 'runs', 'failed runs', 'full']
    history:
        description:
            - The number of days the logs for this job class are retained.
            - If set to V(0), no logs will be kept.
            - If omitted, the global C(LOG_HISTORY) scheduler attribute applies.
        type: int
        required: false
    comments:
        description:
            - A comment about the job class.
        type: str
        required: false
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Oracle RDBMS 10gR2 or later required
    - In check mode, the module exits with C(changed=false) without checking
      the database.
requirements: [ "python-oracledb" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Create job class TESTCLASS
  opitzconsulting.ansible_oracle.oracle_jobclass:
    hostname: dbhost
    port: 1521
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    state: present
    name: testclass
    logging: failed runs
    history: 14
  environment:
    ORACLE_HOME: /usr/lib/oracle/12.1/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib

- name: Drop job class TESTCLASS (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_jobclass:
    service_name: orcl
    state: absent
    name: testclass
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


def query_existing(job_class_name):
    c = conn.cursor()
    c.execute(
        "SELECT resource_consumer_group, service, logging_level, log_history, comments "
        "FROM all_scheduler_job_classes "
        "WHERE owner = 'SYS' AND job_class_name = :jobclass",
        {"jobclass": job_class_name.upper()},
    )
    result = c.fetchone()
    if c.rowcount > 0:
        return {
            "exists": True,
            "resource_group": result[0],
            "service": result[1],
            "logging": result[2],
            "history": result[3],
            "comments": result[4],
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
            state=dict(default="present", choices=["present", "absent"]),
            name=dict(required=True),
            resource_group=dict(required=False),
            service=dict(required=False),
            logging=dict(
                default="failed runs", choices=["off", "runs", "failed runs", "full"]
            ),
            history=dict(required=False, type='int'),
            comments=dict(required=False),
        ),
        supports_check_mode=True,
    )
    # Check input parameters
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
    # c = conn.cursor()
    result_changed = False
    result = query_existing(module.params['name'])
    if result['exists'] and module.params['state'] == "present":
        # Check attributes and modify if needed
        if (
            (result['comments'] != module.params['comments'])
            or (result['resource_group'] != module.params['resource_group'])
            or (result['service'] != module.params['service'])
            or (result['history'] != module.params['history'])
            or (result['logging'] != module.params['logging'].upper())
        ):
            c = conn.cursor()
            c.execute(
                """
            DECLARE
                v_name VARCHAR2(100);
                v_service VARCHAR2(100);
                v_logging PLS_INTEGER;
                v_history PLS_INTEGER;
                v_resource VARCHAR2(100);
                v_comments VARCHAR2(4000);
            BEGIN
                v_logging:= CASE :logging
                            WHEN 'off' THEN DBMS_SCHEDULER.LOGGING_OFF
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
                    DBMS_SCHEDULER.SET_ATTRIBUTE(
                        v_name, 'resource_consumer_group', v_resource
                    );
                ELSE
                    DBMS_SCHEDULER.SET_ATTRIBUTE_NULL(
                        v_name, 'resource_consumer_group'
                    );
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
            """,
                {
                    "logging": module.params['logging'],
                    "name": module.params['name'].upper(),
                    "resource": module.params['resource_group'],
                    "service": module.params['service'],
                    "history": module.params['history'],
                    "comments": module.params['comments'],
                },
            )
            result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop job class
        c = conn.cursor()
        c.execute(
            "BEGIN DBMS_SCHEDULER.DROP_JOB_CLASS(:name); END;",
            {"name": module.params['name'].upper()},
        )
        result_changed = True
    elif not result['exists'] and module.params['state'] == "present":
        # Create job class
        c = conn.cursor()
        c.execute(
            """
        DECLARE
            v_logging PLS_INTEGER;
        BEGIN
            v_logging:= CASE :logging WHEN 'off' THEN DBMS_SCHEDULER.LOGGING_OFF
                        WHEN 'runs' THEN DBMS_SCHEDULER.LOGGING_RUNS
                        WHEN 'failed runs' THEN DBMS_SCHEDULER.LOGGING_FAILED_RUNS
                        WHEN 'full' THEN DBMS_SCHEDULER.LOGGING_FULL
                        END;
            DBMS_SCHEDULER.CREATE_JOB_CLASS(
                job_class_name=>:name,
                resource_consumer_group=>:resource,
                service=>:service,
                logging_level=>v_logging,
                log_history=>:history,
                comments=>:comments
                );
        END;""",
            {
                "logging": module.params['logging'],
                "name": module.params['name'].upper(),
                "resource": module.params['resource_group'],
                "service": module.params['service'],
                "history": module.params['history'],
                "comments": module.params['comments'],
            },
        )
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


if __name__ == '__main__':
    main()
