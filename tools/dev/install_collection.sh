#!/bin/bash
#
# Install the ansible-oracle collection from current source
#
set -eu

# shellcheck disable=SC2086
WORKTDIR="$(dirname ${BASH_SOURCE[0]})/../.."
COLLECTION_OUTDIR=/tmp/ansible-oracle-collection

cd "${WORKTDIR}"
echo "Working in $(pwd)"
test -s "${COLLECTION_OUTDIR}" || mkdir "${COLLECTION_OUTDIR}"

COLLECTION_VERSION=$(grep "^version: " galaxy.yml | cut -d" " -f2)
COLLECTION_ARCHIVE="${COLLECTION_OUTDIR}/opitzconsulting-ansible_oracle-${COLLECTION_VERSION}.tar.gz"
echo "COLLECTION_ARCHIVE: ${COLLECTION_ARCHIVE}"

echo "Building Collection"
ansible-galaxy collection build -v --force --output-path "${COLLECTION_OUTDIR}"

echo "Installing Collection"
ansible-galaxy collection install -v --force "${COLLECTION_ARCHIVE}"

echo "Removing Collectionarchiv"
rm -f "${COLLECTION_ARCHIVE}"
