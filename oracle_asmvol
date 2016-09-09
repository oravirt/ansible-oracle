#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_asmvol
short_description: Manage Oracle ASMCMD Volumes
description:
    - Manage Oracle advm Volumes
version_added: "2.1.0.0"
options:
    name:
        description:
            - The name of the volume
        required: True
        default: None
    size:
        description:
            - The size of the volume
        default: None
    column:
        description:
            - Number of columns in a stripe set
        required: False
    width:
        description:
            - Stripe width of a volume
        required: False
    diskgroup:
        description:
            - The diskgroup in which to create the volume
        required: True
        default: None
        aliases: ['dg']
    state:
        description:
            - The state of the volume.
        default: present
        choices: ['present','absent', 'status']
    oracle_sid:
        description:
            - The name of the ASM instance
        default: +ASM
        aliases: ['sid']
    oracle_home:
        description:
            - The GI ORACLE_HOME
        required: false
        default: None
        aliases: ['oh']

notes:

author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''
# Create an ASM volume
oracle_asmvol: name=acfsvol dg=acfsdg size=100G state=present oh=/u01/app/grid/12.1.0.2/grid sid='+ASM1'

# Delete an ASM volume
oracle_asmvol: name=acfsvol dg=acfsdg state=absent oh=/u01/app/grid/12.1.0.2/grid sid='+ASM1'

'''
import os



# Check if the volume exists
def check_vol_exists(module, msg, oracle_home, diskgroup, name):

    command = '%s/bin/asmcmd volinfo -G %s %s' % (oracle_home, diskgroup, name)
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg[0] = 'Error, stdout: %s, stderr: %s, command is %s' % (stdout, stderr, command)
        return False


    if 'not found' in stdout:
        return False
    else:
        return True


def create_vol(module, msg, oracle_home, diskgroup, column, width, redundancy, name, size):

    command = '%s/bin/asmcmd volcreate %s -G %s -s %s ' % (oracle_home, name, diskgroup, size)

    if column is not None:
        command += ' --column %s' % (column)
    if width is not None:
        command += ' --width %s' % (width)
    if redundancy is not None:
        command += ' --redundancy %s' % (redundancy)

    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg[0] = 'Error, stdout: %s, stderr: %s, command is %s' % (stdout, stderr, command)
        return False
    else:
        return True #<-- all is well

def remove_vol(module, msg, oracle_home, diskgroup, name):

    command = '%s/bin/asmcmd voldelete %s -G %s ' % (oracle_home, name, diskgroup)

    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg[0] = 'Error, stdout: %s, stderr: %s, command is %s' % (stdout, stderr, command)
        return False
    else:
        return True #<-- all is well

def main():

    msg = ['']

    module = AnsibleModule(
        argument_spec = dict(
            name                = dict(required=True, aliases = ['volume_name']),
            diskgroup           = dict(required=True, aliases = ['dg']),
            size                = dict(required=False),
            column              = dict(default=None),
            width               = dict(default=None),
            redundancy          = dict(default=None),
            state               = dict(default="present", choices = ["present", "absent"]),
            oracle_home         = dict(default=None, aliases = ['oh']),
            oracle_sid          = dict(default='+ASM', aliases= ['sid']),
        ),

    )

    name                = module.params["name"]
    diskgroup           = module.params["diskgroup"]
    size                = module.params["size"]
    column              = module.params["column"]
    width               = module.params["width"]
    redundancy          = module.params["redundancy"]
    state               = module.params["state"]
    oracle_home         = module.params["oracle_home"]
    oracle_sid          = module.params["oracle_sid"]


    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']
    else:
        msg[0] = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg[0], changed=False)

    if oracle_sid != '+ASM':
        os.environ['ORACLE_SID'] = oracle_sid
    elif 'ORACLE_SID' in os.environ:
        oracle_sid = os.environ['ORACLE_SID']

    if state == 'present' and not size:
        msg[0] = 'Missing argument: size. Please add and re-run the command'
        module.fail_json(msg=msg[0], changed=False)

    if state == 'present':
        if not check_vol_exists(module, msg, oracle_home, diskgroup, name):
            if create_vol(module, msg, oracle_home, diskgroup, column, width, redundancy, name, size):
                msg[0] = 'Volume %s successfully created' % (name)
                module.exit_json(msg=msg[0], changed=True)
            else:
                module.fail_json(msg=msg[0], changed=False)
        else:
            msg[0] = 'Volume %s already exists' % (name)
            module.exit_json(msgt=msg[0], changed=False)

    elif state == 'absent' :
        if check_vol_exists(module, msg, oracle_home, diskgroup, name):
            if remove_vol(module, msg, oracle_home, diskgroup, name):
                msg[0] = 'Volume %s successfully removed' % (name)
                module.exit_json(msg=msg[0], changed=True)
            else:
                module.fail_json(msg=msg[0], changed=False)
        else:
            msg[0] = 'Volume %s doesn\'t exist' % (name)
            module.exit_json(msg=msg[0], changed=False)



    module.exit_json(msg="Unhandled exit", changed=False)





from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
