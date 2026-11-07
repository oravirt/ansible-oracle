# oradb_standby

Creates standby databases for the standby configurations in `db_standby_config`.

The method for the creation is selected with `create_method` in `db_standby_config`:

- `rman_duplicate_active`: RMAN `DUPLICATE ... FOR STANDBY FROM ACTIVE DATABASE` (default)
- `external`: the standby database is created outside of `ansible-oracle`
- `custom`: tasks file from `create_tasks_file`

The inventory structure is described in `doc/guides/standby_databases.adoc`.

## Table of contents

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oradb_standby_broker_create](#oradb_standby_broker_create)
  - [oradb_standby_rman_compressed](#oradb_standby_rman_compressed)
  - [oradb_standby_rman_logdir](#oradb_standby_rman_logdir)
  - [oradb_standby_rman_parallel](#oradb_standby_rman_parallel)
  - [oradb_standby_start_apply](#oradb_standby_start_apply)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.16.0`

## Default Variables

### oradb_standby_broker_create

Create the Data Guard Broker configuration with `dgmgrl.cfg` on the host of the primary database,
when no broker configuration exists and all other members are physical standby databases.

`false`: `dgmgrl.cfg` is created on all members, but not executed.

#### Default value

```YAML
oradb_standby_broker_create: true
```

### oradb_standby_rman_compressed

Use `USING COMPRESSED BACKUPSET` for `DUPLICATE ... FROM ACTIVE DATABASE`.
`false` uses `USING BACKUPSET`.

#### Default value

```YAML
oradb_standby_rman_compressed: true
```

### oradb_standby_rman_logdir

Directory for the logfiles of RMAN `DUPLICATE`.

#### Default value

```YAML
oradb_standby_rman_logdir: '{{ oracle_base }}/cfgtoollogs/oradb_standby'
```

### oradb_standby_rman_parallel

Number of RMAN channels on the primary and on the standby database
for `create_method: rman_duplicate_active`.

#### Default value

```YAML
oradb_standby_rman_parallel: 2
```

### oradb_standby_start_apply

Start Redo Apply (`RECOVER MANAGED STANDBY DATABASE DISCONNECT`) after the creation
of the standby database.

#### Default value

```YAML
oradb_standby_start_apply: true
```

## Discovered Tags

**_oradb_standby_**

## Dependencies

- orasw_meta
- oradb_facts

## License

license (MIT)

## Author

- Thorsten Bruhns
