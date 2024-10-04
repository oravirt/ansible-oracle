# orahost_ssh

SSH Setup for Oracle Grid-Infrastructure installations.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [orahost_ssh_hostkeytypes](#orahost_ssh_hostkeytypes)
  - [orahost_ssh_key_size](#orahost_ssh_key_size)
  - [orahost_ssh_key_type](#orahost_ssh_key_type)
  - [orahost_ssh_keyname](#orahost_ssh_keyname)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### orahost_ssh_hostkeytypes

SSH host key types to collect/deploy among hosts
Please note, ed25519 and dsa are not supported on FIPS enabled systems and thus better skipped

#### Default value

```YAML
orahost_ssh_hostkeytypes:
  - rsa
  - ecdsa
```

### orahost_ssh_key_size

SSH key size of {{ orahost_ssh_key_type }}
Check "man ssh-keygen" for valid keysizes

#### Default value

```YAML
orahost_ssh_key_size: 0
```

#### Example usage

```YAML
orahost_ssh_key_size: 521
```

### orahost_ssh_key_type

SSH key type for oracle and grid users' SSH Keypairs
Please note, ed25519 and dsa are not supported on FIPS enabled systems. Used here for backward compatibility only.

#### Default value

```YAML
orahost_ssh_key_type: ed25519
```

#### Example usage

```YAML
orahost_ssh_key_type: ecdsa
```

### orahost_ssh_keyname

The name of used key during role execution.

Example for oracle:

/home/oracle/.ssh/{{ orahost_ssh_keyname }}

#### Default value

```YAML
orahost_ssh_keyname: id_{{ orahost_ssh_key_type }}
```



## Dependencies

- orahost_meta
- orasw_meta_internal

## License

license (MIT)

## Author

[Thorsten Bruhns]
