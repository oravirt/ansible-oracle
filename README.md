Various roles to install various Oracle related products.

It's been tested with ansible version 1.6

At the moment you can install Oracle RAC, RAC One Node and normal single instances.
You can take a freshly installed machine and configure it from ground up. It'll configure users, profiles, kernel parameters, storage and install the database server and create one or more databases.

Note: 
- You'll need to manually download the Oracle software and make it available to the control-machine (either locally or on a web-server) before running the playbook.
- Also, at the moment parts of the playbooks are not idempotent (yet), meaning it will try to perform some of the installations again. Will be fixed.

The different roles are:

common:
This will configure stuff that I want on all my machines, - Install some generic packages 
- Configure ntp 
- Possibly add a default/deploy-user.

orahost:
This will configure the host specific Oracle stuff:
- Add a user & group
- Create directory structures
- Generate ssh-keys and set up passwordless ssh between clusternodes in case of RAC/RAC One node
- Handle filesystem storage (partition devices etc)
If you want to create your database on a filesystem (instead of ASM) this is where you define the layout.
- Install required packages
- Change kernel paramemeters
- Set up pam.d/limits config
- Disables transparent hugepages, and at the moment also disables numa. Will make this more dynamic in the future.
- Configures the interconnect network (if needed)
- Configures Oracle ASMLib 

orahost-storage:
This role configures storage that shoud be used by ASM.
- Partitions devices (using parted)
- Create ASMlib labels on disks

oraswgi-install:
This role will install and configure Oracle Grid Infrastructure. I've only tried it with 12.1.0.1/12.1.0.2 yet but there shouldnt be a problem to configure earlier releases.
- Adds a .profile_grid to the oracle user
- Sets up directory structures
- Copies the install-files to the servers
- Install Oracle Grid Infrastructure

oralsnr:
This role will create a default listener.
This only be run if the single node Grid Infrastructure installation (Oracle Restart) is performed.
Note:
At the moment there is no listener configured when creating a database on a filesystem (i.e no grid infrastructure present). Will be added later though.
- Uses srvctl to add/start the default listener

oraasm-configureasm:
This role will create and configure the ASM-instance with an initial diskgroup.
This only be run if the single node Grid Infrastructure installation (Oracle Restart) is performed.
- Generates a shellscript that uses asmca to create the ASM instance

oraasm-createdg:
This role will create the diskgroup(s) that should be used for database storage. Uses asmca to create diskgroups.
- Generates a shellscript that uses asmca to create the diskgroups. 
Note: It will try to create the initial diskgroup again, and fail but that is ok, the error is ignored and the play will continue.

oraswdb-install:
This role will install the oracle database server(s). If there will be more than one database running it will get its own ORACLE_HOME. It performs both Single Instance/RAC installations.
- Creates a .profile_<database_name>
- Creates directory structures
- Transfers installfiles to server(s)
- Installs the database-server(s)

oradb-create:
This role creates the databases (RAC/RAC One Node, Single Instance). Performs a dbca silent run to create the database.
Note:
At the moment there is no listener configured when creating a database on a filesystem (i.e no grid infrastructure present). Will be added later though.
- Generates a responsefile to be used by dbca
- Creates the db using dbca
- Changes parameters based on input.

*** THE FOLLOWING ROLES ARE NOT FINISHED/NOT WORKING PROPERLY YET ****

oraswgi-opatch:
This role will use opatch to apply a patch to a Grid Infrastructure home.

oraswgi-clone:
This role will use a previoulsy installed/patched Grid Infrastructure installation to perform a new Grid Infrastructure installation using the clone method

oraswracdb-clone:
This role will take a previously installed/patched Oracle Database Server installation to perform a new database server installation using the clone method.

