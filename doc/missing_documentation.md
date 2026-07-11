# ansible-oracle missing documentation

## concept guide
- why use a container for ansible-oracle?
- do I have to use a container? installed on each RDBMS machine, how should this work?
- why ansible and not some other IaC?
- ok, now I have used ansible-oracle and the database is installed, how do I run the DB and make changes, do I need ansible-oracle for that too? Can I use ansible-oracle for operations? How exactly do I do this. Document this.
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
- venv, different versions of python / ansible
- ansible controller
- why rendanic Linux, why not standard OL? (security concerns)

## should I use ansible-oracle or ansible-oracle-inventory ?
- ansible-oracle is only meant for development, use the ansible-oracle-inventory to install oracle
- right now, I work in the ansible-oracle to
1. improve documentation
1. improve the examples
later I will probably move to using the ansible-oracle-inventory project

## Install many oracle DBs
To install many Oracle DBs, we do not install a local ansible-controller, but use a central ansible controller. For example...
- awx opensource
- ansible tower
- redhat automation program

## Understanding ansible inventory
- https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html

## why not use ansible-oracle?
1. Currently no support for
- Windows
- Sun Solaris
- HP-UX
- ARM
- AIX
- SLES12/15
- OL5 / RHEL5
- OL6 / RHEL6

ansible-oracle currently works for OL7/8, RHEL7/8

2. Some customers wish to understand exactly what is going on. Often in preparation of cust using the automated method themselves.



## logging
- first beginner installation, running from ansible-container to OL VM took 7 hours
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
   - PLAY RECAP - what does this mean? How ddo I understand if ansible-oracle was successful?*****************************************************************************************************************************************************************
beginner-dbfs-151-192-168-56-161.nip.io : ok=254  changed=119  unreachable=0    failed=0    skipped=154  rescued=0    ignored=1
- how do I know how long the installation took in total?

- how to connect with winscp to Oracle Linux 8?
  1. ssh key
  1. only vagrant user?
  1. which IP? 127.0.0.1 which port?
  1. also 192,168.56.xxx
  - directory structure of new Oracle install
    - adump or audit?
    - rman_backup.sh why bin directory? --> scripts
    - rest of rman config in /u01/app/oracle/rman/ ??
    - /u01/stage/19.3.0.0/ ??
    - /u01/stage/rsp/ --> /tmp

  - operations (Betrieb) of new Oracle, explain rman, perfstat, etc
- how to configure ansible-orcle with examples
- why does sqlus "/ as sysdba" npt work? How to set my environment variables?

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
- how can I change the Oracle DB version to be installed
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
- orachk installation (AHF). and run at the end and produce HTML report
- update sql developer version
- install dbsat
- install db diff
- OL8 not OL7 as the default example
- why special randanic linux? why not std OL8?



# step-by-step guide to install and use ansible-oracle on a VM, but no docker container
- how exactly to install, os packages, git commands
- what to change (home,version, patches, etc.)
- how to run the playbook
- how to debug, log files
- documentation rhel7/8 OL 7/8 SLES12/15

## Inventory
create a new directory under inventory (e.g. copy the existing "dbfs" directory and rename it)
- change host.yml to match your host to be installed
- in directory group_vars
1. choose configuration options in host.yml (disk layout, memory usage, etc.)
1. software_src.yml choose e.g. source directory, local or nfs, unzip (Y/N), etc.
1. dev_sec.yml choose hardening options
in directory "has", you can see other possibilities
1. database.yml, exact sizing of Tablespaces, memory, etc.
1. asm.yml (setup ASM disks)



# Operations with dev-sec enabled
## su - oracle
- su is allowed only for root. Simply use...
sudo su - oracle

# Bugs in ansible-oracle
- path does not include Oracle binaries for oracle user (source ~/.profile_db19_si_se2 missing in .bash_profile)
- patch download does not work "Error 401--Unauthorized"


# Security
- dev-sec hardening, source, description
- SELINUX disabled for installation and permanently disabled

# explain skipped / ignored, etc.
PLAY RECAP ******************************************************************************************************************************************************************
beginner-dbfs-patching-151-192-168-56-162.nip.io : ok=171  changed=6    unreachable=0    failed=1    skipped=109  rescued=0    ignored=2

Playbook run took 0 days, 0 hours, 2 minutes, 21 seconds





## how to add patches
D:\ala\ansible-oracle\example\beginner_patching\ansible\inventory\group_vars\all\db-homes.yml
in section oracle_sw_patches, add a list of all the patches that can be installed....
  - filename: p35320081_190000_Linux-x86-64.zip
    patchid: 35320081
    version: 19.3.0.0
    description: 19.20.0 RDBMS RU patch
    creates: 35320081/README.txt


now in the 	db_homes_config, add a new home
  db1920_si_se2: &db1920_si_se2
    version: 19.3.0.0
    oracle_home: /u01/app/oracle/product/19/db1920-si-se2
    edition: SE2
    opatch_minversion: 12.2.0.1.37
    state: present
    opatchauto: []
    opatch:
      - patchid: 35320081
        # Database Release Update 19.20.0.0.230718
        patchversion: 19.20.0.0.230718
        stop_processes: true
        state: present


## bugs found
1. download patches, never works
1. download patches, not same list as to be installed ??
1. change patches, install home not changed
1. install EE or SE?
1. reboot test, oracle not started
1. su - oracle, ocenv does not set PATH or ORACLE_SID
1.
ansible@ansible-oracle:/git/ansible-oracle/example/beginner/ansible$ ansible-playbook -i inventory/ -e hostgroup=dbfs playbooks/single-instance-fs.yml
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks instead. This feature will be removed in version 2.16. Deprecation warnings can be disabled
by setting deprecation_warnings=False in ansible.cfg.

TASK [opitzconsulting.ansible_oracle.orahost : ansible.builtin.include] ****************************************************************************************************
[DEPRECATION WARNING]: "include" is deprecated, use include_tasks/import_tasks/import_playbook instead. This feature will be removed in version 2.16. Deprecation warnings
can be disabled by setting deprecation_warnings=False in ansible.cfg.
included: /ansible/galaxy/ansible_collections/opitzconsulting/ansible_oracle/roles/orahost/tasks/RedHat-7.yml for beginner-dbfs-151-192-168-56-161.nip.io


major can break change
minor
bugfix


# symantec versioning is used for ansible-oracle
see https://semver.org/lang/de/
- major can break change
- minor, new features
- bugfix, bugfixes only

# examples
- beginner_patching
- local_linux
1. vagrant - testUmgebung
1. customer linux, simple install



## special cases
- partitions
- EE mit packs


## steps in examples
1. ansible-controller in custoemr environment?
if not, install locally on oracle DB server
options
1. script for RHEL7/RHEL8/SLES12/SLES15 (und bald RHEL9)
1. docker container or podman? contains ansible-controller,
https://github.com/ansible/ansible-runner
if existing ansible-controller, it will be complicated...


### problems ansible-container
1. docker or podman?

### problems script
1. rhel7, old version ansible, old version python
1. SLES generally, default versions of ansible are old, python?
https://endoflife.date/sles

both solutions?
script avoids docker/podman
docker/podman allows older Linux


1. partitions
1. special wishes?

## usage goal of ansible-oracle
ansible-oracle only for installation
with Betrieb, throw away ansible-oracle
