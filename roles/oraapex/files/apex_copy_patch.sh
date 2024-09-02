#!/usr/bin/env bash
set -eu
set -o pipefail

echo "APEX_HOME:    ${APEX_HOME}"
echo "APEX_VERSION: ${APEX_VERSION}"
echo "APEX_PATCHID: ${APEX_PATCHID}"
echo ""

copy_patch_data() {
  echo ""
  echo "Copy patch into ${APEX_HOME}"
  cp -r "${APEX_HOME}/${APEX_PATCHID}/"* "${APEX_HOME}/apex"

  echo "Remove unarchive directory: ${APEX_HOME}/${APEX_PATCHID}"
  rm -rf "${APEX_HOME:?}/${APEX_PATCHID:?}"
  echo "removal done"

  # Read current patchversion from copied data
  patchversion=$(head -1 "${APEX_HOME}/apex/README.txt" | tr -d '[:space:]' | cut -d":" -f2)
  statefile="${APEX_HOME}/.ansible_apex_patchstate"
  echo "${patchversion}" > "${statefile}"
  echo "patch statefile ${statefile} created"
}

copy_patch_data
