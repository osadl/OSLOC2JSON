#!/bin/bash

./src/osloc2json.py -demo examples/FTL.txt examples/MIT.txt
if cmp examples/FTL+MIT.json merged.json
then
  echo Pass
else
  echo Fail
fi
rm -f merged.json
