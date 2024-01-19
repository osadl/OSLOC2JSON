#!/bin/bash

./src/osloc2json.py -emo examples/FTL.txt examples/MIT.txt
if ! cmp examples/FTL+MIT.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/FTL.txt examples/MIT.txt examples/BSD-2-Clause.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/FTL.txt examples/MIT.txt examples/BSD-[23]-Clause.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/FTL.txt examples/MIT.txt examples/BSD-[2-4]-Clause.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/FTL.txt examples/MIT.txt examples/BSD-[2-4]-Clause.txt examples/Apache-2.0.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+BSD-4-Clause+Apache-2.0.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/FTL.txt examples/MIT.txt examples/BSD-[2-3]-Clause.txt examples/Apache-2.0.txt examples/GPL-3.0-only.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/EPL-2.0.txt examples/MPL-2.0.txt
if ! cmp examples/EPL-2.0+MPL-2.0.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emo examples/GPL-3.0-only.txt examples/AGPL-3.0-only.txt
if ! cmp examples/GPL-3.0-only+AGPL-3.0-only.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emou examples/FTL.txt examples/MIT.txt examples/BSD-[2-3]-Clause.txt examples/Apache-2.0.txt examples/GPL-3.0-only.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.unified.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emou examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.unified.json
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.unified.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emur examples/GPL-2.0-only.txt examples/Unlicense.txt >merged.checklist
if ! cmp examples/GPL-2.0-only+Unlicense.json merged.json || ! cmp examples/GPL-2.0-only+Unlicense.unified.checklist merged.checklist
then
  exit 1
fi

./src/osloc2json.py -emur examples/0BSD.txt examples/GPL-2.0-only.txt examples/Unlicense.txt examples/WTFPL.txt >merged.checklist
if ! cmp examples/0BSD+GPL-2.0-only+Unlicense+WTFPL.json merged.json || ! cmp examples/0BSD+GPL-2.0-only+Unlicense+WTFPL.unified.checklist merged.checklist
then
  exit 1
fi

./src/osloc2json.py -emur examples/EPL-2.0.txt examples/GPL-2.0-only.txt examples/MPL-2.0.txt >merged.checklist
if ! cmp examples/EPL-2.0+GPL-2.0-only+MPL-2.0.unified.json merged.json || ! cmp examples/EPL-2.0+GPL-2.0-only+MPL-2.0.unified.checklist merged.checklist
then
  exit 1
fi

./src/osloc2json.py -emur examples/Apache-2.0.txt examples/EPL-2.0.txt examples/GPL-3.0-only.txt examples/MPL-2.0.txt >merged.checklist
if ! cmp examples/Apache-2.0+EPL-2.0+GPL-3.0-only+MPL-2.0.unified.json merged.json || ! cmp examples/Apache-2.0+EPL-2.0+GPL-3.0-only+MPL-2.0.unified.checklist merged.checklist
then
  exit 1
fi

./src/osloc2json.py -elmur examples/Apache-2.0.txt examples/GPL-2.0-or-later.txt >merged.checklist
if ! cmp examples/Apache-2.0+GPL-3.0-or-later.unified.json merged.json || ! cmp examples/Apache-2.0+GPL-3.0-or-later.unified.checklist merged.checklist
then
  exit 1
fi

cp examples/FTL.json examples/FTL-old.json
mkdir -p examples/newexamples
./src/osloc2json.py -r examples/FTL.json >examples/newexamples/FTL.txt
./src/osloc2json.py examples/newexamples/FTL.txt
if ! cmp examples/newexamples/FTL.json examples/FTL-old.json
then
  exit 1
fi
mv -f examples/FTL-old.json examples/FTL.json
rm -Rf examples/newexamples

./src/osloc2json.py -emo examples/FTL.json examples/MIT.txt examples/BSD-[2-3]-Clause.txt examples/Apache-2.0.txt examples/GPL-3.0-only.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.json merged.json
then
  exit 1
fi

./src/osloc2json.py -jn examples/*.json >examples/jsonvalidity
if test -s examples/jsonvalidity
then
  echo JSON validity checker erroneously detected invalid JSON
  cat examples/jsonvalidity
  exit 1
fi
rm -f examples/jsonvalidity

rm -f merged.json *.checklist

exit 0
