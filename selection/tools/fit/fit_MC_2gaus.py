from array import array
import numpy as np
import time
import argparse
import yaml
import json
import sys, os
import math

from ROOT import (vector, RooRealVar, RooDataSet, RooDataHist, gSystem,
                  gROOT, TCanvas, TPad, TMath, kBlue, kRed, TLegend, TChain, TH1D,
                  RooStats, TFile, RDataFrame, RooGaussian, TLine, RooArgList, RooAddPdf, RooPolyVar, RooArgSet)
import ROOT as rt
from ROOT import RooFit as rf

#from ..utilities import draw_pull
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities import draw_pull

gROOT.ProcessLine(".x ~/lhcbStyle.C")


def fit(input_files, input_tree_name, mode, in_func,  out_func, output_files, frac_, a1_):
    # batch mode
    gROOT.SetBatch(1)
    # rt.RooMsgService.instance().setGlobalKillBelow(rf.FATAL)


    # configs
    nbins = 50
    xlow, xup = 5250, 5315
    xtitle = {"B2DDpi": "#it{m}_{#it{D}^{+}#it{D}^{#minus}#it{#pi}^{+}} [MeV/#it{c}^{2}]",
              "B2D0D0pi2b2b": "#it{m}_{#it{D}^{0} #bar{#it{D}}^{0}#it{#pi}^{+}} [MeV/#it{c}^{2}]",
              "B2D0D0pi2b4b": "#it{m}_{#it{D}^{0} #bar{#it{D}}^{0}#it{#pi}^{+}} [MeV/#it{c}^{2}]"
              }

    x = RooRealVar("B_PVF_M", "mass", xlow, xup)
    
    # import data chain
    input_files = [input_files] if type(
        input_files) != type([]) else input_files
    ch = TChain(input_tree_name)
    for n in input_files:
        ch.Add(n)
    data = RooDataSet("data", "data", ch, x, "B_PVF_M>{0} && B_PVF_M<{1}".format(xlow, xup))
    nentries = data.numEntries()
    print(f"Total event numbers {nentries}...")

    mean = RooRealVar("mean", "mean", 5279, xlow, xup)
    sigma1 = RooRealVar("sigma1", "sigma1", 11., 0.1, 20)
    a0 = RooRealVar("a0", "a0", 0.)
    a1 = RooRealVar("a1", "a1", 0.5, 0.01, 1.)
    if a1_:
        a1 = RooRealVar("a1", "a1", a1_)
    sigma2 = RooPolyVar("sigma2", "sigma2", sigma1, RooArgSet(a0, a1))
    '''
    sigma2 = RooRealVar("sigma2", "sigma2", 7., 0.1, 20)
    frac = RooRealVar("frac", "", 0.3, 0., 1.)
    '''
    frac = RooRealVar("frac", "", 0.3, 0.01, 1.)
    if frac_:
        frac = RooRealVar("frac", "", frac_)

    signal1 = RooGaussian("signal1", "Gaussian pdf", x, mean, sigma1)
    signal2 = RooGaussian("signal2", "Gaussian pdf", x, mean, sigma2)
    #signal = RooAddPdf("signal", "two gaus", [signal1, signal2], [frac])
    signal = RooAddPdf("signal", "two gaus", RooArgList(signal1, signal2), RooArgList(frac))

    # read parameters in
    # The input func file determines the final setting of params, even if a1
    # and frac may have been fixed before.
    if in_func:
        params = signal.getParameters(x)
        params.readFromFile(in_func)

    r = signal.fitTo(data, rf.Save())
    r.Print()
    params = signal.getParameters(x)
    params.writeToFile(out_func)

    from math import sqrt
    reso = sqrt(frac.getVal()*sigma1.getVal()**2 +
                (1-frac.getVal())*sigma2.getVal()**2)
    print("The resolution of signal peak is: ", reso)

    # Plot the fit results
    xframe = x.frame(Title="Signal pdf fit")
    xframe.SetXTitle(xtitle[mode])
    xframe.SetYTitle("Events")
    data.plotOn(xframe, Name="data_fit", MarkerSize=0.8, Binning=nbins)
    signal.plotOn(xframe, Components = {signal1}, Name = "Gaussian1", LineStyle = 10, LineColor = "kBlue")
    signal.plotOn(xframe, Components = {signal2}, Name = "Gaussian2", LineStyle = 10, LineColor = "kGreen")
    signal.plotOn(xframe, Name = "Total fit", LineColor = "kRed", LineStyle = "-")
    data.plotOn(xframe, Name="data_fit", MarkerSize=0.8, Binning=nbins)
    

    def DrawAll(xframe, xx, drawleg=True):
        can = TCanvas("can", "", 800, 700)
        pad1 = TPad("pad1", "", 0.0, 0.34, 1, 1.0)
        pad1.SetBottomMargin(0.01)
        pad1.Draw()
        pad1.cd()
        xframe.SetMinimum(0.5)
        xframe.GetXaxis().CenterTitle()
        xframe.GetYaxis().CenterTitle()
        xframe.Draw()
        if drawleg:
            leg = TLegend(0.7, 0.6, 0.93, 0.9)
            leg.SetBorderSize(0)
            leg.SetTextSize(0.05)
            leg.SetTextFont(132)
            leg.AddEntry(xframe.findObject("data_fit"), "MC", "lpe")
            leg.AddEntry(xframe.findObject("Gaussian1"), "Gaussian1", "l")
            leg.AddEntry(xframe.findObject("Gaussian2"), "Gaussian2", "l")
            leg.AddEntry(xframe.findObject("Total fit"), "Total fit", "l")
            leg.Draw()
        can.cd()
        pad2 = TPad("pad2", "pull", 0.0, 0.0, 1, 0.32)
        pad2.SetTopMargin(0.07)
        pad2.SetBottomMargin(0.6)
        pad2.Draw()
        pad2.cd()
        pull = draw_pull(xframe, xx, "data_fit", "Total fit", xframe.GetXaxis().GetTitle())
        pull.Draw()
        ln = TLine()
        ln.SetLineColor(rt.kBlack)
        ln.DrawLine(xlow, 0., xup, 0.)
        # It seems that legend object will be deleted outside the DrawAll function, and won't appear in the figure. So I print the Canvas inside the function.
        
        can.Print(output_files)

    DrawAll(xframe, x, drawleg=True)


if __name__ == '__main__':
    time_start = time.time()  # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files',
                        nargs='+',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree',
                        help='Name of the tree')
    parser.add_argument('--mode',
                        help='Mode of the decay')
    parser.add_argument('--in-func',
                        help='Input func file of parameters ')
    parser.add_argument('--out-func',
                        help='Output func file of parameters ')
    parser.add_argument('--output-files',
                        help='Output file of fit plots')
    parser.add_argument('--frac_', type=float,
                        help='Fixed value of frac if fixed')
    parser.add_argument('--a1_', type=float,
                        help='Fixed value of a1 if fixed')
    args = parser.parse_args()

    fit(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum / 60, 2)))
