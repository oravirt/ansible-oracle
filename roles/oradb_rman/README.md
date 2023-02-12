# oradb_rman

Oracle RMAN Backup for ansible-oracle

## Table of content

- [Default Variables](#default-variables)
  - [check_mk_mkjob](#check_mk_mkjob)
  - [rman_catalog_param](#rman_catalog_param)
  - [rman_channel_disk](#rman_channel_disk)
  - [rman_channel_disk_default](#rman_channel_disk_default)
  - [rman_controlfile_autobackup_disk](#rman_controlfile_autobackup_disk)
  - [rman_controlfile_autobackup_disk_default](#rman_controlfile_autobackup_disk_default)
  - [rman_cron_logdir](#rman_cron_logdir)
  - [rman_cron_mkjob](#rman_cron_mkjob)
  - [rman_cronfile](#rman_cronfile)
  - [rman_device_type_disk_default](#rman_device_type_disk_default)
  - [rman_log_dir](#rman_log_dir)
  - [rman_retention_policy](#rman_retention_policy)
  - [rman_retention_policy_default](#rman_retention_policy_default)
  - [rman_script_dir](#rman_script_dir)
  - [rman_service_param](#rman_service_param)
  - [rman_tns_admin](#rman_tns_admin)
  - [rman_wallet_loc](#rman_wallet_loc)
  - [rman_wallet_password](#rman_wallet_password)
  - [rmanautofs](#rmanautofs)
  - [rmanbackuplogdir](#rmanbackuplogdir)
  - [rmanbackupscriptdir](#rmanbackupscriptdir)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Default Variables

### check_mk_mkjob

#### Default value

```YAML
check_mk_mkjob: '{% if rman_cron_mkjob %}/usr/bin/mk-job rman_{{ item.0.oracle_db_name
  }}_{{ item.1.name }} {% endif %}'
```

### rman_catalog_param

#### Default value

```YAML
rman_catalog_param: '{% if item.0.rman_wallet is defined and item.0.rman_wallet %}-c
  /@{{ item.0.rman_tnsalias }} {%- else %} {%- if item.0.rman_user is defined %}-c
  {{ item.0.rman_user }}/{{ dbpasswords[item.0.rman_tnsalias][item.0.rman_user] |
  default(item.0.rman_password) }}@{{ item.0.rman_tnsalias }} {%- endif %} {%- endif
  %}'
```

### rman_channel_disk

#### Default value

```YAML
rman_channel_disk: '{{ item.0.rman_channel_disk | default(rman_channel_disk_default)
  }}'
```

### rman_channel_disk_default

#### Default value

```YAML
rman_channel_disk_default: "'/u10/rmanbackup/%d/%d_%T_%U'"
```

### rman_controlfile_autobackup_disk

#### Default value

```YAML
rman_controlfile_autobackup_disk: '{{ item.0.rman_controlfile_autobackup_disk | default(rman_controlfile_autobackup_disk_default)
  }}'
```

### rman_controlfile_autobackup_disk_default

#### Default value

```YAML
rman_controlfile_autobackup_disk_default: "'/u10/rmanbackup/%d/%d_%F'"
```

### rman_cron_logdir

#### Default value

```YAML
rman_cron_logdir: /var/log/oracle/rman/log
```

### rman_cron_mkjob

#### Default value

```YAML
rman_cron_mkjob: false
```

### rman_cronfile

#### Default value

```YAML
rman_cronfile: oracle_rman_ansible
```

### rman_device_type_disk_default

#### Default value

```YAML
rman_device_type_disk_default: PARALLELISM 1 BACKUP TYPE TO COMPRESSED BACKUPSET
```

### rman_log_dir

#### Default value

```YAML
rman_log_dir: '{% if item is defined and item.0.rman_log_dir is defined %}{{ item.0.rman_log_dir
  }}{% else %}{{ oracle_base }}/rman/log/{% endif %}'
```

### rman_retention_policy

#### Default value

```YAML
rman_retention_policy: '{{ item.0.rman_retention_policy | default(rman_retention_policy_default)
  }}'
```

### rman_retention_policy_default

#### Default value

```YAML
rman_retention_policy_default: RECOVERY WINDOW OF 14 DAYS
```

### rman_script_dir

#### Default value

```YAML
rman_script_dir: '{% if item is defined and item.0.rman_script_dir is defined %}{{
  item.0.rman_script_dir }}{% else %}{{ oracle_base }}/rman/{% endif %}'
```

### rman_service_param

#### Default value

```YAML
rman_service_param: '{% if item.1.service is defined %}--service {{ item.1.service
  }}{% else %}{% endif %}'
```

### rman_tns_admin

#### Default value

```YAML
rman_tns_admin: '{{ oracle_base }}/rman/network/admin'
```

### rman_wallet_loc

#### Default value

```YAML
rman_wallet_loc: '{{ oracle_base }}/rman/network/wallet'
```

### rman_wallet_password

#### Default value

```YAML
rman_wallet_password: oracleWallet1
```

### rmanautofs

#### Default value

```YAML
rmanautofs: false
```

### rmanbackuplogdir

#### Default value

```YAML
rmanbackuplogdir: '{% if item.0.rman_log_dir is defined %}-l {{ item.0.rman_log_dir
  }}{% else %}{% endif %}'
```

### rmanbackupscriptdir

#### Default value

```YAML
rmanbackupscriptdir: '{% if item.0.rman_script_dir is defined %}-r {{ item.0.rman_script_dir
  }}{% else %}{% endif %}'
```

## Discovered Tags

**_assert_**

**_autofs_**

**_rmancopy_**

**_rmancron_**

**_rmanexecute_**

**_tns_**

**_wallet_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
