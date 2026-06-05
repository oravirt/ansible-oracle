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
  - [install_from_nfs](#install_from_nfs)
  - [is_sw_source_local](#is_sw_source_local)
  - [oracle_stage](#oracle_stage)
  - [oracle_sw_copy](#oracle_sw_copy)
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
The variable is used by `use_proxy` and `http_proxy` and
supports client certificates known from orasw_meta.

#### Default value

```YAML
extra_args: ''
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

### install_from_nfs

Mount NFS-Server for installation media?

`nfs_server_sw` and `nfs_server_sw_path` are needed, when `install_from_nfs: true`

#### Default value

```YAML
install_from_nfs: false
```

### is_sw_source_local

#### Default value

```YAML
is_sw_source_local: true
```

### oracle_stage

Defines the base directory for response files, configuration firles etc. for `ansible-oracle`.

There is usually no need to change this variable.

#### Default value

```YAML
oracle_stage: /u01/stage
```

### oracle_sw_copy

#### Default value

```YAML
oracle_sw_copy: '{% if install_from_nfs %}false{% else %}true{% endif %}'
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
