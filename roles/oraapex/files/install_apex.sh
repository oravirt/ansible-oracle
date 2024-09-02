#!/usr/bin/env bash
set -eu
set -o pipefail

echo "ORACLE_HOME:          ${ORACLE_HOME}"
echo "ORACLE_SID:           ${ORACLE_SID}"
echo "IS_CONTAINER:         ${IS_CONTAINER}"
echo "APEX_VERSION:         ${APEX_VERSION}"
echo "APEX_TABLESPACE:      ${APEX_TABLESPACE}"
echo "APEX_TEMP_TABLESPACE: ${APEX_TEMP_TABLESPACE}"
