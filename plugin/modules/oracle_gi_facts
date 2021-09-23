#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: oracle_gi_facts
short_description: Returns some facts about Grid Infrastructure environment
description:
    - Returns some facts about Grid Infrastructure environment
    - Must be run on a remote host
version_added: "2.4"
options:
    oracle_home:
        description:
            - Grid Infrastructure home, can be absent if ORACLE_HOME environment variable is set
        required: false
notes:
    - Oracle Grid Infrastructure 12cR1 or later required
    - Must be run as (become) GI owner
author: Ilmar Kerm, ilmar.kerm@gmail.com, @ilmarkerm
'''

EXAMPLES = '''
---
- hosts: localhost
  vars:
    oracle_env:
      ORACLE_HOME: /u01/app/grid/product/12.1.0.2/grid
  tasks:
    - name: Return GI facts
      oracle_gi_facts:
      environment: "{{ oracle_env }}"
'''

import os, re
from socket import gethostname, getfqdn

# The following is to make the module usable in python 2.6 (RHEL6/OEL6)
# Source: http://pydoc.net/pep8radius/0.9.0/pep8radius.shell/
try:
    from subprocess import check_output, CalledProcessError
except ImportError:  # pragma: no cover
    # python 2.6 doesn't include check_output
    # monkey patch it in!
    import subprocess
    STDOUT = subprocess.STDOUT

    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:  # pragma: no cover
            raise ValueError('stdout argument not allowed, '
                             'it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                                   *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd,
                                                output=output)
        return output
    subprocess.check_output = check_output

    # overwrite CalledProcessError due to `output`
    # keyword not being available (in 2.6)
    class CalledProcessError(Exception):

        def __init__(self, returncode, cmd, output=None):
            self.returncode = returncode
            self.cmd = cmd
            self.output = output

        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" % (
                self.cmd, self.returncode)
    subprocess.CalledProcessError = CalledProcessError

def is_executable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def exec_program_lines(arguments):
    try:
        output = check_output(arguments)
        return output.splitlines()
    except CalledProcessError:
        # Just ignore the error
        return ['']

def exec_program(arguments):
    return exec_program_lines(arguments)[0]

def hostname_to_fqdn(hostname):
    if "." not in hostname:
        return getfqdn(hostname)
    else:
        return hostname

def local_listener():
    global srvctl, shorthostname, iscrs, vips
    args = [srvctl, 'status', 'listener']
    if iscrs:
        args += ['-n', shorthostname]
    listeners_out = exec_program_lines(args)
    re_listener_name = re.compile('Listener (.+) is enabled')
    listeners = []
    out = []
    for l in listeners_out:
        if "is enabled" in l:
            m = re_listener_name.search(l)
            listeners.append(m.group(1))
    for l in listeners:
        config = {}
        output = exec_program_lines([srvctl, 'config', 'listener', '-l', l])
        for line in output:
            if line.startswith('Name:'):
                config['name'] = line[6:]
            elif line.startswith('Type:'):
                config['type'] = line[6:]
            elif line.startswith('Network:'):
                config['network'] = line[9:line.find(',')]
            elif line.startswith('End points:'):
                config['endpoints'] = line[12:]
                for proto in config['endpoints'].split('/'):
                    p = proto.split(':')
                    config[p[0].lower()] = p[1]
        if "network" in config.keys():
            config['address'] = vips[config['network']]['fqdn']
            config['ipv4'] = vips[config['network']]['ipv4']
            config['ipv6'] = vips[config['network']]['ipv6']
        out.append(config)
    return out

def scan_listener():
    global srvctl, shorthostname, iscrs, networks, scans
    out = {}
    for n in networks.keys():
        output = exec_program_lines([srvctl, 'config', 'scan_listener', '-k', n])
        for line in output:
            endpoints = None
            # 19c
            m = re.search('Endpoints: (.+)', line)
            if m is not None:
                endpoints = m.group(1)
            else:
                # 18c, 12c
                m = re.search('SCAN Listener (.+) exists. Port: (.+)', line)
                if m is not None:
                    endpoints = m.group(2)
            if endpoints:
                out[n] = {'network': n, 'scan_address': scans[n]['fqdn'], 'endpoints': endpoints, 'ipv4': scans[n]['ipv4'], 'ipv6': scans[n]['ipv6']}
                for proto in endpoints.split('/'):
                    p = proto.split(':')
                    out[n][p[0].lower()] = p[1]
                break
    return out

def get_networks():
    global srvctl, shorthostname, iscrs
    out = {}
    item = {}
    output = exec_program_lines([srvctl, 'config', 'network'])
    for line in output:
        m = re.search('Network ([0-9]+) exists', line)
        if m is not None:
            if "network" in item.keys():
                out[item['network']] = item
            item = {'network': m.group(1)}
        elif line.startswith('Subnet IPv4:'):
            item['ipv4'] = line[13:]
        elif line.startswith('Subnet IPv6:'):
            item['ipv6'] = line[13:]
    if "network" in item.keys():
        out[item['network']] = item
    return out

def get_vips():
    global srvctl, shorthostname, iscrs
    output = exec_program_lines([srvctl, 'config', 'vip', '-n', shorthostname])
    vip = {}
    out = {}
    for line in output:
        if line.startswith('VIP exists:'):
            if "network" in vip.keys():
                out[vip['network']] = vip
            vip = {}
            m = re.search('network number ([0-9]+),', line)
            vip['network'] = m.group(1)
        elif line.startswith('VIP Name:'):
            vip['name'] = line[10:]
            vip['fqdn'] = hostname_to_fqdn(vip['name'])
        elif line.startswith('VIP IPv4 Address:'):
            vip['ipv4'] = line[18:]
        elif line.startswith('VIP IPv6 Address:'):
            vip['ipv6'] = line[18:]
    if "network" in vip.keys():
        out[vip['network']] = vip
    return out
    
def get_scans():
    global srvctl, shorthostname, iscrs
    out = {}
    item = {}
    output = exec_program_lines([srvctl, 'config', 'scan', '-all'])
    for line in output:
        if line.startswith('SCAN name:'):
            if "network" in item.keys():
                out[item['network']] = item
            m = re.search('SCAN name: (.+), Network: ([0-9]+)', line)
            item = {'network': m.group(2), 'name': m.group(1), 'ipv4': [], 'ipv6': []}
            item['fqdn'] = hostname_to_fqdn(item['name'])
        else:
            m = re.search('SCAN [0-9]+ (IPv[46]) VIP: (.+)', line)
            if m is not None:
                item[m.group(1).lower()] += [m.group(2)]
    if "network" in item.keys():
        out[item['network']] = item
    return out
    
# Ansible code
def main():
    global module, shorthostname, hostname, srvctl, crsctl, cemutlo, iscrs, vips, networks, scans
    msg = ['']
    module = AnsibleModule(
        argument_spec = dict(
            oracle_home = dict(required=False)
        ),
        supports_check_mode=True
    )
    # Preparation
    facts = {}
    if module.params["oracle_home"]:
        os.environ['ORACLE_HOME'] = module.params["oracle_home"]
    srvctl = os.path.join(os.environ['ORACLE_HOME'], 'bin', 'srvctl')
    crsctl = os.path.join(os.environ['ORACLE_HOME'], 'bin', 'crsctl')
    cemutlo = os.path.join(os.environ['ORACLE_HOME'], 'bin', 'cemutlo')
    if not is_executable(srvctl) or not is_executable(crsctl):
        module.fail_json(changed=False, msg="Are you sure ORACLE_HOME=%s points to GI home? I can't find executables srvctl or crsctl under bin/." % os.environ['ORACLE_HOME'])
    iscrs = True # This needs to be dynamically set if it is full clusterware or Oracle restart
    hostname = gethostname()
    shorthostname = hostname.split('.')[0]
    #
    if module.check_mode:
        module.exit_json(changed=False)
    # Cluster name
    if iscrs:
        facts.update({'clustername': exec_program([cemutlo, '-n'])})
    else:
        facts.update({'clustername': 'ORACLE_RESTART'})
    # Cluster version
    if iscrs:
        version = exec_program([crsctl, 'query','crs','activeversion'])
    else:
        version = exec_program([crsctl, 'query','has','releaseversion'])
    m = re.search('\[([0-9\.]+)\]$', version)
    facts.update({'version': m.group(1)})
    # VIPS
    vips = get_vips()
    facts.update({'vip': vips.values()})
    # Networks
    networks = get_networks()
    facts.update({'network': networks.values()})
    # SCANs
    scans = get_scans()
    facts.update({'scan': scans.values()})
    # Listener
    facts.update({'local_listener': local_listener()})
    facts.update({'scan_listener': scan_listener().values() if iscrs else []})
    # Databases
    facts.update({'database_list': exec_program_lines([srvctl, 'config', 'database'])})
    # Output
    module.exit_json(msg=", ".join(msg), changed=False, ansible_facts=facts)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
