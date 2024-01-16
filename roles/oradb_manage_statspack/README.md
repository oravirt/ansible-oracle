# oradb_manage_statspack

Manage Statspack in Oracle.

Not RAC aware at the moment.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [purgedays](#purgedays)
  - [purgeinterval](#purgeinterval)
  - [snapinterval](#snapinterval)
  - [snaplevel](#snaplevel)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### purgedays

Global default variable for Statspack purgetime in days.
Could be defined for each database with `oracle_databases`.
An example is shown there.

#### Default value

```YAML
purgedays: 35
```

### purgeinterval

Global default variable for Statspack purge interval in scheduler job.
Could be defined for each database with `oracle_databases`.
An example is shown there.

#### Default value

```YAML
purgeinterval: FREQ=daily;byhour=3;byminute=15;bysecond=0
```

### snapinterval

Global default variable for Statspack snap interval in scheduler job.
Could be defined for each database with `oracle_databases`.
An example is shown there.

#### Default value

```YAML
snapinterval: FREQ=hourly;byminute=0;bysecond=0
```

### snaplevel

Global default variable for Statspack snaplevel.
Could be defined for each database with `oracle_databases`.
An example is shown there.

#### Default value

```YAML
snaplevel: 7
```

## Discovered Tags

**_spcreate_**\
&emsp;Install Statspack in nonCDB, CDB or PDB

**_spdrop_**\
&emsp;Remove Statspack from nonCDB, CDB or PDB

**_spjob_**\
&emsp;Configure Statspack Scheduler Jobs

**_statspack_**\
&emsp;Do all Tasks for Statspack


## Dependencies

- orasw_meta
- oradb_facts

## License

license (MIT)

## Author

[Thorsten Bruhns]
