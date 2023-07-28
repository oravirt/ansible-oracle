# oraswgi_meta


_Important_

The description for variables is work in progress.!

Meta role used by other roles to share variable defaults.

This role has a dependency to `orahost_meta`.

There are a lot of variables who are used by `orasw_meta`

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [_grid_install_user](#_grid_install_user)
  - [_oraswgi_meta_configure_cluster](#_oraswgi_meta_configure_cluster)
  - [apply_patches_gi](#apply_patches_gi)
  - [asmmonitorpassword](#asmmonitorpassword)
  - [gi_patches](#gi_patches)
  - [oracle_hostname](#oracle_hostname)
  - [patch_before_rootsh](#patch_before_rootsh)
  - [sysasmpassword](#sysasmpassword)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### _grid_install_user

This is an internal variable of `ansible-oracle`.

Do not change it!

#### Default value

```YAML
_grid_install_user: '{% if role_separation %}{{ grid_user }}{% else %}{{ oracle_user
  }}{% endif %}'
```

### _oraswgi_meta_configure_cluster

This is an internal variable of `ansible-oracle`.

Do not change it!

#### Default value

```YAML
_oraswgi_meta_configure_cluster: false
```

### apply_patches_gi

Apply patches to Grid-Infrastructure/Restart?

Do not disable this!

#### Default value

```YAML
apply_patches_gi: true
```

### asmmonitorpassword

#### Default value

```YAML
asmmonitorpassword: '{{ oracle_password }}'
```

### gi_patches

Dictionary of lists for opatch and opatchauto patches for
Grid-Infrastructure/Restart.

#### Default value

```YAML
gi_patches: {}
```

#### Example usage

```YAML
gi_patches_config:
  19.16.0.0.220719:
    19.3.0.0:  # Base Release
      opatch_minversion: 12.2.0.1.30
      opatchauto:
        - patchid: 34130714
          patchversion: 19.16.0.0.220719
          state: present
          path: ./19.16.0.0.220719/gi/34130714/34130714
          subpatches:
            - 34160635  # OCW Release Update 19.16.0.0.220719
            - 33575402  # DBWLM Release Update
            - 34139601  # ACFS Release Update 19.16.0.0.220719
            - 34318175  # TOMCAT RELEASE UPDATE 19.0.0.0.0
            - 34133642  # Database Release Update 19.16.0.0.220719
      opatch:
          # Oracle JavaVM Component Release Update (OJVM RU) 19.16.0.0.220719
          stop_processes: true
          state: present
          path: 19.16.0.0.220719/ojvm/p34086870_190000_Linux-x86-64.zip
          # Oracle Database 19c Important Recommended One-off Patches (Doc ID 555.1)
```

### oracle_hostname

Grid-Infrastructure nodename.

#### Default value

```YAML
oracle_hostname: '{{ ansible_fqdn }}'
```

### patch_before_rootsh

Patch Grid-Infrastructure during installation befor executing
root.sh

#### Default value

```YAML
patch_before_rootsh: true
```

### sysasmpassword

SYSASM Password for ASM.

#### Default value

```YAML
sysasmpassword: '{{ oracle_password }}'
```


## Open Tasks

- (bug): `ansible-oracle` does not support RAC at the moment.

## Dependencies

None.

## License

license (MIT)

## Author

[Thorsten Bruhns]
