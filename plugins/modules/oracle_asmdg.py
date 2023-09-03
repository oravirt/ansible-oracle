#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_asmdg
short_description: Manage diskgroups in an Oracle database
description:
  - Manage diskgroups in an Oracle database
version_added: "2.1.0"
options:
  name:
    description: The name of the diskgroup
    required: true
    default: None
    type: str
    aliases: ['diskgroup', 'dg']
  state:
    description: >
        The intended state of the diskgroup. 'status' will just show the
        status of the diskgroup
    default: present
    type: str
    choices: ['present', 'absent', 'status']
  disks:
    description: >
        A list of disks that should be part of the diskgroup. Only the listed
        disks will be part of the DG, meaning if the disk is removed from the
        list it will also be removed from the DG
    default: None
    type: str
  redundancy:
    description: >
        The redundancy configuration for the diskgroup, It does not yet
        support putting disks in specific failure groups
    default: external
    type: str
    choices: ['external', 'normal', 'high']
  attribute_name:
    description: >
        The attribute name (e.g compatible.rdbms)
    default: None
    type: str
    aliases: ['an']
  attribute_value:
    description: >
      The attribute value (e.g 12.1.0.2)
    default: None
    type: str
    aliases: ['av']
  username:
    description: The ASM username
    required: false
    type: str
    default: sys
    aliases: ['un']
  password:
    description: The password for the ASM user
    required: false
    default: None
    type: str
    aliases: ['pw']
  service_name:
    description: >
      The diskgroup_name to connect to the database if using dbms_diskgroup.
    required: false
    default: +ASM
    type: str
    aliases: ['sn']
  hostname:
    description: >
      The host of the database if using dbms_diskgroup
    required: false
    default: localhost
    type: str
    aliases: ['host']
  port:
    description: >
      The listener port to connect to the database if using dbms_diskgroup
    required: false
    default: 1521
    type: str
  oracle_home:
    description: The GI ORACLE_HOME
    required: false
    default: None
    type: str
    aliases: ['oh']

notes:
  - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Create a diskgroup
oracle_asmdg:
    name: MYDG1
    disks:
       - ORCL:MYDG1
       - ORCL:MYDG2
    attribute_name: compatible.asm
    attribute_value: 12.1.0.2
    redundancy: external
    state: present
    un: sys
    pw: oracle123
    sn: '+ASM'
    host: localhost
    oh: /u01/app/oracle/12.1.2.0/grid

oracle_asmdg:
    name: DATA
    disks:
       - /dev/oracle/data1
       - /dev/oracle/data2
    attributes:
      - {name: compatible.asm, value: 12.2.0.1.0 }
      - {name: compatible.rdbms, value: 12.2.0.1.0 }
    redundancy: external
    state: present
    un: sys
    pw: oracle123
    sn: '+ASM'
    host: localhost
    oh: /u01/app/oracle/12.2.0.1/grid

'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


# Check if the diskgroup exists
def check_diskgroup_exists(cursor, module, msg, name):
    sql = 'select count(*) from gv$asm_diskgroup where lower (name) = \'%s\'' % (
        name.lower()
    )
    result = execute_sql_get(module, msg, cursor, sql)
    if result[0][0] > 0:
        return True
    else:
        return False


def create_diskgroup(
    cursor,
    module,
    msg,
    oracle_home,
    name,
    disks,
    redundancy,
    attribute_name,
    attribute_value,
):
    add_attr = False
    if not any(x is None for x in attribute_name):
        add_attr = True
    if not any(x is None for x in attribute_name):
        add_attr = True

    if add_attr:
        attributes = ','.join(
            [
                '\'' + str(n) + '\'' + '=' + '\'' + str(v) + '\''
                for n, v in zip(attribute_name, attribute_value)
            ]
        )

    disklist = "','".join(disks)
    sql = 'create diskgroup %s ' % (name)
    sql += '%s redundancy ' % (redundancy)
    sql += 'disk \'%s\' ' % (disklist)
    if add_attr:
        sql += ' attribute %s' % (attributes.lower())

    if execute_sql(module, msg, cursor, sql):
        if rac:
            command = '%s/bin/srvctl start diskgroup -g %s' % (
                oracle_home,
                name.lower(),
            )
            (rc, stdout, stderr) = module.run_command(command)
            if rc != 0:
                if 'CRS-5702' in stdout:
                    # 'Edge-case', where there is only one instance in the
                    # cluster. The diskgroup is already running after create
                    # statement so this command errors
                    return True
                else:
                    msg = (
                        'Error, couldn\'t mount the dg on all nodes. stdout: %s, '
                        'stderr: %s, command is %s' % (stdout, stderr, command)
                    )
                    module.fail_json(msg=msg, changed=False)
            else:
                return True
        else:
            return True
    else:
        msg = 'error in exec sql create'
        module.fail_json(msg=msg, changed=False)
        return False


def remove_diskgroup(cursor, module, msg, oracle_home, name):
    mountsql = 'alter diskgroup %s mount' % (name.lower())
    dropsql = 'drop diskgroup %s' % (name.lower())

    # If in a rac config, we need to unmount the dg on all nodes, then mount
    if rac:
        command = '%s/bin/srvctl stop diskgroup -g %s' % (oracle_home, name.lower())
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            msg = (
                'Error, couldn\'t unmount the dg. stdout: %s, stderr: %s, command is %s'
                % (stdout, stderr, command)
            )
            return False

        if execute_sql(module, msg, cursor, mountsql):
            if execute_sql(module, msg, cursor, dropsql):
                return True
            else:
                return False
        else:
            return False
    else:
        if execute_sql(module, msg, cursor, dropsql):
            return True
        else:
            return False


def ensure_diskgroup_state(
    cursor, module, msg, name, state, disks, attribute_name, attribute_value
):
    total_sql = []
    # disk_sql    = []
    disk_sql = 'alter diskgroup %s ' % (name.upper())
    change_attr = False
    change_disk = False
    get_ro_attr_sql = (
        'select distinct(name) from v$asm_attribute where read_only = \'Y\''
    )
    read_only_attributes = []

    # Deal with attribute differences
    if attribute_name and attribute_value:
        # Get all read only attributes
        get_ro_attr = execute_sql_get(module, msg, cursor, get_ro_attr_sql)
        for a in get_ro_attr:
            read_only_attributes.append(a[0])

        # Make sure properties are lower case
        attribute_name = [x.lower() for x in attribute_name]
        attribute_value = [y.lower() for y in attribute_value]
        wanted_attributes = zip(attribute_name, attribute_value)

        # Make sure we don't try to modify read only attributes. Removing them
        # from the wanted_attributes list
        for a in wanted_attributes:
            if a[0] in read_only_attributes:
                wanted_attributes.remove(a)

        # Check the current attributes
        attribute_names_ = ','.join(
            ['\'' + str(n[0]) + '\'' for n in (wanted_attributes)]
        )
        # Only get current attributes if we still have attributes in the wanted list
        if len(attribute_names_) != 0:
            current_properties = get_current_properties(
                cursor, module, msg, name, attribute_names_
            )
            # Convert to dict and compare current with wanted
            if current_properties != wanted_attributes:
                change_attr = True
                for i in wanted_attributes:
                    total_sql.append(
                        "alter diskgroup %s set attribute '%s'='%s'"
                        % (name, i[0], i[1])
                    )

    list_current_name = []
    list_current_path = []
    list_wanted = [x.upper() if ':' in x else x for x in disks]
    list_current = get_current_disks(cursor, module, msg, name)

    for p, n in list_current:
        list_current_name.append(n)
        list_current_path.append(p)

    # List of disks to add
    list_add = set(list_wanted).difference(list_current_path)
    # List of disks to remove
    list_remove = set(list_current_path).difference(list_wanted)
    # Pick out the v$asm_disk.name from the diskgroup
    remove_disks = [a[1] for a in list_current if a[0] in list_remove]

    add_disk = "','".join(list_add)
    remove_disk = "','".join(remove_disks)
    if sorted(list_current_path) == sorted(list_wanted) and change_attr is False:
        msg = "Diskgroup %s is in the intended state" % (name)
        module.exit_json(msg=msg, changed=False)

    if len(list_add) >= 1:
        change_disk = True
        disk_sql += ' add disk '
        disk_sql += "'%s'" % add_disk

    if len(list_remove) >= 1:
        # disk_sql    = 'alter diskgroup %s ' % (name.upper())
        change_disk = True
        disk_sql += ' drop disk '
        disk_sql += "'%s'" % remove_disk
    if change_disk:
        total_sql.append(disk_sql)

    if ensure_diskgroup_state_sql(module, msg, cursor, total_sql):
        msg = 'Diskgroup %s has been put in the intended state' % (name)
        module.exit_json(msg=msg, changed=True)
    else:
        return False


def ensure_diskgroup_state_sql(module, msg, cursor, total_sql):
    for a in total_sql:
        execute_sql(module, msg, cursor, a)
    return True


def get_current_disks(cursor, module, msg, name):
    sql = 'select d.path,d.name from v$asm_disk d, v$asm_diskgroup dg '
    sql += 'where dg.group_number = d.group_number '
    sql += 'and upper(dg.name) = \'%s\'' % (name.upper())

    result = execute_sql_get(module, msg, cursor, sql)
    return result


def get_current_properties(cursor, module, msg, name, attribute_names_):
    sql = 'select lower(a.name),lower(a.value) '
    sql += 'from v$asm_attribute a, v$asm_diskgroup dg '
    sql += 'where dg.group_number = a.group_number '
    sql += 'and upper(dg.name) = \'%s\' ' % (name.upper())
    sql += 'and a.name in (%s) ' % (attribute_names_.lower())

    result = execute_sql_get(module, msg, cursor, sql)
    return result


def execute_sql_get(module, msg, cursor, sql):
    # module.exit_json(msg="In execute_sql_get", changed=False)
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


def main():
    msg = ['']
    cursor = None
    global rac

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['diskgroup', 'dg']),
            disks=dict(required=False, type='list'),
            redundancy=dict(
                default="external", choices=["external", "normal", "high", "flex"]
            ),
            attribute_name=dict(required=False, type='list', aliases=['an']),
            attribute_value=dict(required=False, type='list', aliases=['av']),
            state=dict(default="present", choices=["present", "absent", "status"]),
            user=dict(required=False, aliases=['un', 'username']),
            password=dict(required=False, no_log=True, aliases=['pw']),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            port=dict(required=False, default=1521),
            service_name=dict(required=False, default='+ASM', aliases=['sn']),
            oracle_home=dict(required=False, aliases=['oh']),
        ),
    )

    name = module.params["name"]
    disks = module.params["disks"]
    redundancy = module.params["redundancy"]
    attribute_name = module.params["attribute_name"]
    attribute_value = module.params["attribute_value"]
    state = module.params["state"]
    user = module.params["user"]
    password = module.params["password"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    oracle_home = module.params["oracle_home"]

    if not cx_oracle_exists:
        msg = (
            "The cx_Oracle module is required. 'pip install cx_Oracle' "
            "should do the trick. If cx_Oracle is installed, make sure "
            "ORACLE_HOME & LD_LIBRARY_PATH is set"
        )
        module.fail_json(msg=msg)

    wallet_connect = '/@%s' % service_name
    try:
        if not user and not password:
            # If neither user or password is supplied, the use of an oracle
            # wallet is assumed
            connect = wallet_connect
            conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSASM)
        elif user and password:
            dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name)
            connect = dsn
            conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSASM)
        elif not (user) or not (password):
            module.fail_json(msg='Missing username or password for cx_Oracle')

    except cx_Oracle.DatabaseError as exc:
        (error,) = exc.args
        msg = (
            'Could not connect to ASM: %s, connect descriptor: %s, '
            'username: %s, pass: %s' % (error.message, connect, user, password)
        )
        module.fail_json(msg=msg, changed=False)

    cursor = conn.cursor()

    checkifracsql = 'select parallel from v$instance'
    checkifrac = execute_sql_get(module, msg, cursor, checkifracsql)
    if checkifrac[0][0] == 'YES':
        rac = True
        if oracle_home is not None:
            os.environ['ORACLE_HOME'] = oracle_home
        elif 'ORACLE_HOME' in os.environ:
            oracle_home = os.environ['ORACLE_HOME']
        else:
            msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
            module.fail_json(msg=msg, changed=False)
    else:
        rac = False

    if state == 'present':
        if not check_diskgroup_exists(cursor, module, msg, name):
            if create_diskgroup(
                cursor,
                module,
                msg,
                oracle_home,
                name,
                disks,
                redundancy,
                attribute_name,
                attribute_value,
            ):
                msg = 'Successfully created diskgroup %s ' % (name)
                module.exit_json(msg=msg, changed=True)
            else:
                msg = 'say what?!'
                module.fail_json(msg=msg, changed=False)
        else:
            ensure_diskgroup_state(
                cursor, module, msg, name, state, disks, attribute_name, attribute_value
            )

    elif state == 'absent':
        if check_diskgroup_exists(cursor, module, msg, name):
            if remove_diskgroup(cursor, module, msg, oracle_home, name):
                msg = 'Diskgroup %s successfully removed' % (name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.exit_json(msg=msg, changed=False)
        else:
            msg = 'Diskgroup %s doesn\'t exist' % (name)
            module.exit_json(msg=msg, changed=False)

    elif state == 'status':
        if check_diskgroup_exists(cursor, module, msg, name):
            result = get_current_disks(cursor, module, msg, name)
            # msg = 'Diskgroup %s successfully removed' % (name)
            module.exit_json(msg=result, changed=False)
        else:
            module.exit_json(msg=msg, changed=False)

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
