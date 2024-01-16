# orahost

Role to configure the hostsystem for ansible-oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [asmlib_rpm](#asmlib_rpm)
  - [asmlib_rpm_el6](#asmlib_rpm_el6)
  - [asmlib_rpm_el7](#asmlib_rpm_el7)
  - [asmlib_rpm_el8](#asmlib_rpm_el8)
  - [asmlib_rpm_sles](#asmlib_rpm_sles)
  - [asmlibsupport_rpm](#asmlibsupport_rpm)
  - [asmlibsupport_rpm_el6](#asmlibsupport_rpm_el6)
  - [asmlibsupport_rpm_el7](#asmlibsupport_rpm_el7)
  - [asmlibsupport_rpm_el8](#asmlibsupport_rpm_el8)
  - [configure_etc_hosts](#configure_etc_hosts)
  - [configure_hugepages](#configure_hugepages)
  - [configure_hugepages_by](#configure_hugepages_by)
  - [configure_interconnect](#configure_interconnect)
  - [configure_limits](#configure_limits)
  - [configure_limits_pam](#configure_limits_pam)
  - [configure_oracle_sudo](#configure_oracle_sudo)
  - [configure_ssh](#configure_ssh)
  - [disable_firewall](#disable_firewall)
  - [disable_numa_boot](#disable_numa_boot)
  - [disable_selinux](#disable_selinux)
  - [etc_hosts_ip](#etc_hosts_ip)
  - [extrarepos_disabled](#extrarepos_disabled)
  - [extrarepos_enabled](#extrarepos_enabled)
  - [firewall_service](#firewall_service)
  - [grid_users](#grid_users)
  - [host_fs_layout](#host_fs_layout)
  - [install_os_packages](#install_os_packages)
  - [keyfile](#keyfile)
  - [nr_hugepages](#nr_hugepages)
  - [nr_hugepages_memory](#nr_hugepages_memory)
  - [nr_hugepages_percent](#nr_hugepages_percent)
  - [old_ssh_config](#old_ssh_config)
  - [oracle_asm_packages](#oracle_asm_packages)
  - [oracle_asm_packages_sles](#oracle_asm_packages_sles)
  - [oracle_groups](#oracle_groups)
  - [oracle_hugepages](#oracle_hugepages)
  - [oracle_ic_net](#oracle_ic_net)
  - [oracle_packages](#oracle_packages)
  - [oracle_packages_sles_multi](#oracle_packages_sles_multi)
  - [oracle_sysctl](#oracle_sysctl)
  - [oracle_users](#oracle_users)
  - [os_family_supported](#os_family_supported)
  - [os_min_supported_version](#os_min_supported_version)
  - [percent_hugepages](#percent_hugepages)
  - [size_in_gb_hugepages](#size_in_gb_hugepages)
  - [ssh_keys](#ssh_keys)
  - [sudoers_template](#sudoers_template)
  - [transparent_hugepage_disable](#transparent_hugepage_disable)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### asmlib_rpm

Install oracleasm-support from RPM-Repo on OracleLinux.
Value depends on OS-Release from RHEL/OL.
Uses variables `asmlib_rpm_el6`, `asmlib_rpm_el7` or `asmlib_rpm_el8`

#### Default value

```YAML
asmlib_rpm: Value from `asmlib_rpm_el6`, `asmlib_rpm_el7` or `asmlib_rpm_el8`
```

### asmlib_rpm_el6

Name / Url for rpm oracleasm-support for RHEL6/OL6.

#### Default value

```YAML
asmlib_rpm_el6: 
  http://download.oracle.com/otn_software/asmlib/oracleasmlib-2.0.4-1.el6.x86_64.rpm
```

### asmlib_rpm_el7

Name / Url for rpm oracleasm-support for RHEL7/OL7.

#### Default value

```YAML
asmlib_rpm_el7: 
  http://download.oracle.com/otn_software/asmlib/oracleasmlib-2.0.12-1.el7.x86_64.rpm
```

### asmlib_rpm_el8

Name / Url for rpm oracleasm-support for RHEL8/OL8.

#### Default value

```YAML
asmlib_rpm_el8: 
  https://download.oracle.com/otn_software/asmlib/oracleasmlib-2.0.17-1.el8.x86_64.rpm
```

### asmlib_rpm_sles

Name / Url for rpm oracleasm-support for SLES.

#### Default value

```YAML
asmlib_rpm_sles: 
  http://oss.oracle.com/projects/oracleasm-support/dist/files/RPMS/sles12/amd64/2.1.8/oracleasm-support-2.1.8-1.SLE12.x86_64.rpm
```

### asmlibsupport_rpm

Install oracleasmlib-support from RPM-Repo on OracleLinux.
Value depends on OS-Release from RHEL/OL.

important

Do NOT set this variable.

Set the used variables `asmlibsupport_rpm_el6`, `asmlibsupport_rpm_el7` or `asmlibsupport_rpm_el8`.

#### Default value

```YAML
asmlibsupport_rpm: Value from `asmlibsupport_rpm_el6`, `asmlibsupport_rpm_el7` or
  `asmlibsupport_rpm_el8`
```

### asmlibsupport_rpm_el6

#### Default value

```YAML
asmlibsupport_rpm_el6: 
  http://oss.oracle.com/projects/oracleasm-support/dist/files/RPMS/rhel6/amd64/2.1.8/oracleasm-support-2.1.8-1.el6.x86_64.rpm
```

### asmlibsupport_rpm_el7

#### Default value

```YAML
asmlibsupport_rpm_el7: 
  https://yum.oracle.com/repo/OracleLinux/OL7/latest/x86_64/getPackage/oracleasm-support-2.1.11-2.el7.x86_64.rpm
```

### asmlibsupport_rpm_el8

#### Default value

```YAML
asmlibsupport_rpm_el8: 
  https://yum.oracle.com/repo/OracleLinux/OL8/latest/x86_64/getPackage/oracleasm-support-2.1.11-2.el8.x86_64.rpm
```

### configure_etc_hosts

Add `{{ ansible_hostname }} {{ ansible_fqdn }}` to /etc/hosts`?

#### Default value

```YAML
configure_etc_hosts: false
```

### configure_hugepages

Configure Hugepages?

#### Default value

```YAML
configure_hugepages: true
```

### configure_hugepages_by

Defines if percent_hugepages or size_in_gb_hugepages is used to define the Hugepages.
Allowed values: percentage or memory.

#### Default value

```YAML
configure_hugepages_by: memory
```

#### Example usage

```YAML
configure_hugepages_by: memory

configure_hugepages_by: percentage
```

### configure_interconnect

Should the Interconnect network be configured by Ansible

#### Default value

```YAML
configure_interconnect: false
```

### configure_limits

Configure `/etc/security.d/limits.d/99-oracle-limits.conf`?

#### Default value

```YAML
configure_limits: true
```

### configure_limits_pam

Configure `/etc/pam.d/limits`?

#### Default value

```YAML
configure_limits_pam: true
```

### configure_oracle_sudo

Add oracle to sudoers for root.

#### Default value

```YAML
configure_oracle_sudo: false
```

### configure_ssh

Should passwordless ssh be configured between clusternodes. Only applicable to RAC-installs

#### Default value

```YAML
configure_ssh: false
```

### disable_firewall

#### Default value

```YAML
disable_firewall: true
```

### disable_numa_boot

Disable numa support during boot.

#### Default value

```YAML
disable_numa_boot: true
```

### disable_selinux

#### Default value

```YAML
disable_selinux: true
```

### etc_hosts_ip

Set IP to 2nd Interface on virtualbox and 1st for all otehr installations

#### Default value

```YAML
etc_hosts_ip: "{% if 'virtualbox' in ansible_virtualization_type %}{{ ansible_all_ipv4_addresses[1]
  }}{% else %}{{ ansible_default_ipv4.address }}{% endif %}"
```

### extrarepos_disabled

List of disabled yum repos during installation for RHEL/OL.

#### Default value

```YAML
extrarepos_disabled: '[]'
```

### extrarepos_enabled

#### Default value

```YAML
extrarepos_enabled: "{%- if ansible_distribution == 'OracleLinux' -%}ol{{ ansible_distribution_major_version
  }}_addons{%- else -%}{%- endif %}"
```

### firewall_service

Used firewall service in OS. Value depends on used Distribution and version.

#### Default value

```YAML
firewall_service: firewalld or iptables
```

### grid_users

grid OS-User

#### Default value

```YAML
grid_users:
  - username: grid
    uid: 54320
    primgroup: '{{ oracle_group }}'
    othergroups: '{{ asmadmin_group }},{{ asmdba_group }},{{ asmoper_group }},{{ dba_group
      }}'
    passwd: 
      $6$0xHoAXXF$K75HKb64Hcb/CEcr3YEj2LGERi/U2moJgsCK.ztGxLsKoaXc4UBiNZPL0hlxB5ng6GL.gyipfQOOXplzcdgvD0
```

### host_fs_layout

Define physical Disk, Volume Group, logical Volume, Filesystem and swap Devices.
See example configuration

#### Default value

```YAML
host_fs_layout: '[]'
```

#### Example usage

```YAML
host_fs_layout:
  - vgname: vgora
    state: present
    filesystem:
      - { mntp: /u01, lvname: lvorabase, lvsize: 25G, fstype: xfs }
      - { mntp: /u02, lvname: lvoradata, lvsize: 25G, fstype: xfs, fsopts: "-m reflink=1 -m crc=1" }
    disk:
      - { device: /dev/sdb, pvname: /dev/sdb1 }
```

### install_os_packages

Install addional RPMs for Oracle?

#### Default value

```YAML
install_os_packages: true
```

### keyfile

#### Default value

```YAML
keyfile: /tmp/known_hosts
```

### nr_hugepages

This is an internal variable only. Do not define it!

#### Default value

```YAML
nr_hugepages: _unset_
```

### nr_hugepages_memory

This is an internal variable only. Do not define it!

#### Default value

```YAML
nr_hugepages_memory: _unset_
```

### nr_hugepages_percent

This is an internal variable only. Do not define it!

#### Default value

```YAML
nr_hugepages_percent: _unset_
```

### old_ssh_config

#### Default value

```YAML
old_ssh_config: true
```

### oracle_asm_packages

List of RPMs installed during ASM preparation for RHEL/OL.

There should be no reason to change this variable.

#### Default value

```YAML
oracle_asm_packages:
  - '{{ asmlib_rpm }}'
  - '{{ asmlibsupport_rpm }}'
  - kmod-oracleasm
```

### oracle_asm_packages_sles

List of RPMs installed during ASM preparation for SLES.

There should be no reason to change this variable.

#### Default value

```YAML
oracle_asm_packages_sles:
  - oracleasm-kmp-default
  - oracleasm-kmp-xen
  - '{{ asmlib_rpm_sles }}'
```

### oracle_groups

List of OS-groups for Oracle
Dependent variables are defined in orahost_meta/defaults/main.yml

#### Default value

```YAML
oracle_groups:
  - {group: '{{ asmdba_group }}', gid: 54318}
  - {group: '{{ asmoper_group }}', gid: 54319}
  - {group: '{{ asmadmin_group }}', gid: 54320}
  - {group: '{{ oracle_group }}', gid: 54321}
  - {group: '{{ dba_group }}', gid: 54322}
  - {group: '{{ oper_group }}', gid: 54324}
  - {group: backupdba, gid: 54323}
  - {group: dgdba, gid: 54325}
  - {group: kmdba, gid: 54326}
```

### oracle_hugepages

This is an internal variable. Do not change it!

#### Default value

```YAML
oracle_hugepages:
  - {name: vm.nr_hugepages, value: '{{ nr_hugepages }}'}
```

### oracle_ic_net

Picks the last octet from the public ip to use for
cluster-interconnect ip (e.g 3.3.3.51)

#### Default value

```YAML
oracle_ic_net: 3.3.3.{{ ansible_all_ipv4_addresses[0].split(".")[-1] }}
```

### oracle_packages

List of additinal RPMs for RHEL/OL.

`install_os_packages: true` is needed to install the RPMs.

#### Default value

```YAML
oracle_packages:
  - bind-utils
  - nfs-utils
  - util-linux-ng
  - xorg-x11-utils
  - xorg-x11-xauth
  - binutils
  - compat-libstdc++-33
  - compat-libstdc++-33.i686
  - unixODBC-devel
  - unixODBC-devel.i686
  - gcc
  - gcc-c++
  - glibc
  - glibc.i686
  - glibc-devel
  - glibc-devel.i686
  - libaio
  - libaio-devel
  - libaio.i686
  - libaio-devel.i686
  - libgcc
  - libgcc.i686
  - libstdc++
  - libstdc++-devel
  - libstdc++.i686
  - libstdc++-devel.i686
  - libXext
  - libXext.i686
  - zlib-devel
  - zlib-devel.i686
  - make
  - sysstat
  - openssh-clients
  - compat-libcap1
  - xorg-x11-xauth
  - xorg-x11-xinit
  - libXtst
  - xdpyinfo
  - xterm
  - xsetroot
  - libXp
  - libXt
  - libXau
  - libXau.i686
  - libXi
  - libXi.i686
  - libX11
  - libX11.i686
  - smartmontools
  - elfutils-libelf-devel.i686
  - elfutils-libelf-devel
  - cpp
  - lsof
```

### oracle_packages_sles_multi

List of additinal RPMs for different SLES version.

List is based on: https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/database-installation-guide-linux.pdf

`install_os_packages: true` is needed to install the RPMs.

#### Default value

```YAML
oracle_packages_sles_multi:
  - name: SLES common packages
    condition: true
    packages:
      - bc
      - binutils
      - glibc
      - glibc-devel
      - libaio-devel
      - libaio1
      - libcap-ng-utils
      - libcap-ng0
      - libcap-progs
      - libcap2
      - libgcc_s1
      - libpcap1
      - libpcre1
      - libpcre16-0
      - libpng16-16
      - libstdc++6
      - libtiff5
      - libXau6
      - libXrender1
      - libXtst6
      - make
      - mksh
      - pixz
      - rdma-core
      - rdma-core-devel
      - smartmontools
      - sysstat
      - xorg-x11-libs
      - xz
  - name: SLES 12 packages
    condition: "{{ ansible_distribution_major_version == '12' }}"
    packages:
      - libcap1
      - libelf-devel
      - libjpeg-turbo
      - libjpeg62
      - libjpeg62-turbo
      - libX11
  - name: SLES 15 packages
    condition: "{{ ansible_distribution_major_version == '15' }}"
    packages:
      - insserv-compat
      - libelf1
      - libgfortran4
      - libjpeg8
      - libX11-6
      - libXext-devel
      - libXext6
      - libXi-devel
      - libXi6
      - libXrender-devel
  - name: SLES 15 SP3+ extra packages
    condition: "{{ ansible_distribution_version is version('15.3', 'ge') }}"
    packages:
      - compat-libpthread-nonshared
```

### oracle_sysctl

Configure parameter in sysctl.

_Important_

Do not add configurations for Hugepages here!

#### Default value

```YAML
oracle_sysctl:
  - {name: kernel.shmall, value: 4294967296}
  - {name: kernel.shmmax, value: 68719476736}
  - {name: kernel.shmmni, value: 4096}
  - {name: kernel.sem, value: 250 32000 100 128}
  - {name: fs.file-max, value: 6815744}
  - {name: fs.aio-max-nr, value: 3145728}
  - {name: net.ipv4.ip_local_port_range, value: 9000 65500}
  - {name: net.core.rmem_default, value: 262144}
  - {name: net.core.rmem_max, value: 4194304}
  - {name: net.core.wmem_default, value: 262144}
  - {name: net.core.wmem_max, value: 1048576}
  - {name: kernel.panic_on_oops, value: 1}
  - {name: vm.min_free_kbytes, value: 524288}
```

### oracle_users

oracle OS-User

#### Default value

```YAML
oracle_users:
  - username: oracle
    uid: 54321
    primgroup: '{{ oracle_group }}'
    othergroups: '{{ dba_group }},{{ asmadmin_group }},{{ asmdba_group }},{{ asmoper_group
      }},backupdba,dgdba,kmdba,{{ oper_group }}'
    passwd: 
      $6$0xHoAXXF$K75HKb64Hcb/CEcr3YEj2LGERi/U2moJgsCK.ztGxLsKoaXc4UBiNZPL0hlxB5ng6GL.gyipfQOOXplzcdgvD0
```

### os_family_supported

Support is limited to RHE/OL and SuSE

#### Default value

```YAML
os_family_supported: "{% if ansible_os_family == 'Suse' %}Suse{% else %}RedHat{% endif
  %}"
```

### os_min_supported_version

Minimum supported versions for SLES is 12.1 and RHEL/OL >= 6.4

#### Default value

```YAML
os_min_supported_version: "{% if ansible_os_family == 'Suse' %}12.1{% else %}6.4{%
  endif %}"
```

### percent_hugepages

Define percentage from RAM for Hugepages. Only valud when configure_hugepages_by: percentage

#### Default value

```YAML
percent_hugepages: 50
```

### size_in_gb_hugepages

Size in GB for Hugepages. Only valud when configure_hugepages_by: memory

#### Default value

```YAML
size_in_gb_hugepages: 1
```

### ssh_keys

#### Default value

```YAML
ssh_keys:
  - /tmp/id_rsa
  - /tmp/id_rsa.pub
  - /tmp/authorized_keys
```

### sudoers_template

Used ansible template for sudoers configuration.

#### Default value

```YAML
sudoers_template: sudoers.j2
```

### transparent_hugepage_disable

Disable Transparent Hugepages during boot.

_Important_

It is strongly recommended to disable Transparent Hugepages. Do not change this variable.

#### Default value

```YAML
transparent_hugepage_disable:
  - {disable: echo never >, path: /sys/kernel/mm/transparent_hugepage/enabled, rclocal: /etc/rc.d/rc.local}
  - {disable: echo never >, path: /sys/kernel/mm/transparent_hugepage/defrag, rclocal: /etc/rc.d/rc.local}
```

## Discovered Tags

**_always_**

**_asmlibconfig_**

**_etchosts_**

**_eth1_**

**_group_**

**_hostfs_**

**_nozeroconf_**

**_orahost_assert_**

**_os_packages, oscheck_**

**_os_packages, oscheck, asm1_**

**_oscheck_**

**_pamconfig_**

**_seclimit_**

**_selinux_**

**_sshkeys_**

**_stagedir_**

**_sudoadd_**

**_sysctl,hugepages_**

**_sysctl,hugepages,molecule-idempotence-notest_**

**_sysctl,molecule-idempotence-notest_**

**_tphnuma_**

**_tphnuma,molecule-idempotence-notest_**

**_user_**

## Open Tasks

- (improvement): SSH-Setup needs a rework...
- (security): remove fixed password from oracle OS-Users
- (security): remove fixed password from grid OS-Users

## Dependencies

- orahost_meta

## License

license (MIT)

## Author

[Mikael Sandström]
