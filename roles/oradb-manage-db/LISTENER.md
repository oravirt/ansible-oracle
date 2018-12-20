
# Information for listener configuration
The following special configurations for
listener are currently supported for
installations without Oracle Restart or
Grid Infraststructure.

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
```

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

oracle_databases: 
      - home: 18300-base
        oracle_db_name: cdb183
        listener_name: LISTENER
		
```
