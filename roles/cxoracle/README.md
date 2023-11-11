# cxoracle

Install cx_Oracle with pip

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [cx_oracle3_source](#cx_oracle3_source)
  - [cx_oracle_source](#cx_oracle_source)
  - [cx_oracle_umask](#cx_oracle_umask)
  - [extra_args](#extra_args)
  - [http_proxy](#http_proxy)
  - [install_cx_oracle](#install_cx_oracle)
  - [use_proxy](#use_proxy)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### cx_oracle3_source

Source for `pip3 install cx_Oracle`.

### cx_oracle_source

#### Example usage

```YAML
cx_oracle_source: "file:///tmp/cx_Oracle-7.3.0-cp27-cp27mu-manylinux1_x86_64.whl"
```

### cx_oracle_umask

Define umask for pip installation of cx_Oracle

### extra_args

Define optional arguments for extra_args during pip installation.
The variable is used by `user_proxy` and `http_proxy`.

#### Default value

```YAML
extra_args: _unset_
```

### http_proxy

Define the http_proxy for cx_oracle installation

#### Example usage

```YAML
http_proxy: proxy.example:3128
```

### install_cx_oracle

Install cx_Oracle?

#### Default value

```YAML
install_cx_oracle: true
```

### use_proxy

Use a http_proxy for installation

#### Default value

```YAML
use_proxy: false
```

## Discovered Tags

**_cx_oracle_**


## Dependencies

None.

## License

license (MIT)

## Author

[Mikael Sandström]
