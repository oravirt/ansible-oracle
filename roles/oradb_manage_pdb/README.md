# oradb_manage_pdb

Manage pluggable databases in Oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [pdbadmin_password](#pdbadmin_password)
  - [pdbadmin_user](#pdbadmin_user)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### pdbadmin_password

Password for pdb_admin user.

#### Default value

```YAML
pdbadmin_password: >-
  {{ dbpasswords[odb.1.cdb][odb.1.pdb_name][pdbadmin_user] | default(default_dbpass)
  }}
```

### pdbadmin_user

Default pdb_admin user for newly created PDBs.

Could be set in `oracle_pdbs` to define different pdb_admin user for each PDB.

#### Default value

```YAML
pdbadmin_user: >-
  {{ odb[1].pdbadmin_user | default('PDBADMIN') }}
```

## Discovered Tags

**_pdb_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
