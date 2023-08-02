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

def optjson(l):
    """ If a dict has only keys, but no values, convert it to a list of keys """
    if type(l) is dict:
        for e in l.keys():
            if l[e]:
                optjson(l[e])
                allvalues = 0
                if type(l[e]) is dict:
                    for v in l[e].values():
                        allvalues += len(v)
                    if allvalues == 0:
                        l[e] = list(l[e].keys())

def osloc2json(licensefilenames, outfilename, json, optimize, show, verbose):
    """ Open the OSLOC file or files, convert it or them to a JSON object and store it as specified """
    licenses = len(licensefilenames)
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
                tag = 'SELECTION'
                text = 'EITHER'
            elif re.match('\t*OR', line):
                tag = 'SELECTION'
                text = 'OR'
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

    return

def main(argv):
    if int(sys.version[0]) < 3:
        if len(argv) < 2 or argv[1] == '-h' or argv[1] == '--help':
            print('usage: osloc2json.py [-h] OSLOC\n\
\n\
positional arguments:\n\
  OSLOC           file name of an OSLOC file to process\n\
\n\
options:\n\
  -h, --help      show this help message and exit\n\
\n\
Either parse a single OSLOC file, convert it to JSON format and store it under the original name suffixed by ".json", or\n\
parse all OSLOC files, convert them to a single JSON object and store it under a provided name or "osloc.json" if none given')
            return
        argv.pop(0)
        osloc2json(argv, 'osloc.json', json, True, False, False)
    else:
        parser = argparse.ArgumentParser(prog = 'osloc2json.py', formatter_class = argparse.RawTextHelpFormatter,
          epilog = 'Either parse a single OSLOC file, convert it to JSON format and store it under the original name suffixed by ".json", or\n\
parse all OSLOC files, convert them to a single JSON object and store it under the file OUTPUT or "osloc.json" if none given')

        parser.add_argument('licensefilenames',
          metavar = 'OSLOC',
          nargs='+',
          help = 'file name of an OSLOC file to process')
        parser.add_argument('-f',
          '--filename',
          type = pathlib.Path,
          metavar = 'OUTPUT',
          default = 'osloc.json',
          nargs='?',
          help = 'name of output file for multiple licenses, has no effect if single license, default "osloc.json"')
        parser.add_argument('-o', '--optimize',
          action = 'store_true',
          default = False,
          help = 'convert a dict with no values to a list of keys, add "-opt" to output file name')
        parser.add_argument('-s', '--show',
          action = 'store_true',
          default = False,
          help = 'also list the output to screen')
        parser.add_argument('-v', '--verbose',
          action = 'store_true',
          default = False,
          help = 'show names and texts the program is using')
        args = parser.parse_args()

        osloc2json(args.licensefilenames, args.filename, json, args.optimize, args.show, args.verbose)

if __name__ == '__main__':
    main(sys.argv)
