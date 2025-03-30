# common

sets up the host generic stuff

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [common_packages](#common_packages)
  - [common_packages_el6](#common_packages_el6)
  - [common_packages_el7](#common_packages_el7)
  - [common_packages_el8](#common_packages_el8)
  - [common_packages_el9](#common_packages_el9)
  - [common_packages_sles](#common_packages_sles)
  - [configure_epel_repo](#configure_epel_repo)
  - [configure_motd](#configure_motd)
  - [configure_ntp](#configure_ntp)
  - [configure_public_yum_repo](#configure_public_yum_repo)
  - [epel6_rpm](#epel6_rpm)
  - [epel7_rpm](#epel7_rpm)
  - [epel8_rpm](#epel8_rpm)
  - [epel9_rpm](#epel9_rpm)
  - [install_os_packages](#install_os_packages)
  - [motd_template](#motd_template)
  - [ntp_type](#ntp_type)
  - [ol6_repo_file](#ol6_repo_file)
  - [ol7_repo_file](#ol7_repo_file)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### common_packages

This is an internal variable only. Do not define it!

#### Default value

```YAML
common_packages: _unset_
```

### common_packages_el6

List of RPMs for RHEL6 or OL6

#### Default value

```YAML
common_packages_el6:
  - screen
  - facter
  - procps
  - module-init-tools
  - ethtool
  - lsof
  - bc
  - nc
  - bind-utils
  - nfs-utils
  - make
  - sysstat
  - unzip
  - openssh-clients
  - compat-libcap1
  - collectl
  - rlwrap
  - tigervnc-server
  - ntp
  - expect
  - git
  - lvm2
  - xfsprogs
  - btrfs-progs
  - tmux
  - python-devel
  - python-pip
  - libselinux-python
  - twm
  - autofs
  - parted
  - mlocate
  - ksh
  - psmisc
```

### common_packages_el7

List of RPMs for RHEL7 or OL7

#### Default value

```YAML
common_packages_el7:
  - screen
  - facter
  - procps
  - module-init-tools
  - ethtool
  - lsof
  - bc
  - nc
  - bind-utils
  - nfs-utils
  - make
  - sysstat
  - unzip
  - openssh-clients
  - compat-libcap1
  - collectl
  - rlwrap
  - tigervnc-server
  - ntp
  - expect
  - git
  - lvm2
  - xfsprogs
  - btrfs-progs
  - python-devel
  - python-pip
  - libselinux-python
  - autofs
  - parted
  - mlocate
  - ksh
  - psmisc
  - grubby
```

### common_packages_el8

List of RPMs for RHEL8 or OL8

#### Default value

```YAML
common_packages_el8:
  - facter
  - procps
  - module-init-tools
  - ethtool
  - lsof
  - bc
  - binutils
  - elfutils-libelf
  - elfutils-libelf-devel
  - fontconfig-devel
  - glibc
  - glibc-devel
  - ksh
  - libaio
  - libaio-devel
  - libXrender
  - libX11
  - libXau
  - libXi
  - libXtst
  - libgcc
  - libnsl
  - librdmacm
  - libstdc++
  - libstdc++-devel
  - libxcb
  - libibverbs
  - make
  - smartmontools
  - sysstat
  - nc
  - bind-utils
  - nfs-utils
  - unzip
  - openssh-clients
  - rlwrap
  - tigervnc-server
  - expect
  - git
  - lvm2
  - xfsprogs
  - autofs
  - parted
  - mlocate
  - psmisc
  - python3
  - python3-pip
  - grubby
```

### common_packages_el9

#### Default value

```YAML
common_packages_el9:
  - facter
  - lsof
  - nc
  - rlwrap
  - expect
  - git
  - lvm2
  - xfsprogs
  - autofs
  - parted
  - mlocate
  - python3
  - python3-pip
  - bind-utils
  - binutils
  - ethtool
  - glibc
  - glibc-devel
  - initscripts
  - ksh
  - libaio
  - libaio-devel
  - libgcc
  - libnsl
  - libstdc++
  - libstdc++-devel
  - make
  - module-init-tools
  - net-tools
  - nfs-utils
  - openssh-clients
  - pam
  - policycoreutils
  - policycoreutils-python-utils
  - procps
  - psmisc
  - smartmontools
  - sysstat
  - tar
  - unzip
  - util-linux-ng
  - xorg-x11-utils
  - xorg-x11-xauth
  - grubby
```

### common_packages_sles

List of RPMs for SuSE Linux Enterprise Server

#### Default value

```YAML
common_packages_sles:
  - screen
  - procps
  - module-init-tools
  - ethtool
  - bc
  - bind-utils
  - make
  - sysstat
  - unzip
  - chrony
  - expect
  - lvm2
  - autofs
```

### configure_epel_repo

#### Default value

```YAML
configure_epel_repo: true
```

### configure_motd

Configure Message of the day

#### Default value

```YAML
configure_motd: true
```

### configure_ntp

Configure ntpd or chrony on target system.
The chrony or ntp is automatically chosen by `ntp_type`.

#### Default value

```YAML
configure_ntp: true
```

### configure_public_yum_repo

#### Default value

```YAML
configure_public_yum_repo: true
```

### epel6_rpm

Url for epel-release-latest-6.noarch.rpm

#### Default value

```YAML
epel6_rpm: https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
```

### epel7_rpm

Url for epel-release-latest-7.noarch.rpm

#### Default value

```YAML
epel7_rpm: 
  https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm
```

### epel8_rpm

Url for epel-release-latest-8.noarch.rpm

#### Default value

```YAML
epel8_rpm: https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
```

### epel9_rpm

Url for epel-release-latest-8.noarch.rpm

#### Default value

```YAML
epel9_rpm: oracle-epel-release-el9
```

### install_os_packages

#### Default value

```YAML
install_os_packages: true
```

### motd_template

Used templatename for Message of the day

#### Default value

```YAML
motd_template: motd.j2
```

### ntp_type

This is an internal variable only. Do not define it!

#### Default value

```YAML
ntp_type: _unset_
```

### ol6_repo_file

The variable is used to cleanup the yum repolist for old installations.

#### Default value

```YAML
ol6_repo_file: public-yum-ol6.repo
```

### ol7_repo_file

The variable is used to cleanup the yum repolist for old installations.

#### Default value

```YAML
ol7_repo_file: public-yum-ol7.repo
```

## Discovered Tags

**_common_assert_**

**_commonpackages_**

**_epelrepo_**

**_motd_**

**_olrepo_**


## Dependencies

- global_handlers

## License

license (MIT)

## Author

[Mikael Sandström]
