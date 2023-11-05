# OSLOC2JSON

## Purpose
Convert Open Source License Obligations Checklist to JSON format

## Command line options
```bash
osloc2json.py --help
```
```
usage: osloc2json.py [-h] [-f [OUTPUT]] [-e] [-m] [-o] [-r] [-s] [-v] OSLOC [OSLOC ...]

positional arguments:
  OSLOC                 file names of OSLOC files to process

options:
  -h, --help            show this help message and exit
  -f [OUTPUT], --filename [OUTPUT]
                        name of output file for multiple licenses, has no effect if single license, default "osloc.json"
  -e, --expand          replace keys connected by OR with the individual keys and assign the value of the key to all of them
  -m, --merge           merge all licenses into a single one, has no effect if single license, default file name "merged.json"
  -o, --optimize        convert a dict with no values to a list of keys or string, if only one, add "-opt" to output file name
  -r, --recreate        recreate original checklist from JSON (for debugging)
  -s, --show            also list the output to screen
  -v, --verbose         show names and texts the program is using

Either a single OSLOC file is parsed, converted to JSON format and saved under the original name with the suffix ".json", or
all OSLOC files are parsed, concatenated to a single JSON object and stored under "osloc.json" or OUTPUT if specified, or
(-m) all OSLOC files are parsed, merged into a single JSON object (lists concatenated, duplicates removed) and stored under "merged.json" or OUTPUT if specified
```

## Disclaimer
This is a software tool, no legal advice.

## Examples how to use the software

### Convert an OSLOC file to JSON format
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
--- ../OSLOC/unreflicenses/FTL.json 2023-11-04 02:34:06.978179221 +0100
+++ ../OSLOC/unreflicenses/FTL-opt.json 2023-11-04 02:34:15.882344590 +0100
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

### Merging
Two or more OSLOC files may be merged in such a way that additional license
obligations of the same conditions are concatenated and duplicates are removed.
By default, the resulting merged checklist will be written to a file named
"merged.json", but can be specified using the -f option. Here also, the -o
option can be used.

#### Extending OR-linked conditions
Conditions that contain multiple OR-linked subconditions may optionally split
into independent individual conditions, which can then be subsumed with the
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
This can be further illustrated in the context diff between the original FTL and
the FTL/MIT merged checklist:
```diff
--- ../OSLOC/unreflicenses/FTL-opt.json 2023-11-04 00:55:05.376730567 +0100
+++ merged.json 2023-11-04 00:50:35.531616943 +0100
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
which would be rather meaningless.

### Some more merging examples
Based on the above example of merging the FTL with the MIT license, more
licenses are stepwise added, and the context diffs to the previous checklist are
shown. The merging steps were
* FTL + MIT
* FTL + MIT + BSD-2-Clause
* FTL + MIT + BSD-2-Clause + BSD-3-Clause
* FTL + MIT + BSD-2-Clause + BSD-3-Clause + BSD-4-Clause
* FTL + MIT + BSD-2-Clause + BSD-3-Clause + BSD-4-Clause + Apache-2.0

#### Added BSD-2-Clause license
```diff
--- FTL+MIT.json  2023-11-05 11:54:33.259803561 +0100
+++ FTL+MIT+BSD-2-Clause.json 2023-11-05 11:54:56.564226921 +0100
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
--- FTL+MIT+BSD-2-Clause.json 2023-11-05 11:54:56.564226921 +0100
+++ FTL+MIT+BSD-2-Clause+BSD-3-Clause.json  2023-11-05 11:55:14.225547767 +0100
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
--- FTL+MIT+BSD-2-Clause+BSD-3-Clause.json  2023-11-05 11:55:14.225547767 +0100
+++ FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause.json 2023-11-05 11:55:30.927851180 +0100
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
--- FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause.json	2023-11-05 11:55:30.927851180 +0100
+++ FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause+Apache-2.0.json	2023-11-05 19:07:21.877218819 +0100
@@ -1,12 +1,35 @@
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
@@ -26,8 +49,33 @@
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
