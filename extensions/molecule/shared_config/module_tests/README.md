# Module tests (molecule scenarios dbfs and has-ol9)

The side-effect of the scenarios tests the modules of `opitzconsulting.ansible_oracle`
against an existing database. The tests are shared by the scenarios, only the
scenario specific variables are in `<scenario>/module_tests.yml`.

| Scenario | Environment |
|---|---|
| `dbfs` | Oracle AI Database 26ai on filesystem without Grid Infrastructure (CDB `DB1`, PDB `ORCLPDB`) |
| `has-ol9` | Oracle Restart 26ai with ASM, Oracle Database 19c in `+DATA` (CDB `DBHAS`, PDB `ORCLPDB1`) |

The database is created once with `converge`; the tests can be repeated as often as needed.

## Usage

```bash
cd extensions
task converge S=dbfs                                    # once (creates the database)
task module-test                                        # all module tests in dbfs
task module-test M=oracle_user,oracle_role              # selected modules
task module-test L=cx_oracle                            # result file dbfs/module_tests_results/cx_oracle.json
task module-test M=oracle_user C=false                  # without reinstalling the collection
task module-test S=has-ol9                              # all module tests in has-ol9
task module-test S=has-ol9 M=oracle_asmdg               # selected modules in has-ol9
```

`task module-test` installs the collection from the repository (`task collection`)
and runs `molecule side-effect -s <scenario>` with the environment variables
`MODULE_TESTS` (comma separated list of modules) and `MODULE_TESTS_LABEL` (name of the result file).

IMPORTANT: `molecule side-effect` alone does not install the collection, only `converge` does.
Without `task collection` the tests use the code of the last converge.

`C=false` skips `task collection`, e.g. for repeated runs when only the tests in
`module_tests/` have changed (they are read from the repository, not from the installed collection).
Changes in `plugins/` or `roles/` are not used until the collection is installed again.

## Structure

`<scenario>/side_effect.yml` imports `shared_config/module_tests/module_tests.yml`.
The playbook loads `vars.yml`, `known_bugs.yml` and `<scenario>/module_tests.yml`
(found with `MOLECULE_SCENARIO_DIRECTORY`).

Variables in `<scenario>/module_tests.yml`:

| Variable | Purpose |
|---|---|
| `mt_all_modules` | test files (without `.yml`) of the scenario |
| `mt_oracle_home`, `mt_oracle_sid` | ORACLE_HOME and ORACLE_SID of the database |
| `mt_tns_admin` | directory with `tnsnames.ora` and `sqlnet.ora` (wallet) |
| `mt_cdb`, `mt_pdb` | CDB and PDB for the tests |
| `mt_datafile_dir` | directory or ASM disk group for explicit data files |
| `mt_known_bugs_scenario` | known bugs of the scenario |
| `mt_asm_*`, `mt_conn_asm*` | ASM instance (only has-ol9) |

## Result file

Every check writes `id`, `expect`, `actual` (`changed`, `ok`, `failed`) and `msg` into
`<scenario>/module_tests_results/<label>.json` on the controller (ignored by git).

Comparison before/after a change:

```bash
task module-test L=before
task module-test L=after
diff molecule/dbfs/module_tests_results/before.json molecule/dbfs/module_tests_results/after.json
```

## Known bugs

`known_bugs.yml` (`mt_known_bugs_common`) contains the ids of checks that fail because of a
known bug in a module in all scenarios.
Bugs that depend on the environment (database version, Grid Infrastructure) are in
`mt_known_bugs_scenario` in `<scenario>/module_tests.yml`.
They are reported as `KNOWN BUG` and do not fail the test run.
A check from these lists that passes is reported as `KNOWN BUGS NOT REPRODUCED`
=> remove the entry after the bug has been fixed.

## Files

| File | Purpose |
|---|---|
| `module_tests.yml` | playbook, imported by `<scenario>/side_effect.yml` |
| `vars.yml` | connection variants, environment, module selection |
| `known_bugs.yml` | known bugs in all scenarios (`<check id>: <description>`) |
| `_check.yml` | compare a registered module result with the expectation and record it |
| `_sql.yml` | independent verification with `sqlplus / as sysdba` (or `/ as sysasm`) |
| `<module>.yml` | tests of one module |
| `oracle_services.yml` | `oracle_services` without Grid Infrastructure (DBMS_SERVICE, dbfs) |
| `oracle_services_gi.yml` | `oracle_services` with Grid Infrastructure (srvctl, has-ol9) |
| `oracle_asmdg.yml` | `oracle_asmdg` with an own disk group on files (has-ol9) |

## Conventions for a module test

- File `module_tests/<module>.yml`, added to `mt_all_modules` in `<scenario>/module_tests.yml`.
- No scenario specific values in the tests: use `mt_cdb`, `mt_pdb`, `mt_oracle_home`,
  `mt_datafile_dir` etc.
- All test objects start with `MOLTEST_` (common objects in the CDB: `C##MOLTEST_`).
- The test is repeatable and leaves the database unchanged:
  remove the objects at the beginning (`cleanup`, result ignored) and at the end.
  Changed parameters, AWR settings etc. are restored.
- Every module call has `register: _res` and `ignore_errors: true`,
  followed by `_check.yml` with a unique id `<module>.<cdb|pdb|asm>.<step>` and the expectation:

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
  expectation and the id goes into `known_bugs.yml` (all scenarios) or
  `mt_known_bugs_scenario` (only one scenario).
- Connection: hostname, port, service_name, user, password and mode come from `module_defaults`
  in `module_tests.yml`. Default is `mt_conn_pdb` (system in `mt_pdb`).
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

  In the ASM instance with `mt_sql_asm: true` (`sqlplus / as sysasm`).

- Not tested: `oracle_asmvol` (no ADVM/ACFS in a container), `oracle_ldapuser` (LDAP),
  `oracle_opatch`, `oracle_gi_facts`, `oracle_sqldba` (no python-oracledb).
