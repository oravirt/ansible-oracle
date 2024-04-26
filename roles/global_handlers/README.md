# global_handlers

sets up the host generic stuff

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [reboot_on_requirement](#reboot_on_requirement)
  - [restart_on_requirement](#restart_on_requirement)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

## Default Variables

### reboot_on_requirement

Controls if reboot handler actually reboots the host (true)
or just displays a reboot advice (false)

### restart_on_requirement

#### Default value

```YAML
restart_on_requirement: true
```



## Dependencies

None.

## License

license (MIT)

## Author

[Mikael Sandström]
