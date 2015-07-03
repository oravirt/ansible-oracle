# ansible-oracle-modules
Oracle modules for Ansible


To use them, create a 'library' directory next to your top level playbooks and put the different modules in that directory. Then just reference them as you would any other module.
For more information, check out: http://docs.ansible.com/developing_modules.html

These are the different modules:

<b> oracle_user </b>

pre-req: cx_Oracle

 - Creates & drops a user. 
 - Grants privileges


