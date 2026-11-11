# ahf_fleet_insights

_Experimental_: the role is under development. Breaking changes can happen at any time
and are not always documented.

Install Oracle AHF Fleet Insights as central web interface for the
evaluation of AHF data (Compliance results, TFA collections, Insights)
from many database servers.

The AHF clients (role `ahf` with `ahf_fleet_insights_client: true`) upload
their data to Fleet Insights. The database servers are not contacted
for the evaluation.

Fleet Insights requires a repository database (19c or newer) with the
schema user from `create_db_user.sql` of the installation media.

Fleet Insights has no systemd unit, its processes are started by cron entries of
`ahf_fi_install_user`. The role starts Fleet Insights (`ahffi start`), when it is not running,
and waits for the web application on `ahf_fi_port`.

See `doc/guides/ahf.adoc`.

## Table of contents

- [Requirements](#requirements)
- [Default Variables](#default-variables)
  - [ahf_fi_cert_days](#ahf_fi_cert_days)
  - [ahf_fi_cert_file](#ahf_fi_cert_file)
  - [ahf_fi_cert_generate](#ahf_fi_cert_generate)
  - [ahf_fi_cert_key_file](#ahf_fi_cert_key_file)
  - [ahf_fi_cert_names](#ahf_fi_cert_names)
  - [ahf_fi_clamscan](#ahf_fi_clamscan)
  - [ahf_fi_db_host](#ahf_fi_db_host)
  - [ahf_fi_db_password](#ahf_fi_db_password)
  - [ahf_fi_db_port](#ahf_fi_db_port)
  - [ahf_fi_db_service](#ahf_fi_db_service)
  - [ahf_fi_db_user](#ahf_fi_db_user)
  - [ahf_fi_db_wallet](#ahf_fi_db_wallet)
  - [ahf_fi_firewall](#ahf_fi_firewall)
  - [ahf_fi_install_dir](#ahf_fi_install_dir)
  - [ahf_fi_install_user](#ahf_fi_install_user)
  - [ahf_fi_installer_archive](#ahf_fi_installer_archive)
  - [ahf_fi_instant_client](#ahf_fi_instant_client)
  - [ahf_fi_instantclient_repo](#ahf_fi_instantclient_repo)
  - [ahf_fi_java_home](#ahf_fi_java_home)
  - [ahf_fi_manage_packages](#ahf_fi_manage_packages)
  - [ahf_fi_packages](#ahf_fi_packages)
  - [ahf_fi_port](#ahf_fi_port)
  - [ahf_fi_public_cert_fetch](#ahf_fi_public_cert_fetch)
  - [ahf_fi_registration_password](#ahf_fi_registration_password)
  - [ahf_fi_registration_user](#ahf_fi_registration_user)
  - [ahf_fi_stage_dir](#ahf_fi_stage_dir)
  - [ahf_fi_start_timeout](#ahf_fi_start_timeout)
  - [ahf_fi_upgrade](#ahf_fi_upgrade)
  - [ahf_fi_verify_signature](#ahf_fi_verify_signature)
- [Dependencies](#dependencies)
- [License](#license)
- [Author](#author)

---

## Requirements

- Minimum Ansible version: `2.16.0`

## Default Variables

### ahf_fi_cert_days

Validity of the generated certificate in days.

#### Default value

```YAML
ahf_fi_cert_days: 730
```

### ahf_fi_cert_file

Own certificate (PEM) for Fleet Insights on the Ansible controller, e.g. from an internal CA.
Imported with `ahffi importcert` together with `ahf_fi_cert_key_file`.
Empty: `ahf_fi_cert_generate` is used.

#### Default value

```YAML
ahf_fi_cert_file: ''
```

### ahf_fi_cert_generate

Create a self-signed certificate with Subject Alternative Names (`ahf_fi_cert_names`)
and import it with `ahffi importcert`.

The certificate of the installer has no Subject Alternative Name. The AHF clients
(AHF 26.x) check only the SAN and reject it with
`CERTIFICATE_VERIFY_FAILED ... Hostname mismatch`.
Ignored, when `ahf_fi_cert_file` is set.

#### Default value

```YAML
ahf_fi_cert_generate: true
```

### ahf_fi_cert_key_file

Private key (PEM) of `ahf_fi_cert_file` on the Ansible controller.

#### Default value

```YAML
ahf_fi_cert_key_file: ''
```

### ahf_fi_cert_names

DNS names for the Subject Alternative Name of the generated certificate.
The clients must use one of them in `ahf_fleet_insights_url`.
The first name is the CN.

#### Default value

```YAML
ahf_fi_cert_names: '{{ [ansible_hostname, ansible_fqdn] | unique }}'
```

### ahf_fi_clamscan

Path to `clamscan` for a virus scan of the uploaded collections (`CLAMSCAN`).
Increases the processing time.

#### Default value

```YAML
ahf_fi_clamscan: ''
```

### ahf_fi_db_host

Hostname of the repository database (`DB_HOST`). Oracle Database 19c or newer.

#### Default value

```YAML
ahf_fi_db_host: '{{ inventory_hostname }}'
```

### ahf_fi_db_password

Password of `ahf_fi_db_user` (`DB_PASSWORD`). Use Ansible Vault.

#### Default value

```YAML
ahf_fi_db_password: ''
```

### ahf_fi_db_port

Listener port of the repository database (`DB_PORT`).

#### Default value

```YAML
ahf_fi_db_port: 1521
```

### ahf_fi_db_service

Service name of the repository database (`DB_SERVICE`).

#### Default value

```YAML
ahf_fi_db_service: ''
```

### ahf_fi_db_user

Schema user in the repository database (`DB_USER`).
Create it with `create_db_user.sql` from the installation media.

#### Default value

```YAML
ahf_fi_db_user: AHFFI
```

### ahf_fi_db_wallet

Wallet for the connection to the repository database (`DB_WALLET`).

#### Default value

```YAML
ahf_fi_db_wallet: ''
```

### ahf_fi_firewall

Open `ahf_fi_port` in firewalld, when firewalld is running.

#### Default value

```YAML
ahf_fi_firewall: true
```

### ahf_fi_install_dir

Installation directory of Fleet Insights (`INSTALL_DIR`).
Plan 4 GB per registered cluster.

#### Default value

```YAML
ahf_fi_install_dir: '{{ oracle_base }}/ahffi'
```

### ahf_fi_install_user

OS user for the installation and the processes of Fleet Insights.
The installer fails with `root`.

#### Default value

```YAML
ahf_fi_install_user: '{{ oracle_user }}'
```

### ahf_fi_installer_archive

Filename of the installation media in the software repository
(My Oracle Support Doc ID 3043060.1).

Empty (default): the newest file matching `AHFFI-LINUX_v*.zip` is used from
`oracle_sw_source_local` on the Ansible controller or from `oracle_stage_remote`
(`oracle_sw_copy: false`). Must be set for `oracle_sw_source_www`.

#### Default value

```YAML
ahf_fi_installer_archive: ''
```

#### Example usage

```YAML
ahf_fi_installer_archive: AHFFI-LINUX_v25.2.0.zip
```

### ahf_fi_instant_client

Directory of Oracle Instant Client (`INSTANT_CLIENT`).

#### Default value

```YAML
ahf_fi_instant_client: /usr/lib/oracle/23/client64
```

### ahf_fi_instantclient_repo

Yum repository for Oracle Instant Client on Oracle Linux.
Empty: no repository is configured.

#### Default value

```YAML
ahf_fi_instantclient_repo: >-
  https://yum.oracle.com/repo/OracleLinux/OL{{ ansible_distribution_major_version }}/oracle/instantclient23/x86_64/
```

### ahf_fi_java_home

Java home (Java 22 or newer) for Fleet Insights (`JAVA_HOME`).

Empty (default): the newest Oracle JDK in `/usr/lib/jvm/jdk-*-oracle-x64` is used.
The Oracle JDK RPM installs into a directory with the full version,
e.g. `/usr/lib/jvm/jdk-25.0.5.0.3-oracle-x64`, which changes with every update.

#### Default value

```YAML
ahf_fi_java_home: ''
```

### ahf_fi_manage_packages

Install the required packages (`ahf_fi_packages`) and the yum repository
for Oracle Instant Client (`ahf_fi_instantclient_repo`).

#### Default value

```YAML
ahf_fi_manage_packages: true
```

### ahf_fi_packages

Packages for Fleet Insights: cronie, iproute, hostname, Java 22 or newer and
Oracle Instant Client Basic + SQL*Plus.

The Oracle JDK is used under the Oracle No-Fee Terms and Conditions (NFTC).

#### Default value

```YAML
ahf_fi_packages:
  - cronie
  - iproute
  - hostname
  - https://download.oracle.com/java/25/latest/jdk-25_linux-x64_bin.rpm
  - oracle-instantclient-basic
  - oracle-instantclient-sqlplus
```

### ahf_fi_port

Port of the web application (`WEBAPP_PORT`, 1024 - 49151).
Must be reachable from all AHF clients and the browsers.

#### Default value

```YAML
ahf_fi_port: 5005
```

### ahf_fi_public_cert_fetch

Path on the Ansible controller for the public certificate of Fleet Insights
(`<ahf_fi_install_dir>/ahf_service/certs/cert.pem`, self-signed by the installer).
The AHF clients need it for the registration (role `ahf`: `ahf_fleet_insights_public_cert`).
The certificate is also available as fact `ahf_fi_public_cert`.
Empty: the certificate is not fetched.

#### Default value

```YAML
ahf_fi_public_cert_fetch: ''
```

#### Example usage

```YAML
ahf_fi_public_cert_fetch: "{{ inventory_dir }}/files/ahffi_cert.pem"
```

### ahf_fi_registration_password

Password of `ahf_fi_registration_user` (`GENERIC_REGISTRATION_PASSWORD`).
At least 8 characters with a digit, a special character and an uppercase letter.
Use Ansible Vault.

#### Default value

```YAML
ahf_fi_registration_password: ''
```

### ahf_fi_registration_user

Generic registration user for the AHF clients (`GENERIC_REGISTRATION_USER`).
Created by the installer, when user and password are set.

#### Default value

```YAML
ahf_fi_registration_user: ''
```

### ahf_fi_stage_dir

Directory on the target host for the installation media.
The directory is removed after the installation, because the
properties file contains passwords.

#### Default value

```YAML
ahf_fi_stage_dir: '{{ oracle_stage }}/ahffi'
```

### ahf_fi_start_timeout

Seconds to wait for the web application on `ahf_fi_port` after the installation or start.
The role starts Fleet Insights (`ahffi start`), when `ahffi status` does not report it as running.

#### Default value

```YAML
ahf_fi_start_timeout: 300
```

### ahf_fi_upgrade

Patch an existing installation, when the installation media has a newer version.

#### Default value

```YAML
ahf_fi_upgrade: true
```

### ahf_fi_verify_signature

Verify the signature of the installation media with `openssl`.

#### Default value

```YAML
ahf_fi_verify_signature: true
```

## Dependencies

- orahost_meta
- orasw_meta

## License

license (MIT)

## Author

[Thorsten Bruhns]
