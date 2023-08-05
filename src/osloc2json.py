#!/usr/bin/env python

# This software is licensed under GPL-3.0
# Copyright (c) 2023 Open Source Automation Development Lab (OSADL) eG <info@osadl.org>
# Author Carsten Emde <C.Emde@osadl.org>

# Maintain Python 2.x compatibility
# pylint: disable=consider-using-with,unspecified-encoding

import sys
import re
try:
    import argparse
    import pathlib
    import json
except ImportError:
    import simplejson as json
    from optparse import OptionParser

def optjson(l):
    """ 1. If a dict has only keys, but no values, convert it to a list of keys """
    """ 2. If a dict has a list with a single element that is a dict, propagate the dict to the parent dict """
    if type(l) is dict:
        for e in l:
            if l[e]:
                optjson(l[e])
                allvalues = 0
                if type(l[e]) is dict:
                    for v in l[e].values():
                        allvalues += len(v)
                    if allvalues == 0:
                        l[e] = list(l[e].keys())
                elif type(l[e]) is list and len(l[e]) == 1 and type(l[e][0]) is dict:
                    l[e] = l[e][0]

printnonl = sys.stdout.write
def back2osloc(l, indent, key):
    if type(l) is dict:
        count = 0
        for e in l:
            if not re.search('[a-z]', e):
                print()
                if indent == 0:
                    printnonl(e + ' ')
                else:
                    printnonl(' '*indent + e + ' ')
                increment = 4
            else:
                if count == 0:
                    printnonl(e)
                else:
                    if indent == 0:
                        printnonl(key + ' ' + e)
                    else:
                        if count == 0:
                            printnonl(' '*indent + key + ' ' + e)
                        else:
                            print()
                            if indent - 4 == 0:
                                printnonl(key + ' ' + e)
                            else:
                                printnonl(' '*(indent - 4) + key + ' ' + e)
                increment = 0
            back2osloc(l[e], indent + increment, e)
            count = count + 1
    elif type(l) is list:
        count = 0
        for e in l:
            if type(e) is dict:
                back2osloc(e, indent, key)
            else:
                if count == 0:
                    print()
                if indent != 0:
                    printnonl(' '*indent)
                if l.index(e) != len(l) -1:
                    print(e)
                else:
                    printnonl(e)
                count = count + 1

def osloc2json(licensefilenames, outfilename, json, args):
    """ Open OSLOC files, convert them to JSON objects and store them as specified """
    optimize = args.optimize
    recreate = args.recreate
    show = args.show
    verbose = args.verbose
    licenses = len(licensefilenames)
    eitherlevels = {}

    if licenses == 1:
        if optimize:
            optsuffix = '-opt'
        else:
            optsuffix = ''
        outfilename = licensefilenames[0].replace('.txt', '') + optsuffix + '.json'

    jsondata = {}

    for licensefilename in licensefilenames:
        licensefilenameparts = licensefilename.split('/')
        basename = licensefilenameparts[len(licensefilenameparts) - 1]
        license = basename.replace('.txt', '')
        oslocfile = open(licensefilename, 'r')
        osloc = oslocfile.read()
        oslocfile.close()
        jsondata[license] = {}
        data = jsondata[license]
        parents = {}
        while True:
            endlinepos = osloc.find('\n')
            line = osloc[0:endlinepos]
            line = re.sub(r' \(.*\)', '', line)
            if verbose:
                print(line)
            tabs = line.count('\t')
            tag = ''
            text = ''
            if line[0:8] == 'USE CASE':
                tag = line[0:8]
                text = line[9:]
                if tag not in data:
                    data[tag] = {}
                parents[tabs + 1] = data[tag][text] = {}
                tag = ''
            elif re.match('\t*YOU MUST NOT', line):
                tag = 'YOU MUST NOT'
            elif re.match('\t*YOU MUST', line):
                tag = 'YOU MUST'
            elif re.match('\t*ATTRIBUTE', line):
                tag = 'ATTRIBUTE'
            elif re.match('\t*IF', line):
                tag = 'IF'
            elif re.match('\t*EXCEPT IF', line):
                tag = 'EXCEPT IF'
            elif re.match('\t*EITHER IF', line):
                tag = 'EITHER IF'
            elif re.match('\t*OR IF', line):
                tag = 'OR IF'
            elif re.match('\t*EITHER', line):
                tag = 'EITHER'
            elif re.match('\t*OR', line):
                tag = 'OR'
            elif line[0:12] == 'PATENT HINTS':
                tag = line[0:12]
            elif line[0:15] == 'COPYLEFT CLAUSE':
                tag = line[0:15]
            elif line[0:13] == 'COMPATIBILITY':
                pass
            elif line[0:23] == 'DEPENDING COMPATIBILITY':
                pass
            elif line[0:15] == 'INCOMPATIBILITY':
                pass
            else:
                print('Warning: Unidentified language element encountered in "' + license + '": ' + line)
            if tag != '':
                if text == '':
                    text = line[line.find(tag) + len(tag) + 1:];
                if tabs == 0 and (text == 'Yes' or text == 'No' or text == 'Questionable'):
                    if tag not in data:
                        data[tag] = text
                else:
                    if tag == 'EITHER':
                        eitherlevels[tabs] = 0
                    elif tag == 'OR':
                        text = '#' + str(eitherlevels[tabs])
                        eitherlevels[tabs] = eitherlevels[tabs] + 1
                    if tag not in parents[tabs]:
                        parents[tabs][tag] = {}
                    parents[tabs + 1] = parents[tabs][tag][text] = {}
            osloc = osloc[endlinepos + 1:]
            if len(osloc) == 0:
                break

    if optimize:
        optjson(jsondata)

    if licenses > 1:
        alljsondata = {}
        alljsondata['OSADL OSLOC'] = jsondata
        jsondata = alljsondata

    jsonfile = open(outfilename, 'w')
    json.dump(jsondata, jsonfile, indent = 4, sort_keys = True)
    jsonfile.close()

    if show:
        json.dump(jsondata, sys.stdout, indent = 4, sort_keys = True)
        sys.stdout.write('\n')

    if recreate:
        l = jsondata
        if len(jsondata.keys()) == 1:
            l = l[list(jsondata.keys())[0]]
        back2osloc(l, 0, '')
        print()

    return

def main(argv):
    filenamehelp = 'file names of OSLOC files to process'
    if int(sys.version[0]) < 3:
        parser = OptionParser(prog = 'osloc2json.py', usage = '%prog [-h] -f [OUTPUT] [-o] [-r] [-s] [-v] OSLOC [OSLOC ...]',
          description = 'positional arguments:   ' + filenamehelp)
        parser.add_argument = parser.add_option
        filenametype = 'string'
    else:
        parser = argparse.ArgumentParser(prog = 'osloc2json.py', formatter_class = argparse.RawTextHelpFormatter,
          epilog = 'Either parse a single OSLOC file, convert it to JSON format and store it under the original name suffixed by ".json", or\n\
parse all OSLOC files, convert them to a single JSON object and store it under the file OUTPUT or "osloc.json" if none given')
        parser.add_argument('licensefilenames',
          metavar = 'OSLOC',
          nargs='+',
          help = filenamehelp)
        filenametype = pathlib.Path
    parser.add_argument('-f',
      '--filename',
      type = filenametype,
      metavar = 'OUTPUT',
      default = 'osloc.json',
      nargs='?',
      help = 'name of output file for multiple licenses, has no effect if single license, default "osloc.json"')
    parser.add_argument('-o', '--optimize',
      action = 'store_true',
      default = False,
      help = 'convert a dict with no values to a list of keys, add "-opt" to output file name')
    parser.add_argument('-r', '--recreate',
      action = 'store_true',
      default = False,
      help = 'recreate original checklist from JSON (for debugging)')
    parser.add_argument('-s', '--show',
      action = 'store_true',
      default = False,
      help = 'also list the output to screen')
    parser.add_argument('-v', '--verbose',
      action = 'store_true',
      default = False,
      help = 'show names and texts the program is using')
    if int(sys.version[0]) < 3:
        (args, filenames) = parser.parse_args()
        if len(filenames) < 1:
            print("error: the following arguments are required: OSLOC")
    else:
        args = parser.parse_args()
        filenames = args.licensefilenames

    osloc2json(filenames, args.filename, json, args)

if __name__ == '__main__':
    main(sys.argv)
