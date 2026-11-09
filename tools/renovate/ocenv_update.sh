#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for renovate in ansible-oracle
#
# Replaces roles/oradb_manage_db/files/ocenv with the version from
# opitzconsulting/oracle-scripts and updates tools/renovate/ocenv.version.
# Called by renovate as postUpgradeTasks (see renovate.json).
#
# Usage: ocenv_update.sh <version>   (YYYY.MMDD.HHMMSS, committer date in UTC)
#        ocenv_update.sh --check     (compare ocenv with the blob in ocenv.version)

repo=opitzconsulting/oracle-scripts
api="https://api.github.com/repos/${repo}"

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

ocenv=roles/oradb_manage_db/files/ocenv
marker=tools/renovate/ocenv.version

if [ $# -ne 1 ] ; then
  echo "Usage: $0 <version> | --check"
  exit 2
fi

local_blob=$(git hash-object "${ocenv}")
marker_blob=$(sed -n 's/^blob: *//p' "${marker}")

if [ "$1" = --check ] ; then
  if [ "${local_blob}" != "${marker_blob}" ] ; then
    echo "${ocenv} differs from upstream version in ${marker}"
    echo "  local blob:  ${local_blob}"
    echo "  marker blob: ${marker_blob}"
    exit 1
  fi
  echo "${ocenv} is unchanged ($(sed -n 's/^version: *//p' "${marker}"))"
  exit 0
fi

version="$1"

curl_api() {
  curl -fsSL -H 'Accept: application/vnd.github+json' \
    ${GITHUB_COM_TOKEN:+-H "Authorization: Bearer ${GITHUB_COM_TOKEN}"} "$@"
}

# upstream commit with the committer date of <version>
commit=$(curl_api "${api}/commits?path=ocenv&sha=main&per_page=100" \
  | jq -r --arg v "${version}" \
    '.[] | select((.commit.committer.date | fromdateiso8601 | strftime("%Y.%m%d.%H%M%S")) == $v) | .sha' \
  | head -1)
if [ -z "${commit}" ] ; then
  echo "no commit of ocenv in ${repo} for version ${version}"
  exit 1
fi

blob=$(curl_api "${api}/contents/ocenv?ref=${commit}" | jq -r .sha)

tmpfile=$(mktemp)
trap 'rm -f "${tmpfile}"' EXIT
curl -fsSL -o "${tmpfile}" "https://raw.githubusercontent.com/${repo}/${commit}/ocenv"

new_blob=$(git hash-object "${tmpfile}")
if [ "${new_blob}" != "${blob}" ] ; then
  echo "downloaded ocenv has blob ${new_blob}, expected ${blob} (${repo}@${commit})"
  exit 1
fi

cat "${tmpfile}" > "${ocenv}"
sed -i \
  -e "s/^version: .*/version: ${version}/" \
  -e "s/^commit: .*/commit: ${commit}/" \
  -e "s/^blob: .*/blob: ${blob}/" \
  "${marker}"

echo "Updated ${ocenv} to ${repo}@${commit} (${version}, blob ${blob})"
