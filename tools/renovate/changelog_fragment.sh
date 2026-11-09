#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for renovate in ansible-oracle
#
# Creates an antsibull-changelog fragment for a dependency update.
# Called by renovate as postUpgradeTasks (see renovate.json).
#
# Grouped updates (groupName in renovate.json) pass groupSlug and groupName,
# so all dependencies of a group write the same fragment: one entry per branch.
# A leading "v" of the versions is removed (pre-commit and github tags vs. PyPI).
#
# Usage: changelog_fragment.sh <depNameSanitized|groupSlug> <depName|groupName> <currentVersion> <newVersion>

if [ $# -ne 4 ] ; then
  echo "Usage: $0 <depNameSanitized|groupSlug> <depName|groupName> <currentVersion> <newVersion>"
  exit 2
fi

dep_sanitized="$1"
dep_name="$2"
current_version="${3#v}"
new_version="${4#v}"

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

fragment="changelogs/fragments/renovate-${dep_sanitized}.yml"

cat > "${fragment}" <<EOF
---
minor_changes:
  - "renovate: update ${dep_name} from ${current_version} to ${new_version}"
EOF

echo "Created ${fragment}"
