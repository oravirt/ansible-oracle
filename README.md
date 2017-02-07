# ansible-oracle-modules
Oracle modules for Ansible

- If you have any questions/requests just create an issue and I'll look into it
- I've also included a playbook (test-modules.yml) that'll give you an idea on how the modules can be used.

To use the modules, create a 'library' directory next to your top level playbooks and put the different modules in that directory. Then just reference them as you would any other module.
For more information, check out: http://docs.ansible.com/developing_modules.html


Most (if not all) requires cx_Oracle either on your controlmachine or on the managed node.

The default behaviour for the modules using cx_Oracle is this:

- If neither username or password is passed as input to the module(s), the use of an Oracle wallet is assumed.
- In that case, the cx_Oracle.makedsn step is skipped, and the connection will use the '/@<service_name>' format instead.
- You then need to make sure that you're using the correct tns-entry (service_name) to match the credential stored in the wallet.


These are the different modules:

<b> oracle_user </b>

pre-req: cx_Oracle

 - Creates & drops a user.
 - Grants privileges only (can not remove them with oracle_user, use oracle_grants for that)

<b> oracle_tablespace </b>

pre-req: cx_Oracle

 - Manages normal(permanent), temp & undo tablespaces (create, drop, make read only/read write, offline/online)
 - Tablespaces can be created as bigfile, autoextended


<b> oracle_grants </b>

pre-req: cx_Oracle

 - Manages privileges for a user
 - Grants/revokes privileges
 - Handles roles/sys privileges properly. Does NOT yet handle object privs. They can be added but they are not considered while revoking privileges
 - The grants can be added as a string (dba,'select any dictionary','create any table'), or in a list (ie.g for use with with_items)

<b> oracle_role </b>

pre-req: cx_Oracle

 - Manages roles in the database

<b> oracle_parameter </b>

pre-req: cx_Oracle

 - Manages init parameters in the database (i.e alter system set parameter...)
 - Also handles underscore parameters. That will require using mode=sysdba, to be able to read the X$ tables needed to verify the existence of the parameter.

<b> Note: </b>
 When specifying sga-parameters the database requests memory based on granules which are variable in size depending on the size requested,
 and that means the database may round the requested value to the nearest multiple of a granule.
 e.g sga_max_size=1500M will be rounded up to 1504 (which is 94 granules of 16MB). That will cause the displayed value to be 1504M, which has
 the effect that the next time the module is is run with a desired value of 1500M it will be changed again.
 So that is something to consider when setting parameters that affects the SGA.

 <b> oracle_services </b>

pre-req: cx_Oracle (if GI is not running)

  - Manages services in an Oracle database (RAC/Single instance)

<b> Note: </b>
At the moment, Idempotence only applies to the state (present,absent,started, stopped). No other options are considered.


<b> oracle_pdb </b>

pre-req: cx_Oracle

 - Manages pluggable databases in an Oracle container database
 - Creates/deletes/opens/closes the pdb
 - saves the state if you want it to. Default is yes
 - Can place the datafiles in a separate location


<b> oracle_sql </b>

pre-req: cx_Oracle

- 2 modes: sql or script
- Executes arbitrary sql or runs a script


<b> oracle_asmdg </b>

pre-req: cx_Oracle

- Manages ASM diskgroup state. (absent/present)
- Takes a list of disks and makes sure those disks are part of the DG.
If the disk is removed from the disk it will be removed from the DG.

<b> Note: </b>
- Supports redundancy levels, but does not yet handle specifying failuregroups
- Does not yet handle attributes

<b> oracle_asmvol </b>

- Manages ASM volumes. (absent/present)

**oracle_ldapuser**

pre-req: cx_Oracle, ldap, re

- Syncronises users/role grants from LDAP/Active Directory to the database
