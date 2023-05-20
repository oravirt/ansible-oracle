# oradb_manage_services

Manage services in Oracle

## Table of content

- [Requirements](#requirements)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Discovered Tags

**_create_service,services_**

**_start_service,services_**

## Open Tasks

- (bug): Module oracle_services does not support 'as sysdba'. Connect User system is hard coded for the moment...
- (bug): Role require Oracle Restart/GI at the moment

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
