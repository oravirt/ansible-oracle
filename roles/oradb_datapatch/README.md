oradb-datapatch
=========

This role will run datapatch on selected databases



Role Variables
--------------

```
oracle_user: oracle
db_user: sys
db_password: "{% if dbpasswords is defined and dbpasswords[item.oracle_db_name] is defined and dbpasswords[item.oracle_db_name][db_user] is defined%}{{dbpasswords[item.oracle_db_name][db_user]}}{% else %}{{ default_dbpass}}{% endif%}"

db_service_name: "{%- if item.oracle_db_unique_name is defined -%}
                       {{ item.oracle_db_unique_name }}
                  {%- else -%}
                       {{ item.oracle_db_name }}
                  {%- endif -%}"

listener_port_template: "{% if item.listener_port is defined %}{{ item.listener_port }}{% else %}{{ listener_port }}{% endif %}"
listener_port: 1521
fail_on_db_not_exist: False   <-- If the DB is not yet created at the time of the datapatch run, we still want the play to continue
```


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: oradb-datapatch }

Author Information
------------------

Mikael Sandström, oravirt@gmail.com, @oravirt
