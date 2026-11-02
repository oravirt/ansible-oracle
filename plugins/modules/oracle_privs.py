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
module: oracle_privs
short_description: Manage object and system privileges in an Oracle database
description:
    - Grants and revokes system privileges, roles and object privileges to and from
      users and roles in an Oracle database.
    - Everything is done in one PL/SQL block. Privileges of the same grantee (and
      object) are combined in one C(GRANT) or C(REVOKE) statement.
    - Without O(objs), O(privs) are system privileges or roles. They are compared
      with C(DBA_SYS_PRIVS) and C(DBA_ROLE_PRIVS).
    - With O(objs), O(privs) are object privileges. The objects are resolved in
      C(DBA_OBJECTS) at runtime, filtered by O(objtypes), and compared with
      C(DBA_TAB_PRIVS). Objects created later are not covered.
    - Only privileges that are missing are granted (O(state=present)) and only
      privileges that are granted directly are revoked (O(state=absent)), so
      C(changed=true) is only returned if a statement was executed.
    - Grantees in O(roles) that do not exist, or that are Oracle maintained
      (C(ORACLE_MAINTAINED=Y), 12c and later), are silently ignored. C(SYS) and
      C(SYSTEM) are rejected.
    - In check mode the module only connects to the database and returns
      C(changed=false) without checking the privileges.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
    - Can be run locally on the control machine or on a remote host.
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
            - The user needs the privileges to read the C(DBA_*) views and to grant
              and revoke the privileges, for example C(DBA).
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
            - V(present) - missing privileges are granted.
            - V(absent) - granted privileges are revoked.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
    privs:
        description:
            - Privileges to grant or revoke. Always converted to uppercase.
            - Without O(objs), system privileges or roles, for example
              V(CREATE SESSION) or V(SELECT_CATALOG_ROLE).
            - With O(objs), object privileges, for example V(SELECT) or V(UPDATE).
              Use single privileges as listed in C(DBA_TAB_PRIVS); V(ALL) is not
              idempotent.
        type: list
        elements: str
        required: true
        aliases: ['priv']
    objs:
        description:
            - When setting object privileges, list the objects the privileges are
              set for.
            - Use the format C(SCHEMA_NAME.OBJECT_NAME). The wildcard C(%) can be
              used in the object name part, for example V(HR.%) to set privileges
              for all objects (of the types in O(objtypes)) in schema C(HR).
              C(_) is matched literally.
            - Object names are case-sensitive, see O(convert_to_upper).
        type: list
        elements: str
        required: false
        aliases: ['obj']
    objtypes:
        description:
            - When using object privileges, the object types (C(OBJECT_TYPE) column
              of C(DBA_OBJECTS)) of the objects in O(objs).
            - Always converted to uppercase.
        type: list
        elements: str
        required: false
        default: ['TABLE', 'VIEW']
    roles:
        description:
            - List of user names and role names (grantees) to grant the privileges
              to or revoke them from.
            - Names are case-sensitive, see O(convert_to_upper).
        type: list
        elements: str
        required: true
        aliases: ['role']
    convert_to_upper:
        description:
            - Converts all entries of O(roles) and O(objs) to uppercase to simulate
              case insensitivity.
        type: bool
        required: false
        default: true
    quiet:
        description:
            - If set to V(false), all executed statements are returned in RV(msg).
        type: bool
        required: false
        default: true
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Oracle RDBMS 11gR2 or later required
requirements: [ "python-oracledb", "re" ]
author:
    - Ilmar Kerm (@ilmarkerm)
'''

EXAMPLES = '''
- name: Grant system privileges
  opitzconsulting.ansible_oracle.oracle_privs:
    hostname: dbhost
    port: 1521
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    state: present
    privs:
      - CREATE TABLE
      - CREATE VIEW
      - CREATE TYPE
      - CREATE PROCEDURE
      - CREATE SESSION
    roles:
      - ILMAR
      - HR
      - READER_ROLE
  environment:
    ORACLE_HOME: /usr/lib/oracle/19/client64
    LD_LIBRARY_PATH: /usr/lib/oracle/19/client64/lib

- name: Revoke system privileges
  opitzconsulting.ansible_oracle.oracle_privs:
    hostname: dbhost
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    state: absent
    privs:
      - CREATE ANY TABLE
      - SELECT ANY TABLE
    roles:
      - ILMAR
      - READER_ROLE

- name: Grant object privileges on all tables and views of HR and FINANCE
  opitzconsulting.ansible_oracle.oracle_privs:
    hostname: dbhost
    service_name: orclpdb
    user: system
    password: "{{ system_password }}"
    state: present
    privs:
      - SELECT
      - FLASHBACK
    objs:
      - HR.%
      - FINANCE.%
    roles:
      - ILMAR
      - READER_ROLE

- name: Revoke object privileges on tables of HR (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_privs:
    service_name: orclpdb
    state: absent
    privs:
      - INSERT
      - UPDATE
      - DELETE
    objs:
      - HR.%
    objtypes:
      - TABLE
    roles:
      - READER_ROLE
    quiet: false
'''

RETURN = '''
msg:
    description:
        - The executed statements, each prefixed with C(-), if O(quiet=false).
        - V(null) if O(quiet=true) or if no statement was executed.
    returned: success, not in check mode
    type: str
    sample: >-
        -GRANT CREATE SESSION,CREATE TABLE TO "ILMAR"-GRANT CREATE SESSION
        TO "READER_ROLE"
'''


# Ansible code
def main():
    global conn, module
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521, type='int'),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            state=dict(default="present", choices=["present", "absent"]),
            privs=dict(required=True, type='list', aliases=['priv']),
            objs=dict(
                required=False, type='list', aliases=['obj']
            ),  # CASE SENSITIVE! Can use wildcard %
            objtypes=dict(required=False, default=['TABLE', 'VIEW'], type='list'),
            roles=dict(required=True, type='list', aliases=['role']),
            convert_to_upper=dict(default=True, type='bool'),
            quiet=dict(required=False, default=True, type='bool'),
        ),
        supports_check_mode=True,
    )
    # Check input parameters
    re_priv = re.compile('^[A-Za-z0-9_]+[A-Za-z0-9_ ]*[A-Za-z0-9_]+$')
    re_role = re.compile('^[A-Za-z0-9_\$#\- ]+$')  # noqa W605
    re_obj = re.compile('^[A-Za-z0-9_\$#\- ]*\.[A-Za-z0-9_\$#\%\- ]+$')  # noqa W605
    for p in module.params['privs']:
        if not re_priv.match(p):
            module.fail_json(msg="Invalid privilege '%s'" % p)
    for p in module.params['roles']:
        if not re_role.match(p) or p.upper() in ['SYS', 'SYSTEM']:
            module.fail_json(msg="Invalid user/role '%s'" % p)
    if module.params['objs'] is not None:
        for p in module.params['objs']:
            if not re_obj.match(p):
                module.fail_json(msg="Invalid object '%s'" % p)
    for p in module.params['objtypes']:
        if not re_priv.match(p):
            module.fail_json(msg="Invalid object type '%s'" % p)
    objtypes = ",%s," % ",".join(module.params['objtypes'])
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
    c = conn.cursor()
    var_changes = c.var(oracledb.NUMBER)
    var_error = c.var(oracledb.NUMBER)
    var_errstr = c.var(oracledb.STRING)
    var_privs = c.arrayvar(oracledb.STRING, [p.upper() for p in module.params['privs']])
    objectslist = (
        [p.replace("_", "\_") for p in module.params['objs']]  # noqa W605
        if module.params['objs'] is not None
        else []
    )
    var_objs = c.arrayvar(
        oracledb.STRING,
        objectslist
        if not module.params['convert_to_upper']
        else [p.upper() for p in objectslist],
        100,
    )
    var_roles = c.arrayvar(
        oracledb.STRING,
        module.params['roles']
        if not module.params['convert_to_upper']
        else [p.upper() for p in module.params['roles']],
        50,
    )
    #
    rs_subquery = (
        "SELECT username role "
        "FROM dba_users $IF DBMS_DB_VERSION.VERSION >= 12 $THEN "
        "WHERE oracle_maintained='N' $END "
        "UNION ALL "
        "SELECT role "
        "FROM dba_roles $IF DBMS_DB_VERSION.VERSION >= 12 $THEN "
        "WHERE oracle_maintained='N' $END "
        "INTERSECT "
        "SELECT column_value name "
        "FROM table(v_roles_sql)"
    )
    objs_subquery = (
        "SELECT DISTINCT o.owner, o.object_name "
        "FROM dba_objects o "
        "JOIN table(v_objs_sql) s "
        "  ON o.owner||'.'||o.object_name LIKE s.column_value ESCAPE '\\' "
        "AND v_objtype LIKE '%,'||o.object_type||',%'"
    )
    rp_subquery = (
        "SELECT rs.role, p.column_value priv "
        "FROM rs "
        "CROSS JOIN table(v_privs_sql) p"
    )
    #
    plsql_block = """
    DECLARE
        TYPE str_array IS TABLE OF VARCHAR2(50) INDEX BY BINARY_INTEGER;
        -- output
        v_changes NUMBER:= 0;
        v_error NUMBER:= 0;
        v_errstr VARCHAR2(32267);
        -- input
        v_state VARCHAR2(10);
        v_objects str_array;
        v_objtype VARCHAR2(4000);
        v_privs str_array;
        v_roles str_array;
        v_report_error NUMBER:= 1;
        v_quiet NUMBER;
        v_privs_sql sys.DBMS_DEBUG_VC2COLL:= sys.DBMS_DEBUG_VC2COLL();
        v_roles_sql sys.DBMS_DEBUG_VC2COLL:= sys.DBMS_DEBUG_VC2COLL();
        v_objs_sql sys.DBMS_DEBUG_VC2COLL:= sys.DBMS_DEBUG_VC2COLL();

        PROCEDURE execsql(p_sql VARCHAR2) IS
        BEGIN
            EXECUTE IMMEDIATE p_sql;
            v_changes:= v_changes+1;
            IF v_quiet = 0 THEN
                v_errstr:= v_errstr||'-'||p_sql;
            END IF;
        EXCEPTION
            WHEN others THEN
                v_error:= v_report_error;
                v_errstr:= v_errstr||'-"'||p_sql||'"-'||sqlerrm;
                raise;
        END;

    BEGIN
        -- assign input
        v_state:= :var_state;
        v_objects:= :var_objs;
        v_objtype:= :var_objtype;
        v_privs:= :var_privs;
        v_roles:= :var_roles;
        v_quiet:= :var_quiet;
        -- Copy to a new array that can be used in SQL
        FOR i IN v_privs.FIRST..v_privs.LAST LOOP
            v_privs_sql.extend();
            v_privs_sql(v_privs_sql.count):= v_privs(i);
        END LOOP;
        v_privs.delete;
        FOR i IN v_roles.FIRST..v_roles.LAST LOOP
            v_roles_sql.extend();
            v_roles_sql(v_roles_sql.count):= v_roles(i);
        END LOOP;
        v_roles.delete;
        IF v_objects.COUNT > 0 THEN
            FOR i IN v_objects.FIRST..v_objects.LAST LOOP
                v_objs_sql.extend();
                v_objs_sql(v_objs_sql.count):= v_objects(i);
            END LOOP;
            v_objects.delete;
        END IF;
        --
        BEGIN
            IF v_objs_sql.COUNT > 0 THEN
                -- Object privileges
                IF v_state = 'present' THEN
                    FOR rec IN (
                        WITH objs AS (%s),
                             rs AS (%s),
                             rp AS (%s),
                             objpr AS (SELECT o.owner, o.object_name, rp.priv, rp.role
                                       FROM objs o
                                       CROSS JOIN rp)
                        SELECT owner, object_name, role,
                               LISTAGG(priv,',') WITHIN GROUP (ORDER BY priv) privs
                        FROM (
                            SELECT owner, object_name, priv, role FROM objpr
                            MINUS
                            SELECT owner, table_name, privilege, grantee
                            FROM dba_tab_privs)
                        GROUP BY owner, object_name, role
                    ) LOOP
                        execsql('GRANT ' || rec.privs || ' ON "' ||rec.owner
                            || '"."' || rec.object_name || '" TO "' || rec.role || '"');
                    END LOOP;
                ELSIF v_state = 'absent' THEN
                    FOR rec IN (
                        WITH objs AS (%s),
                             rs AS (%s),
                             rp AS (%s),
                             objpr AS (
                                SELECT o.owner, o.object_name, rp.priv, rp.role
                                FROM objs o CROSS JOIN rp)
                        SELECT t.owner, t.table_name, t.grantee,
                               LISTAGG(t.privilege,',') WITHIN GROUP
                                (ORDER BY t.privilege) privs
                        FROM dba_tab_privs t
                        JOIN objpr o ON t.owner=o.owner
                            AND t.table_name=o.object_name
                            AND t.privilege=o.priv
                            AND t.grantee=o.role
                        GROUP BY t.owner, t.table_name, t.grantee
                    ) LOOP
                        execsql('REVOKE ' || rec.privs || ' ON "' || rec.owner || '"."'
                        || rec.table_name || '" FROM "' || rec.grantee || '"');
                    END LOOP;
                END IF;
            ELSE
                -- System/role grants
                IF v_state = 'present' THEN
                    FOR rec IN (
                        WITH rs AS (%s),
                             rp AS (%s)
                        SELECT role, LISTAGG(priv, ',')
                                WITHIN GROUP (ORDER BY priv) privs
                        FROM (
                            SELECT rp.role, rp.priv FROM rp
                            MINUS
                            SELECT grantee, privilege FROM dba_sys_privs
                            MINUS
                            SELECT grantee, granted_role FROM dba_role_privs)
                        GROUP BY role
                    ) LOOP
                        execsql('GRANT '||rec.privs||' TO "'||rec.role||'"');
                    END LOOP;
                ELSIF v_state = 'absent' THEN
                    FOR rec IN (
                        WITH rs AS (%s),
                             rp AS (%s)
                        SELECT s.role, LISTAGG(s.priv, ',')
                                WITHIN GROUP (ORDER BY s.priv) privs
                        FROM
                            (SELECT grantee role, privilege priv FROM dba_sys_privs
                             UNION ALL
                             SELECT grantee, granted_role
                             FROM dba_role_privs) s
                             JOIN rp ON rp.role = s.role
                                AND rp.priv = s.priv
                        GROUP BY s.role
                    ) LOOP
                        execsql('REVOKE '||rec.privs||' FROM "'||rec.role||'"');
                    END LOOP;
                END IF;
            END IF;
        EXCEPTION
            WHEN others THEN
                NULL;
        END;
        -- assign output
        :var_error:= v_error;
        :var_errstr:= v_errstr;
        :var_changes:= v_changes;
    END;
    """ % (
        objs_subquery,
        rs_subquery,
        rp_subquery,
        objs_subquery,
        rs_subquery,
        rp_subquery,
        rs_subquery,
        rp_subquery,
        rs_subquery,
        rp_subquery,
    )
    c.execute(
        plsql_block,
        {
            'var_changes': var_changes,
            'var_error': var_error,
            'var_errstr': var_errstr,
            'var_privs': var_privs,
            'var_objs': var_objs,
            'var_objtype': objtypes.upper(),
            'var_roles': var_roles,
            'var_state': module.params['state'],
            'var_quiet': 1 if module.params['quiet'] else 0,
        },
    )
    if var_error.getvalue() > 0:
        conn.rollback()
        module.fail_json(msg=var_errstr.getvalue(), changed=var_changes.getvalue() > 0)
    else:
        conn.commit()
    module.exit_json(msg=var_errstr.getvalue(), changed=var_changes.getvalue() > 0)


if __name__ == '__main__':
    main()
