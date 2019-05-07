#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_rsrc_consgroup
short_description: Manage DBMS_RESOURCE_MANAGER consumer groups
description:
    - Manage DBMS_RESOURCE_MANAGER consumer groups
    - Can be run locally on the controlmachine or on a remote host
    - For more accurate documentation about attributes, please check Oracle DB documentation about DBMS_RESOURCE_MANAGER
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
            - If present, then consumer group is created, if absent, then consumer group is removed
        required: true
        choices: ['present','absent']
    name:
        description:
            - Resource consumer group name
        required: True
    comments:
        description:
            - Comment about the group
        required: False
    mgmt_mth:
        description:
            - Name of CPU resource allocation method
        default: round-robin
    category:
        description:
            - Describes the category of the consumer group
        default: other
    map_client_id:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_client_machine:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_client_os_user:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_client_program:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_module_name:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_module_name_action:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_oracle_function:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_oracle_user:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_oracle_user_profile:
        description:
            - Module appends all users with mentioned profiles to map_oracle_user parameter list
        required: False
        type: list
    map_service_module:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_service_module_action:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    map_service_name:
        description:
            - This procedure adds, deletes, or modifies entries that map sessions to consumer groups, based on the session's login and runtime attributes. Check Oracle documentation on DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING on more details.
        required: False
        type: list
    grant_name:
        description:
            - List of users and roles that will be granted switch to this consumer group
        type: list
        required: False
        aliases:
            - grant
            - grant_user
            - grant_role
            - grants
    grant_user_profile:
        description:
            - All users with these profiles will be granted switch to this consumer group
        type: list
        required: False

notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 11gR2 or later required
requirements: [ "cx_Oracle" ]
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
    - name: job class
      oracle_rsrc_consgroup:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
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
      environment: "{{ oracle_env }}"
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

def query_existing(name):
    cgname = name.upper()
    c = conn.cursor()
    c.execute("SELECT mgmt_method, comments, category FROM dba_rsrc_consumer_groups WHERE consumer_group = :name",
        {"name": cgname})
    result = c.fetchone()
    if c.rowcount > 0:
        grants = set()
        c.execute("SELECT grantee FROM dba_rsrc_consumer_group_privs WHERE granted_group = :name", {"name": cgname})
        res = c.fetchall()
        for row in res:
            grants.add(row[0])
        mappings = {}
        c.execute("SELECT attribute, LISTAGG(value,':') WITHIN GROUP (ORDER BY value) FROM dba_rsrc_group_mappings WHERE consumer_group = :name GROUP BY attribute", {"name": cgname})
        res = c.fetchall()
        for row in res:
            mappings[row[0]] = set(row[1].split(":"))
        return {"exists": True, "mgmt_mth": result[0], "comments": result[1], "category": result[2], "grants": grants, "mappings": mappings}
    else:
        return {"exists": False}

def profile_list_to_users(profiles):
    pusers = []
    inlist = [":%i" % k for k in range(len(profiles))]
    c = conn.cursor()
    c.execute("SELECT username FROM dba_users WHERE profile IN (%s)" % ",".join(inlist), [p.upper() for p in profiles])
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
        c.execute("SELECT username FROM (SELECT username FROM dba_users UNION ALL SELECT role FROM dba_roles) WHERE username IN (%s)" % ",".join(inlist), [p.upper() for p in users])
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
    global lconn, conn, msg, module
    msg = []
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
            mgmt_mth      = dict(default='round-robin'),
            category      = dict(default='other'),
            comments      = dict(required=False),
            map_client_id = dict(required=False, type='list'),
            map_client_machine = dict(required=False, type='list'),
            map_client_os_user = dict(required=False, type='list'),
            map_client_program = dict(required=False, type='list'),
            map_module_name = dict(required=False, type='list'),
            map_module_name_action = dict(required=False, type='list'),
            map_oracle_function = dict(required=False, type='list'),
            map_oracle_user = dict(required=False, type='list'),
            map_oracle_user_profile = dict(required=False, type='list'),
            map_service_module = dict(required=False, type='list'),
            map_service_module_action = dict(required=False, type='list'),
            map_service_name = dict(required=False, type='list'),
            grant_name    = dict(required=False, type='list', aliases=['grant','grant_user','grant_role','grants']),
            grant_user_profile = dict(required=False, type='list')
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
    if conn.version < "11.2":
        module.fail_json(msg="Database version must be 11gR2 or greater", changed=False)
    #
    if module.check_mode:
        module.exit_json(changed=False)
    #
    result_changed = False
    result = query_existing(module.params['name'])
    if module.params['state'] == 'present':
        new_grants = new_grants_list(module.params['grant_name'], module.params['grant_user_profile'])
        new_mappings = new_mappings_dict()
    if result['exists'] and module.params['state'] == "present":
        # Check attributes and modify if needed
        if ((result['comments'] != module.params['comments']) or (result['mgmt_mth'] != module.params['mgmt_mth'].upper()) or
                (result['category'] != module.params['category'].upper()) or (new_grants != result['grants']) or (new_mappings != result['mappings'])):
            c = conn.cursor()
            added_grants = list(new_grants - result['grants'])
            msg.append("Added grants: %s" % str(added_grants))
            removed_grants = list(result['grants'] - new_grants)
            msg.append("Removed grants: %s" % str(removed_grants))
            c.execute("""
            BEGIN
                DBMS_RESOURCE_MANAGER.CLEAR_PENDING_AREA;
                DBMS_RESOURCE_MANAGER.CREATE_PENDING_AREA;
                DBMS_RESOURCE_MANAGER.UPDATE_CONSUMER_GROUP(consumer_group=>:name, new_comment=>:comments, new_mgmt_mth=>:mgmt_mth, new_category=>:category);
            END;""", {
                "name": module.params['name'],
                "comments": module.params['comments'],
                "mgmt_mth": module.params['mgmt_mth'],
                "category": module.params['category']
            })
            # Added mappings
            added_maps = {}
            for map_attr in new_mappings.keys():
                s = new_mappings[map_attr]
                t = result['mappings'][map_attr] if map_attr in result['mappings'] else set()
                added_maps[map_attr] = s-t
                for map_value in added_maps[map_attr]:
                    c.execute("""
                    BEGIN
                        DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING(attribute=>:attr, value=>:val, consumer_group=>:group);
                    END;""", {'attr': map_attr, 'val': map_value, 'group': module.params['name']})
            msg.append("Added mappings: %s" % str(added_maps))
            # Removed mappings
            removed_maps = {}
            for map_attr in result['mappings'].keys():
                s = result['mappings'][map_attr]
                t = new_mappings[map_attr] if map_attr in new_mappings else set()
                removed_maps[map_attr] = s-t
                for map_value in removed_maps[map_attr]:
                    c.execute("""
                    BEGIN
                        DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING(attribute=>:attr, value=>:val, consumer_group=>NULL);
                    END;""", {'attr': map_attr, 'val': map_value})
            msg.append("Removed mappings: %s" % str(removed_maps))
            # Grants
            var_add_grants = c.arrayvar(cx_Oracle.STRING, added_grants)
            var_remove_grants = c.arrayvar(cx_Oracle.STRING, removed_grants)
            c.execute("""
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
                    DBMS_RESOURCE_MANAGER_PRIVS.GRANT_SWITCH_CONSUMER_GROUP(grantee_name=>v_add_grants(i), consumer_group=>v_name, grant_option=>false);
                END LOOP;
                FOR i IN 1..v_remove_grants.COUNT LOOP
                    DBMS_RESOURCE_MANAGER_PRIVS.REVOKE_SWITCH_CONSUMER_GROUP(revokee_name=>v_remove_grants(i), consumer_group=>v_name);
                END LOOP;
            END;""", {
                "name": module.params['name'],
                "add_grants": var_add_grants,
                "remove_grants": var_remove_grants
            })
            result_changed = True
    elif result['exists'] and module.params['state'] == "absent":
        # Drop job class
        c = conn.cursor()
        c.execute("""
        BEGIN
            DBMS_RESOURCE_MANAGER.CLEAR_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.CREATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.DELETE_CONSUMER_GROUP(:name);
            DBMS_RESOURCE_MANAGER.VALIDATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.SUBMIT_PENDING_AREA;
        END;""", {"name": module.params['name']})
        result_changed = True
    elif not result['exists'] and module.params['state'] == "present":
        # Create job class
        c = conn.cursor()
        msg.append("Added grants: %s" % str(new_grants))
        msg.append("Added mappings: %s" % str(new_mappings))
        c.execute("""
        BEGIN
            DBMS_RESOURCE_MANAGER.CLEAR_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.CREATE_PENDING_AREA;
            DBMS_RESOURCE_MANAGER.CREATE_CONSUMER_GROUP(consumer_group=>:name, comment=>:comments, mgmt_mth=>:mgmt_mth, category=>:category);
        END;""", {
            "name": module.params['name'],
            "comments": module.params['comments'],
            "mgmt_mth": module.params['mgmt_mth'],
            "category": module.params['category']
        })
        # Mappings
        for map_attr in new_mappings.keys():
            for map_value in new_mappings[map_attr]:
                c.execute("""
                BEGIN
                    DBMS_RESOURCE_MANAGER.SET_CONSUMER_GROUP_MAPPING(attribute=>:attr, value=>:val, consumer_group=>:group);
                END;""", {'attr': map_attr, 'val': map_value, 'group': module.params['name']})
        # Grants
        # Can't put under IF, since need to execute validate and submit commands anyway
        var_grants = c.arrayvar(cx_Oracle.STRING, list(new_grants))
        c.execute("""
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
                DBMS_RESOURCE_MANAGER_PRIVS.GRANT_SWITCH_CONSUMER_GROUP(grantee_name=>v_grants(i), consumer_group=>v_name, grant_option=>false);
            END LOOP;
        END;
        """, {
            "name": module.params['name'],
            "grants": var_grants
        })
        result_changed = True

    conn.commit()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
