FROM docker.io/library/python:3.10-slim-buster

ARG ansible_version

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# group 999 is needed for docker in docker
RUN groupadd -g 999 docker && useradd -m -u 1000 -G 999 ansible

RUN apt-get update -y &&\
    apt-get install -y \
        curl \
        net-tools \
        iputils-ping \
        lsb-release \
        openssh-client \
        sshpass \
        socat \
        git \
        tar \
        unzip \
        jq \
        less

RUN python3 -m pip install --upgrade pip

RUN pip3 install ansible===${ansible_version} && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    rm -rf /root/.local /root/.cache && \
    mkdir /git && chown ansible /git

USER root

# Please add following ENV to docker for Ansible
# ANSIBLE_COLLECTIONS_PATHS=/ansible/galaxy
RUN mkdir -p /ansible/galaxy && chown ansible /ansible/galaxy

USER ansible
