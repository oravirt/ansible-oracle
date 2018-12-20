# Conversion

This will help you to blindly bulk convert from the old way of managing ORACLE_HOMEs to new new one, where ORACLE_HOMEs are split out into 2 new dictionaries:

- db_homes_config
- db_homes_installed


**NOTE**
**This script is in no way fool proof, no checking if the dictionary has already been converted is done**, so consider yourself warned.

Depending on the way your current config is set up, this may or may not work out of the box.
No existing files will be changed, but 2 new ones are created.


### Howto

By default this script will look in group_vars for **all** files containing the `oracle_databases` dictionary and parse it.

It will then:

Create 2 new files in the directory where the **source** file was found.
The files are named:
**sourcefile_dbhome.yml**            <-- This file will contain the new home config
**sourcefile_databases.yml**         <-- This file will contain the way the new `oracle_databases` dictionary should look like, with the correct home mapping.
The `sourcefile_databases.yml` file has the entire dictionary commented out, so as not to interfere with the existing configuration.
   

e.g:

Assuming the `oracle_databases` dictionary looks like this, for `group_vars/dev`:

```
oracle_databases:
      - home: dev1
        oracle_version_db: 12.1.0.2
        oracle_edition: EE
        oracle_db_name: racdba
        oracle_db_type: RAC
        is_container: False
        pdb_prefix: pdb
        num_pdbs: 1
        storage_type: ASM
        datafile_dest: +DATA
        recoveryfile_dest: +FRA
        oracle_db_mem_percent: 25
        oracle_database_type: MULTIPURPOSE
        redolog_size_in_mb: 500
        state: present
```
     
```
# python convert.py

Processing: ./group_vars/dev.yml 
        Writing dbhome config to ./group_vars/dev_dbhome.yml 
        Writing new db config to ./group_vars/dev_databases.yml 
        Writing new pdb config to ./group_vars/dev_pdbs.yml 
```


#### Result
