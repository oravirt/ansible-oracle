# oradb_facts

Gather Ansible Facts from database

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oradb_facts_db_user](#oradb_facts_db_user)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### oradb_facts_db_user

The dbuser for connection to database.

#### Default value

```YAML
oradb_facts_db_user: sys
```

## Discovered Tags

**_db_facts_**

## Open Tasks

- (bug): parameter user, password and sysdba needs a refactoring

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

Thorsten Bruhns
