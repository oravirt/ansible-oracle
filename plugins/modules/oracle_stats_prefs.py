#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = '''
---
module: oracle_stats_prefs
short_description: Manage DBMS_STATS global preferences
description:
    - Sets or resets global optimizer statistics preferences with
      C(DBMS_STATS.SET_GLOBAL_PREFS).
    - The current value is read with C(DBMS_STATS.GET_PREFS).
    - With O(state=present) the preference is only set (C(changed=true)) when the
      current value differs from O(preference_value). The comparison is case
      insensitive.
    - With O(state=absent) the preference is reset to its default by setting it to
      C(NULL). C(changed=true) is only reported when the value after the reset differs
      from the value before.
    - In check mode the module connects to the database and returns C(changed=false)
      without reading or changing the preference.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
    - Can be run locally on the control machine or on a remote host.
version_added: "2.4"
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
            - The user needs privileges to execute C(DBMS_STATS.SET_GLOBAL_PREFS),
              for example the DBA role.
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
    preference_name:
        description:
            - Name of the DBMS_STATS preference, for example V(TABLE_CACHED_BLOCKS)
              or V(STALE_PERCENT).
        type: str
        required: true
        aliases:
            - pname
    preference_value:
        description:
            - Value of the preference.
            - Required in practice with O(state=present), although not enforced by
              the argument spec. Without a value nothing is changed.
            - Ignored with O(state=absent).
        type: str
        required: false
        aliases:
            - pvalue
    state:
        description:
            - V(present) - the preference is set to O(preference_value).
            - V(absent) - the preference is reset to its default value.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Oracle RDBMS 10gR2 or later required
requirements: [ "python-oracledb" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Set global preference TABLE_CACHED_BLOCKS to 16
  opitzconsulting.ansible_oracle.oracle_stats_prefs:
    hostname: dbhost
    port: 1521
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    pname: TABLE_CACHED_BLOCKS
    pvalue: "16"
  environment:
    ORACLE_HOME: /usr/lib/oracle/12.1/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib

- name: Reset global preference STALE_PERCENT to default (Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_stats_prefs:
    service_name: orclpdb
    preference_name: STALE_PERCENT
    state: absent
'''

RETURN = '''
msg:
    description:
        - Result of the PL/SQL block, for example the old and the new value.
        - V(Not changed) when the preference already had the intended value.
    returned: when not running in check mode
    type: str
    sample: "Old value 1 changed to 16"
'''


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
            preference_name=dict(required=True, aliases=['pname']),
            preference_value=dict(aliases=['pvalue']),
            state=dict(default='present', choices=["present", "absent"]),
        ),
        supports_check_mode=True,
    )
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
    c = conn.cursor()
    var_changed = c.var(oracledb.NUMBER)
    var_msg = c.var(oracledb.STRING)
    c.execute(
        """
    DECLARE
        v_param_name VARCHAR2(100);
        v_param_value VARCHAR2(100);
        v_current_v VARCHAR2(100);
        v_state VARCHAR2(10);
        v_msg VARCHAR2(200):= 'Not changed';
        v_changed NUMBER:= 0;
    BEGIN
        v_param_name:= :pname;
        v_param_value:= :pvalue;
        v_state:= :state;
        v_current_v:= DBMS_STATS.GET_PREFS(v_param_name);
        IF v_state = 'present' AND upper(v_param_value) != upper(v_current_v) THEN
            DBMS_STATS.SET_GLOBAL_PREFS(v_param_name, v_param_value);
            v_changed:= 1;
            v_msg:= 'Old value '||v_current_v||' changed to '||v_param_value;
        ELSIF v_state = 'absent' THEN
            DBMS_STATS.SET_GLOBAL_PREFS(v_param_name, NULL);
            v_param_value:= DBMS_STATS.GET_PREFS(v_param_name);
            IF v_param_value != v_current_v THEN
                v_msg:= 'Value reset to default '||v_param_value;
                v_changed:= 1;
            END IF;
        END IF;
        :changed:= v_changed;
        :msg:= v_msg;
    END;
    """,
        {
            'pname': module.params['preference_name'],
            'pvalue': module.params['preference_value'],
            'state': module.params['state'],
            'changed': var_changed,
            'msg': var_msg,
        },
    )
    result_changed = var_changed.getvalue() > 0
    msg[0] = var_msg.getvalue()
    module.exit_json(msg=", ".join(msg), changed=result_changed)


if __name__ == '__main__':
    main()
