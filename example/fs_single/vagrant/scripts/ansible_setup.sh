#!/usr/bin/env bash
###########################################################################################
# This script calls ansible-oracle to install the oracle database
###############################################################################

# Make code more robust
###############################################################################
# Stop immediately if a variable is referenced in this script but not defined 
set -u


function setup_packages ()
{
echo "Install Python3.6 now (python3.9 installed later for ansible controller)"
yum install -y python3
# yum install -y python39

echo "Installing git"
yum install -y git
}


function python_alternatives ()
{
echo "configuring alternatives for python"
update-alternatives --remove-all python
update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1
update-alternatives --install /usr/bin/python python /usr/bin/python3.9 2
update-alternatives --install /usr/bin/python python /usr/libexec/no-python 3
# choose default to be Python 3.9
update-alternatives --set python /usr/bin/python3.6
# update-alternatives --config python

echo "configuring alternatives for python3"
update-alternatives --remove-all python3
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2
update-alternatives --install /usr/bin/python3 python3 /usr/libexec/no-python 3
# choose default to be Python 3.9
update-alternatives --set python3 /usr/bin/python3.6
# update-alternatives --config python3

update-alternatives --list
}


function config_sshd ()
{
# allow password authentication for ssh
echo "updating /etc/ssh/sshd_config"
sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
systemctl restart sshd.service
}



function ansible_ssh ()
{
echo "setup ssh for user ${MY_GIT_USER}"
mkdir -p /home/${MY_GIT_USER}/.ssh
chown ${MY_GIT_USER}:${MY_GIT_GROUP} /home/${MY_GIT_USER}/.ssh
chmod 700 /home/${MY_GIT_USER}/.ssh
# copy public key to ansible user
    SET_KEY_OK=0
    ssh_public_key=$(find /vagrant/*.pub -printf "%p")
    if test -f "$ssh_public_key" ; then
      echo "Check if public key $ssh_public_key is valid."
      if ssh-keygen -l -f "$ssh_public_key" ; then
        echo "Add public key to /home/${MY_GIT_USER}/.ssh/authorized_keys"
        cat "$ssh_public_key" >> /home/${MY_GIT_USER}/.ssh/authorized_keys
        SET_KEY_OK=1
      else
        echo "The SSH Key is in the wrong format, aborting"
        exit 1
      fi
    fi
    if [ ${SET_KEY_OK} -eq 0 ]; then
       echo "Please copy the public ssh key to the same directory as the vagrantfile and the Oracle software"
       exit 1
    fi
chown ${MY_GIT_USER}:${MY_GIT_GROUP} /home/${MY_GIT_USER}/.ssh/authorized_keys
chmod 640 /home/${MY_GIT_USER}/.ssh/authorized_keys


# ssh_private_key has same filename as public key, but without ".pub" at the end
ssh_private_key=${ssh_public_key//.pub/}
ssh_private_key=$(find ${ssh_private_key} -printf "%p")
    if test -f "$ssh_private_key" ; then
      echo "Check if private key $ssh_private_key is valid."
      if ssh-keygen -l -f "$ssh_private_key" ; then
        echo "Add private key to /home/${MY_GIT_USER}/.ssh/id_rsa"
        cat "$ssh_private_key" > /home/${MY_GIT_USER}/.ssh/id_rsa
        SET_KEY_OK=1
      else
        echo "The SSH Key is in the wrong format, aborting"
        exit 1
      fi
    fi
    if [ ${SET_KEY_OK} -eq 0 ]; then
       echo "Please copy the private ssh key to the same directory as the vagrantfile and the Oracle software"
       exit 1
    fi
chown ${MY_GIT_USER}:${MY_GIT_GROUP} /home/${MY_GIT_USER}/.ssh/id_rsa
chmod 600 /home/${MY_GIT_USER}/.ssh/id_rsa
}



function ansible_sudoers ()
{
echo "setup user ${MY_GIT_USER} in /etc/sudoers"
##### https://gist.github.com/buchireddy/19eb6593f692852d2df7
# Take a backup of sudoers file and change the backup file.
rm -f /tmp/sudoers.bak
cp -f /etc/sudoers /tmp/sudoers.bak
# allow use of exclamation mark, but not use it for bash history
set +H
echo "${MY_GIT_USER} ALL=(ALL) NOPASSWD:ALL
Defaults:${MY_GIT_USER} !requiretty
" >> /tmp/sudoers.bak
unalias cp
# Check syntax of the backup file to make sure it is correct.
visudo -cf /tmp/sudoers.bak
if [ $? -eq 0 ]; then
  # Replace the sudoers file with the new only if syntax is correct.
  cp -f /tmp/sudoers.bak /etc/sudoers
  if [ $? -eq 0 ]; then
    echo "sudoers file replaced."
  else
    echo "Could not modify /etc/sudoers file. Please do this manually."
  fi
else
  echo "Could not modify /etc/sudoers file. Please do this manually."
fi
}


function call_ansible_oracle ()
{
echo "create script to run as user ${MY_GIT_USER} to setup oracle with ansible-oracle"
MY_GIT_DIR=/home/${MY_GIT_USER}/git
cat > /tmp/run_as_ansible.sh << ANSIBLE_EOF
MY_GIT_USER=ansible
MY_GIT_DIR=/home/${MY_GIT_USER}/git
mkdir -p ${MY_GIT_DIR}
cd ${MY_GIT_DIR}

echo "git clone"
git clone https://github.com/oravirt/ansible-oracle.git
chown -R ${MY_GIT_USER}:${MY_GIT_GROUP} ${MY_GIT_DIR}

echo "change for this host"
cd ~/git/ansible-oracle/example/beginner_patching/ansible/
sed -i "s/beginner-dbfs-patching-151-192-168-56-162.nip.io/$(hostname --fqdn)/g" inventory/hosts.yml
cd ~/git/ansible-oracle/example/beginner_patching/ansible/inventory/host_vars/
mv beginner-dbfs-patching-151-192-168-56-162.nip.io $(hostname --fqdn)
cd ~/git/ansible-oracle/example/beginner_patching/ansible/inventory/group_vars/all
sed -i "s/configure_host_disks: true/configure_host_disks: false/g" host.yml

echo "call install_ansible.sh"
~/git/ansible-oracle/tools/ansible/install_ansible.sh
. ~/venv/ansible-oracle/bin/activate
cd ~/git/ansible-oracle/example/beginner_patching/ansible/
ansible-galaxy collection install -r requirements.yml

# Download Patches
cd ~/git/ansible-oracle/example/beginner_patching/ansible/
ansible-playbook -i inventory/hosts.yml -e hostgroup=all playbooks/patch_download.yml -e mos_login="@{MY_MOS_LOGIN}" -e mos_password="@{MY_MOS_PASSWORD}"

# Install all
# Patches müssen vorher heruntergeladen werden!
cd ~/git/ansible-oracle/example/beginner_patching/ansible/
ansible-playbook -i inventory/hosts.yml -e hostgroup=all playbooks/single-instance-fs.yml
ANSIBLE_EOF
chown ${MY_GIT_USER} /tmp/run_as_ansible.sh
chmod +x /tmp/run_as_ansible.sh

# su - ${MY_GIT_USER} -c /tmp/run_as_ansible.sh >> ${LOG_FILE} 2>&1
echo "Run script /tmp/run_as_ansible.sh as user ${MY_GIT_USER}"
su - ${MY_GIT_USER} -c /tmp/run_as_ansible.sh
if [ $? -eq 0 ]; then
  echo "Oracle is installed"
else
  echo "Problem installing oracle, see error above."
  # exit commented out, otherwise bash shell closes
  # exit 1
fi
}

###############################################################################
# main code starts here
###############################################################################

# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root"
   exit 1
fi

export MY_GIT_USER=ansible
export MY_GIT_GROUP=ansible
export MY_MOS_LOGIN="xxxxxxxxx"
export MY_MOS_PASSWORD="xxxxxx"
# put MOS login & password in separate file
source /vagrant/scripts/setenv.sh


setup_packages
# python_alternatives
config_sshd
useradd ${MY_GIT_USER}
ansible_sudoers
ansible_ssh
call_ansible_oracle

# vagrant up
# vagrant halt
# vagrant snapshot save test1
# vagrant snapshot restore test1