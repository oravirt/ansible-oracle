# oraasm_manage_diskgroups

Manages ASM diskgroups.

_Important_

All variables in this role are internal use only. Do not set them in inventory!

## Table of content

- [Default Variables](#default-variables)
  - [asmdevice_list](#asmdevice_list)
  - [attr_name](#attr_name)
  - [attr_value](#attr_value)
  - [oracle_asm_disk_prefix](#oracle_asm_disk_prefix)
  - [oracle_env](#oracle_env)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### asmdevice_list

#### Default value

```YAML
asmdevice_list: internal use only
```

### attr_name

#### Default value

```YAML
attr_name: internal use only
```

### attr_value

#### Default value

```YAML
attr_value: internal use only
```

### oracle_asm_disk_prefix

#### Default value

```YAML
oracle_asm_disk_prefix: internal use only
```

### oracle_env

The variable is used for shell, command tasks to set environment Variables.

Do not set it in inventory!

#### Default value

```YAML
oracle_env:
  ORACLE_HOME: '{{ oracle_home_gi }}'
  LD_LIBRARY_PATH: '{{ oracle_home_gi }}/lib'
```

## Discovered Tags

**_diskgroup_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Mikael Sandström]
