# oraswgi_install

Install Grid Infrastructure / ORacle Restart software.

This role has a dependency to `orahost_meta` and `orasw_meta` for default parameter.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [cvuqdisk_rpm](#cvuqdisk_rpm)
  - [default_dbpass](#default_dbpass)
  - [default_gipass](#default_gipass)
  - [endoracle_scan_port](#endoracle_scan_port)
  - [gi_ignoreprereq](#gi_ignoreprereq)
  - [oracle_asm_init_dg](#oracle_asm_init_dg)
  - [oracle_asm_storage_option](#oracle_asm_storage_option)
  - [oracle_cluster_mgmdb](#oracle_cluster_mgmdb)
  - [oracle_cluster_name](#oracle_cluster_name)
  - [oracle_gi_cluster_type](#oracle_gi_cluster_type)
  - [oracle_gi_gns_subdomain](#oracle_gi_gns_subdomain)
  - [oracle_gi_gns_vip](#oracle_gi_gns_vip)
  - [oracle_gi_nic_priv](#oracle_gi_nic_priv)
  - [oracle_gi_nic_pub](#oracle_gi_nic_pub)
  - [oracle_ic_net](#oracle_ic_net)
  - [oracle_scan](#oracle_scan)
  - [oracle_scan_port](#oracle_scan_port)
  - [oracle_sw_image_gi](#oracle_sw_image_gi)
  - [oracle_vip](#oracle_vip)
  - [run_configtoolallcommand](#run_configtoolallcommand)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### cvuqdisk_rpm

Name of RPM for cvuqdisk.

RPM is installed from {{ oracle_home_gi }}/cv/rpm/

#### Default value

```YAML
cvuqdisk_rpm: cvuqdisk-1.0.10-1.rpm
```

### default_dbpass

#### Default value

```YAML
default_dbpass: '{% if item.0.oracle_db_passwd is defined %}{{ item.0.oracle_db_passwd
  }}{% else %}Oracle123{% endif %}'
```

### default_gipass

Default password for Grid-Infrastructure.

#### Default value

```YAML
default_gipass: "{{ oracle_password | default('') }}"
```

### endoracle_scan_port

Port for SCAN-Listener

### gi_ignoreprereq

false => Do not ignore failed runcluvfy.sh
true => Ignore failed runcluvfy.sh

#### Default value

```YAML
gi_ignoreprereq: false
```

### oracle_asm_init_dg

Do not use - is replaced in the future!
Reason why RAC support has been disabled...

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

Create _MGMTBD on cluster.

#### Default value

```YAML
oracle_cluster_mgmdb: false
```

### oracle_cluster_name

Name of Grid-Infrastructure Cluster.

#### Default value

```YAML
oracle_cluster_name: '{{ hostgroup }}'
```

### oracle_gi_cluster_type

Define clusterware type.

#### Default value

```YAML
oracle_gi_cluster_type: STANDARD
```

### oracle_gi_gns_subdomain

Define ths GNS subdomain for Cluster

### oracle_gi_gns_vip

Define GNS VIP for Clusterware.

#### Default value

```YAML
oracle_gi_gns_vip:
```

### oracle_gi_nic_priv

Name of private network interface.

#### Default value

```YAML
oracle_gi_nic_priv: eth1
```

### oracle_gi_nic_pub

Name of public network interface.

#### Default value

```YAML
oracle_gi_nic_pub: eth0
```

### oracle_ic_net

Do not use - is replaced in the future!
Reason why RAC support has been disabled...

#### Default value

```YAML
oracle_ic_net: 3.3.3.{{ ansible_all_ipv4_addresses[0].split(".")[-1] }}
```

### oracle_scan

SCAN DNS-Name

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
```

### oracle_vip

suffix added to hostnames for VIPs.

hostnamea{{ oracle_vip }}

#### Default value

```YAML
oracle_vip: -vip
```

### run_configtoolallcommand

Run configtoolcommand during installation.

Do not disable this!

#### Default value

```YAML
run_configtoolallcommand: true
```

## Discovered Tags

**_asmfd_**

**_crsctl_**

**_cvuqdisk_**

**_directories_**

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

## Open Tasks

- (bug): oracle_vip is not flexible enough.
- (bug): oracle_ic_net will be removed in the future

## Dependencies

- orahost_meta
- orasw_meta
- oraswgi_meta

## License

license (MIT)

## Author

Mikael Sandström, Thorsten Bruhns
