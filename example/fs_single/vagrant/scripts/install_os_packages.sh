#!/usr/bin/env bash
echo "******************************************************************************"
echo "Prepare yum with the latest repos. $(date)"
echo "******************************************************************************"
echo "nameserver 8.8.8.8" >> /etc/resolv.conf

#yum update -y
