---
name: aotest
description: Runs molecule tests of ansible-oracle (full test, destroy, converge, module tests) via the Taskfile in extensions/. Only on explicit invocation via /aotest.
argument-hint: "[S=<scenario>] [T=full|destroy|converge|module[,...]] [M=<module>[,<module>...]]"
disable-model-invocation: true
---

# /aotest – molecule tests in ansible-oracle

Invoking `/aotest` is the explicit authorization to run the requested molecule actions,
including `destroy`, `converge` and `full`. This overrides the general rule that Claude only runs
side-effect/module tests – but only for the actions requested in this invocation.
Do not ask again – only stop in the cases listed under "Stop rules".

Arguments (`$ARGUMENTS`, all optional):
- `S=<scenario>` → molecule scenario, default `dbfs`
- `T=<action>[,<action>...]` → default `module`; several actions run in the given order
  (e.g. `T=destroy,converge,module`)
- `M=<module>[,<module>...]` → only for `T=module`: modules to test; empty = all modules

## 1. Validate

- Repo root: `git rev-parse --show-toplevel` of the current directory; it must contain
  `extensions/Taskfile.yml` and `shell.nix`, otherwise stop.
- `S` must be a directory in `extensions/molecule/` (not `shared_config`).
- `T=module` is only valid for scenarios with module tests: `extensions/molecule/<S>/module_tests.yml`
  exists (currently `dbfs`, `dbfs-ol10`, `has-ol9`).
- Each entry of `M` must have a test file `extensions/molecule/shared_config/module_tests/<module>.yml`.
- `M` without `module` in `T` → ignore it and say so.

## 2. Actions

All commands run inside the repo's nix-shell (provides `task`, molecule venv):

```bash
set -o pipefail; cd <repo> && nix-shell --run 'cd extensions && <task command>' 2>&1 | sed -u 's/\x1b\[[0-9;]*m//g' > <log>
```

| `T`        | Task command                                   |
|------------|------------------------------------------------|
| `full`     | `task test S=<S>` (create, converge, idempotence, side-effect, verify, destroy) |
| `destroy`  | `task destroy S=<S>`                           |
| `converge` | `task converge S=<S>`                          |
| `module`   | `task module-test S=<S> [M=<M>]`               |

- One log file per action in the scratchpad: `aotest-<S>-<action>-<timestamp>.log`.
- Run each action with `run_in_background` (converge/full take a long time) and wait for the
  completion notification – do not poll. Start the next action only after the previous one succeeded.
- Before starting, tell the user in one line what runs in which order and where the logs are.
- Do not change code, tests or `module_tests.yml` during the run.

## 3. Report

- Per action: exit code, duration, last `PLAY RECAP` (failed/unreachable per host).
- `module`: the tables "Summary per module" and "Summary of module tests" from the log, and the
  result file `extensions/molecule/<S>/module_tests_results/<label>.json` (default label: see log).
  List failed checks with `id`, `module` and `msg`; mention `known` and `fixed` (known bug not
  reproduced) separately.
- On failure: the failing task with its error message (search the log for `fatal:` / `FAILED!`),
  and a short assessment of the cause. Suggest a fix, but do not apply it unasked.

## Stop rules (only ask here)

- Unknown scenario, invalid `T`, or `M` module without test file → list the valid values.
- `T=module` on a scenario without running instances (`task list` / `molecule list` shows
  `Converged: false`) → suggest `T=converge,module`, do not start converge on your own.
- An action fails → do not start the following actions; report.
