#!/bin/sh

sudo zpool iostat -v ${1} | grep mirror | tail -n1 | awk 'BEGIN {mult["K"]=1024; mult["M"]=1024*1024; mult["G"]=1024*1024*1024} match($0, /mirror\s+(\S+)(\S)\s+/, a) {print a[1]*mult[a[2]]}'
