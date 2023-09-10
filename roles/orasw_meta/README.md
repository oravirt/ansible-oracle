# orasw_meta


_Important_

The description for variables is work in progress.!

Meta role used by other roles to share variable defaults.

This role has a dependency to `orahost_meta`.

There are a lot of variables who are used by `orasw_meta`

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [_www_download_bin](#_www_download_bin)
  - [apply_patches_db](#apply_patches_db)
  - [autostartup_service](#autostartup_service)
  - [db_homes_config](#db_homes_config)
  - [db_homes_installed](#db_homes_installed)
  - [dbenvdir](#dbenvdir)
  - [dbpasswords](#dbpasswords)
  - [default_dbpass](#default_dbpass)
  - [deploy_ocenv](#deploy_ocenv)
  - [disable_ee_options](#disable_ee_options)
  - [hostgroup](#hostgroup)
  - [install_from_nfs](#install_from_nfs)
  - [is_sw_source_local](#is_sw_source_local)
  - [listener_port](#listener_port)
  - [nfs_server_sw](#nfs_server_sw)
  - [nfs_server_sw_path](#nfs_server_sw_path)
  - [ocenv_bashrc_init](#ocenv_bashrc_init)
  - [ocenv_bashrc_init_section](#ocenv_bashrc_init_section)
  - [oracle_asm_disk_string](#oracle_asm_disk_string)
  - [oracle_base](#oracle_base)
  - [oracle_databases](#oracle_databases)
  - [oracle_dbf_dir_asm](#oracle_dbf_dir_asm)
  - [oracle_dbf_dir_fs](#oracle_dbf_dir_fs)
  - [oracle_ee_options_112](#oracle_ee_options_112)
  - [oracle_ee_options_121](#oracle_ee_options_121)
  - [oracle_ee_options_122](#oracle_ee_options_122)
  - [oracle_ee_options_183](#oracle_ee_options_183)
  - [oracle_ee_options_193](#oracle_ee_options_193)
  - [oracle_ee_options_213](#oracle_ee_options_213)
  - [oracle_home_gi_cl](#oracle_home_gi_cl)
  - [oracle_home_gi_so](#oracle_home_gi_so)
  - [oracle_hostname](#oracle_hostname)
  - [oracle_install_option_gi](#oracle_install_option_gi)
  - [oracle_install_version_gi](#oracle_install_version_gi)
  - [oracle_opatch_patch](#oracle_opatch_patch)
  - [oracle_pdbs](#oracle_pdbs)
  - [oracle_profile_template](#oracle_profile_template)
  - [oracle_reco_dir_asm](#oracle_reco_dir_asm)
  - [oracle_reco_dir_fs](#oracle_reco_dir_fs)
  - [oracle_stage_remote](#oracle_stage_remote)
  - [oracle_sw_patches](#oracle_sw_patches)
  - [oracle_sw_source_local](#oracle_sw_source_local)
  - [oracle_sw_source_www](#oracle_sw_source_www)
  - [shell_aliases](#shell_aliases)
  - [shell_ps1](#shell_ps1)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### _www_download_bin

The variable will be removed soon.
The download will be changed to get_url to simplify the code.

#### Default value

```YAML
_www_download_bin: curl
```

### apply_patches_db

Apply Patches from db_homes_config for installed ORACLE_HOME?

This is a global switch to enable/disable DB-Patching for all ORACLE_HOMEs.

#### Default value

```YAML
apply_patches_db: true
```

### autostartup_service

Enable autostart of database during system startup.

This switch is only used, when Single Instance without Grid Infrastructure / Restart is installed.

#### Default value

```YAML
autostartup_service: false
```

### db_homes_config


This is a central variable for ORACLE_HOME configuration.

Defines the known ORACLE_HOMEs with a lot of additional informations but not the installation itself.

See `db_homes_installed` for a list of installed ORACLE_HOMEs.

The dictionary holds data for:

| Attribute | Description |
| --- | --- |
| imagename | Set an optional name for a golden Image to install from. The archiv is read from same directory as the normal installation medias from Oracle. |
| edition | allowed values: `SE`, `SE2`, `EE`. default value: <todo> |
| opatch_minversion | Is needed for patching. Automatically installs a new version of OPatch, when existing version is older then `opatch_minversion` |
| oracle_home | |
| oracle_home_name | Mandatory variable, when `readonly_home: true`. Oracle allows only characters, numbers and '_' as value in `oracle_home_name`. Do _not_ use '-' as a value!|
| opatch | |
| readonly_home | Should `ansible-oracle` install this ORACLE_HOME as readonly home? Do _NOT_ change this attribute for an installed ORACLE_HOME. default value: false|
| version | The base version for the ORACLE_HOME. Use the version from the official 1st release of Oracle. |

See examples for allowed values.

#### Example usage

```YAML
db_homes_config:
  21300_base: # 21c without patching - you should never use this in production!
    home: db1_base
    version: 21.3.0.0
    edition: EE
  19300_base: # 19c without patching - you should never use this in production!
    home: db1_base
    version: 19.3.0.0
    edition: EE
```

### db_homes_installed

#### Example usage

```YAML
db_homes_installed:
  - home: 19300-base
    apply_patches: true
    state: present
```

### dbenvdir

Define the directory for db environment configurations.

Used during installation of `ocenv.sh`.

#### Default value

```YAML
dbenvdir: '{{ oracle_user_home }}/dbenv'
```

### dbpasswords

#### Default value

```YAML
dbpasswords:
  orcl:
    sys: Oracle_456
    system: Oracle_456
    dbsnmp: Oracle_456
    pdbadmin: Oracle_456
```

### default_dbpass

#### Default value

```YAML
default_dbpass: '{% if item is defined and item.oracle_db_passwd is defined %}{{ item.oracle_db_passwd
  }}{%- elif dbh is defined and dbh.oracle_db_passwd is defined %}{{ dbh.oracle_db_passwd
  }}{%- else %}Oracle123{%- endif %}'
```

### deploy_ocenv

Install the `ocenv.sh` environment script.

Source is from: https://github.com/opitzconsulting/oracle-scripts

#### Default value

```YAML
deploy_ocenv: true
```

### disable_ee_options

Global switch to define if Oracle options should be changed in binary for Enterprise-Edition.

#### Default value

```YAML
disable_ee_options: 'true'
```

#### Example usage

```YAML
disable_ee_options: true # change options in binary
disable_ee_options: false # do not change options in binary
```

### hostgroup

Defines the hostgroup with nodes for a Grid-Infrastructure Cluster.

The variable needs a refactoring.

#### Default value

```YAML
hostgroup: '{{ group_names[0] }}'
```

### install_from_nfs

Mount NFS-Server for installation media?

`nfs_server_sw` and `nfs_server_sw_path` are needed, when `install_from_nfs: true`

#### Default value

```YAML
install_from_nfs: false
```

### is_sw_source_local

#### Default value

```YAML
is_sw_source_local: true
```

### listener_port

The global default port for listener when no dedicated port is configured in listener itself.

#### Default value

```YAML
listener_port: 1521
```

### nfs_server_sw

Defines the NFS-Server used to mount the installation media from.

#### Example usage

```YAML
nfs_server_sw: nfs-server.example.com
```

### nfs_server_sw_path

Path to installation medias on NFS-Ser.

_Important_

`ansible-oracle` expects a fixed structure for installation media and patches!

#### Example usage

```YAML
nfs_server_sw_path: /orasw
```

### ocenv_bashrc_init

Add `ocenv.sh` to `bashrc` of oracle user?

`deploy_ocenv: true` is needed for the installation.

#### Default value

```YAML
ocenv_bashrc_init: true
```

### ocenv_bashrc_init_section

Define the conntents to add to `.bashr` when `ocenv_bashrc_init: true`.

#### Default value

```YAML
ocenv_bashrc_init_section: |
  echo "execute ocenv to source Oracle Environment"
  alias ocenv='. "{{ dbenvdir }}/ocenv"'
```

### oracle_asm_disk_string

#### Default value

```YAML
oracle_asm_disk_string: ORCL:*
```

### oracle_base

`ORACLE_BASE` for Oracle RDBMS and Grid Infrastructure.

There is a known bug for Grid-Infrastructure/Restart.

See (https://github.com/oravirt/ansible-oracle/issues/259) for details.

#### Default value

```YAML
oracle_base: /u01/app/oracle
```

### oracle_databases


Defines the list of databases on a host.

There are diffent sub list to define Profiles, Services, Tablespaces, Users ...

*Sub-Sections*

_statspack_

| Attribute | Description |
| --- | --- |
| purgedays | Purgedays for snapshots |
| snaplevel | snaplevel used in job |
| state | create (`present`) or remove (`absent`) statspack from nonCDB, CDB or PDB |

_tablespaces_

Defines the Tablespace to add, drop or modify to the database.

Known limitations:

Multiple files with dedicated file names are not supported.

Use OMF instead, which is the default during creation of Tablespaces.

| Attribute | Description |
| --- | --- |
| name ||
| size ||
| autoextend ||
| next ||
| maxsize ||
| content ||
| state ||
| bigfile ||
| numfiles | mutually exclusive with datafile |
| datafile | mutually exclusive with numfiles |
See examples for allowed values.

#### Example usage

```YAML

# IMPORTANT! This following example shows the general structure of oracle_databases.
# Do not use it as a real example.

oracle_databases:
  - home: 19300-base
    oracle_db_name: orcl
    state: present
    statspack:
      purgedays: 14
      snaplevel: 5
      state: present
    tablespaces:
      - {name: system, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent, state: present, bigfile: false}
    init_parameters:
      - {name: audit_trail, value: 'NONE', scope: spfile, state: present}
    profiles:
      - name: DEFAULT
    users:
      - schema: dbsnmp

oracle_databases:
  - home: 19300-base
    oracle_db_name: orcl
    oracle_db_type: SI
    is_container: true
    storage_type: FS
    oracle_db_mem_totalmb: 1024
    oracle_database_type: MULTIPURPOSE
    redolog_size: 100M
    redolog_groups: 3
    archivelog: false
    flashback: false
    force_logging: false
    listener_name: LISTENER
    state: present
    statspack:
      purgedays: 14
      snaplevel: 5
      state: present
    tablespaces:
      - {name: system, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent, state: present, bigfile: false}
      - {name: sysaux, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent, state: present, bigfile: false}
      - {name: undotbs1, size: 10M, autoextend: true, next: 50M, maxsize: 8G, content: permanent, state: present, bigfile: false}
      - {name: users, size: 10M, autoextend: true, next: 50M, maxsize: 2G, content: permanent, state: present, bigfile: false}
      - {name: temp, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent, state: present, bigfile: false}
    init_parameters:
      - {name: audit_trail, value: 'NONE', scope: spfile, state: present}
      - {name: control_management_pack_access, value: 'NONE', scope: both, state: present}
      - {name: control_file_record_keep_time, value: '30', scope: both, state: present}
      - {name: db_files, value: '200', scope: spfile, state: present}
      - {name: deferred_segment_creation, value: 'false', scope: both, state: present}
      - {name: filesystemio_options, value: 'setall', scope: spfile, state: present}
      - {name: job_queue_processes, value: '10', scope: both, state: present}
      # Disable forcing hugepages on really small systems
      #  - {name: use_large_pages ,value: 'ONLY', scope: spfile, state: present}
      - {name: log_archive_dest_1, value: 'location=USE_DB_RECOVERY_FILE_DEST', scope: both, state: present}
      - {name: log_buffer, value: '64M', scope: spfile, state: present}
      - {name: pga_aggregate_target, value: '200M', scope: both, state: present, dbca: false}
      - {name: sga_target, value: '1800M', scope: spfile, state: present, dbca: false}
      - {name: recyclebin, value: 'off', scope: spfile, state: present}
      - {name: streams_pool_size, value: '152M', scope: spfile, state: present}
      - {name: "_cursor_obsolete_threshold", value: '1024', scope: spfile, state: present}
      - {name: max_pdbs, value: '3', scope: both, state: present}
      - {name: clonedb, value: 'true', scope: spfile, state: present, dbca: false}
      - {name: db_create_file_dest, value: '/u02/oradata', scope: both, state: present}
      - {name: db_create_online_log_dest_1, value: '/u02/oradata', scope: both, state: present}
      - {name: db_recovery_file_dest_size, value: '10G', scope: both, state: present, dbca: false}
    profiles:
      - name: DEFAULT
        state: present
        attributes:
          - {name: password_life_time, value: unlimited}
    users:
      - schema: dbsnmp
        state: unlocked
        update_password: always
```

### oracle_dbf_dir_asm

#### Default value

```YAML
oracle_dbf_dir_asm: +DATA
```

### oracle_dbf_dir_fs

Global default for `db_create_file_dest`in DBCA.

#### Default value

```YAML
oracle_dbf_dir_fs: /u02/oradata/
```

### oracle_ee_options_112

Define the enabled/disabled options for 11.2 binaries.

#### Default value

```YAML
oracle_ee_options_112:
  - {option: dm, state: false}
  - {option: dv, state: false}
  - {option: lbac, state: false}
  - {option: olap, state: false}
  - {option: partitioning, state: false}
  - {option: rat, state: false}
```

### oracle_ee_options_121

Define the enabled/disabled options for 12.1 binaries.

#### Default value

```YAML
oracle_ee_options_121:
  - {option: dm, state: false}
  - {option: olap, state: false}
  - {option: partitioning, state: false}
  - {option: rat, state: false}
```

### oracle_ee_options_122

Define the enabled/disabled options for 12.2 binaries.

#### Default value

```YAML
oracle_ee_options_122:
  - {option: oaa, state: false}
  - {option: olap, state: false}
  - {option: partitioning, state: false}
  - {option: rat, state: false}
```

### oracle_ee_options_183

Define the enabled/disabled options for 18c binaries.

#### Default value

```YAML
oracle_ee_options_183:
  - {option: oaa, state: false}
  - {option: olap, state: false}
  - {option: partitioning, state: false}
  - {option: rat, state: false}
```

### oracle_ee_options_193

Define the enabled/disabled options for 19c binaries.

#### Default value

```YAML
oracle_ee_options_193:
  - {option: oaa, state: false}
  - {option: olap, state: false}
  - {option: partitioning, state: false}
  - {option: rat, state: false}
```

### oracle_ee_options_213

Define the enabled/disabled options for 21c binaries.

#### Default value

```YAML
oracle_ee_options_213:
  - {option: oaa, state: false}
  - {option: olap, state: false}
  - {option: partitioning, state: false}
  - {option: rat, state: false}
```

### oracle_home_gi_cl

Custom setting for CRS_HOME when Grid-Infrastructure is installed.

The variable is used as a default for `oracle_home_gi`.

Do not forget `` for Cluster installations.

#### Default value

```YAML
oracle_home_gi_cl: /u01/app/{{ oracle_install_version_gi }}/grid
```

### oracle_home_gi_so

Custom setting for CRS_HOME when Oracle Restart is installed.

The variable is used as a default for the internal variable `oracle_home_gi`.

#### Default value

```YAML
oracle_home_gi_so: '{{ oracle_base }}/{{ oracle_install_version_gi }}/grid'
```

### oracle_hostname

Grid-Infrastructure nodename.

Used as hostname for all oradb_manage_-connections and as hostname in RDBMS installation.

#### Default value

```YAML
oracle_hostname: '{{ ansible_fqdn }}'
```

### oracle_install_option_gi

Define the installation type for Grid Infrastructure or Oracle Restart.

| Value | Description |
| --- | --- |
| "" | Install Single Instance (Default) |
| CRS_CONFIG | Install Grid-Infrastructure |
| HA_CONFIG | Install Oracle Restart |

#### Default value

```YAML
oracle_install_option_gi: ''
```

#### Example usage

```YAML

oracle_install_option_gi: ''

oracle_install_option_gi: CRS_CONFIG

oracle_install_option_gi: HA_CONFIG
```

### oracle_install_version_gi

Define the version for Grid-Infrastructure or Oracle Restart.

_Important_

Do not forget to set `oracle_install_option_gi`.

#### Default value

```YAML
oracle_install_version_gi: 19.3.0.0
```

#### Example usage

```YAML

oracle_install_version_gi: 19.3.0.0

oracle_install_version_gi: 21.3.0.0
```

### oracle_opatch_patch

Mapping from OPatch ZIP-archive to Oracle Release.

The variable is configured for all supported Oracle Release by default.

#### Default value

```YAML
oracle_opatch_patch:
  - filename: p6880880_210000_Linux-x86-64.zip
    version: 21.3.0.0
  - filename: p6880880_190000_Linux-x86-64.zip
    version: 19.3.0.0
  - filename: p6880880_180000_Linux-x86-64.zip
    version: 18.3.0.0
  - filename: p6880880_122010_Linux-x86-64.zip
    version: 12.2.0.1
  - filename: p6880880_122010_Linux-x86-64.zip
    version: 12.1.0.2
  - filename: p6880880_121010_Linux-x86-64.zip
    version: 12.1.0.1
  - filename: p6880880_112000_Linux-x86-64.zip
    version: 11.2.0.4
  - filename: p6880880_112000_Linux-x86-64.zip
    version: 11.2.0.3
```

### oracle_pdbs

#### Default value

```YAML
oracle_pdbs:
  - home: 19300-base
    listener_port: 1521
    cdb: orcl
    pdb_name: ORCLPDB
    state: present
    statspack:
      purgedays: 14
      snaplevel: 7
      state: present
    tablespaces:
      - {name: system, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent,
        state: present, bigfile: false}
      - {name: sysaux, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent,
        state: present, bigfile: false}
      - {name: undotbs1, size: 10M, autoextend: true, next: 50M, maxsize: 8G, content: permanent,
        state: present, bigfile: false}
      - {name: users, size: 10M, autoextend: true, next: 50M, maxsize: 2G, content: permanent,
        state: present, bigfile: false}
      - {name: temp, size: 10M, autoextend: true, next: 50M, maxsize: 4G, content: permanent,
        state: present, bigfile: false}
```

### oracle_profile_template

Define which template is used to create .profile scripts.

_Important_

This variable is only used when `deploy_ocenv: false`. The default is `true`.

#### Default value

```YAML
oracle_profile_template: dotprofile-home.j2
```

### oracle_reco_dir_asm

#### Default value

```YAML
oracle_reco_dir_asm: +FRA
```

### oracle_reco_dir_fs

#### Default value

```YAML
oracle_reco_dir_fs: /u02/fra/
```

### oracle_stage_remote

#### Default value

```YAML
oracle_stage_remote: '{{ oracle_stage }}'
```

### oracle_sw_patches

Defines the list of known Patches in `ansible-oracle`.

Usage of this variable:

If a complete software repository with pathches is used with a nfs-mount, this variable is not needed.

#### Default value

```YAML
oracle_sw_patches: []
```

#### Example usage

```YAML
oracle_sw_patches:
  - filename: p28183653_122010_Linux-x86-64.zip
    patchid: 28183653
    version: 12.2.0.1
    patchversion: 12.2.0.1.180717
    description: GI-RU-July-2018
    creates: 28183653/28163133/files/suptools/orachk.zip
  - filename: p27468969_122010_Linux-x86-64.zip
    patchid: 27468969
    version: 12.2.0.1
    patchversion: 12.2.0.1.180417
    description: GI-RU-April-2018
    creates: 27468969/27674384/README.txt
  - filename: p28140658_12201180417DBAPR2018RU_Linux-x86-64.zip
    patchid: 28140658
    version: 12.2.0.1
    patchversion: 12201180417DBAPR2018RU
    description: 'PARALLEL QUERY Patch for Bug# 28140658 for Linux-x86-64 Platforms'
    creates: online/files/hpatch/bug28140658.pch
```

### oracle_sw_source_local

Define the directory when `` is set.

The archives are directly read from this directory.

#### Default value

```YAML
oracle_sw_source_local: /tmp
```

### oracle_sw_source_www

Define the URL for downloading installation medias and patches from a central
server during software installation and patching.

#### Default value

```YAML
oracle_sw_source_www: http://www/orasw
```

### shell_aliases

Define shell Aliases for oracle user.

#### Default value

```YAML
shell_aliases:
  - asmcmd='. oraenv ;rlwrap asmcmd -p'
  - sqlsyso='. oraenv ;rlwrap sqlplus "/ as sysdba"'
  - dgmgrl='rlwrap dgmgrl'
  - rman='rlwrap rman'
  - sid='export ORACLE_SID=$(ps -ef | grep "ora_pmon_$ORACLE_DBNAME" |grep -v grep
    | sed 's/^.*pmon_//g')'
  - sqlp='rlwrap sqlplus'
  - sqlsys='rlwrap sqlplus "/ as sysdba"'
  - dbh='cd $ORACLE_HOME'
  - dbb='cd $ORACLE_BASE'
  - talert='tail -500f $ORACLE_BASE/diag/rdbms/$ORA_DB_UNQ_NAME/$ORACLE_SID/trace/alert_$ORACLE_SID.log'
  - lalert='less $ORACLE_BASE/diag/rdbms/$ORA_DB_UNQ_NAME/$ORACLE_SID/trace/alert_$ORACLE_SID.log'
  - lsnrstart='lsnrctl start $LSNRNAME'
  - lsnrstop='lsnrctl stop $LSNRNAME'
  - lsnrstatus='lsnrctl status $LSNRNAME'
  - lsnrservice='lsnrctl services $LSNRNAME'
```

### shell_ps1

Configure shell prompt for OS-User oracle

#### Default value

```YAML
shell_ps1: "'[$LOGNAME'@'$ORACLE_SID `basename $PWD`]$'"
```

## Discovered Tags

**_always_**

**_assert_ansible_**\
&emsp;Assert version of Ansible Core

**_assert_ansible_oracle_**\
&emsp;Assert inventory variables from ansible-oracle

**_nfsmountdb_**

**_nfsumountdb_**

## Open Tasks

- (bug): add assert for install_from_nfs, nfs_server_sw, nfs_server_sw_path
- (bug): why do we need oracle_stage_remote?
- (bug): is_sw_source_local really needed with default or as dependency from other vars?
- (bug): Open Issue with changed behavior for `_oraswgi_meta_configure_cluster`
- (bug): Variable hosgroup needs a refactoring
- (bug): Change default from autostartup_service for Single Instance
- (bug): Check if shell_ps1 is used for oracle and grid
- (bug): Check when shell_aliases is used in ansible-oracle and change description
- (bug): check if assert for deploy_ocenv + ocenv_bashrc_init is existing
- (information): variable description is missing
- (information): variable description is missing
- (information): variable description is missing
- (information): db_homes_installed not used for a long time...
- (information): variable description is missing
- (information): variable description is missing
- (information): variable description is missing
- (information): variable description is missing
- (todo): Remove variable _www_download_bin

## Dependencies

- orahost_meta
- orasw_meta_internal

## License

license (MIT)

## Author

[Thorsten Bruhns]
