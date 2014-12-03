#!/usr/bin/env python

"""
Find details about a directory or plain file in a ZFS dataset using zdb utility
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
    parser.add_option("-i", "--input-dump-file", dest="ifile", help="Input dump file (does not use zdb) - required if not -d option", metavar="IFILE", type="string")
    parser.add_option("-d", "--dataset", dest="dataset", help="ZFS dataset", metavar="DATASET", type="string")
    parser.add_option("-o", "--output-dump-file", dest="ofile", help="Output dump file (result of zdb) - required if -d option", metavar="OFILE", type="string")
    parser.add_option("-n", "--numbers", dest="numbers", help="Match object numbers (comma separated list)", metavar="NUMBERS", type="string")
    parser.add_option("-t", "--types", dest="types", help="Match object types (comma separated list)", metavar="TYPES", type="string")
    parser.add_option("-p", "--path", dest="re_path", help="Regular expression to match file path with", metavar="PATH", type="string")
    #parser.add_option("-k", "--mail-ok", dest="mail_ok", help="send informative mail also if result is OK", metavar="MAIL_OK", action="store_true", default=False)
    
    (options, args) = parser.parse_args()
    
    options.types_list = None
    options.numbers_list = None

    if options.dataset is None:
        if options.ifile is None:
            raise InputError("You must specify input dump file when dataset is not specified")
    else:
        if options.ofile is None:
            raise InputError("You must specify output dump file when dataset is specified")
    
    if options.types is not None:
        options.types_list = options.types.split(',')
    
    if options.numbers is not None:
        options.numbers_list = options.numbers.split(',')

    return options               

# ======================================================================
def dump_zdb_output(options):
    os.popen("sudo zdb -dddd %s > %s" % (options.dataset, options.ofile))
    return options.ofile
    
# ======================================================================
def select_zdb_data(options, ifile):
    zdump = open(ifile, 'r')
    objstr = ""
    outstr = ""
    objhdr = False
    objselect = False
    
    for zline in zdump:
        iline = zline.strip("\r\n")

        if iline.lstrip().split(' ')[0] == "Object":
            objhdr = True
            if objselect and len(objstr) > 0:
                outstr += objstr
                objselect = False
            objstr = (iline + '\n')
            continue
        else:
            objstr += (iline + '\n')

        if objhdr:
            objhdr = False
            if options.numbers_list is not None:
                for objnum in options.numbers_list:
                    if iline.lstrip().split(' ')[0] == objnum:
                        objselect = True
                        break
                continue
            if not objselect and options.types_list is not None:
                for ztype in options.types_list:
                    if ztype in iline:
                        objselect = True
                        break
                continue

        if not objselect and options.numbers_list is None and options.types_list is None:
            pathLineRE = re.compile(r'^\s+path\s+(\S+)')
            pathLineMatch = pathLineRE.match(iline)
            if pathLineMatch:
                path = pathLineMatch.group(1)
                pathRE = re.compile(r'%s' % options.re_path)
                if pathRE.match(path):
                    objselect = True
        
    if objselect:
        outstr += objstr
        
    return outstr
    
# ======================================================================
def main():
    try:
        options = getInputOptions()
        
        if options.dataset is None:
            ifile = options.ifile
        else:
            ifile = dump_zdb_output(options)
            
        output = select_zdb_data(options, ifile)
        print output[:-1]
        
    except KeyboardInterrupt:
        return 1
    except InputError as e:
        print >> sys.stderr, e.msg
        return 2

        
# ======================================================================
if __name__ == "__main__":
    rc = main()
    exit(rc)
