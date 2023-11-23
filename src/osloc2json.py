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
    """ Remove duplicates, sort case-unsensitive alphabetically, remove singular form, if plural of same term exists """
    sane = sortlist(list(dict.fromkeys(l)))
    return mkpluralonlylist(sane)

def mkpluralonlylist(l):
    """ Remove singular form of list element, if plural of same term exists """
    for e in l.copy():
        if not e.endswith('s') and e + 's' in l:
            l.remove(e)
    return l

def sortlist(l):
    """ Sort list case-unsensitive alphabetically """
    return mkpluralonlylist(sorted(l, key = lambda s: s.lower()))

def mkpluralonlydict(d):
    """ Remove singular form of dict key with identical value, if plural of this key exists """
    for k in d.copy():
        if not k.endswith('s') and k + 's' in d and d[k] == d[k + 's']:
            d.pop(k)
    return d

def expandor(d, parent):
    """ Split a dict item with two OR-ed conditions into two separate items with the same value """
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
    """ Recursively print all dicts of a dict (for debugging only) """
    for k, v in d.items():
        if isinstance(v, dict):
            printdict(v)
        else:
            print("{0} : {1}".format(k, v))

def nonecheck(d):
    """ Recursively check a dict for None values (for debugging only) """
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
    """ Print the instance of a value (for debugging only) """
    if isinstance(v, str):
        return 'str'
    if isinstance(v, list):
        return 'list'
    if isinstance(v, dict):
        return 'dict'
    return 'other'

def isemptyusecase(chain, v):
    """ Check for empty USE CASEs """
    if len(chain) == 1 and chain[0] == 'USE CASE':
        if isinstance(v, str) or isinstance(v, list):
            return True
        if isinstance(v, dict):
            for vx in v.values():
                if vx == {}:
                    return True
    return False

def list2dict(l, d):
    """ Convert a list to a dict """
    l = l.copy()
    d = d.copy()
    for k in d:
        if k in l:
            l.remove(k)
    for v in l:
        if v not in d:
            d[v] = {}
    return d

def listinlist(testlist, fulllist):
    """ Check whether two lists are identical or one is a subset of the other """
    if testlist == fulllist:
        return True
    return set(testlist).issubset(fulllist)

def dictindict(sub, super):
    """ Check whether two dicts are identical or one is a subset of the other """
    if sub == super:
        return True
    return all(item in super.items() for item in sub.items())

def dictlistindictlist(sub, super):
    """ Check whether two dicts are identical or all list items of one are a subset of the list items of the other """
    if sub == super:
        return True
    for k in sub:
        if k not in super or not isinstance(sub[k], list) or not isinstance(super[k], list) or not listinlist(sub[k], super[k]):
            return False
    return True

def extend(l1, l2, devel, chain1, chain2):
    """ Recursively add a dict to another dict while removing duplicates and extending items with the same key """
    if l1 == l2:
        return l1
    new = l1.copy()

    for k1, v1 in l1.items():
        chain1.append(k1)
        for k2, v2 in l2.items():
            chain2.append(k2)
            if chain1 == chain2 and v1 == v2:
                chain2.pop()
                continue
            if isinstance(v2, str):
                if chain1 == chain2:
                    if isinstance(new[k1], str):
                        if v2 != new[k1]:
                            new[k1] = [new[k1], v2]
                    elif isinstance(new[k1], list):
                        if v2 not in new[k1]:
                            new[k1].append(v2)
                            new[k1] = sortlist(new[k1])
                    elif isinstance(new[k1], dict):
                        if v2 not in new[k1]:
                            new[k1][v2] = {}
                else:
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] != v2:
                                new[k2] = [new[k2], v2]
                        elif isinstance(new[k2], list):
                            if v2 not in new[k2]:
                                new[k2].append(v2)
                                new[k2] = sortlist(new[k2])
                        elif isinstance(new[k2], dict):
                            if v2 not in new[k2]:
                                new[k2][v2] = {}

            elif isinstance(v2, list):
                if chain1 == chain2:
                    if isinstance(new[k1], str):
                        if new[k1] not in v2:
                            v2.append(new[k1])
                            new[k1] = v2.copy()
                    elif isinstance(new[k1], list):
                        if not listinlist(v2, new[k1]):
                            new[k1] += v2.copy()
                            new[k1] = sanitizelist(new[k1])
                    elif isinstance(new[k1], dict):
                        new[k1] = list2dict(v2, new[k1])
                else:
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] not in v2:
                                v2.append(new[k2])
                                new[k2] = v2.copy()
                        elif isinstance(new[k2], list):
                            if not listinlist(v2, new[k2]):
                                new[k2] += v2
                                new[k2] = sanitizelist(new[k2])
                        elif isinstance(new[k2], dict):
                            new[k2] = list2dict(v2, new[k2])

            elif isinstance(v2, dict):
                if chain1 == chain2:
                    if isinstance(new[k1], str):
                        if new[k1] not in v2:
                            v2[new[k1]] = {}
                        new[k1] = v2.copy()
                    elif isinstance(new[k1], list):
                        new[k1] = list2dict(new[k1], v2)
                    elif isinstance(new[k1], dict):
                        if not dictlistindictlist(v2, new[k1]):
                            new[k1] = extend(new[k1], v2, devel, chain1, chain2)
                else:
                    if k2 not in new:
                        new[k2] = v2
                    else:
                        if isinstance(new[k2], str):
                            if new[k2] not in v2:
                                v2[new[k2]] = {}
                        elif isinstance(new[k2], list):
                            for k in v2.keys():
                                if k in new[k2]:
                                    new[k2].remove(k)
                            for v in new[k2]:
                                if v not in v2:
                                    v2[v] = {}
                            new[k2] = v2.copy()
                        elif isinstance(new[k2], dict):
                            if not dictlistindictlist(v2, new[k2]):
                                new[k2] = extend(new[k2], v2, devel, chain2.copy(), chain2)
            chain2.pop()
        chain1.pop()
    if isinstance(new, dict):
        new = mkpluralonlydict(new)
    return new

def optjson(l):
    """ 1. If a dict has only keys, but no values, convert it to a list of keys
        2. If a dict has a list with a single element, propagate it to the parent dict
        3. If a dict has a dict with a single element with an empty key, propagate the dict to the parent dict
        4. If a dict has only dicts with consecutively numbered numeric keys, propagate the dicts into a list """
    if isinstance(l, dict):
        for e in l:
            if l[e]:
                optjson(l[e])
                if isinstance(l[e], dict):
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
                if isinstance(l[e], list):
                    if len(l[e]) == 1:
                        l[e] = l[e][0]
                    else:
                        l[e] = sorted(l[e], key = lambda s: s.lower())

printnonl = sys.stdout.write
def back2osloc(l, indent, key, eitherkey, parent):
    if isinstance(l, dict):
        count = 0
        for e in l.copy():
            if indent == 0 and e == 'COMPATIBILITY':
                if isinstance(l[e], list):
                    for v in l[e]:
                        print()
                        printnonl(e + ' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'DEPENDING COMPATIBILITY':
                if isinstance(l[e], list):
                    for v in l[e]:
                        print()
                        printnonl(e + ' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'INCOMPATIBILITY':
                if isinstance(l[e], list):
                    for v in l[e]:
                        print()
                        printnonl(e + ' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'INCOMPATIBLE LICENSES':
                if isinstance(l[e], list):
                    for v in l[e]:
                        print()
                        printnonl(e + ' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'PATENT HINTS':
                if isinstance(l[e], list):
                    print()
                    printnonl(e)
                    for v in l[e]:
                        printnonl(' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'COPYLEFT CLAUSE':
                if isinstance(l[e], list):
                    print()
                    printnonl(e)
                    for v in l[e]:
                        printnonl(' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'COPYLEFT LICENSES':
                continue
            if e == 'EITHER':
                keystring = list(l[e].keys())[0]
                if int(keystring) in range(0, 100):
                    l[e] = l[e][keystring]
                    eitherkey[indent] = keystring
            if e == 'OR':
                if indent-4 in eitherkey:
                    indent -= 4
                    keystring = list(parent[e].keys())[0]
                    if int(keystring) in range(0, 100):
                        parent[e] = parent[e][keystring]
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
            back2osloc(l[e], indent + increment, e, eitherkey, l[e])
            count = count + 1
    elif isinstance(l, list):
        count = 0
        for e in l.copy():
            if isinstance(e, dict):
                back2osloc(e, indent, key, eitherkey, l[e])
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
    elif isinstance(l, str):
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
                tag = line[0:23]
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
            copyleft_licenses = []
            mergednames = ''
            compatibilities = {}
            compatibilities_no = 0
            depending_compatibilities = {}
            depending_compatibilities_no = 0
            for licensename in jsondata:
                licensedata = jsondata[licensename]
                if 'USE CASE' in licensedata:
                    chain = ['USE CASE']
                    if isemptyusecase(chain, licensedata['USE CASE']):
                        Nonetext = "Not do anything for now"
                        if isinstance(licensedata['USE CASE'], list):
                            oldlist = licensedata['USE CASE']
                            licensedata['USE CASE'] = {}
                            for usecase in oldlist:
                                licensedata['USE CASE'][usecase] = {}
                                licensedata['USE CASE'][usecase]['YOU MUST'] = Nonetext
                        elif isinstance(licensedata['USE CASE'], dict):
                            for usecase in licensedata['USE CASE']:
                                if licensedata['USE CASE'][usecase] == {}:
                                    licensedata['USE CASE'][usecase]['YOU MUST'] = Nonetext
                if 'COMPATIBILITY' in licensedata:
                    compatibilities_no += 1
                    if isinstance(licensedata['COMPATIBILITY'], str):
                        all = [licensedata['COMPATIBILITY'], licensename]
                    elif isinstance(licensedata['COMPATIBILITY'], list):
                        all = sanitizelist(licensedata['COMPATIBILITY'] + [licensename])
                    for compatibility in all:
                        if compatibility not in compatibilities:
                            compatibilities[compatibility] = 1
                        else:
                            compatibilities[compatibility] += 1
                if 'DEPENDING COMPATIBILITY' in licensedata:
                    depending_compatibilities_no += 1
                    if isinstance(licensedata['DEPENDING COMPATIBILITY'], str):
                        all = [licensedata['DEPENDING COMPATIBILITY'], licensename]
                    elif isinstance(licensedata['DEPENDING COMPATIBILITY'], list):
                        all = sanitizelist(licensedata['DEPENDING COMPATIBILITY'] + [licensename])
                    for compatibility in all:
                        if compatibility not in depending_compatibilities:
                            depending_compatibilities[compatibility] = 1
                        else:
                            depending_compatibilities[compatibility] += 1
                if 'COPYLEFT CLAUSE' not in licensedata:
                    licensedata['COPYLEFT CLAUSE'] = 'No'
                else:
                    copyleft_licenses.append(licensename)
                if 'PATENT HINTS' not in licensedata:
                    licensedata['PATENT HINTS'] = 'No'
                if mergednames == '':
                    mergednames = licensename
                    new = licensedata
                else:
                    mergednames = mergednames + '|' + licensename
                    if verbose:
                        print(mergednames)
                    new = extend(new, licensedata, devel, [], [])

            new['COMPATIBILITY'] = []
            for k, v in compatibilities.items():
                if v == compatibilities_no:
                    new['COMPATIBILITY'].append(k)
            if len(new['COMPATIBILITY']) == 0:
                new.pop('COMPATIBILITY')
            new['DEPENDING COMPATIBILITY'] = []
            for k, v in depending_compatibilities.items():
                if v == depending_compatibilities_no:
                    new['DEPENDING COMPATIBILITY'].append(k)
            if len(new['DEPENDING COMPATIBILITY']) == 0:
                new.pop('DEPENDING COMPATIBILITY')

            if optimize:
                optjson(new)
            if len(copyleft_licenses) > 0:
                new['COPYLEFT LICENSES'] = copyleft_licenses
            if 'INCOMPATIBILITY' in new:
                incompatible_licenses = []
                names = mergednames.split('|')
                for license in names:
                    if license in new['INCOMPATIBILITY']:
                        incompatible_licenses.append(license)
                for copyleft_license in copyleft_licenses:
                    if 'COMPATIBILITY' in new and copyleft_license not in new['COMPATIBILITY']:
                        incompatible_licenses.append(copyleft_license)
                if len(incompatible_licenses) > 0:
                    new['INCOMPATIBLE LICENSES'] = incompatible_licenses
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
        back2osloc(l, 0, '', {}, {})
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

    if '+' in filenames[0]:
        filenames = filenames[0].split('+')
        filenames = [s + '.txt' for s in filenames]

    osloc2json(filenames, args.filename, json, args)

if __name__ == '__main__':
    main()
