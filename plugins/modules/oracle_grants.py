#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_grants
short_description: Manage users/schemas in an Oracle database
description:
    - Manage grants/privileges in an Oracle database
    - Handles role/sys privileges at the moment.
    - It is possible to add object privileges as well, but they are not considered
      when removing privs at the moment.
version_added: "1.9.1"
options:
    hostname:
        description: >
            The Oracle database host
        required: false
        default: localhost
    port:
        description: The listener port number on the host
        required: false
        default: 1521
    service_name:
        description: >
            The database service name to connect to
        required: true
    user:
        description: >
            The Oracle user name to connect to the database
        required: true
    password:
        description: >
            The Oracle user password for 'user'
        required: true
    mode:
        description: >
            The mode with which to connect to the database
        required: true
        default: normal
        choices: ['normal','sysdba']
    schema:
        description: >
            The schema that should get grants added/removed
        required: false
        default: null
    grants:
        description: >
            The privileges granted to the new schema. Can be a string or a list
        required: false
        default: null
    object_privs:
        description: >
            The privileges granted to specific objects
            # - format: 'priv1,priv2,priv3:owner.object_name'
            #   e.g:
            #   - select,update,insert,delete:sys.dba_tablespaces
            #   - select:sys.v_$session
        required: false
        default: null
    grants_mode:
        description: >
            Should the list of grants be enforced, or just appended to.
            enforce: Whatever is in the list of grants will be enforced,
            i.e grants/privileges will be removed if they are not in the list
            append: Grants/privileges are just appended, nothing is removed
        default: enforce
        choices: ['enforce','append']
    state:
        description: >
            The intended state of the priv
            (present=added to the user,
            absent=removed from the user).
            REMOVEALL will remove ALL role/sys privileges
        default: present
        choices: ['present','absent','REMOVEALL']
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Add grants to the user
oracle_grants:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: manager
    schema:myschema
    state: present
    grants: 'create session','create any table',connect,resource

# Revoke the 'create any table' grant
oracle_grants:
    hostname: localhost
    service_name: orcl
    user: system
    password: manager
    schema: myschema
    state: absent
    grants: 'create any table'

# Remove all grants from a user
oracle_grants:
    hostname: localhost
    service_name: orcl
    user: system
    password: manager
    schema: myschema
    state: REMOVEALL
    grants:
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


def clean_string(item):
    item = (
        item.replace("'", "")
        .replace(", ", ",")
        .lstrip(" ")
        .rstrip(",")
        .replace("[", "")
        .replace("]", "")
    )

    return item


def clean_list(item):
    item = [
        p.replace("'", "")
        .replace(", ", ",")
        .lstrip(" ")
        .rstrip(",")
        .replace("[", "")
        .replace("]", "")
        for p in item
    ]

    return item


# Check if the user/schema exists
def check_user_exists(module, msg, cursor, schema):
    if not (schema):
        module.fail_json(msg='Error: Missing schema name (User)', changed=False)
        return False

    schema = clean_string(schema)
    sql = 'select count(*) from dba_users where username = upper(\'%s\')' % schema

    try:
        cursor.execute(sql)
        result = cursor.fetchone()[0]
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + 'sql: ' + sql
        return False

    if result > 0:
        return True
    else:
        msg = 'User doesn\'t exist'  # noqa F841
        return False


# Check if the user/role exists
def check_role_exists(module, msg, cursor, role):
    if not (role):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    role = clean_string(role)
    sql = 'select role from dba_roles where role = upper(\'%s\')' % role

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + 'sql: ' + sql
        return False

    if result > 0:
        # module.exit_json(msg='(role) sql %s'% sql, changed=False)
        return True
    else:
        msg = 'Role doesn\'t exist'  # noqa F841
        return False


def get_dir_privs(module, msg, cursor, schema, directory_privs, grants_mode):
    total_sql_dir = []
    # Directory Privs

    # module.exit_json(msg=directory_privs)
    wanted_dirprivs_list = directory_privs
    w_object_name_l = [w.split(':')[1].lower() for w in wanted_dirprivs_list]
    # w_object_priv_l = [w.split(':')[0].lower() for w in wanted_dirprivs_list]
    currdsql_all = """
    select lower(listagg(p.privilege,',') within group (order by p.privilege)
           || ':' || p.owner || '.' || p.table_name)
    from dba_tab_privs p, dba_objects o
    where p.grantee = upper(\'%s\')
    and p.table_name = o.object_name
    and p.owner = o.owner
    and o.object_type = 'DIRECTORY'
    group by p.owner,p.table_name
    """ % (
        schema
    )

    result = execute_sql_get(module, msg, cursor, currdsql_all)

    grant_list_dir = []
    revoke_list_dir = []
    current_privs_l = [
        a[0] for a in result
    ]  # Turn list of tuples into list from resultset
    c_dir_name_l = [o.split(':')[1].lower() for o in current_privs_l]
    # c_dir_priv_l = [o.split(':')[0].lower() for o in current_privs_l]
    remove_completely_dir = set(c_dir_name_l).difference(w_object_name_l)
    if len(list(remove_completely_dir)) > 0:
        for remove in list(remove_completely_dir):
            rdsql = 'revoke all on directory %s from %s' % (remove, schema)
            revoke_list_dir.append(rdsql)

    newstuff = set(w_object_name_l).difference(c_dir_name_l)
    if len(list(newstuff)) > 0:
        for index, value in enumerate(w_object_name_l):
            if value in list(newstuff):
                nsql = "grant %s on directory %s to %s" % (
                    wanted_dirprivs_list[index].split(':')[0],
                    value,
                    schema,
                )
                grant_list_dir.append(nsql)

    if len(current_privs_l) > 0 and len(wanted_dirprivs_list) > 0:
        for cp in current_privs_l:
            # object_owner not used anymore
            # object_owner = cp.split(':').pop().split('.')[0]
            # object_name not used anymore
            # object_name = cp.split(':').pop().split('.')[1]
            cp_privs = cp.split(':')[0].lower()
            for wp in wanted_dirprivs_list:
                wp_object = wp.split(':')[1].lower()
                if wp.split(':')[1].lower() == cp.split(':')[1].lower():
                    # Compare object_names
                    cp_privs = cp.split(':')[0].lower().split(',')
                    wp_privs = wp.split(':')[0].lower().split(',')
                    priv_add = set(wp_privs).difference(cp_privs)
                    priv_revoke = set(cp_privs).difference(wp_privs)
                    if len(list(priv_add)) > 0:
                        adsql = "grant %s on directory %s to %s" % (
                            ','.join(a for a in priv_add),
                            wp_object,
                            schema,
                        )
                        grant_list_dir.append(adsql)
                    if len(list(priv_revoke)) > 0:
                        rdsql = "revoke %s on directory %s from %s" % (
                            ','.join(a for a in priv_revoke),
                            wp_object,
                            schema,
                        )
                        revoke_list_dir.append(rdsql)

    if len(grant_list_dir) > 0:
        for a in grant_list_dir:
            total_sql_dir.append(a)

    if grants_mode.lower() == 'enforce':
        if len(revoke_list_dir) > 0:
            for a in revoke_list_dir:
                total_sql_dir.append(a)
    else:
        pass

    return total_sql_dir


def get_obj_privs(module, msg, cursor, schema, object_privs, grants_mode):
    total_sql_obj = []
    # OBJECT PRIVS
    wanted_privs_list = object_privs
    w_object_name_l = [w.split(':')[1].lower() for w in wanted_privs_list]
    # w_object_priv_l = [w.split(':')[0].lower() for w in wanted_privs_list]
    currsql_all = """
    select lower(listagg(p.privilege, ',') within group (order by p.privilege)
                    || ':' || p.owner || '.' || p.table_name
                )
    from dba_tab_privs p, dba_objects o
    where p.grantee = upper(\'%s\')
    and p.table_name = o.object_name
    and p.owner = o.owner
    and o.object_type not in ('DIRECTORY','TABLE PARTITION','TABLE SUBPARTITION')
    group by p.owner,p.table_name
    """ % (
        schema
    )

    result = execute_sql_get(module, msg, cursor, currsql_all)

    grant_list = []
    revoke_list = []
    # Turn list of tuples into list from resultset
    current_privs_l = [a[0] for a in result]
    c_object_name_l = [o.split(':')[1].lower() for o in current_privs_l]
    # c_object_priv_l = [o.split(':')[0].lower() for o in current_privs_l]
    remove_completely = set(c_object_name_l).difference(w_object_name_l)
    if len(list(remove_completely)) > 0:
        for remove in list(remove_completely):
            rsql = 'revoke all on %s from %s' % (remove, schema)
            revoke_list.append(rsql)

    newstuff = set(w_object_name_l).difference(c_object_name_l)
    if len(list(newstuff)) > 0:
        for index, value in enumerate(w_object_name_l):
            if value in list(newstuff):
                nsql = "grant %s on %s to %s" % (
                    wanted_privs_list[index].split(':')[0],
                    value,
                    schema,
                )
                grant_list.append(nsql)

    if len(current_privs_l) > 0 and len(wanted_privs_list) > 0:
        for cp in current_privs_l:
            # object_owner not used anymore
            # object_owner = cp.split(':').pop().split('.')[0]
            # object_name not used anymore
            # object_name = cp.split(':').pop().split('.')[1]
            cp_privs = cp.split(':')[0].lower()
            for wp in wanted_privs_list:
                wp_object = wp.split(':')[1].lower()
                if (
                    wp.split(':')[1].lower() == cp.split(':')[1].lower()
                ):  # Compare object_names
                    cp_privs = cp.split(':')[0].lower().split(',')
                    wp_privs = wp.split(':')[0].lower().split(',')
                    priv_add = set(wp_privs).difference(cp_privs)
                    priv_revoke = set(cp_privs).difference(wp_privs)
                    if len(list(priv_add)) > 0:
                        asql = "grant %s on %s to %s" % (
                            ','.join(a for a in priv_add),
                            wp_object,
                            schema,
                        )
                        grant_list.append(asql)
                    if len(list(priv_revoke)) > 0:
                        rsql = "revoke %s on %s from %s" % (
                            ','.join(a for a in priv_revoke),
                            wp_object,
                            schema,
                        )
                        revoke_list.append(rsql)

    if len(grant_list) > 0:
        for a in grant_list:
            total_sql_obj.append(a)

    if grants_mode.lower() == 'enforce':
        if len(revoke_list) > 0:
            for a in revoke_list:
                total_sql_obj.append(a)
    else:
        pass

    return total_sql_obj


# Add grants to the schema/role
def ensure_grants(
    module,
    msg,
    cursor,
    schema,
    wanted_grants_list,
    object_privs,
    directory_privs,
    grants_mode,
    container,
):
    add_sql = ''
    remove_sql = ''

    # If no privs are added, we set the 'wanted' lists to be empty.
    if wanted_grants_list is None or wanted_grants_list == ['']:
        wanted_grants_list = []
    if object_privs is None or object_privs == ['']:
        object_privs = []
    if directory_privs is None or directory_privs == ['']:
        directory_privs = []

    # This list will hold all grants the user currently has
    dir_privs = []
    obj_privs = []
    total_sql = []
    total_current = []

    dir_privs = get_dir_privs(module, msg, cursor, schema, directory_privs, grants_mode)
    if len(dir_privs) > 0:
        for d in dir_privs:
            total_sql.append(d)

    obj_privs = get_obj_privs(module, msg, cursor, schema, object_privs, grants_mode)
    if len(obj_privs) > 0:
        for o in obj_privs:
            total_sql.append(o)

    # module.exit_json(msg=total_sql)
    exceptions_list = ['DBA']
    exceptions_priv = ['UNLIMITED TABLESPACE']

    if not (schema):  # or not(wanted_grants_list):
        module.fail_json(msg='Error: Missing schema/role name or grants', changed=False)
        return False

    # Strip the list of unnecessary quotes etc
    wanted_grants_list = clean_list(wanted_grants_list)
    wanted_grants_list = [x.lower() for x in wanted_grants_list]
    wanted_grants_list_upper = [x.upper() for x in wanted_grants_list]
    schema = clean_string(schema)

    # Get the current role grants for the schema.
    # If any are present, add them to the total
    curr_role_grants = get_current_role_grants(module, msg, cursor, schema)
    if any(curr_role_grants):
        total_current.extend(curr_role_grants)

    # Get the current sys privs for the schema.
    # If any are present, add them to the total
    curr_sys_grants = get_current_sys_grants(module, msg, cursor, schema)
    if any(curr_sys_grants):
        total_current.extend(curr_sys_grants)

    # Get the difference between current grants and wanted grants
    grants_to_add = set(wanted_grants_list).difference(total_current)
    grants_to_remove = set(total_current).difference(wanted_grants_list)

    # Special case: If DBA is granted to a user, unlimited tablespace is also implicitly
    # granted -> on the next run, unlimited tablespace is removed from the user
    # since it is not part of the wanted grants.
    # The following removes 'unlimited tablespace' privilege from the
    # grants_to_remove list, if DBA is also granted

    if any(x in exceptions_list for x in wanted_grants_list_upper):
        grants_to_remove = [
            x for x in grants_to_remove if x.upper() not in exceptions_priv
        ]

    # if there are differences, they will be added.
    if not any(grants_to_add) and not any(grants_to_remove):
        pass
        # module.exit_json(msg="Nothing to do", changed=False)
    else:
        # Convert the list of grants to a string
        if any(grants_to_add):
            grants_to_add = ','.join(grants_to_add)
            grants_to_add = clean_string(grants_to_add)
            add_sql += 'grant %s to %s' % (grants_to_add, schema)
            if container:
                add_sql += ' container=%s' % (container)
            total_sql.append(add_sql)

        if grants_mode.lower() == 'enforce':
            if any(grants_to_remove):
                grants_to_remove = ','.join(grants_to_remove)
                grants_to_remove = clean_string(grants_to_remove)
                remove_sql += 'revoke %s from %s' % (grants_to_remove, schema)
                total_sql.append(remove_sql)
        else:
            pass

    # module.exit_json(msg=total_sql)
    if len(total_sql) > 0:
        if ensure_grants_state_sql(module, msg, cursor, total_sql):
            module.exit_json(msg=total_sql, changed=True)
    else:
        msg = 'Nothing to do'
        module.exit_json(msg=msg, changed=False)
    #     return False
    # return True


def ensure_grants_state_sql(module, msg, cursor, total_sql):
    for a in total_sql:
        execute_sql(module, msg, cursor, a)
    return True


def execute_sql(module, msg, cursor, sql):
    try:
        cursor.execute(sql)
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
        return False
    return True


# Remove grants to the schema
def remove_grants(module, msg, cursor, schema, remove_grants_list, object_privs, state):
    sql = ''

    # This list will hold all grants/privs the user currently has
    total_current = []

    if not (schema) or not (remove_grants_list):
        module.fail_json(msg='Error: Missing schema name or grants', changed=False)
        return False

    # Strip the list of unnecessary quotes etc
    remove_grants_list = clean_list(remove_grants_list)
    schema = clean_string(schema)

    # Get the current role grants for the schema.
    # If any are present, add them to the total
    curr_role_grants = get_current_role_grants(module, msg, cursor, schema)
    if any(curr_role_grants):
        total_current.extend(curr_role_grants)

    # Get the current sys privs for the schema
    # If any are present, add them to the total
    curr_sys_grants = get_current_sys_grants(module, msg, cursor, schema)
    if any(curr_sys_grants):
        total_current.extend(curr_sys_grants)

    # Get the difference between current grants and wanted grants
    grants_to_remove = set(remove_grants_list).intersection(total_current)

    # If state=REMOVEALL is used, all grants/privs will be removed
    if state == 'REMOVEALL' and any(total_current):
        remove_all = ','.join(total_current)
        sql += 'revoke %s from %s' % (remove_all, schema)
        msg = 'All privileges/grants (%s) are removed from schema/role %s' % (
            remove_all,
            schema,
        )

        try:
            cursor.execute(sql)
        except cx_Oracle.DatabaseError as exc:
            (error,) = exc.args
            msg = (
                'Something went wrong while removing all grants from the schema/role '
                '- %s sql: %s' % (error.message, sql)
            )
            return False

    # if there are differences, they will be removed.
    elif not any(grants_to_remove):
        module.exit_json(
            msg="The schema/role (%s) doesn\'t have the grant(s) you want to remove"
            % schema,
            changed=False,
        )

    else:
        # Convert the list of grants to a string & clean it
        grants_to_remove = ','.join(grants_to_remove)
        grants_to_remove = clean_string(grants_to_remove)
        sql += 'revoke %s from %s' % (grants_to_remove, schema)
        msg = 'The grant(s) (%s) successfully removed from the schema/role %s' % (
            grants_to_remove,
            schema,
        )

        try:
            cursor.execute(sql)
        except cx_Oracle.DatabaseError as exc:
            (error,) = exc.args
            msg = (
                'Blergh, something went wrong while removing grants from the '
                'schema/role - %s sql: %s' % (error.message, sql)
            )
            return False

    return True


# Get the current role/sys grants
def get_current_role_grants(module, msg, cursor, schema):
    curr_role_grants = []

    sql = (
        'select granted_role from dba_role_privs where grantee = upper(\'%s\') '
        % schema
    )

    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + 'sql: ' + sql  # noqa F841
        return False
    # if result > 0:
    for item in result:
        curr_role_grants.append(item[0].lower())

    return curr_role_grants


# Get the current sys grants
def get_current_sys_grants(module, msg, cursor, schema):
    curr_sys_grants = []

    sql = 'select privilege from dba_sys_privs where grantee = upper(\'%s\') ' % schema

    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = error.message + 'sql: ' + sql  # noqa F841
        return False
    # if result > 0:
    for item in result:
        curr_sys_grants.append(item[0].lower())

    return curr_sys_grants


def execute_sql_get(module, msg, cursor, sql):
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql_get - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
        return False
    return result


def main():
    global msg

    msg = ['']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(default='localhost'),
            port=dict(default=1521),
            service_name=dict(required=True),
            user=dict(required=False),
            password=dict(required=False, no_log=True),
            mode=dict(default='normal', choices=["normal", "sysdba"]),
            schema=dict(default=None),
            role=dict(default=None),
            grants=dict(default=None, type="list"),
            object_privs=dict(default=None, type="list", aliases=['objprivs']),
            directory_privs=dict(default=None, type="list", aliases=['dirprivs']),
            grants_mode=dict(
                default="enforce", choices=["append", "enforce"], aliases=['privs_mode']
            ),
            container=dict(default=None),
            state=dict(default="present", choices=["present", "absent", "REMOVEALL"]),
        ),
        mutually_exclusive=[['schema', 'role']],
    )

    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    user = module.params["user"]
    password = module.params["password"]
    mode = module.params["mode"]
    schema = module.params["schema"]
    role = module.params["role"]
    grants = module.params["grants"]
    object_privs = module.params["object_privs"]
    directory_privs = module.params["directory_privs"]
    grants_mode = module.params["grants_mode"]
    container = module.params["container"]
    state = module.params["state"]

    if not cx_oracle_exists:
        module.fail_json(
            msg=(
                "The cx_Oracle module is required. "
                "'pip install cx_Oracle' should do the trick. "
                "If cx_Oracle is installed, make sure "
                "ORACLE_HOME & LD_LIBRARY_PATH is set"
            )
        )

    wallet_connect = '/@%s' % service_name
    try:
        if not user and not password:
            # If neither user or password is supplied,
            # the use of an oracle wallet is assumed
            if mode == 'sysdba':
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
            else:
                connect = wallet_connect
                conn = cx_Oracle.connect(wallet_connect)

        elif user and password:
            if mode == 'sysdba':
                dsn = cx_Oracle.makedsn(
                    host=hostname, port=port, service_name=service_name
                )
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
            else:
                dsn = cx_Oracle.makedsn(
                    host=hostname, port=port, service_name=service_name
                )
                connect = dsn
                conn = cx_Oracle.connect(user, password, dsn)

        elif not (user) or not (password):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Could not connect to database - %s, connect descriptor: %s' % (
            error.message,
            connect,
        )
        module.fail_json(msg=msg, changed=False)

    cursor = conn.cursor()

    if state == 'present' and schema:
        if check_user_exists(module, msg, cursor, schema):
            if ensure_grants(
                module,
                msg,
                cursor,
                schema,
                grants,
                object_privs,
                directory_privs,
                grants_mode,
                container,
            ):
                # msg = 'The grant(s) (%s) have been added to %s successfully'
                #  % (grants, schema)
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            msg = 'Schema %s doesn\'t exist' % (schema)
            module.fail_json(msg=msg, changed=False)

    elif state == 'present' and role:
        if check_role_exists(module, msg, cursor, role):
            ensure_grants(
                module,
                msg,
                cursor,
                role,
                grants,
                object_privs,
                directory_privs,
                grants_mode,
                container,
            )
            # msg = 'The grant(s) (%s) have been added to %s successfully'
            # % (grants, schema)
            module.exit_json(msg=msg, changed=False)
            # else:
            #     module.fail_json(msg=msg, changed=False)
        else:
            msg = 'Role %s doesn\'t exist' % (role)
            module.fail_json(msg=msg, changed=False)

    elif (state == 'absent' or state == 'REMOVEALL') and schema:
        # module.exit_json(msg='absent & schema', changed=False)
        if check_user_exists(module, msg, cursor, schema):
            if remove_grants(module, msg, cursor, schema, grants, state):
                # msg = 'The schema %s has been dropped successfully' % schema
                module.exit_json(msg=msg, changed=True)
        else:
            module.exit_json(
                msg='The schema (%s) doesn\'t exist' % schema, changed=False
            )

    elif (state == 'absent' or state == 'REMOVEALL') and role:
        # module.exit_json(msg='absent & role', changed=False)
        if check_role_exists(module, msg, cursor, role):
            if remove_grants(module, msg, cursor, role, grants, state):
                # msg = 'The schema %s has been dropped successfully' % schema
                module.exit_json(msg=msg, changed=True)
        else:
            module.exit_json(msg='The role (%s) doesn\'t exist' % role, changed=False)
    else:
        module.fail_json(msg='Missing schema or role', changed=False)

    module.fail_json(msg='Unknown object', changed=False)


if __name__ == '__main__':
    main()
