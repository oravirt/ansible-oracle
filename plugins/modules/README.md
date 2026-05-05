# ansible-oracle-modules
**Oracle modules for Ansible**

- If you have any questions/requests just create an issue and I'll look into it
- I've also included a playbook (test-modules.yml) that'll give you an idea on how the modules can be used.

To use the modules, create a 'library' directory next to your top level playbooks and put the different modules in that directory. Then just reference them as you would any other module.
For more information, check out: http://docs.ansible.com/developing_modules.html


Most (if not all) requires `oracledb` either on your controlmachine or on the managed node.

The default behaviour for the modules using `oracledb` is this:

- If neither username or password is passed as input to the module(s), the use of an Oracle wallet is assumed.
- In that case, the `oracledb.makedsn` step is skipped, and the connection will use the `'/@<service_name>'` format instead.
- You then need to make sure that you're using the correct tns-entry (service_name) to match the credential stored in the wallet.


These are the different modules:

**oracle_user**

pre-req: oracledb

 - Creates & drops a user.
 - Grants privileges only (can not remove them with oracle_user, use oracle_grants for that)

**oracle_tablespace**

pre-req: oracledb

 - Manages normal(permanent), temp & undo tablespaces (create, drop, make read only/read write, offline/online)
 - Tablespaces can be created as bigfile, autoextended


**oracle_grants**

pre-req: oracledb

 - Manages privileges for a user
 - Grants/revokes privileges
 - Handles roles/sys privileges properly. Does NOT yet handle object privs. They can be added but they are not considered while revoking privileges
 - The grants can be added as a string (dba,'select any dictionary','create any table'), or in a list (ie.g for use with with_items)

**oracle_role**

pre-req: oracledb

 - Manages roles in the database

**oracle_parameter**

pre-req: oracledb

 - Manages init parameters in the database (i.e alter system set parameter...)
 - Also handles underscore parameters. That will require using mode=sysdba, to be able to read the X$ tables needed to verify the existence of the parameter.

**Note:**
 When specifying sga-parameters the database requests memory based on granules which are variable in size depending on the size requested,
 and that means the database may round the requested value to the nearest multiple of a granule.
 e.g sga_max_size=1500M will be rounded up to 1504 (which is 94 granules of 16MB). That will cause the displayed value to be 1504M, which has
 the effect that the next time the module is is run with a desired value of 1500M it will be changed again.
 So that is something to consider when setting parameters that affects the SGA.

 **oracle_services**

pre-req: oracledb (if GI is not running)

  - Manages services in an Oracle database (RAC/Single instance)

**Note:**
At the moment, Idempotence only applies to the state (present,absent,started, stopped). No other options are considered.


**oracle_pdb**

pre-req: oracledb

 - Manages pluggable databases in an Oracle container database
 - Creates/deletes/opens/closes the pdb
 - saves the state if you want it to. Default is yes
 - Can place the datafiles in a separate location


**oracle_sql**

pre-req: oracledb

- 2 modes: sql or script
- Executes arbitrary sql or runs a script

**Note:**
Should be considered as experimental, or an alpha-release


**oracle_asmdg**

pre-req: oracledb

- Manages ASM diskgroup state. (absent/present)
- Takes a list of disks and makes sure those disks are part of the DG.
If the disk is removed from the disk it will be removed from the DG.
- Also manages attributes

**Note:**
- Supports redundancy levels, but does not yet handle specifying failuregroups


**oracle_asmvol**

- Manages ASM volumes. (absent/present)

**oracle_ldapuser**

pre-req: oracledb, ldap, re

- Syncronises users/role grants from LDAP/Active Directory to the database

**oracle_privs**

pre-req: oracledb, re

- Manages system and object level grants
- Object level grant support wildcards, so now it is possible to grant access to all tables in a schema and maintain it automatically!

**oracle_jobclass**

pre-req: oracledb

- Manages DBMS_SCHEDULER job classes

**oracle_jobschedule**

pre-req: oracledb, re

- Manages DBMS_SCHEDULER job schedules

**oracle_jobwindow**

pre-req: oracledb, datetime

- Manages DBMS_SCHEDULER windows

**oracle_job**

pre-req: oracledb, re

- Manages DBMS_SCHEDULER jobs

**oracle_rsrc_consgroup**

pre-req: oracledb, re

- Manages resource manager consumer groups including its mappings and grants

**oracle_awr**

pre-req: oracledb, datetime

- Manages AWR snapshot settings

**oracle_facts**

pre-req: oracledb

- Gathers facts about Oracle database

**oracle_gi_facts**

- Gathers facts about Grid Infrastructure cluster configuration

**oracle_stats_prefs**

pre-req: oracledb

- Managing DBMS_STATS global preferences


**oracle_redo**

pre-rec: oracledb

- Manage redo-groups and their size in RAC or single instance environments
- NOTE: For RAC environments, the database needs to be in ARCHIVELOG mode. This is not required for SI environments.

**oracle_db**

pre-rec: oracledb

- Create/remove databases (cdb/non-cdb)
- Can be created by passing in a responsefile or just by using parameters
