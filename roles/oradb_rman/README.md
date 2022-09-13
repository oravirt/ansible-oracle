# oradb-rman

Manages RMAN Backups

This role is written by Thorsten Bruhns <thorsten.bruhns@opitz-consulting.com>
There is no warranty for any error in the scripts. Please test the Backup/Recovery after setup with ansible-oracle!
This role used rman_backup.sh from https://github.com/Rendanic/oracleToolbox/blob/master/rman/linux/rman_backup.sh

# Backup Strategies
The role has templates for 3 different strategies. Please do not edit this templates, because patches for this role could create conflicts. You can create your own templates and use them within rman_jobs.


* Online Backup to NFS

  Use the following names in rman_jobs:

  * archivelog
  * online_level0
  * online_level1

* Backup compressed to Recovery-Area and then to NFS

  Use the following names in rman_jobs:

  * archivelog_fra_disk
  * online_level0_fra_disk
  * online_level1_fra_disk


* Offline Backup to NFS

  Use the following names in rman_jobs:

  * offline_level0
  * offline_level1

# Example Playbook

You need root permissions for executing the role!

```
    - hosts: servers
      roles:
         - roles/oradb-rman
```

# Configuration
## Description of rman_jobs
Cronjobs are only created when day, weekday, hour and minute are defined.

* name

  Defines the name of the used template from roles/oradb-rman/templates
* disabled

  Defines the state of cron entry. The cronentry is only disabled but not removed!
* immediate

  This allows an immediate execution of RMAN for the named script. Please be aware thatt the order of elements defines the executionorder of the scripts. The RMAN is NOT executed in ASYNC mode of Ansible. This parameter is most used for the 1st configuration of the parameter.

* service

  This parameter is only used in RAC Environments!
  rman_backup.sh will only start a backup when the service is active on te current node. This allows a cronjob on every clusternode with a failoverservice to make sure, that a backup is running when the 'normal' node has failed. The services must be added with srvctl add service for the Database.

* day / weekday / hour / minute

  Variables for the cronjob.

* rman_retention_policy

  This could be used to overwrite the global default of `rman_retention_policy`at database level.

* 
## Example

The backup is configured in oracle_databases with rman_jobs:

```
  oracle_databases:
    - home: db_home1
      oracle_db_name: TEST

      rman_jobs:
         - name: parameter
         - name: archivelog
           disabled: False
           day: "*"
           weekday: "*"
           hour: "*"
           minute: "10"
         - name: online_level0
           disabled: False
           day: "*"
           weekday: "0"
           hour: "02"
           minute: "30"
         - name: online_level1
           disabled: False
           day: "*"
           weekday: "1-6"
           hour: "02"
           minute: "30"
```

## Variables
The following variables are global. They are not part of oracle_databases!

* rman_cronfile

  Defines the name of the cronfile in /etc/cron.d. Setting rman_cronfile: "" will use the cron of the oracle_user instead of /etc/cron.d

* rman_cron_logdir

  Destination for cron execution which is redirected with `>> rman_cron_logdir 2>&1`
  Default is `/var/log/oracle`

* rman_retention_policy

  Use rman_retention_policy_default when not defined. This variable could be used inside rman_jobs for individual retention policies for every Database.

* rman_channel_disk

  This parameter must be defined. Otherwise the assert of the role will fail, because there is no usable default for this directory.

* rman_retention_policy_default

  This values is used when rman_retention_policy is not defined inside rman_jobs:.
 `Default: "RECOVERY WINDOW OF 14 DAYS"`

* rman_channel_disk_default

  `Default value: "DISK FORMAT   '/u10/rmanbackup/%d/%d_%T_%U'"`

* rman_controlfile_autobackup_disk_default

  This parameter must be defined. Otherwise the assert of the role will fail, because there is no usable default for this directory.

* rman_fra_backupdir

  The target directory when you use the templates to backup the FRA to another disk (usually nfs).

* rmanautofs and rmanautofsmount

  When `rmanautofs: true`, then autofs is implemented to mount `rmanautofsmount` similar to "/net".
  Usually, you may then specify the nfs server and the corresponding export in `rman_channel_disk`.


## Howtos
### How to configure the RMAN scripts?
The role copies the templatefiles from role/oradb-rman/templates to $ORACLE_BASE/admin/<DB_NAME>/rman. The name in the list defines the name of the template with .j2 as extension.
	
### How to configure the cron?

The dictionary elements name, disabled, day, weekday, hour, minute are mandatory. The creation of cron only starts when every element is defined.

### How to use custom RMAN scripts?
Copy the script into the template directory `role/oradb-rman/templates` and add a `- name: <filename>` at `rman_jobs`. The filename must end with `.rman.j2` regardless of Jinja2 in the file. You could use your own variables in the custom files and add entries to `rman_jobs`. They will be added as item.1.<dictionaryelement> to the template.
Please do not edit existing files. They could be changed in future releases of oradb-rman.

