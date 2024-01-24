#!/usr/bin/env python

# This software is licensed under GPL-3.0
# Copyright (c) 2023 Open Source Automation Development Lab (OSADL) eG <info@osadl.org>
# Author Carsten Emde <C.Emde@osadl.org>

# Maintain Python 2.x compatibility
# pylint: disable=consider-using-with,unspecified-encoding

import os
import re
import sys

try:
    import argparse
    import pathlib
    import json
except ImportError:
    import simplejson as json
    from optparse import OptionParser

try:
    import inspect
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

def sortdict(d):
    """ Sort dict alphabetically by key """
    if isinstance(d, dict):
        keylist = list(d.keys())
        keylist.sort()
        dsorted = {}
        for key in keylist:
            dsorted[key] = d[key]
        return dsorted
    return d

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

def commonlistitem(a, b):
    aset = set(a)
    bset = set(b)
    if len(aset.intersection(bset)) > 0:
        return True
    return False

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

def flatten(v, prefix=''):
    result = []
    if isinstance(v, dict):
        for k, v2 in v.items():
            p2 = "{}['{}']".format(prefix, k)
            if v2 == {}:
                result.append(p2)
            else:
                result.extend(flatten(v2, prefix = p2))
    elif isinstance(v, list):
        for i, v2 in enumerate(v):
            #p2 = "{}['{}']".format(prefix, i)
            #result.extend(flatten(v2, prefix = p2))
            result.extend(flatten(v2, prefix))
    elif isinstance(v, str):
        p2 = "{}['{}']".format(prefix, v)
        result.append(p2)
    return result

def deepcopy(target, source, parent = {}, tag = ''):
    if isinstance(source, dict):
        for k, v in source.copy().items():
            target[k] = {}
            deepcopy(target[k], v, target, k)
    elif isinstance(source, list):
        parent[tag] = []
        for i, v in enumerate(source.copy()):
            parent[tag].append(v)
    elif isinstance(source, str):
        parent[tag] = source

formlang = []
def addlrefs(v, lrefs, parent = {}, tag = '', prefix = ''):
    global formlang

    if formlang == []:
        lang = ['USE CASE', 'YOU MUST', 'YOU MUST NOT', 'ATTRIBUTE', 'IF', 'ELSE', 'EITHER', 'OR', 'EXCEPT IF', 'EITHER IF', 'OR IF']
        for l in lang:
            formlang.append("['{}']".format(l))

    result = []
    if isinstance(v, dict):
        for k, v2 in v.copy().items():
            p2 = "{}['{}']".format(prefix, k)
            found = []
            if p2 in lrefs:
                for lic in lrefs[p2]:
                    if lic not in found:
                        found.append(lic)
            islang = False
            for l in formlang:
                if p2.endswith(l):
                    islang = True
                    break
            if not islang:
                if tag != '' and not re.search(r"\['[0-9]*'\]$", p2):
                    for lref,license in lrefs.items():
                        if lref.startswith(p2):
                            for lic in license:
                                if lic not in found:
                                    found.append(lic)
            newk = k + ' | '
            if found != []:
                found = sorted(found, key = lambda s: s.lower())
            for l in found:
                old = v[k]
                parent[tag].pop(k)
                if newk.endswith(' | '):
                    newk += l
                else:
                    newk += ', ' + l
                parent[tag][newk] = old
                k = newk
            if v2 == {}:
                result.append(p2)
            else:
                result.extend(addlrefs(v2, lrefs, v, k, prefix = p2))
    elif isinstance(v, list):
        for i, v2 in enumerate(v):
            #p2 = "{}['{}']".format(prefix, i)
            #result.extend(addlrefs(v2, lrefs, v, i, prefix = p2))
            result.extend(addlrefs(v2, lrefs, v, i, prefix))
    elif isinstance(v, str):
        p2 = "{}['{}']".format(prefix, v)
        if p2 in lrefs:
            newv = parent[tag] + ' | '
            for l in lrefs[p2]:
                if newv.endswith(' | '):
                    newv += l
                else:
                    newv += ', ' + l
            parent[tag] = newv
        result.append(p2)
    return result

def extend(l1, l2, devel, chain1, chain2, unify):
    """ Recursively add a dict to another dict while removing duplicates and extending items with the same key """
    if l1 == l2:
        return l1
    new = {}
    deepcopy(new, l1)
    newl2 = {}
    deepcopy(newl2, l2)
    l2 = newl2

    for k1, v1 in l1.items():
        chain1.append(k1)
        for k2, v2 in l2.items():
            chain2.append(k2)
            if chain1 == chain2 and v1 == v2:
                chain2.pop()
                continue
            if isinstance(v2, str):
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
                if k2 not in new:
                    new[k2] = v2
                else:
                    if isinstance(new[k2], str):
                        if new[k2] not in v2:
                            v2.append(new[k2])
                            new[k2] = v2.copy()
                    elif isinstance(new[k2], list):
                        if not listinlist(v2, new[k2]):
                            for v in v2:
                                if v not in new[k2]:
                                    new[k2].append(v)
                            new[k2] = sortlist(new[k2])
                    elif isinstance(new[k2], dict):
                        new[k2] = list2dict(v2, new[k2])

            elif isinstance(v2, dict):
                if k2 not in new:
                    new[k2] = v2
                else:
                    if isinstance(new[k2], str):
                        if new[k2] not in v2:
                            v2[new[k2]] = {}
                            new[k2] = v2.copy()
                    elif isinstance(new[k2], list):
                        new[k2] = list2dict(new[k2], v2)
                    elif isinstance(new[k2], dict):
                        if not dictlistindictlist(v2, new[k2]):
                            if new[k2] == {} and v2 != {}:
                                new[k2] = v2
                            else:
                                new[k2] = extend(new[k2], v2, devel, chain2.copy(), chain2, unify)

            chain2.pop()
        chain1.pop()
    if isinstance(new, dict):
        if not unify:
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
def back2osloc(l, indent, key, ineitheror, previous):
    if isinstance(l, dict):
        count = 0
        if previous in ['', 'ATTRIBUTE', 'IF', 'YOU MUST', 'YOU MUST NOT']:
            l = sortdict(l)
        if 'OR' in l:
            newl = {}
            for e in l:
                if e != 'OR':
                    newl[e] = l[e]
            for e in l:
                if e == 'OR':
                    newl[e] = l[e]
            l = newl
        for e in l:
            if indent == 0 and e in ['COMPATIBILITY', 'COPYLEFT CLAUSE', 'DEPENDING COMPATIBILITY', 'INCOMPATIBILITY', 'INCOMPATIBLE LICENSES', 'PATENT HINTS']:
                if isinstance(l[e], list):
                    for v in l[e]:
                        print()
                        printnonl(e + ' ' + v)
                else:
                    print()
                    printnonl(e + ' ' + l[e])
                continue
            if indent == 0 and e == 'COPYLEFT LICENSES':
                continue
            for k in ineitheror:
                if k > indent:
                    ineitheror[k] = ''
            if e == 'OR':
                indent -= 1
            if len(ineitheror) > 0 and not e.isdigit() and indent > 0:
                if indent in ineitheror and ineitheror[indent] != '':
                    if previous != '1':
                        print()
                        printnonl('\t'*(indent-1) + ineitheror[indent])
            if e.isdigit():
                increment = 0
                ineitheror[indent] = previous
            else:
                if not re.search('[a-z]', e):
                    print()
                    if e not in ['EITHER', 'OR']:
                        appendchar = ' '
                    else:
                        appendchar = ''
                    if indent == 0:
                        printnonl(e + appendchar)
                    else:
                        printnonl('\t'*indent + e + appendchar)
                    increment = 1
                else:
                    if count == 0:
                        printnonl(e)
                    else:
                        if indent == 0:
                            printnonl(key + ' ' + e)
                        else:
                            if count == 0:
                                printnonl('\t'*indent + key + ' ' + e)
                            else:
                                print()
                                if indent - 1 == 0:
                                    printnonl(key + ' ' + e)
                                else:
                                    printnonl('\t'*(indent - 1) + key + ' ' + e)
                    increment = 0
            back2osloc(l[e], indent + increment, e, ineitheror, e)
            if e == 'OR':
                indent += 1
            count = count + 1
    elif isinstance(l, list):
        count = 0
        for e in l.copy():
            if isinstance(e, dict):
                back2osloc(e, indent, key, ineitheror, '')
            else:
                if count == 0:
                    printnonl(e)
                else:
                    print()
                    printnonl('\t'*indent + key + ' ' + e)
                count += 1
    elif isinstance(l, str):
        printnonl(l)

def unifyobligations(d, tag, replacelist):
    """ Unify obligations according to semantic rules """
    for k, v in d.items():
        tagrefs = ''
        if isinstance(v, dict) and k in ['YOU MUST', 'YOU MUST NOT', 'ATTRIBUTE']:
            tagrefs = ''
            attribute = {}
            for obligation, v1 in v.items():
                if obligation.split(' | ')[0] == tag:
                    tagrefs = obligation
                    attribute = v1
                    break
            if tagrefs != '':
                for obligation, v1 in v.copy().items():
                    for unifyable in replacelist:
                        if obligation.split(' | ')[0] == unifyable:
                            d[k].pop(obligation)
                            d[k].pop(tagrefs)
                            if '|' in obligation:
                                if '|' in tagrefs:
                                    tagrefs += ', (' + unifyable + '): ' + obligation.split(' | ')[1]
                                else:
                                    tagrefs += ' | (' + unifyable + '): ' + obligation.split(' | ')[1]
                            if attribute == {} and v1 == {}:
                                d[k][tagrefs] = {}
                            elif attribute == {} and v1 != {}:
                                d[k][tagrefs] = v1
                            elif attribute != {} and v1 == {}:
                                d[k][tagrefs] = attribute
                            else:
                                d[k][tagrefs] = extend(v1, attribute, False, [], [], True)
            else:
                unifyobligations(v, tag, replacelist)
        elif isinstance(v, list) and k in ['YOU MUST', 'YOU MUST NOT', 'ATTRIBUTE']:
            tagrefs = ''
            for obligation in v:
                if obligation.split(' | ')[0] == tag:
                    tagrefs = obligation
                    break
            if tagrefs != '':
                for obligation in v:
                    for unifyable in replacelist:
                        if obligation.split(' | ')[0] == unifyable:
                            d[k].remove(obligation)
                            d[k].remove(tagrefs)
                            if '|' in obligation:
                                if '|' in tagrefs:
                                    tagrefs += ', (' + unifyable + '): ' + obligation.split(' | ')[1]
                                else:
                                    tagrefs += ' | (' + unifyable + '): ' + obligation.split(' | ')[1]
                            d[k].append(tagrefs)
                            d[k] = sorted(d[k], key = lambda s: s.lower())
        elif isinstance(v, dict):
            unifyobligations(v, tag, replacelist)

def unifylicenses(licenses, rules):
    """ Open OSLOC files, convert them to JSON objects and store them as specified """
    for k, v in rules.items():
        unifyobligations(licenses, k, v)

def osloc2json(licensefilenames, outfilename, json, args):
    """ Open OSLOC files, convert them to JSON objects and store them as specified """
    devel = args.devel
    expand = args.expand
    merge = args.merge
    optimize = args.optimize
    licenseupgrade = args.licenseupgrade
    recreate = args.recreate
    show = args.show
    unify = args.unify
    verbose = args.verbose

    addobligations = {}

    if licenseupgrade:
        rulesfilename = 'licenseupgraderules.json'
        try:
            rulesfile = open(rulesfilename, 'r')
        except:
            try:
                rulesfile = open('../' + rulesfilename, 'r')
            except:
                printnonl('File "' + rulesfilename + '" not found or not accessible in current or in parent directory: ')
        rules = {}
        try:
            rules = json.load(rulesfile)
            rulesfile.close()
        except:
            print('Skipped attempt to upgrade licenses')
        if len(rules) > 0:
            for license in licensefilenames.copy():
                for oldlicense, value in rules.items():
                    if license.find(oldlicense) != -1:
                        newlicense = license.replace(oldlicense, value[0])
                        licensefilenames.remove(license)
                        if newlicense not in licensefilenames:
                            licensefilenames.append(newlicense)
                        addobligations[value[0]] = value[1]
            licensefilenames = sorted(licensefilenames, key = lambda s: s.lower())

    licenses = len(licensefilenames)

    if licenses == 1:
        suffix = os.path.splitext(licensefilenames[0])[1]
        if optimize:
            optsuffix = '-opt'
        else:
            optsuffix = ''
        outfilename = licensefilenames[0].replace(suffix, '') + optsuffix + '.json'

    jsondata = {}

    for licensefilename in licensefilenames:
        licensefilenameparts = licensefilename.split('/')
        basename = licensefilenameparts[len(licensefilenameparts) - 1]
        suffix = os.path.splitext(licensefilename)[1]
        licensename = basename.replace(suffix, '')
        if licensename.endswith('-opt'):
            licensename = licensename[:-4]
            optimize = True
        if licensename.endswith('.unified'):
            licensename = licensename[:-8]
        licensename = licensename.replace('+', '|')
        if verbose:
            print(licensename + ':')
        oslocfile = open(licensefilename, 'r')
        if suffix == '.json':
            try:
                data = json.load(oslocfile)
            except:
                print('File', licensefilename, 'has no valid JSON format')
                lineno = -1
                break
            oslocfile.close()
            jsonlicensename = list(data.keys())[0]
            if licensename == jsonlicensename:
                jsondata[licensename] = data[licensename]
            else:
                print('File', licensefilename, 'has license', '"' + jsonlicensename + '"', 'but filename indicates license', '"' + licensename + '"')
                jsondata[jsonlicensename] = data[jsonlicensename]
            lineno = 0
        else:
            osloc = oslocfile.read()
            oslocfile.close()
            jsondata[licensename] = {}
            data = jsondata[licensename]
            eitherlevels = {}
            orlevels = {}
            eitherextratabs = 0
            parents = {}
            lineno = 0
            while True:
                endlinepos = osloc.find('\n')
                line = osloc[0:endlinepos]
                if line == '':
                    osloc = osloc[endlinepos + 1:]
                    continue
                lineno += 1
                if line.startswith(' '):
                    print('Syntax error (leading space) detected in license', licensename, 'at line', lineno, '- output will be incomplete.')
                    lineno = -1
                    break
                line = re.sub(r' \(.*\)', '', line)
                if verbose:
                    print(line)
                tabs = line.count('\t')
                if devel:
                    print(tabs, orlevels)
                tag = ''
                text = ''
                if line[0:8] == 'USE CASE':
                    tag = line[0:8]
                    text = line[9:]
                    if tag not in data:
                        data[tag] = {}
                    parents[tabs + 1] = data[tag][text] = {}
                    if devel:
                        print(data[tag])
                    tag = ''
                    eitherextratabs = 0
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
                    print('Unidentified or erroneously positioned language element in license', licensename, 'at line', lineno)
                    if not verbose:
                        print(line)
                    lineno = -1
                    break
                if tag != '':
                    if text == '':
                        text = line[line.find(tag) + len(tag) + 1:]
                    if tabs == 0 and (text == 'Yes' or text == 'No' or text == 'Questionable' or tag.find('COMPATIBILITY') != -1):
                        if tag not in data:
                            data[tag] = text
                            if devel:
                                print(data[tag])
                        else:
                            if isinstance(data[tag], str):
                                oldtext = data[tag]
                                data[tag] = []
                                data[tag].append(oldtext)
                            data[tag].append(text)
                            if devel:
                                print(data[tag])
                    else:
                        if len(parents) == 0 or (tabs == 0 and tag != 'USE CASE'):
                            print('Syntax error', '(illegal position of tag ' + tag + ')' , 'detected in license', licensename, 'at line', lineno, '- output will be incomplete.')
                            lineno = -1
                            break
                        if tag == 'EITHER':
                            if tabs in eitherlevels:
                                eitherlevels[tabs] += 1
                            else:
                                eitherlevels[tabs] = 1
                            text = str(eitherlevels[tabs])
                            for k in orlevels.copy():
                                if tabs <= k:
                                    orlevels.pop(k)
                                    if eitherextratabs > 0:
                                        eitherextratabs -= 1
                            orlevels[tabs] = 0
                        else:
                            if len(eitherlevels) > 0:
                                for k in eitherlevels:
                                    if tabs < k and eitherlevels[k] > 0:
                                        eitherlevels[k] = 0
                        if tag == 'OR':
                            if tabs not in orlevels:
                                print('Syntax error (OR before EITHER) detected in license', licensename, 'at line', lineno, '- output will be incomplete.')
                                lineno = -1
                                break
                            orlevels[tabs] += 1
                            text = str(orlevels[tabs])
                            if orlevels[tabs] == 1:
                                eitherextratabs += 1
                        if tag != 'EITHER':
                            if len(orlevels) > 0:
                                for k in orlevels.copy():
                                    if (tag == 'OR' and tabs < k) or (tag != 'OR' and tabs <= k):
                                        orlevels.pop(k)
                                        if eitherextratabs > 0:
                                            eitherextratabs -= 1
                        if tabs + eitherextratabs in parents:
                            if tag not in parents[tabs + eitherextratabs]:
                                parents[tabs + eitherextratabs][tag] = {}
                            parents[tabs + eitherextratabs + 1] = parents[tabs + eitherextratabs][tag][text] = {}
                            if devel:
                                print(parents[tabs + eitherextratabs][tag])
                osloc = osloc[endlinepos + 1:]
                if len(osloc) == 0:
                    break

        if lineno == -1:
            break
        if licenseupgrade and len(addobligations) > 0:
            for newlicense, obligation in addobligations.items():
                if newlicense != licensename or obligation.find('YOU MUST ') == -1:
                    continue
                for usecase in data['USE CASE']:
                    obligation = obligation.replace('YOU MUST ', '')
                    if 'YOU MUST' not in data['USE CASE'][usecase]:
                        data['USE CASE'][usecase]['YOU MUST'] = {}
                    if obligation not in data['USE CASE'][usecase]['YOU MUST']:
                        data['USE CASE'][usecase]['YOU MUST'][obligation] = {}

    if expand:
        expandor(jsondata, licensename)

    if optimize:
        optjson(jsondata)

    if licenses > 1:
        alljsondata = {}
        if merge:
            allrefs = {}
            copyleft_licenses = []
            mergednames = ''
            compatibilities = {}
            depending_compatibilities = {}
            for licensename in jsondata:
                licensedata = {}
                deepcopy(licensedata, jsondata[licensename])
                if 'USE CASE' in licensedata:
                    chain = ['USE CASE']
                    if isemptyusecase(chain, licensedata['USE CASE']):
                        Nonetext = "Not do anything else"
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
                    if isinstance(licensedata['COMPATIBILITY'], str):
                        all = [licensedata['COMPATIBILITY']]
                    elif isinstance(licensedata['COMPATIBILITY'], list):
                        all = licensedata['COMPATIBILITY']
                    for compatibility in all:
                        if compatibility not in compatibilities:
                            compatibilities[compatibility] = 1
                        else:
                            compatibilities[compatibility] += 1
                if 'DEPENDING COMPATIBILITY' in licensedata:
                    if isinstance(licensedata['DEPENDING COMPATIBILITY'], str):
                        all = [licensedata['DEPENDING COMPATIBILITY']]
                    elif isinstance(licensedata['DEPENDING COMPATIBILITY'], list):
                        all = licensedata['DEPENDING COMPATIBILITY']
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
                    allrefs[licensename] = licensedata
                else:
                    mergednames = mergednames + '|' + licensename
                    if verbose:
                        print(mergednames)
                    allrefs[licensename] = licensedata
                    new = extend(new, licensedata, devel, [], [], unify)

            copyleft_licenses = sorted(copyleft_licenses, key = lambda s: s.lower())

            new['COMPATIBILITY'] = []
            for k, v in compatibilities.items():
                if v == len(copyleft_licenses):
                    new['COMPATIBILITY'].append(k)
            if len(new['COMPATIBILITY']) == 0:
                new.pop('COMPATIBILITY')
            new['DEPENDING COMPATIBILITY'] = []
            for k, v in depending_compatibilities.items():
                if v == len(copyleft_licenses):
                    new['DEPENDING COMPATIBILITY'].append(k)
            if len(new['DEPENDING COMPATIBILITY']) == 0:
                new.pop('DEPENDING COMPATIBILITY')

            licenserefs = {}
            allflat = flatten(new.copy())
            for license, refs in allrefs.items():
                for ref in flatten(refs):
                    for allref in allflat:
                        if allref.startswith(ref):
                            if ref not in licenserefs:
                                licenserefs[ref] = []
                            if license not in licenserefs[ref]:
                                licenserefs[ref].append(license)

            newrefs = {}
            deepcopy(newrefs, new)
            addlrefs(newrefs, licenserefs)

            if 'INCOMPATIBILITY' in new or len(copyleft_licenses) > 0:
                incompatible_licensesrefs = []
                incompatible_licenses = []

                names = mergednames.split('|')
                if 'INCOMPATIBILITY' in new:
                    for license in names:
                        if license in new['INCOMPATIBILITY']:
                            for reflicense in newrefs['INCOMPATIBILITY']:
                                if license == reflicense.split(' | ')[0]:
                                    incompatible_licensesrefs.append(reflicense)
                                    incompatible_licenses.append(license)

                for copyleft_license in copyleft_licenses.copy():
                    if 'COMPATIBILITY' not in new or ('COMPATIBILITY' in new and copyleft_license not in new['COMPATIBILITY']):
                        incompatible_copyleft_licenses_str = ''
                        for copyleft_license2 in copyleft_licenses.copy():
                            if copyleft_license2 == copyleft_license:
                                continue
                            if 'COMPATIBILITY' in jsondata[copyleft_license2] and copyleft_license in jsondata[copyleft_license2]['COMPATIBILITY']:
                                continue
                            if incompatible_copyleft_licenses_str != '':
                                incompatible_copyleft_licenses_str += ', '
                            incompatible_copyleft_licenses_str += copyleft_license2
                        if incompatible_copyleft_licenses_str != '':
                            incompatible_licensesrefs.append(copyleft_license + ' | If licensed under ' + incompatible_copyleft_licenses_str)
                            if copyleft_license not in incompatible_licenses:
                                incompatible_licenses.append(copyleft_license)
                if len(incompatible_licenses) > 0:
                    incompatible_licenses = sorted(incompatible_licenses, key = lambda s: s.lower())
                    new['INCOMPATIBLE LICENSES'] = incompatible_licenses
                    newrefs['INCOMPATIBLE LICENSES'] = incompatible_licensesrefs

            if 'INCOMPATIBLE LICENSES' not in new or ('INCOMPATIBLE LICENSES' in new and not commonlistitem(copyleft_licenses, new['INCOMPATIBLE LICENSES'])):
                for copyleft_license in copyleft_licenses:
                    if 'COMPATIBILITY' not in new or ('COMPATIBILITY' in new and copyleft_license not in new['COMPATIBILITY']):
                        ref = ' | ' + copyleft_license + ' (only copyleft license)'
                        if 'COMPATIBILITY' not in new:
                            new['COMPATIBILITY'] = [copyleft_license]
                            newrefs['COMPATIBILITY'] = [copyleft_license + ref]
                        elif isinstance(new['COMPATIBILITY'], str):
                            new['COMPATIBILITY'] = [new['COMPATIBILITY'], copyleft_license]
                            newrefs['COMPATIBILITY'] = [newrefs['COMPATIBILITY'], copyleft_license + ref]
                        else:
                            new['COMPATIBILITY'].append(copyleft_license)
                            newrefs['COMPATIBILITY'].append(copyleft_license + ref)
                        new['COMPATIBILITY'] = sorted(new['COMPATIBILITY'], key = lambda s: s.lower())
                        newrefs['COMPATIBILITY'] = sorted(newrefs['COMPATIBILITY'], key = lambda s: s.lower())

            if unify:
                rulesfilename = 'unifyrules.json'
                try:
                    rulesfile = open(rulesfilename, 'r')
                except:
                    try:
                        rulesfile = open('../' + rulesfilename, 'r')
                    except:
                        printnonl('File "' + rulesfilename + '" not found or not accessible in current or in parent directory: ')
                try:
                    rules = json.load(rulesfile)
                    rulesfile.close()
                except:
                    print('Cannot unify')

                unifylicenses(newrefs, rules)
                unifylicenses(new, rules)

            if optimize:
                optjson(new)
            if len(copyleft_licenses) > 0:
                new['COPYLEFT LICENSES'] = copyleft_licenses

            alljsondata[mergednames] = new
        else:
            alljsondata['OSADL OSLOC'] = jsondata
        jsondata = alljsondata

    if recreate:
        l = {}
        if merge:
            deepcopy(l, newrefs)
        else:
            deepcopy(l, jsondata)
            if len(jsondata.keys()) == 1:
                l = l[list(jsondata.keys())[0]]
        back2osloc(l, 0, '', {}, '')
        print()

    jsonfile = open(outfilename, 'w')
    json.dump(jsondata, jsonfile, indent = 4, sort_keys = True)
    jsonfile.close()

    if show:
        json.dump(jsondata, sys.stdout, indent = 4, sort_keys = True)
        sys.stdout.write('\n')

def main():
    filenamehelp = 'file names of OSLOC files to process'
    if int(sys.version[0]) < 3:
# pragma pylint: disable=used-before-assignment
        parser = OptionParser(prog = 'osloc2json.py', usage = '%prog [-h] -f [OUTPUT] [-d] [-e] [-l] [-m] [-n] [-o] [-r] [-s] [-u] [-v] OSLOC [OSLOC ...]',
          description = 'positional arguments:   ' + filenamehelp)
        parser.add_argument = parser.add_option
        filenametype = 'string'
    else:
        parser = argparse.ArgumentParser(prog = 'osloc2json.py', formatter_class = argparse.RawTextHelpFormatter,
            epilog = 'Either a single ".txt" suffixed OSLOC input file is parsed, converted to JSON format and saved under the original name with the suffix\n\
replaced by ".json", or all OSLOC files are parsed, concatenated to a single JSON object and stored under "osloc.json" or (-f) OUTPUT\n\
if specified, or (-m) all OSLOC files are parsed, merged into a single JSON object (lists concatenated, duplicates removed) and stored under\n\
"merged.json". The input files may already be in JSON format, but all processing except the conversion to JSON remains the same, unless the\n\
-n option is used. The -n option is primarily intended for JSON validation (-jn), if this is the only required action.')
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
    parser.add_argument('-j', '--jsonvalidate',
      action = 'store_true',
      default = False,
      help = 'validate input files in JSON format against the OSLOC schema')
    parser.add_argument('-l', '--licenseupgrade',
      action = 'store_true',
      default = False,
      help = 'attempt to avoid license incompatibility by upgrading licenses according to rules in "licenseupgraderules.json"')
    parser.add_argument('-m', '--merge',
      action = 'store_true',
      default = False,
      help = 'merge all licenses into a single one, has no effect if single license, default file name "merged.json"')
    parser.add_argument('-n', '--noop',
      action = 'store_true',
      default = False,
      help = 'do not execute any conversion operation')
    parser.add_argument('-o', '--optimize',
      action = 'store_true',
      default = False,
      help = 'convert a dict with no values to a list of keys or string, append "-opt" to output file name if only one dict')
    parser.add_argument('-p', '--profiling',
      action = 'store_true',
      default = False,
      help = 'enable snapshot profiling')
    parser.add_argument('-r', '--recreate',
      action = 'store_true',
      default = False,
      help = 'recreate original checklist from JSON')
    parser.add_argument('-s', '--show',
      action = 'store_true',
      default = False,
      help = 'also list the output to screen')
    parser.add_argument('-u', '--unify',
      action = 'store_true',
      default = False,
      help = 'unify merged license obligations if they are semantically similar as defined in the semantic dict "unifyrules.json"')
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

    if not args.jsonvalidate and '+' in filenames[0]:
        dirname = os.path.dirname(filenames[0])
        if len(dirname) > 0:
            dirname += '/'
        splitfilename = os.path.basename(filenames[0])
        if splitfilename.endswith('.json'):
            splitfilename = splitfilename[:-5]
        if splitfilename.endswith('.unified'):
            splitfilename = splitfilename[:-8]
        splitfilenames = splitfilename.split('+')
        splitfilenames[0] = os.path.basename(splitfilenames[0])
        splitfilenames = [dirname + s + '.txt' for s in splitfilenames]
        filenames = splitfilenames

    if args.profiling:
        from pyinstrument import Profiler
        with Profiler(interval=0.0001) as profiler:
            osloc2json(filenames, args.filename, json, args)
        profiler.print()
    else:
        if args.jsonvalidate:
            import fastjsonschema
            schema = open('osloc-schema.json', 'r')
            schemadata = json.load(schema)
            validator = fastjsonschema.compile(schemadata)
            for filename in filenames:
                suffix = os.path.splitext(filename)[1]
                if suffix != '.json':
                    continue
                sample = open(filename, 'r')
                sampledata = json.load(sample)
                try:
                    validator(sampledata)
                except fastjsonschema.JsonSchemaException as e:
                    print(f"Data failed validation: {e}")
                sample.close()
            schema.close()
        if not args.noop:
            osloc2json(filenames, args.filename, json, args)

if __name__ == '__main__':
    main()
