orahost-ssh
=========

Manages passwordless ssh between modes. It will make sure the public keys generated for each user (oracle/grid) will be added to authorized_keys on other nodes.

It also makes sure known_hosts is generated. **NOTE: This part is not idempotent, so on every run the keys will be added again.**

This role will run in serial meaning it will run on 1 host at a time (as opposed to run in parallel which is the default)
Requirements
------------

The user must have ssh-keys already generated. This is taken care of by the orahost role

Example Playbook
----------------

```
    - hosts: vbox-rac-dc1
      become: True
      become_user: root
      serial: 1
      roles:
         - { role: orahost-ssh }
```

Author Information
------------------
Mikael Sandström, oravirt@gmail.com, @oravirt
