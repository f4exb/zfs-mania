#!/bin/sh

snapshot=${1}
dataset=$(echo ${snapshot} | cut -d @ -f 1)
snapid=$(echo ${1} | cut -d @ -f 2)
snapclone=${dataset}/snapclone

sudo zfs clone ${snapshot} ${snapclone}
sudo zfs set sharenfs=on ${snapclone}
sudo showmount -e
