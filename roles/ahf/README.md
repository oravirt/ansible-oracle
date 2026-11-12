# ahf

_Experimental_: the role is under development. Breaking changes can happen at any time
and are not always documented.

Install and configure Oracle Autonomous Health Framework (AHF)
on database servers.

The role installs AHF from the installation media in the software repository
(`AHF-LINUX_v<version>.zip` or patch 30166242 downloaded with AutoUpgrade),
upgrades an existing installation when a newer version is found,
activates or deactivates the components of AHF and registers the server
as client of AHF Fleet Insights (role `ahf_fleet_insights`).

| Task file | Description |
| --- | --- |
| `main.yml` | Install, configure and register (or uninstall with `ahf_state: absent`) |
| `assert.yml` | Packages, check variables, Perl and owner of `ahf_loc` / `ahf_data_dir` |
| `install.yml` | Install or upgrade AHF |
| `configure.yml` | Components and settings of TFA / Compliance (orachk) |
| `fleet_insights_client.yml` | Register/deregister AHF Fleet Insights |
| `uninstall.yml` | Uninstall AHF |

See `doc/guides/ahf.adoc` for decisions about the installation.

## Table of contents

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [ahf_ansible_state_file](#ahf_ansible_state_file)
  - [ahf_command_timeout](#ahf_command_timeout)
  - [ahf_compliance_autostart](#ahf_compliance_autostart)
  - [ahf_compliance_settings](#ahf_compliance_settings)
  - [ahf_data_dir](#ahf_data_dir)
  - [ahf_data_dir_min_free_mb](#ahf_data_dir_min_free_mb)
  - [ahf_fleet_insights_client](#ahf_fleet_insights_client)
  - [ahf_fleet_insights_force_register](#ahf_fleet_insights_force_register)
  - [ahf_fleet_insights_os_user](#ahf_fleet_insights_os_user)
  - [ahf_fleet_insights_password](#ahf_fleet_insights_password)
  - [ahf_fleet_insights_public_cert](#ahf_fleet_insights_public_cert)
  - [ahf_fleet_insights_url](#ahf_fleet_insights_url)
  - [ahf_fleet_insights_user](#ahf_fleet_insights_user)
  - [ahf_install_mode](#ahf_install_mode)
  - [ahf_installer_archive](#ahf_installer_archive)
  - [ahf_installer_patterns](#ahf_installer_patterns)
  - [ahf_installer_version](#ahf_installer_version)
  - [ahf_loc](#ahf_loc)
  - [ahf_manage_packages](#ahf_manage_packages)
  - [ahf_packages](#ahf_packages)
  - [ahf_perl_home](#ahf_perl_home)
  - [ahf_properties](#ahf_properties)
  - [ahf_settings_force](#ahf_settings_force)
  - [ahf_setup_extra_args](#ahf_setup_extra_args)
  - [ahf_stage_dir](#ahf_stage_dir)
  - [ahf_state](#ahf_state)
  - [ahf_tfa_directories](#ahf_tfa_directories)
  - [ahf_tfa_enabled](#ahf_tfa_enabled)
  - [ahf_tfa_settings](#ahf_tfa_settings)
  - [ahf_uninstall_delete_repo](#ahf_uninstall_delete_repo)
  - [ahf_upgrade](#ahf_upgrade)
  - [ahf_verify_signature](#ahf_verify_signature)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.16.0`

## Default Variables

### ahf_ansible_state_file

File with the settings applied by the role. Used to detect changes in
`ahf_tfa_settings`, `ahf_compliance_settings` and the registration of AHF Fleet Insights.

#### Default value

```YAML
ahf_ansible_state_file: '{{ ahf_loc }}/oracle.ahf.ansible.json'
```

### ahf_command_timeout

Timeout in seconds for interactive commands (registration of AHF Fleet Insights).

#### Default value

```YAML
ahf_command_timeout: 300
```

### ahf_compliance_autostart

Start the scheduler for Compliance checks (`ahfctl startahf -compliance`).

Default schedule of Oracle (autorun IDs, `orachk -get all -id all`):

| Autorun ID | AUTORUN_SCHEDULE | Checks | COLLECTION_RETENTION |
| --- | --- | --- | --- |
| `autostart_client_oratier1` | `3 2 * * 1,2,3,4,5,6` | profile `oratier1` | 7 days |
| `autostart_client` | `3 3 * * 0` | all | 14 days |

Change it with `ahf_compliance_settings`.

#### Default value

```YAML
ahf_compliance_autostart: false
```

### ahf_compliance_settings

Requires `ahf_compliance_autostart: true`: the autoruns exist only with a running
Compliance scheduler (`ahfctl stopahf -compliance` removes them).

Settings of the Compliance autoruns per autorun ID - executed as
`orachk -set "<key>=<value>;..." -id <autorun ID>`.
Same behavior as `ahf_tfa_settings`, the settings of an ID are compared as a whole.

The settings are stored per autorun ID by AHF (e.g. `AUTORUN_SCHEDULE`, `AUTORUN_FLAGS`,
`COLLECTION_RETENTION`). Show them with `orachk -get all -id all`.
The ID is used with or without the prefix `orachk.` shown by `orachk -get`.

`orachk -set` requires `AUTORUN_SCHEDULE` (cron expression with 5 fields) in every call.
The role adds the current value, when it is not part of the settings.
A new autorun ID needs `AUTORUN_SCHEDULE` and `AUTORUN_FLAGS`.
Values must not contain `;`.

#### Default value

```YAML
ahf_compliance_settings: {}
```

#### Example usage

```YAML
ahf_compliance_settings:
  autostart_client_oratier1:
    AUTORUN_SCHEDULE: "3 2 * * 1-6"
    COLLECTION_RETENTION: 7
  autostart_client:
    COLLECTION_RETENTION: 30
```

### ahf_data_dir

Parent directory of the AHF repository (collections, Insights reports, Compliance results).
`ahf_setup` creates `oracle.ahf/data` below this directory.

Oracle requires at least 5 GB, 10 GB are recommended.

For `ahf_install_mode: root` all directories in this path must be owned by `root`
(`ahf_setup` fails with `AHF-00014`). A directory below `oracle_base` or a mount point
owned by `oracle_user` (e.g. `/u01`) is not possible.
The default is `ahf_loc` (`/opt/oracle.ahf/data`), the default location of Oracle.
Use a filesystem of its own for `/opt/oracle.ahf` with enough space.

#### Default value

```YAML
ahf_data_dir: "{{ '/opt' if ahf_install_mode == 'root' else oracle_base }}"
```

### ahf_data_dir_min_free_mb

Minimum free space in MB in `ahf_data_dir` for a new installation.

#### Default value

```YAML
ahf_data_dir_min_free_mb: 5120
```

### ahf_fleet_insights_client

Register the host as client of AHF Fleet Insights (`ahf configuration set --type fleet-insights`).
The client uploads Compliance results and TFA collections automatically.

`false` deregisters a client, which was registered by this role.

Requires AHF 24.9 or newer and `ahf_install_mode: root`.
Oracle documents the registration for clusters - check single instance environments.

#### Default value

```YAML
ahf_fleet_insights_client: false
```

### ahf_fleet_insights_force_register

Register again, even when URL and user are unchanged - e.g. after a password change.

#### Default value

```YAML
ahf_fleet_insights_force_register: false
```

### ahf_fleet_insights_os_user

OS user for the REST access of Fleet Insights (`ahf configuration set --os-user`).
Without it the registration reports `AHF-02119: ... the REST Agent was not started`
(no local AHF user with the role `rest-server`).
Empty: `--os-user` is not used.

#### Default value

```YAML
ahf_fleet_insights_os_user: '{{ oracle_user }}'
```

### ahf_fleet_insights_password

Password of `ahf_fleet_insights_user`. Use Ansible Vault.

#### Default value

```YAML
ahf_fleet_insights_password: ''
```

### ahf_fleet_insights_public_cert

Public certificate (PEM) of AHF Fleet Insights for the registration
(`ahf configuration set --public-cert`).
Needed for the self-signed certificate created by the installer of Fleet Insights,
otherwise the registration fails with `CERTIFICATE_VERIFY_FAILED`.
Role `ahf_fleet_insights` provides it as fact `ahf_fi_public_cert` or as file (`ahf_fi_public_cert_fetch`).

#### Default value

```YAML
ahf_fleet_insights_public_cert: ''
```

#### Example usage

```YAML
ahf_fleet_insights_public_cert: "{{ lookup('ansible.builtin.file', inventory_dir + '/files/ahffi_cert.pem') }}"
```

### ahf_fleet_insights_url

Registration URL of AHF Fleet Insights.
Shown by `ahffi info` on the Fleet Insights server - without `/ahfservice`.

#### Default value

```YAML
ahf_fleet_insights_url: ''
```

#### Example usage

```YAML
ahf_fleet_insights_url: https://ahffi.example.com:5005
```

### ahf_fleet_insights_user

Generic registration user of AHF Fleet Insights.

#### Default value

```YAML
ahf_fleet_insights_user: ''
```

### ahf_install_mode

`root` (default): Installation as `root` with TFA daemon (systemd),
automatic diagnostic collections, Compliance scheduler and
AHF Fleet Insights client. Recommended by Oracle.

`extract`: Installation as `oracle_user` with `ahf_setup -extract`.
No daemon, no automatic collections, only on-demand usage of
`orachk` / `tfactl` as `oracle_user`. Settings for TFA and AHF Fleet Insights
are ignored.

#### Default value

```YAML
ahf_install_mode: root
```

### ahf_installer_archive

Filename of the AHF installation media in the software repository.

Empty (default): the newest file (modification time) matching `ahf_installer_patterns`
is used from `oracle_sw_source_local` on the Ansible controller
(`is_sw_source_local: true`, `oracle_sw_copy: true`) or from `oracle_stage_remote`
on the target host (`oracle_sw_copy: false`).
Must be set for `is_sw_source_local: false` (`oracle_sw_source_www`).

#### Default value

```YAML
ahf_installer_archive: ''
```

#### Example usage

```YAML
ahf_installer_archive: AHF-LINUX_v26.10.0.zip
```

### ahf_installer_patterns

Filename patterns for the search of the installation media (`ahf_installer_archive: ""`).

`AHF-LINUX_v*.zip` is the name of the media in My Oracle Support (Doc ID 2550798.1).
`p30166242_*.zip` is the patch "DOWNLOAD LATEST AHF" - e.g. downloaded by
AutoUpgrade with `AHF` in `autoupgrade_download_patches`.

#### Default value

```YAML
ahf_installer_patterns:
  - AHF-LINUX_v*.zip
  - p30166242_*.zip
```

### ahf_installer_version

Version of the installation media, e.g. `26.10.0`.

Normally the version is taken from the filename `AHF-LINUX_v<version>.zip`
(also inside of patch 30166242). Set it, when the filename does not contain the version.

#### Default value

```YAML
ahf_installer_version: ''
```

### ahf_loc

Parent directory of the AHF installation.
`ahf_setup` creates `oracle.ahf` below this directory.

For `ahf_install_mode: root` all directories in this path must be owned by `root`,
because the AHF binaries are executed by `root`. A directory below `oracle_base`
is owned by `oracle_user`, who could replace the binaries.
This is checked by the role.

#### Default value

```YAML
ahf_loc: "{{ '/opt' if ahf_install_mode == 'root' else oracle_base }}"
```

### ahf_manage_packages

Install `ahf_packages` (`ahf_install_mode: root` only).

#### Default value

```YAML
ahf_manage_packages: true
```

### ahf_packages

Packages for AHF. The package `perl` contains all Perl modules required by AHF
(e.g. `File::Copy`, `FindBin`, `Math::BigInt`, `Net::Ping`, `AHF-00074`).
`perl-interpreter` alone is not enough.

#### Default value

```YAML
ahf_packages:
  - perl
  - openssl
  - unzip
```

### ahf_perl_home

Perl for AHF (`ahf_setup -perlhome`), `<ahf_perl_home>/bin/perl` is used.

`ahf_install_mode: root` requires a Perl owned by `root` (`AHF-00026`).
Without `-perlhome`, `ahf_setup` uses the Perl of the Grid Infrastructure home on hosts
with Oracle Restart/RAC, which is owned by the GI owner => the default is the Perl of the OS.
Empty: `ahf_setup` selects the Perl.

#### Default value

```YAML
ahf_perl_home: /usr
```

### ahf_properties

AHF properties - executed as `ahf configuration set --property <key> --value <value>`
(`ahf_install_mode: root` only). Same behavior as `ahf_tfa_settings`.

Show the supported properties with `ahf configuration get --help` and the current value
with `ahf configuration get --property <key>`. Properties of AHF 26.10:

| Property | Default | Description |
| --- | --- | --- |
| `ahf.fleet-insights.upload-only-minimal-files` | `true` | Upload only minimal files to Fleet Insights (not documented by Oracle) |
| `ahf.collectors.alert-history` | `on` | Alert History, only for ASM (dismount, offline, mount) |
| `ahf.collectors.enhanced_os_metrics` | `on` | Enhanced OS metrics |
| `ahf.insights.max-collection-interval` | `4` | not documented by Oracle |
| `ahf.compliance.excluded-check-ids` | | Check IDs excluded from the Compliance checks |

#### Default value

```YAML
ahf_properties: {}
```

#### Example usage

```YAML
ahf_properties:
  ahf.fleet-insights.upload-only-minimal-files: "false"
  ahf.collectors.alert-history: "on"
```

### ahf_settings_force

Execute all settings and component states, even when they are unchanged
since the last run of the role.

#### Default value

```YAML
ahf_settings_force: false
```

### ahf_setup_extra_args

Additional parameters for `ahf_setup`.

`-local` is always added for `ahf_install_mode: root`.
AHF is installed on each host of the play. Use `tfactl syncnodes` for clusters.

#### Default value

```YAML
ahf_setup_extra_args: []
```

#### Example usage

```YAML
ahf_setup_extra_args:
  - -tmp_loc
  - /var/tmp
```

### ahf_stage_dir

Directory on the target host for the extraction of the installation media.
The directory is removed after the installation.

#### Default value

```YAML
ahf_stage_dir: '{{ oracle_stage }}/ahf'
```

### ahf_state

`present`: install, upgrade and configure AHF.

`absent`: uninstall AHF (`ahfctl uninstall -silent`).

#### Default value

```YAML
ahf_state: present
```

### ahf_tfa_directories

Additional directories for TFA (`tfactl directory add`), `ahf_install_mode: root` only.

TFA discovers the directories of GI, ASM, listener and databases (`diag_dest`) automatically
(`tfactl print directories`). Add directories, which are not discovered, e.g. audit files
or a log directory of an application.

| Attribute | Default | Description |
| --- | --- | --- |
| `path` | | directory (mandatory) |
| `component` | `RDBMS` | `RDBMS`, `CRS`, `ASM`, `INSTALL`, `OS`, `CFGTOOLS`, `TNS`, `DBWLM`, `ACFS`, `IPS` |
| `database` / `instance` | | database and instance for `component: RDBMS` |
| `public` | `true` | collection by all users, which can run `tfactl diagcollect` |
| `collection` | `exclusions` | `exclusions`, `noexclusions` (time restrictions only) or `collectall` |
| `state` | `present` | `absent` removes a directory added by the role |

Directories added by the role are removed, when they are removed from the list.

#### Default value

```YAML
ahf_tfa_directories: []
```

#### Example usage

```YAML
ahf_tfa_directories:
  - path: /u01/app/oracle/admin/DB1/adump
    component: RDBMS
    database: db1
    instance: DB1
    collection: noexclusions
```

### ahf_tfa_enabled

Start and enable the TFA daemon (`ahf_install_mode: root` only).

`false` stops the daemon and disables the automatic start.
The software stays installed and can be used on-demand.

#### Default value

```YAML
ahf_tfa_enabled: true
```

### ahf_tfa_settings

Settings for TFA - executed as `tfactl set <key>=<value>`
(`ahf_install_mode: root` only).

A setting is executed only, when it differs from the last run of the role.
The applied settings are stored in `ahf_ansible_state_file`.
Manual changes are not detected - use `ahf_settings_force: true`.

#### Default value

```YAML
ahf_tfa_settings: {}
```

#### Example usage

```YAML
ahf_tfa_settings:
  autodiagcollect: "OFF"
  reposizeMB: 10240
  minfileagetopurge: 48
  ahfnotificationaddress: dba@example.com
```

### ahf_uninstall_delete_repo

Delete the repository in `ahf_data_dir` during the uninstall (`-deleterepo`).

#### Default value

```YAML
ahf_uninstall_delete_repo: false
```

### ahf_upgrade

Upgrade an existing installation, when the installation media has a newer version.

#### Default value

```YAML
ahf_upgrade: true
```

### ahf_verify_signature

Verify the signature of `ahf_setup` with `openssl` and the public key
from the installation media before the installation.

#### Default value

```YAML
ahf_verify_signature: true
```

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
