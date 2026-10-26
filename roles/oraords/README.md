# oraords

Install ORDS on Oracle Linux.

Defaults:

ORACLE_HOME: {{ oracle_base }}/product/ords

This role is limited to Oracle Linux, due to installation
from yum Repository from Oracle.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oraords_apex_image_context](#oraords_apex_image_context)
  - [oraords_apex_image_path](#oraords_apex_image_path)
  - [oraords_db_pools](#oraords_db_pools)
  - [oraords_default_admin_user](#oraords_default_admin_user)
  - [oraords_default_port](#oraords_default_port)
  - [oraords_java_rpm](#oraords_java_rpm)
  - [oraords_oracle_home](#oraords_oracle_home)
  - [oraords_ords_bin](#oraords_ords_bin)
  - [oraords_ords_config](#oraords_ords_config)
  - [oraords_ords_logs](#oraords_ords_logs)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### oraords_apex_image_context

APEX context path for Images.

### oraords_apex_image_path

Directory for APEX Images on ORDS Host.

### oraords_db_pools

List of configured target in ORDS.

Attributes:

db_pool: <Pool in ORDS>

admin_user: <Admin user for ORDS installation. Defaults to `oraords_default_admin_user`>

service: <Servicename of target. Mandatory>

port: <Listener Port. Defaults to `oraords_default_port`>

host: <Hostname for target. Defaults to `inventory_hostname`>

feature_db_api: <true / false (default)>

feature_rest_enabled_sql: <true / false (default)>

feature_sdw: <true / false (default)>

#### Default value

```YAML
oraords_db_pools:
  - db_pool: default
    admin_user: sys
    service: orclpdb
    port: 1521
```

### oraords_default_admin_user

#### Default value

```YAML
oraords_default_admin_user: sys
```

### oraords_default_port

#### Default value

```YAML
oraords_default_port: 1521
```

### oraords_java_rpm

#### Default value

```YAML
oraords_java_rpm: java-21-openjdk
```

### oraords_oracle_home

`ORACLE_HOME` for _ORDS_.

#### Default value

```YAML
oraords_oracle_home: >-
  {{ oracle_base }}/product/ords
```

### oraords_ords_bin

PATH for ords binary

#### Default value

```YAML
oraords_ords_bin: >-
  /opt/oracle/ords/bin
```

### oraords_ords_config

ORDS configuration directory.

#### Default value

```YAML
oraords_ords_config: >-
  /etc/ords/config
```

### oraords_ords_logs

ORDS logging directory.

#### Default value

```YAML
oraords_ords_logs: >-
  /etc/ords/logs
```

## Discovered Tags

**_always_**

**_ords_config_**

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

Thorsten Bruhns
