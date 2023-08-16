# ansible-oracle missing documentation

## concept guide
- why use a container for ansible-oracle?
- do I have to use a container? installed on each RDBMS machine, how should this work?
- why ansible and not some other IaC?
- ok, now I have installed, how do I run the DB and make changes, do I need ansible-oracle for that too?
- can I do patches with ansible-oracle?
- can I upgrade with ansible-oracle?
- what are best practices around 
   -- single install
   -- install e.g. 500 Oracle DBs
   -- install Single instance with GI
   -- convert GI on SI to RAC
   -- upgrading
   -- operations with ansible-oracle
- explain concepts around ansible collection
- meaning of files and directories
- venv, differnt versions of python / ansible
- ansible controller


pre-commit
ansibler-lint nur dev


awx opensource
ansible tower
redhat automation p

wheel, allow for ansible
yum install pythion3-setuptools
pip install --upgrade pip



## logging
- first beginner installation, runing from ansible-container to OL VM took 7 hours
- no timing in log on-screen
- where can I find the log files?


## beginner 
- explain concepts/details around the following...
   - hardening
   - perfstat
   - oracle home
   - PDB or CDB? 
   - rman scripts
   - what is ocenv?
   - systemctl script
   - licensing options, chopt
   - Update orabasetab file to disable Read-Only Oracle home
   - SQL Zauberkasten
   - glogin.sql
   - explain why the installation has so many extra steps and what they do
   - PLAY RECAP *****************************************************************************************************************************************************************
beginner-dbfs-151-192-168-56-161.nip.io : ok=254  changed=119  unreachable=0    failed=0    skipped=154  rescued=0    ignored=1

- how to connect with winscp to Oracle Linux 8?
  1. ssh key
  1. only vagrant user?
  1. which IP? 127.0.0.1 which port?
  1. also 192,168.56.xxx
  - directory structure of new Oracle install
    -- adump or audit?
    -- rman_backup.sh why bin directory? --> scripts
    -- rest of rman config in /u01/app/oracle/rman/ ??
    -- /u01/stage/19.3.0.0/ ??
    -- /u01/stage/rsp/ --> /tmp

  - operations (Betrieb) of new Oracle, explain rman, perfstat, etc
- how to configure ansible-orcle with examples

## developer documentation
- roles documentation is available
- modules?
- inventory?

- my installation took a long time, 7 hours
- where are the log files
- how can I speed it up?

- something went wrong, how can I debug it?
- I found a bug, how can I get it fixed?
- when is support for v23 coming?
- how can I get support for feature XXXX?


## FAQ
- how can I change the version to be installed
- how can I install an RU patch?
    - see MOS 555.1 and 888.1 RU, MRP + 10 patches
    - db_homes.yml
       - apply_patches_db: false
- how can I change the oracle_home?
    - db-homes.yml?
    - ocenv
    - main.yml oracle_base
- how can I change the IP of the beginner Oracle Linux VM (beginner-dbfs-151-192-168-56-161.nip.io)


## ideas
- orachk installation and run at the end
- update sql developer version
- install dbsat
- install db diff
- OL8 not OL7
- why special randanic linux? why not std OL8?

ansible@ansible-oracle:/git/ansible-oracle/example/beginner/ansible$ ansible-playbook -i inventory/ -e hostgroup=dbfs playbooks/single-instance-fs.yml
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks instead. This feature will be removed in version 2.16. Deprecation warnings can be disabled
by setting deprecation_warnings=False in ansible.cfg.

TASK [opitzconsulting.ansible_oracle.orahost : ansible.builtin.include] ****************************************************************************************************
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks/import_playbook instead. This feature will be removed in version 2.16. Deprecation warnings
can be disabled by setting deprecation_warnings=False in ansible.cfg.
included: /ansible/galaxy/ansible_collections/opitzconsulting/ansible_oracle/roles/orahost/tasks/RedHat-7.yml for beginner-dbfs-151-192-168-56-161.nip.io


### step-by-step guide to install and use ansible-oracle on a VM, but no docker container
- how exactly to install, os packages, git commands
- what to change (home,version, patches, etc.)
- how to run the playbook
- how to debug, log files
- documentation rhel7/8 OL 7/8 SLES12/15

#### inventory
create a new directory under inventory (e.g. copy the existing "dbfs" directory and rename it)
- change host.yml to match your host to be installed
- in directory group_vars 
1. choose configuration options in host.yml (disk layout, memory usage, etc.)
1. software_src.yml choose e.g. source directory, local or nfs, unzip (Y/N), etc.
1. dev_sec.yml choose hardening options
in directory "has", you can see other possibilities
1. database.yml, exact sizing of Tablepsaces, memory, etc.
1. asm.yml (setup ASM disks)
