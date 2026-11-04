#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracle_identifier import (  # noqa: E501
    normalize_identifier,
    quote_identifier,
    split_object_identifier,
)

DOCUMENTATION = '''
---
module: oracle_grants
short_description: Manage privileges of users and roles in an Oracle database
description:
    - Grants and revokes roles, system privileges, object privileges and directory
      privileges for a user (O(schema)) or a role (O(role)) in an Oracle database.
    - Current role and system privileges are read from C(DBA_ROLE_PRIVS) and
      C(DBA_SYS_PRIVS), object and directory privileges from C(DBA_TAB_PRIVS).
    - With O(state=present) the wanted privileges are compared with the current ones
      and only the differences are granted (and revoked with
      O(grants_mode=enforce)). C(changed=true) is reported if at least one
      statement was executed.
    - With O(state=absent) or O(state=REMOVEALL) only roles and system privileges are
      revoked. Object and directory privileges are not touched.
    - Names (users, roles, owners, objects, directories) are handled like
      identifiers in SQL. A name in double quotes is case sensitive, e.g.
      V("MyUser") or V(select:APP."MyTable"). A name without quotes is converted to
      uppercase. Names are always quoted in the SQL statements, system privileges
      are never quoted.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "1.9.1"
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
            - The Oracle user name to connect to the database.
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
    schema:
        description:
            - The user (schema) whose privileges are managed.
            - Converted to uppercase unless it is enclosed in double quotes.
            - With O(state=present) the module fails if the user does not exist, with
              O(state=absent) or O(state=REMOVEALL) it returns C(changed=false).
            - Mutually exclusive with O(role). One of O(schema) or O(role) is required.
        type: str
        required: false
    role:
        description:
            - The role whose privileges are managed.
            - Converted to uppercase unless it is enclosed in double quotes.
            - Mutually exclusive with O(schema).
        type: str
        required: false
    grants:
        description:
            - List of roles and system privileges, for example V(connect) or
              V(create session).
            - A role in double quotes is case sensitive, e.g. V("MyRole"). Other
              names (roles and system privileges) are converted to uppercase.
            - Single quotes and square brackets in the elements are removed.
            - With O(state=present) and O(grants_mode=enforce), all roles and system
              privileges not in this list are revoked, so omitting O(grants) revokes
              all of them. If V(dba) is in the list, C(UNLIMITED TABLESPACE) is never
              revoked.
            - With O(state=absent) the listed roles and system privileges are revoked.
            - Must not be empty with O(state=absent) and O(state=REMOVEALL).
        type: list
        elements: str
        required: false
    object_privs:
        description:
            - List of object privileges in the format
              C(<priv>[,<priv>...]:<owner>.<object_name>), for example
              V(select,update:app.orders) or V(select:sys.v_$session).
            - Owner and object name can be in double quotes (case sensitive), e.g.
              V(select:APP."MyTable") or V(select:"MyOwner"."MyTable").
            - Without C(<owner>.), the object is in the current schema of the
              connection, like in C(GRANT).
            - Missing privileges are granted. With O(grants_mode=enforce), privileges
              not in the list are revoked, and all privileges on objects not in the
              list are revoked with C(REVOKE ALL), so omitting O(object_privs)
              revokes all object privileges.
            - Only used with O(state=present).
        type: list
        elements: str
        required: false
        aliases: ['objprivs']
    directory_privs:
        description:
            - List of directory privileges in the format
              C(<priv>[,<priv>...]:<directory_object>), for example
              V(read,write:sys.data_pump_dir).
            - The directory can be given with or without C(sys.), directories are
              owned by C(SYS). The name can be in double quotes (case sensitive),
              e.g. V(read:"MyDir").
            - Missing privileges are granted. With O(grants_mode=enforce), privileges
              not in the list are revoked, and all privileges on directories not in
              the list are revoked with C(REVOKE ALL), so omitting
              O(directory_privs) revokes all directory privileges.
            - Only used with O(state=present).
        type: list
        elements: str
        required: false
        aliases: ['dirprivs']
    grants_mode:
        description:
            - How to handle existing privileges that are not wanted with
              O(state=present).
            - V(enforce) - privileges not listed in O(grants), O(object_privs) and
              O(directory_privs) are revoked.
            - V(append) - missing privileges are granted, nothing is revoked.
        type: str
        required: false
        default: enforce
        choices: ['enforce', 'append']
        aliases: ['privs_mode']
    container:
        description:
            - Value for the C(CONTAINER=) clause, for example V(all) or V(current).
            - Added to the C(GRANT) statement for roles and system privileges and to
              the C(GRANT) and C(REVOKE) statements for object privileges. Not used for
              directory privileges and for revoking roles and system privileges.
        type: str
        required: false
    state:
        description:
            - V(present) - roles and privileges are granted (and revoked, see
              O(grants_mode)).
            - V(absent) - the roles and system privileges in O(grants) are revoked.
            - V(REMOVEALL) - all roles and system privileges are revoked. O(grants)
              must still be set to a non-empty value.
        type: str
        required: false
        default: present
        choices: ['present', 'absent', 'REMOVEALL']
notes:
    - python-oracledb needs to be installed, e.g. with the role
      C(opitzconsulting.ansible_oracle.pyoracledb).
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Grant roles, system and object privileges to a user
  opitzconsulting.ansible_oracle.oracle_grants:
    hostname: remote-db-server
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    schema: myschema
    grants:
      - create session
      - create any table
      - connect
      - resource
    object_privs:
      - select,update,insert,delete:sys.dba_tablespaces
      - select:sys.v_$session
    directory_privs:
      - read,write:sys.data_pump_dir
    state: present

- name: Add a role to a user without revoking other privileges
  opitzconsulting.ansible_oracle.oracle_grants:
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    schema: myschema
    grants: select_catalog_role
    grants_mode: append
    state: present

- name: Revoke the 'create any table' privilege
  opitzconsulting.ansible_oracle.oracle_grants:
    service_name: orcl
    user: system
    password: "{{ system_password }}"
    schema: myschema
    grants: create any table
    state: absent

- name: Revoke all roles and system privileges (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_grants:
    service_name: orcl
    schema: myschema
    grants: all
    state: REMOVEALL
'''

RETURN = '''
msg:
    description:
        - With O(state=present), the list of executed SQL statements if something
          was changed, otherwise V(Nothing to do).
        - With O(state=absent) or O(state=REMOVEALL), a message if nothing was
          changed. If something was revoked, the value is C([""]).
    returned: always
    type: raw
    sample: ["grant connect,resource to myschema"]
'''


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


# Check if the user/schema exists (grantee is normalized)
def check_user_exists(module, msg, cursor, grantee):
    if not (grantee):
        module.fail_json(msg='Error: Missing schema name (User)', changed=False)
        return False

    sql = 'select count(*) from dba_users where username = :name'
    return execute_sql_get(module, msg, cursor, sql, {'name': grantee})[0][0] > 0


# Check if the role exists (grantee is normalized)
def check_role_exists(module, msg, cursor, grantee):
    if not (grantee):
        module.fail_json(msg='Error: Missing role name', changed=False)
        return False

    sql = 'select count(*) from dba_roles where role = :name'
    return execute_sql_get(module, msg, cursor, sql, {'name': grantee})[0][0] > 0


def parse_tab_privs(module, privs_list, default_owner, kind):
    """Parse the wanted object or directory privileges.

    <priv>[,<priv>...]:[<owner>.]<name>, owner and name can be in double quotes.
    Returns {(owner, name): set of privileges in uppercase}.
    """
    wanted = {}
    for entry in privs_list:
        if ':' not in entry:
            module.fail_json(
                msg='Invalid %s privilege %s, format: <priv>[,<priv>...]:<name>'
                % (kind, entry),
                changed=False,
            )
        privs, name = entry.split(':', 1)
        parts = split_object_identifier(name, default_owner)
        if not parts:
            module.fail_json(
                msg='Invalid %s name %s in %s' % (kind, name, entry), changed=False
            )
        key = tuple(parts)
        wanted.setdefault(key, set()).update(
            p.strip().upper() for p in privs.split(',') if p.strip()
        )
    return wanted


def get_current_tab_privs(module, msg, cursor, grantee, directory):
    """Current object or directory privileges of grantee.

    Returns {(owner, name): set of privileges} as stored in DBA_TAB_PRIVS.
    """
    if directory:
        type_filter = "o.object_type = 'DIRECTORY'"
    else:
        type_filter = (
            "o.object_type not in ('DIRECTORY','TABLE PARTITION','TABLE SUBPARTITION')"
        )
    sql = (
        'select p.owner, p.table_name, p.privilege '
        'from dba_tab_privs p, dba_objects o '
        'where p.grantee = :grantee '
        'and p.table_name = o.object_name '
        'and p.owner = o.owner '
        'and %s' % type_filter
    )
    current = {}
    for owner, name, priv in execute_sql_get(
        module, msg, cursor, sql, {'grantee': grantee}
    ):
        current.setdefault((owner, name), set()).add(priv)
    return current


def get_tab_privs_sql(module, msg, cursor, grantee, privs_list, grants_mode, kind):
    """GRANT/REVOKE statements for object (kind='object') or directory privileges."""
    directory = kind == 'directory'
    if directory:
        # directories are owned by SYS, given as sys.<dir> or <dir>
        default_owner = 'SYS'
    else:
        # like in GRANT: an object without owner is in the current schema
        default_owner = execute_sql_get(
            module,
            msg,
            cursor,
            "select sys_context('userenv', 'current_schema') from dual",
        )[0][0]

    wanted = parse_tab_privs(module, privs_list, default_owner, kind)
    current = get_current_tab_privs(module, msg, cursor, grantee, directory)

    def on_object(key):
        if directory:
            return 'directory %s' % quote_identifier(key[1])
        return '%s.%s' % (quote_identifier(key[0]), quote_identifier(key[1]))

    grant_list = []
    revoke_list = []
    for key, privs in wanted.items():
        priv_add = privs.difference(current.get(key, set()))
        if priv_add:
            grant_list.append(
                'grant %s on %s to %s'
                % (
                    ','.join(sorted(priv_add)),
                    on_object(key),
                    quote_identifier(grantee),
                )
            )
        priv_revoke = current.get(key, set()).difference(privs)
        if priv_revoke:
            revoke_list.append(
                'revoke %s on %s from %s'
                % (
                    ','.join(sorted(priv_revoke)),
                    on_object(key),
                    quote_identifier(grantee),
                )
            )
    for key in sorted(set(current).difference(wanted)):
        revoke_list.append(
            'revoke all on %s from %s' % (on_object(key), quote_identifier(grantee))
        )

    if grants_mode.lower() == 'enforce':
        return grant_list + revoke_list
    return grant_list


def parse_grants(grants_list):
    """Normalize roles and system privileges.

    Returns (set of names as stored in the data dictionary, set of names in double
    quotes). A name in double quotes is a role and case sensitive, a name without
    quotes (role or system privilege) is converted to uppercase.
    """
    names = set()
    quoted = set()
    for item in clean_list(grants_list):
        item = item.strip()
        if not item:
            continue
        name = normalize_identifier(item)
        names.add(name)
        if item != name and item.startswith('"'):
            quoted.add(name)
    return names, quoted


def grants_to_sql(names, roles):
    """Comma separated list for GRANT/REVOKE: roles are quoted, system privileges
    (keywords like CREATE SESSION) not."""
    return ','.join(quote_identifier(n) if n in roles else n for n in sorted(names))


# Add grants to the schema/role
def ensure_grants(
    module,
    msg,
    cursor,
    grantee,
    wanted_grants_list,
    object_privs,
    directory_privs,
    grants_mode,
    container,
):
    # If no privs are added, we set the 'wanted' lists to be empty.
    if wanted_grants_list is None or wanted_grants_list == ['']:
        wanted_grants_list = []
    if object_privs is None or object_privs == ['']:
        object_privs = []
    if directory_privs is None or directory_privs == ['']:
        directory_privs = []

    if not (grantee):
        module.fail_json(msg='Error: Missing schema/role name or grants', changed=False)
        return False

    total_sql = []
    total_sql.extend(
        get_tab_privs_sql(
            module, msg, cursor, grantee, directory_privs, grants_mode, 'directory'
        )
    )
    for objpriv_sql in get_tab_privs_sql(
        module, msg, cursor, grantee, object_privs, grants_mode, 'object'
    ):
        if container:
            objpriv_sql += ' container=%s' % (container)
        total_sql.append(objpriv_sql)

    wanted, wanted_quoted = parse_grants(wanted_grants_list)
    curr_roles = get_current_role_grants(module, msg, cursor, grantee)
    curr_sys = get_current_sys_grants(module, msg, cursor, grantee)
    total_current = curr_roles | curr_sys

    # Get the difference between current grants and wanted grants
    grants_to_add = wanted.difference(total_current)
    grants_to_remove = total_current.difference(wanted)

    # Special case: If DBA is granted to a user, unlimited tablespace is also implicitly
    # granted -> on the next run, unlimited tablespace is removed from the user
    # since it is not part of the wanted grants.
    # The following removes 'unlimited tablespace' privilege from the
    # grants_to_remove list, if DBA is also granted
    if 'DBA' in wanted:
        grants_to_remove.discard('UNLIMITED TABLESPACE')

    if grants_to_add:
        add_sql = 'grant %s to %s' % (
            grants_to_sql(grants_to_add, wanted_quoted),
            quote_identifier(grantee),
        )
        if container:
            add_sql += ' container=%s' % (container)
        total_sql.append(add_sql)

    if grants_mode.lower() == 'enforce' and grants_to_remove:
        total_sql.append(
            'revoke %s from %s'
            % (grants_to_sql(grants_to_remove, curr_roles), quote_identifier(grantee))
        )

    if len(total_sql) > 0:
        if ensure_grants_state_sql(module, msg, cursor, total_sql):
            module.exit_json(msg=total_sql, changed=True)
    else:
        msg = 'Nothing to do'
        module.exit_json(msg=msg, changed=False)


def ensure_grants_state_sql(module, msg, cursor, total_sql):
    for a in total_sql:
        execute_sql(module, msg, cursor, a)
    return True


def execute_sql(module, msg, cursor, sql):
    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
        return False
    return True


# Remove grants from the schema/role (grantee is normalized)
def remove_grants(module, msg, cursor, grantee, remove_grants_list, state):
    if not (grantee) or not (remove_grants_list):
        module.fail_json(msg='Error: Missing schema name or grants', changed=False)
        return False

    curr_roles = get_current_role_grants(module, msg, cursor, grantee)
    total_current = curr_roles | get_current_sys_grants(module, msg, cursor, grantee)

    # If state=REMOVEALL is used, all grants/privs will be removed
    if state == 'REMOVEALL':
        grants_to_remove = total_current
    else:
        grants_to_remove = parse_grants(remove_grants_list)[0].intersection(
            total_current
        )

    if not grants_to_remove:
        module.exit_json(
            msg="The schema/role (%s) doesn\'t have the grant(s) you want to remove"
            % grantee,
            changed=False,
        )

    revoke = grants_to_sql(grants_to_remove, curr_roles)
    sql = 'revoke %s from %s' % (revoke, quote_identifier(grantee))
    execute_sql(module, msg, cursor, sql)
    module.exit_json(
        msg='The grant(s) (%s) successfully removed from the schema/role %s'
        % (revoke, grantee),
        changed=True,
    )


# Get the current role grants (as stored in DBA_ROLE_PRIVS)
def get_current_role_grants(module, msg, cursor, grantee):
    sql = 'select granted_role from dba_role_privs where grantee = :grantee'
    return set(
        row[0]
        for row in execute_sql_get(module, msg, cursor, sql, {'grantee': grantee})
    )


# Get the current sys grants (as stored in DBA_SYS_PRIVS)
def get_current_sys_grants(module, msg, cursor, grantee):
    sql = 'select privilege from dba_sys_privs where grantee = :grantee'
    return set(
        row[0]
        for row in execute_sql_get(module, msg, cursor, sql, {'grantee': grantee})
    )


def execute_sql_get(module, msg, cursor, sql, binds=None):
    try:
        cursor.execute(sql, binds or {})
        result = cursor.fetchall()
    except oracledb.DatabaseError as exc:
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
    # grantee as stored in the data dictionary (case sensitive in double quotes)
    schema = module.params["schema"]
    if schema:
        schema = normalize_identifier(clean_string(schema))
    role = module.params["role"]
    if role:
        role = normalize_identifier(clean_string(role))
    grants = module.params["grants"]
    object_privs = module.params["object_privs"]
    directory_privs = module.params["directory_privs"]
    grants_mode = module.params["grants_mode"]
    container = module.params["container"]
    state = module.params["state"]

    conn = oracledb_connect(module, hostname, port, service_name, user, password, mode)
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
