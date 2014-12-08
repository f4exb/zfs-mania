#!/bin/sh
find ${1} -type f -exec stat -c %s {} + | awk '{if ($1 > 0) {sum += $1; sqsum += $1*$1; n++;}} END {avg = sum/n; print avg; print sqrt((sqsum/n)-(avg*avg)); print n;}'
