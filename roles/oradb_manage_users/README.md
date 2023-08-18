# oradb_manage_users

Manage Users in Oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [configure_cluster](#configure_cluster)
  - [db_mode](#db_mode)
  - [db_password_cdb](#db_password_cdb)
  - [db_password_pdb](#db_password_pdb)
  - [db_service_name](#db_service_name)
  - [db_user](#db_user)
  - [listener_port](#listener_port)
  - [listener_port_template](#listener_port_template)
  - [oracle_base](#oracle_base)
  - [oracle_env](#oracle_env)
  - [user_cdb_password](#user_cdb_password)
  - [user_pdb_password](#user_pdb_password)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### configure_cluster

#### Default value

```YAML
configure_cluster: false
```

### db_mode

#### Default value

```YAML
db_mode: sysdba
```

### db_password_cdb

#### Default value

```YAML
db_password_cdb: '{% if dbpasswords is defined and dbpasswords[item.0.oracle_db_name]
  is defined and dbpasswords[item.0.oracle_db_name][db_user] is defined%}{{ dbpasswords[item.0.oracle_db_name][db_user]
  }} {%- else %}{{ default_dbpass }} {%- endif %}'
```

### db_password_pdb

#### Default value

```YAML
db_password_pdb: '{% if dbpasswords is defined and dbpasswords[item.0.cdb] is defined
  and dbpasswords[item.0.cdb][db_user] is defined %}{{ dbpasswords[item.0.cdb][db_user]
  }} {%- else %}{{ default_dbpass }} {%- endif %}'
```

### db_service_name

#### Default value

```YAML
db_service_name: '{% if item.0 is defined %} {%- if item.0.oracle_db_unique_name is
  defined %}{{ item.0.oracle_db_unique_name }} {%- elif item.0.oracle_db_instance_name
  is defined %}{{ item.0.oracle_db_instance_name }} {%- else %}{{ item.0.oracle_db_name
  }} {%- endif %} {%- endif %}'
```

### db_user

#### Default value

```YAML
db_user: sys
```

### listener_port

#### Default value

```YAML
listener_port: 1521
```

### listener_port_template

#### Default value

```YAML
listener_port_template: '{% if item.0.listener_port is defined %}{{ item.0.listener_port
  }}{% else %}{{ listener_port }}{% endif %}'
```

### oracle_base

#### Default value

```YAML
oracle_base: /u01/app/oracle
```

### oracle_env

#### Default value

```YAML
oracle_env:
  ORACLE_HOME: '{{ oracle_home_db }}'
  LD_LIBRARY_PATH: '{{ oracle_home_db }}/lib'
```

### user_cdb_password

#### Default value

```YAML
user_cdb_password: '{% if dbpasswords is defined and dbpasswords[item.0.oracle_db_name]
  is defined and dbpasswords[item.0.oracle_db_name][item.1.schema] is defined %}{{
  dbpasswords[item.0.oracle_db_name][item.1.schema] }} {%- else %}{{ default_dbpass
  }} {%- endif %}'
```

### user_pdb_password

#### Default value

```YAML
user_pdb_password: '{% if dbpasswords is defined and dbpasswords[item.0.cdb] is defined
  and dbpasswords[item.0.cdb][item.0.pdb_name] is defined and dbpasswords[item.0.cdb][item.0.pdb_name][item.1.schema]
  is defined %}{{ dbpasswords[item.0.cdb][item.0.pdb_name][item.1.schema] }} {%- else
  %}{{ default_dbpass }} {%- endif %}'
```

## Discovered Tags

**_users_**


## Dependencies

- orasw_meta
- oradb_facts

## License

license (MIT)

## Author

Mikael Sandström
