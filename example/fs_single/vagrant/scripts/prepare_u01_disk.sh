#!/usr/bin/env bash
function prepare_disk {
  MOUNT_POINT=$1
  DISK_DEVICE=$2

  echo "******************************************************************************"
  echo "Prepare ${MOUNT_POINT} disk. $(date)"
  echo "******************************************************************************"
  # New partition for the whole disk.
  echo -e "n\np\n1\n\n\nw" | fdisk "${DISK_DEVICE}"

  # Add file system.
  mkfs.xfs -f "${DISK_DEVICE}1"

  # Mount it.
  # shellcheck disable=SC2086
  UUID=$(blkid -o export ${DISK_DEVICE}1 | grep UUID | grep -v PARTUUID)
  mkdir "${MOUNT_POINT}"
  echo "${UUID}  ${MOUNT_POINT}    xfs    defaults 1 2" >> /etc/fstab
  mount "${MOUNT_POINT}"
}

prepare_disk /u02 /dev/sdb
