# orasw_download_patches

Download all patches from Oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [mos_login](#mos_login)
  - [mos_password](#mos_password)
  - [opatchinfo](#opatchinfo)
  - [oracle_patch_download_dir](#oracle_patch_download_dir)
  - [oracle_patch_download_host](#oracle_patch_download_host)
  - [oracle_plat_lang](#oracle_plat_lang)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### mos_login

Login name for My Oracle Support (required)

### mos_password

Password for My Oracle Support (required)

### opatchinfo

This is an internal variable for downloading patches.
Usually no need to change it.

#### Default value

```YAML
opatchinfo: []
```

### oracle_patch_download_dir

Target directory for patch downloads

#### Default value

```YAML
oracle_patch_download_dir: '{{ oracle_sw_source_local }}'
```

### oracle_patch_download_host

`delegate_to` host for downloads

#### Default value

```YAML
oracle_patch_download_host: localhost
```

### oracle_plat_lang

This is an internal variable for downloading patches.
Usually no need to change it.

#### Default value

```YAML
oracle_plat_lang: 226P
```

## Dependencies

- orasw_meta

## License

license (MIT)

## Author

bartowl <github@bartowl.eu>
