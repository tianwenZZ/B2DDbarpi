import time
import argparse
import yaml
import os

import ROOT
from ROOT import TMVA, TFile
from array import array

from utilities import get_val


def read_from_yaml(mode, selection_files):
    selection_dict = dict()
    for file in selection_files:
        with open(file, 'r') as stream:
            selection_dict.update(yaml.safe_load(stream)[mode])
    return selection_dict


def apply(input_files, input_tree_name, input_ds,
          output_file, output_tree_name,
          method_config, mode, mva_vars):
    # Default MVA methods to be trained + tested
    ROOT.EnableImplicitMT()
    Use = read_from_yaml("MVAmethods", method_config)
    for key in Use.keys():
        if Use[key]:
            print(f"-----> Method {key} is booked in MVA <-----")
    methods = [m for m in Use.keys() if Use[m]]
    # Default vars to be trained + tested
    vars = read_from_yaml(mode, mva_vars)

    input_file = TFile(input_files)
    input_tree = input_file.Get(input_tree_name)

    TMVA.Tools.Instance()
    reader = TMVA.Reader("!Color:!Silent")

    # Create and declare to reader variables, MUST same orders names and types as weights
    f_arrays = {}
    for v in vars.keys():
        f_arrays[v] = array('f', [0.])
        reader.AddVariable(vars[v], f_arrays[v])

    # --- Book the MVA methods
    for methodName in methods:
        weightfile = input_ds + "/weights/TMVAClassification_" + methodName + ".weights.xml"
        reader.BookMVA(methodName, weightfile)

    output_file = TFile(output_file, "recreate")
    output_tree = input_tree.CloneTree(0)

    responses = {}
    for methodName in methods:
        responses[methodName] = array('d', [0.])
        output_tree.Branch(methodName, responses[methodName], methodName+"/D")

    nentries = input_tree.GetEntries()
    print("Total event number to be applied: ", nentries)
    for ievt in range(nentries):
        input_tree.GetEntry(ievt)
        for v in vars.keys():
            f_arrays[v][0] = get_val(input_tree, vars[v])
        for methodName in methods:
            responses[methodName][0] = reader.EvaluateMVA(methodName)
        output_tree.Fill()
        if ievt%1000==0: print(f"{ievt} events are finished.")

    print("==> TMVAClassificationApplication is done!")
    output_tree.AutoSave()
    output_file.Close()
    input_file.Close()


if __name__ == "__main__":
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree', help='Name of the tree of file')
    parser.add_argument('--input-ds', help='Input dataset directory')
    parser.add_argument('--output-file', help='Output ROOT file')
    parser.add_argument('--output-tree-name', default='DecayTree',
                        help='Tree name of output ROOT file')
    parser.add_argument('--method-config', nargs='+',
                        help='Yaml files of training methods and their configuration')
    parser.add_argument('--mode', help='Name of the decay modes to be trained')
    parser.add_argument('--mva-vars', default='', nargs='+',
                        help='Yaml files of training variables and their possible cuts')
    args = parser.parse_args()

    apply(**vars(args))

    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
