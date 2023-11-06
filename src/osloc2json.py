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

try:
    from inspect import currentframe, getframeinfo
except ImportError:
    pass

def sanitizelist(l):
    sane = list(dict.fromkeys(l))
    sane = sorted(sane, key = lambda s: s.lower())
    return sane

def expandor(d, parent):
    if isinstance(d, dict):
        for k, v in d.copy().items():
            if isinstance(v, dict):
                if (parent == 'USE CASE' or parent == 'IF') and k.find(' OR ') != -1:
                    for k1 in k.split(' OR '):
                        d[k1] = v
                    d.pop(k)
                if len(v) > 0:
                    expandor(v, k)

def printdict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            printdict(v)
        else:
            print("{0} : {1}".format(k, v))

def nonecheck(d):
    for k, v in d.items():
        if isinstance(v, dict):
            if nonecheck(v):
                return True
        elif isinstance(v, list):
            if None in v:
                return True
        else:
            if v is None:
                return True
    return False

def getinstance(v):
    if isinstance(v, str):
        return 'str'
    elif isinstance(v, list):
        return 'list'
    elif isinstance(v, dict):
        return 'dict'

def extend(l1, l2, new, devel):
    for k1, v1 in l1.copy().items():
        for k2, v2 in l2.copy().items():
            if isinstance(v1, str) and isinstance(v2, str):
                if k1 == k2:
                    if v1 == v2:
                        if k1 not in new:
                            new[k1] = v1
                    else:
                        if k1 not in new:
                            new[k1] = [v1, v2]
                        else:
                            if isinstance(new[k1], str):
                                if new[k1] != v1 and new[k1] != v2:
                                    new[k1] = [new[k1], v1, v2]
                                elif new[k1] != v1:
                                    new[k1] = [new[k1], v1]
                                elif new[k1] != v2:
                                    new[k1] = [new[k1], v2]
                            elif isinstance(new[k1], list):
                                new[k1].append(v1)
                                new[k1].append(v2)
                                new[k1] = sanitizelist(new[k1])
                            elif isinstance(new[k1], dict):
                                if v1 not in new[k1]:
                                    new[k1][v1] = {}
                                if v2 not in new[k1]:
                                    new[k1][v2] = {}
                else:
                    if k1 not in new:
                        new[k1] = v1
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] != v1:
                                new[k1] = [new[k1], v1]
                        elif isinstance(new[k1], list):
                            if v1 not in new[k1]:
                                new[k1].append(v1)
                        elif isinstance(new[k1], dict):
                           if v1 not in new[k1]:
                                new[k1][v1] = {}
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] != v2:
                                new[k2] = [new[k2], v2]
                        elif isinstance(new[k2], list):
                            if v2 not in new[k2]:
                                new[k2].append(v2)
                        elif isinstance(new[k2], dict):
                            if v2 not in new[k2]:
                                new[k2][v2] = {}

            elif isinstance(v1, str) and isinstance(v2, list):
                if k1 == k2:
                    if k1 not in new:
                        v2copy = v2
                        v2copy.append(v1)
                        new[k1] = v2copy
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] != v1:
                                new[k1] = [new[k1], v1]
                            if new[k1] not in v2:
                                v2copy = v2
                                v2copy.append(new[k1])
                                new[k1] = v2copy
                        elif isinstance(new[k1], list):
                            if v1 not in new[k1]:
                                new[k1].append(v1)
                            new[k1] += v2
                            new[k1] = sanitizelist(new[k1])
                        elif isinstance(new[k1], dict):
                            if devel:
                                print('t.b.d. str/list/dict new[k1]', new[k1], k1, v1, v2)
                else:
                    if k1 not in new:
                        new[k1] = v1
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] != v1:
                                new[k1] = [new[k1], v1]
                        elif isinstance(new[k1], list):
                            if v1 not in new[k1]:
                                new[k1].append(v1)
                        elif isinstance(new[k1], dict):
                            newdict = {}
                            newdict[v1] = {}
                            new[k1] = extend(new[k1], newdict, new[k1], devel)
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] not in v2:
                                v2copy = v2
                                v2copy.append(new[k2])
                                new[k2] = v2copy
                        elif isinstance(new[k2], list):
                            new[k2] += v2
                            new[k2] = sanitizelist(new[k2])
                        elif isinstance(new[k2], dict):
                            newdict = {}
                            newdict[k2] = v2
                            new[k2] = extend(new[k2], newdict, new[k2], devel)

            elif isinstance(v1, str) and isinstance(v2, dict):
                if k1 not in new:
                    new[k1] = v1
                else:
                    if isinstance(new[k1], str):
                        if new[k1] != v1:
                            new[k1] = [new[k1], v1]
                    elif isinstance(new[k1], list):
                        if v1 not in new[k1]:
                            new[k1].append(v1)
                    elif isinstance(new[k1], dict):
                        if v1 not in new[k1]:
                            new[k1][v1] = {}
                if k2 not in new:
                    new[k2] = v2
                else:
                    if isinstance(new[k2], str):
                        if new[k2] not in v2:
                            v2copy = v2
                            v2copy[k2] = {}
                            new[k2] = v2copy
                    elif isinstance(new[k2], list):
                        newdict = {}
                        for v in new[k2]:
                            newdict[v] = {}
                        new[k2] = newdict
                        new[k2] = extend(newdict, v2, new[k2], devel)
                    elif isinstance(new[k2], dict):
                        if v2 != new[k2]:
                            new[k2] = extend(new[k2], v2, new[k2], devel)

            elif isinstance(v1, list) and isinstance(v2, list):
                v1 = sanitizelist(v1)
                v2 = sanitizelist(v2)
                if k1 == k2:
                    if v1 == v2:
                        if k1 not in new:
                            new[k1] = v1
                    else:
                        if k1 not in new:
                            new[k1] = v1 + v2
                        else:
                            if isinstance(new[k1], list):
                                new[k1] += v1 + v2
                        new[k1] = sanitizelist(new[k1])
                else:
                    if k1 not in new:
                        new[k1] = v1
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] not in v1:
                                v1.append(new[k1])
                        elif isinstance(new[k1], list):
                            new[k1] += v1
                            new[k1] = sanitizelist(new[k1])
                        elif isinstance(new[k1], dict):
                            newdict = {}
                            newdict[k1] = v1
                            new[k1] = extend(new[k1], newdict, {}, devel)
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] not in v2:
                                v2.append(new[k2])
                        elif isinstance(new[k2], list):
                            new[k2] += v2
                            new[k2] = sanitizelist(new[k2])
                        elif isinstance(new[k2], dict):
                            newdict = {}
                            newdict[k2] = v2
                            new[k2] = extend(new[k2], newdict, {}, devel)

            elif isinstance(v1, list) and isinstance(v2, str):
                if k1 == k2:
                    if k1 not in new:
                        v1copy = v1
                        v1copy.append(v2)
                        new[k1] = v1copy
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] not in v1:
                                v1copy = v1
                                v1copy.append(new[k1])
                                new[k1] = v1copy
                            if new[k1] != v2:
                                if isinstance(new[k1], str):
                                    new[k1] = [new[k1], v2]
                                elif isinstance(new[k1], list):
                                    new[k1].append(v2)
                        elif isinstance(new[k1], list):
                            new[k1] += v1
                            new[k1] = sanitizelist(new[k1])
                            if v2 not in new[k1]:
                                new[k1].append(v2)
                        elif isinstance(new[k1], dict):
                            newdict = {}
                            newdict[k1] = v1
                            new[k1] = extend(new[k1], newdict, new[k1], devel)
                else:
                    if k1 not in new:
                        new[k1] = v1
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] not in v1:
                                v1copy = v1
                                v1copy.append(new[k1])
                                new[k1] = v1copy
                        elif isinstance(new[k1], list):
                            new[k1] += v1
                            new[k1] = sanitizelist(new[k1])
                        elif isinstance(new[k1], dict):
                            newdict = {}
                            newdict[k1] = v1
                            new[k1] = extend(new[k1], newdict, {}, devel)
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] != v2:
                                new[k2] = [new[k2], v2]
                        elif isinstance(new[k2], list):
                            if v2 not in new[k2]:
                                new[k2].append(v2)
                        elif isinstance(new[k2], dict):
                            if v2 not in new[k2]:
                                new[k2][v2] = {}

            elif isinstance(v1, list) and isinstance(v2, dict):
                listmatches = 0
                for v in v1:
                    if v in v2:
                        listmatches += 1
                skipv1 = (listmatches == len(v1))

                if k1 == k2:
                    if k1 not in new:
                        if not skipv1:
                            newdict = {}
                            newdict[k1] = v1
                            new[k1] = extend(newdict, v2, new[k1], devel)
                        else:
                            new[k1] = v2
                    else:
                        if isinstance(new[k1], str):
                            if devel:
                                print('t.b.d. str/list/dict new[k1]', new[k1], k1, v1)
                        elif isinstance(new[k1], list):
                            newlist = new[k1]
                            if not skipv1:
                                newlist += v1
                                newlist = sanitizelist(newlist)
                            newdict = {}
                            newdict[k1] = newlist
                            new[k1] = newdict
                            new[k1] = extend(newdict, v2, new[k1], devel)
                        if isinstance(new[k1], dict):
                            if not skipv1:
                                newdict = {}
                                newdict[k1] = v1
                                new[k1] = extend(newdict, v2, new[k1], devel)
                            else:
                                new[k1] = v2
                else:
                    if not skipv1:
                        if k1 not in new:
                            new[k1] = v1
                        else:
                            if isinstance(new[k1], str):
                                if new[k1] not in v1:
                                    v1copy = v1
                                    v1copy.append(new[k1])
                                    new[k1] = v1copy
                            elif isinstance(new[k1], list):
                                new[k1] += v1
                                new[k1] = sanitizelist(new[k1])
                            elif isinstance(new[k1], dict):
                                newdict = {}
                                newdict[k1] = v1
                                new[k1] = extend(new[k1], newdict, new[k1], devel)
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] not in v2:
                                v2copy = v2
                                v2copy[k2] = {}
                                new[k2] = v2copy
                        elif isinstance(new[k2], list):
                            newdict = {}
                            for v in new[k2]:
                                newdict[v] = {}
                            new[k2] = newdict
                            new[k2] = extend(newdict, v2, new[k2], devel)
                        elif isinstance(new[k2], dict):
                            if v2 != new[k2]:
                                new[k2] = extend(new[k2], v2, new[k2], devel)

            elif isinstance(v1, dict) and isinstance(v2, dict):
                if k1 == k2:
                    if v1 == v2:
                        if k1 not in new:
                            new[k1] = v1
                    else:
                        if k1 not in new:
                            new[k1] = {}
                        new[k1] = extend(v1, v2, new[k1], devel)
                else:
                    if k1 not in new:
                        new[k1] = v1
                    if isinstance(new[k1], str):
                        if new[k1] not in v1:
                            v1copy = v2
                            v1copy[k1] = {}
                            new[k1] = v1copy
                    elif isinstance(new[k1], list):
                        newdict = {}
                        for v in new[k1]:
                            newdict[v] = {}
                        newdict[k1] = newdict
                        new[k1] = extend(newdict, v1, new[k1], devel)
                    elif isinstance(new[k1], dict):
                        if v1 != new[k1]:
                            new[k1] = extend(new[k1], v1, new[k1], devel)
                    if k2 not in new:
                        new[k2] = v2
                    if isinstance(new[k2], str):
                        if new[k2] not in v2:
                            v2copy = v2
                            v2copy[k2] = {}
                            new[k2] = v2copy
                    elif isinstance(new[k2], list):
                        newdict = {}
                        for v in new[k2]:
                            newdict[v] = {}
                        new[k2] = newdict
                        new[k2] = extend(newdict, v2, new[k2], devel)
                    elif isinstance(new[k2], dict):
                        if v2 != new[k2]:
                            new[k2] = extend(new[k2], v2, new[k2], devel)

            elif isinstance(v1, dict) and isinstance(v2, str):
                if k1 not in new:
                    new[k1] = v1
                else:
                    if isinstance(new[k1], str):
                        if new[k1] not in v1:
                            v1copy = v1
                            v1copy[new[k1]] = {}
                            new[k1] = v1copy
                    elif isinstance(new[k1], list):
                        newdict = {}
                        for v in new[k1]:
                            newdict[v] = {}
                        newdict[k1] = newdict
                        new[k1] = extend(newdict, v1, new[k1], devel)
                    elif isinstance(new[k1], dict):
                        if v1 != new[k1]:
                            new[k1] = extend(new[k1], v1, new[k1], devel)
                if k2 not in new:
                    new[k2] = v2
                else:
                    if isinstance(new[k2], str):
                        if new[k2] != v2:
                            new[k2] = [new[k2], v2]
                    elif isinstance(new[k2], list):
                        if v2 not in new[k2]:
                            new[k2].append(v2)
                    elif isinstance(new[k2], dict):
                        if v2 not in new[k2]:
                            new[k2][v2] = {}

            elif isinstance(v1, dict) and isinstance(v2, list):
                listmatches = 0
                for v in v2:
                    if v in v1:
                        listmatches += 1
                skipv2 = (listmatches == len(v2))

                if k1 == k2:
                    if k1 not in new:
                        if not skipv2:
                            newdict = {}
                            newdict[k1] = v2
                            new[k1] = extend(v1, newdict, new[k1], devel)
                        else:
                            new[k1] = v1
                    else:
                        if isinstance(new[k1], str):
                            if devel:
                                print('t.b.d. str/list/dict new[k1]', new[k1], k1, v1)
                        elif isinstance(new[k1], list):
                            newlist = new[k1]
                            if not skipv2:
                                newlist += v2
                                newlist = sanitizelist(newlist)
                            newdict = {}
                            newdict[k1] = newlist
                            new[k1] = newdict
                            new[k1] = extend(v1, newdict, new[k1], devel)
                        if isinstance(new[k1], dict):
                            if not skipv2:
                                newdict = {}
                                newdict[k1] = v2
                                new[k1] = extend(v1, newdict, new[k1], devel)
                            else:
                                new[k1] = v1
                else:
                    if k1 not in new:
                        new[k1] = v1
                    else:
                        if isinstance(new[k1], str):
                            if new[k1] not in v1:
                                v1copy = v1
                                v1copy[new[k1]] = {}
                                new[k1] = v1copy
                        elif isinstance(new[k1], list):
                            newdict = {}
                            for v in new[k1]:
                                newdict[v] = {}
                            newdict[k1] = newdict
                            new[k1] = extend(newdict, v1, new[k1], devel)
                        elif isinstance(new[k1], dict):
                            if v1 != new[k1]:
                                new[k1] = extend(new[k1], v1, new[k1], devel)
                    if not skipv2:
                        if k2 not in new:
                            new[k2] = v2
                        else:
                            if isinstance(new[k2], str):
                                if new[k2] not in v2:
                                    v2copy = v2
                                    v2copy.append(new[k2])
                                    new[k2] = v2copy
                            elif isinstance(new[k2], list):
                                new[k2] += v2
                                new[k2] = sanitizelist(new[k2])
                            elif isinstance(new[k2], dict):
                                newdict = {}
                                newdict[k2] = v2
                                new[k2] = extend(new[k2], newdict, new[k2], devel)

    return new

def optjson(l):
    """ 1. If a dict has only keys, but no values, convert it to a list of keys """
    """ 2. If a dict has a list with a single element, propagate it to the parent dict """
    """ 3. If a dict has a dict with a single element with an empty key, propagate the dict to the parent dict """
    """ 4. If a dict has only dicts with consecutively numbered numeric keys, propagate the dicts into a list """
    if type(l) is dict:
        for e in l:
            if l[e]:
                optjson(l[e])
                if type(l[e]) is dict:
                    allvalues = 0
                    for v in l[e].values():
                        if v is not None:
                            allvalues += len(v)
                    if allvalues == 0:
                        l[e] = list(l[e].keys())
                    dictno = 0
                    for k in l[e]:
                        if len(k) == 0 and len(l[e]) == 1:
                            l[e] = l[e][k]
                        break
                    for k in l[e]:
                        if len(k) != 0 and not re.search('[^0-9]', k):
                            if int(k) != dictno:
                               break
                            dictno = dictno + 1
                    if dictno == len(l[e]):
                        newlist = []
                        for k in l[e]:
                            newlist.append(l[e][k])
                        l[e] = newlist
                if type(l[e]) is list:
                    if len(l[e]) == 1:
                        l[e] = l[e][0]
                    else:
                        l[e] = sorted(l[e], key = lambda s: s.lower())

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
    elif type(l) is str:
        printnonl(l)

def osloc2json(licensefilenames, outfilename, json, args):
    """ Open OSLOC files, convert them to JSON objects and store them as specified """
    devel = args.devel
    expand = args.expand
    merge = args.merge
    optimize = args.optimize
    recreate = args.recreate
    show = args.show
    verbose = args.verbose
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
        licensename = basename.replace('.txt', '')
        oslocfile = open(licensefilename, 'r')
        osloc = oslocfile.read()
        oslocfile.close()
        if verbose:
            print(licensename + ':')
        jsondata[licensename] = {}
        data = jsondata[licensename]
        eitherlevels = {}
        orlevels = {}
        eitheror = {}
        eitherextratabs = 0
        eitheriflevels = {}
        oriflevels = {}
        eitherifor = {}
        eitherifextratabs = 0
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
                tag = line[0:13]
            elif line[0:23] == 'DEPENDING COMPATIBILITY':
                tag = line[0:24]
            elif line[0:15] == 'INCOMPATIBILITY':
                tag = line[0:15]
            else:
                if devel:
                    print('Warning: Unidentified language element encountered in "' + licensename + '": ' + line)
            if tag != '':
                if text == '':
                    text = line[line.find(tag) + len(tag) + 1:]
                if tabs == 0 and (text == 'Yes' or text == 'No' or text == 'Questionable' or tag.find('COMPATIBILITY') != -1):
                    if tag not in data:
                        data[tag] = text
                    else:
                        if isinstance(data[tag], str):
                            oldtext = data[tag]
                            data[tag] = []
                            data[tag].append(oldtext)
                        data[tag].append(text)
                else:
                    if len(eitheror) > 0:
                        for i in eitheror:
                            if eitheror[i]:
                                if tabs <= i:
                                    eitheror[i] = 0
                                    eitherextratabs -= 1
                                    orlevels[i] = 0
                                if tabs < i:
                                    eitherlevels[i] = 0
                                    orlevels[i] = 0
                    if tag == 'EITHER':
                        if tabs in eitherlevels:
                            eitherlevels[tabs] += 1
                        else:
                            eitherlevels[tabs] = 1
                        text = str(eitherlevels[tabs])
                        orlevels[tabs] = 0
                    elif tag == 'OR':
                        orlevels[tabs] += 1
                        text = str(orlevels[tabs])
                        if orlevels[tabs] <= 1:
                            eitheror[tabs] = 1
                            eitherextratabs += 1
                    if len(eitherifor) > 0:
                        for i in eitherifor:
                            if eitherifor[i]:
                                if tabs <= i:
                                    eitherifor[i] = 0
                                    eitherifextratabs -= 1
                                    oriflevels[i] = 0
                                if tabs < i:
                                    oriflevels[i] = 0
                    if tag == 'EITHER IF':
                        oriflevels[tabs] = 0
                    elif tag == 'OR IF':
                        oriflevels[tabs] += 1
                        if oriflevels[tabs] <= 1:
                            eitherifor[tabs] = 1
                            eitherifextratabs += 1
                    if tag not in parents[tabs + eitherextratabs + eitherifextratabs]:
                        parents[tabs + eitherextratabs + eitherifextratabs][tag] = {}
                    parents[tabs + eitherextratabs + eitherifextratabs + 1] = parents[tabs + eitherextratabs + eitherifextratabs][tag][text] = {}
            osloc = osloc[endlinepos + 1:]
            if len(osloc) == 0:
                break

    if expand:
        expandor(jsondata, licensename)

    if optimize:
        optjson(jsondata)

    if licenses > 1:
        alljsondata = {}
        if merge:
            new = {}
            mergednames = ''
            for licensename in jsondata:
                licensedata = jsondata[licensename]
                if 'COPYLEFT CLAUSE' not in licensedata:
                    licensedata['COPYLEFT CLAUSE'] = 'No'
                if 'PATENT HINTS' not in licensedata:
                    licensedata['PATENT HINTS'] = 'No'
                if mergednames == '':
                    mergednames = licensename
                    mergeddata = licensedata
                else:
                    mergednames = mergednames + '|' + licensename
                    if verbose:
                        print(mergednames)
                    new = extend(mergeddata, licensedata, new, devel)

            if optimize:
                optjson(new)
            alljsondata[mergednames] = new
        else:
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

def main():
    filenamehelp = 'file names of OSLOC files to process'
    if int(sys.version[0]) < 3:
# pragma pylint: disable=used-before-assignment
        parser = OptionParser(prog = 'osloc2json.py', usage = '%prog [-h] -f [OUTPUT] [-m] [-o] [-r] [-s] [-v] OSLOC [OSLOC ...]',
          description = 'positional arguments:   ' + filenamehelp)
        parser.add_argument = parser.add_option
        filenametype = 'string'
    else:
        parser = argparse.ArgumentParser(prog = 'osloc2json.py', formatter_class = argparse.RawTextHelpFormatter,
          epilog = 'Either a single OSLOC file is parsed, converted to JSON format and saved under the original name with the suffix ".json", or\n\
all OSLOC files are parsed, concatenated to a single JSON object and stored under "osloc.json" or OUTPUT if specified, or\n\
(-m) all OSLOC files are parsed, merged into a single JSON object (lists concatenated, duplicates removed) and stored under "merged.json" or OUTPUT if specified')
        parser.add_argument('licensefilenames',
          metavar = 'OSLOC',
          nargs='+',
          help = filenamehelp)
        filenametype = pathlib.Path
    parser.add_argument('-f', '--filename',
      type = filenametype,
      metavar = 'OUTPUT',
      default = 'osloc.json',
      nargs='?',
      help = 'name of output file for multiple licenses, has no effect if single license, default "osloc.json"')
    parser.add_argument('-d', '--devel',
      action = 'store_true',
      default = False,
      help = 'enable output of information that may be useful for development')
    parser.add_argument('-e', '--expand',
      action = 'store_true',
      default = False,
      help = 'replace keys connected by OR with the individual keys and assign the value of the key to all of them')
    parser.add_argument('-m', '--merge',
      action = 'store_true',
      default = False,
      help = 'merge all licenses into a single one, has no effect if single license, default file name "merged.json"')
    parser.add_argument('-o', '--optimize',
      action = 'store_true',
      default = False,
      help = 'convert a dict with no values to a list of keys or string, if only one, add "-opt" to output file name')
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
        if args.merge:
            parser.set_defaults(filename='merged.json')
            (args, filenames) = parser.parse_args()
        if len(filenames) < 1:
            print("error: the following arguments are required: OSLOC")
    else:
        args = parser.parse_args()
        if args.merge:
            parser.set_defaults(filename='merged.json')
            args = parser.parse_args()
        filenames = args.licensefilenames

    osloc2json(filenames, args.filename, json, args)

if __name__ == '__main__':
    main()
