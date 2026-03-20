# oraswdb_manage_patches

Manage Patch Installation in Database ORACLE_HOMEs.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [opatch_db_conflict_check](#opatch_db_conflict_check)
  - [oraswdb_manage_patches_cleanup_staging](#oraswdb_manage_patches_cleanup_staging)
  - [oraswdb_manage_patches_force_opatch_upgrade](#oraswdb_manage_patches_force_opatch_upgrade)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### opatch_db_conflict_check

When calling oracle_opatch for DB, decide if analyze stage of
opatch/opatchauto should be executed.

**_Type:_** boolean<br />

#### Default value

```YAML
opatch_db_conflict_check: '{{ opatch_conflict_check | bool }}'
```

### oraswdb_manage_patches_cleanup_staging

Remove following list of directories after DB-Patching when `oracle_sw_copy: true`:

- "{{ oracle_stage }}/patches"

#### Default value

```YAML
oraswdb_manage_patches_cleanup_staging: true
```

### oraswdb_manage_patches_force_opatch_upgrade

Upgrade OPatch without checking for existing version.

Needed for prepatch installations, because Home is not
registered in central inventory.

#### Default value

```YAML
oraswdb_manage_patches_force_opatch_upgrade: false
```

## Discovered Tags

**_always_**

**_apply_patch_db_**

**_autopatch_**

**_directories_**

**_molecule-idempotence-notest_**

**_nfsmountdb_**

**_nfsumountdb_**

**_ocmconfig_**

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
