# oradb-tzupgrade

This role can be used to apply the latest timezone upgrade for the
selected Oracle databases. This means that the Oracle home must be
first patched with a higher version of the timezone file. You may use
[oraswdb_manage_patches](/roles/oraswdb_manage_patches) role to
automate the timezone patching of the oracle home. Please note that as
part of the timezone upgrade the database is restarted, so you have to
consider this if high availability is important. Nevertheless, if the
database is already upgraded with the latest timezone file available
in the Oracle home then the upgrade is skipped and no instance restart
is initiated.

## Role Variables

You may customize this role by setting the following variables:

* `oracle_user`: oracle  
The OS user to be used when connecting to the Oracle instance and do the
timezone upgrade.

## Playbook Examples

The following playbook patches the Oracle home with version 39 of the
timezone file and then applies the corresponding upgrade into the
database:

```
- name: Upgrade Oracle timezone
  hosts: all
  become: true
  vars:
    apply_patches_db: true
    oracle_sw_unpack: true
    oracle_sw_patches:
      - filename: p34533061_190000_Linux-x86-64.zip
        patchid: 34533061
        version: 19.3.0.0
        description: DB Timezone V39
        creates: 34533061/README.html
    tz_latest_patch:
      19c:
        opatch:
          - patchid: 34533061
            state: present
            stop_processes: false
  collections:
    - opitzconsulting.ansible_oracle
  tasks:
    - set_fact:
      db_homes_config: "{{ db_homes_config | combine(tz_latest_patch, recursive=true) }}"

    - ansible.builtin.include_role:
        name: "oraswdb_manage_patches"

    - ansible.builtin.include_role:
      name: "oradb_tzupgrade"
```



