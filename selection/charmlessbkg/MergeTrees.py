import ROOT as rt
from ROOT import TFile

import time
import argparse
import yaml

def MergeTrees(input_files, output_file):
    #sideband_region = ["ss", "sb", "bs", "bb"]
    f = {}
    tr= {}
    for name in input_files:
        k = name.split('.')[-2].split('_')[-1]
        f[k] = TFile(name, "r")
        tr[k] = f[k].Get("tr_"+k)
    f_out = TFile(output_file, "recreate")
    for k in tr.keys():
        tr[k].Write()
        f[k].Close()
    f_out.Close()
    print("Combined file for " + ''.join(input_files)+" saved!")
    
        


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files', nargs='+',
                        help='Path to the input file')
    parser.add_argument('--output-file', 
                        help='Path to the output file')
    args = parser.parse_args()
    
    MergeTrees(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
