# orahost_ssh

SSH Setup for Oracle Grid-Infrastructure installations.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [orahost_ssh_keyname](#orahost_ssh_keyname)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### orahost_ssh_keyname

The name of used key during role execution.

Example for oracle:

/home/oracle/.ssh/{{ orahost_ssh_keyname }}

#### Default value

```YAML
orahost_ssh_keyname: id_ed25519
```



## Dependencies

- orahost_meta
- orasw_meta_internal

## License

license (MIT)

## Author

[Thorsten Bruhns]
