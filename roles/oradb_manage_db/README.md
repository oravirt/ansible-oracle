# oradb_manage_db

Create, modify and remove Oracle Databases

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [asmmonitorpassword](#asmmonitorpassword)
  - [create_listener](#create_listener)
  - [datafile_dest](#datafile_dest)
  - [dbca_sys_pass](#dbca_sys_pass)
  - [dbca_system_pass](#dbca_system_pass)
  - [dbca_templatename](#dbca_templatename)
  - [default_gipass](#default_gipass)
  - [hostgroup_hub](#hostgroup_hub)
  - [init_params_list](#init_params_list)
  - [listener_home](#listener_home)
  - [listener_home_config](#listener_home_config)
  - [listener_name](#listener_name)
  - [listener_port](#listener_port)
  - [listener_protocols_template](#listener_protocols_template)
  - [oracle_dbca_rsp](#oracle_dbca_rsp)
  - [oracle_env_dbca](#oracle_env_dbca)
  - [oracle_env_lsnrctl](#oracle_env_lsnrctl)
  - [oracle_gi_cluster_type](#oracle_gi_cluster_type)
  - [oracle_netca_rsp](#oracle_netca_rsp)
  - [oracle_rsp_stage](#oracle_rsp_stage)
  - [recoveryfile_dest](#recoveryfile_dest)
  - [sysasmpassword](#sysasmpassword)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### asmmonitorpassword

#### Default value

```YAML
asmmonitorpassword: '{% if oracle_password is defined %}{{ oracle_password }}{%- else
  %}Oracle123{%- endif %}'
```

### create_listener

#### Default value

```YAML
create_listener: '{%- if oracle_install_option_gi is defined -%}False{%- elif oracle_install_option_gi
  is undefined -%}{%- if dbh is defined and dbh.listener_name is defined -%}True{%-
  else -%}False{%- endif -%}{%- endif -%}'
```

### datafile_dest

#### Default value

```YAML
datafile_dest: "{% if dbh.storage_type | upper == 'FS' %}{{ oracle_dbf_dir_fs }}{%-\
  \ elif dbh.storage_type | upper == 'ASM' %}{{ oracle_dbf_dir_asm }}{%- endif %}"
```

### dbca_sys_pass

#### Default value

```YAML
dbca_sys_pass: "{% if dbpasswords[dbh.oracle_db_name] is defined %}{%- if dbpasswords[dbh.oracle_db_name]['sys']\
  \ is defined %}{{ dbpasswords[dbh.oracle_db_name]['sys'] }}{%- else %}{{ default_dbpass\
  \ }}{%- endif %}{%- else %}{{ default_dbpass }}{%- endif %}"
```

### dbca_system_pass

#### Default value

```YAML
dbca_system_pass: "{% if dbpasswords[dbh.oracle_db_name] is defined %}{%- if dbpasswords[dbh.oracle_db_name]['system']\
  \ is defined %}{{ dbpasswords[dbh.oracle_db_name]['system'] }}{%- else %}{{ default_dbpass\
  \ }}{%- endif %}{%- else %}{{ default_dbpass }}{%- endif %}"
```

### dbca_templatename

#### Default value

```YAML
dbca_templatename: General_Purpose.dbc
```

### default_gipass

#### Default value

```YAML
default_gipass: '{% if oracle_password is defined %}{{ oracle_password }}{%- else
  %}Oracle123{% endif %}'
```

### hostgroup_hub

#### Default value

```YAML
hostgroup_hub: '{{ hostgroup }}-hub'
```

### init_params_list

#### Default value

```YAML
init_params_list: '{%- if dbh.init_parameters is defined -%}{%- for p in dbh.init_parameters
  -%}{%- if p.dbca | default(True) -%}{{ p.name }}={{ p.value }}{%- if not loop.last
  -%},{%- endif -%}{%- endif -%}{%- endfor -%}{%- endif -%}'
```

### listener_home

#### Default value

```YAML
listener_home: "{%- if lsnrinst is defined -%}{%- if db_homes_config[lsnrinst.home]['oracle_home']\
  \ is defined -%}{{ db_homes_config[lsnrinst.home]['oracle_home'] }}{%- else -%}{{\
  \ oracle_base }}/{{ db_homes_config[lsnrinst.home]['version'] }}/{{ db_homes_config[lsnrinst.home]['home']\
  \ }}{%- endif -%}{%- elif tnsinst is defined -%}{%- if db_homes_config[tnsinst.home]['oracle_home']\
  \ is defined -%}{{ db_homes_config[tnsinst.home]['oracle_home'] }}{%- else -%}{{\
  \ oracle_base }}/{{ db_homes_config[tnsinst.home]['version'] }}/{{ db_homes_config[tnsinst.home]['home']\
  \ }}{%- endif -%}{%- elif sqlnetinst is defined -%}{%- if db_homes_config[sqlnetinst.home]['oracle_home']\
  \ is defined -%}{{ db_homes_config[sqlnetinst.home]['oracle_home'] }}{%- else -%}{{\
  \ oracle_base }}/{{ db_homes_config[sqlnetinst.home]['version'] }}/{{ db_homes_config[sqlnetinst.home]['home']\
  \ }}{%- endif -%}{%- endif -%}"
```

### listener_home_config

#### Default value

```YAML
listener_home_config: "{%- if lsnrinst is defined -%}{%- if db_homes_config[lsnrinst.home]['readonly_home']\
  \ | default(false) -%}{{ oracle_base }}/homes/{{ db_homes_config[lsnrinst.home]['oracle_home_name']\
  \ }}{%- else -%}{{ listener_home }}{%- endif -%}{%- elif tnsinst is defined -%}{%-\
  \ if db_homes_config[tnsinst.home]['readonly_home'] | default(false) -%}{{ oracle_base\
  \ }}/homes/{{ db_homes_config[tnsinst.home]['oracle_home_name'] }}{%- else -%}{{\
  \ listener_home }}{%- endif -%}{%- elif sqlnetinst is defined -%}{%- if db_homes_config[sqlnetinst.home]['readonly_home']\
  \ | default(false) -%}{{ oracle_base }}/homes/{{ db_homes_config[sqlnetinst.home]['oracle_home_name']\
  \ }}{%- else -%}{{ listener_home }}{%- endif -%}{%- endif -%}"
```

### listener_name

#### Default value

```YAML
listener_name: LISTENER
```

### listener_port

#### Default value

```YAML
listener_port: 1521
```

### listener_protocols_template

#### Default value

```YAML
listener_protocols_template: '{% if dbh.listener_protocols is defined %}{{ dbh.listener_protocols
  }}{% else %}{{ listener_protocols }}{% endif %}'
```

### oracle_dbca_rsp

This is an internal variable in `ansible-oracle`.

_IMPORTANT_

Do not set this variable in inventory, set_fact ...!

#### Default value

```YAML
oracle_dbca_rsp: dbca_{{ dbh.oracle_db_name }}.rsp
```

### oracle_env_dbca

#### Default value

```YAML
oracle_env_dbca:
  ORACLE_HOME: '{{ oracle_home_db }}'
  LD_LIBRARY_PATH: '{{ oracle_home_db }}/lib'
```

### oracle_env_lsnrctl

#### Default value

```YAML
oracle_env_lsnrctl:
  ORACLE_BASE: '{{ oracle_base }}'
  ORACLE_HOME: '{{ listener_home }}'
  LD_LIBRARY_PATH: '{{ listener_home }}/lib'
  PATH: '{{ listener_home }}/bin:$PATH:/usr/local/bin:/bin:/sbin:/usr/bin:/usr/sbin'
```

### oracle_gi_cluster_type

#### Default value

```YAML
oracle_gi_cluster_type: STANDARD
```

### oracle_netca_rsp

This is an internal variable in `ansible-oracle`.

_IMPORTANT_

Do not set this variable in inventory, set_fact ...!

#### Default value

```YAML
oracle_netca_rsp: netca_{{ dbh.home }}_{{ listener_name_template }}.rsp
```

### oracle_rsp_stage

#### Default value

```YAML
oracle_rsp_stage: '{{ oracle_stage }}/rsp'
```

### recoveryfile_dest

#### Default value

```YAML
recoveryfile_dest: "{% if dbh.storage_type | upper == 'FS' %}{{ oracle_reco_dir_fs\
  \ }}{%- elif dbh.storage_type | upper == 'ASM' %}{{ oracle_reco_dir_asm }}{%- endif\
  \ %}"
```

### sysasmpassword

#### Default value

```YAML
sysasmpassword: '{% if oracle_password is defined %}{{ oracle_password }}{%- else
  %}Oracle123{% endif %}'
```

## Discovered Tags

**_always_**

**_create_cdb,dotprofile_db_**

**_create_db,dbca,customdbcatemplate,dotprofile_db,listener2_**

**_create_db,dbcatemplate_**

**_create_db,dotprofile_db_**

**_create_db,manage_db,dbca_**

**_customdbcatemplate_**

**_dbcatemplate_**

**_dbh_assert_**

**_listener_**

**_listener2_**

**_listener_install_**

**_psout_**

**_remove_db,dbca_**

**_responsefile_netca, listener_install_**

**_set_fact_**

**_sql_script_**

**_sqlnet2_**

**_tnsnames_**

**_tnsnames2_**

**_update_oratab_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
