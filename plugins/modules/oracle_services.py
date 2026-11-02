#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.opitzconsulting.ansible_oracle.plugins.module_utils.oracledb_connect import (  # noqa: E501
    oracledb,
    oracledb_connect,
)

DOCUMENTATION = '''
---
module: oracle_services
short_description: Manage services in an Oracle database
description:
    - Creates, removes, starts, stops and restarts database services and shows their
      status.
    - If the file C(/etc/oracle/olr.loc) exists, the system is treated as managed by
      Grid Infrastructure (RAC or Oracle Restart) and the service is managed with
      C(srvctl) from O(oracle_home). The database connection options are ignored.
    - Otherwise the service is managed with C(DBMS_SERVICE) through a python-oracledb
      connection. In this mode only O(name) is used for the service, O(pdb),
      O(role), O(preferred_instances), O(available_instances), O(clbgoal) and
      O(rlbgoal) are ignored.
    - If neither O(user) nor O(password) is given, a connection with an Oracle
      wallet (C(/@<service_name>)) is used. Otherwise both must be set.
    - With Grid Infrastructure, the configuration of an existing service is compared
      with O(preferred_instances), O(available_instances), O(clbgoal) and O(rlbgoal)
      and changed with C(srvctl modify service) if it differs.
version_added: "2.1.0.0"
options:
    name:
        description:
            - The name of the service.
        type: str
        required: true
        aliases: ['service']
    oracle_home:
        description:
            - The Oracle home of the database. C(srvctl) is called from
              C(<oracle_home>/bin).
            - If not set, the environment variable C(ORACLE_HOME) is used. The module
              fails if neither is set.
        type: str
        required: false
        aliases: ['oh']
    database_name:
        description:
            - The unique name of the database in which the service runs (C(srvctl -d)).
            - Without Grid Infrastructure it is the default for O(service_name).
        type: str
        required: true
        aliases: ['db']
    state:
        description:
            - V(present) - the service is created if it does not exist. With Grid
              Infrastructure the configuration of an existing service is adjusted.
              The service is not started.
            - V(started) - like V(present), then the service is started.
            - V(stopped) - like V(present), then the service is stopped.
            - V(restarted) - the service is stopped and started again.
            - V(absent) - the service is stopped and removed.
            - V(status) - reports whether the service is running, nothing is changed.
              With Grid Infrastructure, the output of C(srvctl status service) is
              returned.
        type: str
        required: false
        default: present
        choices: ['present', 'absent', 'started', 'stopped', 'status', 'restarted']
    preferred_instances:
        description:
            - Comma-separated list of the RAC instances on which the service actively
              runs (C(srvctl -r) / C(-preferred)).
            - Grid Infrastructure only.
        type: str
        required: false
        aliases: ['pi']
    available_instances:
        description:
            - Comma-separated list of the RAC instances on which the service can run
              when the O(preferred_instances) fail (C(srvctl -a) / C(-available)).
            - Grid Infrastructure only.
        type: str
        required: false
        aliases: ['ai']
    pdb:
        description:
            - The pluggable database the service is attached to (C(srvctl -pdb)).
            - Only used when the service is created with Grid Infrastructure.
        type: str
        required: false
    role:
        description:
            - The database role in which the service is started automatically
              (C(srvctl -l)).
            - Only used when the service is created with Grid Infrastructure.
        type: str
        required: false
        choices: ['primary', 'physical_standby', 'logical_standby', 'snapshot_standby']
    clbgoal:
        description:
            - The connection load balancing goal, e.g. V(SHORT) or V(LONG)
              (C(srvctl -clbgoal)).
            - Grid Infrastructure only. For an existing service, V(LONG) is assumed
              when not set, so the goal of the service is reset to V(LONG).
        type: str
        required: false
        aliases: ['clb']
    rlbgoal:
        description:
            - The runtime load balancing goal, e.g. V(NONE), V(SERVICE_TIME) or
              V(THROUGHPUT) (C(srvctl -rlbgoal)).
            - Grid Infrastructure only. For an existing service, V(NONE) is assumed
              when not set, so the goal of the service is reset to V(NONE).
        type: str
        required: false
        aliases: ['rlb']
    force:
        description:
            - Adds the C(-f) flag to C(srvctl remove service) with O(state=absent).
            - Grid Infrastructure only.
        type: bool
        required: false
        default: false
    user:
        description:
            - The Oracle user name to connect to the database.
            - Only used without Grid Infrastructure.
            - Omit O(user) and O(password) to connect with an Oracle wallet.
        type: str
        required: false
        aliases: ['un', 'username']
    password:
        description:
            - The Oracle user password for O(user).
            - Only used without Grid Infrastructure.
        type: str
        required: false
        aliases: ['pw']
    service_name:
        description:
            - The database service name to connect to.
            - Only used without Grid Infrastructure. Defaults to O(database_name).
            - When connecting with an Oracle wallet, this is the TNS alias of the
              wallet entry.
        type: str
        required: false
        aliases: ['sn']
    hostname:
        description:
            - The Oracle database host.
            - Only used without Grid Infrastructure. Ignored when connecting with an
              Oracle wallet.
        type: str
        required: false
        default: localhost
        aliases: ['host']
    port:
        description:
            - The listener port number on the host.
            - Only used without Grid Infrastructure. Ignored when connecting with an
              Oracle wallet.
        type: int
        required: false
        default: 1521
notes:
    - python-oracledb needs to be installed on systems without Grid Infrastructure,
      e.g. with the role C(opitzconsulting.ansible_oracle.pyoracledb).
      With Grid Infrastructure the module uses srvctl only.
    - python-oracledb is used in thick mode. The Oracle Client libraries must be found,
      e.g. with ORACLE_HOME and LD_LIBRARY_PATH set in the environment of the task.
    - Check mode is not supported.
requirements: [ "python-oracledb" ]
author:
    - Mikael Sandström (@oravirt)
'''

EXAMPLES = '''
- name: Create a service
  opitzconsulting.ansible_oracle.oracle_services:
    name: service1
    database_name: db1
    oracle_home: /u01/app/oracle/product/19/db1
    state: present

- name: Create and start a service
  opitzconsulting.ansible_oracle.oracle_services:
    name: service1
    database_name: db1
    oracle_home: /u01/app/oracle/product/19/db1
    state: started

- name: Stop a service
  opitzconsulting.ansible_oracle.oracle_services:
    name: service1
    database_name: db1
    oracle_home: /u01/app/oracle/product/19/db1
    state: stopped

- name: Remove a service
  opitzconsulting.ansible_oracle.oracle_services:
    name: service1
    database_name: db1
    oracle_home: /u01/app/oracle/product/19/db1
    state: absent

- name: Create a service in a RAC PDB and run it on a subset of instances
  opitzconsulting.ansible_oracle.oracle_services:
    name: service1
    database_name: raccdb
    oracle_home: /u01/app/oracle/product/19/db1
    pdb: mypdb
    preferred_instances: raccdb1
    available_instances: raccdb2,raccdb3
    clbgoal: SHORT
    rlbgoal: SERVICE_TIME
    state: started

- name: Show the status of a service
  opitzconsulting.ansible_oracle.oracle_services:
    name: service1
    database_name: db1
    oracle_home: /u01/app/oracle/product/19/db1
    state: status
  register: service_status
'''

RETURN = '''
msg:
    description:
        - Message describing the action that was executed.
        - With O(state=status) and Grid Infrastructure, the output of
          C(srvctl status service).
    returned: always
    type: str
    sample: "Service service1 (db1) successfully created"
'''


# Check if the service exists
def check_service_exists(cursor, module, msg, oracle_home, name, database_name):
    if gimanaged:
        command = "%s/bin/srvctl config service -d %s -s %s" % (
            oracle_home,
            database_name,
            name,
        )
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            if 'PRCR-1001' in stdout:  # <-- service doesn't exist
                return False
            else:
                msg = 'Error: command: %s. stdout: %s, stderr: %s' % (
                    command,
                    stdout,
                    stderr,
                )
                return False
        elif 'Service name: %s' % (name) in stdout:  # <-- service already exist
            # msg = 'Service %s already exists in database %s' % (name, database_name)
            return True
        else:
            msg = '%s' % (stdout)
            return True
    else:
        sql = 'select lower(name) from dba_services where lower (name) = \'%s\'' % (
            name.lower()
        )
        if execute_sql_get(module, msg, cursor, sql):
            return True
        else:
            return False


def create_service(
    cursor,
    module,
    msg,
    oracle_home,
    name,
    database_name,
    state,
    preferred_instances,
    available_instances,
    pdb,
    role,
    clbgoal,
    rlbgoal,
):
    if gimanaged:
        command = "%s/bin/srvctl add service -d %s -s %s" % (
            oracle_home,
            database_name,
            name,
        )
        if preferred_instances is not None:
            command += ' -r %s' % (preferred_instances)

        if available_instances is not None:
            command += ' -a %s' % (available_instances)

        if pdb is not None:
            command += ' -pdb %s' % (pdb)

        if role is not None:
            command += ' -l %s' % (role)

        if clbgoal is not None:
            command += ' -clbgoal %s' % (clbgoal)

        if rlbgoal is not None:
            command += ' -rlbgoal %s' % (rlbgoal)

        # module.fail_json(msg=command)
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            if 'PRKO-3117' in stdout:  # <-- service already exist
                msg = 'Service %s already exists in database %s' % (name, database_name)
                module.exit_json(msg=msg, changed=False)
            else:
                msg = 'Error: %s, command is %s' % (stdout, command)
                return False
        else:
            if pdb is not None:
                database_name = pdb
            return True
    else:
        # if pdb is not None:
        #    database_name = pdb:

        sql = 'BEGIN dbms_service.create_service('
        sql_end = '); END;'
        sql += 'service_name => \'%s\', network_name => \'%s\'' % (name, name)
        sql += sql_end

        if execute_sql(module, msg, cursor, sql):
            return True
        else:
            return False


def ensure_service_state(
    cursor,
    module,
    msg,
    oracle_home,
    name,
    database_name,
    state,
    preferred_instances,
    available_instances,
    pdb,
    role,
    clbgoal,
    rlbgoal,
):
    configchange = False
    if not newservice:
        _wanted_ai = ['']
        _wanted_pi = ['']
        _wanted_config = {}
        if rlbgoal is not None:
            _wanted_config['rlb'] = rlbgoal
        else:
            _wanted_config['rlb'] = 'NONE'
            rlbgoal = 'NONE'
        if clbgoal is not None:
            _wanted_config['clb'] = clbgoal
        else:
            _wanted_config['clb'] = 'LONG'
            clbgoal = 'LONG'

        modify_conf = '%s/bin/srvctl modify service -d %s -s %s' % (
            oracle_home,
            database_name,
            name,
        )
        modify_inst = '%s/bin/srvctl modify service -d %s -s %s -modifyconfig' % (
            oracle_home,
            database_name,
            name,
        )
        _inst_temp = ""
        _conf_temp = ""
        total_mod = []

        if available_instances and available_instances is not None:
            _wanted_ai = available_instances.split(',')
        if preferred_instances and preferred_instances is not None:
            _wanted_pi = preferred_instances.split(',')

        _curr_config, _curr_config_ai, _curr_config_pi = _get_service_config(
            cursor, module, msg, oracle_home, name, database_name
        )

        # Compare instance configurations
        if _wanted_pi != _curr_config_pi:
            _inst_temp += ' -preferred %s' % (preferred_instances)
        if _wanted_ai != _curr_config_ai and '' not in _wanted_ai:
            _inst_temp += ' -available %s' % (available_instances)

        if len(_inst_temp) > 0:
            modify_inst += _inst_temp
            total_mod.append(modify_inst)

        # Compare other configuration
        if not _wanted_config == _curr_config:
            _conf_temp += ' -clbgoal %s -rlbgoal %s' % (clbgoal, rlbgoal)
            # if clbgoal is not None:
            #     _conf_temp += ' -clbgoal %s ' % (clbgoal)
            # if rlbgoal is not None:
            #     _conf_temp += ' -rlbgoal %s' % (rlbgoal)
            modify_conf += _conf_temp
            total_mod.append(modify_conf)

        # module.exit_json(msg="%s, %s, %s"
        #   % (total_mod, _wanted_config, _curr_config))
        if len(total_mod) > 0:
            for cmd in total_mod:
                (rc, stdout, stderr) = module.run_command(cmd)
                if rc != 0:
                    if rc != 0:
                        msg = (
                            "Error modifying service. Command: %s, stdout: %s, "
                            "stderr: %s" % (cmd, stdout, stderr)
                        )
                        module.fail_json(msg=msg, changed=False)
            configchange = True

    if state == 'present':
        if newservice:
            module.exit_json(
                msg="Service %s (%s) successfully created" % (name, database_name),
                changed=True,
            )
        else:
            msg = "Service %s (%s) is in the intended state" % (name, database_name)
            if configchange:
                msg += 'after configchanges had been applied'
                change = True
            module.exit_json(msg=msg, changed=change)

    if state == 'started':
        change = False
        if start_service(
            cursor, module, msg, oracle_home, name, database_name, configchange
        ):
            change = True
            msg = 'Service %s (%s) successfully created/started' % (name, database_name)
            if configchange:
                msg += ' and config changes have been applied'
                change = True
            module.exit_json(msg=msg, changed=change)

    if state == 'stopped':
        if stop_service(cursor, module, msg, oracle_home, name, database_name):
            msg = 'Service %s (%s) successfully stopped' % (name, database_name)
            change = True
            if configchange:
                msg += ' and config changes have been applied'
                change = True
            module.exit_json(msg=msg, changed=change)
        else:
            msg = 'Service %s (%s) already stopped' % (name, database_name)
            change = False
            if configchange:
                msg += ' but config changes have been applied'
                change = True
            module.exit_json(msg=msg, changed=change)


def remove_service(cursor, module, msg, oracle_home, name, database_name, force):
    stop_service(cursor, module, msg, oracle_home, name, database_name)
    if gimanaged:
        command = "%s/bin/srvctl remove service -d %s -s %s" % (
            oracle_home,
            database_name,
            name,
        )
        if force:
            command += ' -f'

        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            if 'PRCR-1001' in stdout:  # <-- service doesn' exist
                return False
            else:
                msg = 'Removal of service %s in database %s failed: %s' % (
                    name,
                    database_name,
                    stdout,
                )
                module.fail_json(msg=msg, changed=False)
        else:
            return True
    else:
        sql = 'BEGIN dbms_service.delete_service('
        sql_end = '); END;'
        sql += 'service_name => \'%s\'' % (name)
        sql += sql_end

        if execute_sql(module, msg, cursor, sql):
            return True
        else:
            return False


def _get_service_config(cursor, module, msg, oracle_home, name, database_name):
    _curr_config_dict = {}
    _curr_config_inst_ai = []
    _curr_config_inst_pi = []
    command = '%s/bin/srvctl config service -d %s -s %s' % (
        oracle_home,
        database_name,
        name,
    )
    (rc, stdout, stderr) = module.run_command(command)
    if rc != 0:
        msg = (  # noqa
            "Error getting service configuration. Command: %s, stdout: %s, stderr: %s"
            % (command, stdout, stderr)
        )

    for l in stdout.splitlines():  # noqa E741
        a = l.split(': ')
        if a[0] == 'Connection Load Balancing Goal':
            _curr_config_dict['clb'] = a[1]
        if a[0] == 'Runtime Load Balancing Goal':
            _curr_config_dict['rlb'] = a[1]
        if a[0] == 'Available instances':
            _curr_config_inst_ai = a[1].split(',')
        if a[0] == 'Preferred instances':
            _curr_config_inst_pi = a[1].split(',')

    return _curr_config_dict, _curr_config_inst_ai, _curr_config_inst_pi


def check_service_status(cursor, module, msg, oracle_home, name, database_name, state):
    if gimanaged:
        command = "%s/bin/srvctl status service -d %s -s %s" % (
            oracle_home,
            database_name,
            name,
        )
        (rc, stdout, stderr) = module.run_command(command)

        if rc != 0:
            msg = 'Checking status of service %s in database %s failed: %s' % (
                name,
                database_name,
                stdout,
            )
            module.fail_json(msg=msg, changed=False)

        elif state == "status":
            module.exit_json(msg=stdout.rstrip('\n'), changed=False)

        elif 'is not running' in stdout:
            return False
        else:
            # msg = 'service %s already running in database %s' % (name,database_name)
            return True
    else:
        sql = '''
            select lower(s.name)
            from v$active_services s
            where lower(s.name) = \'%s\'
              ''' % (
            name.lower()
        )
        # if execute_sql_get(module, msg, cursor, sql):
        if execute_sql_get(module, msg, cursor, sql):
            return True
        else:
            return False


def start_service(cursor, module, msg, oracle_home, name, database_name, configchange):
    if gimanaged:
        command = "%s/bin/srvctl start service -d %s -s %s" % (
            oracle_home,
            database_name,
            name,
        )
        (rc, stdout, stderr) = module.run_command(command)
        if rc != 0:
            if 'PRCR-1001' in stdout:
                msg = 'Service %s doesn\'t exist in database %s' % (name, database_name)
                module.fail_json(msg=msg, changed=False)
            elif (
                'PRCC-1014' in stdout or 'PRCR-1120' in stdout
            ):  # <-- service already running
                msg = 'Service %s (%s) already running' % (name, database_name)
                change = False
                if configchange:
                    msg += ' but config changes have been applied'
                    change = True
                module.exit_json(msg=msg, changed=change)
            else:
                msg = 'Starting service %s in database %s failed: %s' % (
                    name,
                    database_name,
                    stdout,
                )
                module.fail_json(msg=msg, changed=False)

        else:
            return True
    else:
        if check_service_exists(cursor, module, msg, oracle_home, name, database_name):
            if not check_service_status(
                cursor, module, msg, oracle_home, name, database_name, 'status'
            ):
                sql = 'BEGIN dbms_service.start_service('
                sql_end = '); END;'
                sql += 'service_name => \'%s\'' % (name)
                sql += sql_end

                if execute_sql(module, msg, cursor, sql):
                    return True
                else:
                    return False
            else:
                return False
        else:
            msg = 'Service %s doesn\'t exist in database %s' % (name, database_name)
            module.fail_json(msg=msg, changed=False)


def stop_service(cursor, module, msg, oracle_home, name, database_name):
    if gimanaged:
        command = "%s/bin/srvctl stop service -d %s -s %s" % (
            oracle_home,
            database_name,
            name,
        )
        (rc, stdout, stderr) = module.run_command(command)

        if rc != 0:
            if (
                'PRCR-1005' in stdout or 'CRS-2500' or 'PRCD-1316' in stdout
            ):  # Already stopped
                return False
            elif 'PRCR-1001' in stdout or 'PRCD-1132' in stdout:
                msg = 'Service %s doesn\'t exist in database %s' % (name, database_name)
                module.exit_json(msg=msg, changed=False)
            else:
                msg = 'Stopping service %s (%s) failed: %s' % (
                    name,
                    database_name,
                    stdout,
                )
                module.fail_json(msg=msg, changed=False)
        else:
            return True
    else:
        if check_service_exists(cursor, module, msg, oracle_home, name, database_name):
            if check_service_status(
                cursor, module, msg, oracle_home, name, database_name, 'status'
            ):
                sql = 'BEGIN dbms_service.stop_service('
                sql_end = '); END;'
                sql += 'service_name => \'%s\'' % (name)
                sql += sql_end

                if execute_sql(module, msg, cursor, sql):
                    return True
                else:
                    return False
            else:
                return False
        else:
            msg = 'Service %s doesn\'t exist in database %s' % (name, database_name)
            module.exit_json(msg=msg, changed=False)


def execute_sql_get(module, msg, cursor, sql):
    # module.exit_json(msg="In execute_sql_get %s" % sql, changed=False)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()  # noqa F841

    except oracledb.DatabaseError as exc:
        (dberror,) = exc.args
        if dberror.code == 1403:
            # no_data_found
            return False

    except oracledb.DatabaseError as exc:
        (error,) = exc.args
        msg = 'Something went wrong while executing sql_get - %s sql: %s' % (
            error.message,
            sql,
        )
        module.fail_json(msg=msg, changed=False)
        return False

    # we had no error fetching the row from database
    # => True
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


def main():
    global msg

    msg = ['']
    cursor = None
    global gimanaged
    global newservice
    global configchange
    configchange = False
    newservice = False
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['service']),
            oracle_home=dict(default=None, aliases=['oh']),
            database_name=dict(required=True, aliases=['db']),
            state=dict(
                default="present",
                choices=[
                    "present",
                    "absent",
                    "started",
                    "stopped",
                    "status",
                    "restarted",
                ],
            ),
            preferred_instances=dict(required=False, aliases=['pi']),
            available_instances=dict(required=False, aliases=['ai']),
            pdb=dict(required=False),
            role=dict(
                required=False,
                choices=[
                    "primary",
                    "physical_standby",
                    "logical_standby",
                    "snapshot_standby",
                ],
            ),
            clbgoal=dict(required=False, aliases=['clb']),
            rlbgoal=dict(required=False, aliases=['rlb']),
            force=dict(default=False, type='bool'),
            user=dict(required=False, aliases=['un', 'username']),
            password=dict(required=False, no_log=True, aliases=['pw']),
            service_name=dict(required=False, aliases=['sn']),
            hostname=dict(required=False, default='localhost', aliases=['host']),
            port=dict(required=False, default=1521),
        ),
    )

    name = module.params["name"]
    oracle_home = module.params["oracle_home"]
    database_name = module.params["database_name"]
    state = module.params["state"]
    preferred_instances = module.params["preferred_instances"]
    available_instances = module.params["available_instances"]
    pdb = module.params["pdb"]
    role = module.params["role"]
    clbgoal = module.params["clbgoal"]
    rlbgoal = module.params["rlbgoal"]
    force = module.params["force"]
    user = module.params["user"]
    password = module.params["password"]
    service_name = module.params["service_name"]
    hostname = module.params["hostname"]
    port = module.params["port"]

    # ld_library_path = '%s/lib' % (oracle_home)
    if oracle_home is not None:
        os.environ['ORACLE_HOME'] = oracle_home
        # os.environ['LD_LIBRARY_PATH'] = ld_library_path
    elif 'ORACLE_HOME' in os.environ:
        oracle_home = os.environ['ORACLE_HOME']
        # ld_library_path = os.environ['LD_LIBRARY_PATH']
    else:
        msg = 'ORACLE_HOME variable not set. Please set it and re-run the command'
        module.fail_json(msg=msg, changed=False)

    # Decide whether to use srvctl or sqlplus
    if os.path.exists('/etc/oracle/olr.loc'):
        gimanaged = True
    else:
        gimanaged = False
        # Without GI the services are managed with DBMS_SERVICE => database connection.
        # The module has no option mode => normal connection
        if not service_name:
            service_name = database_name

        if pdb and not service_name:
            service_name = pdb
            database_name = pdb

        conn = oracledb_connect(
            module, hostname, port, service_name, user, password, 'normal'
        )
        cursor = conn.cursor()

    if state in ('present', 'started', 'stopped'):
        if not check_service_exists(
            cursor, module, msg, oracle_home, name, database_name
        ):
            if create_service(
                cursor,
                module,
                msg,
                oracle_home,
                name,
                database_name,
                state,
                preferred_instances,
                available_instances,
                pdb,
                role,
                clbgoal,
                rlbgoal,
            ):
                newservice = True
                ensure_service_state(
                    cursor,
                    module,
                    msg,
                    oracle_home,
                    name,
                    database_name,
                    state,
                    preferred_instances,
                    available_instances,
                    pdb,
                    role,
                    clbgoal,
                    rlbgoal,
                )
            else:
                module.fail_json(msg=msg, changed=False)
        else:
            ensure_service_state(
                cursor,
                module,
                msg,
                oracle_home,
                name,
                database_name,
                state,
                preferred_instances,
                available_instances,
                pdb,
                role,
                clbgoal,
                rlbgoal,
            )
            # msg = 'Service %s already exists in database %s' % (name, database_name)
            # module.exit_json(msg=msg, changed=False)

    elif state == 'absent':
        if check_service_exists(cursor, module, msg, oracle_home, name, database_name):
            if remove_service(
                cursor, module, msg, oracle_home, name, database_name, force
            ):
                msg = 'Service %s (%s) successfully removed' % (name, database_name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.exit_json(msg=msg, changed=False)
        else:
            msg = 'Service %s (%s) doesn\'t exist' % (name, database_name)
            module.exit_json(msg=msg, changed=False)

    # elif state == 'started':
    #     if start_service(cursor, module, msg, oracle_home, name, database_name):
    #         msg = (
    #             "Service %s started successfully in database %s"
    #               ) % (name, database_name)
    #         module.exit_json(msg=msg, changed=True)
    #     else:
    #         msg = "Service %s already running in database %s" % (name, database_name)
    #         module.exit_json(msg=msg, changed=False)
    #
    # elif state == 'stopped':
    #     if stop_service(cursor, module, msg, oracle_home, name, database_name):
    #         msg = (
    #             "Service %s stopped successfully in database %s
    #               ) % (name, database_name)
    #         module.exit_json(msg=msg, changed=True)
    #     else:
    #         msg = "Service %s already stopped in database %s" % (name, database_name)
    #         module.exit_json(msg=msg, changed=False)

    elif state == 'restarted':
        if stop_service(cursor, module, msg, oracle_home, name, database_name):
            if start_service(cursor, module, msg, oracle_home, name, database_name):
                msg = "Service %s restarted in database %s" % (name, database_name)
                module.exit_json(msg=msg, changed=True)
            else:
                module.fail_json(msg=msg, changed=True)
        else:
            module.fail_json(msg=msg, changed=True)

    elif state == 'status':
        if check_service_exists(cursor, module, msg, oracle_home, name, database_name):
            if check_service_status(
                cursor, module, msg, oracle_home, name, database_name, state
            ):
                msg = 'Service %s is running in database %s' % (name, database_name)
                module.exit_json(msg=msg, changed=False)
            else:
                msg = 'Service %s is not running in database %s' % (name, database_name)
                module.exit_json(msg=msg, changed=False)
        else:
            msg = "Service %s doesn\'t exist in database %s" % (name, database_name)
            module.exit_json(msg=msg, changed=False)

    module.exit_json(msg="Unhandled exit", changed=False)


if __name__ == '__main__':
    main()
