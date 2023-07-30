# OSLOC2JSON

## Purpose
Convert Open Source License Obligations Checklist to JSON format

## Command line options
```bash
osloc2json.py --help
```
```
usage: osloc2json.py [-h] [-v] OSLOC

positional arguments:
  OSLOC          file name of an OSLOC file to process

options:
  -h, --help     show this help message and exit
  -v, --verbose  show names and texts the program is using

Parse OSLOC file, convert it to JSON format and store it under the original name suffixed by ".json"
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
