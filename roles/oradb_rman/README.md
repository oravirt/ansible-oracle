# oradb_rman

Oracle RMAN Backup for ansible-oracle

Please use only `oradb_rman_` variables from role `oradb_rman`.

All other role variables from `oradb_rman` are deprecated and will be removed in a future release.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [oradb_rman_autofs](#oradb_rman_autofs)
  - [oradb_rman_channel_disk_default](#oradb_rman_channel_disk_default)
  - [oradb_rman_controlfile_autobackup_disk_default](#oradb_rman_controlfile_autobackup_disk_default)
  - [oradb_rman_cron_logdir](#oradb_rman_cron_logdir)
  - [oradb_rman_cron_mkjob](#oradb_rman_cron_mkjob)
  - [oradb_rman_cronfile](#oradb_rman_cronfile)
  - [oradb_rman_log_dir](#oradb_rman_log_dir)
  - [oradb_rman_retention_policy_default](#oradb_rman_retention_policy_default)
  - [oradb_rman_script_dir](#oradb_rman_script_dir)
  - [oradb_rman_tns_admin](#oradb_rman_tns_admin)
  - [oradb_rman_tnsnames_installed](#oradb_rman_tnsnames_installed)
  - [oradb_rman_wallet_loc](#oradb_rman_wallet_loc)
  - [oradb_rman_wallet_password](#oradb_rman_wallet_password)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.9.0`


## Default Variables

### oradb_rman_autofs

Configure autofs for RMAN Backups?

#### Default value

```YAML
oradb_rman_autofs: '{{ rmanautofs | default(false) }}'
```

### oradb_rman_channel_disk_default

Defines the format for disk target in RMAN-Templates from role.

#### Default value

```YAML
oradb_rman_channel_disk_default: >-
  {% set __channel_disk_default = "'/u10/rmanbackup/%d/%d_%T_%U'" -%}
  {{ rman_channel_disk_default | default(__channel_disk_default) -}}
```

### oradb_rman_controlfile_autobackup_disk_default

Defines the contolfile autobackup target directory for the RMAN-Templates from role.

#### Default value

```YAML
oradb_rman_controlfile_autobackup_disk_default: >-
  {% set __autobackup_disk_default = "'/u10/rmanbackup/%d/%d_%F'" -%}
  {{ rman_controlfile_autobackup_disk_default | default(__autobackup_disk_default)
  -}}
```

### oradb_rman_cron_logdir

Lgofiledirectory for output of cronjobs.

#### Default value

```YAML
oradb_rman_cron_logdir: "{{ rman_cron_logdir | default('/var/log/oracle/rman/log')\
  \ }}"
```

### oradb_rman_cron_mkjob

Add mk-job to all cronjobs in `/etc/cron.d` for RMAN backups.

This is only needed when RMAN backups are monitored by checkmk.

#### Default value

```YAML
oradb_rman_cron_mkjob: '{{ rman_cron_mkjob | default(false) }}'
```

### oradb_rman_cronfile

Name for file for crontab in /etc/cron.d

#### Default value

```YAML
oradb_rman_cronfile: oracle_rman_ansible
```

### oradb_rman_log_dir

Lgofiledirectory for `rman_wrapper.sh`.

#### Default value

```YAML
oradb_rman_log_dir: "{{ rman_log_dir | default(odb.0.rman_log_dir | default(oracle_base\
  \ + '/rman/log')) }}"
```

### oradb_rman_retention_policy_default

Defines the policy for the RMAN-Templates from role.

#### Default value

```YAML
oradb_rman_retention_policy_default: "{{ rman_retention_policy_default | default('RECOVERY\
  \ WINDOW OF 14 DAYS') }}"
```

### oradb_rman_script_dir

Directory for `*.rman`-Files.

#### Default value

```YAML
oradb_rman_script_dir: "{{ rman_script_dir | default(odb.0.rman_script_dir | default(oracle_base\
  \ + '/rman')) }}"
```

### oradb_rman_tns_admin

TNS_ADMIN for `rman_wrapper.sh`.
This is needed for RMAN-Catalogconnections.

#### Default value

```YAML
oradb_rman_tns_admin: "{{ rman_tns_admin | default(oracle_base + '/rman/network/admin')\
  \ }}"
```

### oradb_rman_tnsnames_installed

Defines custom entries in tnsnames.ora in `oradb_rman_tns_admin`.

Format is same as `tnsnames_installed`.

#### Example usage

```YAML
oradb_rman_tnsnames_installed:
  - home: db19-si-ee
    tnsname: orclpdb
    state: present
```

### oradb_rman_wallet_loc

Directory for Oracle wallet.

#### Default value

```YAML
oradb_rman_wallet_loc: "{{ rman_wallet_loc | default(oracle_base + '/rman/network/wallet')\
  \ }}"
```

### oradb_rman_wallet_password

Password for Orale wallet.

#### Default value

```YAML
oradb_rman_wallet_password: "{{ rman_wallet_password | default('oracleWallet1') }}"
```

## Discovered Tags

**_always_**

**_assert_**

**_assert_rman_tns_admin_**

**_autofs_**

**_notest_**

**_rmancopy_**

**_rmancron_**

**_rmanexecute_**

**_rmanregister_**

**_tns_**

**_tnsnames_**

**_wallet_**

**_wallet_contents_**


## Dependencies

- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
