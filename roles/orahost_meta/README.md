# orahost_meta

Meta role used by other roles to share variable defaults.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [asm_diskgroups](#asm_diskgroups)
  - [asmadmin_group](#asmadmin_group)
  - [asmdba_group](#asmdba_group)
  - [asmoper_group](#asmoper_group)
  - [configure_host_disks](#configure_host_disks)
  - [dba_group](#dba_group)
  - [device_persistence](#device_persistence)
  - [grid_user](#grid_user)
  - [grid_user_home](#grid_user_home)
  - [oper_group](#oper_group)
  - [oracle_group](#oracle_group)
  - [oracle_inventory_loc](#oracle_inventory_loc)
  - [oracle_nr_bg_processes](#oracle_nr_bg_processes)
  - [oracle_rsp_stage](#oracle_rsp_stage)
  - [oracle_script_env](#oracle_script_env)
  - [oracle_seclimits](#oracle_seclimits)
  - [oracle_stage](#oracle_stage)
  - [oracle_tmp_stage](#oracle_tmp_stage)
  - [oracle_user](#oracle_user)
  - [oracle_user_home](#oracle_user_home)
  - [orahost_meta_cv_assume_distid](#orahost_meta_cv_assume_distid)
  - [orahost_meta_java_options](#orahost_meta_java_options)
  - [orahost_meta_tmpdir](#orahost_meta_tmpdir)
  - [orahost_min_swap_mb](#orahost_min_swap_mb)
  - [orahost_ssh_hostkeytypes](#orahost_ssh_hostkeytypes)
  - [orahost_ssh_key_size](#orahost_ssh_key_size)
  - [orahost_ssh_key_type](#orahost_ssh_key_type)
  - [role_separation](#role_separation)
  - [scripts_folder](#scripts_folder)
  - [sysctl_kernel_sem_force](#sysctl_kernel_sem_force)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### asm_diskgroups

ASM Diskgroupdefinition for Oracle Restart/Grid-Infrastructure

#### Default value

```YAML
asm_diskgroups: []
```

#### Example usage

```YAML
asm_diskgroups:
 - diskgroup: crs
   properties:
     - {redundancy: normal, ausize: 4}
   attributes:
     - {name: 'compatible.rdbms', value: 11.2.0.4.0}
     - {name: 'compatible.asm', value: 12.1.0.2.0}
   disk:
     - {device: /dev/sdc, asmlabel: crs01}
     - {device: /dev/sdd, asmlabel: crs02}
     - {device: /dev/sde, asmlabel: crs03}
 - diskgroup: data
   properties:
     - {redundancy: external, ausize: 4}
   attributes:
     - {name: compatible.rdbms, value: 11.2.0.4.0}
     - {name: compatible.asm, value: 12.1.0.2.0}
   disk:
     - {device: /dev/sdf, asmlabel: data01}
 - diskgroup: fra
   properties:
    - {redundancy: external, ausize: 4}
  attributes:
     - {name: compatible.rdbms, value: 11.2.0.4.0}
     - {name: compatible.asm, value: 12.1.0.2.0}
   disk:
     - {device: /dev/sdg, asmlabel: fra01}
```

### asmadmin_group

The os-group for asmadmin role in Oracle ASM.

#### Default value

```YAML
asmadmin_group: asmadmin
```

### asmdba_group

The os-group for asmdba role in Oracle ASM.

#### Default value

```YAML
asmdba_group: asmdba
```

### asmoper_group

The os-group for asmoper role in Oracle ASM.

#### Default value

```YAML
asmoper_group: asmoper
```

### configure_host_disks

Should the specified directories be on their
devices -> (true), or do they live in the root-filesystem (/) -> (false).
mountpoints are described in host_fs_layout

#### Default value

```YAML
configure_host_disks: false
```

### dba_group

The os-group for sysdba role in Oracle RDBMS.

#### Default value

```YAML
dba_group: dba
```

### device_persistence

Defines the device persistency in ansible-oracle.

Values:

- asmlib
- asmfd
- '' - no special device configuration

#### Default value

```YAML
device_persistence: ''
```

#### Example usage

```YAML
device_persistence: asmlib

device_persistence: asmfd
```

### grid_user

Defines the os-User for Oracle Restart/Grid-Infrastructure,
when role_separation is true.

#### Default value

```YAML
grid_user: grid
```

### grid_user_home

home directory for `grid_user`.

Only used, when `role_seperation: true` which is false by default.

#### Default value

```YAML
grid_user_home: /home/grid
```

### oper_group

The os-group for sysoper role in Oracle RDBMS.

#### Default value

```YAML
oper_group: oper
```

### oracle_group

The name for the oinstall group.

#### Default value

```YAML
oracle_group: oinstall
```

### oracle_inventory_loc

Directory for central Oracle Inventory.

#### Default value

```YAML
oracle_inventory_loc: /u01/app/oraInventory
```

### oracle_nr_bg_processes

Estimated number of background processes of an Oracle instance. Used to calculate kernel SEMMNS

#### Default value

```YAML
oracle_nr_bg_processes: 130
```

### oracle_rsp_stage

Defines the directory for response files for installation.

There is usually no need to change this variable.

#### Default value

```YAML
oracle_rsp_stage: '{{ oracle_stage }}/rsp'
```

### oracle_script_env

(Minimum) environment settings to pass to Oracle scripts.
Usually passed to shell: or command: through "environment:" keyword

#### Default value

```YAML
oracle_script_env:
  CV_ASSUME_DISTID: '{{ orahost_meta_cv_assume_distid }}'
  TMPDIR: '{{ orahost_meta_tmpdir }}'
  _JAVA_OPTIONS: '{{ orahost_meta_java_options }}'
```

### oracle_seclimits

ulimit definition for orahost role.

#### Default value

```YAML
oracle_seclimits:
  - {name: soft nproc, value: 16384}
  - {name: hard nproc, value: 16384}
  - {name: soft nofile, value: 4096}
  - {name: hard nofile, value: 65536}
  - {name: soft stack, value: 10240}
  - {name: hard stack, value: 32768}
  - {name: soft memlock, value: '{{ ((0.91 * ansible_memtotal_mb) * 1024) | round
      | int }}'}
  - {name: hard memlock, value: '{{ ((0.91 * ansible_memtotal_mb) * 1024) | round
      | int }}'}
```

### oracle_stage

Defines the base directory for response files, configuration firles etc. for `ansible-oracle`.

There is usually no need to change this variable.

#### Default value

```YAML
oracle_stage: /u01/stage
```

### oracle_tmp_stage

Defines the temporary directory to be used by Oracle scripts.
(on hardened systems, /tmp usually is noexec-flagged and thus not usable to execute scripts)

There is usually no need to change this variable.

#### Default value

```YAML
oracle_tmp_stage: >-
  {% if ansible_fips | default(false) %}{{ oracle_stage }}{%- endif %}/tmp
```

### oracle_user

Defines the os-User for Oracle Database installation.
Is also used as the grid owner, when role_separation is false.

#### Default value

```YAML
oracle_user: oracle
```

### oracle_user_home

home directory for `oracle_user`.

#### Default value

```YAML
oracle_user_home: /home/oracle
```

### orahost_meta_cv_assume_distid

The variable is used by `oracle_script_env` and passed
to shell: or command: through "environment:" keyword

Riles:
- Redhat/OL and ansible_distribution_major_version <= 8

`OL{{ ansible_distribution_major_version }}`

- Redhat/OL and ansible_distribution_major_version = 9

`OL8`

- SuSE

`SLES15`

#### Default value

```YAML
orahost_meta_cv_assume_distid: |-
  {% if ansible_os_family == 'RedHat' %}OL
  {%- if ansible_distribution_major_version is version('8', '<=') %}{{ ansible_distribution_major_version }}
  {%- elif ansible_distribution_major_version is version('9', '=') %}8
  {%- endif %}
  {%- elif ansible_os_family in ('SuSe', 'Suse') %}SUSE{{ ansible_distribution_major_version }}
  {%- endif %}
```

### orahost_meta_java_options

The variable is used by `oracle_script_env` and passed
to shell: or command: through "environment:" keyword

#### Default value

```YAML
orahost_meta_java_options: >-
  {% if oracle_tmp_stage != '/tmp' -%}
  -Djava.io.tmpdir={{ oracle_tmp_stage -}}
  {% endif %}
```

### orahost_meta_tmpdir

#### Default value

```YAML
orahost_meta_tmpdir: '{{ oracle_tmp_stage }}'
```

### orahost_min_swap_mb

Minimum amount of swap space (in MB) required for DB server.
Note: We observed ansible_memory_mb.swap.total is 1MB less than configured
swap (e.g. 16383 instead of 16384 for 16GB)

**_Type:_** integer<br />

#### Default value

```YAML
orahost_min_swap_mb: 16383
```

### orahost_ssh_hostkeytypes

SSH host key types to collect/deploy among hosts
Please note, ed25519 is not supported on FIPS enabled systems and though better not collected

#### Default value

```YAML
orahost_ssh_hostkeytypes:
  - dsa
  - rsa
  - ecdsa
```

### orahost_ssh_key_size

SSH key size of {{ orahost_ssh_key_type }} key

#### Default value

```YAML
orahost_ssh_key_size: 4096
```

### orahost_ssh_key_type

SSH key type for oracle and grid users' SSH Keys

#### Default value

```YAML
orahost_ssh_key_type: rsa
```

### role_separation

Should role separation be used for Oracle Restart/Grid-Infrastructure.
See `grid_user` and `oracle_user` for Grid-Infrastructure user.

#### Default value

```YAML
role_separation: false
```

### scripts_folder

Folder under Oracle user home dir to place scripts in

#### Default value

```YAML
scripts_folder: .Scripts
```

### sysctl_kernel_sem_force

Force setting kernel.sem depending on configured instances
(collections: oracle_databases, oracle_asm_instance), even if calculated values are lower than current ones

#### Default value

```YAML
sysctl_kernel_sem_force: false
```

## Discovered Tags

**_always_**

**_assert_ansible_oracle_**

**_molecule-notest_**

## Dependencies

- oraswgi_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
