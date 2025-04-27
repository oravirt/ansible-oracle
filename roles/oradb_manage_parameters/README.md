# oradb_manage_parameters

Manage Oracle Database Parameters

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [restart_spparameter_changed](#restart_spparameter_changed)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### restart_spparameter_changed

Bounce instane when parameter changes detected between SPFile and memory parameter.

IMPORTANT Note!

Some memory parameters are rounded internally by Oracle.
Changing them in SPFile could lead to a bounce of the instance each time the role is executed.
Change the paramter to the rounded value from Oracle to prevent this.

#### Default value

```YAML
restart_spparameter_changed: false
```

## Discovered Tags

**_initparams_**\
&emsp;Configure parameter for nonCDB, CDB and PDB

**_initparams_cdb_**\
&emsp;Configure parameter for nonCDB and CDB

**_initparams_pdb_**\
&emsp;Configure parameter for PDB

**_spfile_bounce_**\
&emsp;Bounce database when changed parameter need a restart.

## Dependencies

- orasw_meta
- oradb_facts

## License

license (MIT)

## Author

[Mikael Sandström]
