#!/usr/bin/env bash
#
# Date: 18.07.2023
#
# Thorsten Bruhns (thorsten.bruhns@opitz-consulting.de)
#
# Simple RMAN-Backupscript
#
# Important Note for Real Application Clusters!
# Do NOT USE the real ORACLE_SID. Please use the normal DB_NAME without the
# the number at the end. The scripts is detecting the real instance from the
# clusterware. We are able to backup RAC OneNode Databases or policy managed
# environments now!
#
# This script search for an rman-file in $ORACLE_BASE/admin/<ORACLE_SID|DB_NAME>/rman
# with filename <action>.rman. This search could be changed with -r or RMANSCRIPTDIR.
#
# The script checks for an existing directory $ORACLE_BASE/admin/<ORACLE_SID|DB_NAME>/rman/log.
# This directory could be changed with -l or RMANLOGDIR.
# Backup will not start when directory or backupscript is not existing.
# Script will check for a catalog. When the catalog is not reachable the backup
# will run without a catalog.
# Configuration for RMAN-Catalog is done with Environment variable CATALOGCONNECT
# Example:
# CATALOGCONNECT=rman/catalog@hostname:port/service
# rman target / catalog $CATALOGCONNECT
#
# Major actions are logged in syslog of operating system
# A Logfile with name <logdir>/<ORACLE_SID>_<action>.log includes
# all output from RMAN
#
# Exit codes:
#   0     RMAN successful or backup skipped (service not running on this node)
#   1     wrong parameters or service not existing
#   10-12 ORACLE_SID, ORACLE_HOME or ORACLE_BASE not found
#   21-23 log directory, RMAN script or logfile not existing
#   99    RMAN failed
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#

PROGNAME=$(basename "$0")
ORATAB=/etc/oratab

function print_usage() {
	echo "Usage:"
	echo "  $PROGNAME -a <action> -s <ORACLE_SID|DB_NAME> [-r <Directory>]"
	echo "            [-l <Directory>] [-c <CATALOGCONNECT>] [-t <TARGETCONNECT>]"
	echo "            [--service <Servicename in GI/Restart>]"
	echo "  $PROGNAME -h"
}

function print_help() {
	echo ""
	print_usage
	echo ""
	echo "RMAN Backupscript"
	echo ""
	echo "-a/--action           Name for .rman-Script without extension"
	echo "-s/--ORACLE_SID       ORACLE_SID / DB_NAME (RAC) of Database"
	echo "                       Please use the DB_NAME from oratab in RAC-Environments!"
	echo "-r/--rmanscriptdir    Directory for *.rman-Scripts"
	echo "                       You could use the environment variable RMANSCRIPTDIR as well"
	echo "                       Default: <ORACLE_BASE>/admin/<ORACLE_SID|DB_NAME>/rman"
	echo "-l/--logdir           Directory for tee-output of RMAN"
	echo "                       You could use the environment variable RMANLOGDIR as well"
	echo "                       Default: <rmanscriptdir>/log"
	echo "-c/--catalogconnect   connect catalog <catalogconnect>"
	echo "                       You could use the environment variable CATALOGCONNECT as well"
	echo "-t/--targetconnect    connect target <targetconnect>"
	echo "                       You could use the environment variable TARGETCONNECT as well"
	echo "--service             Execute rman when Service in GI/Restart is running on current node."
	echo ""
	echo "The environment variable RMANTNS_ADMIN is used as TNS_ADMIN for RMAN."
}

print_syslog() {
	# Don't write to syslog when logger is not there
	if command -v logger > /dev/null 2>&1; then
		logger -t "${PROGNAME}" -- "${*}"
	fi
}

# message to stdout and syslog
print_msg() {
	echo "${*}"
	print_syslog "${*}"
}

abort_script() {
	print_syslog "Abort Code=${1}"
	exit "${1}"
}

check_catalog() {
	# check for availible catalog
	# catalog not working => switch to nocatalog!
	print_syslog "Check for working RMAN Catalog"
	catalogconnect="connect catalog ${CATALOGCONNECT}"
	if "${ORACLE_HOME}/bin/rman" << _EOF_
connect target ${TARGETCONNECT:-"/"}
${catalogconnect}
_EOF_
	then
		print_syslog "Using Catalog for Backup!"
	else
		# catalog not working => clear variable
		catalogconnect=''
		print_syslog "Catalog not reachable. Working without Catalog!"
	fi
}

check_service() {
	# get data from srvctl for service
	echo "Checking for running service ${INSTANCE_SERVICE} on current node"
	retstr=$("${SRVCTL}" status service -d "${ORACLE_SID}" -s "${INSTANCE_SERVICE}")
	echo "${retstr}"

	# Is service existing?
	if echo "${retstr}" | grep -q "^PRCR-1001:"; then
		echo "Service not existing. Aborting backup!"
		abort_script 1
	fi

	# Is service running on current node?
	if [ "${local_only}" = 'true' ]; then
		# Oracle Restart: only one node
		running_service=$(echo "${retstr}" | sed -e 's/^Service .* is running//g' -e 's/ //g')
		if [ -n "${running_service}" ]; then
			print_msg "Service ${INSTANCE_SERVICE} not running on current node. Skipping backup!"
			exit 0
		fi
	else
		running_instances=$(echo "${retstr}" | sed -e 's/^Service .* is running on instance(s)//g' -e 's/ //g')
		if [ ! "${node_sid}" = "${running_instances}" ]; then
			print_msg "Service ${INSTANCE_SERVICE} not running on current node. Skipping backup!"
			exit 0
		fi
	fi
}

setenv() {
	SHORTOPTS="ha:s:r:l:t:c:"
	LONGOPTS="help,action:,ORACLE_SID:,rmanscriptdir:,logdir:,targetconnect:,catalogconnect:,service:"

	if ! ARGS=$(getopt -s bash --options "${SHORTOPTS}" --longoptions "${LONGOPTS}" --name "${PROGNAME}" -- "$@"); then
		print_usage
		exit 1
	fi

	eval set -- "${ARGS}"

	while true; do
		case "$1" in
			-h|--help)
				print_help
				exit 0;;
			-a|--action)
				rmanbackuptyp=${2}
				shift 2;;
			-s|--ORACLE_SID)
				ORACLE_SID=${2}
				shift 2;;
			-r|--rmanscriptdir)
				RMANSCRIPTDIR=${2}
				shift 2;;
			-l|--logdir)
				RMANLOGDIR=${2}
				shift 2;;
			-t|--targetconnect)
				TARGETCONNECT=${2}
				shift 2;;
			-c|--catalogconnect)
				CATALOGCONNECT=${2}
				shift 2;;
			--service)
				INSTANCE_SERVICE=${2}
				shift 2;;
			--)
				shift
				break;;
		esac
	done

	if [ -z "${ORACLE_SID}" ]; then
		echo "Missing parameter for ORACLE_SID"
		echo " "
		print_usage
		exit 1
	fi

	if [ -z "${rmanbackuptyp}" ]; then
		echo "Missing parameter for action"
		echo " "
		print_usage
		exit 1
	fi

	# set NLS_DATE_FORMAT for nice date-format
	export NLS_DATE_FORMAT='dd.mm.yy hh24:mi:ss'

	# ORACLE_SID or DB_NAME (RAC) from command line, used for the default directories
	DB_NAME=${ORACLE_SID}

	# getting ORACLE_HOME from oratab (1st entry)
	ORACLE_HOME=$(grep "^${ORACLE_SID}:" "${ORATAB}" 2>/dev/null | head -1 | cut -d":" -f2)

	if [ -z "${ORACLE_HOME}" ]; then
		print_msg "ORACLE_SID ${ORACLE_SID} not found in ${ORATAB}"
		abort_script 10
	fi

	if [ ! -d "${ORACLE_HOME}" ]; then
		# ORACLE_HOME not existing => we need to exit the script!
		print_msg "ORACLE_HOME ${ORACLE_HOME} from ${ORATAB} not found"
		abort_script 11
	fi
	export ORACLE_HOME

	# we could be on Grid-Infrastructure
	# => There is only an entry for the DB_NAME in oratab!
	# => We need to find the right ORACLE_SID from Clusterware
	OCRLOC=/etc/oracle/ocr.loc
	if [ -f "${OCRLOC}" ]; then
		# shellcheck source=/dev/null
		. "${OCRLOC}"
		# shellcheck source=/dev/null
		. /etc/oracle/olr.loc
		SRVCTL="${ORACLE_HOME}/bin/srvctl"

		# Some Installations store local_only in uppercase...
		local_only=$(echo "${local_only:-true}" | tr '[:upper:]' '[:lower:]')

		if [ "${local_only}" = 'false' ]; then
			# We are on a real Grid-Infrastructure!
			# => instance of the database on the current node
			# crs_home is set by olr.loc
			# shellcheck disable=SC2154
			node_sid=$("${SRVCTL}" status instance -d "${ORACLE_SID}" -node "$("${crs_home}/bin/olsnodes" -l)" | cut -d" " -f2)
		fi

		if [ -n "${INSTANCE_SERVICE}" ]; then
			check_service
		fi

		if [ "${local_only}" = 'false' ]; then
			# => overwrite the ORACLE_SID from command parameterline
			ORACLE_SID=${node_sid}
		fi
	fi
	export ORACLE_SID

	# Do we have an executable for getting the current ORACLE_BASE?
	orabase="${ORACLE_HOME}/bin/orabase"
	if [ -x "${orabase}" ]; then
		ORACLE_BASE=$("${orabase}")
	fi

	# do we have a valid ORACLE_BASE?
	if [ ! -d "${ORACLE_BASE:-leer}" ]; then
		print_msg "We cannot work without ORACLE_BASE=${ORACLE_BASE}"
		abort_script 12
	fi
	export ORACLE_BASE

	# where are the rman-skripts?
	# Default: $ORACLE_BASE/admin/<ORACLE_SID|DB_NAME>/rman/<action>.rman
	RMANSCRIPTDIR=${RMANSCRIPTDIR:-${ORACLE_BASE}/admin/${DB_NAME}/rman}
	RMANLOGDIR=${RMANLOGDIR:-${RMANSCRIPTDIR}/log}

	if [ -n "${RMANTNS_ADMIN}" ]; then
		echo "Setting TNS_ADMIN from RMANTNS_ADMIN to: ${RMANTNS_ADMIN}"
		export TNS_ADMIN="${RMANTNS_ADMIN}"
	fi

	rmanskript="${RMANSCRIPTDIR}/${rmanbackuptyp}.rman"
	rmanlog="${RMANLOGDIR}/${ORACLE_SID}_${rmanbackuptyp}.log"

	if [ -n "${CATALOGCONNECT}" ]; then
		check_catalog
	else
		print_syslog "Using no Catalog for Backup!"
		catalogconnect=''
	fi
}

check_requirements() {
	if [ ! -d "${RMANLOGDIR}" ]; then
		print_msg "Directory ${RMANLOGDIR} for RMAN logfiles not existing."
		abort_script 21
	fi

	if [ ! -f "${rmanskript}" ]; then
		print_msg "RMAN-script ${rmanskript} not existing!"
		abort_script 22
	fi

	if ! touch "${rmanlog}"; then
		print_msg "Logfile ${rmanlog} for RMAN could not be created."
		abort_script 23
	fi
}

do_backup() {
	# tee: all output is written to the logfile as well
	"${ORACLE_HOME}/bin/rman" << _EOF_ | tee -a "${rmanlog}"
connect target ${TARGETCONNECT:-"/"}
${catalogconnect}
@${rmanskript}
_EOF_
	retcode=${PIPESTATUS[0]}
	if [ "${retcode}" -eq 0 ]; then
		print_syslog "RMAN Backup successful. Logfile ${rmanlog}"
	else
		print_msg "RMAN return code ${retcode}. Please check logfile ${rmanlog}"
		abort_script 99
	fi
}

##############################################################################
#                                                                            #
#                                   MAIN                                     #
#                                                                            #
##############################################################################
print_syslog "Begin"
setenv "$@"
check_requirements
do_backup
print_syslog "End Code=0"
exit 0
