# autoupgrade

Manage Oracle AutoUpgrade.

The role has no `tasks/main.yml`.
Each area of AutoUpgrade has its own task file, which must be called with `tasks_from`:

| Task file | Description |
| --- | --- |
| `assert.yml` | Check variables and Java |
| `install.yml` | Install `autoupgrade.jar` into `autoupgrade_home` |
| `download_patches.yml` | Download patches from My Oracle Support with AutoUpgrade |

## Table of content

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [autoupgrade_download_dir](#autoupgrade_download_dir)
  - [autoupgrade_download_filename_regex](#autoupgrade_download_filename_regex)
  - [autoupgrade_download_gold_image](#autoupgrade_download_gold_image)
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
  - [autoupgrade_run_local](#autoupgrade_run_local)
- [Discovered Tags](#discovered-tags)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.14.0`

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
     | ternary(_autoupgrade_home + '/log', oracle_base + '/cfgtoollogs/autoupgrade')
  }}
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
