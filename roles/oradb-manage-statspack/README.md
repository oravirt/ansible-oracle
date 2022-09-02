Role Name
=========

A brief description of the role goes here.

Requirements
------------

Do not create the perfstat user before creating the statspack
inside the database. The detection of existing statspack installation
is based on the perfstat user. The installation will be skkipped when
user is existing.

Role Variables
--------------

The following example only shows mandatory variables from oracle_databases:

```yaml
oracle_databases:
  - oracle_db_name: DB1
    oracle_db_type: SI
    statspack:
      state: present
      tablespace: sysaux
      tablespace_temp: temp
      purgedays: 14
      snaplevel: 7
      snapinterval: "FREQ=hourly;byminute=0;bysecond=0"
```

Dependencies
------------

Author Information
------------------

Thorsten Bruhns <thorsten.bruhns@googlemail.com>
