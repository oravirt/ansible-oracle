# oraswgi_manage_patches

Install/Remove Patches from Oracle Database Homes

## Table of content

- [Default Variables](#default-variables)
  - [apply_patches_gi](#apply_patches_gi)
  - [cluster_master](#cluster_master)
  - [gi_patches](#gi_patches)
  - [ocm_response_file](#ocm_response_file)
  - [oracle_hostname](#oracle_hostname)
  - [oracle_patch_install](#oracle_patch_install)
  - [oracle_sw_source_local](#oracle_sw_source_local)
  - [oracle_sw_source_www](#oracle_sw_source_www)
  - [patch_before_rootsh](#patch_before_rootsh)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### apply_patches_gi

#### Default value

```YAML
apply_patches_gi: false
```

### cluster_master

#### Default value

```YAML
cluster_master: '{{ play_hosts[0] }}'
```

### gi_patches

#### Default value

```YAML
gi_patches: {}
```

### ocm_response_file

Was needed when `opatch` requirired `ocm.rsp` in old days.

#### Default value

```YAML
ocm_response_file: '{{ oracle_patch_stage }}/{{ oracle_install_version_gi }}/ocm.rsp'
```

### oracle_hostname

#### Default value

```YAML
oracle_hostname: '{{ ansible_fqdn }}'
```

### oracle_patch_install

#### Default value

```YAML
oracle_patch_install: '{% if not oracle_sw_copy and not oracle_sw_unpack %}{{ oracle_patch_stage_remote
  }}{% else %}{{ oracle_patch_stage }}{% endif %}'
```

### oracle_sw_source_local

#### Default value

```YAML
oracle_sw_source_local: /tmp
```

### oracle_sw_source_www

#### Default value

```YAML
oracle_sw_source_www: http://www/orasw
```

### patch_before_rootsh

#### Default value

```YAML
patch_before_rootsh: true
```

## Discovered Tags

**_apply_psu_grid_**

**_current_opatch_version_**

**_directories_**

**_ocmconfig_**

**_oragridopatchget_**

**_oragridpatchget_**

**_oragridpatchpush_**

**_oragridpatchunpack_**

**_oragridpsuunpack1_**

**_oragridpsuunpack2_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

Mikael Sandström
