# ansible-oracle

- Installs Oracle RAC, RAC One Node and normal single instances.
- Start with one or more clean machine(s), end up with a fully configured RAC Cluster.


By default, you can install a single instance 12.2.0.1 database on filesystem. Just put the following file in /tmp on the control-machine

- `linuxx64_12201_database.zip`



### Getting started

Pre-requisites:

- Ansible >= 2.1
- Oracle Linux (or any RHEL-based Linux System) >= 6.4
- Oracle Database/Grid Infrastructure 12.2.0.1, 12.1.0.1, 12.1.0.2, 11.2.0.4, 11.2.0.3


### Roles

**common**:
This will configure stuff common to all machines
- Install some generic packages
- Configure ntp


**orahost**:
This will configure the host specific Oracle stuff:
- Add a user & group
- Create directory structures
- Handle filesystem storage (partition devices, creates vg/lv and a filesystem (ext4, xfs, btrfs) etc). If you want to create your database on a filesystem (instead of ASM) this is where you define the layout.
- Install required packages
- Change kernel paramemeters
- Set up pam.d/limits config
- Configures Hugepages (as a percentage of total RAM)
- Disables transparent hugepages
- Disables NUMA (if needed)
- Configures the interconnect network (if needed)
- Configures Oracle ASMLib


**orahost-ssh**
Configures passwordless ssh between clusternodes if setting up RAC (`configure_cluster=True`)
- Uses existing ssh-keys


**orahost-storage**
This role configures storage that shoud be used by ASM.
- Partitions devices (using parted)
- Create ASMlib labels or sets up udev-rules for device name persistence


**oraswgi-install**
This role will install and configure Oracle Grid Infrastructure. Tested with 12.1.0.1/12.1.0.2 & 11.2.0.4/11.2.0.3
- Adds a .profile_grid to the oracle user
- Sets up directory structures
- Copies the install-files to the servers, or installs from a remote location (e.g nfs share)
- Install Oracle Grid Infrastructure


**oraasm-createdg**
This role will create the diskgroup(s) that should be used for database storage. Uses asmca to create diskgroups.
- Generates a shellscript that uses asmca to create the diskgroups.


**oraswdb-install**
This role will install the oracle database server(s). It is possible to run more than 1 database from each home. It performs both Single Instance/RAC installations.
- Creates a .profile with the correct environment
- Creates directory structures
- Installs the database-server(s)


**oradb-manage-db**
This role creates/deletes databases
- Generates a responsefile to be used by dbca
- Creates the db using dbca


**oradb-create (deprecated - use oradb-manage-db instead)**
This role creates the databases (RAC/RAC One Node, Single Instance). Possible to create container databases. Performs a dbca silent run to create the database.
Note:
At the moment there is no listener configured when creating a database on a filesystem (i.e no grid infrastructure present). Will be added later though.
- Generates a responsefile to be used by dbca
- Creates the db using dbca
- Changes parameters based on input.


**oradb-delete (deprecated - use oradb-manage-db instead)**
This role deletes a database


**oraswgi-opatch**
This role will use opatch to apply a patch to a Grid Infrastructure home. At the moment it is basically written to apply PSU's, not one-off patches. It'll probably work but it is not designed for that at the moment.
Does an initial check to see if the patches are already applied, and skips through all steps if they are.


**cxoracle**
Installs cx_Oracle in preparation for using [ansible-oracle-modules](https://github.com/oravirt/ansible-oracle-module)


**orahost-cron**
Configures cron schedules if needed


**orahost-logrotate**
By default sets up logrotate for alert logs and listener logs



### Note

These are the Oracle binaries that are pre-configured to be used. They have to be manually downloaded and made available (either locally, from a web endpoint or through a nfs-share)

For 12.2.0.1:
```
    linuxx64_12201_database.zip
    linuxx64_12201_grid_home.zip
 ```

For 12.1.0.2
```
    linuxamd64_12102_database_1of2.zip
    linuxamd64_12102_database_2of2.zip
    linuxamd64_12102_grid_1of2.zip
    linuxamd64_12102_grid_2of2.zip
 ```

For 12.1.0.1:
```
    linuxamd64_12c_database_1of2.zip
    linuxamd64_12c_database_2of2.zip
    linuxamd64_12c_grid_1of2.zip
    linuxamd64_12c_grid_2of2.zip
 ```

For 11.2.0.4:
```
    p13390677_112040_Linux-x86-64_1of7.zip
    p13390677_112040_Linux-x86-64_2of7.zip
    p13390677_112040_Linux-x86-64_3of7.zip
 ```

 For 11.2.0.3:
 ```
    p10404530_112030_Linux-x86-64_1of7.zip
    p10404530_112030_Linux-x86-64_2of7.zip
    p10404530_112030_Linux-x86-64_3of7.zip
 ```
