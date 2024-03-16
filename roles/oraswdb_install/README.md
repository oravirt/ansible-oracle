# oraswdb_install

Install Oracle Database Software

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [autostartup_service](#autostartup_service)
  - [configure_oracle_profile](#configure_oracle_profile)
  - [glogin_default_cdb](#glogin_default_cdb)
  - [glogin_default_nocdb](#glogin_default_nocdb)
  - [hostgroup](#hostgroup)
  - [hostgroup_hub](#hostgroup_hub)
  - [hostgroup_leaf](#hostgroup_leaf)
  - [hostinitdaemon](#hostinitdaemon)
  - [oracle_ee_options](#oracle_ee_options)
  - [oraswdb_install_forcechopt](#oraswdb_install_forcechopt)
  - [oraswdb_install_remove_install_images](#oraswdb_install_remove_install_images)
  - [ulimit_systemd_mapping](#ulimit_systemd_mapping)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### autostartup_service

Force a chopt operation in ORACLE_HOME.

This is needed, when an existing ORACLE_HOME had multiple
switches between on/off for an option.

#### Default value

```YAML
autostartup_service: false
```

### configure_oracle_profile

Create .profile_-environment scripts for databases
in `oracle_databases`.

Mandatory when `listener_installed` is defined and
`autostartup_service: true`. Otherwise the listener will not start!

#### Default value

```YAML
configure_oracle_profile: true
```

### glogin_default_cdb

content of glogin.sql for CDB/PDB databases

#### Default value

```YAML
glogin_default_cdb:
  - define gname=idle
  - column global_name new_value gname
  - set heading off
  - set termout off
  - col global_name noprint
  - select upper(sys_context ('userenv', 'instance_name') || ':' || sys_context('userenv',
    'con_name')) global_name from dual;
  - set sqlprompt '_user @ &gname:>'
  - set heading on
  - set termout on
  - set time on
```

### glogin_default_nocdb

#### Default value

```YAML
glogin_default_nocdb:
  - set sqlprompt "_user @ _connect_identifier:>"
  - set time on
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

### hostinitdaemon

The start daemon of the OS.

Usually no need to change this value!

#### Default value

```YAML
hostinitdaemon: '{{ ansible_service_mgr }}'
```

### oracle_ee_options

#### Default value

```YAML
oracle_ee_options: "{{ _oracle_ee_opiton_dict[db_homes_config[dbh.home]['version']]
  }}"
```

### oraswdb_install_forcechopt

#### Default value

```YAML
oraswdb_install_forcechopt: false
```

### oraswdb_install_remove_install_images

Remove installation media from staging after installation when `oracle_sw_copy: true`.

#### Default value

```YAML
oraswdb_install_remove_install_images: true
```

### ulimit_systemd_mapping

Addional limits for systemd.

#### Default value

```YAML
ulimit_systemd_mapping:
  hard nproc: {name: LimitNPROC}
  hard nofile: {name: LimitNOFILE}
  hard stack: {name: LimitSTACK, sysctlfactor: 1024}
  hard memlock: {name: LimitMEMLOCK, sysctlfactor: 1024}
```

## Discovered Tags

**_always_**

**_assert_**

**_autostartup_service_**

**_checkdbswinstall_**

**_create_db,dotprofile_db_**

**_dbchopt_**

**_directoriesdb_**

**_existing_dbhome_**

**_glogindb_**

**_install_home_**

**_nfsmountdb_**

**_nfsumountdb_**

**_opatchls_**

**_oradbinstall_**

**_oradbinstall,dbchopt_**

**_oradbsw_**

**_oradbswunpack_**

**_orainst_**

**_responsefileswdb_**

**_roohctl_**

**_runroot_**

**_seclimit_**

## Open Tasks

- (information): hostgroup, hostgroup_hub, hostgroup_leaf needs some more tests

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
