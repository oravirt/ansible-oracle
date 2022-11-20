============================================
opitzconsulting.ansible_oracle Release Notes
============================================

.. contents:: Topics


v3.3.0
======

Release Summary
---------------

This Release introduce ASM Filter Driver Support for Oracle Grid-Infrastructure/Restart. It is experimental for the moment, because it requires more testing in the field.

Minor Changes
-------------

- Documentation: Added feauturelist and missing picture (oravirt#299)
- Replace include with include_tasks due to deprecation warning (oravirt#301)
- Update ocenv to 2022-11-22 (oravirt#305)
- added support to upgrade the timezone in the database using the oradb_tzupgrade role (oravirt#291)
- ansible-lint: move to v6.8.2 (oravirt#290)
- documentation: New Beginners Guide (oravirt#293)
- experimental support for ASMFD (Filter Driver) (oravirt#297)
- github-actions: Add development branch to Actions (oravirt#295)
- oradb_manage_db: support for dbca custom scripts (oravirt#300)
- pre-commit: move to v4.3.0 (oravirt#290)

Deprecated Features
-------------------

- inventory structure will be moved to new examples directory (oravirt#293)
- vagrant folder will be moved to examples (oravirt#293)

Bugfixes
--------

- common, orahost, oraswdb_install: Make some of the j2 templates source configurable (oravirt#296)
- fix oradb_manage_grants (oravirt#306)
- oraasm_manage_diskgroups: Added support for ASMFD (oravirt#302)
- oracle_datapatch: Fix password alias (oravirt#304)
- oradb_manage_db: Add option to set the path of the dbca template (oravirt#292)
- oraswdb_install: Fix oracle export environment variables (oravirt#294)
- pre-commit: added some extra hooks (oravirt#291)

Known Issues
------------

- Problem Instance <db_unique_name> is not running during DBCA in RAC (opitzconsulting#91)
- removal of database not working when db_name <> db_instance_name (opitzconsulting#28)
- wrong ORACLE_BASE in RAC with role sepepration (oravirt#259)

v3.2.0
======

Bugfixes
--------

- oracle_sqldba module: Use byte streams for sqlplus process communication.
- oradb-manage-db: Make the deployment of ocenv configurable (#285)
- oraswdb_install: Make it possible to install Oracle 19.3 on RedHat 8 (#284)

v3.1.0
======

Release Summary
---------------

The switch to ansible-lint 0.6.1 introduced a lto of changes in 3.1.0. Hopefully nothing brokes by that.

Minor Changes
-------------

- Development helper install_collection.sh (#279)
- READMEs rewritten (#268)
- Support of Read-Only ORACLE_HOMEs (#273)
- ansible-lint: Move to  v6.6.1 (#277)
- ansible-lint: linting and github actions for playbooks and inventory (#270)
- ansible-lint: removed disabled rules for v6.6.1 (#280)
- github Actions: check antsibull changelog files (#276)
- github actions: antsibull-changelog removed obsolete branches (#270)
- inventory: New Inventory for has (#272)
- inventory: replaced old example inventory (#268)
- new playbooks for future inventory (#268)
- using ansible in docker container (#268)
- vagrant: Vagrantfile for dbfs & has (#272)

Removed Features (previously deprecated)
----------------------------------------

- desupported leftover racattackl-install.yml (#272)

Security Fixes
--------------

- orahost: fix permissions for sudoers (#263)
- orahost: security: changed default for configure_oracle_sudo to false (#263)

Bugfixes
--------

- ansible-lint: removed name[play] from execptions (#272)
- fix for oracle_packages with SLES 15 and 15.3 (#282)
- fixed/fully implemented rman catalog support in oradb_rman (#278)
- fixes transparent huge pages handling for SLES 15.x (#282)
- github actions: ansible-lint: removed args due to deprecation warning (#270)
- oradb_manage_db: Bugfix listener.ora for multiple Instances on 1 host (#275)
- oradb_manage_db: add missing netca.rsp.19.3.0.0.j2 (#267)
- oradb_manage_db: new defaults for role (#268)
- orahost: new defaults for role (#268)
- orahost_ssh: added block with configure_cluster check (#271)
- orahost_storage: add --script to parted (#264)
- orasw_meta: added tasks/mount_stage_remote.yml (#269)
- orasw_meta: added tasks/umount_stage_remote.yml (#269)
- orasw_meta: new defaults for role (#268)
- requirements.yml: removed ansible-oracle due to loop in ansible-lint (#270)

v3.0.0
======

Release Summary
---------------

ansible-oracle has been converted into a collection.
This release starts using antsibull-changelog for managing the CHANGELOG.rst.


Major Changes
-------------

- Added antsibull-changelog for managing the CHANGELOG.rst (opitzconsulting#102)
- moved ansible-oracle into a collection (opitzconsulting#99)

Minor Changes
-------------

- Parameter oracle_asm_disk_string could be set when asmlib is used (opitzconsulting#82)
- Refactoring oraswgi-install for 19c and 21c (opitzconsulting#82)
- Removed parameter -ignorePrereq during GridSetup.sh (opitzconsulting#82)
- Replace broken .profile_* Envrionmentscript with ocenv (opitzconsulting#85)
- added execution of runcluvfy.sh before GridSetup.sh (opitzconsulting#82)
- added extra debug tasks with "msg: install-home-gi | Start .." before long running tasks (opitzconsulting#82)
- added support for updating opatch under 19c and 21c (opitzconsulting#98)
- added support to interpret password as hash instead of plaintext in dbpasswords by setting users[*].password_is_hash=true (opitzconsulting#81)
- ansible-lint: move to ansible-lint-action@v6.5.2 (opitzconsulting#261)
- merge ansible-oracle-modules/oc into plugins/modules (opitzconsulting#103)
- new way installing cvuqdisk.rpm in Grid-Infrastructure (opitzconsulting#82)
- ocenv: update to 2022-08-10 (#261)
- oradb-manage-db: use custom DBCA-Templates from ORACLE_HOME directly (opitzconsulting#87)
- orahost: add new attributes to host_fs_layout (opitzconsulting#96)
- oraswgi: assert OL8 and GI 19.3 without RU (opitzconsulting#84)
- oraswgi: move from package to yum for cvuqdisk.rpm (opitzconsulting#84)
- refactoring the includes for 19c and 21c (opitzconsulting#82)
- removed all check exceptions from .ansible-lint (opitzconsulting#99)
- uid/gid/passwd attribute in oracle_users/grid_users/oracle_groups is now optional (opitzconsulting#107)
- update ansible-lint for git pre-commit to v6.3.0 (opitzconsulting#99)

Breaking Changes / Porting Guide
--------------------------------

- Ansible 2.9+ needed (opitzconsulting#99)
- moved old playbooks to playbooks folder (opitzconsulting#99)
- rename all roles with '-' in name to '_' (opitzconsulting#99)
- renamed variable for EE-Options in Binaries (opitzconsulting#99)

Removed Features (previously deprecated)
----------------------------------------

- role removed: oraasm-createdg - replaced by oraasm_manage_diskgroups (opitzconsulting#97)
- role removed: oradb-create - replaced by oradb_manage_db (opitzconsulting#97)
- role removed: oradb-delete - replaced by oradb_manage_db (opitzconsulting#97)
- role removed: oradb-failover - should be implemented in oraswgi-install -no replacement availible (opitzconsulting#97)
- role removed: oraswgi-clone - not working with current Oracle versions, no replacement availible (opitzconsulting#97)

Bugfixes
--------

- added asmoper to oracle user in orahost (opitzconsulting#82)
- be less verbose during ansible-playbook (opitzconsulting#101)
- does not require host_fs_layout to have "disks" attribute when "configure_host_disks==false" (opitzconsulting#108)
- fixed gold image copy path (opitzconsulting#92)
- fixes a problem where oracle user home directory has been hardcoded to be under /home (opitzconsulting#93)
- make ansible-lint more happy due to new rules (opitzconsulting#94)
- make collection compatble for galaxy.ansible.com (opitzconsulting#101)
- oracle_db: Set SYSTEM password when creating a DB
- oracle_profile: make it compatible for Python3 (opitzconsulting#95)
- oradb_manage_grants & oradb_manage_users: pass container and container_data parameters to modules
- oradb_manage_statspack: Bugfix for db.state <> present
- oraswgi_install: fixed wrong script task to shell (#261)
- remove auto execution of ocenv from .bashrc (opitzconsulting#100)

Known Issues
------------

- Problem Instance <db_unique_name> is not running during DBCA in RAC (opitzconsulting#91)
- removal of database not working when db_name <> db_instance_name (opitzconsulting#28)
- wrong ORACLE_BASE in RAC with role sepepration (#259)
