#!/usr/bin/env bash
#
# shellcheck disable=SC2034
ORACLE_HOME_NAME=testgrid12c
ORACLE_BASE=/u01/app/oracle
ORACLE_HOME=/u01/app/12.1.0.1/grid
ORAINVENTORY_LOC=/u01/app/oraInventory

perl $ORACLE_HOME/clone/bin/clone.pl -silent \
  ORACLE_BASE="$ORACLE_BASE" \
  ORACLE_HOME="$ORACLE_HOME" \
  ORACLE_HOME_NAME="$ORAHOME_NAME" \
  INVENTORY_LOCATION="$ORAINVENTORY_LOC" \
  -O'"CLUSTER_NODES={ansrac01, ansrac02}"' \
  -O'"LOCAL_NODE=ansrac01"' CRS=TRUE
