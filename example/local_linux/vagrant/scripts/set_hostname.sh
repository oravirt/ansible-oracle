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

set_host_domain "${THE_HOSTNAME}" "${THE_DOMAINNAME}"

