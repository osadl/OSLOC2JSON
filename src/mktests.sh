#!/bin/bash

./src/osloc2json.py examples/Apache-2.0.txt examples/GPL-3.0-or-later.txt
if ! cmp examples/Apache-2.0+GPL-3.0-or-later-concatenated.json osloc.json
then
  exit 1
fi

cd examples
../src/osloc2json.py Apache-2.0+GPL-3.0-or-later
if ! cmp Apache-2.0+GPL-3.0-or-later-concatenated.json osloc.json
then
  exit 1
fi
rm -f osloc.json

../src/osloc2json.py -m Apache-2.0+GPL-3.0-or-later
if ! cmp Apache-2.0+GPL-3.0-or-later.json merged.json
then
  exit 1
fi
rm -f merged.json

cd - >/dev/null

./src/osloc2json.py -m examples/CHECKLIST-2.0.txt examples/CHECKLIST-2.0.txt
if ! cmp examples/CHECKLIST-2.0.json merged.json
then
  exit 1
fi

./src/osloc2json.py -mo examples/CHECKLIST-2.0.txt examples/CHECKLIST-2.0.txt
if ! cmp examples/CHECKLIST-2.0-opt.json merged.json
then
  exit 1
fi

./src/osloc2json.py -m examples/CHECKLIST-2.0.txt examples/CHECKLIST-3.0.txt
if ! cmp examples/CHECKLIST-2.0+CHECKLIST-3.0.json merged.json
then
  exit 1
fi

./src/osloc2json.py -m examples/CHECKLIST-2.0.txt examples/CHECKLIST-4.0.txt
if ! cmp examples/CHECKLIST-2.0+CHECKLIST-4.0.json merged.json
then
  exit 1
fi

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

./src/osloc2json.py -emol examples/EPL-2.0.txt examples/MPL-1.1.txt
if ! cmp examples/EPL-2.0+MPL-2.0.json merged.json
then
  exit 1
fi

./src/osloc2json.py -emor examples/GPL-3.0-only.txt examples/AGPL-3.0-only.txt >merged.checklist
if ! cmp examples/GPL-3.0-only+AGPL-3.0-only.json merged.json || ! cmp examples/GPL-3.0-only+AGPL-3.0-only.checklist merged.checklist
then
  diff -u examples/GPL-3.0-only+AGPL-3.0-only.checklist merged.checklist
  exit 1
fi

./src/osloc2json.py -emor examples/GPL-3.0-only.txt examples/LGPL-3.0-only.txt >merged.checklist
if ! cmp examples/GPL-3.0-only+LGPL-3.0-only.json merged.json || ! cmp examples/GPL-3.0-only+LGPL-3.0-only.checklist merged.checklist
then
  diff -u examples/GPL-3.0-only+LGPL-3.0-only.checklist merged.checklist
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
  diff -u examples/EPL-2.0+GPL-2.0-only+MPL-2.0.unified.checklist merged.checklist
  exit 1
fi

./src/osloc2json.py -emur examples/Apache-2.0.txt examples/EPL-2.0.txt examples/GPL-3.0-only.txt examples/MPL-2.0.txt >merged.checklist
if ! cmp examples/Apache-2.0+EPL-2.0+GPL-3.0-only+MPL-2.0.unified.json merged.json || ! cmp examples/Apache-2.0+EPL-2.0+GPL-3.0-only+MPL-2.0.unified.checklist merged.checklist
then
  exit 1
fi

#./src/osloc2json.py -emor examples/GPL-3.0-or-later.txt examples/Minpack.txt >merged.checklist
#if ! cmp examples/GPL-3.0-or-later+Minpack.checklist merged.checklist
#then
#  diff -u examples/GPL-3.0-or-later+Minpack.checklist merged.checklist
#  exit 1
#fi

./src/osloc2json.py -elmur examples/Apache-2.0.txt examples/GPL-2.0-or-later.txt >merged.checklist
if ! cmp examples/Apache-2.0+GPL-2.0-or-later.upgraded.unified.json merged.json || ! cmp examples/Apache-3.0+GPL-2.0-or-later.upgraded.unified.checklist merged.checklist
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

./src/osloc2json.py examples/GPL-3.0-only.txt
mkdir -p examples/newexamples
./src/osloc2json.py -r examples/GPL-3.0-only.json >examples/newexamples/GPL-3.0-only.txt
./src/osloc2json.py examples/newexamples/GPL-3.0-only.txt
if ! cmp examples/newexamples/GPL-3.0-only.json examples/GPL-3.0-only.json
then
  exit 1
fi
rm -f examples/GPL-3.0-only.json
rm -Rf examples/newexamples

./src/osloc2json.py examples/Artistic-2.0.txt
mkdir -p examples/newexamples
./src/osloc2json.py -r examples/Artistic-2.0.json >examples/newexamples/Artistic-2.0.txt
./src/osloc2json.py examples/newexamples/Artistic-2.0.txt
if ! cmp examples/newexamples/Artistic-2.0.json examples/Artistic-2.0.json
then
  exit 1
fi
rm -f examples/Artistic-2.0.json
rm -Rf examples/newexamples

./src/osloc2json.py examples/Apache-2.0.txt
mkdir -p examples/newexamples
./src/osloc2json.py -r examples/Apache-2.0.json >examples/newexamples/Apache-2.0.txt
./src/osloc2json.py examples/newexamples/Apache-2.0.txt
if ! cmp examples/newexamples/Apache-2.0.json examples/Apache-2.0.json
then
  exit 1
fi
rm -f examples/Apache-2.0.json
rm -Rf examples/newexamples

./src/osloc2json.py -emo examples/FTL.json examples/MIT.txt examples/BSD-[2-3]-Clause.txt examples/Apache-2.0.txt examples/GPL-3.0-only.txt
if ! cmp examples/FTL+MIT+BSD-2-Clause+BSD-3-Clause+Apache-2.0+GPL-3.0-only.json merged.json
then
  exit 1
fi

for i in `ls -1 examples/*.json | grep -v concatenated`
do
  ./src/osloc2json.py -jn $i >examples/jsonvalidity
  if test -s examples/jsonvalidity
  then
    echo JSON validity checker erroneously detected invalid JSON
    cat examples/jsonvalidity
    exit 1
  fi
done
rm -f examples/jsonvalidity

rm -f osloc.json merged.json *.checklist

echo All tests passed

exit 0
