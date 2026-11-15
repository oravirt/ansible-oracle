#!/usr/bin/env bash
# molecule with the variables from extensions/.env (MOLECULE_SW_DIR, MOS_USERNAME, MOS_PASSWORD, ...)
#
# Usage (from extensions/): tools/molecule.sh <molecule arguments>
#   e.g. tools/molecule.sh converge -s dbfs
#
# Variables already set in the environment have precedence over extensions/.env.
# A shared lock (tools/lock.sh) prevents the reinstallation of the collection during the run.
set -euo pipefail
TOOLS_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source-path=SCRIPTDIR source=load_env.sh
. "${TOOLS_DIR}/load_env.sh"
# shellcheck source-path=SCRIPTDIR source=lock.sh
. "${TOOLS_DIR}/lock.sh"

case "${1:-}" in
  # diff of the changed tasks (only tasks with the result changed print a diff, e.g. file:
  # owner/mode, template, lineinfile) => the log shows why a task is not idempotent
  idempotence) export ANSIBLE_DIFF_ALWAYS=True ;;
esac

case "${1:-}" in
  # no lock for interactive shells and lists
  login | list) exec molecule "$@" ;;
esac

# fd 9 is inherited by molecule => the lock is held until molecule ends
exec 9>"${MOLECULE_LOCK}"
flock -s 9
exec molecule "$@"
