#!/usr/bin/env bash
#
set -eu

docker build -t ol8-ansible:latest -f Dockerfile-ol8  .
docker build -t ol7-ansible:latest -f Dockerfile-ol7  .
# SLES is not working with this container for ansible-oracle
# => bci-base <> SLES ...
# => not all needed RPMs are availible during installation
# docker build -t registry.suse.com/bci/bci-base-ansible:15.3 -f Dockerfile-SLES15SP3  .
# docker build -t registry.suse.com/bci/bci-base-ansible:15.4 -f Dockerfile-SLES15SP4  .
# docker build -t registry.suse.com/bci/bci-base-ansible:15.5 -f Dockerfile-SLES15SP4  .
