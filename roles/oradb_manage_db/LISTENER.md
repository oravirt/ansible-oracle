
# Information for listener configuration

The following special configurations for
listener are supported. See below for Oracle Restart and
Grid Infrastructure.

# Requirements

- only supported with new home structure
- 'listener_installed' and  'oracle_listeners_config'  are needed
- multiple Hosts/Ports for each Listener
- Extproc support
- only Database in Filesystem without Restart/Grid Infrastructure is supported at the moment
- Definition of listener_installed disables old functionality
- listener_name in oracle_database for SID_LIST_ in listener.ora
When listener_name in oracle_database is defined a static  entry for the instance is added to SID_LIST_ in Listener.
- An Instance could only be part of 1 SID_LIST_ in the Listener
- Don't forget local_listener in init.ora!
- address in oracle_listeners_config need protocol for a host
- listener_port in oracle_database is ignored!


# Example Configuration

oracle_listeners_config:
    LISTENER:
        home: 18300-base
        address:
          - host: hwe2018
            port: 1521
            protocol: TCP
    LISTENER1523:
        home: 18300-base
        address:
          - host: hwe2018
            port: 1523
            protocol: TCP


listener_installed:
      - home: 18300-base
        listener_name: LISTENER
        state: present
      - home: 18300-base
        listener_name: LISTENER1523
        state: present

# Grid Infrastructure / Oracle Restart

With Grid Infrastructure or Oracle Restart (`oracle_install_option_gi`) every listener from
`listener_installed` is registered with `srvctl add/modify listener` (module `oracle_crs_listener`).

| Entry in `listener_installed` | ORACLE_HOME of the listener resource | `listener.ora` | OS user |
|---|---|---|---|
| `home: <db_homes_config key>` | ORACLE_HOME of `home` (`srvctl ... -oraclehome`) | ORACLE_HOME / ORACLE_BASE_HOME of `home` | `oracle_user` |
| `use_gi_home: true` (without `home`) | GI / Oracle Restart home: `crs_home` from `/etc/oracle/olr.loc` | GI / Oracle Restart home | `grid_user` with `role_separation`, otherwise `oracle_user` |

- Each entry has either `home` or `use_gi_home: true`.
- The GI / Oracle Restart home of a listener is always `crs_home` from `/etc/oracle/olr.loc`:
  there is only one Grid Infrastructure / Oracle Restart per host.

```yaml
listener_installed:
  # listener in the GI / Oracle Restart home
  - listener_name: LISTENER
    use_gi_home: true
    state: present
  # additional listener in the ORACLE_HOME of the database
  - listener_name: LISTENER2
    home: db19-gi-ee
    state: present
```
