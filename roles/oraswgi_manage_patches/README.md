# oraswgi_manage_patches

Install/Remove Patches from Oracle Database Homes

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [opatch_gi_conflict_check](#opatch_gi_conflict_check)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### opatch_gi_conflict_check

When calling oracle_opatch for GI, decide if analyze stage of
opatch/opatchauto should be executed.

**_Type:_** boolean<br />

#### Default value

```YAML
opatch_gi_conflict_check: '{{ opatch_conflict_check | bool }}'
```

## Discovered Tags

**_always_**

**_assert_**

**_current_opatch_version_**

## Dependencies

- orahost_meta
- orasw_meta
- oraswgi_meta

## License

license (MIT)

## Author

- Mikael Sandström

- Thorsten Bruhns
