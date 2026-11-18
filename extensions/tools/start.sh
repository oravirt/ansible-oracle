#!/usr/bin/env bash
# Start the instances of a scenario again, e.g. after a restart of WSL/docker
# (the containers have no restart policy and stay stopped).
#
# Usage (from extensions/): tools/start.sh <scenario>
#   e.g. tools/start.sh rac      (task start S=rac)
#
# 1. starts the stopped containers of the scenario (molecule state: created)
# 2. runs molecule/<scenario>/start.yml, if it exists, with the inventory of molecule
#    (molecule side-effect with start.yml instead of side_effect.yml, tools/molecule-start.yml)
#    e.g. rac: loop devices of the ASM disks, /etc/hosts, Clusterware stack, RAC databases
# Scenarios without start.yml need the start of the containers only (systemd/Oracle Restart
# start the services in the containers).
set -euo pipefail
TOOLS_DIR=$(cd "$(dirname "$0")" && pwd)
# shellcheck source-path=SCRIPTDIR source=load_env.sh
. "${TOOLS_DIR}/load_env.sh"
cd "${TOOLS_DIR}/.."

SCENARIO="${1:-}"
if [ -z "${SCENARIO}" ] || [ ! -d "molecule/${SCENARIO}" ]; then
  echo "Usage: tools/start.sh <scenario> (directory in extensions/molecule)" >&2
  exit 1
fi

# instances of the scenario with molecule state created (columns: name driver provisioner
# scenario created converged), without color codes
mapfile -t instances < <(
  molecule list -s "${SCENARIO}" -f plain 2>/dev/null \
    | sed 's/\x1b\[[0-9;]*m//g' \
    | awk -v s="${SCENARIO}" '$4 == s && $5 == "true" {print $1}'
)
if [ "${#instances[@]}" -eq 0 ]; then
  echo "No created instances in scenario ${SCENARIO}. Use task converge S=${SCENARIO}." >&2
  exit 1
fi

for instance in "${instances[@]}"; do
  state=$(docker inspect -f '{{.State.Running}}' "${instance}" 2>/dev/null || echo missing)
  case "${state}" in
    true) echo "${instance}: running" ;;
    false)
      echo "${instance}: start"
      docker start "${instance}" >/dev/null
      ;;
    *)
      echo "${instance}: container is missing => task destroy S=${SCENARIO} and task converge S=${SCENARIO}" >&2
      exit 1
      ;;
  esac
done

if [ -f "molecule/${SCENARIO}/start.yml" ]; then
  echo "${SCENARIO}: start.yml"
  exec "${TOOLS_DIR}/molecule.sh" --base-config "${TOOLS_DIR}/molecule-start.yml" side-effect -s "${SCENARIO}"
fi
echo "${SCENARIO}: no start.yml, the containers are started"
