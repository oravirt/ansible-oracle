# ansible-oracle

- Installs Oracle RAC, RAC One Node and normal single instances.
- Start with one or more clean machine(s), end up with a fully configured RAC Cluster.

### Getting started

Pre-requisites:

- Ansible >= 2.4
- Oracle Linux (or any RHEL-based Linux System) >= 6.4
- Oracle Database/Grid Infrastructure 18.3.0.0, 12.2.0.1, 12.1.0.1, 12.1.0.2, 11.2.0.4, 11.2.0.3

By default, installs a single instance 18.3.0.0 database on a filesystem.

1. Clone this repository:
   `git clone --recursive https://github.com/oravirt/ansible-oracle`

2. Add the following file to `/tmp` on the controlmachine
   - `LINUX.X64_180000_db_home.zip`

3. Create an Ansible inventory file
   ```
   [myhostgroup]
    dbhost
   ```

4. Run the playbook:

   `ansible-playbook single-instance-db-on-fs.yml -e hostgroup=myhostgroup -i /path/to/inventory`

   where the `-i` part is optional


### Roles

**common**

This will configure stuff common to all machines
- Install some generic packages
- Configure ntp


**orahost**

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

This role will install and configure Oracle Grid Infrastructure (RAC/SI)
- Adds a .profile_grid to the oracle user
- Sets up directory structures
- Copies the install-files to the servers, or installs from a remote location (e.g nfs share)
- Install Oracle Grid Infrastructure


_**oraasm-createdg (deprecated - use oraasm-manage-diskgroups instead)**_

_This role will create the diskgroup(s) that should be used for database storage. Uses asmca to create diskgroups.
- Generates a shellscript that uses asmca to create the diskgroups._

**oraasm-manage-diskgroups**

This role will statefully manage the lifecycle of an ASM diskgroup
- Uses the **oracle_asmdg** module
- Create/delete diskgroup.
- Add/remove disks
- Manage attributes for the DG

**oraswdb-install**

This role will install the oracle database server(s). It is possible to run more than 1 database from each home. It performs both Single Instance/RAC installations.
- Creates a .profile with the correct environment
- Creates directory structures
- Installs the database-server(s)


**oradb-manage-db**

This role statefully manages the lifecycle of a database
- Manages the db using the **oracle_db** module
- Maintains archivelog/force_logging True/False


_**oradb-create (deprecated - use oradb-manage-db instead)**_

_This role creates the databases (RAC/RAC One Node, Single Instance). Possible to create container databases. Performs a dbca silent run to create the database.
- Generates a responsefile to be used by dbca
- Creates the db using dbca
- Changes parameters based on input._


_**oradb-delete (deprecated - use oradb-manage-db instead)**_

_This role deletes a database_


_**oraswgi-opatch (deprecated - use oraswgi-manage-patches instead)_

_This role will use opatch to apply a patch to a Grid Infrastructure home. At the moment it is basically written to apply PSU's, not one-off patches. It'll probably work but it is not designed for that at the moment.
Does an initial check to see if the patches are already applied, and skips through all steps if they are._

**oraswgi-manage-patches**

Manage patches in a GI environment
- Uses the **oracle_opatch** module
- Manages opatchauto type of patches as well as 'normal' one-offs

**oraswdb-manage-patches**

Statefully manage patches in a DB environment
- Uses the **oracle_opatch** module
- Manages opatchauto type of patches as well as 'normal' one-offs


**cxoracle**

Installs cx_Oracle in preparation for using [ansible-oracle-modules](https://github.com/oravirt/ansible-oracle-module)


**orahost-cron**

Configures cron schedules if needed


**orahost-logrotate**


**oradb-manage-<*>**

Statefully manages various aspects of the DB
- **oradb-manage-pdb**
- **oradb-manage-tablespace**
- **oradb-manage-parameters**
- **oradb-manage-roles**
- **oradb-manage-users**
- **oradb-manage-grants**
- **oradb-manage-redo**
- **oradb-manage-services**



### Note

These are the Oracle binaries that are pre-configured to be used. They have to be manually downloaded and made available (either locally, from a web endpoint or through a nfs-share)

For 18.3.0.0:
```
    LINUX.X64_180000_db_home.zip
    LINUX.X64_180000_grid_home.zip
 ```


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
