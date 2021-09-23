#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
module: oracle_ldapuser
short_description: Syncronises user accounts from LDAP/Active directory to Oracle database and maps group membership to Oracle roles
description:
    - Syncronises user accounts from LDAP/Active directory to Oracle database and maps group membership to Oracle roles
    - Can be run locally on the controlmachine or on a remote host
version_added: "2.2.0"
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
        required: false
    password:
        description:
            - The Oracle user password for 'user'
        required: false
    mode:
        description:
            - The mode with which to connect to the database
        required: true
        default: normal
        choices: ['normal','sysdba']
    user_default_tablespace:
        description:
            - Default tablespace for syncronised users
        required: false
        default: USERS
    user_quota_on_default_tbs_mb:
        description:
            - Quota in MB for the default tablespace
            - Do not specify for unlimited quota
        required: false
    user_temp_tablespace:
        description:
            - Temporary tablespace for syncronised user
        required: false
        default: TEMP
    user_profile:
        description:
            - Profile for syncronised user
            - Must be dedicated profile for this syncronization process, since this is the only way to detect which users should be locked/dropped
        required: false
        default: LDAP_USER
    user_default_password:
        description:
            - Default password for newly created user
            - Password is expired immediately
            - Do not specify for EXTERNAL authentication_type
        required: false
    user_grants:
        description:
            - List of all grants all syncronised users will get
        required: false
        type: list
        default: create session
    ldap_connect:
        description:
            - LDAP connect string eg ldap://domain.int:389
        required: true
    ldap_binddn:
        description:
            - LDAP login username eg reader@domain.int
        required: true
    ldap_bindpassword:
        description:
            - LDAP login password
        required: true
    ldap_user_basedn:
        description:
            - LDAP BASE DN for syncronised users
        required: true
    ldap_user_subtree:
        description:
            - Is the entire subtree searched for users (true) or just one level (false)
        required: false
        default: true
    ldap_user_filter:
        description:
            - LDAP filter to search for syncronised users
        required: false
        default: (objectClass=user)
    ldap_username_attribute:
        description:
            - LDAP attribute that is used for user name in Oracle
            - If value does not "Oracle identifier" compatible, then this user is silently skipped
        required: false
        default: sAMAccountName
    deleted_user_mode:
        description:
            - What action to take then user is not found in LDAP search anymore
        required: false
        default: lock
        choices: ['lock','drop']
    group_role_map:
        description:
            - Each user can be granted additional roles based on LDAP group membership, this parameter describes the relationship between group LDAP DN and Oracle group name
            - Each list item must be DICT with elements dn and groups
            - Example list item: {dn: "CN=prod_db_reader,OU=Security Groups,DC=domain,DC=int", group: "prod_db_reader"}
        required: false
        type: list of dicts
notes:
    - cx_Oracle needs to be installed
    - ldap python module needs to be installed, but not from PIP! yum install python-ldap!
requirements: [ "cx_Oracle", "ldap", "re" ]
author: Ilmar Kerm, ilmar.kerm@gmail.com, @ilmarkerm
'''

EXAMPLES = '''
- hosts: localhost
  vars:
    oracle_env:
      ORACLE_HOME: /usr/lib/oracle/12.1/client64
      LD_LIBRARY_PATH: /usr/lib/oracle/12.1/client64/lib
  tasks:
    - name: oracle_ldapuser
      oracle_ldapuser:
        hostname: testldap
        port: 1521
        service_name: orcl
        user: system
        password: Oracle123
        ldap_connect: ldap://domain.int:389
        ldap_binddn: reader@domain.int
        ldap_bindpassword: HelloWorld123
        ldap_user_basedn: OU=Users,DC=domain,DC=int
        #user_default_password: Oracle123
        # The following filter means that objectClass is person, member of one specific group, but not COMPUTER and account is not disabled
        ldap_user_filter: (&(objectClass=person)(memberOf=CN=prod_db,OU=Security Groups,DC=domain,DC=int)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(!(objectClass=COMPUTER)))
        #ldap_user_filter: (sAMAccountName=*prod*)
        ldap_username_attribute: sAMAccountName
        user_profile: LDAP_USER
        #user_quota_on_default_tbs_mb: 200
        user_grants:
          - create session
          - create table
        group_role_map:
          - {dn: "CN=prod_db_reader,OU=Security Groups,DC=domain,DC=int", group: "prod_db_reader"}
          - {dn: "CN=prod_db_writer,OU=Security Groups,DC=domain,DC=int", group: "prod_db_writer"}
      environment: "{{ oracle_env }}"
'''

import re

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

try:
    import ldap
except ImportError:
    ldap_module_exists = False
else:
    ldap_module_exists = True

# Helper code
oraclepattern = None

def clean_string(s):
    # This function should uppercase and clean all strings sent as identifiers to Oracle
    # raise exception if string cannot be cleaned
    global oraclepattern
    supper = s.upper()
    if oraclepattern is None:
        oraclepattern = re.compile('^[A-Z]+[A-Z0-9_]*[A-Z0-9]+$')
    if (len(s) > 32) or not oraclepattern.match(supper):
        raise
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
        result = lconn.search_s(lparam['basedn'], ldap.SCOPE_SUBTREE if lparam['subtree'] else ldap.SCOPE_ONELEVEL, lparam['filter'], resultattrlist)
        results = [entry for dn, entry in result if isinstance(entry, dict)]
        for user in results:
            try:
                userinfo = { 'username': clean_string(user[lparam['username']][0]) }
                if module.params['group_role_map'] is not None:
                    userinfo['memberOf'] = user['memberOf']
                users.append(userinfo)
            except:
                pass
    except ldap.LDAPError as e:
        module.fail_json(msg="Error querying LDAP: %s" % e, changed=False)
    return users

# Ansible code
def main():
    global lconn, conn, lparam, module
    msg = ['']
    module = AnsibleModule(
        argument_spec = dict(
            hostname      = dict(default='localhost'),
            port          = dict(default=1521, type='int'),
            service_name  = dict(required=True),
            user          = dict(required=False),
            password      = dict(required=False),
            mode          = dict(default='normal', choices=["normal","sysdba"]),
            user_default_tablespace = dict(default='USERS'),
            user_quota_on_default_tbs_mb = dict(default=None, type='int'), # None is unlimited
            user_temp_tablespace = dict(default='TEMP'),
            user_profile  = dict(default='LDAP_USER'),
            user_default_password = dict(default=None), # None means EXTERNAL
            user_grants   = dict(default=['create session'], type='list'),
            ldap_connect  = dict(required=True),
            ldap_binddn   = dict(required=True),
            ldap_bindpassword = dict(required=True),
            ldap_user_basedn  = dict(required=True),
            ldap_user_subtree = dict(default=True, type='bool'),
            ldap_user_filter  = dict(default='(objectClass=user)'),
            ldap_username_attribute = dict(default='sAMAccountName'),
            deleted_user_mode = dict(default='lock', choices=['lock','drop']),
            group_role_map    = dict(default=None, type='list')
        ),
        supports_check_mode=True
        #, mutually_exclusive=[['schema_password', 'schema_password_hash']]
    )
    # Check input variables
    if module.params['user_profile'].upper() == 'DEFAULT':
        module.fail_json(msg='Please use a dedicated profile for LDAP users, since this is the only method of detecting if user has been deleted from LDAP and should also be closed in database side.')
    if module.params['user_default_tablespace'].upper() in ['SYSTEM','SYSAUX']:
        module.fail_json(msg='no No NO! Choose a proper non-system tablespace for users.')
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    if not ldap_module_exists:
        module.fail_json(msg="The ldap module is required. 'pip install ldap' should do the trick.")
    # Connect to LDAP
    try:
        lconn = ldap.initialize(module.params['ldap_connect'])
        lconn.set_option(ldap.OPT_REFERRALS, 0)
        lconn.simple_bind_s(module.params['ldap_binddn'], module.params['ldap_bindpassword'])
    except ldap.LDAPError as e:
        module.fail_json(msg="LDAP connection error: %s" % e)
    lparam = {
        'basedn': module.params['ldap_user_basedn'],
        'subtree': module.params['ldap_user_subtree'],
        'filter': module.params['ldap_user_filter'],
        'username': module.params['ldap_username_attribute']
    }
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
                    except:
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
    var_usernames = c.arrayvar(cx_Oracle.STRING, usernames)
    var_grants = c.arrayvar(cx_Oracle.STRING, [x.upper() for x in module.params['user_grants']])
    var_ldapgroups = c.arrayvar(cx_Oracle.STRING, ldapgroups)
    var_changes = c.var(cx_Oracle.NUMBER)
    c.execute("""
      DECLARE
          TYPE str_array IS TABLE OF VARCHAR2(50) INDEX BY BINARY_INTEGER;
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

          PROCEDURE check_grants(p_username dba_users.username%type, p_ldap_groups str_array) IS
              v_all_privs VARCHAR2(4000);
              v_needed_privs VARCHAR2(4000);
          BEGIN
              -- Check what needs to be added
              SELECT ','||listagg(priv,',') WITHIN GROUP (order by priv)||',' INTO v_all_privs FROM (
                  SELECT privilege priv FROM dba_sys_privs WHERE grantee = p_username
                  UNION ALL
                  SELECT granted_role FROM dba_role_privs WHERE grantee = p_username
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
                                SELECT privilege priv FROM dba_sys_privs WHERE grantee = p_username
                                UNION ALL
                                SELECT granted_role FROM dba_role_privs WHERE grantee = p_username)
                          WHERE v_needed_privs NOT LIKE '%,'||priv||',%') LOOP
                  execsql('REVOKE '||rec.priv||' FROM '||p_username);
              END LOOP;
          END;

          PROCEDURE add_user(p_username dba_users.username%type) IS
              v_sql VARCHAR2(200);
          BEGIN
              v_sql:= 'CREATE USER '||p_username||
                  ' IDENTIFIED '||case when v_default_password is null then 'EXTERNALLY' ELSE 'BY "'||v_default_password||'" PASSWORD EXPIRE' end||
                  ' PROFILE '||v_profile||' DEFAULT TABLESPACE '||v_tbs||' TEMPORARY TABLESPACE '||v_tmp||
                  ' QUOTA '||CASE WHEN v_tbs_quota IS NULL THEN 'unlimited' ELSE v_tbs_quota||'M' END||' ON '||v_tbs;
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
              execsql('ALTER USER '||p_username||' '||case when v_default_password is null then 'IDENTIFIED EXTERNALLY' end||
                  ' PROFILE '||v_profile||' DEFAULT TABLESPACE '||v_tbs||' TEMPORARY TABLESPACE '||v_tmp||' ACCOUNT UNLOCK'||
                  ' QUOTA '||CASE WHEN v_tbs_quota IS NULL THEN 'unlimited' ELSE v_tbs_quota||'M' END||' ON '||v_tbs);
          END;

          PROCEDURE process_user(p_username dba_users.username%type, p_ldap_groups varchar2) IS
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
              SELECT u.account_status, u.authentication_type, u.default_tablespace, u.temporary_tablespace, u.profile,
                  CASE WHEN q.max_bytes > 0 THEN q.max_bytes/1024/1024 ELSE q.max_bytes END
                  INTO v_as, v_at, v_dt, v_temp, v_p, v_qmb
              FROM dba_users u LEFT OUTER JOIN dba_ts_quotas q ON q.username = u.username AND q.dropped = 'NO' AND q.tablespace_name = v_tbs
              WHERE u.username = p_username;
              -- In any change in data is detected, correct it back
              IF v_dt != v_tbs OR v_temp != v_tmp OR v_p != v_profile OR v_as LIKE '%LOCKED%' OR (v_default_password IS NULL AND v_at = 'PASSWORD') OR
                  (NVL(v_tbs_quota, -1) != NVL(v_qmb, -100)) THEN
                  alter_user(p_username);
              END IF;
              check_grants(p_username, v_ldap_groups);
          EXCEPTION
              WHEN no_data_found THEN
                  add_user(p_username);
                  check_grants(p_username, v_ldap_groups);
          END;

          PROCEDURE process_array(p_usernames IN str_array, p_ldap_groups IN str_array) IS
          BEGIN
              FOR i IN p_usernames.FIRST..p_usernames.LAST LOOP
                  process_user(p_usernames(i), p_ldap_groups(i));
              END LOOP;
          END;

      BEGIN
          -- Validate parameters, if any tablespace does not exist, the select will excpetion with no_data_found
          v_tbs:= :var_tbs;
          v_tmp:= :var_temp;
          v_profile:= :var_profile;
          BEGIN
              SELECT 1 INTO i FROM dba_tablespaces WHERE tablespace_name = v_tbs and contents = 'PERMANENT';
              SELECT 1 INTO i FROM dba_tablespaces WHERE tablespace_name = v_tmp and contents = 'TEMPORARY';
          EXCEPTION
              WHEN no_data_found THEN
                  raise_application_error(-20100, 'Permanent or temporary tablespace not found.');
          END;
          BEGIN
              SELECT 1 INTO i FROM dba_profiles WHERE profile = v_profile AND rownum <= 1;
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
          FOR rec IN (SELECT username FROM dba_users WHERE profile = v_profile AND (account_status = 'OPEN' OR account_status NOT LIKE '%LOCKED%') ) LOOP
            -- separate check in PL/SQL since v_processed_users can be over 4000 bytes long
              IF v_processed_users NOT LIKE '%,'||rec.username||',%' THEN
                remove_user(rec.username);
              END IF;
          END LOOP;
          -- Return
          :var_changes:= v_changes;
      END;
    """, {
        'var_usernames': var_usernames, 'var_changes': var_changes,
        'var_tbs': clean_string(module.params['user_default_tablespace']),
        'var_temp': clean_string(module.params['user_temp_tablespace']),
        'var_profile': clean_string(module.params['user_profile']),
        'var_deleted_user_mode': module.params['deleted_user_mode'],
        'var_default_password': module.params['user_default_password'],
        'var_user_quota': module.params['user_quota_on_default_tbs_mb'],
        'var_grants': var_grants,
        'var_ldapgroups': var_ldapgroups
    })
    conn.commit()
    #
    module.exit_json(msg=msg[0], changed=var_changes.getvalue()>0)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
