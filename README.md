

<b> Requirements:

- Ansible >= 1.6
- Oracle Linux (or any RHEL-based Linux System) >= 6.4
- Oracle Database/Grid Infrastructure 12.2.0.1, 12.1.0.1, 12.1.0.2, 11.2.0.4, 11.2.0.3

</b>

At the moment you can install Oracle RAC, RAC One Node and normal single instances.
You can take a freshly installed machine and configure it from ground up. It'll configure users, profiles, kernel parameters, storage and install the database server and create one or more databases.
It also supports role separation when installing Grid Infrastructure, meaning a 'grid' user owns and runs the GI and the 'oracle' user owns and runs the databases.

By default, you can install a single instance 12.1.0.2 database on filesystem, without having to change any parameters. Just put the following files in /tmp on the control-machine:
- linuxamd64_12102_database_1of2.zip
- linuxamd64_12102_database_2of2.zip

I'm creating a bunch of examples which illustrates how to use/run the different roles. They can be found here: http://oravirt.wordpress.com/category/ansible-oracle. 

As this is based on the EL6 platform the lowest supported Oracle version will be 11.2.0.3, as per Oracle's certification matrix.

<b>Note: </b>
- You'll need to manually download the Oracle software and make it available to the control-machine (either locally or on a web-server, or through a nfs-share) before running the playbook. By default the 
path to the software is /tmp on the control-machine.
- All roles are built on Oracle Linux 6, but should work with any EL6-based system.
- Storage options only supports block devices at the moment (FS & ASM). Will add support for NFS

<b>The different roles are:</b>

<b> common: </b>
This will configure stuff common to all machines
- Install some generic packages 
- Configure ntp 
- Possibly add a default/deploy user.

<b>orahost:</b>
This will configure the host specific Oracle stuff:
- Add a user & group
- Create directory structures
- Generate ssh-keys and set up passwordless ssh between clusternodes in case of RAC/RAC One node
- Handle filesystem storage (partition devices, creates vg/lv and a filesystem (ext4, xfs, btrfs) etc). If you want to create your database on a filesystem (instead of ASM) this is where you define the layout.
- Install required packages
- Change kernel paramemeters
- Set up pam.d/limits config
- Configures Hugepages (as a percentage of total RAM)
- Disables transparent hugepages
- Disables NUMA (if needed)
- Configures the interconnect network (if needed)
- Configures Oracle ASMLib 

<b>orahost-storage:</b>
This role configures storage that shoud be used by ASM.
- Partitions devices (using parted)
- Create ASMlib labels or sets up udev-rules for device name persistence

<b>oraswgi-install:</b>
This role will install and configure Oracle Grid Infrastructure. Tested with 12.1.0.1/12.1.0.2 & 11.2.0.4/11.2.0.3
- Adds a .profile_grid to the oracle user
- Sets up directory structures
- Copies the install-files to the servers, or installs from a remote location (e.g nfs share)
- Install Oracle Grid Infrastructure



<b>oraasm-configureasm:</b>
This role will create and configure the ASM-instance with an initial diskgroup.

- Generates a shellscript that uses asmca to create the ASM instance

<b>oraasm-createdg:</b>
This role will create the diskgroup(s) that should be used for database storage. Uses asmca to create diskgroups.
- Generates a shellscript that uses asmca to create the diskgroups. 

<b>oraswdb-install:</b>
This role will install the oracle database server(s). It is possible to run more than 1 database from each home. It performs both Single Instance/RAC installations.
- Creates a .profile_databasename
- Creates directory structures
- Transfers installfiles to server(s)
- Installs the database-server(s)

<b>oradb-create:</b>
This role creates the databases (RAC/RAC One Node, Single Instance). Possible to create container databases. Performs a dbca silent run to create the database.
Note:
At the moment there is no listener configured when creating a database on a filesystem (i.e no grid infrastructure present). Will be added later though.
- Generates a responsefile to be used by dbca
- Creates the db using dbca
- Changes parameters based on input.


<b>oraswgi-opatch:</b>
This role will use opatch to apply a patch to a Grid Infrastructure home. At the moment it is basically written to apply PSU's, not one-off patches. It'll probably work but it is not designed for that.
Does an initial check to see if the patches are already applied, and skips through all steps if they are.


<b>*** THE FOLLOWING ROLES ARE NOT FINISHED/NOT WORKING PROPERLY YET ****</b>

<b>oraswgi-clone:</b>
This role will use a previously installed/patched Grid Infrastructure installation to perform a new Grid Infrastructure installation using the clone method

<b>oraswracdb-clone:</b>
This role will take a previously installed/patched Oracle Database Server installation to perform a new database server installation using the clone method.



<b>TODO</b>
- Add service to database as part of db-creation
- Add support for NFS storage
- Cleanup
- .........

********************************
