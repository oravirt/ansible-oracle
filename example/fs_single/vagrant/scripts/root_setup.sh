#!/usr/bin/env bash

# shellcheck source=/dev/null
. /vagrant/scripts/setenv.sh
sh /vagrant/scripts/set_hostname.sh
sh /vagrant/scripts/set_keyboard.sh
sh /vagrant/scripts/prepare_u01_disk.sh
sh /vagrant/scripts/install_os_packages.sh

