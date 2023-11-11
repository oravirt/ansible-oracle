# orahost_storage

Role to configure the storage for oracle.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [asmlib_binary](#asmlib_binary)
  - [multipath](#multipath)
  - [oradnfs](#oradnfs)
  - [partition_devices](#partition_devices)
  - [partition_suffix](#partition_suffix)
  - [use_partition_devices](#use_partition_devices)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### asmlib_binary

#### Default value

```YAML
asmlib_binary: /usr/sbin/oracleasm
```

### multipath

Configure multipath

#### Default value

```YAML
multipath: none
```

#### Example usage

```YAML
multipath: dm-multipath
```

### oradnfs

Defines the settings for dnfstab in Oracle.

#### Default value

```YAML
oradnfs: _unset_
```

#### Example usage

```YAML
oradnfs:
 - server: nfsserver
   ips:
     - local: dbserver
       path: nfsserver
   exports:
     - export: /nfs/oradata
       mount: /u02/oradata2
     - export: /nfs/oradata2
       mount: /u02/oradata
```

### partition_devices

Create a partition on storage disk?

#### Default value

```YAML
partition_devices: true
```

### partition_suffix

Value of `partition_suffix` depends on vairable `multipath`.
No need to set this variable.

#### Default value

```YAML
partition_suffix: '1'
```

### use_partition_devices

Deprecated variable. Use `partition_devices` as replacement.

#### Default value

```YAML
use_partition_devices: '{{ partition_devices }}'
```

## Discovered Tags

**_asmlibconfig_**

**_asmstorage_**

**_kpartx_**

**_partition_**

**_udev_**

## Open Tasks

- (bug): why is variable multipath only used for dm-multipath?

## Dependencies

- orahost_meta

## License

license (MIT)

## Author

[Mikael Sandström]
