# oraswdb_install

Install Oracle Database Software

## Table of content

- [Default Variables](#default-variables)
  - [_hostinitdaemon_dict](#_hostinitdaemon_dict)
  - [autostartup_service](#autostartup_service)
  - [choptcheck](#choptcheck)
  - [configure_oracle_profile](#configure_oracle_profile)
  - [forcechopt](#forcechopt)
  - [glogin_default_cdb](#glogin_default_cdb)
  - [glogin_default_nocdb](#glogin_default_nocdb)
  - [hostgroup](#hostgroup)
  - [hostgroup_hub](#hostgroup_hub)
  - [hostgroup_leaf](#hostgroup_leaf)
  - [hostinitdaemon](#hostinitdaemon)
  - [oracle_db_responsefile](#oracle_db_responsefile)
  - [oracle_directories](#oracle_directories)
  - [oracle_ee_options](#oracle_ee_options)
  - [oracle_hostname](#oracle_hostname)
  - [oracle_sw_image_db](#oracle_sw_image_db)
  - [oracle_sw_source_www](#oracle_sw_source_www)
  - [ulimit_systemd_mapping](#ulimit_systemd_mapping)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### _hostinitdaemon_dict

#### Default value

```YAML
_hostinitdaemon_dict:
  RedHat:
    version_highest: 6
  Suse:
    version_highest: 11
```

### autostartup_service

#### Default value

```YAML
autostartup_service: false
```

### choptcheck

#### Default value

```YAML
choptcheck: '{% if forcechopt | bool %}dochopt{% endif %}'
```

### configure_oracle_profile

#### Default value

```YAML
configure_oracle_profile: true
```

### forcechopt

#### Default value

```YAML
forcechopt: false
```

### glogin_default_cdb

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

#### Default value

```YAML
hostinitdaemon: "{% if ansible_distribution_major_version is version(_hostinitdaemon_dict[ansible_os_family]['version_highest'],\
  \ '<=') %}init{% else %}systemd{% endif %}"
```

### oracle_db_responsefile

#### Default value

```YAML
oracle_db_responsefile: '{{ dbh.home }}_{{ ansible_hostname }}.rsp'
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
  - {name: '{{ oracle_user_home }}/.Scripts', owner: '{{ oracle_user }}', group: '{{
      oracle_group }}', mode: 775}
```

### oracle_ee_options

#### Default value

```YAML
oracle_ee_options: "{{ _oracle_ee_opiton_dict[db_homes_config[dbh.home]['version']]\
  \ }}"
```

### oracle_hostname

#### Default value

```YAML
oracle_hostname: '{{ ansible_fqdn }}'
```

### oracle_sw_image_db

#### Default value

```YAML
oracle_sw_image_db:
  - {filename: LINUX.X64_213000_db_home.zip, version: 21.3.0.0, creates: install/.img.bin}
  - {filename: LINUX.X64_193000_db_home.zip, version: 19.3.0.0, creates: install/.img.bin}
  - {filename: LINUX.X64_180000_db_home.zip, version: 18.3.0.0, creates: install/.img.bin}
  - {filename: linuxx64_12201_database.zip, version: 12.2.0.1, creates: database/runInstaller}
  - {filename: linuxamd64_12102_database_1of2.zip, version: 12.1.0.2, creates: database/stage/sizes/oracle.server.Custom.sizes.properties}
  - {filename: linuxamd64_12102_database_2of2.zip, version: 12.1.0.2, creates: database/install/.oui}
  - {filename: linuxamd64_12c_database_1of2.zip, version: 12.1.0.1, creates: database/runInstaller}
  - {filename: linuxamd64_12c_database_2of2.zip, version: 12.1.0.1, creates: database/runInstaller}
  - {filename: p13390677_112040_Linux-x86-64_1of7.zip, version: 11.2.0.4, creates: database/install/resource/cons_zh_TW.nls}
  - {filename: p13390677_112040_Linux-x86-64_2of7.zip, version: 11.2.0.4, creates: database/stage/Components/oracle.db/11.2.0.4.0/1/DataFiles/filegroup18.jar}
  - {filename: p10404530_112030_Linux-x86-64_1of7.zip, version: 11.2.0.3, creates: database/readme.html}
  - filename: p10404530_112030_Linux-x86-64_2of7.zip
    version: 11.2.0.3
    creates: database/stage/Components/oracle.sysman.console.db/11.2.0.3.0/1/DataFiles/filegroup2.jar
```

### oracle_sw_source_www

#### Default value

```YAML
oracle_sw_source_www: ''
```

### ulimit_systemd_mapping

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

**_create_db,dotprofile_db_**

**_dbchopt_**

**_directoriesdb_**

**_glogindb_**

**_install_home,existing_dbhome,checkdbswinstall_**

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

- (bug): oracle_hostname really needed? Maybe as hostname for all the oradb-manage-* roles as extension?
- (information): hostgroup, hostgroup_hub, hostgroup_leaf needs some more tests

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
