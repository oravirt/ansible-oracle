#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.parsing.convert_bool import boolean
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_asmdg
short_description: Manage ASM disk groups
description:
    - Creates, changes and drops ASM disk groups and shows their disks.
    - The module connects to the ASM instance with C(SYSASM) privileges.
    - The existence of a disk group is checked in C(GV$ASM_DISKGROUP)
      (case-insensitive).
    - A new disk group is created with C(CREATE DISKGROUP <name> <redundancy>
      REDUNDANCY [[QUORUM] FAILGROUP <failgroup>] DISK ... [ATTRIBUTE ...]).
    - For an existing disk group with O(state=present), the disks and attributes
      are compared with the wanted state. Missing disks are added and disks not
      listed in O(disks) are dropped with C(ALTER DISKGROUP ... ADD [[QUORUM]
      FAILGROUP ...] DISK ... DROP DISK ...), differing attributes are set with
      C(ALTER DISKGROUP ... SET ATTRIBUTE). Read-only attributes are ignored.
      O(redundancy) is not changed.
    - The failure group of an existing disk can't be changed. If it differs from
      O(disks), the module returns a warning and does not change the disk.
    - In a RAC environment (C(V$INSTANCE.PARALLEL=YES)), a new disk group is
      started on all nodes with C(srvctl start diskgroup), and before dropping a
      disk group it is stopped with C(srvctl stop diskgroup) and mounted locally.
      This needs O(oracle_home) or the environment variable E(ORACLE_HOME).
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "2.1.0"
options:
    name:
        description:
            - The name of the disk group.
        type: str
        required: true
        aliases: ['diskgroup', 'dg']
    disks:
        description:
            - The list of disks that should be part of the disk group.
            - An entry is the path of the disk, or a dictionary with the keys
              C(disk) (path, required), C(failure_group) (name of the failure
              group) and C(quorum) (V(true) for a quorum failure group, default
              V(false)).
            - Disks with the same C(failure_group) are put into the same failure
              group. C(quorum) must be the same for all disks of a failure group.
              Disks without C(failure_group) get their own failure group from ASM.
            - The failure group is used when a disk is added (create of the disk
              group or new disk).
            - Only the listed disks will be part of the disk group. Disks of an
              existing disk group that are not in the list are dropped.
            - Disk names containing C(:) (ASMLib, for example V(ORCL:DISK1)) are
              converted to uppercase, other paths are compared case-sensitive with
              C(V$ASM_DISK.PATH).
            - Required with O(state=present), although not enforced by the
              argument spec.
        type: list
        elements: raw
        required: false
    redundancy:
        description:
            - The redundancy of the disk group.
            - Used only when the disk group is created. Use C(failure_group) in
              O(disks) to place disks in specific failure groups.
        type: str
        required: false
        default: external
        choices: ['external', 'normal', 'high', 'flex']
    attribute_name:
        description:
            - List of disk group attribute names, for example V(compatible.asm).
            - Each entry corresponds to the entry at the same position in
              O(attribute_value).
            - Names and values are converted to lowercase.
        type: list
        elements: str
        required: false
        aliases: ['an']
    attribute_value:
        description:
            - List of disk group attribute values, for example V(19.0.0.0).
            - Must have the same number of entries as O(attribute_name).
            - Attributes are only compared for an existing disk group when both
              O(attribute_name) and O(attribute_value) are set. If any attribute
              differs, all listed attributes are set again. C(compatible.asm) is
              set first, because C(compatible.rdbms) and C(compatible.advm) can't
              be higher than C(compatible.asm).
        type: list
        elements: str
        required: false
        aliases: ['av']
    state:
        description:
            - V(present) - the disk group is created, or its disks and attributes
              are changed to the wanted state.
            - V(absent) - the disk group is dropped (C(DROP DISKGROUP) without
              C(INCLUDING CONTENTS)).
            - V(status) - returns the disks of the disk group in RV(msg). Nothing
              is changed.
        type: str
        required: false
        default: present
        choices: ['present', 'absent', 'status']
    user:
        description:
            - The user name to connect to the ASM instance (as C(SYSASM)).
            - Omit O(user) and O(password) to connect with an Oracle wallet.
        type: str
        required: false
        aliases: ['un', 'username']
    password:
        description:
            - The password for O(user).
        type: str
        required: false
        aliases: ['pw']
    hostname:
        description:
            - The host of the ASM instance.
            - Ignored when connecting with an Oracle wallet.
        type: str
        required: false
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port number on the host.
            - Ignored when connecting with an Oracle wallet.
        type: int
        required: false
        default: 1521
    service_name:
        description:
            - The service name of the ASM instance.
            - When connecting with an Oracle wallet, this is the TNS alias of the
              wallet entry.
        type: str
        required: false
        default: '+ASM'
        aliases: ['sn']
    oracle_home:
        description:
            - The Grid Infrastructure C(ORACLE_HOME).
            - Only used in a RAC environment to call C(srvctl). If not set, the
              environment variable E(ORACLE_HOME) is used.
        type: str
        required: false
        aliases: ['oh']
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
- name: Create disk group MYDG1 with ASMLib disks
  opitzconsulting.ansible_oracle.oracle_asmdg:
    name: MYDG1
    disks:
      - ORCL:MYDG1
      - ORCL:MYDG2
    attribute_name: compatible.asm
    attribute_value: 12.1.0.2
    redundancy: external
    state: present
    user: sys
    password: "{{ asm_password }}"
    service_name: '+ASM'
    hostname: localhost
    oracle_home: /u01/app/oracle/12.1.0.2/grid

- name: Create disk group DATA with several attributes
  opitzconsulting.ansible_oracle.oracle_asmdg:
    name: DATA
    disks:
      - /dev/oracle/data1
      - /dev/oracle/data2
    attribute_name:
      - compatible.asm
      - compatible.rdbms
    attribute_value:
      - 19.0.0.0
      - 19.0.0.0
    redundancy: external
    state: present
    user: sys
    password: "{{ asm_password }}"
    oracle_home: /u01/app/19.0.0/grid

- name: Create disk group CRS with failure groups and a quorum failure group
  opitzconsulting.ansible_oracle.oracle_asmdg:
    name: CRS
    disks:
      - {disk: /dev/oracle/crs01, failure_group: storage01}
      - {disk: /dev/oracle/crs02, failure_group: storage02}
      - {disk: /nfs/vote/crs03, failure_group: nfs, quorum: true}
    redundancy: normal
    state: present
    user: sys
    password: "{{ asm_password }}"

- name: Show the disks of disk group DATA (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_asmdg:
    name: DATA
    state: status

- name: Drop disk group MYDG1
  opitzconsulting.ansible_oracle.oracle_asmdg:
    name: MYDG1
    state: absent
    user: sys
    password: "{{ asm_password }}"
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
        - With O(state=status) and an existing disk group, a list of
          C([path, name]) entries of the disks (from C(V$ASM_DISK)) is returned
          instead of a string.
    returned: always
    type: raw
    sample: "Diskgroup DATA has been put in the intended state"
'''


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
    add_attr = bool(attribute_name) and bool(attribute_value)

    if add_attr:
        attributes = ','.join(
            [
                '\'' + str(n) + '\'' + '=' + '\'' + str(v) + '\''
                for n, v in zip(attribute_name, attribute_value)
            ]
        )

    sql = 'create diskgroup %s ' % (name)
    sql += '%s redundancy ' % (redundancy)
    sql += '%s ' % get_disk_clause(disks)
    if add_attr:
        sql += ' attribute %s' % (attributes.lower())

    if execute_sql(module, msg, cursor, sql):
        if rac:
            command = '%s/bin/srvctl start diskgroup -g %s' % (
                oracle_home,
                name.lower(),
            )
            rc, stdout, stderr = module.run_command(command)
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
        rc, stdout, stderr = module.run_command(command)
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

        # Make sure properties are lower case, values can be numbers in YAML
        attribute_name = [str(x).lower() for x in attribute_name]
        attribute_value = [str(y).lower() for y in attribute_value]
        wanted_attributes = zip(attribute_name, attribute_value)

        # Zip object type apparently changed from list (python2) to iterator (python3)
        # We convert it to list because otherwise we'd loose it's content with the first
        # iteration
        if not isinstance(wanted_attributes, list):
            wanted_attributes = list(wanted_attributes)

        # Make sure we don't try to modify read only attributes. Removing them
        # from the wanted_attributes list (a new list, removing elements while
        # iterating over the list skips the next element)
        wanted_attributes = [
            a for a in wanted_attributes if a[0] not in read_only_attributes
        ]

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
            if sorted(current_properties) != sorted(wanted_attributes):
                change_attr = True
                # compatible.rdbms and compatible.advm can't be higher than
                # compatible.asm => set compatible.asm first
                for i in sorted(
                    wanted_attributes, key=lambda a: a[0] != 'compatible.asm'
                ):
                    total_sql.append(
                        "alter diskgroup %s set attribute '%s'='%s'"
                        % (name, i[0], i[1])
                    )

    list_current_name = []
    list_current_path = []
    list_wanted = [d['disk'] for d in disks]
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

    warn_failgroup_changes(cursor, module, msg, name, disks)

    remove_disk = "','".join(remove_disks)
    if sorted(list_current_path) == sorted(list_wanted) and change_attr is False:
        msg = "Diskgroup %s is in the intended state" % (name)
        module.exit_json(msg=msg, changed=False)

    if len(list_add) >= 1:
        change_disk = True
        disk_sql += ' add %s' % get_disk_clause(
            [d for d in disks if d['disk'] in list_add]
        )

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


# disks as list of dict with disk, failure_group and quorum
def normalize_disks(module, disks):
    result = []
    quorum_of_failgroup = {}
    for d in disks:
        if isinstance(d, dict):
            unknown = set(d) - set(['disk', 'failure_group', 'quorum'])
            if unknown or not d.get('disk'):
                module.fail_json(
                    msg='Invalid entry in disks: %s. Use a path or a dictionary '
                    'with the keys disk, failure_group and quorum' % d,
                    changed=False,
                )
            disk = str(d['disk'])
            failgroup = d.get('failure_group')
            failgroup = str(failgroup).upper() if failgroup else None
            quorum = boolean(d.get('quorum', False))
        else:
            disk, failgroup, quorum = str(d), None, False

        if failgroup:
            if quorum_of_failgroup.setdefault(failgroup, quorum) != quorum:
                module.fail_json(
                    msg='quorum must be the same for all disks of failure group %s'
                    % failgroup,
                    changed=False,
                )

        result.append(
            {
                'disk': disk.upper() if ':' in disk else disk,
                'failure_group': failgroup,
                'quorum': quorum,
            }
        )
    return result


# [QUORUM] [FAILGROUP <failgroup>] DISK '<path>',... for create and add disk
def get_disk_clause(disks):
    # disks without failure group are grouped by quorum
    groups = []
    for d in disks:
        for g in groups:
            if (g['failure_group'], g['quorum']) == (d['failure_group'], d['quorum']):
                g['disks'].append(d['disk'])
                break
        else:
            groups.append(dict(d, disks=[d['disk']]))

    clause = []
    for g in groups:
        sql = 'quorum ' if g['quorum'] else ''
        if g['failure_group']:
            sql += 'failgroup %s ' % g['failure_group']
        sql += 'disk ' + ','.join("'%s'" % p for p in g['disks'])
        clause.append(sql)
    return ' '.join(clause)


# the failure group of an existing disk can't be changed
def warn_failgroup_changes(cursor, module, msg, name, disks):
    wanted = dict((d['disk'], d['failure_group']) for d in disks if d['failure_group'])
    if not wanted:
        return
    sql = 'select d.path, d.failgroup from v$asm_disk d, v$asm_diskgroup dg '
    sql += 'where dg.group_number = d.group_number '
    sql += 'and upper(dg.name) = \'%s\'' % (name.upper())
    for path, failgroup in execute_sql_get(module, msg, cursor, sql):
        if path in wanted and wanted[path] != failgroup:
            module.warn(
                'Disk %s is in failure group %s, not %s. The failure group of an '
                'existing disk is not changed.' % (path, failgroup, wanted[path])
            )


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
    sql += 'and a.read_only = \'N\' '
    sql += 'and upper(dg.name) = \'%s\' ' % (name.upper())
    sql += 'and a.name in (%s) ' % (attribute_names_.lower())

    result = execute_sql_get(module, msg, cursor, sql)
    return result


def execute_sql_get(module, msg, cursor, sql):
    # module.exit_json(msg="In execute_sql_get", changed=False)
    try:
        cursor.execute(sql)
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


def main():
    msg = ['']
    cursor = None
    global rac

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['diskgroup', 'dg']),
            disks=dict(required=False, type='list', elements='raw'),
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

    if disks:
        disks = normalize_disks(module, disks)

    if len(attribute_name or []) != len(attribute_value or []):
        module.fail_json(
            msg='attribute_name and attribute_value must have the same number '
            'of entries',
            changed=False,
        )

    # connects always as SYSASM
    conn = oracledb_connect(
        module, hostname, port, service_name, user, password, 'sysasm'
    )
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
