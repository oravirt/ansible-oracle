# oradb_manage_profiles

Manage database profiles in Oracle

## Table of content

- [Default Variables](#default-variables)
  - [attr_name](#attr_name)
  - [attr_value](#attr_value)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### attr_name

#### Default value

```YAML
attr_name: "{% if opdb.1.attributes is defined %}{{ opdb.1.attributes | default (omit)\
  \ | map(attribute='name') | list }} {%- else %}None {%- endif %}"
```

### attr_value

#### Default value

```YAML
attr_value: "{% if opdb.1.attributes is defined -%}{{ opdb.1.attributes | default\
  \ (omit) | map(attribute='value') | list }} {%- else %}None{% endif %}"
```

## Discovered Tags

**_dbprofiles_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

- Mikael Sandström

- Thorsten Bruhns
