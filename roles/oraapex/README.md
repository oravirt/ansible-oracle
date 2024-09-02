# oraapex

The role is in pre ALPHA state.

A lot of changes are planned during development at the moment.

Limitations:

- Oracle RDBMS 19c+ - older versions may work but not tested anymore.
- Installation in nonCDB or single PDB only - no CDB installation at the moment
- RAC not tested yet.

Documentation: https://github.com/oravirt/ansible-oracle/blob/master/doc/guides/apex_ords.adoc

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oraapex_base](#oraapex_base)
  - [oraapex_default_admin_password](#oraapex_default_admin_password)
  - [oraapex_default_files_tablespace](#oraapex_default_files_tablespace)
  - [oraapex_default_tablespace](#oraapex_default_tablespace)
  - [oraapex_default_temp_tablespace](#oraapex_default_temp_tablespace)
  - [oraapex_image_path](#oraapex_image_path)
  - [oraapex_rac_primary_node_only](#oraapex_rac_primary_node_only)
  - [oraapex_rac_primary_only](#oraapex_rac_primary_only)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.15.0`

## Default Variables

### oraapex_base

`oraapex_base` is used as a prefix directory for unzip for apex.zip.

#### Default value

```YAML
oraapex_base: >-
  {{ oracle_base }}/product
```

### oraapex_default_admin_password

Password for apex_admin_user from `oracle_databases` or `oracle_pdbs`.

### oraapex_default_files_tablespace

#### Default value

```YAML
oraapex_default_files_tablespace: SYSAUX
```

### oraapex_default_tablespace

#### Default value

```YAML
oraapex_default_tablespace: SYSAUX
```

### oraapex_default_temp_tablespace

#### Default value

```YAML
oraapex_default_temp_tablespace: TEMP
```

### oraapex_image_path

#### Default value

```YAML
oraapex_image_path: /i/
```

### oraapex_rac_primary_node_only

#### Default value

```YAML
oraapex_rac_primary_node_only: true
```

### oraapex_rac_primary_only

unarchive apex.zip in RAC only on 1st node or on all nodes?

This is only true, when ORDS runs on RAC nodes as well, because we need
the images for ORDS. This should not be done on production setups!


## Open Tasks

- (information): oraapex_rac_primary_only not implemented yet.

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author



- Thorsten Bruhns
