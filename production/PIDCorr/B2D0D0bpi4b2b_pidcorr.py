###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import print_function

import os
import sys
import time
import argparse
import yaml


def main(input_file, output_file):
    ## START OF CONFIG
    # Read comments and check vars
    # at least until end of config section

    # List of input ROOT files with MC ntuples. Format:
    #   (inputfile, outputfile, dataset)
    y = input_file.split('/')[-1].split('.')[0].split('_')[1]
    mag = input_file.split('/')[-1].split('.')[0].split('_')[2]
    if mag=="mu": ds="MagUp_"+y
    if mag=="md": ds="MagDown_"+y

    files = [(input_file, output_file, ds)]


    # Name of the input tree
    # Could also include ROOT directory, e.g. "Dir/Ntuple"
    input_tree = "B2D0D0Pi2b4b/DecayTree"

    simversion = "run2"

    # Postfixes of the Pt, Eta and Ntracks variables (ntuple variable name w/o branch name)
    # e.g. if the ntuple contains "pion_PT", it should be just "PT"
    ptvar = "PT"
    #etavar = "eta"
    #pvar = None
    ## Could use P variable instead of eta
    etavar = None
    pvar   = "P"

    ntrvar = "nTracks"  # This should correspond to the number of "Best tracks", not "Long tracks"!

    # Dictionary of tracks with their PID variables, in the form {branch name}:{pidvars}
    # For each track branch name, {pidvars} is a dictionary in the form {ntuple variable}:{pid config},
    #   where
    #     {ntuple variable} is the name of the corresponding ntuple PID variable without branch name,
    #   and
    #     {pid_config} is the string describing the PID configuration.
    # Run PIDCorr.py without arguments to get the full list of PID configs
    tracks = {
        'D2bK': {
            "ProbNNk": "K_MC15TuneV1_ProbNNK_Brunel_Mod2",
            "ProbNNpi": "K_MC15TuneV1_ProbNNpi_Brunel",
            "ProbNNp": "K_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "K_CombDLLK_Brunel",
            "PIDp": "K_CombDLLp_Brunel",
        },
        'D2bH':{
            "ProbNNk": "pi_MC15TuneV1_ProbNNK_Brunel",
            "ProbNNpi": "pi_MC15TuneV1_ProbNNpi_Brunel_Mod2",
            "ProbNNp": "pi_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "pi_CombDLLK_Brunel",
            "PIDp": "pi_CombDLLp_Brunel",
        },
        'D4bK': {
            "ProbNNk": "K_MC15TuneV1_ProbNNK_Brunel_Mod2",
            "ProbNNpi": "K_MC15TuneV1_ProbNNpi_Brunel",
            "ProbNNp": "K_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "K_CombDLLK_Brunel",
            "PIDp": "K_CombDLLp_Brunel",
        },
        'D4bHp':{
            "ProbNNk": "pi_MC15TuneV1_ProbNNK_Brunel",
            "ProbNNpi": "pi_MC15TuneV1_ProbNNpi_Brunel_Mod2",
            "ProbNNp": "pi_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "pi_CombDLLK_Brunel",
            "PIDp": "pi_CombDLLp_Brunel",
        },
        'D4bHm1':{
            "ProbNNk": "pi_MC15TuneV1_ProbNNK_Brunel",
            "ProbNNpi": "pi_MC15TuneV1_ProbNNpi_Brunel_Mod2",
            "ProbNNp": "pi_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "pi_CombDLLK_Brunel",
            "PIDp": "pi_CombDLLp_Brunel",
        },
        'D4bHm2':{
            "ProbNNk": "pi_MC15TuneV1_ProbNNK_Brunel",
            "ProbNNpi": "pi_MC15TuneV1_ProbNNpi_Brunel_Mod2",
            "ProbNNp": "pi_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "pi_CombDLLK_Brunel",
            "PIDp": "pi_CombDLLp_Brunel",
        },

        'BH':{
            "ProbNNk": "pi_MC15TuneV1_ProbNNK_Brunel",
            "ProbNNpi": "pi_MC15TuneV1_ProbNNpi_Brunel_Mod2",
            "ProbNNp": "pi_MC15TuneV1_ProbNNp_Brunel",
            "PIDK": "pi_CombDLLK_Brunel",
            "PIDp": "pi_CombDLLp_Brunel",

        },
            
    }

    # IF ON LXPLUS: if /tmp exists and is accessible, use for faster processing
    # IF NOT: use /tmp if you have enough RAM
    # temp_folder = '/tmp'
    # ELSE: use current folder
    temp_folder = '.'

    ## END OF CONFIG

    # make sure we don't overwrite local files and prefix them with random strings
    import string
    import random
    rand_string = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(10))  # get 10 random chars for temp_file prefix

    temp_file_prefix = temp_folder + '/' + rand_string  # prefix temp files with folder and unique ID

    output_tree = input_tree.split("/")[-1]

    for input_file, output_file, dataset in files:
        treename = input_tree
        tmpinfile = input_file
        tmpoutfile = "%s_tmp1.root" % temp_file_prefix
        for track, subst in tracks.items():
            for var, config in subst.items():
                command = "python $PIDPERFSCRIPTSROOT/scripts/python/PIDGenUser/PIDCorr.py"
                command += " -m %s_%s" % (track, ptvar)
                if etavar:
                    command += " -e %s_%s" % (track, etavar)
                elif pvar:
                    command += " -q %s_%s" % (track, pvar)
                else:
                    print('Specify either ETA or P branch name per track')
                    sys.exit(1)
                command += " -n %s" % ntrvar
                command += " -t %s" % treename
                command += " -p %s_%s_corr" % (track, var)
                command += " -s %s_%s" % (track, var)
                command += " -c %s" % config
                command += " -d %s" % dataset
                command += " -i %s" % tmpinfile
                command += " -o %s" % tmpoutfile
                command += " -S %s" % simversion
                command += " --outtree %s" % output_tree

                treename = output_tree
                tmpinfile = tmpoutfile
                if 'tmp1' in tmpoutfile:
                    tmpoutfile = tmpoutfile.replace('tmp1', 'tmp2')
                else:
                    tmpoutfile = tmpoutfile.replace('tmp2', 'tmp1')

                print(command)
                os.system(command)

        if "root://" in output_file:
            print("xrdcp %s %s" % (tmpinfile, output_file))
            os.system("xrdcp %s %s" % (tmpinfile, output_file))
        else:
            print("mv %s %s" % (tmpinfile, output_file))
            os.system("mv %s %s" % (tmpinfile, output_file))

if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file',
                        help='Path to the input file')
    parser.add_argument('--output-file',
                        help='Path to the output file')
    args = parser.parse_args()
    main(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
