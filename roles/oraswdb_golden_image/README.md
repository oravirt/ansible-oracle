# oraswdb_golden_image

Create Golden-Images from Oracle Database Homes and Oracle Grid-Infrastructure/Restart

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [golden_image_dest](#golden_image_dest)
  - [oraswdb_golden_image_create](#oraswdb_golden_image_create)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### golden_image_dest

Set destination directory for Golden-Image extraction.

Variable has no default value.

### oraswdb_golden_image_create

Crfeate Golden-Image for Database Home.

#### Default value

```YAML
oraswdb_golden_image_create: false
```

## Discovered Tags

**_always_**

**_golden_image_db_**

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
