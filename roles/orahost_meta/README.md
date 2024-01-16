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
  - [oracle_password](#oracle_password)
  - [oracle_rsp_stage](#oracle_rsp_stage)
  - [oracle_seclimits](#oracle_seclimits)
  - [oracle_stage](#oracle_stage)
  - [oracle_user](#oracle_user)
  - [oracle_user_home](#oracle_user_home)
  - [role_separation](#role_separation)
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

### oracle_password

This is the default password for sys, system, ASM etc.

IMPORTANT!

This will be a mandatory inventory variable in the future!

See: https://github.com/oravirt/ansible-oracle/issues/327

#### Default value

```YAML
oracle_password: Oracle123
```

### oracle_rsp_stage

Defines the directory for response files for installation.

There is usually no need to change this variable.

#### Default value

```YAML
oracle_rsp_stage: '{{ oracle_stage }}/rsp'
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
  - {name: soft memlock, value: '{{ ((0.9 * ansible_memtotal_mb) * 1024) | round |
      int }}'}
  - {name: hard memlock, value: '{{ ((0.9 * ansible_memtotal_mb) * 1024) | round |
      int }}'}
```

### oracle_stage

Defines the base directory for response files, configuration firles etc. for `ansible-oracle`.

There is usually no need to change this variable.

#### Default value

```YAML
oracle_stage: /u01/stage
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

### role_separation

Should role separation be used for Oracle Restart/Grid-Infrastructure.
See `grid_user` and `oracle_user` for Grid-Infrastructure user.

#### Default value

```YAML
role_separation: false
```



## Dependencies

- oraswgi_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
