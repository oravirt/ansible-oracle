#!/bin/bash
#
# Date: 22.05.2018
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
# This script search for an rman-file in $ORACLE_BASE/admin/$ORACLE_SID/rman
# with filename <parameter 2>.rman. This search could be changed with 3rd parameter.
# 
# The script checks for an existing directory $ORACLE_BASE/admin/$ORACLE_SID/rman/log.
# Backup will not start when directory or backupscript is not existing.
# Script will check for a catalog. When the catalog is not reachable the backup
# will run without a catalog.
# Configuration for RMAN-Catalog is done with Environment variable CATALOGCONNECT
# Example:
# CATALOGCONNECT=rman/catalog@hostname:port/service
# rman target / catalog $CATALOGCONNECT
#
# Major actions are logged in syslog of operating system
# A Logfile with name $ORACLE_BASE/admin/$ORACLE_SID/rman/log/<backuptyp>.log includes
# all output from RMAN
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

PROGNAME=`basename $0`
PROGPATH=`echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,'`

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
  echo "                       Default: <ORACLE_BASE>/admin/<ORACLE_SID|DB_NAME>/rman"
  echo "-l/--logdir           Directory for tee-output of RMAN"
  echo "                       Default: <ORACLE_BASE>/admin/<ORACLE_SID|DB_NAME>/rman/log"
  echo "-c/--catalogconnect   connect catalog <catalogconnect>"
  echo "                       You could use the environment variable CATALOGCONNECT as well>"
  echo "-t/--targetconnect    connect target <targetconnect>"
  echo "                       You could use the environment variable TARGETCONNECT as well>"
  echo "--service             Execute rman when Service in GI/Restart is running on current node."
  
}

print_syslog()
{
	# Don't write to syslog when logger is not there
	which logger > /dev/null 2>&1
	retcode=${?}
	
	if [ ${retcode} -eq 0 ]
	then
		logger `basename $0` $param1 $param2 : " "${*}
	fi
}

abort_script()
{
	print_syslog "Abort Code="${1}
	exit ${1}
}

check_catalog() {
	# check for availible catalog
	# catalog not working => switch to nocatalog!
	print_syslog "Check for working RMAN Catalog"
	catalogconnect="connect catalog "${CATALOGCONNECT}
	${ORACLE_HOME}/bin/rman << _EOF_
connect target ${TARGETCONNECT:-"/"}
${catalogconnect} 
_EOF_

	retcode=${?}
	if [ ${retcode} -eq 0 ]
	then
		print_syslog "Using Catalog for Backup!"
	else
		# catalog not working
		# => clear variable
		catalogconnect=''
		export catalogconnect
		print_syslog "Catalog not reachable. Working without Catalog!"
	fi
}

check_service()
{
	# get data from srvctl for service
	retstr=$(${SRVCTL} status service -d ${ORACLE_SID} -s ${INSTANCE_SERVICE})
	echo "Checking for running service "${INSTANCE_SERVICE}" on current node"
	echo $retstr

	# Is service existing?
	echo ${retstr} | grep "^PRCR-1001:" >/dev/null
	if [ ${?} -eq 0 ]
	then
		echo "Service not existing. Aborting backup!"
		echo ${retstr}
		echo "Aborting backup!"
		exit 1
	fi

	# Is service running??
	if [ $local_only = 'TRUE' ]
	then
		running_service=$(${SRVCTL} status service -d ${ORACLE_SID} -s ${INSTANCE_SERVICE} | sed 's/^Service .* is running//g' | sed 's/ //g')
		if [ ! $running_service = '' ]
		then
			echo "Service not running on current node. Skipping backup!"
			exit 0
		fi
	else
		running_instances=$(${SRVCTL} status service -d ${ORACLE_SID} -s ${INSTANCE_SERVICE} | sed 's/^Service .* is running on instance(s)//g' | sed 's/ //g')
		node_sid=$(${SRVCTL} status instance -d ${ORACLE_SID} -node $(${crs_home}/bin/olsnodes -l) | cut -d" " -f2)
		if [ ! $node_sid = "$running_instances" ]
		then
			echo "Service not running on current node. Skipping backup!"
			exit 0
		fi
	fi
}

setenv()
{
	SHORTOPTS="ha:s:r:l:t:c:"
	LONGOPTS="help,action:,ORACLE_SID:,rmanscriptdir:,logdir:,targetconnect:,catalogconnect:,service:"

	ARGS=$(getopt -s bash --options $SHORTOPTS  --longoptions $LONGOPTS --name $PROGNAME -- "$@" ) 
	if [ ${?} -ne 0 ]
	then
		exit
	fi

	eval set -- "$ARGS"

	while true;
	do
		case "$1" in
			-h|--help)
				print_help
				exit 0;;

			-a|--action)
					rmanbackuptyp=${2}
				shift 2;;

			-s|--ORACLE_SID)
					ORACLE_SID=${2}
					export ORACLE_SID
				shift 2;;

			-r|--rmanscriptdir)
					RMANSCRIPTDIR=${2}
				shift 2;;

			-l|--logdir)
					RMANLOGDIR=${2}
				shift 2;;

			-t|--targetconnect)
					TARGETCONNECT=${2}
					export TARGETCONNECT
				shift 2;;

			-c|--catalogconnect)
					CATALOGCONNECT=${2}
					export CATALOGCONNECT
				shift 2;;

			--service)
					INSTANCE_SERVICE=${2}
					export INSTANCE_SERVICE
				shift 2;;
			--)
				shift
				break;;
		esac
	done

	if [ -z ${ORACLE_SID} ]
	then
		echo "Missing parameter for ORACLE_SID"
		echo " "
		print_usage
		exit 1
	fi
	
	if [ -z ${rmanbackuptyp} ]
	then
		echo "Missing parameter for action"
		echo " "
		print_usage
		exit 1
	fi
	
	# set NLS_DATE_FORMAT for nice date-format
	export NLS_DATE_FORMAT='dd.mm.yy hh24:mi:ss'

	ORATAB=/etc/oratab

	# getting ORACLE_HOME from oratab
	ORACLE_HOME=`cat ${ORATAB} | grep "^"${ORACLE_SID}":" | cut -d":" -f2`
	# did we found the SID in oratab?
	export ORACLE_HOME

	if [ ! -z ${ORACLE_HOME} ]
	then
		# we could be on Grid-Infrastructure
		# => There is only an entry for the DB_NAME in oratab!
                # => We need to find the right ORACLE_SID from Clusterware
		OCRLOC=/etc/oracle/ocr.loc
		if [ -f $OCRLOC ]
		then
			. $OCRLOC
			. /etc/oracle/olr.loc
			export crs_home
			export SRVCTL=${ORACLE_HOME}/bin/srvctl

			if [ ! -z ${INSTANCE_SERVICE} ]
			then
				check_service
			fi
		fi

		# Some Installations store local_only in uppercase...
		local_only=$(echo ${local_only:-"true"} | tr '[:upper:]' '[:lower:]')

		if [ ${local_only:-"true"} = 'false' ]
		then
			# We are on a real Grid-Infrastructure!
			# => overwrite the ORACLE_SID from command parameterline
			ORACLE_SID=$(${SRVCTL} status instance -d ${ORACLE_SID} -node $(${crs_home}/bin/olsnodes -l) | cut -d" " -f2)
		fi

	else	
		echo "ORACLE_HOME "${ORACLE_SID}" not found in "${ORATAB}
		print_syslog "ORACLE_SID "${ORACLE_SID}" not found in "${ORATAB}
		abort_script 10
		
	fi

	if [ ! -d ${ORACLE_HOME:-"leer"} ]
	then
		# ORACLE_HOME not existing or ORACLE_SID not availible
		# => we need to exit the script!
		echo "ORACLE_HOME "${ORACLE_HOME}" not found in "${ORATAB}
		print_syslog "ORACLE_HOME "${ORACLE_HOME}" not found in "${ORATAB}
		abort_script 11
	else
		export ORACLE_HOME
	fi


	orabase=${ORACLE_HOME}/bin/orabase
	# Do we have an executable for getting the current ORACLE_BASE?
	# This script is not availible for Oracle <11g. :-(
	if [ -x ${orabase} ]
	then
		ORACLE_BASE=`${orabase}` > /dev/null
	fi

	# do we have a valid ORACLE_BASE?
	if [ ! -d ${ORACLE_BASE:-"leer"} ]
	then
		echo "We cannot work without ORACLE_BASE="${ORACLE_BASE}
		print_syslog "We cannot work without ORACLE_BASE="${ORACLE_BASE}
		abort_script 12
	fi
	export ORACLE_BASE

	# where are the rman-skripts?
	# we have the option with RMANSCRIPTDIR for a dedicated directory
	if [ ! -d ${RMANSCRIPTDIR:-"leer"}  ]
	then
		# Do we have a rman-Skript for doing the backup?
		# The skript must be located in $ORACLE_BASE/admin/ORACLE_SID/rman/<Skript>.rman

		RMANSCRIPTDIR=${ORACLE_BASE}/admin/${ORACLE_SID}/rman
	fi

	if [ ! -z ${RMANTNS_ADMIN} ]
	then
		echo "Setting TNS_ADMIN from RMANTNS_ADMIN to: "${RMANTNS_ADMIN}
		export TNS_ADMIN=${RMANTNS_ADMIN}
	fi

	rmanskript=${RMANSCRIPTDIR}/${rmanbackuptyp}.rman

	rmanlog=${RMANLOGDIR}/${ORACLE_SID}_${rmanbackuptyp}.log

	if [ ! ${CATALOGCONNECT:-"leer"} = 'leer' ]
	then
		check_catalog
	else
		print_syslog "Using no Catalog for Backup!"
		catalogconnect=''
	fi
}

check_requirements()
{
	if [ ! -d ${RMANLOGDIR} ]
	then
		echo "Directory "${RMANLOGDIR}" for RMAN logfiles not existing."
		print_syslog "Directory "${RMANLOGDIR}" for RMAN logfiles not existing."
		abort_script 21
	fi

	if [ ! -f ${rmanskript} ]
	then
		echo "RMAN-script "${rmanskript}" not existing!"
		print_syslog "RMAN-script "${rmanskript}" not existing!"
		abort_script 22
	fi

	touch ${rmanlog}
	if [ ! -f ${rmanlog} ]
	then
		echo "Logfile "${rmanlog}" for RMAN could not be created."
		print_syslog "Logfile "${rmanlog}" for RMAN could not be created."
		abort_script 23
	fi
}

do_backup()
{
	# tee, damit alle Ausgaben weg geschrieben werden.
	${ORACLE_HOME}/bin/rman \
<< _EOF_  | tee -a ${rmanlog}
	connect target ${TARGETCONNECT:-"/"}
	${catalogconnect}
@${rmanskript}
_EOF_
	retcode=${PIPESTATUS[0]}
	if [ ${retcode} -eq 0 ]
	then
		print_syslog "RMAN Backup successful. Logfile "${rmanlog}
	else
		echo "RMAN return code "${retcode}". Please check logfile "${rmanlog}
		print_syslog "RMAN return code "${retcode}". Please check logfile "${rmanlog}
		abort_script 99
	fi
	return ${retcode}
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
retcode=${?}
print_syslog "End Code="${retcode}
exit ${retcode}
