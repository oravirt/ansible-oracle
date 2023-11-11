# oraswdb_manage_patches

Manage Patch Installation in Database ORACLE_HOMEs.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oraswdb_manage_patches_cleanup_staging](#oraswdb_manage_patches_cleanup_staging)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### oraswdb_manage_patches_cleanup_staging

Remove following list of directories after DB-Patching when `oracle_sw_copy: true`:

- "{{ oracle_stage }}/patches"

#### Default value

```YAML
oraswdb_manage_patches_cleanup_staging: true
```

## Discovered Tags

**_always_**

**_apply_patch_db_**

**_autopatch_**

**_current_opatch_version_**

**_directories_**

**_molecule-idempotence-notest_**

**_nfsmountdb_**

**_nfsumountdb_**

**_ocmconfig_**

**_oragridopatchget_**

**_oragridpatchpush_**

**_oragridpatchunpack_**

**_oraswdbpsuunpack1_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
