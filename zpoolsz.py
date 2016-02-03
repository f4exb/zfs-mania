#!/usr/bin/env python

"""
Computes sizes related to ZFS pool using iostats -v
- pool
- ZIL cache
- L2ARC cache
Assumes mirror pool with mirror ZIL and L2ARC stripe over 2 disks
"""

import sys, os, traceback
import re
from optparse import OptionParser

# ======================================================================
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

# ======================================================================
class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
        
# ======================================================================
def getInputOptions():

    parser = OptionParser(usage="usage: %%prog options\n\n%s")
    parser.add_option("-p", "--pool", dest="pool", help="ZFS pool name", metavar="IFILE", type="string")
    parser.add_option("-z", "--print-zil", dest="zil", help="Print ZIL log cache statistics", metavar="PRINT_ZIL", action="store_true", default=False)
    parser.add_option("-l", "--print-l2-cache", dest="l2", help="Print L2 cache statistics", metavar="PRINT_L2", action="store_true", default=False)
    
    (options, args) = parser.parse_args()
    
    if options.pool is None:
        raise InputError("You must specify the pool name (-p option)")

    return options               

# ======================================================================
def get_multi(multiplier):
    if multiplier == "K":
        return 1024
    elif multiplier == "M":
        return 1024*1024
    elif multiplier == "G":
        return 1024*1024*1024
    elif multiplier == "T":
        return 1024*1024*1024*1024
    else:
        return 1
    
# ======================================================================
def get_size(size_str):
    if size_str == "0":
        return 0
    else:
        num = 0
        try:
            num = float(size_str)
        except ValueError:
            num_str = size_str[:-1]
            multiplier = size_str[-1]
            num = float(num_str) * get_multi(multiplier)
        return num

# ======================================================================
def get_zpool_stats(poolname):
    zlines = os.popen("sudo zpool iostat -v %s" % poolname)
    poolsection = False
    zilsection = False
    l2section = False
    zpool_use = 0
    zpool_free = 0
    zil_uae = 0
    zil_free = 0
    l2_use = 0
    l2_free = 0
    
    for zline in zlines:
        iline = zline.strip("\r\n")
        words = iline.split()
        
        if len(words) == 0:
            continue
        
        if words[0] == poolname:
            zpool_use = get_size(words[1])
            zpool_free = get_size(words[2])
            poolsection = True
            continue

        if words[0][0] == '-':
            poolsection = False
            zilsection = False
            l2section = False
            continue

        if poolsection:
            if words[0] == "logs":
                zilsection = True
                continue
            elif words[0] == "cache":
                l2section = True
                continue
            
        if zilsection and words[0] == "mirror":
            zil_use = get_size(words[1])
            zil_free = get_size(words[2])
        elif l2section:
            l2_use += get_size(words[1])
            l2_free += get_size(words[2])
            
    return (zpool_use, zpool_free), (zil_use, zil_free), (l2_use, l2_free)
    
# ======================================================================
def main():
    try:
        options = getInputOptions()

        pool_stats, zil_stats, l2_stats = get_zpool_stats(options.pool)
        
        if options.zil:
            print "%d %d" % zil_stats
        elif options.l2:
            print "%d %d" % l2_stats
        else:
            print "%d %d" % pool_stats
                    
    except KeyboardInterrupt:
        return 1
    except InputError as e:
        print >> sys.stderr, e.msg
        return 2

        
# ======================================================================
if __name__ == "__main__":
    rc = main()
    exit(rc)
