# oradb_datapatch

Manage datapatch for Oracle Database

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oradb_datapatch_fail_on_db_not_exist](#oradb_datapatch_fail_on_db_not_exist)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### oradb_datapatch_fail_on_db_not_exist

Should task for datapatch fail when database from `oracle_databases` is not existing?

Important!
Do not use `fail_on_db_not_exist` anymore.
The variable is deprecated and will be removed in a future release!

#### Default value

```YAML
oradb_datapatch_fail_on_db_not_exist: '{{ fail_on_db_not_exist | default(false) }}'
```

## Discovered Tags

**_datapatch_**

**_startdb_**

## Open Tasks

- (bug): Do we really need db-connection here?

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
