#!/usr/bin/env bash
#
# Check if the permanent firewalld config allows SSH connections on the
# interface/port of the current SSH connection.
# Starting firewalld activates its permanent config, so this must be checked
# before firewalld is started, to not block new SSH connections of Ansible.
#
# Usage: firewall_check_ssh.sh [<server ip> <server port>]
#        Without arguments the values are taken from SSH_CONNECTION.
#
# Exit codes: 0 = SSH allowed or firewalld running, 1 = SSH not allowed
#
# Limitation: Rich rules and zones bound to sources are not evaluated.
set -eu
set -o pipefail

if [ $# -eq 2 ]; then
  server_ip=$1
  server_port=$2
else
  # SSH_CONNECTION: <client ip> <client port> <server ip> <server port>
  read -r _ _ server_ip server_port <<< "${SSH_CONNECTION:?Usage: $0 <server ip> <server port>}"
fi

if systemctl is-active --quiet firewalld; then
  echo "firewalld is running"
  exit 0
fi

dev=$(ip -o addr show | awk -v ip="$server_ip" '{split($4, a, "/"); if (a[1] == ip) print $2}' | head -1)

# Zone of interface: NetworkManager connection => firewalld config => default zone
zone=""
if [ -n "$dev" ]; then
  con=$(nmcli -g GENERAL.CONNECTION device show "$dev" 2>/dev/null) || con=""
  if [ -n "$con" ]; then
    zone=$(nmcli -g connection.zone connection show "$con" 2>/dev/null) || zone=""
  fi
  if [ -z "$zone" ]; then
    zone=$(firewall-offline-cmd --get-zone-of-interface="$dev" 2>/dev/null) || zone=""
  fi
fi
if [ -z "$zone" ]; then
  zone=$(firewall-offline-cmd --get-default-zone)
fi

echo "interface: ${dev:-unknown}, zone: ${zone}, ssh port: ${server_port}/tcp"

if [ "$(firewall-offline-cmd --zone="$zone" --get-target)" = "ACCEPT" ]; then
  echo "zone target ACCEPT"
  exit 0
fi
if [ "$server_port" = "22" ] && firewall-offline-cmd --zone="$zone" --query-service=ssh >/dev/null; then
  echo "service ssh allowed"
  exit 0
fi
if firewall-offline-cmd --zone="$zone" --query-port="${server_port}/tcp" >/dev/null; then
  echo "port ${server_port}/tcp allowed"
  exit 0
fi

echo "SSH is not allowed in permanent firewalld config"
exit 1
