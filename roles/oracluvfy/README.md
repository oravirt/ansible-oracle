# oracluvfy

Manage Cluster Verification Utility from Oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oracluvfy_archive](#oracluvfy_archive)
  - [oracluvfy_force_update](#oracluvfy_force_update)
  - [oracluvfy_home](#oracluvfy_home)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### oracluvfy_archive

ZIP Archive used by the role.

#### Default value

```YAML
oracluvfy_archive: cvupack_linux_ol7_x86_64.zip
```

### oracluvfy_force_update

Force unarchive of cluvfy in `oracluvfy_home`.

#### Default value

```YAML
oracluvfy_force_update: false
```

### oracluvfy_home

#### Default value

```YAML
oracluvfy_home: '{{ oracle_base }}/product/cluvfy'
```

## Discovered Tags

**_always_**

**_assert_**

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
