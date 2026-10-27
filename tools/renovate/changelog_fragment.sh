#!/usr/bin/env bash
set -eu
set -o pipefail

# Shellscript for renovate in ansible-oracle
#
# Creates an antsibull-changelog fragment for a dependency update.
# Called by renovate as postUpgradeTasks (see renovate.json).
#
# Usage: changelog_fragment.sh <depNameSanitized> <depName> <currentVersion> <newVersion>

if [ $# -ne 4 ] ; then
  echo "Usage: $0 <depNameSanitized> <depName> <currentVersion> <newVersion>"
  exit 2
fi

dep_sanitized="$1"
dep_name="$2"
current_version="$3"
new_version="$4"

workdir=$(dirname "$0")
cd "${workdir}/../.." || exit 1

fragment="changelogs/fragments/renovate-${dep_sanitized}.yml"

cat > "${fragment}" <<EOF
---
trivial:
  - "renovate: update ${dep_name} from ${current_version} to ${new_version}"
EOF

echo "Created ${fragment}"
