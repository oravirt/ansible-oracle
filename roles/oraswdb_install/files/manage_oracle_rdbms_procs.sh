#!/bin/bash
#
# Date: 10.11.2018
#
# Thorsten Bruhns (thorsten.bruhns@googlemail.com)
#
# The startup-scritp is bundled with ansible-oracle
# The .profile_<ORACLE_SID> files are needed for starting listeners
#
# Limitations:
#  - 1 Listener per Instance
#    An Instance can only start 1 Listener. Multieple Listeners inside
#    an ORACLE_HOME are possible, when an Instance is existing for each
#    Listener
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


PROGNAME=`basename $0`
PROGPATH=`echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,'`

function print_usage() {
    echo "Usage:"
    echo "  $PROGNAME -a <start|stop> [-m abort|immediate] [-s SID] [-h]"
}

function print_help() {
    echo ""
    print_usage
    echo ""
    echo "Start/Stop Oracle Listeners and Instances on Host"
    echo ""
    echo "-a/--action <start|stop> Start/Stop of all components"
    echo "-m/--mode <abort|immediate> Shutdown Mode for all databases"
    echo "-s/--ORACLE_SID SID of database to perform action on"
}

setenv()
{
    SHORTOPTS="ha:m:s:"
    LONGOPTS="help,action:mode:,ORACLE_SID:"

    ARGS=$(getopt -s bash --options $SHORTOPTS  --longoptions $LONGOPTS --name $PROGNAME -- "$@" ) 
    if [ ${?} -ne 0 ] ; then
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
                  global_action=${2}
                  export global_action
                  shift 2;;

              -m|--mode)
                  global_dbmode=${2}
                  export global_dbmode
                  shift 2;;
    
              -s|--ORACLE_SID)
                  SID=${2}
                  export SID
                  shift 2;;
    
              --)
                  shift
                  break;;
        esac
    done
}

function start_database() {

    ORACLE_HOME=${1}
    ORACLE_SID=${2}
    ORA_STARTMODE=${3}
    echo "########################################"
    echo "ORACLE_HOME: "${ORACLE_HOME}
    echo "ORACLE_SID : "${ORACLE_SID}

    # Check for SPFile/PFile
    test -f ${ORACLE_HOME}/dbs/spfile${ORACLE_SID}.ora || test -f ${ORACLE_HOME}/dbs/init${ORACLE_SID}.ora
    if [ ${?} -ne 0 ] ; then
        echo "no parameter file found."
        echo "Skipping entry in oratab!"
        return 1
    fi

    if [ ! -z "${global_dbmode}" ] ; then

        DB_STARTMODE=${global_dbmode}
        STARTDB=Y

    elif [ ${ORA_STARTMODE} = 'Y' ] ; then

        # 'Y' => Startup open
        DB_STARTMODE=""
        STARTDB=Y

    elif [ ${ORA_STARTMODE} = 'M' ] ; then

        DB_STARTMODE='MOUNT'
        STARTDB=Y

    fi

    if [ ${STARTDB:-"N" = "Y" } ] ; then

        # Using RMAN for startup
        # => easy to switch from mount to open for running instance during execution
        echo "startup ${DB_STARTMODE}" | ${ORACLE_HOME}/bin/rman  target /

    else
        echo "Skipping Oracle Instance: "${ORACLE_SID}" due to Startmode "${ORA_STARTMODE}
    fi
}

function stop_database() {

    ORACLE_HOME=${1}
    ORACLE_SID=${2}
    ORA_STOPMODE=${3}
    echo "########################################"
    # check for pmon
    ps ax | grep "[0-9] ora_pmon_${ORACLE_SID}$" > /dev/null 2>&1
    if [ ${?} -ne 0 ] ; then
        echo "Instance "${ORACLE_SID}" not running"
        return
    else
        echo "Stopping Oracle Instance: "${ORACLE_SID}" with rman"

        # Using RMAN for startup
        # => easy to switch from mount to open for running instance during execution
        echo "shutdown "${ORA_STOPMODE} | ${ORACLE_HOME}/bin/rman  target /

    fi
}

function start_listener() {
    ORACLE_HOME=${1}
    LSNRNAME=${2}
    echo "checking Listener: "${LSNRNAME}" in ORACLE_HOME: "${ORACLE_HOME}
    ORACLE_BASE=$(${ORACLE_HOME}/bin/orabase)
    ${ORACLE_HOME}/bin/lsnrctl status ${LSNRNAME} > /dev/null 2>&1
    if [ ${?} -eq 0 ] ; then
        echo "Listener still running"
    else
        ${ORACLE_HOME}/bin/lsnrctl start ${LSNRNAME}
    fi
}

function stop_listener() {
    ORACLE_HOME=${1}
    LSNRNAME=${2}
    echo "checking Listener: "${LSNRNAME}" in ORACLE_HOME: "${ORACLE_HOME}
    ORACLE_BASE=$(${ORACLE_HOME}/bin/orabase)
    ${ORACLE_HOME}/bin/lsnrctl status ${LSNRNAME} > /dev/null 2>&1
    if [ ${?} -eq 0 ] ; then
        ${ORACLE_HOME}/bin/lsnrctl stop ${LSNRNAME}
    else
        echo "Listener not running"
    fi
}

function do_sidline() {
    sidline=${1}

    ORA_SID=$(echo $sidline | cut -d":" -f1)
    ORA_HOME=$(echo $sidline | cut -d":" -f2)
    ORA_STARTMODE=$(echo $sidline | cut -d":" -f3)
    ORA_OWNER=$(stat -c '%U' ${ORA_HOME/bin/oracle})
    PROFILE_FILE=$(getent passwd ${ORA_OWNER} | cut -d":" -f6)/.profile_${ORA_SID}

    if [ ${ORA_OWNER:-"_"} != $(id -n -u) ] ; then
        echo "Script started with wrong user."
        echo "current user : "$(id -n -u)
        echo "expected user: "${ORA_OWNER}
        exit 50
    fi

    if [ ${global_action:-"unknown"} = "unknown" ] ; then

        echo "no action found on command line."
        print_usage
        exit 99

    elif [ ${global_action:-"unknown"} = "start" ] ; then

        echo "########################################"
        test -f ${PROFILE_FILE} && . ${PROFILE_FILE} > /dev/null
        if [ ${?} -eq 0 ] ; then
            echo "working on profile: "${PROFILE_FILE}
            # listener need the LSNRNAME from .profile_!
            start_listener ${ORA_HOME} ${LSNRNAME}
        fi

        start_database ${ORA_HOME} ${ORA_SID} ${ORA_STARTMODE}

    elif [ ${global_action:-"unknown"} = "stop" ] ; then

        echo "########################################"
        echo "working on profile: "${PROFILE_FILE}
        test -f ${PROFILE_FILE} && . ${PROFILE_FILE} > /dev/null
        stop_database ${ORA_HOME} ${ORA_SID} ${global_dbmode:-"immediate"}

        test -f ${PROFILE_FILE} && . ${PROFILE_FILE} > /dev/null
        if [ ${?} -eq 0 ] ; then
            echo "working on profile: "${PROFILE_FILE}
            # listener need the LSNRNAME from .profile_!
            stop_listener ${ORA_HOME} ${LSNRNAME}
        fi


    else

        echo "wrong action found on command line."
        print_usage
        exit 99

    fi
}

setenv $*
if [[ ! -z "${SID}" ]] ; then
  filter_SID=${SID}
  grep "^${filter_SID}:" /etc/oratab > /dev/null 2>&1
  if [ $? -ne 0 ] ; then
    echo "Could not find an SID in /etc/oratab for ${SID}"
    print_usage
  fi
else
  filter_SID=".*"
fi

for sidline in $(cat /etc/oratab | grep -v "^#" | grep "^${filter_SID}:" ) ; do
  echo "for ${sidline}"
  do_sidline ${sidline}
done


