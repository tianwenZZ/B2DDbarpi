import time
import argparse
import yaml

import ROOT
from ROOT import (
    vector,
    TCut,
    kBlack, kRed, kBlue,
    TCanvas,
    TH1F,
)

from utilities import read_from_yaml, load_data


def plot_misID_shape(input_files, input_tree_name,
                     output_file,
                     config_file, mode):
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine(".x ~/lhcbStyle.C")

    config = read_from_yaml(mode, config_file)
    nbins = config["nbins"]
    var = config["var"]
    xlow = config["min"]
    xup = config["max"]
    cut = config["cut"]

    tree = load_data(input_tree_name, input_files)
    # histo of mB distributions of + -> D+ D- K+ where K mis-identified as pi
    h_mB0 = TH1F("h_mB0", "histo of mB distribution w/o cut", nbins, xlow, xup)
    h_mB = TH1F("h_mB", "histo of mB distribution", nbins, xlow, xup)
    h_Bpeak = TH1F("h_Bpeak", "histo of signal B peak", nbins, xlow, xup)
    # Set the attributes of histogram
    h_mB0.GetXaxis().SetTitle("m(B^{+}) [MeV/c^{2}]")
    h_mB0.GetYaxis().SetTitle("Events")
    h_mB0.SetLineColor(kBlack)
    h_mB.GetXaxis().SetTitle("m(B^{+}) [MeV/c^{2}]")
    h_mB.GetYaxis().SetTitle("Events")
    h_mB.SetLineColor(kRed)
    h_Bpeak.GetXaxis().SetTitle("m(B^{+}) [MeV/c^{2}]")
    h_Bpeak.GetYaxis().SetTitle("Events")
    h_Bpeak.SetLineColor(kBlue)

    can = TCanvas("can", "", 800, 600)
    tree.Draw("(B_M-D1_M-D2_M+1.86966*2)*1000>>h_Bpeak")
    #tree.Draw(var+">>h_mB0","","same")
    tree.Draw(var+">>h_mB", cut, "same")

    can.Print(output_file)


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files', nargs='+',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree', help='Name of the tree')
    parser.add_argument('--output-file', help='Output ROOT file')
    parser.add_argument('--config-file', nargs='+',
                        help='Yaml file of figure configuraions')
    parser.add_argument('--mode', help='Decay mode')
    args = parser.parse_args()
    plot_misID_shape(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
