#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: oracle_opatch
short_description: Manage patches in an Oracle environment
    - Manages patches (applies/rolls back)
    - Only manages the opatch part of patching (opatch/opatch auto/opatchauto)
    - If opatchauto is true, the task has to be run as root
version_added: "2.4.0.0"
options:
    oracle_home:
        description:
            - The home which will be patched
        required: True
        aliases: ['oh']
    patch_base:
        description:
            - Path to where the patch is located
              e.g /nfs/patches/12.1.0.2/27468957
        required: False
        default: None
        aliases: ['path','source','patch_source','phBaseDir']
    patch_id:
        description:
            - The patch id
              e.g 27468957
        required: False
        default: None
        aliases: ['id']
    patch_version:
        description:
            - The patch version
              e.g 12.2.0.1.180417
            - This key is mandatory if you're applying a 'opatchauto' type of patch
        required: False
        default: None
        aliases: ['version_added']
    opatch_minversion:
        description:
            - The minimum version of opatch needed
            - If this key is set, a comparison is made between existing version and opatch_minversion
              If existing < opatch_minversion an error is raised
        required: False
        default: None
        aliases: ['opmv']
    opatchauto:
        description:
            - Should the patch be applied using opatchato
            - If set to true, the task has to run as 'root'
        required: False
        default: False
        aliases: ['autopatch']
    conflict_check:
        description:
            - Should a conflict check be run before applying a patch.
            - If the check errors the module exits with a failure
        required: False
        default: True
    stop_processes:
        description:
            - Stop Instances and Listener before applying a patch in ORACLE_HOME
        required: False
        default: False
    rolling:
        description:
            - Should a patch installed in rolling upgrade mode?
        required: False
        default: True
    ocm_response_file:
        description:
            - The OCM responsefile needed for OPatch versions < '12.2.0.1.5' (basically for DB/GI versions < 12.1)
        required: False
        default: False
    state:
        description:
            - Should a patch be applied or removed
            - present = applied, absent = removed, opatchversion = returns the version of opatch
        default: present
        choices: ['present','absent','opatchversion']
    hostname:
        description:
            - The host of the database if using dbms_service
        required: false
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port to connect to the database if using dbms_service
        required: false
        default: 1521

notes:
    -
requirements: [ "os","pwd","distutils.version" ]
author: Mikael Sandström, oravirt@gmail.com, @oravirt
'''

EXAMPLES = '''

'''
import os, pwd
from distutils.version import LooseVersion
#
# try:
#     import cx_Oracle
# except ImportError:
#     cx_oracle_exists = False
# else:
#     cx_oracle_exists = True


def get_version(module, msg, oracle_home):
    '''
    Returns the DB server version
    '''

    command = '%s/bin/sqlplus -V' % (oracle_home)
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
        module.fail_json(msg=msg, changed=False)
    else:
        return stdout.split(' ')[2][0:4]

def get_opatch_version(module, msg, oracle_home):
    '''
    Returns the Opatch version
    '''

    command = '%s/OPatch/opatch version' % (oracle_home)
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
        module.fail_json(msg=msg, changed=False)
    else:
        return stdout.split('\n')[0].split(':')[1].strip()

def get_file_owner(module, msg, oracle_home):
    '''
    This will only be run if opatchauto is True.
    The owner of ORACLE_HOME has to be established, and we do this be checking file
    ownership on ORACLE_HOME/bin/oracle.
    returns the owner
    '''

    checkfile = '%s/bin/oracle' % (oracle_home)
    if os.path.exists(checkfile):
        stat_info = os.stat(checkfile)
        uid = stat_info.st_uid
        user = pwd.getpwuid(uid)[0]
        return user
    else:
        msg = 'Could not determine owner of %s ' % (checkfile)
        module.fail_json(msg=msg)

def check_patch_applied(module, msg, oracle_home, patch_id, patch_version, opatchauto):
    '''
    Gets all patches already applied and compares to the
    intended patch
    '''

    command = ''
    if opatchauto:
        oh_owner = get_file_owner(module,msg,oracle_home)
        command += 'sudo -u %s ' % (oh_owner)
    command += '%s/OPatch/opatch lspatches ' % (oracle_home)
    (rc, stdout, stderr) = module.run_command(command)
    #module.exit_json(msg=stdout, changed=False)
    if rc != 0:
      msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
      module.fail_json(msg=msg, changed=False)
    else:
        if opatchauto:
            chk = '%s' % (patch_version)
        elif not opatchauto and patch_id is not None and patch_version is not None:
            chk = '%s (%s)' % (patch_version,patch_id)
        else:
            chk = '%s' % (patch_id)

        if chk in stdout:
            return True
        else:
            return False

def analyze_patch (module, msg, oracle_home, patch_base, opatchauto):

    checks = []

    if opatchauto:
        if major_version < '12.1':
            oh_owner = get_file_owner(module,msg,oracle_home)
            command = ''
            command += 'sudo -u %s ' % (oh_owner)
            opatch_cmd = 'opatch '
            conflcommand = '%s %s/OPatch/opatch prereq CheckConflictAgainstOHWithDetail -ph %s -oh %s' % (command,oracle_home, patch_base, oracle_home)
            spacecommand = '%s %s/OPatch/opatch prereq CheckSystemSpace -ph %s -oh %s' % (command,oracle_home, patch_base, oracle_home)
            checks.append(conflcommand)
            checks.append(spacecommand)

        else:
            opatch_cmd = 'opatchauto'
            command = '%s/OPatch/%s apply %s -oh %s -analyze' % (oracle_home, opatch_cmd, patch_base, oracle_home)
            checks.append(command)
    else:
        conflcommand = '%s/OPatch/opatch prereq CheckConflictAgainstOHWithDetail -ph %s -oh %s' % (oracle_home, patch_base, oracle_home)
        spacecommand = '%s/OPatch/opatch prereq CheckSystemSpace -ph %s -oh %s' % (oracle_home, patch_base, oracle_home)
        checks.append(conflcommand)
        checks.append(spacecommand)

    for cmd in checks:
        (rc, stdout, stderr) = module.run_command(cmd)
        # module.exit_json(msg=stdout, changed=False)
        if rc != 0:
            msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, cmd)
            module.fail_json(msg=msg, changed=False)
        elif rc == 0 and 'failed' in stdout: # <- Conflicts exist
            msg = 'STDOUT: %s, COMMAND: %s' % (stdout,cmd)
            module.fail_json(msg=msg, changed=False)
        else:
            return True

def apply_patch (module, msg, oracle_home, patch_base, patch_id, patch_version, opatchauto, ocm_response_file, offline, stop_processes, rolling, output):
    '''
    Applies the patch
    '''

    if conflict_check:
        if not analyze_patch(module, msg, oracle_home, patch_base, opatchauto):
            module.fail_json(msg='Prereq checks failed')

    if opatchauto:
        opoptions = ''
        if major_version < '12.1':
            opatch_cmd = 'opatch auto'
            if offline:
                oh = ' -och'
            else:
                oh = ' -oh'
        else:
            oh = ' -oh'
            opatch_cmd = 'opatchauto apply'

            if not rolling:
                opoptions += ' -nonrolling '

        command = '%s/OPatch/%s %s %s %s %s' % (oracle_home,opatch_cmd, opoptions, patch_base,oh,oracle_home)

    else:
        if stop_processes:
            stop_process(module, oracle_home)

        opatch_cmd = 'opatch'
        command = '%s/OPatch/%s apply %s -oh %s -silent' % (oracle_home,opatch_cmd, patch_base,oracle_home)

    if ocm_response_file is not None and (LooseVersion(opatch_version) < LooseVersion(opatch_version_noocm)):
        command += ' -ocmrf %s' % (ocm_response_file)

    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
      msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
      module.fail_json(msg=msg, changed=False)
    elif rc == 0 and 'Opatch version check failed' in stdout: # OPatch version check failed
        msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
        module.fail_json(msg=msg, changed=False)
    else:
        checks = ['successfully applied' in stdout,
                 'patch applied successfully' in stdout,
                 'apply successful' in stdout]
        if any(checks):
            if output == 'short':
                return True
            else:
                msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
                module.exit_json(msg=msg, changed=True)
        else:
            msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
            module.exit_json(msg=msg, changed=False)

def stop_process(module, oracle_home):
    '''
    Stop processes in ORACLE_HOME for non GI/Restart Environments
    '''

    oratabfile = '/etc/oratab'

    if os.path.exists(oratabfile):
        with open(oratabfile) as oratab:

           msg = ''

           for line in oratab:
               if line.startswith('#') or line.startswith(' '):
                   continue
               elif len(line.split(':')) >= 2 and line.split(':')[1] == oracle_home:

                   # Find listener for ORACLE_HOME
                   p = subprocess.Popen('ps -o cmd -C tnslsnr | grep "^%s/bin/tnslsnr "' % (line) , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                   output, error = p.communicate()
                   p_status = p.wait()

                   if output:
                       for lline in output.split('\n'):

                           proclen = len("%s/bin/tnslsnr " % (oracle_home))

                           # remove executable from ps output, split by ' '
                           # => 1st element is listener_name
                           # ps example: /.../bin/tnslsnr LISTENER -inherit
                           listener_name = lline[proclen:].split(' ')[0]
                           if len(listener_name) > 0:
                               lsnrctl_bin = '%s/bin/lsnrctl' % (oracle_home)
                               try:
                                   p = subprocess.check_call([lsnrctl_bin, 'stop', '%s' % listener_name])
                               except subprocess.CalledProcessError:
                                   msg += 'Stop of Listener %s failed ' % listener_name
               
                   # Stop instances in ORACLE_HOME
                   # The [0-9] is used to remove the grep itself from the result!
                   p = subprocess.Popen('ps -elf| grep "[0-9] ora_pmon_%s"' % (line.split(':')[0]) , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                   output, error = p.communicate()
                   p_status = p.wait()

                   if output and p.returncode == 0:
                       os.environ['ORACLE_SID'] = line.split(':')[0]
                       shutdown_sql = '''connect / as sysdba
                                         shutdown immediate;
                                         exit'''
                       sqlplus_bin = '%s/bin/sqlplus' % (oracle_home)
                       p = subprocess.Popen([sqlplus_bin,'/nolog'],stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                       (stdout,stderr) = p.communicate(shutdown_sql.encode('utf-8'))
                       p_status = p.wait()
                       #module.fail_json(msg=stdout, changed=False)

                       rc = p.returncode
                       if rc != 0:
                           msg += 'Stop of Instance %s failed' % line.split(':')[0]

                   if msg:
                       module.fail_json(msg=msg, changed=False)

def remove_patch (module, msg, oracle_home, patch_base, patch_id, opatchauto, ocm_response_file,output):
    '''
    Removes the patch
    '''

    if opatchauto:
        if major_version < '12.1':
            opatch_cmd = 'opatch auto -rollback'
        else:
            opatch_cmd = 'opatchauto rollback'

        command = '%s/OPatch/%s %s -oh %s ' % (oracle_home,opatch_cmd, patch_base, oracle_home)
    else:
        opatch_cmd = 'opatch rollback'
        command = '%s/OPatch/%s -id %s -silent' % (oracle_home,opatch_cmd, patch_id)


    if ocm_response_file is not None and (LooseVersion(opatch_version) < LooseVersion(opatch_version_noocm)):
        command += ' -ocmrf %s' % (ocm_response_file)

    #module.exit_json(msg=command, changed=False)
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
      msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
      module.fail_json(msg=msg, changed=False)
    else:
        checks = ['RollbackSession removing interim patch' in stdout,
                 'rolled back successfully' in stdout,
                 'rollback successful' in stdout]
        if any(checks):
            if output == 'short':
                return True
            else:
                msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
                module.exit_json(msg=msg, changed=True)
        else:
            msg = 'STDOUT: %s, COMMAND: %s' % (stdout,command)
            module.exit_json(msg=msg, changed=False)


#
# def execute_sql_get(module, msg, cursor, sql):
#
#     try:
#         cursor.execute(sql)
#         result = (cursor.fetchall())
#     except cx_Oracle.DatabaseError as exc:
#         error, = exc.args
#         msg = 'Something went wrong while executing sql_get - %s sql: %s' % (error.message, sql)
#         module.fail_json(msg=msg, changed=False)
#         return False
#     return result
#
# def execute_sql(module, msg, cursor, sql):
#
#     try:
#         cursor.execute(sql)
#     except cx_Oracle.DatabaseError as exc:
#         error, = exc.args
#         msg = 'Something went wrong while executing sql - %s sql: %s' % (error.message, sql)
#         module.fail_json(msg=msg, changed=False)
#         return False
#     return True
#
# def getconn(module,msg):
#
#     hostname = os.uname()[1]
#     wallet_connect = '/@%s' % service_name
#     try:
#         if (not user and not password ): # If neither user or password is supplied, the use of an oracle wallet is assumed
#             connect = wallet_connect
#             conn = cx_Oracle.connect(wallet_connect, mode=cx_Oracle.SYSDBA)
#         elif (user and password ):
#             dsn = cx_Oracle.makedsn(host=hostname, port=port, service_name=service_name, )
#             connect = dsn
#             conn = cx_Oracle.connect(user, password, dsn, mode=cx_Oracle.SYSDBA)
#         elif (not(user) or not(password)):
#             module.fail_json(msg='Missing username or password for cx_Oracle')
#
#     except cx_Oracle.DatabaseError as exc:
#             error, = exc.args
#             msg = 'Could not connect to database - %s, connect descriptor: %s' % (error.message, connect)
#             module.fail_json(msg=msg, changed=False)
#
#     cursor = conn.cursor()
#     return cursor



def main():

    msg = ['']
    cursor = None
    global major_version
    global opatch_version
    global opatch_version_noocm
    global hostname
    global port
    global conflict_check

    module = AnsibleModule(
        argument_spec = dict(
            oracle_home         = dict(required=True, aliases = ['oh']),
            patch_base          = dict(default=None, aliases = ['path','source','patch_source','phBaseDir']),
            patch_id            = dict(default=None, aliases = ['id']),
            patch_version       = dict(required=None, aliases = ['version']),
            opatch_minversion   = dict(default=None, aliases = ['opmv']),
            opatchauto          = dict(default='False', type='bool',aliases = ['autopatch']),
            rolling             = dict(default='True', type='bool',aliases = ['rolling']),
            conflict_check      = dict(default='True', type='bool'),
            ocm_response_file   = dict(required=None,aliases = ['ocmrf']),
            offline             = dict(default='False', type='bool'),
#            stop_processes      = dict(default='True', type='bool'),
            stop_processes      = dict(default='False', type='bool'),
            output              = dict(default="short", choices = ["short","verbose"]),
            state               = dict(default="present", choices = ["present", "absent", "opatchversion"]),
            hostname            = dict(required=False, default = 'localhost', aliases = ['host']),
            port                = dict(required=False, default = 1521),



        ),

    )

    oracle_home         = module.params["oracle_home"]
    patch_base          = module.params["patch_base"]
    patch_id            = module.params["patch_id"]
    patch_version       = module.params["patch_version"]
    opatch_minversion   = module.params["opatch_minversion"]
    opatchauto          = module.params["opatchauto"]
    rolling             = module.params["rolling"]
    conflict_check      = module.params["conflict_check"]
    ocm_response_file   = module.params["ocm_response_file"]
    offline             = module.params["offline"]
    stop_processes      = module.params["stop_processes"]
    output              = module.params["output"]
    state               = module.params["state"]
    hostname            = module.params["hostname"]
    port                = module.params["port"]


    if not os.path.exists(oracle_home):
        msg = 'oracle_home: %s doesn\'t exist' % (oracle_home)
        module.fail_json(msg=msg, changed=False)

    if not os.path.exists('%s/OPatch/opatch' % (oracle_home)):
        msg = 'OPatch doesn\'t seem to exist in %s/OPatch/' % (oracle_home)
        module.fail_json(msg=msg, changed=False)

    if (patch_base or patch_id) is None and state in ('present','absent'):
        msg = 'patch_base & patch_id needs to be set'
        module.fail_json(msg=msg, changed=False)

    if opatchauto:
        if patch_version is None:
            msg = 'patch_version (e.g 12.1.0.2.1801417) needs to be set if opatchauto is True'
            module.fail_json(msg=msg, changed=False)

    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
        #os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home     = os.environ['ORACLE_HOME']
        #ld_library_path = os.environ['LD_LIBRARY_PATH']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg, changed=False)


    # Get the Oracle % Opatch version
    major_version = get_version(module,msg,oracle_home)
    opatch_version = get_opatch_version(module,msg,oracle_home)
    opatch_version_noocm = '12.2.0.1.5'

    if opatch_minversion is not None:
        opatch_minversion_ = opatch_minversion.replace('.','')
        if LooseVersion(opatch_version) < LooseVersion(opatch_minversion):
            msg = 'Current OPatch version: %s, minimum version needed is: %s' % (opatch_version,opatch_minversion)
            module.fail_json(msg=msg, changed=False)

    if state == 'present' and ocm_response_file is None and LooseVersion(opatch_version) < LooseVersion(opatch_version_noocm):
        msg='An OCM response file is needed when the opatch version is < %s. Current opatch version: %s' % (opatch_version_noocm,opatch_version)
        module.fail_json(msg=msg,changed=False)

    if state == 'opatchversion':
        module.exit_json(msg=opatch_version,changed=False)

    if state == 'present':
        if not check_patch_applied(module, msg, oracle_home, patch_id, patch_version, opatchauto):
            if apply_patch(module, msg, oracle_home, patch_base, patch_id,patch_version, opatchauto,ocm_response_file,offline,stop_processes,rolling,output):
                if patch_version is not None:
                    msg = 'Patch %s (%s) successfully applied to %s' % (patch_id,patch_version, oracle_home)
                else:
                    msg = 'Patch %s successfully applied to %s' % (patch_id, oracle_home)
                module.exit_json(msg=msg, changed=True)

        else:
            if patch_version is not None:
                msg = 'Patch %s (%s) is already applied to %s' % (patch_id,patch_version, oracle_home)
            else:
                msg = 'Patch %s is already applied to %s' % (patch_id, oracle_home)
            module.exit_json(msg=msg, changed=False)

    elif state == 'absent':
        if check_patch_applied(module, msg, oracle_home, patch_id, patch_version, opatchauto):
            if remove_patch(module, msg, oracle_home, patch_base, patch_id, opatchauto,ocm_response_file, output):
                if patch_version is not None:
                    msg = 'Patch %s (%s) successfully removed from %s' % (patch_id,patch_version, oracle_home)
                else:
                    msg = 'Patch %s successfully removed from %s' % (patch_id, oracle_home)
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            if patch_version is not None:
                msg = 'Patch %s (%s) is not applied to %s' % (patch_id,patch_version, oracle_home)

            else:
                msg = 'Patch %s is not applied to %s' % (patch_id, oracle_home)

            module.exit_json(msg=msg, changed=False)


    module.exit_json(msg="Unhandled exit", changed=False)




from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
