# ansible-oracle-modules
Oracle modules for Ansible


To use them, create a 'library' directory next to your top level playbooks and put the different modules in that directory. Then just reference them as you would any other module.
For more information, check out: http://docs.ansible.com/developing_modules.html

These are the different modules:

<b> oracle_user </b>

pre-req: cx_Oracle

 - Creates & drops a user. 
 - Grants privileges only (can not remove them with oracle_user, use oracle_grants for that)

<b> oracle_tablespace </b>

pre-req: cx_Oracle

 - Manages tablespaces (create, drop, make read only/read write, offline/online)
 - Tablespaces can be created as bigfile, autoextended


<b> oracle_grants </b>

pre-req: cx_Oracle

 - Manages privileges for a user
 - Grants/revokes privileges
 - Handles roles/sys privileges properly. Does NOT yet handle object privs. They can be added but they are not considered while revoking privileges
 - The grants can be added as a string (dba,'select any dictionary','create any table'), or in a list (ie.g for use with with_items)

