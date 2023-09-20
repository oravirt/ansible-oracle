# oradb_manage_db

Create, modify and remove Oracle Databases

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [dbca_templatename](#dbca_templatename)
  - [hostgroup_hub](#hostgroup_hub)
  - [listener_name](#listener_name)
  - [oracle_gi_cluster_type](#oracle_gi_cluster_type)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### dbca_templatename

Default template name used by DBCA during execution.

#### Default value

```YAML
dbca_templatename: General_Purpose.dbc
```

### hostgroup_hub

#### Default value

```YAML
hostgroup_hub: '{{ hostgroup }}-hub'
```

### listener_name

Default name for LISTENER

#### Default value

```YAML
listener_name: LISTENER
```

### oracle_gi_cluster_type

#### Default value

```YAML
oracle_gi_cluster_type: STANDARD
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

**_listener_**

**_listener2_**

**_listener_install_**

**_molecule-idempotence-notest_**

**_odb_assert_**

**_psout_**

**_remove_db,dbca_**

**_responsefile_netca, listener_install_**

**_set_fact_**

**_sql_script_**

**_sqlnet2_**

**_tnsnames_**

**_tnsnames2_**

**_update_oratab_**

## Open Tasks

- (bug): replace netca with new listener_details tasks

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
