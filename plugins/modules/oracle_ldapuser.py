#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

try:
    import ldap
except ImportError:
    ldap_module_exists = False
else:
    ldap_module_exists = True


DOCUMENTATION = '''
---
module: oracle_ldapuser
short_description: Synchronise users from LDAP/Active Directory to an Oracle database
description:
    - Synchronises user accounts from LDAP/Active Directory to an Oracle database and
      maps LDAP group membership to Oracle roles.
    - Can be run locally on the control machine or on a remote host.
    - The users are searched below O(ldap_user_basedn) with O(ldap_user_filter).
      The value of O(ldap_username_attribute) is used as the Oracle user name.
    - All synchronised users are identified by O(user_profile). Missing users are
      created with O(user_default_tablespace), O(user_temp_tablespace),
      O(user_profile) and the quota O(user_quota_on_default_tbs_mb) on the default
      tablespace.
    - Existing users with differing tablespaces, profile, quota or authentication
      type, or with a locked account, are changed back with C(ALTER USER ...
      ACCOUNT UNLOCK).
    - Each synchronised user gets exactly the privileges and roles from
      O(user_grants) plus the roles mapped by O(group_role_map). All other system
      privileges and roles granted directly to the user are revoked.
    - Users with profile O(user_profile) that are no longer found in LDAP are
      locked or dropped, see O(deleted_user_mode).
    - The whole synchronisation runs in one PL/SQL block. The module reports
      changed=true if at least one DDL statement was executed.
    - If neither O(user) nor O(password) is given, a connection with an Oracle
      wallet (C(/@<service_name>)) is used. Otherwise both must be set.
    - In check mode the module only connects to LDAP and the database and returns
      changed=false. No changes are predicted.
version_added: "2.2.0"
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
    user_default_tablespace:
        description:
            - Default tablespace for synchronised users.
            - Must be an existing permanent tablespace. V(SYSTEM) and V(SYSAUX) are
              rejected.
        type: str
        required: false
        default: USERS
    user_quota_on_default_tbs_mb:
        description:
            - Quota in MB on O(user_default_tablespace).
            - Do not specify for unlimited quota.
        type: int
        required: false
    user_temp_tablespace:
        description:
            - Temporary tablespace for synchronised users.
            - Must be an existing temporary tablespace.
        type: str
        required: false
        default: TEMP
    user_profile:
        description:
            - Profile for synchronised users. The profile must exist.
            - Must be a dedicated profile for this synchronisation process, since this
              is the only way to detect which users should be locked or dropped.
              V(DEFAULT) is rejected.
        type: str
        required: false
        default: LDAP_USER
    user_default_password:
        description:
            - Password for newly created users. The password is expired immediately
              (C(PASSWORD EXPIRE)).
            - If not set, users are created and kept C(IDENTIFIED EXTERNALLY).
              Existing synchronised users with password authentication are then
              changed to C(IDENTIFIED EXTERNALLY).
            - The password of existing users is not changed.
        type: str
        required: false
    user_grants:
        description:
            - List of system privileges and roles all synchronised users get.
            - Privileges and roles not listed here or in O(group_role_map) are
              revoked from the users.
        type: list
        elements: str
        required: false
        default: ['create session']
    ldap_connect:
        description:
            - LDAP connect URI, e.g. V(ldap://domain.int:389).
        type: str
        required: true
    ldap_binddn:
        description:
            - LDAP bind user, e.g. V(reader@domain.int).
        type: str
        required: true
    ldap_bindpassword:
        description:
            - LDAP bind password.
        type: str
        required: true
    ldap_user_basedn:
        description:
            - LDAP base DN for the user search.
        type: str
        required: true
    ldap_user_subtree:
        description:
            - Whether the entire subtree below O(ldap_user_basedn) is searched for
              users (V(true)) or just one level (V(false)).
        type: bool
        required: false
        default: true
    ldap_user_filter:
        description:
            - LDAP filter to search for synchronised users.
        type: str
        required: false
        default: (objectClass=user)
    ldap_username_attribute:
        description:
            - LDAP attribute that is used as user name in Oracle.
            - The value is converted to uppercase. It must be at most 32 characters
              long, start with a letter, contain only letters, digits and
              underscores and must not end with an underscore.
        type: str
        required: false
        default: sAMAccountName
    deleted_user_mode:
        description:
            - What to do with users that have profile O(user_profile), are not
              locked and are not found in the LDAP search anymore.
            - V(lock) - the account is locked (C(ALTER USER ... ACCOUNT LOCK)).
            - V(drop) - the user is dropped (C(DROP USER ... CASCADE)).
        type: str
        required: false
        default: lock
        choices: ['lock', 'drop']
    group_role_map:
        description:
            - Maps LDAP group membership to Oracle roles.
            - Each list item is a dictionary with the keys C(dn) (the DN of the LDAP
              group) and C(group) (the name of the Oracle role).
            - A user gets the role if C(dn) is contained in the C(memberOf)
              attribute of the user. The role must exist in the database.
        type: list
        elements: dict
        required: false
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - ldap python module needs to be installed, but not from PIP!
      yum install python-ldap
    - The module fails if the LDAP search returns no users.
requirements: [ "python-oracledb", "ldap", "re" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Synchronise LDAP users into the database
  opitzconsulting.ansible_oracle.oracle_ldapuser:
    hostname: dbhost
    port: 1521
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    ldap_connect: ldap://domain.int:389
    ldap_binddn: reader@domain.int
    ldap_bindpassword: "{{ ldap_password }}"
    ldap_user_basedn: OU=Users,DC=domain,DC=int
    # objectClass is person, member of one specific group, not a computer
    # and the account is not disabled
    ldap_user_filter: "{{ ldap_filter_parts | join('') }}"
    ldap_username_attribute: sAMAccountName
    user_profile: LDAP_USER
    user_grants:
      - create session
      - create table
    group_role_map:
      - dn: CN=prod_db_reader,OU=Security Groups,DC=domain,DC=int
        group: prod_db_reader
      - dn: CN=prod_db_writer,OU=Security Groups,DC=domain,DC=int
        group: prod_db_writer
  vars:
    ldap_filter_parts:
      - "(&(objectClass=person)"
      - "(memberOf=CN=prod_db,OU=Security Groups,DC=domain,DC=int)"
      - "(!(userAccountControl:1.2.840.113556.1.4.803:=2))"
      - "(!(objectClass=COMPUTER)))"
  environment:
    ORACLE_HOME: /usr/lib/oracle/19/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/19/client64/lib

- name: Synchronise users with password authentication and drop removed users
  opitzconsulting.ansible_oracle.oracle_ldapuser:
    service_name: orcl
    ldap_connect: ldap://domain.int:389
    ldap_binddn: reader@domain.int
    ldap_bindpassword: "{{ ldap_password }}"
    ldap_user_basedn: OU=Users,DC=domain,DC=int
    user_default_password: "{{ initial_password }}"
    user_quota_on_default_tbs_mb: 200
    deleted_user_mode: drop
'''

RETURN = '''
msg:
    description:
        - One entry per synchronised user in the form C(<USERNAME> - <ROLES>),
          where C(<ROLES>) is the comma-separated list of roles from
          O(group_role_map).
        - Not returned in check mode.
    returned: success
    type: list
    elements: str
    sample: ["JDOE - PROD_DB_READER,PROD_DB_WRITER", "MMUSTER - "]
'''


# Helper code
oraclepattern = None


def clean_string(s):
    # This function should uppercase and clean all strings sent as identifiers to Oracle
    # raise exception if string cannot be cleaned
    global oraclepattern
    # Python 3 python-ldap may return LDAP attribute values as bytes,
    # decode before processing
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    supper = s.upper()
    if oraclepattern is None:
        oraclepattern = re.compile('^[A-Z]+[A-Z0-9_]*[A-Z0-9]+$')
    if (len(s) > 32) or not oraclepattern.match(supper):
        raise ValueError
    return supper


# Module code


def query_ldap_users():
    # What attributes to get from LDAP
    resultattrlist = [lparam['username']]
    if module.params['group_role_map'] is not None:
        resultattrlist.append('memberOf')
    #
    users = []
    try:
        result = lconn.search_s(
            lparam['basedn'],
            ldap.SCOPE_SUBTREE if lparam['subtree'] else ldap.SCOPE_ONELEVEL,
            lparam['filter'],
            resultattrlist,
        )
        results = [entry for dn, entry in result if isinstance(entry, dict)]
        for user in results:
            try:
                userinfo = {'username': clean_string(user[lparam['username']][0])}
                if module.params['group_role_map'] is not None:
                    # Python 3 python-ldap may return memberOf values as bytes,
                    # decode to str for comparisons
                    userinfo['memberOf'] = [
                        x.decode('utf-8') if isinstance(x, bytes) else x
                        for x in user['memberOf']
                    ]
                users.append(userinfo)
            except (
                ldap.LDAPError,
                ValueError,
                TypeError,
                KeyError,
                UnicodeDecodeError,
            ):
                pass
    except ldap.LDAPError as e:
        module.fail_json(msg="Error querying LDAP: %s" % e, changed=False)
    return users


# Ansible code
def main():
    global lconn, conn, lparam, module
    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521, type='int'),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            user_default_tablespace=dict(default='USERS'),
            user_quota_on_default_tbs_mb=dict(
                default=None, type='int'
            ),  # None is unlimited
            user_temp_tablespace=dict(default='TEMP'),
            user_profile=dict(default='LDAP_USER'),
            user_default_password=dict(
                default=None, no_log=True
            ),  # None means EXTERNAL
            user_grants=dict(default=['create session'], type='list'),
            ldap_connect=dict(required=True),
            ldap_binddn=dict(required=True),
            ldap_bindpassword=dict(required=True, no_log=True),
            ldap_user_basedn=dict(required=True),
            ldap_user_subtree=dict(default=True, type='bool'),
            ldap_user_filter=dict(default='(objectClass=user)'),
            ldap_username_attribute=dict(default='sAMAccountName'),
            deleted_user_mode=dict(default='lock', choices=['lock', 'drop']),
            group_role_map=dict(default=None, type='list'),
        ),
        supports_check_mode=True,
        # , mutually_exclusive=[['schema_password', 'schema_password_hash']]
    )
    # Check input variables
    if module.params['user_profile'].upper() == 'DEFAULT':
        module.fail_json(
            msg=(
                'Please use a dedicated profile for LDAP users, since this is the only '
                'method of detecting if user has been deleted from LDAP and should '
                'also be closed in database side.'
            )
        )
    if module.params['user_default_tablespace'].upper() in ['SYSTEM', 'SYSAUX']:
        module.fail_json(
            msg='no No NO! Choose a proper non-system tablespace for users.'
        )
    if not ldap_module_exists:
        module.fail_json(
            msg="The ldap module is required. 'pip install ldap' should do the trick."
        )
    # Connect to LDAP
    try:
        lconn = ldap.initialize(module.params['ldap_connect'])
        lconn.set_option(ldap.OPT_REFERRALS, 0)
        lconn.simple_bind_s(
            module.params['ldap_binddn'], module.params['ldap_bindpassword']
        )
    except ldap.LDAPError as e:
        module.fail_json(msg="LDAP connection error: %s" % e)
    lparam = {
        'basedn': module.params['ldap_user_basedn'],
        'subtree': module.params['ldap_user_subtree'],
        'filter': module.params['ldap_user_filter'],
        'username': module.params['ldap_username_attribute'],
    }
    # Connect to database
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
    #
    if module.check_mode:
        module.exit_json(changed=False)
    #
    users = query_ldap_users()
    lconn.unbind()
    # Prepare lists to send to Oracle
    usernames = []
    ldapgroups = []
    msgstr = []
    for user in users:
        usernames.append(user['username'])
        if module.params['group_role_map'] is not None and 'memberOf' in user:
            # Search matching DN from the user memberOf list
            mgroups = []
            for gr in module.params['group_role_map']:
                if gr['dn'] in user['memberOf']:
                    try:
                        mgroups.append("%s" % clean_string(gr['group']))
                    except (
                        ldap.LDAPError,
                        ValueError,
                        TypeError,
                        KeyError,
                        UnicodeDecodeError,
                    ):
                        pass
            g = ",".join(mgroups)
        else:
            g = ""
        ldapgroups.append(g)
        msgstr.append("%s - %s" % (user['username'], g))
    #
    if not len(usernames):
        module.fail_json(msg="No users found in LDAP", changed=False)
    #
    msg[0] = msgstr
    c = conn.cursor()
    var_usernames = c.arrayvar(oracledb.STRING, usernames)
    var_grants = c.arrayvar(
        oracledb.STRING, [x.upper() for x in module.params['user_grants']]
    )
    var_ldapgroups = c.arrayvar(oracledb.STRING, ldapgroups)
    var_changes = c.var(oracledb.NUMBER)
    c.execute(
        """
      DECLARE
          TYPE str_array IS TABLE OF VARCHAR2(50)
            INDEX BY BINARY_INTEGER;
          v_changes NUMBER:= 0;
          v_profile dba_users.profile%type;
          v_tbs dba_users.default_tablespace%type;
          v_tmp dba_users.temporary_tablespace%type;
          v_processed_users VARCHAR2(32267);
          v_default_password VARCHAR2(30);
          v_tbs_quota number;
          v_grants str_array;
          i NUMBER;

          PROCEDURE execsql(v_sql VARCHAR2) IS
          BEGIN
              EXECUTE IMMEDIATE v_sql;
              v_changes:= v_changes + 1;
          END;

          PROCEDURE check_grants(p_username dba_users.username%type,
                                 p_ldap_groups str_array) IS
              v_all_privs VARCHAR2(4000);
              v_needed_privs VARCHAR2(4000);
          BEGIN
              -- Check what needs to be added
              SELECT ','||listagg(priv,',') WITHIN GROUP (order by priv)||','
              INTO v_all_privs
              FROM (
                  SELECT privilege priv
                  FROM dba_sys_privs
                  WHERE grantee = p_username
                  UNION ALL
                  SELECT granted_role
                  FROM dba_role_privs
                  WHERE grantee = p_username
              );
              IF v_grants IS NOT NULL AND v_grants.COUNT > 0 THEN
                  FOR i IN v_grants.FIRST..v_grants.LAST LOOP
                      v_needed_privs:= v_needed_privs||','||v_grants(i);
                      IF v_all_privs NOT LIKE '%,'||v_grants(i)||',%' THEN
                          execsql('GRANT '||v_grants(i)||' TO '||p_username);
                      END IF;
                  END LOOP;
              END IF;
              IF p_ldap_groups IS NOT NULL AND p_ldap_groups.COUNT > 0 THEN
                  FOR i IN p_ldap_groups.FIRST..p_ldap_groups.LAST LOOP
                      v_needed_privs:= v_needed_privs||','||p_ldap_groups(i);
                      IF v_all_privs NOT LIKE '%,'||p_ldap_groups(i)||',%' THEN
                          execsql('GRANT '||p_ldap_groups(i)||' TO '||p_username);
                      END IF;
                  END LOOP;
              END IF;
              v_needed_privs:= v_needed_privs||',';
              -- Check what need to be revoked
              FOR rec IN (SELECT priv FROM (
                                SELECT privilege priv
                                FROM dba_sys_privs
                                WHERE grantee = p_username
                                UNION ALL
                                SELECT granted_role
                                FROM dba_role_privs
                                WHERE grantee = p_username)
                          WHERE v_needed_privs NOT LIKE '%,'||priv||',%') LOOP
                  execsql('REVOKE '||rec.priv||' FROM '||p_username);
              END LOOP;
          END;

          PROCEDURE add_user(p_username dba_users.username%type) IS
              v_sql VARCHAR2(200);
          BEGIN
              v_sql:= 'CREATE USER '|| p_username ||
                  ' IDENTIFIED ' ||
                        CASE WHEN v_default_password is null
                        THEN 'EXTERNALLY'
                        ELSE 'BY "' || v_default_password || '" PASSWORD EXPIRE'
                        END ||
                  ' PROFILE ' || v_profile ||
                  ' DEFAULT TABLESPACE ' || v_tbs ||
                  ' TEMPORARY TABLESPACE ' || v_tmp ||
                  ' QUOTA ' || CASE WHEN v_tbs_quota IS NULL
                               THEN 'unlimited'
                               ELSE v_tbs_quota || 'M'
                               END ||
                  ' ON '||v_tbs;
              execsql(v_sql);
          END;

          PROCEDURE remove_user(p_username dba_users.username%type) IS
          BEGIN
              IF :var_deleted_user_mode = 'drop' THEN
                  execsql('DROP USER '||p_username||' CASCADE');
              ELSIF :var_deleted_user_mode = 'lock' THEN
                  execsql('ALTER USER '||p_username||' ACCOUNT LOCK');
              END IF;
          END;

          PROCEDURE alter_user(p_username dba_users.username%type) IS
          BEGIN
              execsql('ALTER USER ' || p_username ||
                      ' ' || case when v_default_password is null
                             then 'IDENTIFIED EXTERNALLY'
                             end ||
                  ' PROFILE ' || v_profile ||
                  ' DEFAULT TABLESPACE ' || v_tbs ||
                  ' TEMPORARY TABLESPACE ' || v_tmp ||
                  ' ACCOUNT UNLOCK'||
                  ' QUOTA ' ||
                    CASE WHEN v_tbs_quota IS NULL
                    THEN 'unlimited'
                    ELSE v_tbs_quota || 'M'
                    END ||
                  ' ON '||v_tbs);
          END;

          PROCEDURE process_user(p_username dba_users.username%type,
                                 p_ldap_groups varchar2) IS
              v_as dba_users.account_status%type;
              v_at dba_users.authentication_type%type;
              v_dt dba_users.default_tablespace%type;
              v_temp dba_users.temporary_tablespace%type;
              v_p dba_users.profile%type;
              v_qmb dba_ts_quotas.max_bytes%type;
              v_ldap_groups str_array;
              l_comma_index PLS_INTEGER;
              l_index PLS_INTEGER:= 1;
              v_tmpstr VARCHAR2(4000);
              v_s varchar2(50);
          BEGIN
              v_processed_users:= v_processed_users||','||p_username;
              -- Process LDAP groups
              v_tmpstr:= p_ldap_groups||',';
              LOOP
                  l_comma_index:= INSTR(v_tmpstr, ',', l_index);
                  EXIT WHEN l_comma_index = 0;
                  v_s:= SUBSTR(v_tmpstr, l_index, l_comma_index - l_index);
                  IF v_s IS NOT NULL THEN
                      v_ldap_groups(v_ldap_groups.COUNT+1):= v_s;
                  END IF;
                  l_index:= l_comma_index + 1;
              END LOOP;
              --
              SELECT u.account_status,
                     u.authentication_type,
                     u.default_tablespace,
                     u.temporary_tablespace,
                     u.profile,
                     CASE WHEN q.max_bytes > 0
                     THEN q.max_bytes/1024/1024
                     ELSE q.max_bytes
                     END
                  INTO v_as, v_at, v_dt, v_temp, v_p, v_qmb
              FROM dba_users u
              LEFT OUTER JOIN dba_ts_quotas q
                 ON q.username = u.username
                 AND q.dropped = 'NO'
                 AND q.tablespace_name = v_tbs
              WHERE u.username = p_username;
              -- In any change in data is detected, correct it back
              IF v_dt != v_tbs
                 OR v_temp != v_tmp
                 OR v_p != v_profile
                 OR v_as LIKE '%LOCKED%'
                 OR (v_default_password IS NULL
                     AND v_at = 'PASSWORD')
                 OR NVL(v_tbs_quota, -1) != NVL(v_qmb, -100) THEN
                  alter_user(p_username);
              END IF;
              check_grants(p_username, v_ldap_groups);
          EXCEPTION
              WHEN no_data_found THEN
                  add_user(p_username);
                  check_grants(p_username, v_ldap_groups);
          END;

          PROCEDURE process_array(
            p_usernames IN str_array,
            p_ldap_groups IN str_array) IS
          BEGIN
              FOR i IN p_usernames.FIRST..p_usernames.LAST LOOP
                  process_user(p_usernames(i), p_ldap_groups(i));
              END LOOP;
          END;

      BEGIN
          -- Validate parameters, if any tablespace does not exist, the select
          -- will excpetion with no_data_found
          v_tbs:= :var_tbs;
          v_tmp:= :var_temp;
          v_profile:= :var_profile;
          BEGIN
              SELECT 1
              INTO i
              FROM dba_tablespaces
              WHERE tablespace_name = v_tbs
              AND contents = 'PERMANENT';

              SELECT 1
              INTO i
              FROM dba_tablespaces
              WHERE tablespace_name = v_tmp
              AND contents = 'TEMPORARY';
          EXCEPTION
              WHEN no_data_found THEN
                  raise_application_error(
                    -20100, 'Permanent or temporary tablespace not found.'
                  );
          END;
          BEGIN
              SELECT 1
              INTO i
              FROM dba_profiles
              WHERE profile = v_profile
              AND rownum <= 1;
          EXCEPTION
              WHEN no_data_found THEN
                  raise_application_error(-20101, 'Profile not found.');
          END;
          v_default_password:= :var_default_password;
          v_grants:= :var_grants;
          v_tbs_quota:= :var_user_quota;
          -- Process userlist
          process_array(:var_usernames, :var_ldapgroups);
          -- Check users who are not listed
          v_processed_users:= v_processed_users||',';
          FOR rec IN (SELECT username
                        FROM dba_users
                       WHERE profile = v_profile
                         AND (account_status = 'OPEN'
                              OR account_status NOT LIKE '%LOCKED%')
                    ) LOOP
            -- separate check in PL/SQL since v_processed_users
            -- can be over 4000 bytes long
              IF v_processed_users NOT LIKE '%,'||rec.username||',%' THEN
                remove_user(rec.username);
              END IF;
          END LOOP;
          -- Return
          :var_changes:= v_changes;
      END;
    """,
        {
            'var_usernames': var_usernames,
            'var_changes': var_changes,
            'var_tbs': clean_string(module.params['user_default_tablespace']),
            'var_temp': clean_string(module.params['user_temp_tablespace']),
            'var_profile': clean_string(module.params['user_profile']),
            'var_deleted_user_mode': module.params['deleted_user_mode'],
            'var_default_password': module.params['user_default_password'],
            'var_user_quota': module.params['user_quota_on_default_tbs_mb'],
            'var_grants': var_grants,
            'var_ldapgroups': var_ldapgroups,
        },
    )
    conn.commit()
    #
    module.exit_json(msg=msg[0], changed=var_changes.getvalue() > 0)


if __name__ == '__main__':
    main()
