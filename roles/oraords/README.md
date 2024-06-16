# oraords

Install ORDS on Oracle Linux.

Defaults:

ORACLE_HOME: {{ oracle_base }}/product/ords

This role is limited to Oracle Linux, due to installation
from yum Repository from Oracle.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oraords_apex_image_path](#oraords_apex_image_path)
  - [oraords_db_pools](#oraords_db_pools)
  - [oraords_default_admin_user](#oraords_default_admin_user)
  - [oraords_default_port](#oraords_default_port)
  - [oraords_java_rpm](#oraords_java_rpm)
  - [oraords_oracle_home](#oraords_oracle_home)
  - [oraords_ords_bin](#oraords_ords_bin)
  - [oraords_ords_config](#oraords_ords_config)
  - [oraords_ords_logs](#oraords_ords_logs)
  - [ords_config](#ords_config)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### oraords_apex_image_path

Directory for APEX Images on ORDS Host.

### oraords_db_pools

List of configured target in ORDS.

Attributes:

db_pool: <Pool in ORDS>

pdb_name: <Target PDB. Needed to find the Password s>

port: <Listener Port>

service: <servicename of target. Defaults to pdb_name>

hostname: <Hostname for target. Defaults to `inventory_hostname`>

#### Default value

```YAML
oraords_db_pools:
  - db_pool: default
    pdb_name: orclpdb
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

#### Default value

```YAML
oraords_ords_bin: >-
  /usr/local/bin
```

### oraords_ords_config

#### Default value

```YAML
oraords_ords_config: >-
  /etc/ords/config
```

### oraords_ords_logs

#### Default value

```YAML
oraords_ords_logs: >-
  /etc/ords/logs
```

### ords_config

APEX context path for Images.

## Discovered Tags

**_ords_config_**


## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

Thorsten Bruhns
