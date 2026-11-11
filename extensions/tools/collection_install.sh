#!/usr/bin/env bash
# Install the collection from this repository (ansible-galaxy collection install --force)
#
# Fails, when another molecule run uses the installed collection (tools/lock.sh).
# Use C=false for a second molecule run in parallel.
set -euo pipefail
TOOLS_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source-path=SCRIPTDIR source=lock.sh
. "${TOOLS_DIR}/lock.sh"

exec 9>"${MOLECULE_LOCK}"
if ! flock -x -n 9; then
  echo "ERROR: another molecule run uses the installed collection (lock ${MOLECULE_LOCK})." >&2
  echo "       The collection is not reinstalled. Use C=false or wait for the other run." >&2
  exit 1
fi
ansible-galaxy collection install --force "${TOOLS_DIR}/../.."
