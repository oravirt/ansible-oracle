# oradb_manage_wallet

Manage Wallets for Oracle with `mkstore`.

Multiple wallets with different locations are possivle.
Define a password for the wallet in `oracle_wallet_password`.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oracle_wallet_config](#oracle_wallet_config)
  - [oracle_wallet_password](#oracle_wallet_password)
  - [oracle_wallet_show_password](#oracle_wallet_show_password)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.15.0`

## Default Variables

### oracle_wallet_config

#### Default value

```YAML
oracle_wallet_config: []
```

#### Example usage

```YAML
oracle_wallet_config:
  - name: wallet1
    home: 19300_base
    path: /u01/app/oracle/wallet
    state: present
    dbcredential:
      - tns_name: db1
        db_name: db1
        db_user: user1
        state: present
```

### oracle_wallet_password

#### Default value

```YAML
oracle_wallet_password: {}
```

#### Example usage

```YAML
oracle_wallet_password:
  wallet1: <password>
  wallet2: <password>
```

### oracle_wallet_show_password

Show password during execution in loop label.

#### Default value

```YAML
oracle_wallet_show_password: false
```

## Discovered Tags

**_always_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
