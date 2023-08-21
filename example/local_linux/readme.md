# local_linux
- This example shows how you can use ansible-oracle to install the Oracle database on your local linux. You do not need to setup any extra virtual environment.
- local, not across network. your local linux. not using a central ansible controller for many installations. this is a simple local installation on linux.
- This is the way I use ansible-oracle to install Oracle at customer sites

## Prerequisites
1. Oracle Software 19.3
1. Oracle patches (will be downloaded if MOS patch download works now. The MOS patch download service is often down)

## FAQs
1. Which IP address
The existing IP address will be used
1. which hostname?
The existing hostname will be used. Please setup a hostname and a domainname
1. which storage layout
Oracle will be installed in /u01 and /u02
xxx detaisl
--> Better to change to using /u01 only


## Use in Vagrant
1. new to vagrant? see the vagrant_basics.md in the doc directory.
1. see the vagrantfile in the vagrant directory, to be changed as you wish.
1. vagrant up

### recommended addons to vagrant
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

1. Automatically update the hosts file on your Windows machine (not the virtual linux)

In a DOS command prompt...
```cmd
vagrant plugin install vagrant-hostsupdater
```
## Use in non-vagrant environments (e.g. on physical hardware, VMware, etc.)
1. software downloaded?
1. IP address set?
1. hostname and domainname set?
1. git clone fill_in_details/add_path_here
1. cd .../xx/yy
1. run_this script.sh


## TODO
1. change check for private key
ls -l Vagrantfile .vagrant/machines/default/virtualbox/private_key
1. add exact instructions for use above in non-vagrant
1. Change storage to use /u01 only
1. Add checks in shell script to check 
    1. hostname and domainname before running
    1. IP != 127.0.0.1
    1. abort if not enough storage
    1. /u01 partition available, if not abort
    1. /u01 abort? or warning if enough space in root (nasty)