#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_rsrc_consgroup
short_description: Manage DBMS_RESOURCE_MANAGER consumer groups
description:
    - Creates, changes and drops Resource Manager consumer groups with
      C(DBMS_RESOURCE_MANAGER), including their consumer group mappings and the
      switch privileges (C(DBMS_RESOURCE_MANAGER_PRIVS)).
    - Can be run locally on the control machine or on a remote host.
    - For more accurate documentation about attributes, please check Oracle DB
      documentation about DBMS_RESOURCE_MANAGER.
    - The existence of the consumer group is checked in
      C(DBA_RSRC_CONSUMER_GROUPS) with the uppercased O(name).
    - With O(state=present), an existing group is changed if O(comments),
      O(mgmt_mth), O(category), the switch grants or the mappings differ. Grants
      and mappings are synchronised completely, entries not listed are removed.
    - If neither O(user) nor O(password) is given, a connection with an Oracle
      wallet (C(/@<service_name>)) is used. Otherwise both must be set.
    - In check mode the module only connects to the database and returns
      changed=false. No changes are predicted.
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
            - The Oracle user name to connect to the database, must have DBA
              privileges.
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
            - V(present) - the consumer group is created or changed, grants and
              mappings are synchronised.
            - V(absent) - the consumer group is dropped
              (C(DBMS_RESOURCE_MANAGER.DELETE_CONSUMER_GROUP)).
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
    name:
        description:
            - Resource consumer group name.
        type: str
        required: true
    comments:
        description:
            - Comment for the consumer group.
        type: str
        required: false
    mgmt_mth:
        description:
            - Resource allocation method for distributing CPU among sessions in the
              consumer group, V(round-robin) or V(run-to-completion).
            - Compared case-insensitively with the existing value.
        type: str
        required: false
        default: round-robin
    category:
        description:
            - The category of the consumer group, e.g. V(other), V(interactive),
              V(batch) or V(maintenance).
            - Compared case-insensitively with the existing value.
        type: str
        required: false
        default: other
    map_client_id:
        description:
            - Sessions whose C(CLIENT_ID) matches one of the values are mapped
              to this consumer group.
            - C(CLIENT_ID) is the client identifier of the session.
            - Mappings are set with
              C(DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING). Values are
              converted to uppercase.
            - With O(state=present), all existing mappings of this consumer group
              that are not listed in any C(map_*) option are removed.
        type: list
        elements: str
        required: false
    map_client_machine:
        description:
            - Sessions whose C(CLIENT_MACHINE) matches one of the values are mapped
              to this consumer group.
            - C(CLIENT_MACHINE) is the name of the client machine.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_client_os_user:
        description:
            - Sessions whose C(CLIENT_OS_USER) matches one of the values are mapped
              to this consumer group.
            - C(CLIENT_OS_USER) is the operating system user of the client.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_client_program:
        description:
            - Sessions whose C(CLIENT_PROGRAM) matches one of the values are mapped
              to this consumer group.
            - C(CLIENT_PROGRAM) is the name of the client program.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_module_name:
        description:
            - Sessions whose C(MODULE_NAME) matches one of the values are mapped
              to this consumer group.
            - C(MODULE_NAME) is the module name set with C(DBMS_APPLICATION_INFO).
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_module_name_action:
        description:
            - Sessions whose C(MODULE_NAME_ACTION) matches one of the values are mapped
              to this consumer group.
            - C(MODULE_NAME_ACTION) is module name and action, separated by a dot.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_oracle_function:
        description:
            - Sessions whose C(ORACLE_FUNCTION) matches one of the values are mapped
              to this consumer group.
            - C(ORACLE_FUNCTION) is an Oracle function, e.g. V(BACKUP) or V(COPY).
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_oracle_user:
        description:
            - Sessions whose C(ORACLE_USER) matches one of the values are mapped
              to this consumer group.
            - C(ORACLE_USER) is the database user name.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_oracle_user_profile:
        description:
            - List of profiles. All users that have one of these profiles at module
              runtime are added to O(map_oracle_user).
        type: list
        elements: str
        required: false
    map_service_module:
        description:
            - Sessions whose C(SERVICE_MODULE) matches one of the values are mapped
              to this consumer group.
            - C(SERVICE_MODULE) is service name and module name, separated by a dot.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_service_module_action:
        description:
            - Sessions whose C(SERVICE_MODULE_ACTION) matches one of the values are
              mapped to this consumer group.
            - C(SERVICE_MODULE_ACTION) is service, module and action, separated by dots.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    map_service_name:
        description:
            - Sessions whose C(SERVICE_NAME) matches one of the values are mapped
              to this consumer group.
            - C(SERVICE_NAME) is the service name used to connect.
            - See O(map_client_id) for the mapping behaviour.
        type: list
        elements: str
        required: false
    grant_name:
        description:
            - List of users and roles that are granted the privilege to switch to this
              consumer group (C(GRANT_SWITCH_CONSUMER_GROUP)).
            - Names are converted to uppercase. Users and roles that do not exist in
              the database are silently ignored.
            - With O(state=present), the switch privilege is revoked from all other
              grantees that are not covered by O(grant_name) or
              O(grant_user_profile).
        type: list
        elements: str
        required: false
        aliases: ['grant', 'grant_user', 'grant_role', 'grants']
    grant_user_profile:
        description:
            - List of profiles. All users that have one of these profiles at module
              runtime are granted the privilege to switch to this consumer group.
        type: list
        elements: str
        required: false
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Oracle RDBMS 11gR2 or later required
requirements: [ "python-oracledb" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Create consumer group with grants and mappings
  opitzconsulting.ansible_oracle.oracle_rsrc_consgroup:
    hostname: dbhost
    port: 1521
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    state: present
    name: testgroup1
    comments: hello world
    grant:
      - OE
      - SH
      - PM
      - IX
    grant_user_profile:
      - HR1
    map_oracle_user_profile:
      - HR1
    map_oracle_user:
      - OE
      - SH
      - PM
      - IX
    map_service_name:
      - app1
      - app2
    map_client_machine:
      - appserver3
  environment:
    ORACLE_HOME: /usr/lib/oracle/19/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/19/client64/lib

- name: Drop consumer group (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_rsrc_consgroup:
    service_name: orcl
    name: testgroup1
    state: absent
'''

RETURN = '''
msg:
    description:
        - Comma-separated summary of the added and removed grants and mappings.
        - Empty if nothing was changed. Not returned in check mode.
    returned: success
    type: str
    sample: "Added grants: ['OE'], Removed grants: [], Added mappings:
      {'ORACLE_USER': {'OE'}}, Removed mappings: {}"
'''


def query_existing(name):
    cgname = name.upper()
    c = conn.cursor()
    c.execute(
        "SELECT mgmt_method, comments, category "
        "FROM dba_rsrc_consumer_groups "
        "WHERE consumer_group = :name",
        {"name": cgname},
    )
    result = c.fetchone()
    if c.rowcount > 0:
        grants = set()
        c.execute(
            (
                "SELECT grantee "
                "FROM dba_rsrc_consumer_group_privs "
                "WHERE granted_group = :name"
            ),
            {"name": cgname},
        )
        res = c.fetchall()
        for row in res:
            grants.add(row[0])
        mappings = {}
        c.execute(
            (
                "SELECT attribute, LISTAGG(value,':') WITHIN GROUP (ORDER BY value) "
                "FROM dba_rsrc_group_mappings "
                "WHERE consumer_group = :name "
                "GROUP BY attribute"
            ),
            {"name": cgname},
        )
        res = c.fetchall()
        for row in res:
            mappings[row[0]] = set(row[1].split(":"))
        return {
            "exists": True,
            "mgmt_mth": result[0],
            "comments": result[1],
            "category": result[2],
            "grants": grants,
            "mappings": mappings,
        }
    else:
        return {"exists": False}


def profile_list_to_users(profiles):
    pusers = []
    inlist = [":%i" % k for k in range(len(profiles))]
    c = conn.cursor()
    c.execute(
        "SELECT username FROM dba_users WHERE profile IN (%s)" % ",".join(inlist),
        [p.upper() for p in profiles],
    )
    res = c.fetchall()
    for row in res:
        pusers.append(row[0])
    c.close()
    return pusers


def new_grants_list(users, profiles):
    s = set()
    # Return the list of users and roles that actually exist
    if users:
        pusers = []
        inlist = [":%i" % k for k in range(len(users))]
        c = conn.cursor()
        c.execute(
            (
                "SELECT username "
                "FROM (SELECT username FROM dba_users "
                "      UNION ALL "
                "      SELECT role FROM dba_roles) "
                "WHERE username IN (%s)"
            )
            % ",".join(inlist),
            [p.upper() for p in users],
        )
        res = c.fetchall()
        for row in res:
            pusers.append(row[0])
        c.close()
        s.update(pusers)
    # For profiles get the user list that have this profile
    if profiles:
        s.update(profile_list_to_users(profiles))
    return s


def new_mappings_dict():
    s = {}
    for key in module.params.keys():
        if key[:4] == 'map_' and module.params[key]:
            new_key = key[4:].upper()
            s[new_key] = set([v.upper() for v in module.params[key]])
    if "ORACLE_USER_PROFILE" in s:
        if "ORACLE_USER" not in s:
            s["ORACLE_USER"] = set()
        s["ORACLE_USER"].update(profile_list_to_users(s["ORACLE_USER_PROFILE"]))
        del s["ORACLE_USER_PROFILE"]
    return s


# Ansible code
def main():
    global conn, msg, module
    msg = []
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
            mgmt_mth=dict(default='round-robin'),
            category=dict(default='other'),
            comments=dict(required=False),
            map_client_id=dict(required=False, type='list'),
            map_client_machine=dict(required=False, type='list'),
            map_client_os_user=dict(required=False, type='list'),
            map_client_program=dict(required=False, type='list'),
            map_module_name=dict(required=False, type='list'),
            map_module_name_action=dict(required=False, type='list'),
            map_oracle_function=dict(required=False, type='list'),
            map_oracle_user=dict(required=False, type='list'),
            map_oracle_user_profile=dict(required=False, type='list'),
            map_service_module=dict(required=False, type='list'),
            map_service_module_action=dict(required=False, type='list'),
            map_service_name=dict(required=False, type='list'),
            grant_name=dict(
                required=False,
                type='list',
                aliases=['grant', 'grant_user', 'grant_role', 'grants'],
            ),
            grant_user_profile=dict(required=False, type='list'),
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
    if conn.version < "11.2":
        module.fail_json(msg="Database version must be 11gR2 or greater", changed=False)
    #
    if module.check_mode:
        module.exit_json(changed=False)
    #
    result_changed = False
    result = query_existing(module.params['name'])
    if module.params['state'] == 'present':
        new_grants = new_grants_list(
            module.params['grant_name'], module.params['grant_user_profile']
        )
        new_mappings = new_mappings_dict()
    if result['exists'] and module.params['state'] == "present":
        # Check attributes and modify if needed
        if (
            (result['comments'] != module.params['comments'])
            or (result['mgmt_mth'] != module.params['mgmt_mth'].upper())
            or (result['category'] != module.params['category'].upper())
            or (new_grants != result['grants'])
            or (new_mappings != result['mappings'])
        ):
            c = conn.cursor()
            added_grants = list(new_grants - result['grants'])
            msg.append("Added grants: %s" % str(added_grants))
            removed_grants = list(result['grants'] - new_grants)
            msg.append("Removed grants: %s" % str(removed_grants))
            c.execute(
                """
            BEGIN
                DBMS_RESOURCE_MANAGER.CLEAR_PENDING_AREA;
                DBMS_RESOURCE_MANAGER.CREATE_PENDING_AREA;
                DBMS_RESOURCE_MANAGER.UPDATE_CONSUMER_GROUP(
                    consumer_group=>:name,
                    new_comment=>:comments,
                    new_mgmt_mth=>:mgmt_mth,
                    new_category=>:category
                    );
            END;""",
                {
                    "name": module.params['name'],
                    "comments": module.params['comments'],
                    "mgmt_mth": module.params['mgmt_mth'],
                    "category": module.params['category'],
                },
            )
            # Added mappings
            added_maps = {}
            for map_attr in new_mappings.keys():
                s = new_mappings[map_attr]
                t = (
                    result['mappings'][map_attr]
                    if map_attr in result['mappings']
                    else set()
                )
                added_maps[map_attr] = s - t
                for map_value in added_maps[map_attr]:
                    c.execute(
                        """
                    BEGIN
                        DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING(
                            attribute=>:attr,
                            value=>:val,
                            consumer_group=>:group
                            );
                    END;""",
                        {
                            'attr': map_attr,
                            'val': map_value,
                            'group': module.params['name'],
                        },
                    )
            msg.append("Added mappings: %s" % str(added_maps))
            # Removed mappings
            removed_maps = {}
            for map_attr in result['mappings'].keys():
                s = result['mappings'][map_attr]
                t = new_mappings[map_attr] if map_attr in new_mappings else set()
                removed_maps[map_attr] = s - t
                for map_value in removed_maps[map_attr]:
                    c.execute(
                        """
                    BEGIN
                        DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING(
                            attribute=>:attr,
                            value=>:val,
                            consumer_group=>NULL
                            );
                    END;""",
                        {'attr': map_attr, 'val': map_value},
                    )
            msg.append("Removed mappings: %s" % str(removed_maps))
            # Grants
            var_add_grants = c.arrayvar(oracledb.STRING, added_grants)
            var_remove_grants = c.arrayvar(oracledb.STRING, removed_grants)
            c.execute(
                """
            DECLARE
                TYPE str_array IS TABLE OF VARCHAR2(500) INDEX BY BINARY_INTEGER;
                v_name VARCHAR2(50);
                v_add_grants str_array;
                v_remove_grants str_array;
            BEGIN
                v_name:= :name;
                v_add_grants:= :add_grants;
                v_remove_grants:= :remove_grants;
                DBMS_RESOURCE_MANAGER.VALIDATE_PENDING_AREA;
                DBMS_RESOURCE_MANAGER.SUBMIT_PENDING_AREA;
                FOR i IN 1..v_add_grants.COUNT LOOP
                    DBMS_RESOURCE_MANAGER_PRIVS.GRANT_SWITCH_CONSUMER_GROUP(
                        grantee_name=>v_add_grants(i),
                        consumer_group=>v_name,
                        grant_option=>false
                        );
                END LOOP;
                FOR i IN 1..v_remove_grants.COUNT LOOP
                    DBMS_RESOURCE_MANAGER_PRIVS.REVOKE_SWITCH_CONSUMER_GROUP(
                        revokee_name=>v_remove_grants(i),
                        consumer_group=>v_name
                        );
                END LOOP;
            END;""",
                {
                    "name": module.params['name'],
                    "add_grants": var_add_grants,
                    "remove_grants": var_remove_grants,
                },
            )
            result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop job class
        c = conn.cursor()
        c.execute(
            """
        BEGIN
            DBMS_RESOURCE_MANAGER.CLEAR_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.CREATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.DELETE_CONSUMER_GROUP(:name);
            DBMS_RESOURCE_MANAGER.VALIDATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.SUBMIT_PENDING_AREA;
        END;""",
            {"name": module.params['name']},
        )
        result_changed = True
    elif not result['exists'] and module.params['state'] == "present":
        # Create job class
        c = conn.cursor()
        msg.append("Added grants: %s" % str(new_grants))
        msg.append("Added mappings: %s" % str(new_mappings))
        c.execute(
            """
        BEGIN
            DBMS_RESOURCE_MANAGER.CLEAR_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.CREATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.CREATE_CONSUMER_GROUP(
                consumer_group=>:name,
                comment=>:comments,
                mgmt_mth=>:mgmt_mth,
                category=>:category
                );
        END;""",
            {
                "name": module.params['name'],
                "comments": module.params['comments'],
                "mgmt_mth": module.params['mgmt_mth'],
                "category": module.params['category'],
            },
        )
        # Mappings
        for map_attr in new_mappings.keys():
            for map_value in new_mappings[map_attr]:
                c.execute(
                    """
                BEGIN
                    DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING(
                        attribute=>:attr,
                        value=>:val,
                        consumer_group=>:group
                        );
                END;""",
                    {
                        'attr': map_attr,
                        'val': map_value,
                        'group': module.params['name'],
                    },
                )
        # Grants
        # Can't put under IF, since need to execute validate and submit commands anyway
        var_grants = c.arrayvar(oracledb.STRING, list(new_grants))
        c.execute(
            """
        DECLARE
            TYPE str_array IS TABLE OF VARCHAR2(500) INDEX BY BINARY_INTEGER;
            v_name VARCHAR2(50);
            v_grants str_array;
        BEGIN
            v_name:= :name;
            v_grants:= :grants;
            DBMS_RESOURCE_MANAGER.VALIDATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.SUBMIT_PENDING_AREA;
            FOR i IN 1..v_grants.COUNT LOOP
                DBMS_RESOURCE_MANAGER_PRIVS.GRANT_SWITCH_CONSUMER_GROUP(
                    grantee_name=>v_grants(i),
                    consumer_group=>v_name,
                    grant_option=>false
                    );
            END LOOP;
        END;
        """,
            {"name": module.params['name'], "grants": var_grants},
        )
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


if __name__ == '__main__':
    main()
