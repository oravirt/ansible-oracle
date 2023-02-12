# oraswgi_opatch

Install patches with opatch in Grid-Infrastructure/Restart.

## Table of content

- [Default Variables](#default-variables)
  - [grid_install_user](#grid_install_user)
  - [oracle_hostname](#oracle_hostname)
  - [oracle_inventory_loc](#oracle_inventory_loc)
  - [oracle_psu_apply_gi](#oracle_psu_apply_gi)
  - [oracle_psu_stage](#oracle_psu_stage)
  - [oracle_rsp_stage](#oracle_rsp_stage)
  - [oracle_sw_source_local](#oracle_sw_source_local)
  - [oracle_sw_source_www](#oracle_sw_source_www)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### grid_install_user

#### Default value

```YAML
grid_install_user: '{% if role_separation %}{{ grid_user }}{% else %}{{ oracle_user
  }}{% endif %}'
```

### oracle_hostname

#### Default value

```YAML
oracle_hostname: '{{ ansible_fqdn }}'
```

### oracle_inventory_loc

#### Default value

```YAML
oracle_inventory_loc: /u01/app/oraInventory
```

### oracle_psu_apply_gi

#### Default value

```YAML
oracle_psu_apply_gi: true
```

### oracle_psu_stage

#### Default value

```YAML
oracle_psu_stage: '{{ oracle_stage }}/psu'
```

### oracle_rsp_stage

#### Default value

```YAML
oracle_rsp_stage: '{{ oracle_stage }}/rsp'
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

## Discovered Tags

**_apply_psu_grid_**

**_check_applied_gi_patches_**

**_crsctl_**

**_crsctl-opatch_**

**_directoriespsu_**

**_opatchls_**

**_oragridnewopatch_**

**_oragridpatchunpack_**

**_oragridpsuunpack_**

**_psuapplym_**

**_psuapplyo_**


## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

Mikael Sandström, Thorsten Bruhns
