# OSLOC2JSON

* [Purpose](#purpose)
* [Command line options](#command-line-options)
* [Disclaimer](#disclaimer)
* [Examples how to use the software](#examples-how-to-use-the-software)
  * [Convert an OSLOC file to JSON format](#convert-an-osloc-file-to-json-format)
  * [Optimization](#optimization)
  * [License upgrade](#license-upgrade)
  * [Merging](#merging)
    * [Additional command line option when in merge mode](#additional-command-line-option-when-in-merge-mode)
    * [Additional keys available when in merge mode](#additional-keys-available-when-in-merge-mode)
    * [Some more merging examples](#some-more-merging-examples)
    * [Merging limitations](#merging-limitations)
* [Schema](#schema)

## Purpose
Convert the [OSADL Open Source License Obligations
Checklists](https://www.osadl.org/OSLOC) into JSON format and provide functions
for evaluating license obligations with each other, such as generating joint
checklists of several licenses.

## Command line options
```bash
osloc2json.py --help
```
```
usage: osloc2json.py [-h] [-f [OUTPUT]] [-1] [-d] [-e] [-j] [-l] [-m] [-n] [-o] [-p] [-r] [-s] [-u] [-v] OSLOC [OSLOC ...]

positional arguments:
  OSLOC                 file names of OSLOC files to process

options:
  -h, --help            show this help message and exit
  -f [OUTPUT], --filename [OUTPUT]
                        name of output file for multiple licenses, has no effect if single license, default "osloc.json"
  -1, --v1              use version 1 of the JSON data structure
  -d, --devel           enable output of information that may be useful for development
  -e, --expand          replace keys connected by OR with the individual keys and assign the value of the key to all of them
  -j, --jsonvalidate    validate input files in JSON format against the OSLOC schema
  -l, --licenseupgrade  attempt to avoid license incompatibility by upgrading licenses according to rules in "licenseupgraderules.json"
  -m, --merge           merge all licenses into a single one, has no effect if single license, default file name "merged.json"
  -n, --noop            do not execute any conversion operation
  -o, --optimize        convert a dict with no values to a list of keys or string, append "-opt" to output file name if only one dict
  -p, --profiling       enable snapshot profiling
  -r, --recreate        recreate original checklist from JSON
  -s, --show            also list the output to screen
  -u, --unify           unify merged license obligations if they are semantically similar as defined in the semantic dict "unifyrules.json"
  -v, --verbose         show names and texts the program is using

Either a single ".txt" suffixed OSLOC input file is parsed, converted to JSON format and saved under the original name with the suffix
replaced by ".json", or all OSLOC files are parsed, concatenated to a single JSON object and stored under "osloc.json" or (-f) OUTPUT
if specified, or (-m) all OSLOC files are parsed, merged into a single JSON object (lists concatenated, duplicates removed) and stored under
"merged.json". The input files may already be in JSON format, but all processing except the conversion to JSON remains the same, unless the
-n option is used. The -n option is primarily intended for JSON validation (-jn), if this is the only required action.
```

## Disclaimer
This is a software tool, no legal advice.

## Examples how to use the software
### Usage scenarios
#### Conversion to JSON format
```bash
osloc2json.py OSLOC.txt
```
Output will be written to OSLOC.json.

#### Conversion to OSLOC format
```bash
osloc2json.py -r OSLOC.json >OSLOC.txt
```
Output will be written to standard output.

#### Concatenation of several OSLOC or JSON files
```bash
osloc2json.py FILE-1 FILE-2 FILE-N
```
Output will be written to "osloc.json".

#### Merging (remove duplicates, concatenate additional obligations) of several OSLOC or JSON files
```bash
osloc2json.py -m FILE-1 FILE-2 FILE-N
```
Output will be written to "merged.json".

#### Extended merging (remove duplicates, concatenate additional obligations) of several OSLOC or JSON files
```bash
./src/osloc2json.py -elmours FILE-1 FILE-2 FILE-N
```
Extend OR-ed use cases into serveral ones, allow license upgrade according to
rules in file "licenseupgraderules.json", optimize JSON ouput, unify expressions
according to unify rules in file "unifyrules.json", convert output to OSLOC
format and write it to standard output, write resulting JSON file to standard
output and store it in file "merged.json".

#### Validate JSON input files against OSLOC schema
```bash
./src/osloc2json.py -jn FILE-1 FILE-2 FILE-N
```
JSON error description will be written to standard output if any

### Input and output files of a conversion of an OSLOC file to JSON format
Original OSLOC file of the Freetype Project License (FTL):
```
USE CASE Source code delivery
	YOU MUST Forward License text
	YOU MUST NOT Modify License text
	IF Software modification
		YOU MUST Provide Modification report
	YOU MUST Forward Copyright notices
	YOU MUST NOT Promote
	YOU MUST Credit FreeType Team
USE CASE Binary delivery
	YOU MUST Credit In Documentation FreeType Team
	YOU MUST NOT Promote
	YOU MUST Credit FreeType Team
```

After running
```bash
osloc2json.py FTL.txt
```
the following output is available in the file "FTL.json":
```json
{
    "FTL": {
        "USE CASE": {
            "Source code delivery": {
                "YOU MUST": {
                    "Forward License text": {},
                    "Forward Copyright notices": {},
                    "Credit FreeType Team": {}
                },
                "YOU MUST NOT": {
                    "Modify License text": {},
                    "Promote": {}
                },
                "IF": {
                    "Software modification": {
                        "YOU MUST": {
                            "Provide Modification report": {}
                        }
                    }
                }
            },
            "Binary delivery": {
                "YOU MUST": {
                    "Credit In Documentation FreeType Team": {},
                    "Credit FreeType Team": {}
                },
                "YOU MUST NOT": {
                    "Promote": {}
                }
            }
        }
    }
}
```

### Optimization
Because of the freedom offered by the OSLOC "language", JSON dict keys can have
no values. If all keys of a dict do not have values, the dict can be converted
into a list of keys or even to a string, if the list has only one element. This
is done when the "--optimize" flag is selected. Thus, after running
```bash
osloc2json.py -o FTL.txt
```
the following optimized output is available in the file "FTL-opt.json":
```json
{
    "FTL": {
        "USE CASE": {
            "Binary delivery": {
                "YOU MUST": [
                    "Credit FreeType Team",
                    "Credit In Documentation FreeType Team"
                ],
                "YOU MUST NOT": "Promote"
            },
            "Source code delivery": {
                "IF": {
                    "Software modification": {
                        "YOU MUST": "Provide Modification report"
                    }
                },
                "YOU MUST": [
                    "Credit FreeType Team",
                    "Forward Copyright notices",
                    "Forward License text"
                ],
                "YOU MUST NOT": [
                    "Modify License text",
                    "Promote"
                ]
            }
        }
    }
}
```
As can be seen in this diff
```diff
--- ../OSLOC/unreflicenses/FTL.json
+++ ../OSLOC/unreflicenses/FTL-opt.json
@@ -2,31 +2,27 @@
     "FTL": {
         "USE CASE": {
             "Binary delivery": {
-                "YOU MUST": {
-                    "Credit FreeType Team": {},
-                    "Credit In Documentation FreeType Team": {}
-                },
-                "YOU MUST NOT": {
-                    "Promote": {}
-                }
+                "YOU MUST": [
+                    "Credit FreeType Team",
+                    "Credit In Documentation FreeType Team"
+                ],
+                "YOU MUST NOT": "Promote"
             },
             "Source code delivery": {
                 "IF": {
                     "Software modification": {
-                        "YOU MUST": {
-                            "Provide Modification report": {}
-                        }
+                        "YOU MUST": "Provide Modification report"
                     }
                 },
-                "YOU MUST": {
-                    "Credit FreeType Team": {},
-                    "Forward Copyright notices": {},
-                    "Forward License text": {}
-                },
-                "YOU MUST NOT": {
-                    "Modify License text": {},
-                    "Promote": {}
-                }
+                "YOU MUST": [
+                    "Credit FreeType Team",
+                    "Forward Copyright notices",
+                    "Forward License text"
+                ],
+                "YOU MUST NOT": [
+                    "Modify License text",
+                    "Promote"
+                ]
             }
         }
     }
```
all keys in dicts without values have been converted to simple list elements.

### License upgrade
Newer versions of licenses may be available that may offer more options with
respect to license compatibility. Related upgrade rules may be defined in a file
named "licenseupgraderules.json" with an associative array of two-element lists
where the key denotes the licenses to be upgraded, the first list element the
license to upgrade to and the optional second list element comma-separated
license obligations to add such as, for example, "YOU MUST Notify License
change". To enable automatic license upgrade, the "-l" or "--licenseupgrade"
command line option must be specified. An upgrade rule file may look like the
following example:
```json
{
  "EUPL-1.1": ["EUPL-1.2", "YOU MUST NOT Restrict License change,YOU MUST Use EUPL-1.2 License"],
  "MPL-1.1": ["MPL-2.0", "YOU MUST Notify License change,YOU MUST Use MPL-2.0 License"],
  "GPL-2.0-or-later": ["GPL-3.0-or-later", "YOU MUST Use GPL-3.0-or-later License"]
}
```

### Merging
Two or more OSLOC files may be merged in such a way that additional license
obligations of the same conditions are concatenated and duplicates are removed.
By default, the resulting merged checklist will be written to a file named
"merged.json", but can be specified using the -f option. Here also, the -o
option can be used.

#### Expanding OR-linked conditions
Use cases that contain multiple OR-linked subconditions may optionally be split
into independent individual use cases, which can then be subsumed with the
conditions of checklists that contain them in unlinked form in the first place.
The MIT checklist, for example, combines the two conditions "Binary delivery"
and "Source code delivery" to "Binary delivery OR Source code delivery"

```json
{
    "MIT": {
        "USE CASE": {
            "Source code delivery OR Binary delivery": {
                "YOU MUST": [
                    "Provide Copyright notices",
                    "Provide License text",
                    "Provide Warranty disclaimer"
                ]
            }
        }
    }
}
```
which may be split into the single conditions "Binary delivery" and "Source code
delivery" using the '-e' command line option of the Python script. This makes it
possible to subsume them, for example, with the respective conditions of the FTL
checklist:
```json
{
    "FTL|MIT": {
        "COPYLEFT CLAUSE": "No",
        "PATENT HINTS": "No",
        "USE CASE": {
            "Binary delivery": {
                "YOU MUST": [
                    "Credit FreeType Team",
                    "Credit In Documentation FreeType Team",
                    "Provide Copyright notices",
                    "Provide License text",
                    "Provide Warranty disclaimer"
                ],
                "YOU MUST NOT": "Promote"
            },
            "Source code delivery": {
                "IF": {
                    "Software modification": {
                        "YOU MUST": "Provide Modification report"
                    }
                },
                "YOU MUST": [
                    "Credit FreeType Team",
                    "Forward Copyright notices",
                    "Forward License text",
                    "Provide Copyright notices",
                    "Provide License text",
                    "Provide Warranty disclaimer"
                ],
                "YOU MUST NOT": [
                    "Modify License text",
                    "Promote"
                ]
            }
        }
    }
}
```
The above checklist was generated with the command
```bash
osloc2json.py -emo FTL.txt MIT.txt
```
The effect of merging the MIT with the FTL license obligations checklist can be
further illustrated in the context diff between the original FTL and the FTL/MIT
merged checklist:
```diff
--- ../OSLOC/unreflicenses/FTL-opt.json
+++ merged.json
@@ -1,10 +1,15 @@
 {
-    "FTL": {
+    "FTL|MIT": {
+        "COPYLEFT CLAUSE": "No",
+        "PATENT HINTS": "No",
         "USE CASE": {
             "Binary delivery": {
                 "YOU MUST": [
                     "Credit FreeType Team",
-                    "Credit In Documentation FreeType Team"
+                    "Credit In Documentation FreeType Team",
+                    "Provide Copyright notices",
+                    "Provide License text",
+                    "Provide Warranty disclaimer"
                 ],
                 "YOU MUST NOT": "Promote"
             },
@@ -17,7 +22,10 @@
                 "YOU MUST": [
                     "Credit FreeType Team",
                     "Forward Copyright notices",
-                    "Forward License text"
+                    "Forward License text",
+                    "Provide Copyright notices",
+                    "Provide License text",
+                    "Provide Warranty disclaimer"
                 ],
                 "YOU MUST NOT": [
                     "Modify License text",
```
Without the option to expand OR-ed conditions the merged checklist would look like
```json
{
    "FTL|MIT": {
        "COPYLEFT CLAUSE": "No",
        "PATENT HINTS": "No",
        "USE CASE": {
            "Binary delivery": {
                "YOU MUST": [
                    "Credit FreeType Team",
                    "Credit In Documentation FreeType Team"
                ],
                "YOU MUST NOT": "Promote"
            },
            "Source code delivery": {
                "IF": {
                    "Software modification": {
                        "YOU MUST": "Provide Modification report"
                    }
                },
                "YOU MUST": [
                    "Credit FreeType Team",
                    "Forward Copyright notices",
                    "Forward License text"
                ],
                "YOU MUST NOT": [
                    "Modify License text",
                    "Promote"
                ]
            },
            "Source code delivery OR Binary delivery": {
                "YOU MUST": [
                    "Provide Copyright notices",
                    "Provide License text",
                    "Provide Warranty disclaimer"
                ]
            }
        }
    }
}
```
which would be rather meaningless. It must, however, be noted that this expansion feature requires that only complete use cases are OR-ed together. If, for example, the above use case had been
```
USE CASE Source code OR Binary delivery
```
the expansion would have led to
```
USE CASE Source code
```
and
```
USE CASE Binary delivery
```
whereby the former could not have been merged with another occurrence of "IF Source code delivery". Similarly in order to correctly use the expansion feature,
```
USE CASE Source code delivery OR Binary delivery Of Combined library
```
would lead to an incorrect merge result, but
```
USE CASE Source code delivery Of Combined library OR Binary delivery Of Combined library
```
would work.

### Additional command line option when in merge mode
In merge mode, the -u (--unify) option may be specified which will remove
semantically redundant obligations defined in the file "unifyrules.json". This
file is expected to contain dicts with an associated list of obligations each of
them will be replaced by the obligation specified in the key if both the key and
the particular obligation are contained in license obligations of the same
condition or use case.

The rules file "unifyrules.json" currently contains the following settings:
```json
{
  "Provide License text": ["Provide License notice", "Reference License text", "Forward License text"],
  "Provide Copyright notices": ["Provide Copyright notice", "Forward Copyright notices"],
  "Provide Warranty disclaimer": ["Forward Warranty disclaimer"],
  "Provide License text In Documentation": ["Provide License text"],
  "Provide Copyright notices In Documentation": ["Provide Copyright notices"],
  "Provide Warranty disclaimer In Documentation": ["Provide Warranty disclaimer"],
  "Provide License text In Documentation OR Distribution material": ["Provide License text In Documentation", "Provide License text"],
  "Provide Copyright notices In Documentation OR Distribution material": ["Provide Copyright notices In Documentation", "Provide Copyright notices"],
  "Provide Warranty disclaimer In Documentation OR Distribution material": ["Provide Warranty disclaimer In Documentation", "Provide Warranty disclaimer"],
  "Provide Modification report": ["Provide Modification notice"],
  "Modify Warranty disclaimers": ["Modify Warranty disclaimer"]
}
```

For example, merging the licenses FTL, MIT, BSD-2-Clause, BSD-3-Clause,
Apache-2.0 and GPL-3.0-only with and without unifying differ from each other as
shown in the following context diff:
```diff
--- examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.json
+++ examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.unified.json
@@ -261,9 +261,7 @@
                         ]
                     },
                     "Provide Copyright notices In Documentation OR Distribution material": {},
-                    "Provide License text": {},
                     "Provide License text In Documentation OR Distribution material": {},
-                    "Provide Warranty disclaimer": {},
                     "Provide Warranty disclaimer In Documentation OR Distribution material": {}
                 },
                 "YOU MUST NOT": {
@@ -344,9 +342,6 @@
                 },
                 "YOU MUST": {
                     "Credit FreeType Team": {},
-                    "Forward Copyright notices": {},
-                    "Forward License text": {},
-                    "Forward Warranty disclaimer": {},
                     "Provide Copyright notices": {
                         "ATTRIBUTE": [
                             "Appropriately",
```
Please note that unifying license obligations may lead to overfulfillment of obligations of some licenses.

### Additional keys available when in merge mode
In merge mode, two additional keys may be added, if appropriate.

#### Licenses with copyleft clause
A list of names of licenses with copyleft clause, if any, will be added under
the key 'COPYLEFT LICENSES' such as:
```json
{
    "COPYLEFT LICENSES": [
        "AGPL-3.0-or-later",
        "CDDL-1.1",
        "CPL-1.0"
    ]
}
```

#### Incompatible licenses
If licenses are found that are incompatible to any of the licenses of the
current merge set, a list of them will be added under the key 'INCOMPATIBLE
LICENSES' such as:
```json
{
    "INCOMPATIBLE LICENSES": [
        "FTL",
        "BSD-4-Clause",
        "Apache-2.0"
    ]
}
```

### Some more merging examples
Based on the above example of merging the FTL with the MIT license, more
licenses are stepwise added, and the context diffs to the previous checklist are
shown. The merging steps were
* [FTL + MIT](https://github.com/osadl/OSLOC2JSON/blob/main/examples/FTL%2BMIT.json)
* [FTL + MIT + BSD-2-Clause](https://github.com/osadl/OSLOC2JSON/blob/main/examples/FTL%2BMIT%2BBSD-2-Clause.json)
* [FTL + MIT + BSD-2-Clause + BSD-3-Clause](https://github.com/osadl/OSLOC2JSON/blob/main/examples/FTL%2BMIT%2BBSD-2-Clause%2BBSD-3-Clause.json)
* [FTL + MIT + BSD-2-Clause + BSD-3-Clause + BSD-4-Clause](https://github.com/osadl/OSLOC2JSON/blob/main/examples/FTL%2BMIT%2BBSD-2-Clause%2BBSD-3-Clause%2BBSD-4-Clause.json)
* [FTL + MIT + BSD-2-Clause + BSD-3-Clause + BSD-4-Clause + Apache-2.0](https://github.com/osadl/OSLOC2JSON/blob/main/examples/FTL%2BMIT%2BBSD-2-Clause%2BBSD-3-Clause%2BBSD-4-Clause%2BApache-2.0.json)

If not for demonstation purposes, it would, of course, be sufficient to only
execute the last merge operation.

#### Added BSD-2-Clause license
```diff
--- FTL+MIT.json
+++ FTL+MIT+BSD-2-Clause.json
@@ -1,5 +1,5 @@
 {
-    "FTL|MIT": {
+    "FTL|MIT|BSD-2-Clause": {
         "COPYLEFT CLAUSE": "No",
         "PATENT HINTS": "No",
         "USE CASE": {
@@ -8,8 +8,11 @@
                     "Credit FreeType Team",
                     "Credit In Documentation FreeType Team",
                     "Provide Copyright notices",
+                    "Provide Copyright notices In Documentation OR Distribution material",
                     "Provide License text",
-                    "Provide Warranty disclaimer"
+                    "Provide License text In Documentation OR Distribution material",
+                    "Provide Warranty disclaimer",
+                    "Provide Warranty disclaimer In Documentation OR Distribution material"
                 ],
                 "YOU MUST NOT": "Promote"
             },
@@ -24,6 +27,7 @@
                     "Credit In Documentation FreeType Team",
                     "Forward Copyright notices",
                     "Forward License text",
+                    "Forward Warranty disclaimer",
                     "Provide Copyright notices",
                     "Provide License text",
                     "Provide Warranty disclaimer"
```
#### Added BSD-3-Clause license
Here, only the name of the combined license has changed, as the additional
obligations of the BSD-3 clause license "Neither the name of the copyright
holder nor the names of its contributors may be used to endorse or promote
products derived from this software" (in checklist language: "YOU MUST NOT
Promote") were already introduced in the combined input checklist by the FTL
license.
```diff
--- FTL+MIT+BSD-2-Clause.json
+++ FTL+MIT+BSD-2-Clause+BSD-3-Clause.json
@@ -1,5 +1,5 @@
 {
-    "FTL|MIT|BSD-2-Clause": {
+    "FTL|MIT|BSD-2-Clause|BSD-3-Clause": {
         "COPYLEFT CLAUSE": "No",
         "PATENT HINTS": "No",
         "USE CASE": {
```
#### Added BSD-4-Clause license
```diff
--- FTL+MIT+BSD-2-Clause+BSD-3-Clause.json
+++ FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause.json
@@ -1,9 +1,14 @@
 {
-    "FTL|MIT|BSD-2-Clause|BSD-3-Clause": {
+    "FTL|MIT|BSD-2-Clause|BSD-3-Clause|BSD-4-Clause": {
         "COPYLEFT CLAUSE": "No",
         "PATENT HINTS": "No",
         "USE CASE": {
             "Binary delivery": {
+                "IF": {
+                    "Advertisement": {
+                        "YOU MUST": "Credit In Advertisement Verbatim \"This product includes software developed by [the organization].\""
+                    }
+                },
                 "YOU MUST": [
                     "Credit FreeType Team",
                     "Credit In Documentation FreeType Team",
@@ -18,6 +23,9 @@
             },
             "Source code delivery": {
                 "IF": {
+                    "Advertisement": {
+                        "YOU MUST": "Credit In Advertisement Verbatim \"This product includes software developed by [the organization].\""
+                    },
                     "Software modification": {
                         "YOU MUST": "Provide Modification report"
                     }
```
#### Added Apache-2.0 license
```diff
--- FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause.json 2023-11-08 21:01:38.094295227 +0100
+++ FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause+Apache-2.0.json  2023-12-29 11:27:43.614566330 +0100
@@ -1,12 +1,41 @@
 {
-    "FTL|MIT|BSD-2-Clause|BSD-3-Clause|BSD-4-Clause": {
+    "FTL|MIT|BSD-2-Clause|BSD-3-Clause|BSD-4-Clause|Apache-2.0": {
         "COPYLEFT CLAUSE": "No",
-        "PATENT HINTS": "No",
+        "PATENT HINTS": [
+            "No",
+            "Yes"
+        ],
         "USE CASE": {
             "Binary delivery": {
                 "IF": {
                     "Advertisement": {
                         "YOU MUST": "Credit In Advertisement Verbatim \"This product includes software developed by [the organization].\""
+                    },
+                    "Service offerings": {
+                        "YOU MUST": "Indemnify Other contributors"
+                    },
+                    "Software modification": {
+                        "IF": {
+                            "Work Includes File \"NOTICE\"": {
+                                "EITHER": {
+                                    "1": {
+                                        "OR": {
+                                            "1": {
+                                                "YOU MUST": "Provide File \"NOTICE\" In Source code"
+                                            },
+                                            "2": {
+                                                "YOU MUST": "Provide File \"NOTICE\" In Documentation"
+                                            },
+                                            "3": {
+                                                "YOU MUST": "Display File \"NOTICE\""
+                                            }
+                                        },
+                                        "YOU MUST": "Provide File \"NOTICE\""
+                                    }
+                                },
+                                "YOU MUST": "Delete Irrelevant parts"
+                            }
+                        }
                     }
                 },
                 "YOU MUST": [
@@ -26,8 +55,39 @@
                     "Advertisement": {
                         "YOU MUST": "Credit In Advertisement Verbatim \"This product includes software developed by [the organization].\""
                     },
+                    "Service offerings": {
+                        "YOU MUST": "Indemnify Other contributors"
+                    },
                     "Software modification": {
-                        "YOU MUST": "Provide Modification report"
+                        "IF": {
+                            "Work Includes File \"NOTICE\"": {
+                                "EITHER": {
+                                    "1": {
+                                        "OR": {
+                                            "1": {
+                                                "YOU MUST": "Provide File \"NOTICE\" In Source code"
+                                            },
+                                            "2": {
+                                                "YOU MUST": "Provide File \"NOTICE\" In Documentation"
+                                            },
+                                            "3": {
+                                                "YOU MUST": "Display File \"NOTICE\""
+                                            }
+                                        },
+                                        "YOU MUST": "Provide File \"NOTICE\""
+                                    }
+                                },
+                                "YOU MUST": "Delete Irrelevant parts"
+                            }
+                        },
+                        "YOU MUST": [
+                            "Forward Attribution notices",
+                            "Forward Copyright notices",
+                            "Forward Patent notices",
+                            "Forward Trademark notices",
+                            "Provide Modification notice",
+                            "Provide Modification report"
+                        ]
                     }
                 },
                 "YOU MUST": [
```

### Merging limitations
#### Merging copyleft licenses
The more licenses are similar, the better the merging works. This is usually the
case with permissive licenses, as shown in the examples above, and with derived
or otherwise similar copyleft licenses. For example, merging the two copyleft
licenses GPL-3.0-only and AGPL-3.0-only results in a comprehensive combined
checklist, and the context diff between the GPL-3.0-only and the merged
checklist clearly shows that the additional obligation of AGPL-3.0-only is
imposed when the use of the software is offered as a network service.
```diff
--- ../unreflicenses/GPL-3.0-only-opt.json
+++ merged.json
@@ -1,5 +1,5 @@
 {
-    "GPL-3.0-only": {
+    "AGPL-3.0-only|GPL-3.0-only": {
         "COMPATIBILITY": [
             "Apache-2.0",
             "Artistic-2.0",
@@ -15,35 +15,28 @@
             "EFL-2.0",
             "FSFAP",
             "FSFULLR",
-            "GPL-1.0-or-later",
-            "GPL-2.0-or-later",
-            "GPL-3.0-or-later",
             "IBM-pibs",
             "ICU",
             "ISC",
-            "LGPL-2.1-only",
-            "LGPL-2.1-or-later",
-            "LGPL-3.0-only",
-            "LGPL-3.0-or-later",
             "Libpng",
             "MIT",
             "MPL-2.0",
             "NTP",
             "Unlicense",
             "UPL-1.0",
-            "W3C",
-            "W3C-19980720",
-            "W3C-20150513",
             "WTFPL",
             "X11",
             "Zlib",
             "ZPL-2.0"
         ],
         "COPYLEFT CLAUSE": "Yes",
+        "COPYLEFT LICENSES": [
+            "AGPL-3.0-only",
+            "GPL-3.0-only"
+        ],
         "DEPENDING COMPATIBILITY": [
             "AGPL-3.0-only",
-            "AGPL-3.0-or-later",
-            "EPL-2.0"
+            "GPL-3.0-only"
         ],
         "INCOMPATIBILITY": [
             "Apache-1.0",
@@ -164,7 +157,10 @@
                     }
                 },
                 "IF": {
-                    "Combined work With AGPL-3.0-only OR AGPL-3.0-or-later": {
+                    "AGPL-3.0-or-later": {
+                        "YOU MUST": "Fulfill License obligations Of AGPL-3.0-only OR AGPL-3.0-or-later"
+                    },
+                    "Combined work With AGPL-3.0-only": {
                         "YOU MUST": "Fulfill License obligations Of AGPL-3.0-only OR AGPL-3.0-or-later"
                     },
                     "Software modification": {
@@ -237,9 +233,27 @@
                     "Sublicense": {}
                 }
             },
+            "Network service": {
+                "IF": {
+                    "Software modification": {
+                        "YOU MUST": {
+                            "Provide Source code": {
+                                "ATTRIBUTE": [
+                                    "Customary method",
+                                    "No charges",
+                                    "Via Internet"
+                                ]
+                            }
+                        }
+                    }
+                }
+            },
             "Source code delivery": {
                 "IF": {
-                    "Combined work With AGPL-3.0-only OR AGPL-3.0-or-later": {
+                    "AGPL-3.0-or-later": {
+                        "YOU MUST": "Fulfill License obligations Of AGPL-3.0-only OR AGPL-3.0-or-later"
+                    },
+                    "Combined work With AGPL-3.0-only": {
                         "YOU MUST": "Fulfill License obligations Of AGPL-3.0-only OR AGPL-3.0-or-later"
                     },
                     "Software modification": {
```
#### License compatibility
While it makes sense to specify the cumulative incompatible licenses, the
accumulation of compatible or conditionally compatible licenses does not provide
a meaningful result. Instead, all previously compatible licenses must be removed
from the list when a newly merged license does not feature a given
compatibility. This was already shown in the above example when the GPL-3.0-only
license was merged with the AGPL-3.0-only license and all compatibilities that
were not available in both of them were removed. In addition, it should be noted
that much more needs to be taken into account when considering the compatibility
of licenses and especially copyleft licenses. In this respect, the information
on compatibility resulting from the merging of the checklists is only a very
first indication, so that individual legal advice must always be obtained, which
of course also applies to all other information in the checklists.

## Schema
The validate function (-j) uses the below JSON schema. This version 2 of the
schema is used by default for the conversion in either direction and for
validation. The deprecated first version of the schema is still supported, but
requires that the command line option "-1" is specified. Version 1 did not
correctly treat the EITHER IF/OR IF block and failed when another block
occurred at the same indent level.
```json
{
    "$schema": "http://json-schema.org/draft-06/schema#",

    "copyrightclause": {
        "type": "string",
        "enum": ["Yes", "No", "Questionable"]
    },

    "patenthints": {
        "type": "string",
        "enum": ["Yes", "No"]
    },

    "obligations": {
        "patternProperties": {
            "^EITHER$": {
                "patternProperties": {
                    "^[0-9]*$": {
                        "required": ["OR"],
                        "not": {
                           "required": ["OR IF"]
                        },
                        "property": {
                           "$ref": "#/obligations"
                        }
                    }
                },
                "additionalProperties": false
            },
            "^OR$": {
                "patternProperties": {
                    "^[0-9]*$": {
                        "$ref": "#/obligations"
                    }
                },
                "additionalProperties": false
            },
            "^EITHER IF$": {
                "patternProperties": {
                    "^[0-9]*$": {
                        "patternProperties": {
                            ".*": {
                               "required": ["OR IF"],
                               "not": {
                                   "required": ["OR"]
                               },
                               "property": {
                                   "$ref": "#/obligations"
                               }
                            }
                        },
                        "additionalProperties": false
                    }
                }
            },
            "^OR IF$": {
                "patternProperties": {
                    "^[0-9]*$": {
                        "patternProperties": {
                            ".*": {
                                "$ref": "#/obligations"
                            }
                        },
                        "additionalProperties": false
                    }
                }
            },
            "^(ATTRIBUTE|EXCEPT IF|IF|YOU MUST|YOU MUST NOT)$": {
                "patternProperties": {
                    ".*": {
                        "$ref": "#/obligations"
                    }
                },
                "additionalProperties": false
            }
        },
        "additionalProperties": false
    },

    "license": {
        "type": "object",
        "patternProperties": {
            "^[0-9A-Za-z\\.| -]*$": {
                "required": ["USE CASE"],
                "type": "object",
                "properties": {
                    "USE CASE": {
                        "type": ["string", "object"],
                        "patternProperties": {
                            "^.* ([Dd]elivery|service).*$": {
                                "$ref": "#/obligations"
                            }
                        },
                        "additionalProperties": false
                    },
                    "COMPATIBILITY": {
                        "type": ["string", "array"]
                    },
                    "DEPENDING COMPATIBILITY": {
                        "type": ["string", "array"]
                    },
                    "INCOMPATIBILITY": {
                        "type": ["string", "array"]
                    },
                    "INCOMPATIBLE LICENSES": {
                        "type": ["string", "array"]
                    },
                    "COPYLEFT LICENSES": {
                        "type": ["string", "array"]
                    },
                    "COPYLEFT CLAUSE": {
                        "oneOf": [{
                            "type": "string",
                            "$ref": "#/copyrightclause"
                        },{
                            "type": "array",
                            "items": {
                                "$ref": "#/copyrightclause"
                            }
                        }]
                    },
                    "PATENT HINTS": {
                        "oneOf": [{
                            "type": "string",
                            "$ref": "#/patenthints"
                        },{
                            "type": "array",
                            "items": {
                                "$ref": "#/patenthints"
                            }
                        }]
                    }
                },
            "additionalProperties": false
            }
        },
        "additionalProperties": false
    },

    "type": "object",
    "$ref": "#/license"
}
```
