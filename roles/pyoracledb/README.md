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
  - [pyoracledb_umask](#pyoracledb_umask)
  - [pyoracledb_use_proxy](#pyoracledb_use_proxy)
  - [pyoracledb_version](#pyoracledb_version)
  - [pyoracledb_version_py36](#pyoracledb_version_py36)
  - [pyoracledb_version_py37](#pyoracledb_version_py37)
  - [pyoracledb_version_py38](#pyoracledb_version_py38)
  - [pyoracledb_version_py39](#pyoracledb_version_py39)
  - [pyoracledb_wheel_dir](#pyoracledb_wheel_dir)
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
Set it for other pip options, e.g. `--index-url=https://pypi.example.com/simple` for an internal mirror.

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

### pyoracledb_umask

Define umask for pip installation of python-oracledb

### pyoracledb_use_proxy

Use a http_proxy for the pip installation

#### Default value

```YAML
pyoracledb_use_proxy: false
```

### pyoracledb_version

Version of python-oracledb for Python versions without an own variable `pyoracledb_version_py<major><minor>`.

The version is updated by renovate.
The version is selected with the Python version of the target host (`ansible_python_interpreter`).

#### Default value

```YAML
pyoracledb_version: 26.1.0
```

### pyoracledb_version_py36

Version of python-oracledb for Python 3.6 (Oracle Linux / RHEL 8, SLES 15).
Last release for Python 3.6, not updated by renovate.

#### Default value

```YAML
pyoracledb_version_py36: 1.4.2
```

### pyoracledb_version_py37

Version of python-oracledb for Python 3.7.
Last release for Python 3.7, not updated by renovate.

#### Default value

```YAML
pyoracledb_version_py37: 2.3.0
```

### pyoracledb_version_py38

Version of python-oracledb for Python 3.8.
Last release for Python 3.8, not updated by renovate.

#### Default value

```YAML
pyoracledb_version_py38: 3.0.0
```

### pyoracledb_version_py39

Version of python-oracledb for Python 3.9 (Oracle Linux / RHEL 9).
Last release for Python 3.9, not updated by renovate.

#### Default value

```YAML
pyoracledb_version_py39: 4.0.2
```

### pyoracledb_wheel_dir

Directory with wheel files of python-oracledb for an installation without the Python package index.

pip selects the wheel file matching the Python version of the target host
(`pip install --no-index --find-links <pyoracledb_wheel_dir> oracledb==<version>`),
so one directory can contain the wheel files for all Python versions (e.g. `cp36` and `cp39`).

- local directory on the Ansible controller, copied to `<oracle_stage>/pyoracledb` on the target host
when `is_sw_source_local: true` and `oracle_sw_copy: true`.
With `oracle_sw_copy: false` the directory must exist on the target host (e.g. NFS).
- URL (`http://`, `https://`) of a page with links to the wheel files, used directly by pip

The role ensures pip >= 19.3 (needed for manylinux2014 wheels, the system pip of OL8 is 9.0.3).
Add a pip wheel to the directory for target hosts with an older pip, e.g. `pip-21.3.1-py3-none-any.whl` for Python 3.6.

Download the wheel files on a host with access to the package index, e.g.:
`pip download --no-deps --only-binary=:all: --python-version 3.9 --platform manylinux2014_x86_64 -d <dir> oracledb==4.0.2`

#### Example usage

```YAML
pyoracledb_wheel_dir: /sw/python-oracledb
```

## Discovered Tags

**_pyoracledb_**

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
