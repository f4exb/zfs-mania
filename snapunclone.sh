#!/bin/sh

snapshot=${1}
dataset=$(echo ${snapshot} | cut -d @ -f 1)
snapid=$(echo ${1} | cut -d @ -f 2)
snapclone=${dataset}/snapclone

sudo zfs set sharenfs=off ${snapclone}
sudo zfs destroy -r ${snapclone}

sudo zfs list -r ${dataset}
sudo zfs list -t snapshot
sudo showmount -e
