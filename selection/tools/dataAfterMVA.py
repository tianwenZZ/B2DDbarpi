from ROOT import TCanvas, TTree, TH1F, TFile
from ROOT import TLatex, TArrow
from ROOT import kRed
import ROOT

import time
import argparse
import yaml

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine(".x ~/lhcbStyle.C")
ROOT.gStyle.SetLegendTextSize(0.03)

ROOT.gROOT.SetBatch(1)
nbins = 100
xlow = 5000
xup = 5600

xtitle = {"B2DDpi": "m_{D^{+}D^{-}#pi^{+}} [MeV/c^{2}]",
          "B2D0D0pi2b2b": "m_{D^{0}#bar{D}^{0}#pi^{+}} [MeV/c^{2}]",
          "B2D0D0pi2b4b": "m_{D^{0}#bar{D}^{0}#pi^{+}} [MeV/c^{2}]",
          "B2DpDstmpi": "m_{D^{+}D^{*-}#pi^{+}} [MeV/c^{2}]",
          "B2DstpDmpi": "m_{D^{*+}D^{-}#pi^{+}} [MeV/c^{2}]",
          "B2DstDstpi": "m_{D^{*+}D^{*-}#pi^{+}} [MeV/c^{2}]",
          }

pos = {
    "B2DDpi": {"signal": [500, 100],
               "bkg": [200, 100],
               "BDT": 850},
    "B2D0D0pi2b2b": {"signal": [500, 100],
                     "bkg": [200, 100],
                     "BDT": 850},
    "B2D0D0pi2b4b": {"signal": [500, 100],
                     "bkg": [200, 100],
                     "BDT": 850},
    "B2DpDstmpi": {"signal": [60, 45],
                   "bkg": [30, 10],
                   "BDT": 80},
    "B2DstpDmpi": {"signal": [60, 45],
                   "bkg": [30, 10],
                   "BDT": 80},
    "B2DstDstpi": {"signal": [10, 6],
                   "bkg": [4, 2],
                   "BDT": -1},
}


def plot(input_files, input_tree_name, output_file_path, mode, method, working_point):
    f = TFile(input_files, "r")
    t = f.Get(input_tree_name)

    h = TH1F("h", "", nbins, xlow, xup)
    tcut = method + ">" + working_point
    t.Draw("B_PVF_M>>h", tcut)

    htot = TH1F("htot", "bkg", nbins, xlow, xup)
    htot.SetLineColor(ROOT.kBlue)
    htot.SetMarkerStyle(0)
    t.Draw("B_PVF_M>>htot")
    # htot.Scale(h.Integral()/htot.Integral())
    htot.SetMinimum(0)
    htot.SetXTitle(xtitle[mode])
    htot.SetYTitle("Candidates")

    can = TCanvas("can", "", 800, 600)
    h.SetXTitle(xtitle[mode])
    h.SetYTitle("Candidates")
    h.SetLineColor(kRed)

    htot.Draw("hist")
    # for B->DstDstpi don't apply MVA (signal too small)
    if mode != "B2DstDstpi":
        h.Draw("hist,same")

        lt = TLatex()
        lt.SetTextSize(0.08)
        lt.SetTextColor(kRed)
        lt.DrawLatex(5400, pos[mode]["BDT"], tcut)

    # ar2 = TArrow(5350, 230, 5300, 100, 0.03, "|>")
    ar2 = TArrow(5350, pos[mode]["signal"][0], 5300,
                 pos[mode]["signal"][1], 0.03, "|>")
    ar2.SetAngle(60)
    ar2.SetLineWidth(2)
    ar2.SetFillColor(kRed)
    ar2.SetLineColor(kRed)
    ar2.Draw()

    text2 = ROOT.TText()
    text2.SetTextFont(43)
    text2.SetTextSize(25)
    text2.SetTextColor(kRed)
    text2.DrawText(5360, pos[mode]["signal"][0], "Signal")

    ar3 = TArrow(5450, pos[mode]["bkg"][0], 5400, pos[mode]["bkg"][1], 0.03, "|>")
    ar3.SetAngle(60)
    ar3.SetLineWidth(2)
    ar3.SetFillColor(kRed)
    ar3.SetLineColor(kRed)
    ar3.Draw()

    text3 = ROOT.TText()
    text3.SetTextFont(43)
    text3.SetTextSize(25)
    text3.SetTextColor(kRed)
    text3.DrawText(5425, pos[mode]["bkg"][0], "Combinatorial bkg")

    leg = ROOT.TLegend(0.65, 0.7, 0.83, 0.92)
    if mode != "B2DstDstpi":
        leg.AddEntry(h, "Pass MVA cut", "l")
    leg.AddEntry(htot, "Pass only preselections", "l")
    leg.Draw()

    can.Print(output_file_path+"/data_aftermva.pdf")


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree', help='Name of the tree')
    parser.add_argument('--output-file-path', help='Output ROOT file path')
    parser.add_argument('--mode', help='Mode of decay')
    parser.add_argument('--method', help='Method of MVA')
    parser.add_argument('--working-point', help='Working point')

    args = parser.parse_args()
    plot(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
