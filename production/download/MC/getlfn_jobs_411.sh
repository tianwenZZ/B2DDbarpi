#/bin/bash

mkdir 411
cd 411

if [ -f Tuple_1.root ]; then
   echo "subjob 1 existed. skip..."
else
   echo "Downloading subjob 1 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2024_04/872145/872145931/Tuple.root
   mv Tuple.root Tuple_1.root
fi
