# ansible-oracle

* Automated installation of
   * Single Instance Oracle databases without and with Oracle Restart
   * Oracle Restart (Grid Infrastructure for a Standalone Server) with ASM
   * Grid Infrastructure for a Cluster, RAC and RAC One Node databases: the roles contain tasks for it,
     but they are not tested and will probably not work
* Start with one or more clean Linux machine(s), end up with a fully configured Oracle database system

# Documentation

## Features

1. Full list of features of ansible-oracle <https://github.com/oravirt/ansible-oracle/blob/master/doc/featurelist.adoc>
1. More details <https://github.com/oravirt/ansible-oracle>


## Getting Started

1. Vagrant setup on Windows <https://github.com/oravirt/ansible-oracle/blob/master/doc/vagrant.adoc>
1. Beginner <https://github.com/oravirt/ansible-oracle/blob/master/doc/guides/beginner.adoc>
1. Data Guard <https://github.com/oravirt/ansible-oracle/blob/master/doc/guides/dataguard.adoc>

### Next Steps

1. [APEX and ORDS in `ansible-oracle`](doc/guides/apex_ords.adoc)
2. [Oracle AutoUpgrade in `ansible-oracle`](doc/guides/autoupgrade.adoc)
3. [RMAN Backups with `oradb_rman`](doc/guides/rman.adoc)
4. [Upgrade of PDBs with AutoUpgrade (Unplug/Plug)](doc/guides/autoupgrade_upgrade.adoc)
5. [How to develop in ansible-oracle](doc/development.adoc)
6. [List of roles in ansible-oracle](doc/roles.adoc)
7. [Breaking Changes - Upgrade Guide](doc/guides/breaking_changes.adoc)


## Pre-requisites

* ansible-core 2.16 - 2.19

  `ansible-oracle` 4.x supports ansible-core 2.14 - 2.18 only
* Oracle Linux (or any RHEL-based Linux System) >= 8
* Oracle Database 26ai, 19c
* Oracle Restart 19c, 26ai
* Oracle Grid Infrastructure for a Cluster: not tested
