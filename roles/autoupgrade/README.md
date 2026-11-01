# autoupgrade

Manage Oracle AutoUpgrade.

The role has no `tasks/main.yml`.
Each area of AutoUpgrade has its own task file, which must be called with `tasks_from`:

| Task file | Description |
| --- | --- |
| `assert.yml` | Check variables and Java |
| `install.yml` | Install `autoupgrade.jar` into `autoupgrade_home` |
| `download_patches.yml` | Download patches from My Oracle Support with AutoUpgrade |
| `upgrade_analyze.yml` | Analyze phase for the Unplug/Plug upgrade of PDBs (`oracle_pdbs`): AutoUpgrade `analyze` |
| `upgrade_fixups.yml` | Fixups phase: AutoUpgrade `fixups` in the source CDB/PDBs |
| `upgrade_deploy.yml` | Unplug/Plug upgrade of PDBs: analyze phase + AutoUpgrade `deploy` |

See `doc/guides/autoupgrade_upgrade.adoc` for the upgrade of PDBs.

## Table of contents

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [autoupgrade_download_dir](#autoupgrade_download_dir)
  - [autoupgrade_download_filename_regex](#autoupgrade_download_filename_regex)
  - [autoupgrade_download_gold_image](#autoupgrade_download_gold_image)
  - [autoupgrade_download_gold_image_latest](#autoupgrade_download_gold_image_latest)
  - [autoupgrade_download_gold_image_prefix](#autoupgrade_download_gold_image_prefix)
  - [autoupgrade_download_gold_image_rename](#autoupgrade_download_gold_image_rename)
  - [autoupgrade_download_latest](#autoupgrade_download_latest)
  - [autoupgrade_download_patches](#autoupgrade_download_patches)
  - [autoupgrade_download_platform](#autoupgrade_download_platform)
  - [autoupgrade_download_supported_releases](#autoupgrade_download_supported_releases)
  - [autoupgrade_download_use_oracle_sw_patches](#autoupgrade_download_use_oracle_sw_patches)
  - [autoupgrade_force_update](#autoupgrade_force_update)
  - [autoupgrade_home](#autoupgrade_home)
  - [autoupgrade_jar](#autoupgrade_jar)
  - [autoupgrade_jar_filesource](#autoupgrade_jar_filesource)
  - [autoupgrade_jar_url](#autoupgrade_jar_url)
  - [autoupgrade_java_home](#autoupgrade_java_home)
  - [autoupgrade_java_options](#autoupgrade_java_options)
  - [autoupgrade_keystore](#autoupgrade_keystore)
  - [autoupgrade_keystore_fail_on_invalid_credentials](#autoupgrade_keystore_fail_on_invalid_credentials)
  - [autoupgrade_keystore_manage](#autoupgrade_keystore_manage)
  - [autoupgrade_keystore_no_log](#autoupgrade_keystore_no_log)
  - [autoupgrade_keystore_password](#autoupgrade_keystore_password)
  - [autoupgrade_keystore_recreate](#autoupgrade_keystore_recreate)
  - [autoupgrade_keystore_timeout](#autoupgrade_keystore_timeout)
  - [autoupgrade_local_home](#autoupgrade_local_home)
  - [autoupgrade_local_java_home](#autoupgrade_local_java_home)
  - [autoupgrade_log_dir](#autoupgrade_log_dir)
  - [autoupgrade_proxy_check](#autoupgrade_proxy_check)
  - [autoupgrade_proxy_check_timeout](#autoupgrade_proxy_check_timeout)
  - [autoupgrade_proxy_check_urls](#autoupgrade_proxy_check_urls)
  - [autoupgrade_proxy_password](#autoupgrade_proxy_password)
  - [autoupgrade_proxy_username](#autoupgrade_proxy_username)
  - [autoupgrade_run_local](#autoupgrade_run_local)
  - [autoupgrade_upgrade_clear_recovery_data](#autoupgrade_upgrade_clear_recovery_data)
  - [autoupgrade_upgrade_fail_on_precheck_errors](#autoupgrade_upgrade_fail_on_precheck_errors)
  - [autoupgrade_upgrade_global_parameters](#autoupgrade_upgrade_global_parameters)
  - [autoupgrade_upgrade_parameters](#autoupgrade_upgrade_parameters)
  - [autoupgrade_upgrade_pdbs](#autoupgrade_upgrade_pdbs)
  - [autoupgrade_upgrade_poll](#autoupgrade_upgrade_poll)
  - [autoupgrade_upgrade_restoration](#autoupgrade_upgrade_restoration)
  - [autoupgrade_upgrade_timeout](#autoupgrade_upgrade_timeout)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.16.0`

## Default Variables

### autoupgrade_download_dir

Value for `global.download_folder`. Downloaded patches are placed here.

#### Default value

```YAML
autoupgrade_download_dir: '{{ oracle_sw_source_local }}'
```

### autoupgrade_download_filename_regex

Regex for `filename` in `oracle_sw_patches`.
Only matching entries are downloaded by AutoUpgrade (database patches for `autoupgrade_download_platform`).

#### Default value

```YAML
autoupgrade_download_filename_regex: ^p[0-9]+_[0-9A-Za-z]+_Linux-x86-64\.zip$
```

### autoupgrade_download_gold_image

Value for `patch<n>.gold_image` in the AutoUpgrade config file for all patch sections.
Can be overwritten with attribute `gold_image` in `autoupgrade_download_patches`.

`NO`: no gold image is downloaded.
`AUTO`, `YES`, `ALL`: see Oracle documentation for AutoUpgrade.

Empty: parameter is not written and the default from AutoUpgrade (`AUTO`) is used.

#### Default value

```YAML
autoupgrade_download_gold_image: ''
```

#### Example usage

```YAML
autoupgrade_download_gold_image: "NO"
```

### autoupgrade_download_gold_image_latest

Create a symlink to the latest Gold Image of each release (`autoupgrade_download_gold_image_rename: true`).

The symlink is named `autoupgrade_download_gold_image_prefix` + major release + `_latest.zip`
and points to the renamed Gold Image with the highest release update in `autoupgrade_download_dir`:

| Renamed Gold Images | Symlink |
| --- | --- |
| `db_home_19.31.zip`, `db_home_19.32.zip` | `db_home_19_latest.zip -> db_home_19.32.zip` |
| `db_home_26.03.zip`, `db_home_26.04.zip` | `db_home_26_latest.zip -> db_home_26.04.zip` |

The symlink is changed only, when a newer Gold Image exists.
The download of an older release update does not change the symlink.

Use the symlink as `imagename` in `db_homes_config` for an inventory independent of the release update.

#### Default value

```YAML
autoupgrade_download_gold_image_latest: false
```

### autoupgrade_download_gold_image_prefix

Prefix for the new filename of a Gold Image (`autoupgrade_download_gold_image_rename: true`).

#### Default value

```YAML
autoupgrade_download_gold_image_prefix: db_home_
```

### autoupgrade_download_gold_image_rename

Rename downloaded Gold Images after the download.

AutoUpgrade creates unique filenames with a timestamp, e.g. `db_goldimage_19_32_20261021112350.zip`.
The file is renamed to `autoupgrade_download_gold_image_prefix` + release + `.zip`:

| Gold Image (AutoUpgrade) | Renamed file |
| --- | --- |
| `db_goldimage_19_32_<timestamp>.zip` (19.32) | `db_home_19.32.zip` |
| `db_goldimage_23_26_3_<timestamp>.zip` (23.26.3) | `db_home_26.03.zip` |

A symlink with the original filename is created for the renamed file.
AutoUpgrade finds the file under the original name and skips a new download.
The symlinks can be removed for cleanup. They are not created again.

Release and filename are taken from `patches_info.json` in `autoupgrade_download_dir`.
An existing file with the new name is never replaced.

#### Default value

```YAML
autoupgrade_download_gold_image_rename: false
```

### autoupgrade_download_latest

Download the latest `autoupgrade.jar` from `autoupgrade_jar_url` into the software
repository before the installation.

The target depends on the location of the installation media:

| Installation media | Download to |
| --- | --- |
| `oracle_sw_copy: true` or `autoupgrade_run_local: true` | Ansible controller (`run_once`, no `become`): `autoupgrade_jar_filesource` or `oracle_sw_source_local`/`autoupgrade_jar`. Requires `is_sw_source_local: true`. |
| `oracle_sw_copy: false` | target host as `oracle_user`: `autoupgrade_jar_filesource` or `oracle_stage_remote`/`autoupgrade_jar`. The directory must exist and be writable for `oracle_user`. |

Existing installations are only replaced with `autoupgrade_force_update: true`.

#### Default value

```YAML
autoupgrade_download_latest: false
```

### autoupgrade_download_patches

List of patches to download with `download_patches.yml`.
Each element creates a `patch<n>` section in the AutoUpgrade config file.

| Attribute | Description |
| --- | --- |
| target_version | mandatory: release, e.g. `19`, `23` |
| patch | mandatory: e.g. `RECOMMENDED` or `RU,OPATCH,OJVM,DPBP` or `RU:19.28,OPATCH` |
| platform | optional: default `autoupgrade_download_platform` |
| gold_image | optional: `NO`, `AUTO`, `YES`, `ALL` - default `autoupgrade_download_gold_image` |

#### Default value

```YAML
autoupgrade_download_patches: []
```

#### Example usage

```YAML
autoupgrade_download_patches:
  - target_version: 19
    patch: RU,OPATCH,OJVM,DPBP
  - target_version: 23
    patch: RECOMMENDED
    platform: LINUX.X64
  - target_version: 19
    patch: RU,OPATCH,OJVM,DPBP
    gold_image: "NO"
```

### autoupgrade_download_platform

Default platform for the download, when `platform` is not set in `autoupgrade_download_patches`.

#### Default value

```YAML
autoupgrade_download_platform: LINUX.X64
```

### autoupgrade_download_supported_releases

Releases supported by AutoUpgrade for downloading patches.

#### Default value

```YAML
autoupgrade_download_supported_releases: [19, 21, 23, 26]
```

### autoupgrade_download_use_oracle_sw_patches

Use the same variables as role `orasw_download_patches` for the download:

- `oracle_sw_patches`: each entry is added to the AutoUpgrade patch list
of the release from `version` (e.g. `19.3.0.0` -> `target_version=19`).
AutoUpgrade does not accept Release Updates by patch number. The keyword is derived:

| Entry in `oracle_sw_patches` | AutoUpgrade |
| --- | --- |
| attribute `autoupgrade_patch` | value, e.g. `RU:19.24`, `OJVM`, `DPBP` |
| attribute `ru_version` (Release Update), e.g. `19.24.0.0.240716` | `RU:19.24` |
| `description` contains `OJVM` | `OJVM` |
| others | `patchid` (one-off) |
- `db_homes_installed` / `db_homes_config` and `oracle_install_version_gi`
(`oracle_install_option_gi`: `CRS_CONFIG` or `HA_CONFIG`):
`OPATCH` is downloaded for each release

The result is added to `autoupgrade_download_patches`.

See `autoupgrade_run_local` for multiple hosts in the play.
Only entries from `oracle_sw_patches` are used, where `filename` matches
`autoupgrade_download_filename_regex` and the release from `version` is in
`autoupgrade_download_supported_releases`. Others (e.g. APEX, cvupack) are ignored with a warning.

The My Oracle Support credentials (`mos_username` / `mos_password`) are read
by AutoUpgrade from the keystore `autoupgrade_keystore`.

#### Default value

```YAML
autoupgrade_download_use_oracle_sw_patches: true
```

### autoupgrade_force_update

Update an existing `autoupgrade.jar` in the AutoUpgrade home.

`false`: An existing file is never replaced.

`true`: The file is replaced, when it differs from the file in the software repository.

#### Default value

```YAML
autoupgrade_force_update: false
```

### autoupgrade_home

Directory for `autoupgrade.jar` and the generated AutoUpgrade config files
on the target host.

#### Default value

```YAML
autoupgrade_home: '{{ oracle_base }}/product/autoupgrade'
```

### autoupgrade_jar

Filename of AutoUpgrade.
The file is expected under `oracle_sw_source_local` / `oracle_sw_source_www`.

On the Ansible controller the file is always taken from `oracle_sw_source_local`
(`is_sw_source_local: true`) or `oracle_sw_source_www` - `oracle_sw_copy` is ignored.

#### Default value

```YAML
autoupgrade_jar: autoupgrade.jar
```

### autoupgrade_jar_filesource

If `autoupgrade_jar` is not placed under `oracle_sw_source_local` / `oracle_sw_source_www`,
path can be forced using `autoupgrade_jar_filesource` instead.
`autoupgrade_jar_filesource` must be the full path/URL, including the filename.

#### Example usage

```YAML
autoupgrade_jar_filesource: /orasw/autoupgrade/autoupgrade.jar
```

### autoupgrade_jar_url

URL for the latest version of AutoUpgrade (used by `autoupgrade_download_latest`).

#### Default value

```YAML
autoupgrade_jar_url: https://download.oracle.com/otn-pub/otn_software/autoupgrade.jar
```

### autoupgrade_java_home

JAVA_HOME used for AutoUpgrade on the target host.
`java` from `PATH` is used, when `autoupgrade_java_home` is empty.

#### Default value

```YAML
autoupgrade_java_home: ''
```

#### Example usage

```YAML
autoupgrade_java_home: /u01/app/oracle/product/19/db1/jdk
```

### autoupgrade_java_options

Additional Java options for each call of `autoupgrade.jar`, e.g. a truststore
for a proxy with TLS inspection.

With proxy credentials (`autoupgrade_proxy_username` or credentials in `https_proxy`)
`-Djdk.http.auth.tunneling.disabledSchemes=` is added automatically,
because Java disables Basic authentication for HTTPS tunneling by default.

#### Default value

```YAML
autoupgrade_java_options: []
```

#### Example usage

```YAML
autoupgrade_java_options:
  - -Djavax.net.ssl.trustStore=/etc/pki/java/cacerts
  - -Djavax.net.ssl.trustStorePassword=changeit
```

### autoupgrade_keystore

Value for `global.keystore` in the AutoUpgrade config files.

The keystore holds the My Oracle Support credentials (`mos_username`, `mos_password`)
and is managed by `keystore.yml` (included by `download_patches.yml`).

#### Default value

```YAML
autoupgrade_keystore: '{{ _autoupgrade_home }}/keystore'
```

### autoupgrade_keystore_fail_on_invalid_credentials

Fail, when the credentials in the keystore cannot login into My Oracle Support.

#### Default value

```YAML
autoupgrade_keystore_fail_on_invalid_credentials: true
```

### autoupgrade_keystore_manage

Create/update the keystore with `mos_username` / `mos_password` in `download_patches.yml`.

`false`: The keystore must exist. It is not changed by the role.

Requires the Python module `pexpect` on the host executing AutoUpgrade.

#### Default value

```YAML
autoupgrade_keystore_manage: true
```

### autoupgrade_keystore_no_log

Hide the output of tasks with passwords for the keystore console.
Set to `false` for debugging only!

#### Default value

```YAML
autoupgrade_keystore_no_log: true
```

### autoupgrade_keystore_password

Password for the AutoUpgrade keystore. At least 16 characters are required.

When `autoupgrade_keystore_password` is empty, the SHA256 hash of `mos_password` is used.
When `mos_password` is changed, the keystore cannot be opened for changes anymore.
The keystore is then removed and created again with the new credentials.
The same happens, when `autoupgrade_keystore_password` is changed.

#### Default value

```YAML
autoupgrade_keystore_password: ''
```

### autoupgrade_keystore_recreate

Remove and create the keystore in each execution.

#### Default value

```YAML
autoupgrade_keystore_recreate: false
```

### autoupgrade_keystore_timeout

Timeout in seconds for each prompt of the keystore console.
The console connects to My Oracle Support for checking the credentials.

#### Default value

```YAML
autoupgrade_keystore_timeout: 300
```

### autoupgrade_local_home

Directory for `autoupgrade.jar` and the generated AutoUpgrade config files
on the Ansible controller (`autoupgrade_run_local: true`).

#### Default value

```YAML
autoupgrade_local_home: "{{ lookup('ansible.builtin.env', 'HOME') }}/autoupgrade"
```

### autoupgrade_local_java_home

JAVA_HOME used for AutoUpgrade on the Ansible controller (`autoupgrade_run_local: true`).
`java` from `PATH` is used, when `autoupgrade_local_java_home` is empty.

#### Default value

```YAML
autoupgrade_local_java_home: ''
```

### autoupgrade_log_dir

Value for `global.global_log_dir` in the AutoUpgrade config files.

#### Default value

```YAML
autoupgrade_log_dir: >-
  {{ _autoupgrade_run_local | bool
     | ternary(_autoupgrade_home + '/log', oracle_base + '/cfgtoollogs/autoupgrade') }}
```

### autoupgrade_proxy_check

Check the connection to Oracle before AutoUpgrade (`download_patches.yml`) or `get_url`
(`autoupgrade_download_latest`) is executed.

The check uses the same host, user and proxy settings (`http_proxy`, `https_proxy`, `no_proxy`,
`autoupgrade_proxy_username`, `autoupgrade_proxy_password`) as the later download.
Any HTTP response of the target counts as success.
Errors are explained (e.g. proxy authentication failed, proxy not reachable, no route to the internet),
before they lead to misleading errors of AutoUpgrade or of the keystore.

The upgrade of PDBs does not need a connection to the internet and does not execute the check.

#### Default value

```YAML
autoupgrade_proxy_check: true
```

### autoupgrade_proxy_check_timeout

Timeout in seconds for each URL of the check of the connection.

#### Default value

```YAML
autoupgrade_proxy_check_timeout: 30
```

### autoupgrade_proxy_check_urls

URLs for the check of the connection in `download_patches.yml`.
These are the hosts used by AutoUpgrade 26 for the login into My Oracle Support and the download of patches.
For `autoupgrade_download_latest` the host of `autoupgrade_jar_url` is checked.

#### Default value

```YAML
autoupgrade_proxy_check_urls:
  - https://login-ext.identity.oraclecloud.com
  - https://transport.oracle.com
  - https://updates.oracle.com
  - https://aru-akam.oracle.com
```

### autoupgrade_proxy_password

Password for an HTTP proxy with authentication. See `autoupgrade_proxy_username`.

#### Default value

```YAML
autoupgrade_proxy_password: ''
```

### autoupgrade_proxy_username

Username for an HTTP proxy with authentication.

The proxy itself is defined with `http_proxy`, `https_proxy` and `no_proxy`
(same variables as for other downloads in `ansible-oracle`).
Username and password are added URL encoded to `http_proxy` and `https_proxy`:
`http://<user>:<password>@proxy:3128`.
Credentials in `http_proxy` / `https_proxy` are not changed.

The proxy is used by `get_url` (download of `autoupgrade.jar`) and by AutoUpgrade
(keystore, download of patches). AutoUpgrade reads `https_proxy`.
AutoUpgrade needs access to `updates.oracle.com`, `login-ext.identity.oraclecloud.com`
and `aru-akam.oracle.com`.

#### Default value

```YAML
autoupgrade_proxy_username: ''
```

#### Example usage

```YAML
https_proxy: http://proxy.example.com:3128
no_proxy: localhost,.example.com
autoupgrade_proxy_username: proxyuser
autoupgrade_proxy_password: "{{ vault_proxy_password }}"
```

### autoupgrade_run_local

Execute AutoUpgrade on the Ansible controller instead of the target host.
The switch is valid for all task files (`install.yml`, `keystore.yml`, `download_patches.yml`).

`true` (default): Tasks are delegated to `localhost` with `run_once` and without `become`.
`autoupgrade_local_home` and `autoupgrade_local_java_home` are used.
This is useful for downloading patches into the software repository on the Ansible controller.

`false`: Tasks are executed on the target host as `oracle_user`,
e.g. for the installation of AutoUpgrade on database servers.

_Important_

With `true` the tasks are executed only once (`run_once`) with the variables
of the first host in the play (`oracle_sw_patches`, `db_homes_installed`, `db_homes_config`,
`oracle_install_version_gi`, `autoupgrade_download_patches`).
These variables must be the same for all hosts in the play - e.g. defined in `group_vars/all`
for the whole environment.
When they are defined per host, limit the playbook to one host (`--limit <host>`)
or execute it for each host.

#### Default value

```YAML
autoupgrade_run_local: true
```

### autoupgrade_upgrade_clear_recovery_data

Discard the recovery data of AutoUpgrade (`-clear_recovery_data`) before the analyze phase.

AutoUpgrade keeps recovery data after each deploy - finished or not.
The role handles it automatically:

| Recovery data | Behaviour |
| --- | --- |
| finished deploy, PDBs pending | cleared automatically before analyze/fixups |
| finished deploy, all PDBs upgraded | kept (needed for `-restore`) |
| unfinished deploy | deploy phase: resumed. analyze/fixups phase: fail |

`true`: the recovery data is discarded in any case, e.g. after a manual restore of the PDBs.
An unfinished deploy cannot be resumed anymore!

#### Default value

```YAML
autoupgrade_upgrade_clear_recovery_data: false
```

### autoupgrade_upgrade_fail_on_precheck_errors

Fail the analyze phase and the fixups phase, when AutoUpgrade reports checks with severity `ERROR`,
which cannot be fixed automatically by AutoUpgrade (no fixup available or `runfix` is `NO`).

The deploy phase is never started, when these checks fail.

#### Default value

```YAML
autoupgrade_upgrade_fail_on_precheck_errors: true
```

### autoupgrade_upgrade_global_parameters

Additional global parameters for the upgrade config files (`global.<key>=<value>`).
`global_log_dir` is set by the role.

#### Default value

```YAML
autoupgrade_upgrade_global_parameters: {}
```

#### Example usage

```YAML
autoupgrade_upgrade_global_parameters:
  keystore: /u01/app/oracle/admin/autoupgrade/keystore
```

### autoupgrade_upgrade_parameters

Default AutoUpgrade parameters for all AutoUpgrade jobs (`upg1.<key>=<value>`).
Can be overwritten with `autoupgrade.parameters` in `oracle_pdbs`.

Values are written unchanged. Booleans are converted into `yes`/`no`.

#### Default value

```YAML
autoupgrade_upgrade_parameters: {}
```

#### Example usage

```YAML
autoupgrade_upgrade_parameters:
  timezone_upg: "yes"
  drop_grp_after_upgrade: "yes"
```

### autoupgrade_upgrade_pdbs

Limit `upgrade_analyze.yml` / `upgrade_fixups.yml` / `upgrade_deploy.yml` to these PDBs (`pdb_name` in `oracle_pdbs`).

Empty (default): all PDBs in `oracle_pdbs` with attribute `autoupgrade`
and `state: present` are processed.

The upgrade is an Unplug/Plug upgrade of PDBs into a CDB of the new release.
`oracle_pdbs` defines the _end state_: `cdb` and `home` are the target CDB and target `ORACLE_HOME`.
The source is defined with the attribute `autoupgrade` of the PDB:

| Attribute | Description |
| --- | --- |
| source_cdb | mandatory: `oracle_db_name` of the source CDB |
| source_home | optional: key in `db_homes_config` of the source `ORACLE_HOME`. Default: `home` of `source_cdb` in `oracle_databases` |
| source_sid | optional: SID of the source CDB. Default: from `source_cdb` in `oracle_databases`, otherwise `source_cdb` |
| source_pdb_name | optional: name of the PDB in the source CDB. Default: `pdb_name` |
| copy_option | optional: `upg1.target_pdb_copy_option.<pdb>`, e.g. `file_name_convert=NONE`. Default: datafiles are reused (no copy) |
| restoration | optional: `true`/`false` - default `autoupgrade_upgrade_restoration` |
| parameters | optional: dict with additional AutoUpgrade parameters (`upg1.<key>=<value>`). Overrides `autoupgrade_upgrade_parameters`. |

All PDBs with the same `source_cdb` and `cdb` are upgraded in one AutoUpgrade job.
`restoration` and `parameters` must be identical for these PDBs.

`sid`, `source_home`, `target_home`, `target_cdb`, `pdbs`, `log_dir` and `restoration`
are set by the role and must not be used in `parameters`.

_Important_: Do not execute playbook `manage_db` between the change of `oracle_pdbs`
and the upgrade. `oradb_manage_pdb` would create a new, empty PDB in the target CDB.

#### Default value

```YAML
autoupgrade_upgrade_pdbs: []
```

#### Example usage

```YAML
autoupgrade_upgrade_pdbs:
  - ORCLPDB1

oracle_pdbs:
  - cdb: DB26              # target CDB (end state)
    home: db26-si-ee       # target ORACLE_HOME (end state)
    pdb_name: ORCLPDB1
    state: present
    autoupgrade:
      source_cdb: DB2      # source CDB in 19c
      source_home: db1932-si-ee
      parameters:
        timezone_upg: "yes"
```

### autoupgrade_upgrade_poll

Poll interval in seconds for AutoUpgrade in deploy mode.

#### Default value

```YAML
autoupgrade_upgrade_poll: 60
```

### autoupgrade_upgrade_restoration

Value for `upg1.restoration` for all AutoUpgrade jobs.
Can be overwritten with `autoupgrade.restoration` in `oracle_pdbs`.

`false` (default): AutoUpgrade creates no Guaranteed Restore Point before the upgrade
(`upg1.restoration=no`). There is no automatic fallback - take a backup before the upgrade!

`true`: AutoUpgrade creates a Guaranteed Restore Point before the upgrade (`upg1.restoration=yes`).
Requires a Fast Recovery Area and Enterprise Edition.

#### Default value

```YAML
autoupgrade_upgrade_restoration: false
```

### autoupgrade_upgrade_timeout

Maximum runtime in seconds for AutoUpgrade in deploy mode per AutoUpgrade job (`async`).

#### Default value

```YAML
autoupgrade_upgrade_timeout: 21600
```

## Discovered Tags

**_always_**

**_assert_**

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
