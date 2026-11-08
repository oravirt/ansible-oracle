#!/usr/bin/env bash
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
# Configuration
# =============
# The settings are read in the following order (the 1st value wins):
#   1. parameters on the command line
#   2. environment variables
#   3. configuration file <ORACLE_ADMIN>/rman/rman_backup.cfg
#   4. defaults of the script
#
# ORACLE_ADMIN is determined in the following order:
#   1. --admin on the command line or environment variable ORACLE_ADMIN
#   2. <ORACLE_BASE>/admin/<db_unique_name> (db_unique_name from the running instance)
#   3. <ORACLE_BASE>/admin/<ORACLE_SID|DB_NAME>
#
# The configuration file contains lines with KEY=VALUE (no shell code, it is not sourced).
# Allowed keys: see CFG_KEYS below or the help of the script (-h).
# The file could contain the password of the RMAN catalog => mode 0600.
#
# Backup
# ======
# The RMAN script <RMAN_SCRIPTDIR>/<action>.rman is executed.
# The script checks for the catalog. When the catalog is not reachable the backup
# will run without a catalog.
#
# Logging
# =======
# All output of the script and RMAN is written to stdout and to a logfile per execution:
#   <RMAN_LOGDIR>/<db_unique_name>_<action>_<YYYYmmdd>_<HHMMSS>_<pid>.log
# The symlink <RMAN_LOGDIR>/<db_unique_name>_<action>.log points to the logfile of the
# last execution. Logfiles older than RMAN_LOG_RETENTION days are removed (0: keep all).
# => cron could redirect the output to /dev/null.
# Major actions and errors before the logfile is opened are logged in syslog.
#
# Parallel executions of the same action for a database are not allowed (flock):
# the 2nd execution stops with exit code 30.
#
# Exit codes:
#   0     RMAN successful or backup skipped (service not running on this node,
#         --role does not match the database role)
#   1     wrong parameters or service not existing
#   10-12 ORACLE_SID, ORACLE_HOME or ORACLE_BASE not found
#   13    database role could not be determined (--role)
#   14    configuration file not readable
#   21-23 log directory, RMAN script or logfile not existing
#   30    the action is running already for the database
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
CFGNAME=rman_backup.cfg

# keys of the configuration file (= environment variables)
CFG_KEYS="RMAN_SCRIPTDIR RMAN_LOGDIR RMAN_LOG_RETENTION RMAN_TARGETCONNECT RMAN_CATALOGCONNECT RMAN_SERVICE RMAN_ROLE RMAN_TNS_ADMIN"

# output before the logfile is opened (written to the logfile afterwards)
early_log=''
log_open=false

function print_usage() {
	echo "Usage:"
	echo "  $PROGNAME -a <action> [-s <ORACLE_SID|DB_NAME>] [--admin <Directory>]"
	echo "            [-r <Directory>] [-l <Directory>] [-c <CATALOGCONNECT>] [-t <TARGETCONNECT>]"
	echo "            [--service <Servicename in GI/Restart>] [--role <PRIMARY|STANDBY>] [--nocatalog]"
	echo "  $PROGNAME -h"
}

function print_help() {
	echo ""
	print_usage
	echo ""
	echo "RMAN Backupscript"
	echo ""
	echo "Parameter             Environment / configuration file"
	echo "-a/--action           -                    Name of the .rman-Script without extension (mandatory)"
	echo "-s/--ORACLE_SID       ORACLE_SID           ORACLE_SID / DB_NAME (RAC) of Database"
	echo "                                            Please use the DB_NAME from oratab in RAC-Environments!"
	echo "--admin               ORACLE_ADMIN         Admin directory of the database"
	echo "                                            Default: <ORACLE_BASE>/admin/<db_unique_name>"
	echo "                                            db_unique_name from the running instance,"
	echo "                                            <ORACLE_SID|DB_NAME> when the instance is not running"
	echo "-r/--rmanscriptdir    RMAN_SCRIPTDIR       Directory for *.rman-Scripts"
	echo "                                            Default: <ORACLE_ADMIN>/rman"
	echo "-l/--logdir           RMAN_LOGDIR          Directory for the logfiles"
	echo "                                            Default: <RMAN_SCRIPTDIR>/log"
	echo "-                     RMAN_LOG_RETENTION   Remove logfiles older than <n> days, 0: keep all"
	echo "                                            Default: 30"
	echo "-c/--catalogconnect   RMAN_CATALOGCONNECT  connect catalog <catalogconnect>"
	echo "                                            Use the configuration file for passwords,"
	echo "                                            parameters are visible in the process list!"
	echo "--nocatalog           -                    Do not use the catalog (overrides RMAN_CATALOGCONNECT)"
	echo "-t/--targetconnect    RMAN_TARGETCONNECT   connect target <targetconnect>, Default: /"
	echo "--service             RMAN_SERVICE         Execute rman when Service in GI/Restart is running on current node."
	echo "--role                RMAN_ROLE            Execute rman only when the database has this role (Data Guard)."
	echo "                                            PRIMARY: database_role PRIMARY"
	echo "                                            STANDBY: database_role PHYSICAL STANDBY"
	echo "-                     RMAN_TNS_ADMIN       TNS_ADMIN for RMAN (e.g. catalog)"
	echo ""
	echo "Order of the settings (the 1st value wins):"
	echo "  parameter, environment, <ORACLE_ADMIN>/rman/${CFGNAME}, default"
	echo ""
	echo "${CFGNAME} contains lines with KEY=VALUE, e.g.:"
	echo "  RMAN_CATALOGCONNECT=rman/password@rmancat"
	echo "  RMAN_ROLE=PRIMARY"
	echo ""
	echo "Logfile: <RMAN_LOGDIR>/<db_unique_name>_<action>_<YYYYmmdd>_<HHMMSS>_<pid>.log"
	echo "         symlink <db_unique_name>_<action>.log to the last execution"
	echo ""
	echo "The old environment variables RMANSCRIPTDIR, RMANLOGDIR, CATALOGCONNECT,"
	echo "TARGETCONNECT and RMANTNS_ADMIN are still supported."
}

print_syslog() {
	# Don't write to syslog when logger is not there
	if command -v logger > /dev/null 2>&1; then
		logger -t "${PROGNAME}" -- "${*}"
	fi
}

# message to stdout, buffered until the logfile is opened
say() {
	echo "${*}"
	if [ "${log_open}" = 'false' ]; then
		early_log+="${*}"$'\n'
	fi
}

# message to stdout and syslog
print_msg() {
	say "${*}"
	print_syslog "${*}"
}

abort_script() {
	print_syslog "Abort Code=${1}"
	exit "${1}"
}

# Execute SQL with a bequeath connection (no listener, no password) and
# print the value of the 1st line starting with <prefix>=
# $1: prefix, $2: SQL
query_value() {
	"${ORACLE_HOME}/bin/sqlplus" -S -L /nolog << _EOF_ 2>&1 | sed -n "s/^${1}=//p" | head -1
whenever sqlerror exit failure
connect / as sysdba
set heading off feedback off pagesize 0 linesize 1000
${2}
_EOF_
}

# cli_* variables are read indirectly in setenv_rman (${!cli_var})
# shellcheck disable=SC2034
parse_args() {
	SHORTOPTS="ha:s:r:l:t:c:"
	LONGOPTS="help,action:,ORACLE_SID:,admin:,rmanscriptdir:,logdir:,targetconnect:,catalogconnect:,nocatalog,service:,role:"

	if ! ARGS=$(getopt -s bash --options "${SHORTOPTS}" --longoptions "${LONGOPTS}" --name "${PROGNAME}" -- "$@"); then
		print_usage
		exit 1
	fi

	eval set -- "${ARGS}"

	# values from the command line, applied after the configuration file
	while true; do
		case "$1" in
			-h|--help)
				print_help
				exit 0;;
			-a|--action)
				rmanbackuptyp=${2}
				shift 2;;
			-s|--ORACLE_SID)
				cli_ORACLE_SID=${2}
				shift 2;;
			--admin)
				cli_ORACLE_ADMIN=${2}
				shift 2;;
			-r|--rmanscriptdir)
				cli_RMAN_SCRIPTDIR=${2}
				shift 2;;
			-l|--logdir)
				cli_RMAN_LOGDIR=${2}
				shift 2;;
			-t|--targetconnect)
				cli_RMAN_TARGETCONNECT=${2}
				shift 2;;
			-c|--catalogconnect)
				cli_RMAN_CATALOGCONNECT=${2}
				shift 2;;
			--nocatalog)
				nocatalog=true
				shift;;
			--service)
				cli_RMAN_SERVICE=${2}
				shift 2;;
			--role)
				cli_RMAN_ROLE=${2}
				shift 2;;
			--)
				shift
				break;;
		esac
	done

	if [ -z "${rmanbackuptyp}" ]; then
		echo "Missing parameter for action"
		echo " "
		print_usage
		exit 1
	fi
}

# old environment variables => new names (when the new variable is not set)
legacy_env() {
	RMAN_SCRIPTDIR=${RMAN_SCRIPTDIR:-${RMANSCRIPTDIR}}
	RMAN_LOGDIR=${RMAN_LOGDIR:-${RMANLOGDIR}}
	RMAN_CATALOGCONNECT=${RMAN_CATALOGCONNECT:-${CATALOGCONNECT}}
	RMAN_TARGETCONNECT=${RMAN_TARGETCONNECT:-${TARGETCONNECT}}
	RMAN_TNS_ADMIN=${RMAN_TNS_ADMIN:-${RMANTNS_ADMIN}}
}

setenv_oracle() {
	ORACLE_SID=${cli_ORACLE_SID:-${ORACLE_SID}}
	if [ -z "${ORACLE_SID}" ]; then
		echo "Missing parameter for ORACLE_SID (-s or environment variable ORACLE_SID)"
		echo " "
		print_usage
		exit 1
	fi

	# set NLS_DATE_FORMAT for nice date-format
	export NLS_DATE_FORMAT='dd.mm.yy hh24:mi:ss'

	# ORACLE_SID or DB_NAME (RAC) from command line, used for srvctl and the default directories
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
	local_only=''
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
			node_sid=$("${SRVCTL}" status instance -d "${DB_NAME}" -node "$("${crs_home}/bin/olsnodes" -l)" | cut -d" " -f2)
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
}

# ORACLE_ADMIN: parameter, environment, db_unique_name of the running instance, ORACLE_SID/DB_NAME
setenv_admin() {
	ORACLE_ADMIN=${cli_ORACLE_ADMIN:-${ORACLE_ADMIN}}
	if [ -z "${ORACLE_ADMIN}" ]; then
		db_unique_name=$(query_value UNIQUE "select 'UNIQUE=' || value from v\$parameter where name = 'db_unique_name';")
		if [ -n "${db_unique_name}" ]; then
			ORACLE_ADMIN="${ORACLE_BASE}/admin/${db_unique_name}"
		else
			say "db_unique_name of ${ORACLE_SID} could not be determined (instance not running?)."
			ORACLE_ADMIN="${ORACLE_BASE}/admin/${DB_NAME}"
		fi
	fi
	say "ORACLE_ADMIN: ${ORACLE_ADMIN}"
}

# Read KEY=VALUE from the configuration file.
# A value is only set, when the variable is not set in the environment.
read_config() {
	cfgfile="${ORACLE_ADMIN}/rman/${CFGNAME}"

	if [ ! -e "${cfgfile}" ]; then
		say "No configuration file ${cfgfile}"
		return
	fi

	if [ ! -r "${cfgfile}" ]; then
		print_msg "Configuration file ${cfgfile} not readable."
		abort_script 14
	fi

	if [ -n "$(find "${cfgfile}" -perm /077 2>/dev/null)" ]; then
		print_msg "WARNING: ${cfgfile} is readable by other users (mode 0600 recommended)."
	fi

	say "Configuration file: ${cfgfile}"
	while IFS= read -r line || [ -n "${line}" ]; do
		line=${line%$'\r'}
		# remove leading whitespace, skip empty lines and comments
		line="${line#"${line%%[![:space:]]*}"}"
		if [ -z "${line}" ] || [[ "${line}" == \#* ]]; then
			continue
		fi

		if [[ ! "${line}" =~ ^([A-Z_]+)=(.*)$ ]]; then
			print_msg "WARNING: invalid line in ${cfgfile} ignored: ${line%%=*}"
			continue
		fi
		key=${BASH_REMATCH[1]}
		value=${BASH_REMATCH[2]}

		case " ${CFG_KEYS} " in
			*" ${key} "*) ;;
			*)
				print_msg "WARNING: unknown key ${key} in ${cfgfile} ignored"
				continue;;
		esac

		# remove one pair of quotes around the value
		if [[ "${value}" =~ ^\"(.*)\"$ ]] || [[ "${value}" =~ ^\'(.*)\'$ ]]; then
			value=${BASH_REMATCH[1]}
		fi

		# environment wins
		if [ -z "${!key}" ]; then
			printf -v "${key}" '%s' "${value}"
		fi
	done < "${cfgfile}"
}

# parameters from the command line win, defaults for unset values
setenv_rman() {
	for key in ${CFG_KEYS}; do
		cli_var="cli_${key}"
		if [ -n "${!cli_var}" ]; then
			printf -v "${key}" '%s' "${!cli_var}"
		fi
	done

	RMAN_SCRIPTDIR=${RMAN_SCRIPTDIR:-${ORACLE_ADMIN}/rman}
	RMAN_LOGDIR=${RMAN_LOGDIR:-${RMAN_SCRIPTDIR}/log}
	RMAN_TARGETCONNECT=${RMAN_TARGETCONNECT:-/}
	RMAN_LOG_RETENTION=${RMAN_LOG_RETENTION:-30}
	if [[ ! "${RMAN_LOG_RETENTION}" =~ ^[0-9]+$ ]]; then
		print_msg "WARNING: invalid RMAN_LOG_RETENTION ${RMAN_LOG_RETENTION}, using 30 days"
		RMAN_LOG_RETENTION=30
	fi
	RMAN_ROLE=$(echo "${RMAN_ROLE}" | tr '[:lower:]' '[:upper:]')

	if [ -n "${RMAN_TNS_ADMIN}" ]; then
		say "Setting TNS_ADMIN from RMAN_TNS_ADMIN to: ${RMAN_TNS_ADMIN}"
		export TNS_ADMIN="${RMAN_TNS_ADMIN}"
	fi

	rmanskript="${RMAN_SCRIPTDIR}/${rmanbackuptyp}.rman"

	# name of the logfiles and the lock: db_unique_name or the name of ORACLE_ADMIN
	log_id="${db_unique_name:-$(basename "${ORACLE_ADMIN}")}_${rmanbackuptyp}"
}

# Called at the end of the script (trap EXIT in open_log), also after exit in abort_script.
# tee runs as own process and writes the last lines after the script has finished, when we
# do not wait for it => the end of the logfile would be missing or appear after the prompt.
# shellcheck disable=SC2329
finish_log() {
	if [ "${log_open}" = 'true' ]; then
		# connect stdout/stderr to the saved file descriptors (terminal or cron) again
		# => the pipe to tee is closed, tee gets EOF, writes the rest and terminates
		exec 1>&3 2>&4
		# wait until tee has written everything to the logfile
		wait "${tee_pid}" 2>/dev/null
	fi
}

# stdout and stderr => terminal and logfile of the execution
open_log() {
	if [ ! -d "${RMAN_LOGDIR}" ]; then
		print_msg "Directory ${RMAN_LOGDIR} for RMAN logfiles not existing."
		abort_script 21
	fi

	rmanlog="${RMAN_LOGDIR}/${log_id}_$(date '+%Y%m%d_%H%M%S')_$$.log"
	if ! printf '%s' "${early_log}" >> "${rmanlog}"; then
		print_msg "Logfile ${rmanlog} for RMAN could not be created."
		abort_script 23
	fi

	# Redirect all output of the script to terminal and logfile (like '| tee', but for the
	# whole script instead of a single command):
	#
	# 1. Save the current stdout (fd 1) and stderr (fd 2) as fd 3 and fd 4.
	#    They point to the terminal for a manual execution or /dev/null in cron.
	#    finish_log restores them at the end.
	exec 3>&1 4>&2
	# 2. 'exec' without a command changes the file descriptors of the running shell itself,
	#    from here on for all commands of the script (echo, sqlplus, rman, ...).
	#    '>(tee -a <logfile>)' is a process substitution: bash starts 'tee' as a separate
	#    background process and provides its stdin as a file (pipe), e.g. /dev/fd/63.
	#    '> /dev/fd/63' sends stdout into the pipe, '2>&1' sends stderr to the same place.
	#    tee copies everything it reads to its own stdout (= the saved terminal/cron output)
	#    and appends it to the logfile.
	exec > >(tee -a "${rmanlog}") 2>&1
	# 3. $! is the PID of the last background process = tee from the process substitution,
	#    needed for 'wait' in finish_log.
	tee_pid=$!
	log_open=true
	# 4. finish_log runs at every end of the script (normal end, exit, abort_script)
	trap finish_log EXIT
	echo "Logfile: ${rmanlog}"
}

# only one execution of an action for a database
lock_action() {
	lockfile="${RMAN_LOGDIR}/.${log_id}.lock"
	exec 9>> "${lockfile}"
	if ! flock -n 9; then
		print_msg "${rmanbackuptyp} is running already for ${log_id%_"${rmanbackuptyp}"} (lock ${lockfile}). Aborting!"
		abort_script 30
	fi

	# symlink to the logfile of the last execution
	# an existing logfile of older versions (appended on every execution) is kept as *.log.old
	latest="${RMAN_LOGDIR}/${log_id}.log"
	if [ -f "${latest}" ] && [ ! -L "${latest}" ]; then
		mv "${latest}" "${latest}.old"
		echo "Old logfile moved to ${latest}.old"
	fi
	ln -sfn "$(basename "${rmanlog}")" "${latest}"

	# remove old logfiles of the action
	if [ "${RMAN_LOG_RETENTION}" -gt 0 ]; then
		find "${RMAN_LOGDIR}" -maxdepth 1 -type f -name "${log_id}_[0-9]*_[0-9]*_[0-9]*.log" \
			-mtime "+${RMAN_LOG_RETENTION}" -print -delete
	fi
}

check_service() {
	if [ -z "${RMAN_SERVICE}" ]; then
		return
	fi

	if [ -z "${SRVCTL}" ]; then
		print_msg "Service ${RMAN_SERVICE} could not be checked without Grid-Infrastructure/Oracle Restart."
		abort_script 1
	fi

	# get data from srvctl for service
	echo "Checking for running service ${RMAN_SERVICE} on current node"
	retstr=$("${SRVCTL}" status service -d "${DB_NAME}" -s "${RMAN_SERVICE}")
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
			print_msg "Service ${RMAN_SERVICE} not running on current node. Skipping backup!"
			exit 0
		fi
	else
		running_instances=$(echo "${retstr}" | sed -e 's/^Service .* is running on instance(s)//g' -e 's/ //g')
		if [ ! "${node_sid}" = "${running_instances}" ]; then
			print_msg "Service ${RMAN_SERVICE} not running on current node. Skipping backup!"
			exit 0
		fi
	fi
}

check_role() {
	if [ -z "${RMAN_ROLE}" ]; then
		return
	fi

	# role from the local instance (bequeath connection, no listener needed)
	case "${RMAN_ROLE}" in
		PRIMARY) expected_role='PRIMARY';;
		STANDBY) expected_role='PHYSICAL STANDBY';;
		*)
			echo "Invalid value for --role/RMAN_ROLE: ${RMAN_ROLE} (PRIMARY or STANDBY)"
			print_usage
			exit 1;;
	esac

	database_role=$(query_value ROLE "select 'ROLE=' || database_role from v\$database;")

	if [ -z "${database_role}" ]; then
		print_msg "Database role of ${ORACLE_SID} could not be determined (instance not mounted?)."
		abort_script 13
	fi

	if [ ! "${database_role}" = "${expected_role}" ]; then
		print_msg "Database role of ${ORACLE_SID} is ${database_role}, not ${expected_role}. Skipping backup!"
		exit 0
	fi
	print_syslog "Database role of ${ORACLE_SID} is ${database_role}."
}

check_catalog() {
	catalogconnect=''
	if [ -z "${RMAN_CATALOGCONNECT}" ] || [ "${nocatalog}" = 'true' ]; then
		print_syslog "Using no Catalog for Backup!"
		return
	fi

	# check for availible catalog
	# catalog not working => switch to nocatalog!
	print_syslog "Check for working RMAN Catalog"
	if "${ORACLE_HOME}/bin/rman" << _EOF_
connect target ${RMAN_TARGETCONNECT}
connect catalog ${RMAN_CATALOGCONNECT}
_EOF_
	then
		catalogconnect="connect catalog ${RMAN_CATALOGCONNECT}"
		print_syslog "Using Catalog for Backup!"
	else
		print_msg "Catalog not reachable. Working without Catalog!"
	fi
}

check_requirements() {
	if [ ! -f "${rmanskript}" ]; then
		print_msg "RMAN-script ${rmanskript} not existing!"
		abort_script 22
	fi
}

do_backup() {
	"${ORACLE_HOME}/bin/rman" << _EOF_
connect target ${RMAN_TARGETCONNECT}
${catalogconnect}
@${rmanskript}
_EOF_
	retcode=$?
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
parse_args "$@"
legacy_env
setenv_oracle
setenv_admin
read_config
setenv_rman
open_log
lock_action
check_service
check_role
check_requirements
check_catalog
do_backup
print_syslog "End Code=0"
exit 0
