#!/usr/bin/env bash
set -eu
set -o pipefail

if [ "$#" -ne 1 ] ; then
  echo "Execute install_dev.sh with Python executable"
  echo "Example:"
  echo "./install_dev.sh python3.10"
  echo ""
  echo "Make sure that venv for used python binary is installed before starting the script!"
  exit 1
fi

PYTHONBIN="${1}"
echo "Using Python for venv: ${PYTHONBIN}"

basedir=$(dirname -- "$0")

##########################
##### ansible-oracle #####
##########################

echo "venv for ansible-oracle"
venv_dir=~/venv/ansible-oracle
test -d "${venv_dir}/bin/activate" 2>/dev/null || "${PYTHONBIN}" -m venv "${venv_dir}"

# shellcheck source=/dev/null
source "${venv_dir}"/bin/activate

echo "install pip modules"
pip --require-virtualenv install -q -r "${basedir}/requirements_dev.txt"
pip list

##########################
##### ansible-doctor #####
##########################

echo "venv for ansible-doctor"
venv_dir=~/venv/ansible-doctor
test -d "${venv_dir}" 2>/dev/null || python3 -m venv "${venv_dir}"

# shellcheck source=/dev/null
source "${venv_dir}"/bin/activate

echo "install pip modules"
pip --require-virtualenv install -q -r "${basedir}/requirements_doctor.txt"
pip list

###############################
##### antsibull-changelog #####
###############################

echo "venv for antsibull-changelog"
venv_dir=~/venv/antsibull
test -d "${venv_dir}" 2>/dev/null || python3 -m venv "${venv_dir}"

# shellcheck source=/dev/null
source "${venv_dir}"/bin/activate

echo "install pip modules"
pip --require-virtualenv install -q -r "${basedir}/requirements_antsibull.txt"
pip list
