# oraswgi_golden_image

Create Golden-Images from Oracle Grid-Infrastructure/Restart

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [golden_image_dest](#golden_image_dest)
  - [oraswgi_golden_image_filename](#oraswgi_golden_image_filename)
  - [oraswgi_golen_image_create](#oraswgi_golen_image_create)
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

### oraswgi_golden_image_filename

Filename of created Image archive.

#### Default value

```YAML
oraswgi_golden_image_filename: >-
  {% if oracle_install_option_gi == 'CRS_CONFIG' -%}
  gi_{% else %}restart_{% endif %}{{ oracle_install_version_gi | split('.') | first
  }}.zip
```

### oraswgi_golen_image_create

Crfeate Golden-Image for Grid-Infrastructure/Restart.

#### Default value

```YAML
oraswgi_golen_image_create: false
```

## Discovered Tags

**_always_**

**_golden_image_gi_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
