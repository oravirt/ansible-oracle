=============================================
opitzconsulting.ansible\_oracle Release Notes
=============================================

.. contents:: Topics

v4.13.1
=======

Minor Changes
-------------

- Upgrade ansible-doctor 6.0.5 and pre-commit (oravirt#517)
- ansible-lint upgrade to 25.2.1 (oravirt#517)
- helper script for building releases (oravirt#518)
- nix: Adding direnv and nix configuration for easy setup of dev environment via nix-shell (oravirt#517)

Security Fixes
--------------

- ansible-core: Upgrade versions due to security alerts from dependbot (oravirt#517)

Bugfixes
--------

- oradb_tzupgrade_pdbs: compose the list of PDBs in Ansible (oravirt#516)

v4.13.0
=======

Minor Changes
-------------

- Added a guide on how to install Ansible-Oracle manually on a server without Internet access. (oravirt#506)
- Fix typo for sql_zauberkasten (oravirt#509)
- ansible-lint: more excludes (oravirt#505)
- create OMF enabled databases using dbca's -useOMF flag (oravirt#507)
- manage_pdb: Enter nested loop only when oracle_pdbs has an entry (oravirt#507)
- oraapex: Added missing option to copy source from remote or local host (oravirt#512)
- oradb_manage_db: make hard coded folder .Scripts configurable (oravirt#511)
- oradb_tzupgrade: Add orasw_meta_internal as a dependent role (oravirt#510)

Bugfixes
--------

- orahost_meta: move scripts_folder variable from common to orahost_meta (oravirt#504)

v4.12.0
=======

Minor Changes
-------------

- ansible-lint: more excludes (oravirt#505)
- common: remove screen from default rhel8,9 package list (oravirt#496)
- orahost: firewall_service should default to firewalld on OL/EL 8 (oravirt#499)

Bugfixes
--------

- common: Exclude alias interfaces when templating motd.j2 (oravirt#486)
- common: force bool type in certain conditionals
- fix for re global flags when extracting sga/processes parameters in orahost_meta (oravirt#493)
- orahost_meta: Aggregate SGAs fails if no sga_target or sga_max_size is defined (oravirt#498)
- orahost_meta: Applying 'lower' filter to oracle_databases+oracle_asm_instance converts list to string (oravirt#484)
- oraswdb_manage_patches, oraswgi_manage_patches: make unarchive check work for combo patches too (oravirt#482)
- set and check _oradb_tzupgrade_candidate_pdbs fact when upgrading timezone for a CDB database (oravirt#490)

v4.11.1
=======

Bugfixes
--------

- devsec: changed hosts=all to hosts={{ hostgroup | default('all') }} (oravirt#479)
- orasw_download_patches: bugfix for empty oracle_databases or oracle_pdbs (oravirt#480)
- orasw_meta: empty oracle_databases broke orasw_download_patches (oravirt#480)

v4.11.0
=======

Release Summary
---------------

Roles for APEX and ORDS have been added in experimental state.
The old issue with missing support for listener configuration in Oracle GI/Restart has been fixed.
A new Playbook manage_sqlnet.ora has been added for easier configuration of listener.ora, sqlnet.ora and tnsnames.ora.

Minor Changes
-------------

- ORDS: new experimental role to install and configure ORDS on OracleLinux (oravirt#473)
- ansible-oracle Documentation fixes (oravirt#473)
- beginner_patching: Inventory for ORDS + APEX (oravirt#473)
- example rac: create multiple listener as example (oravirt#475)
- galaxy: added new collection as dependency for RAC/Restart listener configuration (oravirt#475)
- molecule: Added APEX and ORDS to dbfs-ol9 (oravirt#473)
- molecule: added 2nd listener for testing (oravirt#475)
- oraapex: New role to install APEX in databases - experimental (oravirt#473)
- oradb_manage_db: Configure sqlnet.ora, listener.ora and tnsnames.ora wirh playbook manage_sqlnet.yml (oravirt#475)
- orasw_download_patches: added support for downloading apex installation archives (oravirt#473)
- orasw_meta: changed assert for playbook manage_sqlnet.yml on RAC/Restart (oravirt#475)

Bugfixes
--------

- oraswgi_install: documentation changes for ansible-doctor make happy again (oravirt#474)

v4.10.0
=======

Release Summary
---------------

`ansible-oracle` 4.10.0 supports OL9/RHEL9 without the need to install the software
from a golden image. The exmples for beginner_patching and RAC have been fixed to
use the new pre-patching support in `oraswdb_install`.

Minor Changes
-------------

- added missing collection dependencies (oravirt#469)
- ansible-builder: moved to new base image (oravirt#470)
- ansible-lint: Update ansible-lint to 24.7.0 (oravirt#471)
- ansible-lint: fqcn[action-core] for ansible.builtin.yum due to OL7 compatibility (oravirt#471)
- antsibull-changelog: Upgrade version 0.29.0
- beginner_patching: updated example to ansible-oracle 4.x (oravirt#469)
- molecule: changes to dbfs for new dbfs-ol9 szenario (oravirt#469)
- molecule: dbfs-ol9 for RDBMS prepatch testing (oravirt#469)
- ocenv: version 2024-08-23 of ocenv environment script (oravirt#468)
- oraswdb_install: Added support for prepatching in runInstaller for 19c (oravirt#469)
- oraswdb_manage_patches: added parameter oraswdb_manage_patches_force_opatch_upgrade for applyRU in runInstaller (oravirt#469)
- tools: changed requirements_dev.txt for venv (oravirt#470)

Deprecated Features
-------------------

- End of Life for Oracle Linux 7 and RHEL7 (oravirt#466)

Bugfixes
--------

- orahost_meta: Added default for oracle_install_option_gi to limit dependency to other roles (oravirt#467)

v4.9.0
======

Release Summary
---------------

This is the 1st production release of ansible-oracle 4.x.
The RAC support was the last missing option in 4.x compared to 3.12.0.
A documentation for migration from 3.12.0 to 4.x is work in progress.

Minor Changes
-------------

- added option to disable transparent hugepages in grub (oravirt#460)
- bugfix set custom environment for executables with oracle_script_env (oravirt#458)
- global_handlers: Introduce a global handlers role (oravirt#455)
- global_handlers: Reboot handler improvements, restart_on_requirement=false, ansible-lint (oravirt#457)
- molecule: added MOLECULE_IMAGE for custom images and support for SuSE (oravirt#458)
- oracle_opatch.py needs to support configurable temp directory  (oravirt#462)
- orahost: Add a list of additional hosts to /etc/hosts (oravirt#447)
- orahost: add oracle_sysctl_file and oracle_hugepages_sysctl_file variables (oravirt#432)
- orahost: set vm.hugetlb_shm_group to oracle user GID (oravirt#461)
- orahost_logrotate: logrotate setup for oracle files should be optional (oravirt#449)
- orahost_meta: Enable calculation of several kernel parameters (oravirt#451)
- orahost_meta: added oracle_tmp_stage for hardened systems (oravirt#453)
- oraswdb_manage_patches: make role compatible with oraswgi_manage_patches (oravirt#464)
- oraswgi_install: Next refactoring of role for RAC (oravirt#464)
- set custom environment for executables with oracle_script_env (oravirt#453)

Breaking Changes / Porting Guide
--------------------------------

- CV_ASSUME_DISTID: SLES15 when ansible_os_family == 'SuSE' (oravirt#458)
- oraswgi_manage_patches: python-module xmltodict needed on ansible-controller (oravirt#464)

Bugfixes
--------

- Consider home was removed earlier, leaving REMOVED=T (oravirt#437)
- bugfix: added apply_patches_gi to some tasks with patch_before_rootsh (oravirt#464)
- default_gipass is not required if sysasmpassword and asmmonitorpassword are set (oravirt#433)
- fixed jinja spacing warning (oravirt#463)
- oracluvfy did not fail when error was detected (oravirt#464)
- orasw_meta: grid_base != oracle_base only required if role_separation=true (oravirt#439)
- oraswdb_install: Configure systemd only for Single Instance without GI/Restart (oravirt#431)
- oraswgi_install: honour deploy_ocenv setting (oravirt#443)

v4.8.0
======

Minor Changes
-------------

- oradb_manage_pdb: added missing defaults for pdbadmin_user and pdbadmin_password (oravirt#426)

v4.7.0
======

Minor Changes
-------------

- Replace run_once: _oraswgi_meta_configure_cluster with when condition (oravirt#422)
- molecule: download for current cluvfy added (oravirt#423)
- oracluvfy: New role for managing cluvfy (oravirt#423)
- orahost_meta: increase defaults for memlock limits from 0.90 to 0.91 for cluvfy (oravirt#423)
- oraswgi_install: use role oracluvfy for cluvfy during installation (oravirt#423)

Bugfixes
--------

- oradb_rman: Removed unwanted newlines from rman_backup.sh command line (oravirt#420)
- orahost: fix wrong permissions in filesystem | Create directories (oravirt#424)
- oraswdb_install: fix broken Transfer oracle installfiles to server (oravirt#421)
- reviewed entire roles/ code basis and removed unwanted indents from yaml multiline blocks (oravirt#420)

Known Issues
------------

- RAC installation with oracle_sw_copy=true not working

v4.6.0
======

Release Summary
---------------

This is the 1st Release of ansible-oracle 4.x with RAC support in expeimental stete.
The fixes from (oravirt#416) are very important for setups with more then 1 database on a host.
Please remove `oracle_db_mem_totalmb` from `oracle_databases` and set `sga_target` in `initparams` as a replacement.

Minor Changes
-------------

- RAC: Reenabled RAC-Support in 4.x (oravirt#418)
- molecule: Added 2nd database to tests (oravirt#417)
- oradb_facts: add attribute oradb_facts_ignore_unreachable to oracle_databases (oravirt#417)
- oradb_manage_db: Ignore errors during create/manage db when oradb_facts_ignore_unreachable=true (oravirt#417)
- oradb_manage_grants: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_parameters: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_pdb: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_profiles: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_redo: Disable role in RAC environments (oravirt#418)
- oradb_manage_redo: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_roles: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_services: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_statspack: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_tablespace: check state from oracledb_facts during execution (oravirt#417)
- oradb_manage_users: check state from oracledb_facts during execution (oravirt#417)
- orahost_ssh: Role rewritten with modern ansible modules (oravirt#418)
- orasw_download_patches: Download OPatch for GI/Restart (oravirt#415)

Breaking Changes / Porting Guide
--------------------------------

- oradb_manage_db: move echo for usage of ocenv from .bashrc to .bash_profile (oravirt#418)
- orasw_meta: added assert for oracle_db_mem_totalmb in oracle_databases (oravirt#414)
- orasw_meta: added variable orasw_meta_cluster_hostgroup for RAC (oravirt#418)
- orasw_meta: assert that cdb from oracle_pdbs is in oracle_databases (oravirt#417)

Bugfixes
--------

- global: removed redundant flatten(levels=1) filter on oracle_database/oracle_pdbs (oravirt#416)
- global: replaced `match` filter fith `equalto` to prevent partial matches where not wanted (oravirt#416)
- oradb_facts: Loop gathered facts only for first database from oracle_databases (oravirt#416)
- oradb_facts: Prevent re-using results from previous loop run when ignore_errors set to true (oravirt#416)
- oradb_manage_redo: Loop processed only first database from oracle_databases (oravirt#416)
- oradb_manage_statspack: Loops processed only first database/pdb from oracle_databases/oracle_pdbs (oravirt#416)
- oradb_rman: Loops processed only first database from oracle_databases (oravirt#416)
- orasw_meta_internal: replaced all odb[0]/opdb[0] with _odb_loop_helper/_opdb_loop_helper (oravirt#416)

v4.5.0
======

Minor Changes
-------------

- Change Shebang to /usr/bin/env bash (oravirt#409)
- Documentation updates (oravirt#389)
- build(deps): bump ansible-core from 2.15.8 to 2.15.9 in /tools/dev (oravirt#408)
- minor fixes for role separation in Oracle Restart (oravirt#409)
- oradb_manage_db: Assert SYS password in inventory before dbca (oravirt#409)

Breaking Changes / Porting Guide
--------------------------------

- Removed oracle_password - use default_gipass as replacement (oravirt#409)
- orahost: Removed fixed password for oracle and grid from defaults (oravirt#409)
- orasw_meta: Removed default passwords from default_dbpass and dbpasswords (oravirt#409)
- oraswgi_install: Removed default password from default_gipass (oravirt#409)

Security Fixes
--------------

- orahost: Removed fixed password for oracle and grid from defaults (oravirt#409)
- orasw_meta: Removed default passwords from default_dbpass and dbpasswords (oravirt#409)
- oraswgi_install: Removed default password from default_gipass (oravirt#409)

Bugfixes
--------

- orahost: fix for broken configure_hugepages=false (oravirt#412)
- orasw_meta: Removed warning from ansible (oravirt#409)

v4.4.2
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!

Bugfixes
--------

- oradb_manage_wallet: bugfix for broken Remove DB-Credentials (oravirt#406)
- oradb_manage_wallet: bugfix for broken oracle_wallet_password (oravirt#406)
- oraswdb_manage_patches: refresh opatch lsinv after opatch rollback (oravirt#405)

v4.4.1
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!

Bugfixes
--------

- oradb_manage_wallet: fixed wrong dbpassword assignment, added debug option for password (oravirt#404)

v4.4.0
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!

Minor Changes
-------------

- ansible-doctor: Update to 4.0.1 (oravirt#397)
- oradb_manage_db: Added support for aliasnames for Oracle Wallet (oravirt#400)
- oradb_manage_db: allow multiline values for keys in sqlnet_ansible.ora (oravirt#400)
- oradb_manage_wallet: New role for managing Oracle Wallets (oravirt#400)
- pre-commit: Update multiple hooks (oravirt#397)

Security Fixes
--------------

- dependabo: Update ansible-core in dev-tools (oravirt#398)
- dependabo: bump ansible from 6.7.0 to 8.5.0 in /tools/ansible (oravirt#395)
- dependabo: bump tj-actions/changed-files from 31 to 41 in /.github/workflows (oravirt#396)
- oradb_manage_db: Remove visible password for sys, system and dbsnmp from dbca responsefile for 12.2+ (oravirt#401)

v4.3.0
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!

Minor Changes
-------------

- ansible-lint v6.22.1 (oravirt#392)
- molecule: add tnsname configuration to shared inventory (oravirt#388)
- oradb_facts: Skip oracledb_facts when db not reachable (oravirt#387)

Bugfixes
--------

- common: install lsof for all RHEL/OL distributions (oravirt#391)
- oradb_manage_db: Bugfix for undefined variable listener_home_config (oravirt#386)
- orahost: Fix warning conditional statements should not include jinja2 templating (oravirt#391)

v4.2.0
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!

Major Changes
-------------

- Ansible 7 (2.14) is new minimal version in ansible-oracle 4.x (oravirt#384)

Minor Changes
-------------

- example: added oracle_listeners_config and listener_installed due to new asserts in 4.0 (oravirt#384)
- experimental support for OracleLinux 9 (oravirt#384)
- molecule: Switch to RU 19.21 (oravirt#384)

Breaking Changes / Porting Guide
--------------------------------

- Ansible 7 (2.14) is new minimal version in ansible-oracle 4.x (oravirt#384)
- oraswdb_golden_image: Fixed wrong varible names oraswdb_golen_* to oraswdb_golden_* from breaking change oravirt#383 (oravirt#384)
- oraswgi_golden_image: Fixed wrong varible names oraswgi_golen_* to oraswgi_golden_* from breaking change oravirt#383 (oravirt#384)

Bugfixes
--------

- oraswdb_manage_patches: bugfix for wrong stage directory when oracle_sw_copy=true (oravirt#384)

v4.1.0
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!

Minor Changes
-------------

- ansible-lint V6.20.3 (oravirt#383)
- molecule: new stage download to prepare dbfs stage (oravirt#383)
- molecule: new stage golden to create golden images (oravirt#383)
- oiraswgi: Added Support for gridSetup.sh -applyRU for 19c and 21c (oravirt#383)
- oraasm_manage_diskgroups: Refactoring and bugfixes for 4.0 (oravirt#383)
- oracle_opatch: replace sqlplus -V with oraversion for newer releases (oravirt#383)
- oraswdb_golen_image: Rename created archive to fixed name (oravirt#383)
- oraswgi_golen_image: Rename created archive to fixed name (oravirt#383)

Breaking Changes / Porting Guide
--------------------------------

- oraswdb_golen_image: New variable oraswdb_golen_image_create: false (oravirt#383)
- oraswgi_golen_image: New variable oraswgi_golen_image_create: false (oravirt#383)

Bugfixes
--------

- Bugfix for state=absent in oracle_databases with CDB (oravirt#383)
- molecule: Use shared inventory with download scenario (oravirt#383)
- oracle_opatch: fix wrong rolling parameter definition, fix broken opatch opatchauto rollback (oravirt#383)
- oradb_datapatch: allow execution of role with empty oracle_databases and oracle_pdbs (oravirt#383)
- oradb_manage_db: Regather oradb_facts after database change (oravirt#383)
- oradb_manage_statspack: Bugfix for nonCDB setups (oravirt#383)
- orahost: Do not set NOZEROCONF on SuSE platform (oravirt#383)

v4.0.0
======

Release Summary
---------------

This is a BETA Release of ansible-oracle. Do not use it in production environments!
The release introduce https://github.com/thegeeklab/ansible-doctor[ansible-doctor] for documentation with annotations.
Please make sure, that furture Pull-Requests have updated README.md included, when changes in annotations are included.
A new github Action will check for it.
Some variable defaults have been changed.

Minor Changes
-------------

- Added molecule to improve testing in development (oravirt#318)
- Renamed all playbooks for collection compatibility and added symbolic links (oravirt#318)
- ansible-lint 6.17.0 (oravirt#318)
- antsibull-changelog: Update to 0.23.0 in development tools (oravirt#318)
- common: ansible-doctor (oravirt#318)
- cxoracle: ansible-doctor (oravirt#318)
- cxoracle: removed pip installation for Python2 (oravirt#318)
- github Action ansible-doctor (oravirt#318)
- github Action changelog filecheck only during pull requests (oravirt#318)
- molecule: helper for easier development in ansible-oracle (oravirt#318)
- oradb_facts: new role for oracle_fact.py module (oravirt#318)
- oradb_manage_db: sys and system passwords could be different in database creation (oravirt#318)
- oradb_manage_profiles: added missing option mode for normal/sysdba connections (oravirt#318)
- oradb_manage_statspack: major code refactoring (oravirt#318)
- oradb_manage_tablespace: added missing option mode for normal/sysdba connections (oravirt#318)
- orahost: 1st test of ansible-doctor (oravirt#318)
- orahost: refactoring role (oravirt#318)
- orahost_cron: ansible-doctor (oravirt#318)
- orahost_logrotate: ansible-doctor (oravirt#318)
- orahost_meta: ansible-doctor (oravirt#318)
- orahost_meta: moved some variables from orahost into orahost_meta (oravirt#318)
- oraswdb_install: optimize installations with oracle_sw_copy (oravirt#318)
- oraswgi_instal: replace .profile_grid with ocenv (oravirt#318)
- oraswgi_meta: added asserts for inventory variables ()
- pre-commit: added ShellCheck Hook (oravirt#318)
- python-venv: helper for easier development in ansible-oracle (oravirt#318)
- replaced ansible_hostname with oracle_hostname in oracle manage roles (oravirt#318)
- rman_backup.sh: make scripte shellcheck happy (oravirt#318)

Breaking Changes / Porting Guide
--------------------------------

- INCOMPATIBLE CHANGE: Please replace configure_cluster with oracle_install_option_gi (oravirt#318)
- change configure_cluster to _oraswgi_meta_configure_cluster (oravirt#318)
- changed variable defaults for (oravirt#318)
- dbhome-conversion tool removed (oravirt#318)
- oracle_acfs: Rename module to disable it due to broken code (oravirt#318)
- oracle_asmdg: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_asmvol: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_awr: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_datapatch: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_directory: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_facts: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_gi_facts: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_grants: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_jobclass: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_jobs: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_jobschedule: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_jobwindow: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_ldapuser: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_parameter: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_pdb: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_privs: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_profile: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_redo: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_role: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_rsrc_consgroup: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_services: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_sql: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_sqldba: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_stat_prefs: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_tablespace: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- oracle_user: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#318)
- orahost: removed default values for host_fs_layout (oravirt#318)

Removed Features (previously deprecated)
----------------------------------------

- Remove old desupported playbooks from playbooks/desupported (oravirt#318)
- Removed duplicate role oraswgi_opatch. Use oraswgi_manage_patches (oravirt#318)
- Removed inventory folder, comes back in example at later time (oravirt#318)
- removed role oraemagent_install (oravirt#318)

Known Issues
------------

- Oracle Restart is not fully tested at the moment (oravirt#318)
- RAC support not availible in this release (oravirt#318)

v3.12.0
=======

Minor Changes
-------------

- oradb_facts: add missing attributes collected by oracle_facts module (oravirt#375)

Security Fixes
--------------

- oracle_awr: added no_log attribute to password fields (oravirt#375)
- oracle_facts: added no_log attribute to password fields (oravirt#375)
- oracle_job: added no_log attribute to password fields (oravirt#375)
- oracle_jobclass: added no_log attribute to password fields (oravirt#375)
- oracle_jobschedule: added no_log attribute to password fields (oravirt#375)
- oracle_jobwindow: added no_log attribute to password fields (oravirt#375)
- oracle_ldapuser: added no_log attribute to password fields (oravirt#375)
- oracle_rsrc_consgroup: added no_log attribute to password fields (oravirt#375)

Bugfixes
--------

- oradb_rman: better handle rman_jobs with state: absent (oravirt#374)

v3.11.0
=======

Minor Changes
-------------

- new vagrantbox example beginner_patching (oravirt#370)
- oradb_rman: added option state for cronjobs, disabled is optional now (oravirt#369)

Bugfixes
--------

- oradb_manage_db: bugfix for wrong IFILE path in tnsnames.ora and sqlnet.ora when readonly ORACLE_HOME is used (oravirt#371)

v3.10.1
=======

Bugfixes
--------

- oradb_facts: Bugfix for missing default variable definitions (oravirt#366)
- oradb_manage_grant: Bugfix for broken grant on pdb with db_domain (oravirt#365)

v3.10.0
=======

Minor Changes
-------------

- oracle_sqldba: refactoring code, make it usable for ansible-doc, Python3 usable only (oravirt#361)
- oradb_manage_db: create _DGMGRL SID in listener.ora for EE only (oravirt#359)

Bugfixes
--------

- Bugfix for missing Listener autostart and readonly Homes in systemd (oravirt#358)
- oracle_sqldba: Bugfix for Python3 (oravirt#361)
- oraswdb_install: shellchecker for manage_oracle_rdbms_procs.sh (oravirt#358)
- pre-commit: Bugfix for known issue from ansible-oracle 3.8.0 (oravirt#383)

v3.9.0
======

Release Summary
---------------

This release adds support for db_domain in init.ora for nonCDB and CDB. Read (oravirt#356) for requirements and notes.

Minor Changes
-------------

- Added support for db_domain in init.ora (oravirt#356)
- oradb_facts: Backported role from dev release (oravirt#356)
- oraswdb_install: fixed wrong creates in curl.yml (oravirt#354)

Bugfixes
--------

- oraswdb_install: enable CV_ASSUME_DISTID=OL7 for Golden-Image on OL/RHEL8 (oravirt#355)

v3.8.1
======

Bugfixes
--------

- oraswdb_install: bugfix for imagename in db_homes_config  (oravirt#352)

v3.8.0
======

Release Summary
---------------

This is ansible-oracle 3.8.0.
The target database server must have Python3 installaed which is automatically done with role `orahost`.
It is mandatory for the module `oracle_db` which is used in `oradb_manage_db`.

Minor Changes
-------------

- Add restart possibility after scope=spfile init parameters change (oravirt#342)
- Add state=restarted to oracle_db (oravirt#342)
- Remove deprecation warnings for community.general 7.x (oravirt#339)
- black: adding black to pre-commit (oravirt#343)
- flake8: adding flake8 to pre-commit (oravirt#343)
- github Actions: adding Action for black and flake8 (oravirt#343)
- ocenv: version 2023-06-06 of ocenv environment script (oravirt#347)
- oracle_db: Refactoring code for flake8 (oravirt#342)

Breaking Changes / Porting Guide
--------------------------------

- cx_Oracle: requires Python3 installed on target system  (oravirt#342)
- cx_oracle: Added installation of cx_Oracle for Python3 (oravirt#346)
- oradb_manage_db: requires Python3 installed on target system  (oravirt#342)

Deprecated Features
-------------------

- modules: all modules will loose support for Python2 in ansible-oracle 4.0.0  (oravirt#346)

Bugfixes
--------

- common: removed assert for python due to oravirt#346 (oravirt#350)
- orasw_download_patches: added missing assert for oracle_sw_source_local (oravirt#340)
- oraswdb_install: changed oracle_databases to db_homes_installed for installation source of ORACLE_HOMEs (oravirt#348)
- oraswdb_manage_patches: Bugfix for missing opatch or opatchauto in db_homs_config dict (oravirt#349)
- pre-commit: added antsibull-changelog-lint (oravirt#345)
- pre-commit: moved ansible-lint to end of pre-commit hooks (oravirt#344)

Known Issues
------------

- pre-commit: Ignore [WARNING] The 'rev' field of repo 'https://github.com/ansible-community/antsibull-changelog.git'. This will be fixed with next antsibull-changelog release.

v3.7.0
======

Minor Changes
-------------

- added task to REGISTER DATABASE in Rman Catalog (oravirt#336)
- ansible-lint: Update to 6.14.4 (oravirt#329)
- orahost: improve oracle os packages selection for Suse (oravirt#337)

v3.6.0
======

Minor Changes
-------------

- added new orasw_download_patches role (oravirt#332)
- common: assert python2 interpreter on OL/RHEL7 (oravirt#330)
- github action: deploy collection (oravirt#324)
- github action: stale issues & PRs  (oravirt#326)
- orasw_meta: added central assert tasks for ansible-oracle (oravirt#325)

v3.5.1
======

Bugfixes
--------

- oradb_manage_tablespace: added missing defaults for password (oravirt#323)

v3.5.0
======

Release Summary
---------------

This is a small monthly release of ansible-oracle.

Minor Changes
-------------

- add configuration variables for pam_limits to orahost (oravirt#317)

Deprecated Features
-------------------

- Removal of deprecated directory /inventory from repository with next release.

v3.4.0
======

Minor Changes
-------------

- oradb_manage_db: customize ocenv initialization in bashrc (oravirt#310)

Bugfixes
--------

- Fixed oracle packages for SLES 15.3 (oravirt#311)

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
