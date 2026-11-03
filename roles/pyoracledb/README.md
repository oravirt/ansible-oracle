# pyoracledb

Install python-oracledb with pip.

python-oracledb is the successor of cx_Oracle and is used by the modules of ansible-oracle.
The role replaces the removed role `cxoracle`.

This role has a dependency to `orasw_meta`.

## Table of contents

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [pyoracledb_extra_args](#pyoracledb_extra_args)
  - [pyoracledb_http_proxy](#pyoracledb_http_proxy)
  - [pyoracledb_install](#pyoracledb_install)
  - [pyoracledb_source](#pyoracledb_source)
  - [pyoracledb_umask](#pyoracledb_umask)
  - [pyoracledb_use_proxy](#pyoracledb_use_proxy)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.16.0`

## Default Variables

### pyoracledb_extra_args

Define optional arguments for extra_args during pip installation.
The variable is used by `pyoracledb_use_proxy` and `pyoracledb_http_proxy` and
supports client certificates known from orasw_meta.

#### Default value

```YAML
pyoracledb_extra_args: ''
```

### pyoracledb_http_proxy

Define the http_proxy for the pip installation.

Needed when `pyoracledb_use_proxy: true`.

#### Example usage

```YAML
pyoracledb_http_proxy: proxy.example:3128
```

### pyoracledb_install

Install python-oracledb?

#### Default value

```YAML
pyoracledb_install: true
```

### pyoracledb_source

Source for `pip3 install`. Default is the package `oracledb` from the package index.

Supported values:

- package name with optional version specifier, e.g. `oracledb==3.4.0`
- local file on the Ansible controller (`/path` or `file:///path`),
copied to the managed node when `is_sw_source_local: true` and `oracle_sw_copy: true`.
With `oracle_sw_copy: false` the path must exist on the managed node.
- URL (`http://`, `https://`, `ftp://`), downloaded on the managed node
when `is_sw_source_local: false` and `oracle_sw_copy: true`

#### Default value

```YAML
pyoracledb_source: oracledb
```

#### Example usage

```YAML
pyoracledb_source: "oracledb==3.4.0"
```

### pyoracledb_umask

Define umask for pip installation of python-oracledb

### pyoracledb_use_proxy

Use a http_proxy for the pip installation

#### Default value

```YAML
pyoracledb_use_proxy: false
```

## Discovered Tags

**_pyoracledb_**

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
