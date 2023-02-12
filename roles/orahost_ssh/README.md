# orahost_ssh

SSH Setup for Oracle Grid-Infrastructure installations.

This role needs a complete refactoring in the future!

## Table of content

- [Default Variables](#default-variables)
  - [grid_user](#grid_user)
  - [hostgroup](#hostgroup)
  - [oracle_group](#oracle_group)
  - [oracle_user](#oracle_user)
  - [oracle_users](#oracle_users)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### grid_user

#### Default value

```YAML
grid_user: grid
```

### hostgroup

#### Default value

```YAML
hostgroup: '{{ group_names[0] }}'
```

### oracle_group

#### Default value

```YAML
oracle_group: oinstall
```

### oracle_user

#### Default value

```YAML
oracle_user: oracle
```

### oracle_users

#### Default value

```YAML
oracle_users:
  - {username: oracle, primgroup: oinstall}
  - {username: grid, primgroup: oinstall}
```

## Discovered Tags

**_sshkeys_**

**_sshkeys,known_hosts_**


## Dependencies

- orahost_meta
- orasw_meta_internal

## License

license (MIT)

## Author

[Mikael Sandström]
