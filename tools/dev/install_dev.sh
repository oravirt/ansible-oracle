#!/usr/bin/env bash
set -eu
set -o pipefail

basedir=$(dirname -- "$0")

##########################
##### ansible-oracle #####
##########################

echo "venv for ansible-oracle"
venv_dir=~/venv/ansible-oracle
test -d "${venv_dir}" 2>/dev/null || python3 -m venv "${venv_dir}"

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
