#!/usr/bin/env bash
#
#
set -eu
set -o pipefail

workdir=$(dirname -- "$( readlink -f -- "$0"; )";)

install_python()
{
  if test -f /etc/oracle-release ; then
    # https://yum.oracle.com/oracle-linux-python.html
    sudo dnf -y module install python39
    sudo dnf -y install python39-pip

    # install libselinux-python3 for ansible
    sudo dnf install -y python3-libselinux
  fi
}

setup_venv()
{
  /usr/bin/python3.9 -m venv ~/venv/ansible-oracle

  # shellcheck source=/dev/null
  . ~/venv/ansible-oracle/bin/activate
  pip install --upgrade pip
}

setup_ansible()
{
  echo "Install Ansible with pip3"
  echo "$workdir"
  pip3 install -r "$workdir/requirements_ansible.txt"
}

cd "$workdir"
echo "working directory: $(pwd)"

install_python
setup_venv
setup_ansible
