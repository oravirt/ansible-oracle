# global_handlers

Collection of handlers includeable by other roles.

Make them available to your role by including it into the
dependency list in meta/main.yml of your role, for instance.

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [restart_on_requirement](#restart_on_requirement)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### restart_on_requirement

Controls if reboot handler actually reboots the host (true)
or just displays a reboot advice (false)

**_Type:_** bool<br />

#### Default value

```YAML
restart_on_requirement: false




## Dependencies

None.

## License

license (MIT)

## Author

[Thilo Solbrig]
