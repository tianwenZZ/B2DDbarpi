#/bin/bash

mkdir 375
cd 375

if [ -f Tuple_0.root ]; then
   echo "subjob 0 existed. skip..."
else
   echo "Downloading subjob 0 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918590/Tuple.root
   mv Tuple.root Tuple_0.root
fi
if [ -f Tuple_1.root ]; then
   echo "subjob 1 existed. skip..."
else
   echo "Downloading subjob 1 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918591/Tuple.root
   mv Tuple.root Tuple_1.root
fi
if [ -f Tuple_2.root ]; then
   echo "subjob 2 existed. skip..."
else
   echo "Downloading subjob 2 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918592/Tuple.root
   mv Tuple.root Tuple_2.root
fi
if [ -f Tuple_3.root ]; then
   echo "subjob 3 existed. skip..."
else
   echo "Downloading subjob 3 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918593/Tuple.root
   mv Tuple.root Tuple_3.root
fi
if [ -f Tuple_4.root ]; then
   echo "subjob 4 existed. skip..."
else
   echo "Downloading subjob 4 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918594/Tuple.root
   mv Tuple.root Tuple_4.root
fi
if [ -f Tuple_5.root ]; then
   echo "subjob 5 existed. skip..."
else
   echo "Downloading subjob 5 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918595/Tuple.root
   mv Tuple.root Tuple_5.root
fi
if [ -f Tuple_6.root ]; then
   echo "subjob 6 existed. skip..."
else
   echo "Downloading subjob 6 ..."
   lb-dirac dirac-dms-get-file /lhcb/user/t/tzhou/2023_12/828918/828918596/Tuple.root
   mv Tuple.root Tuple_6.root
fi
