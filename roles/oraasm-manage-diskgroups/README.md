oraasm-manage-diskgroups
=========

- Manages ASM diskgroups.

- Uses oracle_asmdg module from [ansible-oracle-modules](https://github.com/oravirt/ansible-oracle-modules)

Role Variables
--------------
`asm_diskgroups` - defines the various disksgroups and their attributes.

e.g

```
asm_diskgroups:
  - diskgroup: crs
    state: present
    properties:
      - {redundancy: external, ausize: 4}
    attributes:
      - {name: compatible.asm, value: 12.2.0.1.0}
      - {name: compatible.rdbms, value: 11.2.0.4.0}
    disk:
      - {device: /dev/sdc, asmlabel: crs01}
  - diskgroup: data
    state: present
    properties:
      - {redundancy: external, ausize: 4}
    attributes:
      - {name: compatible.asm, value: 12.2.0.1}
      - {name: compatible.rdbms, value: 11.2.0.4.0}
    disk:
      - {device: /dev/sdd, asmlabel: data01}
      - {device: /dev/sde, asmlabel: data02}
```


Example Playbook
----------------
```
    - hosts: vbox-rac-dc1
      become: True
      become_user:
      roles:
         - { role: oraasm-manage-diskgroups }
```

Author Information
------------------
Mikael Sandström, @oravirt, oravirt@gmail.com
