# Module tests (molecule scenario dbfs)

The side-effect of the scenario `dbfs` tests the modules of `opitzconsulting.ansible_oracle`
against an existing Oracle AI Database 26ai (CDB `DB1`, PDB `ORCLPDB`).
The database is created once with `converge`; the tests can be repeated as often as needed.

## Usage

```bash
cd extensions
task converge S=dbfs                                    # once (creates the database)
task module-test                                        # all module tests
task module-test M=oracle_user,oracle_role              # selected modules
task module-test L=cx_oracle                            # result file results/cx_oracle.json
task module-test M=oracle_user C=false                  # without reinstalling the collection
```

`task module-test` installs the collection from the repository (`task collection`)
and runs `molecule side-effect -s dbfs` with the environment variables
`MODULE_TESTS` (comma separated list of modules) and `MODULE_TESTS_LABEL` (name of the result file).

IMPORTANT: `molecule side-effect` alone does not install the collection, only `converge` does.
Without `task collection` the tests use the code of the last converge.

`C=false` skips `task collection`, e.g. for repeated runs when only the tests in
`module_tests/` have changed (they are read from the repository, not from the installed collection).
Changes in `plugins/` or `roles/` are not used until the collection is installed again.

## Result file

Every check writes `id`, `expect`, `actual` (`changed`, `ok`, `failed`) and `msg` into
`module_tests/results/<label>.json` on the controller (ignored by git).

Comparison before/after the migration from cx_Oracle to python-oracledb:

```bash
task module-test L=cx_oracle      # before the migration
task module-test L=oracledb       # after the migration
diff molecule/dbfs/module_tests/results/cx_oracle.json molecule/dbfs/module_tests/results/oracledb.json
```

## Known bugs

`known_bugs.yml` contains the ids of checks that fail because of a known bug in a module.
They are reported as `KNOWN BUG` and do not fail the test run.
A check from this list that passes is reported as `KNOWN BUGS NOT REPRODUCED`
=> remove the entry after the bug has been fixed.

## Files

| File | Purpose |
|---|---|
| `vars.yml` | module list, connection variants, environment |
| `known_bugs.yml` | known bugs (`<check id>: <description>`) |
| `_check.yml` | compare a registered module result with the expectation and record it |
| `_sql.yml` | independent verification with `sqlplus / as sysdba` |
| `<module>.yml` | tests of one module |

## Conventions for a module test

- File `module_tests/<module>.yml`, added to `mt_all_modules` in `vars.yml`.
- All test objects start with `MOLTEST_` (common objects in the CDB: `C##MOLTEST_`).
- The test is repeatable and leaves the database unchanged:
  remove the objects at the beginning (`cleanup`, result ignored) and at the end.
  Changed parameters, AWR settings etc. are restored.
- Every module call has `register: _res` and `ignore_errors: true`,
  followed by `_check.yml` with a unique id `<module>.<cdb|pdb>.<step>` and the expectation:

  ```yaml
  - name: oracle_role | create
    opitzconsulting.ansible_oracle.oracle_role:
      role: MOLTEST_ROLE
    register: _res
    ignore_errors: true
  - name: oracle_role | check create
    ansible.builtin.include_tasks: _check.yml
    vars: {mt_id: oracle_role.pdb.create, mt_res: "{{ _res }}", mt_expect: changed}
  ```

- Typical steps: create (`changed`), same call again (`ok`), check mode if supported
  (`changed`, verify with sqlplus that nothing happened), change (`changed`), again (`ok`),
  verify with `_sql.yml`, drop (`changed`), drop again (`ok`), error case (`failed`).
- The expectation is the documented behaviour (DOCUMENTATION of the module).
  If the module behaves differently because of a bug, the check keeps the documented
  expectation and the id goes into `known_bugs.yml`.
- Connection: hostname, port, service_name, user, password and mode come from `module_defaults`
  in `side_effect.yml`. Default is `mt_conn_pdb` (system in ORCLPDB).
  Switch it with `vars: {mt_conn: "{{ mt_conn_cdb }}"}` on the task. Variants in `vars.yml`:
  `mt_conn_cdb`, `mt_conn_pdb`, `mt_conn_cdb_sysdba`, `mt_conn_pdb_sysdba`,
  `mt_conn_pdb_wallet`, `mt_conn_pdb_wrong_password`.
  Every module test uses the wallet and sysdba at least once.
- Verification with sqlplus (independent of the Python driver):

  ```yaml
  - name: oracle_role | verify create
    ansible.builtin.include_tasks: _sql.yml
    vars:
      mt_sql_container: "{{ mt_pdb }}"
      mt_sql: "select count(*) from dba_roles where role = 'MOLTEST_ROLE';"
      mt_sql_expect: "1"
      mt_sql_id: oracle_role.pdb.create_sql
  ```

- Not tested in dbfs: `oracle_asmdg`, `oracle_asmvol` (ASM), `oracle_ldapuser` (LDAP),
  `oracle_opatch`, `oracle_gi_facts`, `oracle_sqldba` (no cx_Oracle).
