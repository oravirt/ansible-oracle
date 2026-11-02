#!/usr/bin/python
# -*- coding: utf-8 -*-

# import os
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_asmvol
short_description: Manage Oracle ASM Dynamic Volumes (ADVM)
description:
    - Creates and drops ASM Dynamic Volumes (ADVM) in an ASM disk group.
    - The module connects to the ASM instance with C(SYSASM) privileges and runs
      C(ALTER DISKGROUP <diskgroup> ADD VOLUME <name> SIZE <size>) or
      C(ALTER DISKGROUP <diskgroup> DROP VOLUME <name>).
    - The existence of a volume is checked in C(V$ASM_VOLUME) joined with
      C(V$ASM_DISKGROUP) (case-insensitive).
    - The size of an existing volume is not changed.
    - If neither O(user) nor O(password) is given, a connection with an Oracle wallet
      (C(/@<service_name>)) is used. Otherwise both must be set.
version_added: "2.1.0"
options:
    name:
        description:
            - The name of the volume.
        type: str
        required: true
        aliases: ['volume_name']
    diskgroup:
        description:
            - The name of the disk group in which the volume is created or dropped.
        type: str
        required: true
        aliases: ['dg']
    size:
        description:
            - The size of the volume, for example V(100G).
            - The value is used as is in the C(SIZE) clause.
            - Required with O(state=present), although not enforced by the
              argument spec.
        type: str
        required: false
    column:
        description:
            - Number of columns in a stripe set.
            - Currently not used by the module.
        type: str
        required: false
    width:
        description:
            - Stripe width of the volume.
            - Currently not used by the module.
        type: str
        required: false
    redundancy:
        description:
            - Redundancy of the volume.
            - Currently not used by the module.
        type: str
        required: false
    state:
        description:
            - V(present) - the volume is created if it does not exist.
            - V(absent) - the volume is dropped if it exists.
        type: str
        required: false
        default: present
        choices: ['present', 'absent']
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
            - Currently not used by the module.
        type: str
        required: false
        aliases: ['oh']
notes:
    - cx_Oracle needs to be installed
requirements: [ "cx_Oracle" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Create an ASM volume
  opitzconsulting.ansible_oracle.oracle_asmvol:
    name: acfsvol
    diskgroup: acfsdg
    size: 100G
    state: present
    user: sys
    password: "{{ asm_password }}"

- name: Drop an ASM volume (connection with Oracle wallet)
  opitzconsulting.ansible_oracle.oracle_asmvol:
    name: acfsvol
    diskgroup: acfsdg
    state: absent
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
        - Not returned when the volume already exists with O(state=present)
          (the message is returned in RV(msgt) instead).
    returned: when a volume was created or dropped, or does not exist
    type: str
    sample: "Volume ACFSVOL successfully created. Size: 100G "
msgt:
    description:
        - Message returned instead of RV(msg) when the volume already exists.
    returned: when O(state=present) and the volume already exists
    type: str
    sample: "Volume ACFSVOL already exists"
'''

try:
    import cx_Oracle
except ImportError:
    cx_oracle_exists = False
else:
    cx_oracle_exists = True


# Check if the volume exists
def check_vol_exists(cursor, module, msg, diskgroup, name):
    sql = '''
          select count (*)
          from v$asm_volume v,v$asm_diskgroup g
          where v.group_number = g.group_number
          and lower (g.name) = \'%s\'
          and lower (v.volume_name) = \'%s\'
          ''' % (
        diskgroup.lower(),
        name.lower(),
    )
    result = execute_sql_get(module, msg, cursor, sql)
    # msg = 'Normal Result is: %s, [0] is: %s, [0][0] is: %s, len is: %s, type is: %s'
    # % (result,result[0],result[0][0],len(result), type(result))
    # module.exit_json(msg=msg)
    if result[0][0] > 0:
        return True
    else:
        return False
    # command = '%s/bin/asmcmd volinfo -G %s %s' % (oracle_home, diskgroup, name)
    # (rc, stdout, stderr) = module.run_command(command)
    # if rc != 0:
    #     msg = 'Error, stdout: %s, stderr: %s, command is %s'
    #       % (stdout, stderr, command)
    #     module.fail_json(msg=msg, changed=False)
    #
    #
    # if 'not found' in stdout:
    #     return False
    # else:
    #     return True


def create_vol(cursor, module, msg, diskgroup, name, size):
    sql = 'alter diskgroup %s ' % (diskgroup)
    sql += 'add volume %s ' % (name)
    sql += 'size %s ' % (size)

    if execute_sql(module, msg, cursor, sql):
        return True
    else:
        msg = 'error in exec sql create'
        module.fail_json(msg=msg, changed=False)

    # command = '%s/bin/asmcmd volcreate %s -G %s -s %s '
    #   % (oracle_home, name, diskgroup, size)
    #
    # if column is not None:
    #     command += ' --column %s' % (column)
    # if width is not None:
    #     command += ' --width %s' % (width)
    # if redundancy is not None:
    #     command += ' --redundancy %s' % (redundancy)
    #
    # (rc, stdout, stderr) = module.run_command(command)
    # if rc != 0:
    #     msg = 'Error, STDOUT: %s, STDERR: %s, command is: %s'
    #         % (stdout, stderr, command)
    #     module.fail_json(msg=msg, changed=False)
    # else:
    #     return True #<-- all is well


def remove_vol(cursor, module, msg, diskgroup, name):
    sql = 'alter diskgroup %s ' % (diskgroup)
    sql += 'drop volume %s ' % (name)

    if execute_sql(module, msg, cursor, sql):
        return True
    else:
        msg = 'error in exec sql remove'
        module.fail_json(msg=msg, changed=False)


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

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['volume_name']),
            diskgroup=dict(required=True, aliases=['dg']),
            size=dict(required=False),
            column=dict(default=None),
            width=dict(default=None),
            redundancy=dict(default=None),
            state=dict(default="present", choices=["present", "absent"]),
            user=dict(required=False, aliases=['un', 'username']),
            password=dict(required=False, no_log=True, aliases=['pw']),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            port=dict(required=False, default=1521),
            service_name=dict(required=False, default='+ASM', aliases=['sn']),
            oracle_home=dict(required=False, aliases=['oh']),
        ),
    )

    name = module.params["name"]
    diskgroup = module.params["diskgroup"]
    size = module.params["size"]
    # column = module.params["column"]
    # width = module.params["width"]
    # redundancy = module.params["redundancy"]
    state = module.params["state"]
    user = module.params["user"]
    password = module.params["password"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    service_name = module.params["service_name"]
    # oracle_home = module.params["oracle_home"]

    # if oracle_home is not None:
    #     os.environ['ORACLE_HOME'] = oracle_home
    # elif 'ORACLE_HOME' in os.environ:
    #     oracle_home = os.environ['ORACLE_HOME']
    # else:
    #     msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
    #     module.fail_json(msg=msg, changed=False)

    # if oracle_sid != '+ASM':
    #     os.environ['ORACLE_SID'] = oracle_sid
    # elif 'ORACLE_SID' in os.environ:
    #     oracle_sid = os.environ['ORACLE_SID']

    if not cx_oracle_exists:
        msg = (
            "The cx_Oracle module is required. "
            "'pip install cx_Oracle' should do the trick. "
            "If cx_Oracle is installed, make sure ORACLE_HOME & LD_LIBRARY_PATH is set"
        )
        module.fail_json(msg=msg)

    wallet_connect = '/@%s' % service_name
    try:
        if not user and not password:
            # If neither user or password is supplied,
            # the use of an oracle wallet is assumed
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

    if state == 'present' and not size:
        msg = 'Missing argument: size. Please add and re-run the command'
        module.fail_json(msg=msg, changed=False)

    if state == 'present':
        if not check_vol_exists(cursor, module, msg, diskgroup, name):
            if create_vol(cursor, module, msg, diskgroup, name, size):
                msg = 'Volume %s successfully created. Size: %s ' % (name.upper(), size)
                module.exit_json(msg=msg, changed=True)
        else:
            msg = 'Volume %s already exists' % (name.upper())
            module.exit_json(msgt=msg, changed=False)

    elif state == 'absent':
        if check_vol_exists(cursor, module, msg, diskgroup, name):
            if remove_vol(cursor, module, msg, diskgroup, name):
                msg = 'Volume %s successfully removed' % (name.upper())
                module.exit_json(msg=msg, changed=True)
        else:
            msg = 'Volume %s doesn\'t exist' % (name.upper())
            module.exit_json(msg=msg, changed=False)

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
