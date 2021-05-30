#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_privs
short_description: Manage object and system privileges in Oracle database
description:
    - Manage users/schemas in an Oracle database
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
            - If present, then privileges are granted, if absent then privileges are revoked
        required: true
        choices: ['present','absent']
    privs:
        description:
            - Privileges to grant or revoke
            - Can be either system privileges (then objs parameter must not be specified) or object privileges (objs parameter must also be set)
        required: true
        type: list
        aliases: priv
    objs:
        description:
            - When setting object privileges, list the objects the privileges are set for.
            - Use format: SCHEMA_NAME.OBJECT_NAME
            - Wildcard (%) can be used in OBJECT_NAME part, for example HR.% to set privileges for all objects (with type objecttype) in schema HR.
            - Object names are CASE SENSITIVE, so by default use UPPER CASE.
        required: false
        type: list
        aliases: obj
    objtypes:
        description:
            - When using object privileges, list also the object types (from OBJECT_TYPE column from DBA_OBJECTS).
        required: false
        default: ['TABLE','VIEW']
        type: list
    roles:
        description:
            - List of user names and role names to set permissions to.
            - Names are CASE SENSITIVE! So by default use UPPER CASE.
        required: true
        type: list
        aliases: role
    convert_to_upper:
        description:
            - Converts all entries for role and objs parameters silently to upper case to simulate case insensitivity
        required: False
        default: True
        type: bool
    quiet:
        description:
            - If set to False, all executed commands are returned as Ansible output message
        required: False
        default: True
        type: bool

notes:
    - cx_Oracle needs to be installed
    - Oracle RDBMS 11gR2 or later required
requirements: [ "cx_Oracle", "re" ]
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
    - name: grant oracle system privileges
      oracle_privs:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
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
      environment: "{{ oracle_env }}"

    - name: revoke oracle system privileges
      oracle_privs:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
        state: absent
        privs:
          - CREATE ANY TABLE TABLE
          - SELECT ANY TABLE
        roles:
          - ILMAR
          - READER_ROLE
      environment: "{{ oracle_env }}"

    - name: grant oracle object privileges
      oracle_privs:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
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
      environment: "{{ oracle_env }}"

    - name: revoke oracle object privileges
      oracle_privs:
        hostname: "{{ oraclehost }}"
        port: "{{ oracleport }}"
        service_name: "{{ oracleservice }}"
        user: "{{ oracleuser }}"
        password: "{{ oraclepassword }}"
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
        quiet: False
      environment: "{{ oracle_env }}"
'''

import re

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True

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
            password      = dict(required=False, no_log=True),
            mode          = dict(default='normal', choices=["normal","sysdba"]),
            state         = dict(default="present", choices=["present", "absent"]),
            privs         = dict(required=True, type='list', aliases=['priv']),
            objs          = dict(required=False, type='list', aliases=['obj']), # CASE SENSITIVE! Can use wildcard %
            objtypes      = dict(required=False, default=['TABLE','VIEW'], type='list'),
            roles         = dict(required=True, type='list', aliases=['role']),
            convert_to_upper = dict(default=True, type='bool'),
            quiet         = dict(required=False, default=True, type='bool')
        ),
        supports_check_mode=True
    )
    # Check for required modules
    if not cx_oracle_exists:
        module.fail_json(msg="The cx_Oracle module is required. 'pip install cx_Oracle' should do the trick. If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set")
    # Check input parameters
    re_priv = re.compile('^[A-Za-z0-9_]+[A-Za-z0-9_ ]*[A-Za-z0-9_]+$')
    re_role = re.compile('^[A-Za-z0-9_\$#\- ]+$')
    re_obj = re.compile('^[A-Za-z0-9_\$#\- ]*\.[A-Za-z0-9_\$#\%\- ]+$')
    for p in module.params['privs']:
        if not re_priv.match(p):
            module.fail_json(msg="Invalid privilege '%s'" % p)
    for p in module.params['roles']:
        if not re_role.match(p) or p.upper() in ['SYS','SYSTEM']:
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
    c = conn.cursor()
    var_changes = c.var(cx_Oracle.NUMBER)
    var_error = c.var(cx_Oracle.NUMBER)
    var_errstr = c.var(cx_Oracle.STRING)
    var_privs = c.arrayvar(cx_Oracle.STRING, [p.upper() for p in module.params['privs']])
    objectslist = [p.replace("_", "\_") for p in module.params['objs']] if module.params['objs'] is not None else []
    var_objs = c.arrayvar(cx_Oracle.STRING, objectslist if not module.params['convert_to_upper'] else [p.upper() for p in objectslist], 100)
    var_roles = c.arrayvar(cx_Oracle.STRING, module.params['roles'] if not module.params['convert_to_upper'] else [p.upper() for p in module.params['roles']], 50)
    #
    rs_subquery = "SELECT username role FROM dba_users $IF DBMS_DB_VERSION.VERSION >= 12 $THEN WHERE oracle_maintained='N' $END UNION ALL SELECT role FROM dba_roles $IF DBMS_DB_VERSION.VERSION >= 12 $THEN WHERE oracle_maintained='N' $END INTERSECT SELECT column_value name FROM table(v_roles_sql)"
    objs_subquery = "SELECT DISTINCT o.owner, o.object_name FROM dba_objects o JOIN table(v_objs_sql) s ON o.owner||'.'||o.object_name LIKE s.column_value ESCAPE '\\' AND v_objtype LIKE '%,'||o.object_type||',%'"
    rp_subquery = "SELECT rs.role, p.column_value priv FROM rs CROSS JOIN table(v_privs_sql) p"
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
                             objpr AS (SELECT o.owner, o.object_name, rp.priv, rp.role FROM objs o CROSS JOIN rp)
                        SELECT owner, object_name, role, LISTAGG(priv,',') WITHIN GROUP (ORDER BY priv) privs FROM (
                            SELECT owner, object_name, priv, role FROM objpr
                            MINUS
                            SELECT owner, table_name, privilege, grantee FROM dba_tab_privs)
                        GROUP BY owner, object_name, role
                    ) LOOP
                        execsql('GRANT '||rec.privs||' ON "'||rec.owner||'"."'||rec.object_name||'" TO "'||rec.role||'"');
                    END LOOP;
                ELSIF v_state = 'absent' THEN
                    FOR rec IN (
                        WITH objs AS (%s),
                             rs AS (%s),
                             rp AS (%s),
                             objpr AS (SELECT o.owner, o.object_name, rp.priv, rp.role FROM objs o CROSS JOIN rp)
                        SELECT t.owner, t.table_name, t.grantee, LISTAGG(t.privilege,',') WITHIN GROUP (ORDER BY t.privilege) privs
                        FROM dba_tab_privs t JOIN objpr o ON t.owner=o.owner AND t.table_name=o.object_name AND t.privilege=o.priv AND t.grantee=o.role
                        GROUP BY t.owner, t.table_name, t.grantee
                    ) LOOP
                        execsql('REVOKE '||rec.privs||' ON "'||rec.owner||'"."'||rec.table_name||'" FROM "'||rec.grantee||'"');
                    END LOOP;
                END IF;
            ELSE
                -- System/role grants
                IF v_state = 'present' THEN
                    FOR rec IN (
                        WITH rs AS (%s),
                             rp AS (%s)
                        SELECT role, LISTAGG(priv, ',') WITHIN GROUP (ORDER BY priv) privs FROM (
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
                        SELECT s.role, LISTAGG(s.priv, ',') WITHIN GROUP (ORDER BY s.priv) privs FROM
                            (SELECT grantee role, privilege priv FROM dba_sys_privs
                             UNION ALL
                             SELECT grantee, granted_role FROM dba_role_privs) s JOIN rp ON rp.role = s.role AND rp.priv = s.priv
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
    """ % (objs_subquery, rs_subquery, rp_subquery, objs_subquery, rs_subquery, rp_subquery, rs_subquery, rp_subquery, rs_subquery, rp_subquery)
    c.execute(plsql_block, {
        'var_changes': var_changes,
        'var_error': var_error,
        'var_errstr': var_errstr,
        'var_privs': var_privs,
        'var_objs': var_objs,
        'var_objtype': objtypes.upper(),
        'var_roles': var_roles,
        'var_state': module.params['state'],
        'var_quiet': 1 if module.params['quiet'] else 0
    })
    if var_error.getvalue() > 0:
        conn.rollback()
        module.fail_json(msg=var_errstr.getvalue(), changed=var_changes.getvalue()>0)
    else:
        conn.commit()
    module.exit_json(msg=var_errstr.getvalue(), changed=var_changes.getvalue()>0)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
