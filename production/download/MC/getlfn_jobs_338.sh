#/bin/bash

mkdir 338
cd 338

if [ -f Tuple_0.root ]; then
   echo "subjob 0 existed. skip..."
else
   echo "Downloading subjob 0 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828894/828894504/Tuple.root
   mv Tuple.root Tuple_0.root
fi
if [ -f Tuple_1.root ]; then
   echo "subjob 1 existed. skip..."
else
   echo "Downloading subjob 1 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828894/828894507/Tuple.root
   mv Tuple.root Tuple_1.root
fi
if [ -f Tuple_2.root ]; then
   echo "subjob 2 existed. skip..."
else
   echo "Downloading subjob 2 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828894/828894509/Tuple.root
   mv Tuple.root Tuple_2.root
fi
if [ -f Tuple_3.root ]; then
   echo "subjob 3 existed. skip..."
else
   echo "Downloading subjob 3 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828894/828894512/Tuple.root
   mv Tuple.root Tuple_3.root
fi
if [ -f Tuple_4.root ]; then
   echo "subjob 4 existed. skip..."
else
   echo "Downloading subjob 4 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828894/828894514/Tuple.root
   mv Tuple.root Tuple_4.root
fi
if [ -f Tuple_5.root ]; then
   echo "subjob 5 existed. skip..."
else
   echo "Downloading subjob 5 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828894/828894516/Tuple.root
   mv Tuple.root Tuple_5.root
fi
