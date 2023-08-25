#!/usr/bin/env bash
function set_host_domain ()
{
  MY_HOSTNAME="${1}"
  MY_DOMAINNAME="${2}"
  echo "******************************************************************************"
  echo "Set hostname:${MY_HOSTNAME}.${MY_DOMAINNAME} $(date)"
  echo "******************************************************************************"
     hostname "${MY_HOSTNAME}.${MY_DOMAINNAME}"                       # applied immediately, not valid after reboot
     hostnamectl set-hostname "${MY_HOSTNAME}.${MY_DOMAINNAME}"       # valid after reboot
     domainname "${MY_DOMAINNAME}"                                    # applied immediately, not valid after reboot
     echo "Show short hostname:$(hostname -s)"
     echo "Show fqdn hostname:$(hostname --fqdn)"
     echo "Show domainname:$(domainname)"
}

function setup_hosts ()
{
# DEFDEV is the default network device (e.g. eth1)
DEFDEV=$(/sbin/ip route list|grep default|awk 'NR==1 {FS=" "; print $5}')
# now get the IP address of the default network device
IPADDR=$( /sbin/ip addr show "${DEFDEV}" |grep inet |grep -v inet6|awk '{print $2}'|awk -F/ 'NR==1 {print $1}')

# if not already in the /etc/hosts, let's add an entry for this machine
if [ "$(grep -c $(hostname --fqdn) /etc/hosts)" -eq 0 ]; then
   echo "updating /etc/hosts"
cat >> /etc/hosts << HOST_EOF
${IPADDR}   $(hostname --fqdn)   $(hostname -s)
HOST_EOF
fi
}



set_host_domain "${THE_HOSTNAME}" "${THE_DOMAINNAME}"
setup_hosts
