#!/usr/bin/env python

# This software is licensed under GPL-3.0
# Copyright (c) 2023 Open Source Automation Development Lab (OSADL) eG <info@osadl.org>
# Author Carsten Emde <C.Emde@osadl.org>

# Maintain Python 2.x compatibility
# pylint: disable=consider-using-with,unspecified-encoding

import sys
import os
import subprocess
import argparse
import re
import json

def osloc2json(infilename, verbose):
    """ Open the OSLOC file, convert it to JSON and store it under the original name suffixed by '.json' """
    outfilename = infilename.replace('.txt', '') + '.json'
    infileparts = infilename.split('/')
    basename = infileparts[len(infileparts) - 1]
    license = basename.replace('.txt', '')
    osloc = open(infilename, 'r').read()
    jsonfile = open(outfilename, 'w')
    jsondata = {}
    jsondata[license] = {}
    data = jsondata[license]
    parents = {}
    oldtabs = -1
    while True:
        endlinepos = osloc.find('\n')
        line = osloc[0:endlinepos]
        if verbose:
            print(line)
        tabs = line.count('\t')
        if oldtabs == -1:
            oldtabs = tabs
        if line[0:8] == 'USE CASE':
            usecasetag = line[0:8]
            lasttag = usecasetag
            usecase = line[9:]
            if usecasetag not in data:
                data[usecasetag] = {}
            parents[tabs + 1] = data[usecasetag][usecase] = {}
        elif re.match('\t*YOU MUST', line) and not re.match('\t*YOU MUST NOT', line):
            youmusttag = 'YOU MUST'
            lasttag = youmusttag
            if youmusttag not in parents[tabs]:
                parents[tabs][youmusttag] = []
            parents[tabs][youmusttag].append(line[line.find('YOU MUST') + 9:])
        elif re.match('\t*YOU MUST NOT', line):
            youmustnottag = 'YOU MUST NOT'
            lasttag = youmustnottag
            if youmustnottag not in parents[tabs]:
                parents[tabs][youmustnottag] = []
            parents[tabs][youmustnottag].append(line[line.find('YOU MUST NOT') + 13:])
        elif re.match('\t*IF', line):
            iftag = 'IF'
            lasttag = iftag
            ifcond = line[line.find('IF') + 3:]
            if iftag not in parents[tabs]:
                parents[tabs][iftag] = {}
            parents[tabs + 1] = parents[tabs][iftag][ifcond] = {}
        osloc = osloc[endlinepos + 1:]
        oldtabs = tabs
        if len(osloc) == 0:
            break
    json.dump(jsondata, jsonfile, indent = 4)
    return

def main(argv):
    parser = argparse.ArgumentParser(prog = 'jar2src.py',
      epilog = 'Parse OSLOC file, convert it to JSON format and store it under the original name suffixed by ".json"')

    parser.add_argument('filename',
      metavar = 'OSLOC',
      help = 'file name of an OSLOC file to process')
    parser.add_argument('-v', '--verbose',
      action = 'store_true',
      default = False,
      help = 'show names and texts the program is using')
    args = parser.parse_args()

    osloc2json(args.filename, args.verbose)

if __name__ == '__main__':
    main(sys.argv)