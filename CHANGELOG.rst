============================================
opitzconsulting.ansible_oracle Release Notes
============================================

.. contents:: Topics


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
