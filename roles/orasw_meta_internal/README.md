# orasw_meta_internal

Meta role used to store internal variables from `ansible-oracle`.

Do not use any of the variables in your inventory!

This will create issues and problems in `ansible-oracle` and is not supported.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [_db_password_cdb](#_db_password_cdb)
  - [_db_password_pdb](#_db_password_pdb)
  - [_db_service_name](#_db_service_name)
  - [_db_service_pdb](#_db_service_pdb)
  - [_db_unique_name_for_pdb](#_db_unique_name_for_pdb)
  - [_grid_env](#_grid_env)
  - [_listener_port_cdb](#_listener_port_cdb)
  - [_listener_port_pdb](#_listener_port_pdb)
  - [_odb_loop_helper](#_odb_loop_helper)
  - [_opdb_home](#_opdb_home)
  - [_opdb_loop_helper](#_opdb_loop_helper)
  - [_oracle_all_editions_options](#_oracle_all_editions_options)
  - [_oracle_db_instance_name](#_oracle_db_instance_name)
  - [_oracle_db_unique_name](#_oracle_db_unique_name)
  - [_oracle_ee_opiton_dict](#_oracle_ee_opiton_dict)
  - [_oracle_env](#_oracle_env)
  - [_oracle_env_pdb](#_oracle_env_pdb)
  - [_oracle_home_db](#_oracle_home_db)
  - [_oracle_home_db_pdb](#_oracle_home_db_pdb)
  - [cluster_master](#cluster_master)
  - [db_mode](#db_mode)
  - [db_password](#db_password)
  - [db_service_name](#db_service_name)
  - [db_user](#db_user)
  - [db_version](#db_version)
  - [grid_env](#grid_env)
  - [listener_home](#listener_home)
  - [listener_port_template](#listener_port_template)
  - [listener_protocols](#listener_protocols)
  - [ocm_response_file](#ocm_response_file)
  - [oracle_all_editions_options](#oracle_all_editions_options)
  - [oracle_env](#oracle_env)
  - [oracle_env_lsnrctl](#oracle_env_lsnrctl)
  - [oracle_home_db](#oracle_home_db)
  - [oracle_home_gi](#oracle_home_gi)
  - [oracle_patch_install](#oracle_patch_install)
  - [oracle_patch_stage](#oracle_patch_stage)
  - [oracle_patch_stage_remote](#oracle_patch_stage_remote)
  - [oracle_stage_install](#oracle_stage_install)
  - [oracle_sw_copy](#oracle_sw_copy)
  - [oracle_sw_extract_path](#oracle_sw_extract_path)
  - [oracle_sw_unpack](#oracle_sw_unpack)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### _db_password_cdb

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_db_password_cdb: _internal_used_
```

### _db_password_pdb

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_db_password_pdb: _internal_used_
```

### _db_service_name

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_db_service_name: _internal_used_
```

### _db_service_pdb

The variable is internal used only.

Do not set it in inventory!

Get the service_name for a PDB.

Requires `opdb` as `loop_var`.

#### Default value

```YAML
_db_service_pdb: _internal_used_
```

### _db_unique_name_for_pdb

The variable is internal used only.

Do not set it in inventory!

get db_unique_name from CDB for current pdb
Requires `opdb` as `loop_var`.

#### Default value

```YAML
_db_unique_name_for_pdb: _internal_used_
```

### _grid_env

The variable is used for shell, command tasks to set environment Variables.

Do not set it in inventory!

#### Default value

```YAML
_grid_env:
  ORACLE_HOME: '{{ oracle_home_gi }}'
  LD_LIBRARY_PATH: '{{ oracle_home_gi }}/lib'
```

### _listener_port_cdb

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_listener_port_cdb: _internal_used_
```

### _listener_port_pdb

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_listener_port_pdb: _internal_used_
```

### _odb_loop_helper

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_odb_loop_helper: _internal_used_
```

### _opdb_home

#### Default value

```YAML
_opdb_home: "{{ (oracle_databases | selectattr('oracle_db_name', 'equalto', _opdb_loop_helper['cdb']))[0]['home']
  }}"
```

### _opdb_loop_helper

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_opdb_loop_helper: _internal_used_
```

### _oracle_all_editions_options

Defines linkable options available for all editions of oracle database (e.g. Unified auditing, DirectNFS)
Dictionary key (dnfs, uniaud, etc.), suffixed by _on/_off, must match the make target in {{ oracle_home_db }}/rdbms/lib/ins_rdbms.mk
match_file: File relative to {{ oracle_home_db }} where to grep for current state of the option
enabled_matches: Pattern that matches in match_file if option currently is enabled

### _oracle_db_instance_name

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_oracle_db_instance_name: _internal_used_
```

### _oracle_db_unique_name

The variable is internal used only.

Do not set it in inventory!

#### Default value

```YAML
_oracle_db_unique_name: _internal_used_
```

### _oracle_ee_opiton_dict

This is an internal variable in `ansible-oracle`.

_IMPORTANT_

Do not set this variable in inventory, set_fact ...!

#### Default value

```YAML
_oracle_ee_opiton_dict:
  11.2.0.4: '{{ oracle_ee_options_112 }}'
  12.1.0.1: '{{ oracle_ee_options_121 }}'
  12.1.0.2: '{{ oracle_ee_options_121 }}'
  12.2.0.1: '{{ oracle_ee_options_122 }}'
  18.3.0.0: '{{ oracle_ee_options_183 }}'
  19.3.0.0: '{{ oracle_ee_options_193 }}'
  21.3.0.0: '{{ oracle_ee_options_213 }}'
```

### _oracle_env

The variable is used for shell, command tasks to set environment Variables.

Do not set it in inventory!

#### Default value

```YAML
_oracle_env:
  ORACLE_HOME: '{{ _oracle_home_db }}'
  LD_LIBRARY_PATH: '{{ _oracle_home_db }}/lib'
```

### _oracle_env_pdb

#### Default value

```YAML
_oracle_env_pdb:
  ORACLE_HOME: '{{ _oracle_home_db_pdb }}'
  LD_LIBRARY_PATH: '{{ _oracle_home_db_pdb }}/lib'
```

### _oracle_home_db

This is an internal variable in `ansible-oracle`.

Do not set it in inventory!

#### Default value

```YAML
_oracle_home_db: _internal_used_
```

### _oracle_home_db_pdb

#### Default value

```YAML
_oracle_home_db_pdb: "{{ db_homes_config[_opdb_home]['oracle_home'] }}"
```

### cluster_master

#### Default value

```YAML
cluster_master: '{{ play_hosts[0] }}'
```

### db_mode

#### Default value

```YAML
db_mode: sysdba
```

### db_password

#### Default value

```YAML
db_password: >-
  {% if dbpasswords is defined
      and dbpasswords[item.oracle_db_name] is defined
      and dbpasswords[item.oracle_db_name][db_user] is defined -%}
    {{- dbpasswords[item.oracle_db_name][db_user] }}
  {%- else %}{{ default_dbpass }}
  {%- endif %}
```

### db_service_name

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
db_service_name: '{% if item is defined -%} {%- if item.oracle_db_unique_name is defined
  -%}{{ item.oracle_db_unique_name }}{%- elif item.oracle_db_instance_name is defined
  -%}{{ item.oracle_db_instance_name }}{%- else -%}{{ item.oracle_db_name }}{%- endif
  -%}{%- endif %}'
```

### db_user

#### Default value

```YAML
db_user: sys
```

### db_version

This is an internal variable in `ansible-oracle`.

_IMPORTANT_

Do not set this variable in inventory, set_fact ...!

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
db_version: _unset_
```

### grid_env

The variable is used for shell, command tasks to set environment Variables.

Do not set it in inventory!

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
grid_env:
  ORACLE_HOME: '{{ oracle_home_gi }}'
  LD_LIBRARY_PATH: '{{ oracle_home_gi }}/lib'
```

### listener_home

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
listener_home: "{%- if lsnrinst is defined -%}{%- if db_homes_config[lsnrinst.home]['oracle_home']
  is defined -%}{{ db_homes_config[lsnrinst.home]['oracle_home'] }}{%- else -%}{{
  oracle_base }}/{{ db_homes_config[lsnrinst.home]['version'] }}/{{ db_homes_config[lsnrinst.home]['home']
  }}{%- endif -%}{%- endif -%}"
```

### listener_port_template

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
listener_port_template: '{% if item.listener_port is defined %}{{ item.listener_port
  }}{% else %}{{ listener_port }}{% endif %}'
```

### listener_protocols

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
listener_protocols: TCP
```

### ocm_response_file

#### Default value

```YAML
ocm_response_file: '{{ oracle_patch_stage }}/{{ db_version }}/ocm.rsp'
```

### oracle_all_editions_options

#### Default value

```YAML
oracle_all_editions_options:
  21.3.0.0: &213_all_editions_options
    dnfs:
      match_file: rdbms/lib/odm/libnfsodm??.so
      enabled_matches: .*
    uniaud:
      match_file: rdbms/lib/libknlopt.a
      enabled_matches: \bkzaiang\.
  19.3.0.0:
    <<: *213_all_editions_options
  18.3.0.0:
    <<: *213_all_editions_options
  12.2.0.1:
    <<: *213_all_editions_options
  12.1.0.2:
    <<: *213_all_editions_options
  12.1.0.1:
    <<: *213_all_editions_options
  11.2.0.4: &1124_all_editions_options
    dnfs:
      match_file: rdbms/lib/odm/libnfsodm??.so
      enabled_matches: .*
  11.2.0.3:
    <<: *1124_all_editions_options
```

### oracle_env

The variable is used for shell, command tasks to set environment Variables.

Do not set it in inventory!

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
oracle_env:
  ORACLE_HOME: '{{ oracle_home_db }}'
  LD_LIBRARY_PATH: '{{ oracle_home_db }}/lib'
```

### oracle_env_lsnrctl

The variable is used for shell, command tasks to set environment Variables.

Do not set it in inventory!

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
oracle_env_lsnrctl:
  ORACLE_BASE: '{{ oracle_base }}'
  ORACLE_HOME: '{{ listener_home }}'
  LD_LIBRARY_PATH: '{{ listener_home }}/lib'
  PATH: '{{ listener_home }}/bin:$PATH:/usr/local/bin:/bin:/sbin:/usr/bin:/usr/sbin'
```

### oracle_home_db

This is an internal variable in `ansible-oracle`.

The variable is deprecated and removed in a future version.

_IMPORTANT_

Do not set this variable in inventory, set_fact ...!

**_Deprecated:_** since v4.0.0<br />

#### Default value

```YAML
oracle_home_db: _unset_
```

### oracle_home_gi

Custom setting for CRS_HOME.

The default value depends on `_oraswgi_meta_configure_cluster` and `oracle_home_gi_cl` or `oracle_home_gi_so`.

#### Default value

```YAML
oracle_home_gi: '{% if oracle_install_version_gi is defined -%}{%- if _oraswgi_meta_configure_cluster
  -%}{{ oracle_home_gi_cl }}{%- else -%}{{ oracle_home_gi_so }}{%- endif -%}{%- endif
  %}'
```

### oracle_patch_install

#### Default value

```YAML
oracle_patch_install: '{% if not oracle_sw_copy and not oracle_sw_unpack %}{{ oracle_patch_stage_remote
  }}{% else %}{{ oracle_patch_stage }}{% endif %}'
```

### oracle_patch_stage

#### Default value

```YAML
oracle_patch_stage: '{{ oracle_stage }}/patches'
```

### oracle_patch_stage_remote

#### Default value

```YAML
oracle_patch_stage_remote: '{{ oracle_stage_remote }}/patches'
```

### oracle_stage_install

This is an internal variable. Do not set it in Inventory.

#### Default value

```YAML
oracle_stage_install: '{% if not oracle_sw_copy and not oracle_sw_unpack %}{{ oracle_stage_remote
  }}{% else %}{{ oracle_stage }}{% endif %}'
```

### oracle_sw_copy

#### Default value

```YAML
oracle_sw_copy: '{% if install_from_nfs %}false{% else %}true{% endif %}'
```

### oracle_sw_extract_path

#### Default value

```YAML
oracle_sw_extract_path: "{%- if '18' in db_version -%}{{ oracle_home_db }}{%- else
  -%}{{ oracle_stage }}/{{ item[0].version }}{%- endif -%}"
```

### oracle_sw_unpack

#### Default value

```YAML
oracle_sw_unpack: '{% if install_from_nfs %}false{% else %}true{% endif %}'
```

## Dependencies

None.

## License

license (MIT)

## Author

[Thorsten Bruhns]
