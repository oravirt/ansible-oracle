#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for managing releases in ansible-oracle
#
# used to update the collection version in files.

galaxy="../../galaxy.yml"

workdir=$(dirname "$0")
cd "$workdir" || exit 1

build_release=$(git branch --show-current | cut -d"/" -f2)

function change_release_version() {
  echo "Using Release from branch: $build_release"
  echo "Format galaxy.yml"
  sed -i "/^version: /c\version: ${build_release}" "${galaxy}"
  grep "version: " "${galaxy}"

  echo "Format requirements.yml"
  sed -i "/^    version: /c\    version: ${build_release}" requirements.yml
  grep "version: " requirements.yml

  target_dirs="example/beginner_patching/ansible/requirements.yml
  example/rac/ansible/requirements.yml
  example/beginner/ansible/requirements.yml"

  for requirement_file in ${target_dirs} ; do
    filename="../../${requirement_file}"

    echo "target file: ${filename}"
    cp requirements.yml "${filename}"
  done

}

check_antsibull_changes() {

  # check if all antsibull entries have a reference with (oravirt#[0-9][0-9][0-9])
  echo "Checking antsibull changelog entries"

  pwd

  for clfile in "../../changelogs/fragments"/*yml ; do
    echo "Checking file: ${clfile}"

    if grep "  - " "${clfile}" | grep -v "oravirt#[0-9][0-9][0-9]" ; then
      echo "Found changelog entries without PR reference"
      exit
    fi
  done

}

function make_changelog() {
  # cd "${workdir}/../.."
  pwd
  echo "Starting antsibull changelog"
  ../.././.venv/antsibull/bin/antsibull-changelog release
}

check_antsibull_changes
change_release_version

make_changelog
