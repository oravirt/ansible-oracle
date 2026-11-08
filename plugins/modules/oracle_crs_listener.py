#!/usr/bin/python
# -*- coding: utf-8 -*-

# Based on oracle_crs_listener from ibre5041.ansible_oracle_modules (Ivan Brezina)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: oracle_crs_listener
short_description: >-
  Manage listener resources in Oracle Grid Infrastructure / Oracle Restart
description:
  - Add, modify, remove, enable/disable, start, stop and restart listener resources
    (C(ora.<name>.lsnr)) with srvctl.
  - The current configuration is read with C(crsctl stat res -p).
  - The Grid Infrastructure home is read from C(crs_home) in C(/etc/oracle/olr.loc).
version_added: "4.18.0"
options:
  name:
    description:
      - Listener name.
    type: str
    default: LISTENER
  state:
    description:
      - C(present) adds or modifies the listener resource and starts it,
        the same as C(started).
        A disabled listener (I(enabled=false)) is not started.
      - C(started) and C(stopped) ensure the running state after add/modify.
        Use C(stopped) to add a listener without starting it.
      - C(restarted) stops (when running) and starts the listener, always C(changed).
      - C(absent) removes the listener resource (stopped before with I(force)).
    type: str
    choices: ['present', 'absent', 'started', 'stopped', 'restarted']
    default: present
  enabled:
    description:
      - Enables or disables the listener resource.
    type: bool
    default: true
  oraclehome:
    description:
      - ORACLE_HOME of the listener.
      - When not set, the ORACLE_HOME of an existing listener is not changed and a new
        listener is added in the Grid Infrastructure home.
      - The path of the Grid Infrastructure home and C(%CRS_HOME%) are the same.
      - C(srvctl add/modify listener) is executed with C(srvctl) of this ORACLE_HOME
        (C(srvctl) of the Grid Infrastructure home fails for an older database home
        with C(PRCN-3018)).
    type: str
    aliases: ['oracle_home']
  endpoints:
    description:
      - "Comma separated TCP ports or listener endpoints:
        C([TCP:]<port>[, ...][/IPC:<key>][/NMP:<pipe_name>][/TCPS:<s_port>]
        [/SDP:<port>][/EXADIRECT:<port>])"
      - A port without protocol is TCP, e.g. C(1521) is the same as C(TCP:1521).
      - When not set, the endpoints of an existing listener are not changed.
    type: str
  skip:
    description:
      - Skip the checking of ports (C(srvctl add listener -skip)).
    type: bool
    default: false
  force:
    description:
      - Remove the listener with C(-force) (stops a running listener).
    type: bool
    default: true
notes:
  - Must be executed as owner of Grid Infrastructure / Oracle Restart.
  - Supports check mode.
author:
  - Ivan Brezina
  - Thorsten Bruhns
'''

EXAMPLES = '''
- name: Register and start listener LISTENER with port 1521
  opitzconsulting.ansible_oracle.oracle_crs_listener:
    name: LISTENER
    endpoints: TCP:1521
    enabled: true

- name: Add listener LISTENER_DB in a database home without starting it
  opitzconsulting.ansible_oracle.oracle_crs_listener:
    name: LISTENER_DB
    oraclehome: /u01/app/oracle/product/19/db_19.33
    endpoints: "1523"
    state: stopped

- name: Add and start listener ASM_LISTENER
  opitzconsulting.ansible_oracle.oracle_crs_listener:
    name: ASM_LISTENER
    endpoints: "1522"
    state: started

- name: Restart listener ASM_LISTENER
  opitzconsulting.ansible_oracle.oracle_crs_listener:
    name: ASM_LISTENER
    state: restarted

- name: Remove listener ASM_LISTENER
  opitzconsulting.ansible_oracle.oracle_crs_listener:
    name: ASM_LISTENER
    state: absent
'''

RETURN = '''
commands:
  description: srvctl commands executed (or to be executed in check mode)
  returned: always
  type: list
  elements: str
listener:
  description: >-
    configuration of the listener resource before the change
    (empty when not existing)
  returned: always
  type: dict
  contains:
    name:
      description: listener name
      type: str
    oracle_home:
      description: >-
        ORACLE_HOME of the listener
        (C(%CRS_HOME%) for the Grid Infrastructure home)
      type: str
    endpoints:
      description: endpoints of the listener
      type: str
    enabled:
      description: listener resource is enabled
      type: bool
'''

CRS_HOME_PLACEHOLDER = '%CRS_HOME%'
OLR_LOC = '/etc/oracle/olr.loc'


def normalize_endpoints(endpoints):
    """Normalize an endpoint string for comparison.

    '1521' => 'TCP:1521', 'tcp:1521, 1522/ipc:key' => 'TCP:1521,1522/IPC:key'
    """
    if not endpoints:
        return None
    parts = []
    for part in endpoints.split('/'):
        part = part.strip()
        if not part:
            continue
        if ':' in part:
            proto, value = part.split(':', 1)
            proto = proto.strip().upper()
        else:
            proto, value = ('TCP', part)
        value = ','.join(v.strip() for v in value.split(',') if v.strip())
        parts.append('{0}:{1}'.format(proto, value))
    return '/'.join(parts)


def parse_crs_resources(stdout):
    """Parse 'crsctl stat res -p' into a list of dicts (one per resource).

    Resources are separated by empty lines. The last resource is added, even when the
    output does not end with an empty line.
    """
    resources = []
    resource = {}
    for line in stdout.splitlines():
        line = line.strip()
        if '=' not in line:
            if resource:
                resources.append(resource)
            resource = {}
            continue
        key, value = line.split('=', 1)
        resource[key] = value
    if resource:
        resources.append(resource)
    return [r for r in resources if 'NAME' in r]


class OracleCrsListener(object):

    def __init__(self, module, crs_home):
        self.module = module
        self.crs_home = crs_home.rstrip('/')
        self.crsctl = os.path.join(self.crs_home, 'bin', 'crsctl')
        self.srvctl = os.path.join(self.crs_home, 'bin', 'srvctl')
        self.name = module.params['name']
        self.commands = []
        self.changed = False
        # srvctl/crsctl must not use ORACLE_HOME, TNS_ADMIN or LD_LIBRARY_PATH
        # of a database home
        self.env = {
            'ORACLE_HOME': self.crs_home,
            'LD_LIBRARY_PATH': os.path.join(self.crs_home, 'lib'),
        }
        self.current = self.get_listener()

    def fail(self, msg, **kwargs):
        self.module.fail_json(
            msg=msg, commands=self.commands, changed=self.changed, **kwargs
        )

    def run(self, command, env=None):
        return self.module.run_command(command, environ_update=env or self.env)

    def home_srvctl(self, home):
        """srvctl and environment of the ORACLE_HOME of a listener.

        srvctl add/modify listener must be executed from the ORACLE_HOME
        of the listener:
        srvctl of the GI home fails for a listener in an older database home
        (PRCN-3018 : Addition of listener version ... is not allowed
        using srvctl version ...).
        """
        if not home or self.same_home(home, CRS_HOME_PLACEHOLDER):
            return self.srvctl, self.env
        home = home.rstrip('/')
        srvctl = os.path.join(home, 'bin', 'srvctl')
        if not os.access(srvctl, os.X_OK):
            self.fail('{0} not found or not executable'.format(srvctl))
        return srvctl, {
            'ORACLE_HOME': home,
            'LD_LIBRARY_PATH': os.path.join(home, 'lib'),
        }

    def run_change_command(self, command, env=None):
        self.commands.append(' '.join(command))
        self.changed = True
        if self.module.check_mode:
            return 0, '', ''
        rc, stdout, stderr = self.run(command, env)
        if rc != 0:
            self.fail(
                'srvctl failed({0}): {1} {2}'.format(
                    rc, stdout.strip(), stderr.strip()
                ),
                rc=rc,
                stdout=stdout,
                stderr=stderr,
            )
        for line in stderr.splitlines():
            if line.strip():
                self.module.warn(line)
        return rc, stdout, stderr

    def get_listener(self):
        command = [self.crsctl, 'stat', 'res', '-p', '-w', '(TYPE = ora.listener.type)']
        rc, stdout, stderr = self.run(command)
        # CRS-2613: Could not find resource => no listener resource at all
        if rc != 0 and 'CRS-2613' not in stdout + stderr:
            self.fail(
                'Failed command: {0}: {1} {2}'.format(
                    ' '.join(command), stdout.strip(), stderr.strip()
                ),
                rc=rc,
            )
        wanted = 'ora.{0}.lsnr'.format(self.name).lower()
        for resource in parse_crs_resources(stdout):
            if resource['NAME'].lower() == wanted:
                return resource
        return {}

    def same_home(self, home1, home2):
        def norm(home):
            if not home:
                return None
            home = home.rstrip('/')
            return (
                CRS_HOME_PLACEHOLDER
                if home in (CRS_HOME_PLACEHOLDER, self.crs_home)
                else home
            )

        return norm(home1) == norm(home2)

    def listener_info(self):
        if not self.current:
            return {}
        return {
            'name': self.name,
            'oracle_home': self.current.get('ORACLE_HOME'),
            'endpoints': self.current.get('ENDPOINTS'),
            'enabled': self.current.get('ENABLED', '1') == '1',
        }

    def configure(self):
        state = self.module.params['state']
        oraclehome = self.module.params['oraclehome']
        endpoints = self.module.params['endpoints']

        if state == 'absent':
            if self.current:
                command = [self.srvctl, 'remove', 'listener', '-listener', self.name]
                if self.module.params['force']:
                    command.append('-force')
                self.run_change_command(command)
            return

        if not self.current:
            # srvctl of the new ORACLE_HOME of the listener (GI home without oraclehome)
            srvctl, env = self.home_srvctl(oraclehome)
            command = [srvctl, 'add', 'listener', '-listener', self.name]
            if oraclehome and not self.same_home(oraclehome, CRS_HOME_PLACEHOLDER):
                command.extend(['-oraclehome', oraclehome])
            if endpoints:
                command.extend(['-endpoints', endpoints])
            if self.module.params['skip']:
                command.append('-skip')
            self.run_change_command(command, env)
            return

        # srvctl of the target ORACLE_HOME:
        # oraclehome or the current ORACLE_HOME of the listener
        srvctl, env = self.home_srvctl(oraclehome or self.current.get('ORACLE_HOME'))
        command = [srvctl, 'modify', 'listener', '-listener', self.name]
        modify = False
        if oraclehome and not self.same_home(
            oraclehome, self.current.get('ORACLE_HOME')
        ):
            command.extend(['-oraclehome', oraclehome])
            modify = True
        if endpoints and normalize_endpoints(endpoints) != normalize_endpoints(
            self.current.get('ENDPOINTS')
        ):
            command.extend(['-endpoints', endpoints])
            modify = True
        if modify:
            self.run_change_command(command, env)

    def is_running(self):
        command = [self.srvctl, 'status', 'listener', '-listener', self.name]
        rc, stdout, stderr = self.run(command)
        for line in stdout.splitlines():
            if 'is not running' in line:
                return False
            if 'is running' in line:
                return True
        if self.module.check_mode and not self.current:
            # listener would be added => not running
            return False
        self.fail(
            'Could not check if listener {0} is running: {1} {2}'.format(
                self.name, stdout.strip(), stderr.strip()
            ),
            rc=rc,
        )

    def ensure_state(self):
        state = self.module.params['state']
        if state == 'absent':
            return

        # a new listener is enabled after srvctl add listener
        enabled = self.current.get('ENABLED', '1') == '1'
        if self.module.params['enabled'] and not enabled:
            self.run_change_command(
                [self.srvctl, 'enable', 'listener', '-listener', self.name]
            )
        elif not self.module.params['enabled'] and enabled:
            self.run_change_command(
                [self.srvctl, 'disable', 'listener', '-listener', self.name]
            )

        # present = started: a listener is rarely added without starting it,
        # a disabled listener cannot be started => running state unchanged
        if state == 'present':
            if not self.module.params['enabled']:
                return
            state = 'started'

        running = self.is_running()
        if state == 'stopped' and running:
            self.run_change_command(
                [self.srvctl, 'stop', 'listener', '-listener', self.name]
            )
        elif state == 'started' and not running:
            self.run_change_command(
                [self.srvctl, 'start', 'listener', '-listener', self.name]
            )
        elif state == 'restarted':
            if running:
                self.run_change_command(
                    [self.srvctl, 'stop', 'listener', '-listener', self.name]
                )
            self.run_change_command(
                [self.srvctl, 'start', 'listener', '-listener', self.name]
            )


# The Grid Infrastructure home is always crs_home from olr.loc:
# there is only one Grid Infrastructure / Oracle Restart per host.
def get_crs_home(module):
    crs_home = None
    try:
        with open(OLR_LOC) as f:
            for line in f:
                if line.startswith('crs_home='):
                    crs_home = line.strip().split('=', 1)[1]
    except IOError as e:
        module.fail_json(
            msg='Oracle Grid Infrastructure / Oracle Restart not detected: {0}'.format(
                e
            ),
            changed=False,
        )
    if not crs_home:
        module.fail_json(msg='crs_home not found in {0}'.format(OLR_LOC), changed=False)
    for tool in ('crsctl', 'srvctl'):
        path = os.path.join(crs_home, 'bin', tool)
        if not os.access(path, os.X_OK):
            module.fail_json(
                msg='{0} not found or not executable'.format(path), changed=False
            )
    return crs_home


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', default='LISTENER'),
            state=dict(
                type='str',
                default='present',
                choices=['present', 'absent', 'started', 'stopped', 'restarted'],
            ),
            enabled=dict(type='bool', default=True),
            oraclehome=dict(type='str', aliases=['oracle_home']),
            endpoints=dict(type='str'),
            skip=dict(type='bool', default=False),
            force=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )

    listener = OracleCrsListener(module, get_crs_home(module))
    info = listener.listener_info()
    listener.configure()
    listener.ensure_state()

    if listener.changed:
        msg = 'Listener resource {0} was reconfigured'.format(listener.name)
    else:
        msg = 'Listener resource {0} was already in intended state'.format(
            listener.name
        )
    module.exit_json(
        msg=msg, commands=listener.commands, changed=listener.changed, listener=info
    )


if __name__ == '__main__':
    main()
