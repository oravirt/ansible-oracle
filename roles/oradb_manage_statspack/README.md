# oradb_manage_statspack

Manage Statspack in Oracle

## Table of content

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

## Default Variables

### purgedays

#### Default value

```YAML
purgedays: 35
```

### purgeinterval

#### Default value

```YAML
purgeinterval: FREQ=daily;byhour=3;byminute=15;bysecond=0
```

### snapinterval

#### Default value

```YAML
snapinterval: FREQ=hourly;byminute=0;bysecond=0
```

### snaplevel

#### Default value

```YAML
snaplevel: 7
```

## Discovered Tags

**_spcdb_**

**_spcreate_**

**_spdrop_**

**_spjob_**

**_sppdb_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
