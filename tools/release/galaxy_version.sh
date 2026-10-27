#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for managing releases in ansible-oracle
#
# Check or set the collection version from galaxy.yml in all requirements.yml
# which reference opitzconsulting.ansible_oracle.
#
# Usage: galaxy_version.sh check|fix

collection="opitzconsulting.ansible_oracle"

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

galaxy="galaxy.yml"

requirement_files="tools/release/requirements.yml
example/beginner_patching/ansible/requirements.yml
example/rac/ansible/requirements.yml
example/beginner/ansible/requirements.yml"

function usage() {
  echo "Usage: $0 check|fix"
  exit 2
}

function galaxy_version() {
  sed -n -E "s/^version:\s*([^[:space:]]+).*/\1/p" "${galaxy}"
}

# version of the first not commented entry for the collection
function requirement_version() {
  sed -n -E "/^\s*- name:\s*${collection//./\\.}\s*$/{n;s/^\s*version:\s*([^[:space:]]+).*/\1/p;q}" "$1"
}

function check_versions() {
  local version rc=0 current
  version=$(galaxy_version)

  for requirement_file in ${requirement_files} ; do
    current=$(requirement_version "${requirement_file}")
    if [ "${current}" = "${version}" ] ; then
      echo "OK       ${requirement_file}: ${current}"
    else
      echo "MISMATCH ${requirement_file}: ${current:-<missing>} (galaxy.yml: ${version})"
      rc=1
    fi
  done
  return ${rc}
}

function fix_versions() {
  local version
  version=$(galaxy_version)

  echo "Using version from galaxy.yml: ${version}"
  for requirement_file in ${requirement_files} ; do
    sed -i -E "/^\s*- name:\s*${collection//./\\.}\s*$/{n;s/^(\s*version:\s*).*/\1${version}/}" "${requirement_file}"
  done
  check_versions
}

[ $# -eq 1 ] || usage

case "$1" in
  check) check_versions ;;
  fix)   fix_versions ;;
  *)     usage ;;
esac
