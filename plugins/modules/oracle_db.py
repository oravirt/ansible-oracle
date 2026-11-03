#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
    oracledb_init,
)

DOCUMENTATION = '''
---
module: oracle_db
short_description: Manage an Oracle database
description:
    - Creates and deletes an Oracle database with C(dbca), starts or restarts it and
      manages some database settings (archivelog, force logging, flashback,
      supplemental logging, default tablespaces, time zone).
    - Must run on the database server. If C(/etc/oracle/olr.loc) exists, the database
      is treated as managed by Oracle Grid Infrastructure and C(srvctl) is used to
      check, start and stop it. Otherwise C(/etc/oratab) and C(sqlplus / as sysdba)
      are used.
    - The existence of a database is checked with C(srvctl config database) or in
      C(/etc/oratab). If the database is registered with a different Oracle home,
      the module fails.
    - The module connects as C(SYS) with C(SYSDBA) privilege using O(sys_password)
      to the service O(db_unique_name) (or O(db_name)), extended by
      C(.<domain>) when O(domain) is set. If O(sys_password) is not set, a
      connection with an Oracle wallet (C(/@<service>)) is used.
    - The Oracle version is determined with C(sqlplus -V) from O(oracle_home). Some
      C(dbca) arguments are only passed for specific versions.
    - Check mode is not supported.
version_added: "2.4.0"
options:
    oracle_home:
        description:
            - The Oracle home of the database. Used for C(dbca), C(srvctl) and
              C(sqlplus).
            - If not set, the environment variable C(ORACLE_HOME) is used. The module
              fails if neither is set.
        required: false
        type: str
        aliases: ['oh']
    db_name:
        description:
            - The name of the database (C(-gdbName) for C(dbca)).
        required: true
        type: str
        aliases: ['db', 'database_name', 'name']
    sid:
        description:
            - The instance name (C(-sid) for C(dbca)).
            - Used to find the database in C(/etc/oratab) and as C(ORACLE_SID) for
              C(sqlplus). Defaults to O(db_name) where needed.
        required: false
        type: str
    db_unique_name:
        description:
            - The C(db_unique_name) of the database.
            - When set, C(db_name) and C(db_unique_name) are passed to C(dbca) as
              init parameters. Also used as service name for the connection and as
              database name for C(srvctl).
        required: false
        type: str
        aliases: ['dbunqn', 'unique_name']
    sys_password:
        description:
            - Password for the C(SYS) user.
            - Used for C(dbca) (create and delete) and for the database connection.
            - Required in practice for O(state=absent) and, unless an Oracle wallet
              is used, for all states connecting to the database, although not
              enforced by the argument spec.
        required: false
        type: str
        aliases: ['syspw', 'sysdbapassword', 'sysdbapw']
    system_password:
        description:
            - Password for the C(SYSTEM) user, used when creating the database.
            - Defaults to O(sys_password). With O(responsefile), O(sys_password) is
              only used when the response file contains no C(systemPassword).
        required: false
        type: str
        aliases: ['systempw']
    dbsnmp_password:
        description:
            - Password for the C(DBSNMP) user, used when creating the database.
            - Defaults to O(sys_password).
        required: false
        type: str
        aliases: ['dbsnmppw']
    responsefile:
        description:
            - Path to a C(dbca) response file on the database server.
            - If set, the database is created with C(-responseFile). Only O(db_name),
              O(sid), O(db_unique_name), O(domain), O(initparams), the passwords,
              O(nodelist) (with O(dbconfig_type=RAC)) and O(omf) are passed in
              addition. All other creation options are ignored.
            - The module fails if the file does not exist.
        required: false
        type: str
    template:
        description:
            - The C(dbca) template the database is created from (C(-templateName)).
            - Ignored when O(responsefile) is set.
        required: false
        type: str
        default: General_Purpose.dbc
    cdb:
        description:
            - Whether the database is created as container database
              (C(-createAsContainerDatabase)).
            - Only passed for versions newer than 11.2 and without O(responsefile).
        required: false
        type: bool
        default: false
        aliases: ['container']
    local_undo:
        description:
            - Whether local undo is used for PDBs (C(-useLocalUndoForPDBs)).
            - Only used with O(cdb=true), for versions newer than 11.2 and without
              O(responsefile).
        required: false
        type: bool
        default: true
    datafile_dest:
        description:
            - Where the database files are placed (ASM disk group or file system
              path, C(-datafileDestination)).
            - Ignored when O(responsefile) is set.
        required: false
        type: str
        aliases: ['dfd']
    recoveryfile_dest:
        description:
            - Where the fast recovery area is placed (ASM disk group or file system
              path, C(-recoveryAreaDestination)).
            - Ignored when O(responsefile) is set.
        required: false
        type: str
        aliases: ['rfd']
    storage_type:
        description:
            - Type of the underlying storage (C(-storageType)), file system or ASM.
            - Ignored when O(responsefile) is set.
        required: false
        type: str
        default: FS
        aliases: ['storage']
        choices: ['FS', 'ASM']
    dbconfig_type:
        description:
            - Type of the database - single instance (V(SI)), RAC or RAC One Node.
            - Passed as C(-databaseConfigType) (12.2) or C(-databaseConfType) (12.1)
              only. V(SI) is passed as C(SINGLE).
            - Also controls whether O(nodelist) and O(racone_service) are used.
        required: false
        type: str
        default: SI
        choices: ['SI', 'RAC', 'RACONENODE']
    db_type:
        description:
            - Database type for C(dbca) (C(-databaseType)).
            - Ignored when O(responsefile) is set.
        required: false
        type: str
        default: MULTIPURPOSE
        choices: ['MULTIPURPOSE', 'DATA_WAREHOUSING', 'OLTP']
    racone_service:
        description:
            - Name of the service that is created with a RAC One Node database
              (C(-RACOneNodeServiceName)).
            - Only used with O(dbconfig_type=RACONENODE) and without O(responsefile).
              Defaults to C(<db_name>_ronserv).
        required: false
        type: str
        aliases: ['ron_service']
    characterset:
        description:
            - The database character set (C(-characterSet)).
            - Ignored when O(responsefile) is set.
        required: false
        type: str
        default: AL32UTF8
    memory_percentage:
        description:
            - The database total memory in percent of the available memory
              (C(-memoryPercentage)).
            - Ignored when O(responsefile) is set.
            - Mutually exclusive with O(memory_totalmb).
        required: false
        type: str
    memory_totalmb:
        description:
            - The database total memory in MB (C(-totalMemory)).
            - Ignored when O(responsefile) is set.
            - Mutually exclusive with O(memory_percentage).
        required: false
        type: str
        default: '1024'
    nodelist:
        description:
            - The list of cluster nodes a RAC database is created on (C(-nodelist)).
            - Only used with O(dbconfig_type=RAC).
        required: false
        type: list
        elements: str
    amm:
        description:
            - Whether Automatic Memory Management (C(memory_target)) is used.
            - Version 12.2 - C(-memoryMgmtType AUTO) or C(AUTO_SGA).
              Version 12.1 - C(-automaticMemoryManagement true|false).
              Version 11.2 - C(-automaticMemoryManagement) if V(true).
              Not passed for other versions.
            - Ignored when O(responsefile) is set.
        required: false
        type: bool
        default: false
        aliases: ['automatic_memory_management']
    initparams:
        description:
            - List of init parameters in the form C(name=value), passed to C(dbca)
              with C(-initParams).
        required: false
        type: list
        elements: str
    force_restart:
        description:
            - Only used with O(state=restarted).
            - If V(true), the database is restarted without further checks.
            - If V(false), the database is only restarted when an spfile is in use
              and parameters in the spfile differ from the runtime values
              (C(V$SPPARAMETER) vs. C(V$PARAMETER2)). Otherwise it is only started
              if it is not running.
        required: false
        type: bool
        default: true
        version_added: "3.8.0"
    customscripts:
        description:
            - List of SQL scripts that C(dbca) runs after the database is created
              (C(-customScripts)).
            - Ignored when O(responsefile) is set.
        required: false
        type: list
        elements: str
    default_tablespace_type:
        description:
            - Default tablespace type of the database (C(DEFAULT_TBS_TYPE)), set with
              C(ALTER DATABASE SET DEFAULT ... TABLESPACE).
            - Used with O(state=present).
        required: false
        type: str
        default: smallfile
        choices: ['smallfile', 'bigfile']
    default_tablespace:
        description:
            - Default permanent tablespace of the database
              (C(ALTER DATABASE DEFAULT TABLESPACE)).
            - Used with O(state=present). The current value is compared in lowercase,
              so the name should be given in lowercase.
        required: false
        type: str
    default_temp_tablespace:
        description:
            - Default temporary tablespace of the database
              (C(ALTER DATABASE DEFAULT TEMPORARY TABLESPACE)).
            - Used with O(state=present). The current value is compared in lowercase,
              so the name should be given in lowercase.
        required: false
        type: str
    archivelog:
        description:
            - Whether the database runs in archivelog mode.
            - Used with O(state=present). Changing the mode restarts the database
              (shutdown, startup mount, C(ALTER DATABASE [NO]ARCHIVELOG), restart).
        required: false
        type: bool
        default: false
    force_logging:
        description:
            - Whether force logging is enabled for the database.
            - Used with O(state=present).
        required: false
        type: bool
        default: false
    supplemental_logging:
        description:
            - Whether minimal supplemental logging is enabled
              (C(ALTER DATABASE ADD|DROP SUPPLEMENTAL LOG DATA)).
            - Used with O(state=present) and only for version 19 and newer.
        required: false
        type: bool
        default: false
    flashback:
        description:
            - Whether flashback database is enabled.
            - Used with O(state=present).
        required: false
        type: bool
        default: false
    datapatch:
        description:
            - Currently not used by the module.
        required: false
        type: bool
        default: true
    domain:
        description:
            - The database domain.
            - Appended to the service name for the database connection.
            - With O(responsefile), passed to C(dbca) as init parameter C(db_domain).
        required: false
        type: str
    timezone:
        description:
            - The database time zone (C(ALTER DATABASE SET TIME_ZONE)).
            - Used with O(state=present). The current value is compared in lowercase.
        required: false
        type: str
    output:
        description:
            - V(short) - short messages.
            - V(verbose) - the messages of a create or delete contain the output and
              the C(dbca) command line.
        required: false
        type: str
        default: short
        choices: ['short', 'verbose']
    state:
        description:
            - V(present) - the database is created if it does not exist. For new and
              existing databases the settings O(archivelog), O(force_logging),
              O(flashback), O(supplemental_logging), O(default_tablespace_type),
              O(default_tablespace), O(default_temp_tablespace) and O(timezone)
              are enforced. Creation options are not applied to an existing
              database.
            - V(absent) - the database is deleted with C(dbca -deleteDatabase). The
              database must be running.
            - V(started) - the database is started if it is not running.
            - V(restarted) - the database is restarted, see O(force_restart).
            - V(started) and V(restarted) fail if the database does not exist.
        required: false
        type: str
        default: present
        choices: ['present', 'absent', 'started', 'restarted']
    hostname:
        description:
            - Currently not used. The connection always uses the local host name of
              the database server.
        required: false
        type: str
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port used to connect to the database.
        required: false
        type: int
        default: 1521
    script_env:
        description:
            - Dictionary of environment variables passed to the C(sqlplus -V),
              C(srvctl config), C(srvctl status) and C(srvctl start) commands.
        required: false
        type: dict
        default: {}
    omf:
        description:
            - Whether Oracle Managed Files are used (C(-useOMF)).
            - Only passed for version 18.4 and newer.
        required: false
        type: bool
        default: false
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
- name: Create a non-CDB on ASM
  opitzconsulting.ansible_oracle.oracle_db:
    oracle_home: /u01/app/oracle/product/19/db1
    db_name: orcl
    sys_password: "{{ sys_password }}"
    storage_type: ASM
    datafile_dest: +DATA
    recoveryfile_dest: +FRA
    default_tablespace_type: bigfile
    state: present

- name: Create a container database with a response file and archivelog mode
  opitzconsulting.ansible_oracle.oracle_db:
    oracle_home: /u01/app/oracle/product/19/db1
    db_name: orclcdb
    db_unique_name: orclcdb_site1
    sid: orclcdb
    sys_password: "{{ sys_password }}"
    system_password: "{{ system_password }}"
    responsefile: /tmp/dbca_orclcdb.rsp
    initparams:
      - sga_target=1500M
      - sga_max_size=1500M
    archivelog: true
    force_logging: true
    state: present
  environment:
    ORACLE_HOME: /u01/app/oracle/product/19/db1
  run_once: true

- name: Restart the database only if spfile parameters were changed
  opitzconsulting.ansible_oracle.oracle_db:
    oracle_home: /u01/app/oracle/product/19/db1
    db_name: orcl
    sys_password: "{{ sys_password }}"
    force_restart: false
    state: restarted

- name: Delete a database
  opitzconsulting.ansible_oracle.oracle_db:
    oracle_home: /u01/app/oracle/product/19/db1
    db_name: orcl
    sys_password: "{{ sys_password }}"
    state: absent
'''

RETURN = '''
msg:
    description: Message describing the action that was executed.
    returned: always
    type: str
    sample: "Database orcl already exists and is in the intended state -
      Archivelog: False, Force Logging: False, Flashback: False, Supplemental
      Logging: False, Timezone: None"
restart_reason:
    description:
        - Reasons for the restart, either V(force_restart option was given) or the
          spfile parameters that differ from the runtime values
          (C(name:runtime -> spfile)).
    returned: when the database was restarted with O(state=restarted)
    type: list
    elements: str
    sample: ["sga_target:1536M -> 2G"]
'''


def get_version(module, oracle_home, script_env):
    command = '%s/bin/sqlplus -V' % (oracle_home)
    (rc, stdout, stderr) = module.run_command(command, environ_update=script_env)
    if rc != 0:
        msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
        module.fail_json(msg=msg, changed=False)

    else:
        return stdout.split(' ')[2][0:4]


# Check if the database exists
def check_db_exists(module, oracle_home, db_name, sid, db_unique_name, script_env):
    global msg

    if sid is None:
        sid = ''
    if gimanaged:
        if db_unique_name is not None:
            checkdb = db_unique_name
        else:
            checkdb = db_name

        command = "%s/bin/srvctl config database -d %s " % (oracle_home, checkdb)
        (rc, stdout, stderr) = module.run_command(command, environ_update=script_env)
        if rc != 0:
            if 'PRCD-1229' in stdout:
                # DB created, with different ORACLE_HOME
                msg = 'Database %s already exists in a different home. Stdout -> %s' % (
                    db_name,
                    stdout,
                )
                module.fail_json(msg=msg, changed=False)

            elif '%s' % (db_name) in stdout:
                # <-- db doesn't exist
                return False

            else:
                msg = 'Error: command is %s. stdout is %s' % (command, stdout)
                return False

        elif 'Database name: %s' % (db_name) in stdout:
            # <-- Database already exist
            return True

        else:
            msg = '%s' % (stdout)
            return True

    else:
        existingdbs = []
        oratabfile = '/etc/oratab'
        if os.path.exists(oratabfile):
            with open(oratabfile) as oratab:
                for line in oratab:
                    if line.startswith('#') or line.startswith(' '):
                        continue

                    elif re.search(db_name + ':', line) or re.search(sid + ':', line):
                        existingdbs.append(line)

        if not existingdbs:
            # <-- db doesn't exist
            return False

        else:
            for dbs in existingdbs:
                if sid != '':
                    if '%s:' % db_name in dbs or '%s:' % sid in dbs:
                        if dbs.split(':')[1] != oracle_home.rstrip('/'):
                            # <-- DB created, but with a different ORACLE_HOME
                            msg = (
                                'Database %s already exists in a different '
                                'ORACLE_HOME (%s)' % (db_name, dbs.split(':')[1])
                            )
                            module.fail_json(msg=msg, changed=False)

                        elif dbs.split(':')[1] == oracle_home.rstrip('/'):
                            # <-- Database already exist
                            return True

                else:
                    if '%s:' % db_name in dbs:
                        if dbs.split(':')[1] != oracle_home.rstrip('/'):
                            # <-- DB created, but with a different ORACLE_HOME
                            msg = (
                                'Database %s already exists in a different '
                                'ORACLE_HOME (%s)' % (db_name, dbs.split(':')[1])
                            )
                            module.fail_json(msg=msg, changed=False)

                        elif dbs.split(':')[1] == oracle_home.rstrip('/'):
                            # <-- Database already exist
                            return True


def create_db(
    module,
    oracle_home,
    sys_password,
    system_password,
    dbsnmp_password,
    db_name,
    sid,
    db_unique_name,
    responsefile,
    template,
    cdb,
    local_undo,
    datafile_dest,
    recoveryfile_dest,
    storage_type,
    dbconfig_type,
    racone_service,
    characterset,
    memory_percentage,
    memory_totalmb,
    nodelist,
    db_type,
    amm,
    initparams,
    customscripts,
    datapatch,
    domain,
    omf,
):
    initparam = ' -initParams '
    paramslist = ''
    scriptlist = ''

    command = "%s/bin/dbca -createDatabase -silent " % (oracle_home)
    if responsefile is not None:
        if os.path.exists(responsefile):
            command += ' -responseFile %s ' % (responsefile)
        else:
            msg = 'Responsefile %s doesn\'t exist' % (responsefile)
            module.fail_json(msg=msg, changed=False)

        if db_unique_name is not None:
            initparam += 'db_name=%s,db_unique_name=%s,' % (db_name, db_unique_name)

        if domain is not None:
            initparam += 'db_domain=%s,' % domain

        if initparams is not None:
            paramslist = ",".join(initparams)
            initparam += '%s' % (paramslist)

        command += ' -gdbName %s' % (db_name)
        if sid is not None:
            command += ' -sid %s' % (sid)
        if sys_password is not None:
            command += ' -sysPassword \"%s\"' % (sys_password)
        if system_password is not None:
            command += ' -systemPassword \"%s\"' % (system_password)
        else:
            pw_found = False
            with open(responsefile) as rspfile:
                for line in rspfile:
                    if re.match('systemPassword=.+', line):
                        pw_found = True
                        break
            if not pw_found:
                command += ' -systemPassword \"%s\"' % (sys_password)
        if dbsnmp_password is not None:
            command += ' -dbsnmpPassword \"%s\"' % (dbsnmp_password)
        else:
            dbsnmp_password = sys_password
            command += ' -dbsnmpPassword \"%s\"' % (dbsnmp_password)
        if dbconfig_type == 'RAC':
            if nodelist is not None:
                nodelist = ",".join(nodelist)
                command += ' -nodelist %s ' % (nodelist)

    else:
        command += ' -gdbName %s' % (db_name)
        if sid is not None:
            command += ' -sid %s' % (sid)
        if sys_password is not None:
            command += ' -sysPassword \"%s\"' % (sys_password)
        if system_password is not None:
            command += ' -systemPassword \"%s\"' % (system_password)
        else:
            system_password = sys_password
            command += ' -systemPassword \"%s\"' % (system_password)
        if dbsnmp_password is not None:
            command += ' -dbsnmpPassword \"%s\"' % (dbsnmp_password)
        else:
            dbsnmp_password = sys_password
            command += ' -dbsnmpPassword \"%s\"' % (dbsnmp_password)
        if template:
            command += ' -templateName \"%s\"' % (template)
        if major_version > '11.2':
            if cdb is True:
                command += ' -createAsContainerDatabase true '
                if local_undo is True:
                    command += ' -useLocalUndoForPDBs true'
                else:
                    command += ' -useLocalUndoForPDBs false'
            else:
                command += ' -createAsContainerDatabase false '
        if datafile_dest is not None:
            command += ' -datafileDestination %s ' % (datafile_dest)
        if recoveryfile_dest is not None:
            command += ' -recoveryAreaDestination %s ' % (recoveryfile_dest)
        if storage_type is not None:
            command += ' -storageType %s ' % (storage_type)
        if dbconfig_type is not None:
            if dbconfig_type == 'SI':
                dbconfig_type = 'SINGLE'
            if major_version == '12.2':
                command += ' -databaseConfigType %s ' % (dbconfig_type)
            elif major_version == '12.1':
                command += ' -databaseConfType %s ' % (dbconfig_type)
        if dbconfig_type == 'RACONENODE':
            if racone_service is None:
                racone_service = db_name + '_ronserv'
            command += ' -RACOneNodeServiceName %s ' % (racone_service)
        if characterset is not None:
            command += ' -characterSet %s ' % (characterset)
        if memory_percentage is not None:
            command += ' -memoryPercentage %s ' % (memory_percentage)
        if memory_totalmb is not None:
            command += ' -totalMemory %s ' % (memory_totalmb)
        if dbconfig_type == 'RAC':
            if nodelist is not None:
                nodelist = ",".join(nodelist)
                command += ' -nodelist %s ' % (nodelist)
        if db_type is not None:
            command += ' -databaseType %s ' % (db_type)
        if amm is not None:
            if major_version == '12.2':
                if amm is True:
                    command += ' -memoryMgmtType AUTO '
                else:
                    command += ' -memoryMgmtType AUTO_SGA '
            elif major_version == '12.1':
                command += ' -automaticMemoryManagement %s ' % (str(amm).lower())

            elif major_version == '11.2':
                if amm is True:
                    command += ' -automaticMemoryManagement '

        if customscripts is not None:
            scriptlist = ",".join(customscripts)
            command += ' -customScripts %s ' % (scriptlist)

        if db_unique_name is not None:
            initparam += 'db_name=%s,db_unique_name=%s,' % (db_name, db_unique_name)

        if initparams is not None:
            # paramslist = ",".join(initparams)
            # initparam += ' %s' % (paramslist)
            initparam += ' %s' % (initparams)

    if omf is not None:
        if major_version >= '18.4':
            if omf is True:
                command += ' -useOMF true '
            else:
                command += ' -useOMF false '

    if initparam != ' -initParams ' or paramslist != "":
        command += initparam

    # msg = "command: %s" % (command)
    # module.fail_json(msg=msg, changed=False)
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (stdout, stderr, command)
        module.fail_json(msg=msg, changed=False)

    else:
        if output == 'short':
            return True

        else:
            verbosemsg = 'STDOUT: %s,  COMMAND: %s' % (stdout, command)
            verboselist.append(verbosemsg)
            return True, verboselist
            # module.exit_json(msg=verbosemsg, changed=True)

    # elif rc == 0 and datapatch:
    #     if run_datapatch(module, oracle_home, db_name, db_unique_name):
    #         return True
    # else:
    #     return True


def remove_db(module, oracle_home, db_name, sid, db_unique_name, sys_password):
    cursor = getconn(module)
    israc_sql = 'select parallel, instance_name, host_name from v$instance'
    israc_ = execute_sql_get(module, cursor, israc_sql)
    remove_db = ''
    if gimanaged:
        if db_unique_name is not None:
            remove_db = db_unique_name
        elif sid is not None and israc_[0][0] == 'YES':
            remove_db = db_name
        elif sid is not None and israc_[0][0] == 'NO':
            remove_db = sid
        else:
            remove_db = db_name
    else:
        if sid is not None:
            remove_db = sid
        else:
            remove_db = db_name

    command = (
        "%s/bin/dbca -deleteDatabase -silent -sourceDB %s -sysDBAUserName sys "
        "-sysDBAPassword %s" % (oracle_home, remove_db, sys_password)
    )
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg = 'Removal of database %s failed: %s' % (db_name, stdout)
        module.fail_json(msg=msg, changed=False)

    else:
        if output == 'short':
            return True
        else:
            msg = 'STDOUT: %s,  COMMAND: %s' % (stdout, command)
            module.exit_json(msg=msg, changed=True)


def ensure_db_state(
    module,
    oracle_home,
    db_name,
    db_unique_name,
    sid,
    archivelog,
    force_logging,
    supplemental_logging,
    flashback,
    default_tablespace_type,
    default_tablespace,
    default_temp_tablespace,
    timezone,
    script_env,
):
    cursor = getconn(module)
    global israc
    slcomp = ''
    alterdb_sql = 'alter database'

    propsql = "select lower(property_value) from database_properties where \
        property_name in ('DEFAULT_TBS_TYPE', 'DEFAULT_PERMANENT_TABLESPACE', \
            'DEFAULT_TEMP_TABLESPACE') order by 1"
    tzsql = "select lower(property_value) from database_properties \
        where property_name = 'DBTIMEZONE'"

    curr_time_zone = execute_sql_get(module, cursor, tzsql)
    def_tbs_type, def_tbs, def_temp_tbs = execute_sql_get(module, cursor, propsql)
    israc_sql = 'select parallel, instance_name from v$instance'
    israc_ = execute_sql_get(module, cursor, israc_sql)
    instance_name = israc_[0][1]

    change_restart_sql = []
    change_db_sql = []
    log_check_sql = 'select log_mode, force_logging, flashback_on \
        from v$database'
    log_check_ = execute_sql_get(module, cursor, log_check_sql)

    if major_version >= '19.0':
        supp_log_check_sql = 'select SUPPLEMENTAL_LOG_DATA_MIN, \
            SUPPLEMENTAL_LOG_DATA_PL, SUPPLEMENTAL_LOG_DATA_SR, \
            SUPPLEMENTAL_LOG_DATA_PK, SUPPLEMENTAL_LOG_DATA_UI \
            from v$database'
        supp_log_check_ = execute_sql_get(module, cursor, supp_log_check_sql)
        if supp_log_check_[0][0] != slcomp:
            if supplemental_logging is True:
                slcomp = 'YES'
                slsql = alterdb_sql + ' add supplemental log data'
            else:
                slcomp = 'NO'
                slsql = alterdb_sql + ' drop supplemental log data'

            change_db_sql.append(slsql)

    if israc_[0][0] == 'NO':
        israc = False
    else:
        israc = True

    if archivelog is True:
        archcomp = 'ARCHIVELOG'
        archsql = alterdb_sql + ' archivelog'
    else:
        archcomp = 'NOARCHIVELOG'
        archsql = alterdb_sql + ' noarchivelog'

    if force_logging is True:
        flcomp = 'YES'
        flsql = alterdb_sql + ' force logging'
    else:
        flcomp = 'NO'
        flsql = alterdb_sql + ' no force logging'

    if flashback is True:
        fbcomp = 'YES'
        fbsql = alterdb_sql + ' flashback on'
    else:
        fbcomp = 'NO'
        fbsql = alterdb_sql + ' flashback off'

    if def_tbs_type[0] != default_tablespace_type:
        deftbstypesql = 'alter database set default %s tablespace ' % (
            default_tablespace_type
        )
        change_db_sql.append(deftbstypesql)

    if default_tablespace is not None and def_tbs[0] != default_tablespace:
        deftbssql = 'alter database default tablespace %s' % (default_tablespace)
        change_db_sql.append(deftbssql)

    if (
        default_temp_tablespace is not None
        and def_temp_tbs[0] != default_temp_tablespace
    ):
        deftempsql = 'alter database default temporary tablespace %s' % (
            default_temp_tablespace
        )
        change_db_sql.append(deftempsql)

    if timezone is not None and curr_time_zone[0][0] != timezone:
        deftzsql = 'alter database set time_zone = \'%s\'' % (timezone)
        change_db_sql.append(deftzsql)

    if log_check_[0][0] != archcomp:
        change_restart_sql.append(archsql)

    if log_check_[0][1] != flcomp:
        change_db_sql.append(flsql)

    if log_check_[0][2] != fbcomp:
        change_db_sql.append(fbsql)

    if len(change_db_sql) > 0 or len(change_restart_sql) > 0:
        if (
            log_check_[0][0] == 'ARCHIVELOG'
            and log_check_[0][2] == 'YES'
            and not archivelog
            and not flashback
        ):
            # Flashback database needs to be turned off before
            # archivelog is turned off
            # todo: This is not needed anymore!

            if len(change_db_sql) > 0:
                # <- Apply changes that does not require a restart
                apply_norestart_changes(module, change_db_sql)

            if len(change_restart_sql) > 0:
                # Apply changes that requires a restart
                apply_restart_changes(
                    module,
                    oracle_home,
                    db_name,
                    db_unique_name,
                    sid,
                    instance_name,
                    israc,
                    change_restart_sql,
                    script_env,
                )
        else:
            if len(change_restart_sql) > 0:
                # <- Apply changes that requires a restart
                apply_restart_changes(
                    module,
                    oracle_home,
                    db_name,
                    db_unique_name,
                    sid,
                    instance_name,
                    israc,
                    change_restart_sql,
                    script_env,
                )

            if len(change_db_sql) > 0:
                # Apply changes that does not require a restart
                apply_norestart_changes(module, change_db_sql)

        msg = (
            'Database %s has been put in the intended state - Archivelog: %s, '
            'Force Logging: %s, Flashback: %s, Supplemental Logging: %s, '
            'Timezone: %s'
            % (
                db_name,
                archivelog,
                force_logging,
                flashback,
                supplemental_logging,
                timezone,
            )
        )

        module.exit_json(msg=msg, changed=True)
    else:
        if newdb:
            msg = 'Database %s successfully created created (%s) ' % (db_name, archcomp)
            if output == 'verbose':
                msg += ' ,'.join(verboselist)
            changed = True
        else:
            msg = (
                'Database %s already exists and is in the intended state - '
                'Archivelog: %s, Force Logging: %s, Flashback: %s, Supplemental '
                'Logging: %s, Timezone: %s'
                % (
                    db_name,
                    archivelog,
                    force_logging,
                    flashback,
                    supplemental_logging,
                    timezone,
                )
            )
            changed = False
        module.exit_json(msg=msg, changed=changed)


def apply_restart_changes(
    module,
    oracle_home,
    db_name,
    db_unique_name,
    sid,
    instance_name,
    israc,
    change_restart_sql,
    script_env,
):
    open_mode = stop_db(module, oracle_home, db_name, db_unique_name, sid)
    start_instance(
        module,
        oracle_home,
        db_name,
        db_unique_name,
        sid,
        script_env,
        'mount',
        israc,
        instance_name,
    )
    cursor = getconn(module)
    for sql in change_restart_sql:
        execute_sql(module, cursor, sql)
    stop_db(module, oracle_home, db_name, db_unique_name, sid)
    start_db(module, oracle_home, db_name, db_unique_name, sid, script_env, open_mode)


def apply_norestart_changes(module, change_db_sql):
    cursor = getconn(module)
    for sql in change_db_sql:
        execute_sql(module, cursor, sql)


def spfile_restart_needed(module, force_restart):
    if force_restart:
        return True, ['force_restart option was given']
    cursor = getconn(module)
    init_parameter_sql = 'SELECT DECODE(value, NULL, \
          \'PFILE\', \'SPFILE\') "Init File Type" \
          FROM sys.v$parameter WHERE name = \'spfile\''
    init_parameter_style = execute_sql_get(module, cursor, init_parameter_sql)
    if init_parameter_style[0][0] == 'PFILE':
        # no restart needed if running with PFILE
        return False, ['database running without spfile and force_restart is false']

    if major_version > '11.2':
        spf_check_sql = (
            "select vsp.name || ':' || vp.value || ' -> ' || "
            "vsp.value as change from "
            "( select name, listagg(value,', ') within group "
            "(order by value) as value, con_id from v$spparameter"
            "  group by name, con_id) vsp, "
            "( select name, listagg(value,', ') within group "
            "(order by value) as value, con_id from v$parameter2 "
            " group by name, con_id) vp "
            "where vsp.name=vp.name "
            "and vsp.con_id = vp.con_id "
            "and upper(vsp.value) != upper(vp.value)"
        )
    else:
        spf_check_sql = (
            "select vsp.name || ':' || vp.value || ' -> ' || "
            "vsp.value as change from "
            "( select name, listagg(value,', ') within group "
            "(order by value) as value from v$spparameter "
            "group by name) vsp, "
            "( select name, listagg(value,', ') within group "
            "(order by value) as value from v$parameter2 "
            "group by name) vp "
            "where vsp.name=vp.name and upper(vsp.value) != upper(vp.value)"
        )

    init_changes = execute_sql_get(module, cursor, spf_check_sql)
    if len(init_changes) == 0:
        return False, ['spfile parameters match runtime']
    else:
        return True, [i[0] for i in init_changes]


def stop_db(module, oracle_home, db_name, db_unique_name, sid):
    # global debug
    # debug.append('stop_db called')

    if gimanaged:
        if db_unique_name is not None:
            db_name = db_unique_name
        command = '%s/bin/srvctl stop database -d %s -o immediate' % (
            oracle_home,
            db_name,
        )
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            msg = 'Error(stop_db) - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                command,
            )
            module.fail_json(msg=msg, changed=False)

        else:
            # Grid knows the right open mode, so return None to be passed to
            # start_instance
            return None

    else:
        # query current open_mode for potential restart in case of non-grid
        cursor = getconn(module)
        open_mode_sql = (
            "SELECT CASE OPEN_MODE WHEN 'MOUNTED' "
            "THEN 'mount' "
            "WHEN 'READ WRITE' THEN 'open read write' "
            "ELSE 'open read only' END AS open_mode FROM V$DATABASE"
        )
        open_mode = execute_sql_get(module, cursor, open_mode_sql)

        if sid is not None:
            os.environ['ORACLE_SID'] = sid
        else:
            os.environ['ORACLE_SID'] = db_name
        shutdown_sql = '''
        connect / as sysdba
        shutdown immediate;
        exit
        '''
        sqlplus_bin = '%s/bin/sqlplus' % (oracle_home)
        p = subprocess.Popen(
            [sqlplus_bin, '/nolog'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (stdout, stderr) = p.communicate(shutdown_sql.encode('utf-8'))
        rc = p.returncode
        # debug.append('stop_db: rc=%d, STDOUT: %s, STDERR: %s, COMMAND: %s' %
        #              (rc, stdout, stderr, shutdown_sql))
        # debug.append('stop_db env: USER:%s ORACLE_HOME:%s ORACLE_SID:%s' %
        #              (os.environ['USER'], os.environ['ORACLE_SID'],
        #               os.environ['ORACLE_HOME']))
        if rc != 0 or (b'ORA-' in stdout and b'ORA-01109:' not in stdout):
            msg = 'Error(stop_db) - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                shutdown_sql,
            )
            # module.fail_json(msg=msg, changed=False, debug=debug)
            module.fail_json(msg=msg, changed=False)
        else:
            # return previous open_mode in format suitable for startup command
            return open_mode[0][0]


def start_db(
    module, oracle_home, db_name, db_unique_name, sid, script_env, open_mode=None
):
    # global debug
    # debug.append('start_db called with open_mode %s,
    #              calling start_instance' % \
    #              (open_mode or "None"))
    return start_instance(
        module, oracle_home, db_name, db_unique_name, sid, open_mode, is_cluster, sid
    )


def start_instance(
    module,
    oracle_home,
    db_name,
    db_unique_name,
    sid,
    script_env,
    open_mode=None,
    israc=False,
    instance_name='',
):
    # global debug
    # debug.append('start_instance called with open_mode %s' % (open_mode or "None"))  # noqa E501

    if gimanaged:
        if db_unique_name is not None:
            db_name = db_unique_name

        if israc:
            command = '%s/bin/srvctl status instance -d %s -i %s' % (
                oracle_home,
                db_name,
                instance_name,
            )
        else:
            command = '%s/bin/srvctl status database -d %s ' % (oracle_home, db_name)

        (rc, stdout, stderr) = module.run_command(command, environ_update=script_env)
        if rc != 0:
            msg = 'Error(start_instance) - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                command,
            )  # noqa E501
            module.fail_json(msg=msg, changed=False)

        elif 'is running' in stdout:
            return 'ok'

        elif 'is not running' in stdout:
            if israc:
                command = '%s/bin/srvctl start instance -d %s -i %s' % (
                    oracle_home,
                    db_name,
                    instance_name,
                )
            else:
                if is_cluster:
                    command = '%s/bin/srvctl start database -d %s -node %s ' % (
                        oracle_home,
                        db_name,
                        os.uname()[1].split('.')[0],
                    )
                else:
                    command = '%s/bin/srvctl start database -d %s ' % (
                        oracle_home,
                        db_name,
                    )
            if open_mode is not None:
                command += ' -o %s ' % (open_mode)
            (rc, stdout, stderr) = module.run_command(
                command, environ_update=script_env
            )

            # To allow the DB to register with the listener,
            # as following tasks may want to connect to it immediately and fail
            time.sleep(10)

            if rc != 0:
                msg = (
                    'Error(start_instance) - STDOUT: %s, STDERR: %s, '
                    'COMMAND: %s' % (stdout, stderr, command)
                )
                module.fail_json(msg=msg, changed=False)
            else:
                return 'changed'
        else:
            msg = 'Error - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                command,
            )
            module.fail_json(msg=msg, changed=False)

    else:
        if sid is not None:
            os.environ['ORACLE_SID'] = sid
        else:
            os.environ['ORACLE_SID'] = db_name

        startup_sql = '''
        connect / as sysdba
        startup %s;
        exit
        ''' % (
            open_mode or ""
        )
        sqlplus_bin = '%s/bin/sqlplus' % (oracle_home)
        p = subprocess.Popen(
            [sqlplus_bin, '/nolog'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (stdout, stderr) = p.communicate(startup_sql.encode('utf-8'))
        rc = p.returncode

        # To allow the DB to register with the listener,
        # as following tasks may want to connect to it immediately and fail
        time.sleep(10)

        # debug.append('start_instance: rc=%d, Error - STDOUT: %s, ' \
        #              'STDERR: %s, COMMAND: %s' % \
        #              (rc, stdout, stderr, startup_sql))
        # debug.append('start_instance: env: USER:%s ORACLE_HOME:%s ' \
        #              'ORACLE_SID:%s' % (os.environ['USER'],
        #                                 os.environ['ORACLE_SID'],
        #                                 os.environ['ORACLE_HOME']))
        if b'ORA-01081:' in stdout:
            return 'ok'
        elif rc != 0 or b'ORA-' in stdout:
            msg = 'Error(start_instance) - STDOUT: %s, STDERR: %s, COMMAND: %s' % (
                stdout,
                stderr,
                startup_sql,
            )
            # module.fail_json(msg=msg, changed=False, debug=debug)
            module.fail_json(msg=msg, changed=False)
        else:
            return 'changed'


def execute_sql_get(module, cursor, sql):
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
    return result


def execute_sql(module, cursor, sql):
    try:
        cursor.execute(sql)
    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
    return True


def getconn(module):
    hostname = os.uname()[1]
    # oracle_db connects always as SYSDBA
    conn = oracledb_connect(
        module, hostname, port, service_name, user, password, 'sysdba'
    )
    cursor = conn.cursor()
    return cursor


def main():
    global msg
    global gimanaged
    global major_version
    global user
    global password
    global service_name
    global hostname
    global port
    global newdb
    global output
    global verbosemsg
    global verboselist
    global domain
    global cursor
    global is_cluster

    cursor = None

    # global debug
    verbosemsg = ''
    verboselist = []
    # debug = []
    newdb = False

    # fmt: off
    module = AnsibleModule(
        argument_spec=dict(
            oracle_home         = dict(default=None, aliases = ['oh']), # noqa E231
            db_name             = dict(required=True, aliases = ['db', 'database_name', 'name']), # noqa E231
            sid                 = dict(required=False), # noqa E231
            db_unique_name      = dict(required=False, aliases = ['dbunqn','unique_name']), # noqa E231
            sys_password        = dict(required=False, no_log=True, aliases = ['syspw', 'sysdbapassword', 'sysdbapw']), # noqa E231
            system_password     = dict(required=False, no_log=True, aliases = ['systempw']), # noqa E231
            dbsnmp_password     = dict(required=False, no_log=True, aliases = ['dbsnmppw']), # noqa E231
            responsefile        = dict(required=False), # noqa E231
            template            = dict(default='General_Purpose.dbc'), # noqa E231
            cdb                 = dict(default=False, type='bool', aliases=['container']), # noqa E231
            local_undo          = dict(default=True, type='bool'), # noqa E231
            datafile_dest       = dict(required=False, aliases= ['dfd']), # noqa E231
            recoveryfile_dest   = dict(required=False, aliases= ['rfd']), # noqa E231
            storage_type        = dict(default='FS', aliases= ['storage'], choices = ['FS','ASM']), # noqa E231
            dbconfig_type       = dict(default='SI', choices = ['SI', 'RAC', 'RACONENODE']), # noqa E231
            db_type             = dict(default='MULTIPURPOSE', choices = ['MULTIPURPOSE', 'DATA_WAREHOUSING', 'OLTP']), # noqa E231
            racone_service      = dict(required=False, aliases = ['ron_service']), # noqa E231
            characterset        = dict(default='AL32UTF8'), # noqa E231
            memory_percentage   = dict(required=False), # noqa E231
            memory_totalmb      = dict(default='1024'), # noqa E231
            nodelist            = dict(required=False, type='list'), # noqa E231
            amm                 = dict(default=False, type='bool', aliases = ['automatic_memory_management']), # noqa E231
            initparams          = dict(required=False, type='list'), # noqa E231
            force_restart       = dict(default=True, type='bool'), # noqa E231
            customscripts       = dict(required=False, type='list'), # noqa E231
            default_tablespace_type = dict(default='smallfile', choices = ['smallfile', 'bigfile']), # noqa E231
            default_tablespace  = dict(required=False), # noqa E231
            default_temp_tablespace  = dict(required=False), # noqa E231
            archivelog          = dict(default=False, type='bool'), # noqa E231
            force_logging       = dict(default=False, type='bool'), # noqa E231
            supplemental_logging       = dict(default=False, type='bool'), # noqa E231
            flashback           = dict(default=False, type='bool'), # noqa E231
            datapatch           = dict(default=True, type='bool'), # noqa E231
            domain              = dict(required=False), # noqa E231
            timezone            = dict(required=False), # noqa E231
            output              = dict(default="short", choices = ["short", "verbose"]), # noqa E231
            state               = dict(default="present", choices = ["present", "absent", "started", "restarted"]), # noqa E231
            hostname            = dict(required=False, default = 'localhost', aliases = ['host']), # noqa E231
            port                = dict(required=False, default = 1521), # noqa E231
            omf                 = dict(required=False, type='bool', default=False), # noqa E231
            script_env          = dict(required=False, type='dict', default={}), # noqa E231
        ),
        mutually_exclusive=[['memory_percentage', 'memory_totalmb']],
    )
    # fmt: on

    # fmt: off
    oracle_home         = module.params["oracle_home"] # noqa E221
    db_name             = module.params["db_name"] # noqa E221
    sid                 = module.params["sid"] # noqa E221
    db_unique_name      = module.params["db_unique_name"] # noqa E221
    sys_password        = module.params["sys_password"] # noqa E221
    system_password     = module.params["system_password"] # noqa E221
    dbsnmp_password     = module.params["dbsnmp_password"] # noqa E221
    responsefile        = module.params["responsefile"] # noqa E221
    template            = module.params["template"] # noqa E221
    cdb                 = module.params["cdb"] # noqa E221
    local_undo          = module.params["local_undo"] # noqa E221
    datafile_dest       = module.params["datafile_dest"] # noqa E221
    recoveryfile_dest   = module.params["recoveryfile_dest"] # noqa E221
    storage_type        = module.params["storage_type"] # noqa E221
    dbconfig_type       = module.params["dbconfig_type"] # noqa E221
    racone_service      = module.params["racone_service"] # noqa E221
    characterset        = module.params["characterset"] # noqa E221
    memory_percentage   = module.params["memory_percentage"] # noqa E221
    memory_totalmb      = module.params["memory_totalmb"] # noqa E221
    nodelist            = module.params["nodelist"] # noqa E221
    db_type             = module.params["db_type"] # noqa E221
    amm                 = module.params["amm"] # noqa E221
    initparams          = module.params["initparams"] # noqa E221
    force_restart       = module.params["force_restart"] # noqa E231
    customscripts       = module.params["customscripts"] # noqa E221
    default_tablespace_type = module.params["default_tablespace_type"] # noqa E221
    default_tablespace      = module.params["default_tablespace"] # noqa E221
    default_temp_tablespace = module.params["default_temp_tablespace"] # noqa E221
    archivelog          = module.params["archivelog"] # noqa E221
    force_logging       = module.params["force_logging"] # noqa E221
    supplemental_logging    = module.params["supplemental_logging"] # noqa E221
    flashback           = module.params["flashback"] # noqa E221
    datapatch           = module.params["datapatch"] # noqa E221
    domain              = module.params["domain"] # noqa E221
    timezone            = module.params["timezone"] # noqa E221
    output              = module.params["output"] # noqa E221
    state               = module.params["state"] # noqa E221
    hostname            = module.params["hostname"] # noqa E221
    port                = module.params["port"] # noqa E221
    omf                 = module.params["omf"] # noqa E221
    script_env          = module.params["script_env"] # noqa E221
    # fmt: on

    # ld_library_path = '%s/lib' % (oracle_home)
    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home.rstrip('/')
        # os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']
        # ld_library_path = os.environ['LD_LIBRARY_PATH']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'  # noqa E501
        module.fail_json(msg=msg, changed=False)

    # fail before dbca, when python-oracledb or the Oracle Client libraries are missing
    oracledb_init(module)

    # Decide whether to use srvctl or sqlplus
    if os.path.exists('/etc/oracle/olr.loc'):
        gimanaged = True
    else:
        gimanaged = False

    # If gimanaged, check whether it's Oracle Restart or Oracle Clusterware
    is_cluster = False
    ocr_loc = '/etc/oracle/ocr.loc'
    if gimanaged and os.path.exists(ocr_loc):
        ocr_grep = subprocess.run(
            ['grep', '-Piq', '^\\s*local_only\\s*=\\s*false', ocr_loc]
        )
        is_cluster = not bool(ocr_grep.returncode)

    # Connection details for database
    user = 'sys'
    password = sys_password
    if db_unique_name is not None:
        service_name = db_unique_name
    else:
        service_name = db_name

    if domain is not None and domain != '':
        service_name = "%s.%s" % (service_name, domain)

    # Get the Oracle version
    major_version = get_version(module, oracle_home, script_env)

    if state == 'started' or state == 'restarted':
        msg = "oracle_home: %s db_name: %s sid: %s db_unique_name: %s" % (
            oracle_home,
            db_name,
            sid,
            db_unique_name,
        )
        spf_restart_needed = False

        if not check_db_exists(
            module, oracle_home, db_name, sid, db_unique_name, script_env
        ):
            msg = "Database not found. %s" % msg
            module.fail_json(msg=msg, changed=False)

        else:
            if state == 'restarted':
                spf_restart_needed, spf_restart_reason = spfile_restart_needed(
                    module, force_restart
                )

                if spf_restart_needed:
                    open_mode = stop_db(
                        module, oracle_home, db_name, db_unique_name, sid
                    )

                else:
                    # ensure db runs (in default open mode) if not restarting
                    open_mode = None

                start_db_state = start_db(
                    module,
                    oracle_home,
                    db_name,
                    db_unique_name,
                    sid,
                    script_env,
                    open_mode,
                )
            else:
                start_db_state = start_db(
                    module, oracle_home, db_name, db_unique_name, sid, script_env
                )

            if start_db_state == 'changed' and not spf_restart_needed:
                msg = "Database started."
                # module.exit_json(msg=msg, changed=True, debug=debug)
                module.exit_json(msg=msg, changed=True)
            elif start_db_state == 'changed':
                msg = "Database restarted."
                # module.exit_json(msg=msg, restart_reason=spf_restart_reason,
                # changed=True, debug=debug)
                module.exit_json(
                    msg=msg, restart_reason=spf_restart_reason, changed=True
                )
            elif start_db_state == 'ok' and state == 'restarted':
                msg = "No restart needed (%s)" % (spf_restart_reason[0])
                module.exit_json(msg=msg, changed=False)
            elif start_db_state == 'ok':
                msg = "Database already running."
                module.exit_json(msg=msg, changed=False)
            else:
                msg = "Startup failed. %s" % msg
                module.fail_json(msg=msg, changed=False)

    elif state == 'present':
        if not check_db_exists(
            module, oracle_home, db_name, sid, db_unique_name, script_env
        ):
            if create_db(
                module,
                oracle_home,
                sys_password,
                system_password,
                dbsnmp_password,
                db_name,
                sid,
                db_unique_name,
                responsefile,
                template,
                cdb,
                local_undo,
                datafile_dest,
                recoveryfile_dest,
                storage_type,
                dbconfig_type,
                racone_service,
                characterset,
                memory_percentage,
                memory_totalmb,
                nodelist,
                db_type,
                amm,
                initparams,
                customscripts,
                datapatch,
                domain,
                omf,
            ):
                newdb = True
                ensure_db_state(
                    module,
                    oracle_home,
                    db_name,
                    db_unique_name,
                    sid,
                    archivelog,
                    force_logging,
                    supplemental_logging,
                    flashback,
                    default_tablespace_type,
                    default_tablespace,
                    default_temp_tablespace,
                    timezone,
                    script_env,
                )

            else:
                module.fail_json(msg=msg, changed=False)
        else:
            ensure_db_state(
                module,
                oracle_home,
                db_name,
                db_unique_name,
                sid,
                archivelog,
                force_logging,
                supplemental_logging,
                flashback,
                default_tablespace_type,
                default_tablespace,
                default_temp_tablespace,
                timezone,
                script_env,
            )
            # msg = 'Database %s already exists' % (db_name)
            # module.exit_json(msg=msg, changed=False)

    elif state == 'absent':
        if check_db_exists(
            module, oracle_home, db_name, sid, db_unique_name, script_env
        ):
            if remove_db(
                module, oracle_home, db_name, sid, db_unique_name, sys_password
            ):
                msg = 'Successfully removed database %s' % (db_name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            msg = 'Database %s doesn\'t exist' % (db_name)
            module.exit_json(msg=msg, changed=False)

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
