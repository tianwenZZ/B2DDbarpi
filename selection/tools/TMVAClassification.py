import time
import argparse
import yaml
import os
from ConfigureEachMethod import ConfigureEachMethod

import ROOT
from ROOT import TFile, TChain, TCut, gROOT, RDataFrame, vector, TCut
from ROOT import TMVA

def read_from_yaml(mode, selection_files):
    selection_dict = dict()
    for file in selection_files:
        with open(file, 'r') as stream:
            selection_dict.update(yaml.safe_load(stream)[mode])
    return selection_dict

def load_data(treename, files):
    names = []
    for n in files:
        names.append(n if n.endswith('.root') else n+'*.root')
    tree = TChain(treename)
    for n in names:
        tree.Add(n)
    return tree

def train(input_files_mc, input_tree_name_mc, input_files_bkg, input_tree_name_bkg,
                       output_file, output_ds,
                       method_config, mode, mva_vars, selection_files):

    #ROOT.EnableImplicitMT()
    # Default MVA methods to be trained + tested
    Use = read_from_yaml("MVAmethods", method_config)
    for key in Use.keys():
        if Use[key]:
            print(f"-----> Method {key} is booked for MVA <-----")
    
    # Default vars to be trained + tested
    vars = read_from_yaml(mode, mva_vars)
    cuts = read_from_yaml(mode, selection_files)

    TMVA.Tools.Instance()
    print("==> Start TMVAClassification")

    tsig = load_data(input_tree_name_mc, input_files_mc)
    print("numSig:", tsig.GetEntries())
    tbkg = load_data(input_tree_name_bkg, input_files_bkg)
    print("numBkg:", tbkg.GetEntries())
    
    if not output_file.endswith(".root"): output_file+=".root"
    outputFile = TFile(output_file, "RECREATE") # output_file name should have a prefix of "TMVA"

    factory = TMVA.Factory("TMVAClassification", outputFile,
                           "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification")

    dataloader = TMVA.DataLoader(output_ds)

    for v in vars.keys():
        dataloader.AddVariable(vars[v])

    signalWeight = 1.0
    backgroundWeight = 1.0

    dataloader.AddSignalTree(tsig, signalWeight)
    dataloader.AddBackgroundTree(tbkg, backgroundWeight)

    scut=cuts["scut"]
    bcut=cuts["bcut"]

    train_test = "nTrain_Signal={}:nTrain_Background={}:SplitMode=Random:NormMode=NumEvents:!V".format(
        int(tsig.GetEntries(scut) * 0.5),
        int(tbkg.GetEntries(bcut) * 0.5)
    )
    
    dataloader.PrepareTrainingAndTestTree(TCut(scut), TCut(bcut), train_test)
    
    ConfigureEachMethod(factory, dataloader, Use)
    #factory.BookMethod(dataloader, TMVA.Types.kBDT, "BDT",
    #                "!H:!V:NTrees=850:MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20")
    
    # ----------------------------------
    # Train, test, and evaluate the MVAs
    # ----------------------------------
    # Train MVAs using the set of training events
    factory.TrainAllMethods()
    # Evaluate all MVAs using the set of test events
    factory.TestAllMethods()
    # Evaluate and compare performance of all configured MVAs
    factory.EvaluateAllMethods()

    # Save the output
    outputFile.Close()
    print("==> Wrote root file:", outputFile.GetName())
    print("==> TMVAClassification is done!")

    # Launch the GUI for the root macros
    #if not gROOT.IsBatch():
    #    TMVA.TMVAGui(output_file)

def evaluate(output_ds, output_file):
    ROOT.gROOT.SetBatch(True)

    # input variable distributions
    TMVA.variables(output_ds, output_file)
    # correlation matrices
    TMVA.correlations(output_ds, output_file)
    # overtraining test
    TMVA.mvas(output_ds, output_file, TMVA.HistType.kCompareType)
    # TMVA.mvas(f'dataset_{prefix}',ofile,TMVA.HistType.kMVAType)
    # ROC
    TMVA.efficiencies(output_ds, output_file)


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files-mc', nargs='+',
                        help='Path to the input MC file')
    parser.add_argument('--input-tree-name-mc',
                        default='DecayTree', help='Name of the tree of MC file')
    parser.add_argument('--input-files-bkg', nargs='+',
                        help='Path to the input bkg file')
    parser.add_argument('--input-tree-name-bkg',
                        default='DecayTree', help='Name of the tree of bkg file')
    parser.add_argument('--output-file', help='Output ROOT file')
    parser.add_argument('--output-ds', help='Output dataset directory')
    parser.add_argument('--method-config', nargs='+',
                        help='Yaml files of training methods and their configuration')
    parser.add_argument('--mode', help='Name of the decay modes to be trained')
    parser.add_argument('--mva-vars', default='', nargs='+',
                        help='Yaml files of training variables')
    parser.add_argument('--selection-files', default='', nargs='+',
                        help='Yaml files of cuts for signals and bkg')
    args = parser.parse_args()
    
    train(**vars(args))
    evaluate(args.output_ds, args.output_file)
    
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
