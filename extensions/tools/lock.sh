# shellcheck shell=bash
# Lock between molecule runs and the installation of the collection
#
# - molecule runs (tools/molecule.sh, tools/regression.sh) hold a shared lock
# - the installation of the collection (tools/collection_install.sh) needs an exclusive lock
# => the collection is not replaced while a molecule run uses it
MOLECULE_LOCK="${MOLECULE_LOCK:-${TMPDIR:-/tmp}/ansible-oracle-molecule.lock}"
export MOLECULE_LOCK
