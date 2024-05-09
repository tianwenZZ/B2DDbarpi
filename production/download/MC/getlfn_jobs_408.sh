#/bin/bash

mkdir 408
cd 408

if [ -f Tuple_1.root ]; then
   echo "subjob 1 existed. skip..."
else
   echo "Downloading subjob 1 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2024_04/872145/872145060/Tuple.root
   mv Tuple.root Tuple_1.root
fi
