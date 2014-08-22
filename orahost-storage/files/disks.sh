#!/bin/bash
#Create a single primary partiton with whole disk size and create LVM PV on it
disk=$1
#remove ending numbers if found
disk=${disk%%[0-9]}
partno=1
export PATH=$PATH:/sbin/:/usr/sbin/
#only new version parted supports -a
if [ $(parted -h | grep -- -a | wc -l) -gt 0  ]; then
 partedcmd='parted -a optimal'
else
 partedcmd='parted'
fi

if [[ -z $disk ]]; then
 echo "Usage: $0 disk device name: e.g $0 /dev/sdb"
 exit 0
fi

if [[ -e ${disk}${partno} ]]; then
 echo "==> ${disk}${partno} already exist"
 exit 0
fi

echo "==> Create MBR label"
parted -s $disk  mklabel msdos
ncyl=$(parted $disk unit cyl print  | sed -n 's/.*: \([0-9]*\)cyl/\1/p')

if [[ $ncyl != [0-9]* ]]; then
	echo "disk $disk has invalid cylinders number: $ncyl"
	exit 1
fi

echo "==> create primary parition  $partno with $ncyl cylinders"
$partedcmd $disk mkpart primary 0cyl ${ncyl}cyl
#echo "==> set partition $partno to type: lvm "
#parted $disk set $partno lvm on
partprobe > /dev/null 2>&1
sleep 3
