#!/bin/bash
# Setup the RAPIDSIM_ROOT environment variable (or add to .bashrc)
# set up lhcb environment
source /cvmfs/lhcb.cern.ch/lib/lcg/releases/LCG_87/gcc/4.9.3/x86_64-slc6/setup.sh
# Set ROOT environment
source /cvmfs/lhcb.cern.ch/lib/lcg/releases/LCG_87/ROOT/6.08.02/x86_64-slc6-gcc49-opt/bin/thisroot.sh

export RAPIDSIM_ROOT='/home/zhoutw/workdir/RapidSim'
export RAPIDSIM_CONFIG='/home/zhoutw/workdir/B2DDbarpi/snakemake_chain/selection/misID'
$RAPIDSIM_ROOT/build/src/RapidSim.exe $RAPIDSIM_CONFIG/validation/$1 $2 1

