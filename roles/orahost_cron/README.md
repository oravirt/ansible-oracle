# orahost_cron

Configure cronjobs for ansible-oracle

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [cron_config](#cron_config)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`


## Default Variables

### cron_config

Define custom cronjobs for ansible-oracle.
No job is existing by default.

#### Example usage

```YAML
cron_config:
  - { user: oracle, name: "clean-up job", job: "some fancy thing", hour: "1", cron_file: oracle-cleanup, state: present }
```

## Discovered Tags

**_cron_**


## Dependencies

None.

## License

license (MIT)

## Author

[Mikael Sandström]
