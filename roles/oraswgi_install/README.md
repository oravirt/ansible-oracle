# oraswgi_install

Install Grid Infrastructure / ORacle Restart software.

This role has a dependency to `orahost_meta` and `orasw_meta` for default parameter.

## Table of content

- [Default Variables](#default-variables)
  - [apply_patches_gi](#apply_patches_gi)
  - [asmmonitorpassword](#asmmonitorpassword)
  - [cluster_master](#cluster_master)
  - [cvuqdisk_rpm](#cvuqdisk_rpm)
  - [default_dbpass](#default_dbpass)
  - [default_gipass](#default_gipass)
  - [device_persistence](#device_persistence)
  - [gi_ignoreprereq](#gi_ignoreprereq)
  - [giignoreprereqparam](#giignoreprereqparam)
  - [hostgroup](#hostgroup)
  - [hostgroup_hub](#hostgroup_hub)
  - [hostgroup_leaf](#hostgroup_leaf)
  - [init_dg_exists](#init_dg_exists)
  - [opatcharchive](#opatcharchive)
  - [oracle_asm_disk_string](#oracle_asm_disk_string)
  - [oracle_asm_init_dg](#oracle_asm_init_dg)
  - [oracle_asm_storage_option](#oracle_asm_storage_option)
  - [oracle_cluster_mgmdb](#oracle_cluster_mgmdb)
  - [oracle_cluster_name](#oracle_cluster_name)
  - [oracle_directories](#oracle_directories)
  - [oracle_env](#oracle_env)
  - [oracle_gi_cluster_type](#oracle_gi_cluster_type)
  - [oracle_gi_gns_subdomain](#oracle_gi_gns_subdomain)
  - [oracle_gi_gns_vip](#oracle_gi_gns_vip)
  - [oracle_gi_image](#oracle_gi_image)
  - [oracle_gi_nic_priv](#oracle_gi_nic_priv)
  - [oracle_gi_nic_pub](#oracle_gi_nic_pub)
  - [oracle_grid_responsefile](#oracle_grid_responsefile)
  - [oracle_hostname](#oracle_hostname)
  - [oracle_ic_net](#oracle_ic_net)
  - [oracle_install_option_gi](#oracle_install_option_gi)
  - [oracle_install_version_gi](#oracle_install_version_gi)
  - [oracle_profile_name_gi](#oracle_profile_name_gi)
  - [oracle_scan](#oracle_scan)
  - [oracle_scan_port](#oracle_scan_port)
  - [oracle_sw_image_gi](#oracle_sw_image_gi)
  - [oracle_vip](#oracle_vip)
  - [patch_before_rootsh](#patch_before_rootsh)
  - [role_separation](#role_separation)
  - [run_configtoolallcommand](#run_configtoolallcommand)
  - [sysasmpassword](#sysasmpassword)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### apply_patches_gi

#### Default value

```YAML
apply_patches_gi: false
```

### asmmonitorpassword

#### Default value

```YAML
asmmonitorpassword: '{% if oracle_password is defined %}{{ oracle_password }}{% else
  %}Oracle123{% endif %}'
```

### cluster_master

#### Default value

```YAML
cluster_master: '{{ play_hosts[0] }}'
```

### cvuqdisk_rpm

#### Default value

```YAML
cvuqdisk_rpm: "{%- if oracle_install_version_gi > '12.1.0.2' -%}cvuqdisk-1.0.10-1.rpm{%-\
  \ else -%}cvuqdisk-1.0.9-1.rpm{%- endif -%}"
```

### default_dbpass

#### Default value

```YAML
default_dbpass: '{% if item.0.oracle_db_passwd is defined %}{{ item.0.oracle_db_passwd
  }}{% else %}Oracle123{% endif %}'
```

### default_gipass

#### Default value

```YAML
default_gipass: '{% if oracle_password is defined %}{{ oracle_password }}{% else %}Oracle123{%
  endif %}'
```

### device_persistence

#### Default value

```YAML
device_persistence: asmlib
```

### gi_ignoreprereq

#### Default value

```YAML
gi_ignoreprereq: false
```

### giignoreprereqparam

#### Default value

```YAML
giignoreprereqparam: '{% if gi_ignoreprereq | bool %}-ignorePrereq{% endif %}'
```

### hostgroup

#### Default value

```YAML
hostgroup: '{{ group_names[0] }}'
```

### hostgroup_hub

#### Default value

```YAML
hostgroup_hub: '{{ hostgroup }}-hub'
```

### hostgroup_leaf

#### Default value

```YAML
hostgroup_leaf: '{{ hostgroup }}-leaf'
```

### init_dg_exists

#### Default value

```YAML
init_dg_exists: '{% for dg in asm_diskgroups if oracle_asm_init_dg == dg.diskgroup
  %}true{% endfor %}'
```

### opatcharchive

#### Default value

```YAML
opatcharchive: "{{ oracle_stage_install }}/{{ oracle_install_version_gi }}/ {%- for\
  \ opatchfile in oracle_opatch_patch if opatchfile['version']==oracle_install_version_gi\
  \ -%}{{ opatchfile['filename'] }} {%- endfor -%}"
```

### oracle_asm_disk_string

#### Default value

```YAML
oracle_asm_disk_string: ORCL:*
```

### oracle_asm_init_dg

#### Default value

```YAML
oracle_asm_init_dg: crs
```

### oracle_asm_storage_option

#### Default value

```YAML
oracle_asm_storage_option: "{% if oracle_install_version_gi is version('12.2', '>=')\
  \ %}FLEX_ASM_STORAGE{% else %}LOCAL_ASM_STORAGE{% endif %}"
```

### oracle_cluster_mgmdb

#### Default value

```YAML
oracle_cluster_mgmdb: true
```

### oracle_cluster_name

#### Default value

```YAML
oracle_cluster_name: '{{ hostgroup }}'
```

### oracle_directories

#### Default value

```YAML
oracle_directories:
  - {name: '{{ oracle_stage }}', owner: '{{ oracle_user }}', group: '{{ oracle_group
      }}', mode: 775}
  - {name: '{{ oracle_rsp_stage }}', owner: '{{ oracle_user }}', group: '{{ oracle_group
      }}', mode: 775}
  - {name: '{{ oracle_base }}', owner: '{{ oracle_user }}', group: '{{ oracle_group
      }}', mode: 775}
  - {name: '{{ oracle_inventory_loc }}', owner: '{{ grid_install_user }}', group: '{{
      oracle_group }}', mode: 775}
  - {name: '{{ oracle_base }}/cfgtoollogs', owner: '{{ oracle_user }}', group: '{{
      oracle_group }}', mode: 775}
  - {name: '{{ oracle_base }}/admin', owner: '{{ oracle_user }}', group: '{{ oracle_group
      }}', mode: 775}
  - {name: '{{ oracle_base }}/audit', owner: '{{ oracle_user }}', group: '{{ oracle_group
      }}', mode: 775}
  - {name: '{{ oracle_base }}/cfgtoollogs/dbca', owner: '{{ oracle_user }}', group: '{{
      oracle_group }}', mode: 775}
  - {name: '{{ oracle_base }}/cfgtoollogs/sqlpatch', owner: '{{ oracle_user }}', group: '{{
      oracle_group }}', mode: 775}
  - {name: '{{ oracle_base }}/cfgtoollogs/netca', owner: '{{ oracle_user }}', group: '{{
      oracle_group }}', mode: 775}
```

### oracle_env

#### Default value

```YAML
oracle_env:
  ORACLE_HOME: '{{ oracle_home_gi }}'
```

### oracle_gi_cluster_type

#### Default value

```YAML
oracle_gi_cluster_type: STANDARD
```

### oracle_gi_gns_subdomain

#### Default value

```YAML
oracle_gi_gns_subdomain: a.b.c
```

### oracle_gi_gns_vip

#### Default value

```YAML
oracle_gi_gns_vip: gnsvip.a.b.c
```

### oracle_gi_image

#### Default value

```YAML
oracle_gi_image: '{%- if oracle_sw_copy %}{{ oracle_stage }}{%- else %}{{ oracle_stage_remote
  }}{%- endif %}{%- if oracle_install_image_gi is defined %}/{{ oracle_install_image_gi
  }}{%- else %}//{{ item.filename }}{%- endif %}'
```

### oracle_gi_nic_priv

#### Default value

```YAML
oracle_gi_nic_priv: eth1
```

### oracle_gi_nic_pub

#### Default value

```YAML
oracle_gi_nic_pub: eth0
```

### oracle_grid_responsefile

#### Default value

```YAML
oracle_grid_responsefile: grid-{{ oracle_cluster_name }}.rsp
```

### oracle_hostname

#### Default value

```YAML
oracle_hostname: '{{ ansible_fqdn }}'
```

### oracle_ic_net

#### Default value

```YAML
oracle_ic_net: 3.3.3.{{ ansible_all_ipv4_addresses[0].split(".")[-1] }}
```

### oracle_install_option_gi

#### Default value

```YAML
oracle_install_option_gi: '{% if configure_cluster %}CRS_CONFIG{% else %}HA_CONFIG{%
  endif %}'
```

### oracle_install_version_gi

#### Default value

```YAML
oracle_install_version_gi: 12.2.0.1
```

### oracle_profile_name_gi

#### Default value

```YAML
oracle_profile_name_gi: .profile_grid
```

### oracle_scan

#### Default value

```YAML
oracle_scan: your.scan.address
```

### oracle_scan_port

#### Default value

```YAML
oracle_scan_port: 1521
```

### oracle_sw_image_gi

#### Default value

```YAML
oracle_sw_image_gi:
  - {filename: LINUX.X64_213000_grid_home.zip, version: 21.3.0.0, creates: install/.img.bin}
  - {filename: LINUX.X64_193000_grid_home.zip, version: 19.3.0.0, creates: install/.img.bin}
  - {filename: LINUX.X64_180000_grid_home.zip, version: 18.3.0.0, creates: install/.img.bin}
  - {filename: linuxx64_12201_grid_home.zip, version: 12.2.0.1, creates: xdk/mesg/lsxja.msb}
  - {filename: linuxamd64_12102_grid_1of2.zip, version: 12.1.0.2, creates: grid/stage/sizes/oracle.crs.12.1.0.2.0.sizes.properties}
  - {filename: linuxamd64_12102_grid_2of2.zip, version: 12.1.0.2, creates: grid/install/.oui}
  - {filename: linuxamd64_12c_grid_1of2.zip, version: 12.1.0.1}
  - {filename: linuxamd64_12c_grid_2of2.zip, version: 12.1.0.1}
  - {filename: p13390677_112040_Linux-x86-64_3of7.zip, version: 11.2.0.4, creates: grid/welcome.html}
  - {filename: p10404530_112030_Linux-x86-64_3of7.zip, version: 11.2.0.3, creates: grid/stage/properties/userPaths.properties}
```

### oracle_vip

#### Default value

```YAML
oracle_vip: -vip
```

### patch_before_rootsh

#### Default value

```YAML
patch_before_rootsh: true
```

### role_separation

#### Default value

```YAML
role_separation: false
```

### run_configtoolallcommand

#### Default value

```YAML
run_configtoolallcommand: true
```

### sysasmpassword

#### Default value

```YAML
sysasmpassword: '{% if oracle_password is defined %}{{ oracle_password }}{% else %}Oracle123{%
  endif %}'
```

## Discovered Tags

**_asmfd_**

**_crsctl_**

**_cvuqdisk_**

**_directories_**

**_dotprofilegi_**

**_dsset_**

**_glogingi_**

**_nfsmountdb_**

**_nfsumountdb_**

**_olsnodes_**

**_opatchls_**

**_oragridinstall_**

**_oragridsw_**

**_oragridswunpack_**

**_responsefileconfigtool_**

**_responsefilegi_**

**_runcluvfy_**

**_runconfigtool_**

**_runroot_**

**_updatenodelist_**


## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

Mikael Sandström, Thorsten Bruhns
