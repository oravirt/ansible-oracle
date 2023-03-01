# orasw_download_patches

Download all patches from Oracle

## Table of content

- [Default Variables](#default-variables)
  - [http_proxy](#http_proxy)
  - [https_proxy](#https_proxy)
  - [mos_login](#mos_login)
  - [mos_password](#mos_password)
  - [no_proxy](#no_proxy)
  - [opatchinfo](#opatchinfo)
  - [oracle_patch_download_dir](#oracle_patch_download_dir)
  - [oracle_patch_download_host](#oracle_patch_download_host)
  - [oracle_plat_lang](#oracle_plat_lang)
  - [proxy_env](#proxy_env)
  - [use_proxy](#use_proxy)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### http_proxy

Define the http proxy for downloads

#### Default value

```YAML
http_proxy:
```

### https_proxy

Define the https proxy for downloads

#### Default value

```YAML
https_proxy:
```

### mos_login

Login name for My Oracle Support (required)

### mos_password

Password for My Oracle Support (required)

### no_proxy

Define no_proxy list für downlads.

#### Default value

```YAML
no_proxy:
```

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

### proxy_env

This is an internal variable for downloading patches.
Usually no need to change it.

#### Default value

```YAML
proxy_env:
  http_proxy: '{{ http_proxy }}'
  https_proxy: '{{ https_proxy }}'
  no_proxy: '{{ no_proxy }}'
```

### use_proxy

Enable Proxy for Download

#### Default value

```YAML
use_proxy: false
```



## Dependencies

- orasw_meta

## License

license (MIT)

## Author

bartowl <github@bartowl.eu>
