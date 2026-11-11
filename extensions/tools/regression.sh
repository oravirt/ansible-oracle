#!/usr/bin/env bash
# Regression test of molecule scenarios with one run directory per execution.
#
# Usage (from extensions/, normally via 'task molecule:regression:<preset>', see Taskfile.regression.yml):
#   tools/regression.sh [-s dbfs,has-ol9] [-t destroy,converge,module-test] [-j 2] [-m <modules>]
#
#   -s  scenarios (comma separated), default: dbfs,dbfs-sh,has-ol9,dataguard
#   -t  steps per scenario (comma separated, executed in this order),
#       default: destroy,converge,module-test
#       allowed: destroy, create, converge, idempotence, module-test, verify
#   -j  number of scenarios running in parallel, default: 6
#   -m  MODULE_TESTS for the step module-test (default: all module tests)
#
# Behavior:
# - The collection is installed once before all scenarios (no parallel installations).
# - Scenarios run in parallel (max -j), the steps of a scenario run one after the other.
# - A failed create/converge stops the scenario, all other failures do not.
# - Results: test-runs/<run-id>/ with
#     run.env          git commit, branch, dirty flag, parameters
#     git-status.txt   uncommitted changes of the tested code
#     steps.jsonl      one JSON line per finished step (rc, duration, logfile)
#     <scenario>-<step>.log
#     module_tests/<scenario>.json  results of the module tests (MODULE_TESTS_LABEL=<run-id>)
#     summary.md       report (tools/regression_report.py), updated after every step
# - test-runs/latest is a symlink to the last run.
set -u

TOOLS_DIR=$(cd "$(dirname "$0")" && pwd)
EXT_DIR=$(dirname "${TOOLS_DIR}")
REPO_DIR=$(dirname "${EXT_DIR}")

# MOLECULE_SW_DIR, MOS_USERNAME, ... from extensions/.env (environment has precedence)
# shellcheck source-path=SCRIPTDIR source=load_env.sh
. "${TOOLS_DIR}/load_env.sh"
# shellcheck source-path=SCRIPTDIR source=lock.sh
. "${TOOLS_DIR}/lock.sh"

SCENARIOS=dbfs,dbfs-sh,has-ol9,dataguard
STEPS=destroy,converge,module-test
JOBS=6
MODULES=""

while getopts "s:t:j:m:h" opt; do
  case ${opt} in
    s) SCENARIOS=${OPTARG} ;;
    t) STEPS=${OPTARG} ;;
    j) JOBS=${OPTARG} ;;
    m) MODULES=${OPTARG} ;;
    *) sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
  esac
done

for s in ${SCENARIOS//,/ }; do
  if [ ! -f "${EXT_DIR}/molecule/${s}/molecule.yml" ]; then
    echo "Unknown scenario: ${s}" >&2
    exit 1
  fi
done
for t in ${STEPS//,/ }; do
  case ${t} in
    destroy|create|converge|idempotence|module-test|verify) ;;
    *) echo "Unknown step: ${t}" >&2; exit 1 ;;
  esac
done

cd "${EXT_DIR}" || exit 1

SHA=$(git -C "${REPO_DIR}" rev-parse --short HEAD)
DIRTY=""
if [ -n "$(git -C "${REPO_DIR}" status --porcelain --untracked-files=no)" ]; then
  DIRTY="-dirty"
fi
RUN_ID="$(date +%Y%m%d-%H%M)_${SHA}${DIRTY}"
RUN_DIR="${EXT_DIR}/test-runs/${RUN_ID}"
mkdir -p "${RUN_DIR}/module_tests"
ln -sfn "${RUN_ID}" "${EXT_DIR}/test-runs/latest"

{
  echo "RUN_ID=${RUN_ID}"
  echo "COMMIT=$(git -C "${REPO_DIR}" rev-parse HEAD)"
  echo "BRANCH=$(git -C "${REPO_DIR}" branch --show-current)"
  echo "SUBJECT=$(git -C "${REPO_DIR}" log -1 --format=%s)"
  echo "DIRTY=${DIRTY:+true}"
  echo "SCENARIOS=${SCENARIOS}"
  echo "STEPS=${STEPS}"
  echo "JOBS=${JOBS}"
  echo "MODULES=${MODULES}"
  echo "START=$(date '+%Y-%m-%d %H:%M:%S')"
} > "${RUN_DIR}/run.env"
git -C "${REPO_DIR}" status --short > "${RUN_DIR}/git-status.txt"

# plain logs for the report (no ANSI colors)
export ANSIBLE_FORCE_COLOR=false
export ANSIBLE_NOCOLOR=1
export PY_COLORS=0
export NO_COLOR=1

report() {
  python3 "${TOOLS_DIR}/regression_report.py" "${RUN_DIR}" > /dev/null 2>&1 || true
}

# steps.jsonl: one line per step, appended atomically (short lines)
record() {
  # scenario step rc start end
  printf '{"scenario": "%s", "step": "%s", "rc": %s, "start": "%s", "end": "%s", "duration_s": %s, "log": "%s"}\n' \
    "$1" "$2" "$3" "$(date -d "@$4" '+%Y-%m-%d %H:%M:%S')" "$(date -d "@$5" '+%Y-%m-%d %H:%M:%S')" \
    "$(($5 - $4))" "$1-$2.log" >> "${RUN_DIR}/steps.jsonl"
  report
}

run_step() {
  local s=$1 t=$2
  case ${t} in
    module-test)
      MODULE_TESTS="${MODULES}" MODULE_TESTS_LABEL="${RUN_ID}" molecule side-effect -s "${s}"
      ;;
    *)
      molecule "${t}" -s "${s}"
      ;;
  esac
}

run_scenario() {
  local s=$1 t rc start
  for t in ${STEPS//,/ }; do
    start=$(date +%s)
    echo "$(date +%H:%M) ${s} ${t} started"
    run_step "${s}" "${t}" > "${RUN_DIR}/${s}-${t}.log" 2>&1
    rc=$?
    if [ "${t}" = module-test ] \
       && [ -f "molecule/${s}/module_tests_results/${RUN_ID}.json" ]; then
      cp "molecule/${s}/module_tests_results/${RUN_ID}.json" "${RUN_DIR}/module_tests/${s}.json"
    fi
    record "${s}" "${t}" "${rc}" "${start}" "$(date +%s)"
    echo "$(date +%H:%M) ${s} ${t} rc=${rc}"
    if [ "${rc}" -ne 0 ] && { [ "${t}" = converge ] || [ "${t}" = create ]; }; then
      echo "$(date +%H:%M) ${s}: ${t} failed => remaining steps skipped"
      return "${rc}"
    fi
  done
}

trap 'echo "interrupted"; kill 0' INT TERM

echo "Run ${RUN_ID}: ${RUN_DIR}"
# exclusive lock for the installation, then shared lock for the molecule runs (tools/lock.sh)
exec 9>"${MOLECULE_LOCK}"
if ! flock -x -n 9; then
  echo "Another molecule run uses the installed collection (lock ${MOLECULE_LOCK})." >&2
  exit 1
fi
echo "Install collection"
if ! ansible-galaxy collection install --force .. > "${RUN_DIR}/collection-install.log" 2>&1; then
  echo "Installation of the collection failed, see ${RUN_DIR}/collection-install.log" >&2
  exit 1
fi
flock -s 9

for s in ${SCENARIOS//,/ }; do
  while [ "$(jobs -rp | wc -l)" -ge "${JOBS}" ]; do
    wait -n
  done
  run_scenario "${s}" &
done
wait

echo "END=$(date '+%Y-%m-%d %H:%M:%S')" >> "${RUN_DIR}/run.env"
python3 "${TOOLS_DIR}/regression_report.py" "${RUN_DIR}"
echo "Report: ${RUN_DIR}/summary.md"
