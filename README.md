# OSLOC2JSON

## Purpose
Convert Open Source License Obligations Checklist to JSON format

## Command line options
```bash
osloc2json.py --help
```
```
usage: osloc2json.py [-h] [-f [OUTPUT]] [-m] [-o] [-r] [-s] [-v] OSLOC [OSLOC ...]

positional arguments:
  OSLOC                 file names of OSLOC files to process

options:
  -h, --help            show this help message and exit
  -f [OUTPUT], --filename [OUTPUT]
                        name of output file for multiple licenses, has no effect if single license, default "osloc.json"
  -m, --merge           merge all licenses into a single one, has no effect if single license, default file name "merged.json"
  -o, --optimize        convert a dict with no values to a list of keys, add "-opt" to output file name
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
into a list of keys. This is done when the "--optimize" flag is selected. Thus,
after running
```bash
osloc2json.py -o FTL.txt
```
the following optimized output is available in the file "FTL-opt.json":
```json
{
    "FTL": {
        "USE CASE": {
            "Source code delivery": {
                "YOU MUST": [
                    "Forward License text",
                    "Forward Copyright notices",
                    "Credit FreeType Team"
                ],
                "YOU MUST NOT": [
                    "Modify License text",
                    "Promote"
                ],
                "IF": {
                    "Software modification": {
                        "YOU MUST": [
                            "Provide Modification report"
                        ]
                    }
                }
            },
            "Binary delivery": {
                "YOU MUST": [
                    "Credit In Documentation FreeType Team",
                    "Credit FreeType Team"
                ],
                "YOU MUST NOT": [
                    "Promote"
                ]
            }
        }
    }
}
```
As can be seen in this diff
```diff
--- ../OSLOC/unreflicenses/FTL.json 2023-07-31 22:10:36.065513054 +0200
+++ ../OSLOC/unreflicenses/FTL-opt.json 2023-07-31 22:15:33.383434885 +0200
@@ -2,31 +2,31 @@
     "FTL": {
         "USE CASE": {
             "Source code delivery": {
-                "YOU MUST": {
-                    "Forward License text": {},
-                    "Forward Copyright notices": {},
-                    "Credit FreeType Team": {}
-                },
-                "YOU MUST NOT": {
-                    "Modify License text": {},
-                    "Promote": {}
-                },
+                "YOU MUST": [
+                    "Forward License text",
+                    "Forward Copyright notices",
+                    "Credit FreeType Team"
+                ],
+                "YOU MUST NOT": [
+                    "Modify License text",
+                    "Promote"
+                ],
                 "IF": {
                     "Software modification": {
-                        "YOU MUST": {
-                            "Provide Modification report": {}
-                        }
+                        "YOU MUST": [
+                            "Provide Modification report"
+                        ]
                     }
                 }
             },
             "Binary delivery": {
-                "YOU MUST": {
-                    "Credit In Documentation FreeType Team": {},
-                    "Credit FreeType Team": {}
-                },
-                "YOU MUST NOT": {
-                    "Promote": {}
-                }
+                "YOU MUST": [
+                    "Credit In Documentation FreeType Team",
+                    "Credit FreeType Team"
+                ],
+                "YOU MUST NOT": [
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
