# What is vagrant?
Vagrant is a tool that makes it EASIER and FASTER to setup virtual machines. Vagrant Boxes are pre-built base images (e.g. Oracle Linux) that can be imported into Vagrant as a starting point. For our use-case, we will use Vagrant together with Virtualbox and Oracle Linux


## Installation
1. Download and install Vagrant
1. Download and install Oracle Virtualbox

## Let's start
Using Tim Halls's guide, let's play
https://oracle-base.com/articles/vm/vagrant-a-beginners-guide

1. hmm, cannot download that first OL box, let's see the oracle doc https://yum.oracle.com/boxes/
1. Note also that the default provider for vagrant has changed to libvirt (was virtualbox), so we will need to add "--provider virtualbox" to our vagrant add commands


## Download Vagrant boxes
- Instead of downloading a large DVD image, we can download a small vagrant box. 
- We can manually download a new box using the vagrant box add command. 
- We only need to do this once for each vagrant box (e.g. one time for Oracle Linux 7 and one time for Oracle Linux 8). 
- This download process would also happen automatically if required, when you reference a new box in a Vagrantfile

In a DOS command prompt...
```cmd
vagrant box add --provider virtualbox https://oracle.github.io/vagrant-projects/boxes/oraclelinux/7.json
vagrant box add --provider virtualbox https://oracle.github.io/vagrant-projects/boxes/oraclelinux/8.json
```

## Some vagrant addons
1. allows us to resize disks (optional)

In a DOS command prompt...
```cmd
vagrant plugin install vagrant-disksize
```
1. ensure the virtualbox guest additions is updated, required to ensure that the guest additions are automatically updated for all new vagrant boxes

In a DOS command prompt...
```cmd
vagrant plugin install vagrant-vbguest
```

1. Automatically update the /etc/hosts

In a DOS command prompt...
```cmd
vagrant plugin install vagrant-hostsupdater
```
## Create the initial vagrantfile
To create the virtual machine, we first of all create a new directory, change to it and create the initial "vagrantfile"

In a DOS command prompt...
```cmd
mkdir D:\vagrant\vol7db19
cd /D D:\vagrant\vol7db19
vagrant init
```

## Start the VM
edit the vagrantfile (see Tim Hall's website above) and when ready with our configuration, we can install, create and start the VM with the following command...

In a DOS command prompt...
```cmd
vagrant up
```


## Changing the vagrantfile
if you change the vagrantfile, destroy and recreate your virtual machine

In a DOS command prompt...
```cmd
vagrant destroy -f
vagrant up
```

## accessing the VM
1. use the command "vagrant ssh" to access the VM per shh in your DOS command prompt
1. or connect with ssh to 127.0.0.1, port 2222 with your favourite tool

## Removing Vagrant boxes
- We can remove any old boxes we are no longer using, with the vagrant box remove command.
- These boxes will be automatically downloaded again if required. 
- It is best not to remove them, if still used regularly, as it takes a few minutes to download them

In a DOS command prompt...
```cmd
vagrant box remove oraclelinux/7
vagrant box remove oraclelinux/8
```

# Open issues
1. ssh key usage, see https://superuser.com/questions/1783979/is-there-a-way-to-create-disk-partitions-on-vagrant-vm
1. install oracle DB
