# orahost_logrotate

Configure logrotate for ansible-oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [logrotate_config](#logrotate_config)
  - [oracle_cleanup_days](#oracle_cleanup_days)
  - [oracle_home_gi](#oracle_home_gi)
  - [oracle_home_gi_cl](#oracle_home_gi_cl)
  - [oracle_home_gi_so](#oracle_home_gi_so)
  - [oracle_trace_cleanup_days](#oracle_trace_cleanup_days)
- [Discovered Tags](#discovered-tags)
- [Open Tasks](#open-tasks)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### logrotate_config

Configuration of logrotate definitions.

#### Default value

```YAML
logrotate_config:
  - name: oracle_alert
    file: '{{ oracle_base }}/diag/rdbms/*/*/trace/*alert*.log {{ oracle_base }}/diag/asm/*/*/trace/alert*+ASM*.log'
    options:
      - missingok
      - notifempty
      - weekly
      - rotate 3
      - dateext
  - name: oracle_listener
    file: '{{ oracle_base }}/diag/tnslsnr/*/*/trace/*listener*.log'
    options:
      - missingok
      - notifempty
      - weekly
      - rotate 3
      - dateext
      - compress
  - name: oracle_rman
    file: "{{ rman_cron_logdir | default('/var/log/oracle/rman/log') }}/*.log {{ oracle_base\
      \ }}/admin/*/rman/*.log {{ oracle_base }}/admin/*/rman/log/*.log"
    options:
      - missingok
      - notifempty
      - compress
      - weekly
      - rotate 24
      - dateext
```

### oracle_cleanup_days

Define number of days for oracle_cleanup.sh logfiles and audit files.

#### Default value

```YAML
oracle_cleanup_days: 14
```

### oracle_home_gi

#### Default value

```YAML
oracle_home_gi: '{% if _oraswgi_meta_configure_cluster %}{{ oracle_home_gi_cl }}{%
  else %}{{ oracle_home_gi_so }}{% endif %}'
```

### oracle_home_gi_cl

#### Default value

```YAML
oracle_home_gi_cl: /u01/app/{{ oracle_install_version_gi }}/grid
```

### oracle_home_gi_so

#### Default value

```YAML
oracle_home_gi_so: '{{ oracle_base }}/{{ oracle_install_version_gi }}/grid'
```

### oracle_trace_cleanup_days

Define number of days for ADR in Oracle.

#### Default value

```YAML
oracle_trace_cleanup_days: 7
```

## Discovered Tags

**_cleanup_**

**_logrotate_**

## Open Tasks

- (bug): oracle_home_gi variables require a central meta role

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
