import time
import argparse
import yaml


import ROOT
from ROOT import TFile, TCanvas, TArrow, TGraph, TGraphErrors


ROOT.gROOT.ProcessLine(".x ~/lhcbStyle.C")
ROOT.gROOT.SetBatch(True)


def read_from_yaml(mode, selection_files):
    selection_dict = dict()
    for file in selection_files:
        with open(file, 'r') as stream:
            selection_dict.update(yaml.safe_load(stream)[mode])
    return selection_dict


def plot(input_files, input_tree_name, output_file, method_config, working_point):
    f = TFile(input_files, "r")

    for i in range(len(method_config)):
        method = method_config[i]
        wp = working_point[i]
        fom = f.Get(input_tree_name+method)
        can = TCanvas("can", "", 800, 600)
        fom.GetHistogram().SetMinimum(0)
        fom.GetHistogram().SetMaximum(fom.GetHistogram().GetMaximum()*1.1)
        fom.Draw("ACP")
        ar = TArrow()
        ar.SetAngle(40)
        ar.SetLineWidth(2)
        ar.SetLineColor(ROOT.kRed)
        ar.SetFillColor(ROOT.kRed)
        ar.DrawArrow(wp, 0, wp, fom.Eval(wp), 0.05, "|>")
        can.Print(output_file)
        can.Close()


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree', help='Name of the tree of file')
    parser.add_argument('--output-file', help='Output file name')
    parser.add_argument('--method-config', nargs='+',
                        help='Method to draw.')
    parser.add_argument('--working-point', type=float, nargs='+', help='Working point of MVA')
    args = parser.parse_args()

    plot(**vars(args))

    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
