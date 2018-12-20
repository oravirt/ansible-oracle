# ansible-oracle

- Installs Oracle RAC, RAC One Node and normal single instances.
- Start with one or more clean machine(s), end up with a fully configured RAC Cluster.

### Getting started

Pre-requisites:

- Ansible >= 2.4
- Oracle Linux (or any RHEL-based Linux System) >= 6.4
- Oracle Database/Grid Infrastructure 18.3.0.0, 12.2.0.1, 12.1.0.1, 12.1.0.2, 11.2.0.4, 11.2.0.3
- For example configurations, look in:
```
  SI/FS:   group_vars/vbox-si-fs.  - vagrant config: http://github.com/oravirt/vagrant-vbox-si-fs
  SI/ASM:  group_vars/vbox-si-asm  - vagrant config: http://github.com/oravirt/vagrant-vbox-si-asm
  RAC/ASM: group_vars/vbox-rac-dc1 - vagrant config: http://github.com/oravirt/vagrant-vbox-rac
```

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

A lot of these roles uses Ansible modules that comes from [ansible-oracle-modules](https://github.com/oravirt/ansible-oracle-modules)

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
- Uses the **oracle_db** module
- Creates/deletes: `state: present/absent`
- Maintains archivelog/force_logging True/False

**oraswgi-manage-patches**

Manage patches in a GI environment
- Uses the **oracle_opatch** module
- Manages opatchauto type of patches as well as 'normal' one-offs

**oraswdb-manage-patches**

Statefully manage patches in a DB environment
- Uses the **oracle_opatch** module
- Manages opatchauto type of patches as well as 'normal' one-offs


**cxoracle**

Installs cx_Oracle in preparation for using [ansible-oracle-modules](https://github.com/oravirt/ansible-oracle-modules)


**orahost-cron**

Configures cron schedules if needed


**orahost-logrotate**


**oradb-manage-<*>**

Statefully manages various aspects of the DB. They all use modules from [ansible-oracle-modules](https://github.com/oravirt/ansible-oracle-modules)

- **oradb-manage-pdb**
- **oradb-manage-tablespace**
- **oradb-manage-parameters**
- **oradb-manage-roles**
- **oradb-manage-users**
- **oradb-manage-grants**
- **oradb-manage-redo**
- **oradb-manage-services**



### Deprecated roles

_**oraasm-createdg (use oraasm-manage-diskgroups instead)**_

_**oradb-create (use oradb-manage-db instead)**_

_**oradb-delete (use oradb-manage-db instead)**_

_**oraswgi-opatch (use oraswgi-manage-patches instead)**_



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
