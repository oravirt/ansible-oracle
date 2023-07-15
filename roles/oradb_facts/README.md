# oradb_facts

Gather Ansible Facts from database

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [__db_service_name](#__db_service_name)
  - [__db_user](#__db_user)
  - [__listener_port](#__listener_port)
  - [__oracle_env](#__oracle_env)
  - [__oracle_home_db](#__oracle_home_db)
  - [_db_password_cdb](#_db_password_cdb)
  - [listener_port](#listener_port)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### __db_service_name

#### Default value

```YAML
__db_service_name: '{% if odb.0 is defined %} {%- if odb.0.oracle_db_unique_name is
  defined %}{{ odb.0.oracle_db_unique_name }} {%- elif odb.0.oracle_db_instance_name
  is defined %}{{ odb.0.oracle_db_instance_name }} {%- else %}{{ odb.0.oracle_db_name
  }} {%- endif %} {%- endif %}'
```

### __db_user

#### Default value

```YAML
__db_user: sys
```

### __listener_port

#### Default value

```YAML
__listener_port: '{{ odb.0.listener_port | default(listener_port) }}'
```

### __oracle_env

#### Default value

```YAML
__oracle_env:
  ORACLE_HOME: '{{ __oracle_home_db }}'
  LD_LIBRARY_PATH: '{{ __oracle_home_db }}/lib'
```

### __oracle_home_db

#### Default value

```YAML
__oracle_home_db: >-
  {%- if odb[0] is defined -%}
  {%- if db_homes_config[odb[0]['home']]['oracle_home'] is defined -%}
  {{ db_homes_config[odb[0]['home']]['oracle_home'] }}{%- endif -%}{%- endif -%}
```

### _db_password_cdb

#### Default value

```YAML
_db_password_cdb: >-
  {% if dbpasswords is defined
      and dbpasswords[odb.0.oracle_db_name] is defined
      and dbpasswords[odb.0.oracle_db_name][db_user] is defined -%}
      {{ dbpasswords[odb.0.oracle_db_name][db_user] }}
  {%- else %}{{ default_dbpass }}
  {%- endif %}
```

### listener_port

#### Default value

```YAML
listener_port: 1521
```

## Discovered Tags

**_db_facts_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

Thorsten Bruhns
