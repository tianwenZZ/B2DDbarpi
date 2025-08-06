from array import array
import numpy as np
import time
import argparse
import yaml
import json
import math
import sys, os


from ROOT import (vector, RooRealVar, RooDataSet, RooDataHist, gSystem,
                  gROOT, TCanvas, TPad, TMath, kBlue, kRed, TLegend, TChain, TH1D,
                  RooStats, TFile, RDataFrame, RooGaussian, TLine, RooArgList, RooAddPdf, RooPolyVar, RooArgSet, RooExponential,
                  TString)
import ROOT as rt
from ROOT import RooFit as rf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities import draw_pull

gROOT.ProcessLine(".x ~/lhcbStyle.C")
gROOT.ProcessLine(".x /home/zhoutw/workdir/B2DDbarpi/git-repo/selection/tools/fit/RooCruijffPdf.cxx")


def fit(input_files, input_tree_name, mode, in_func,  out_func, cfit_figs, output_files, output_tree_name):
    # batch mode
    gROOT.SetBatch(1)
    # rt.RooMsgService.instance().setGlobalKillBelow(rf.FATAL)

    # set lhcb style
    gROOT.ProcessLine(".x ~/lhcbStyle.C")

    # configs
    nbins = 40
    xlow, xup = 5250, 5450
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
    '''
    names = vector('string')()
    for n in input_files:
        names.push_back(n if n.endswith('.root') else n+'*.root')
    dataframe = RDataFrame(input_tree_name, names)
    df_array = dataframe.AsNumpy()
    Bmass = np.array([m[0] for m in df_array["B_PVFitD_M"]])
    Bmass = Bmass[(Bmass > xlow) & (Bmass < xup)]
    data = RooDataSet.from_numpy({"mB": Bmass}, x)
    '''
    nentries = data.numEntries()
    print(f"Total event numbers {nentries}...")

    # Signal pdf
    mean = RooRealVar("mean", "mean", 5279, xlow, xup)

    sigmaL = RooRealVar("sigmaL", "sigmaL", 8.9, 0.1, 20)
    sigmaR = RooRealVar("sigmaR", "sigmaR", 8.9, 0.1, 20) 
    nl = RooRealVar("nl", "nl", 70.,0.,140.)
    nr = RooRealVar("nr", "nr", 70.,0.,140.)
    al = RooRealVar("al", "al", 1.39, 0, 20)
    ar = RooRealVar("ar", "ar", 1.55, 0, 20)

    signal = rt.RooCruijffPdf("signal", "cruijff pdf", x, mean, sigmaL, sigmaR, al, ar)


    # read parameters in
    if in_func:
        params = signal.getParameters(x)
        params.readFromFile(in_func)
        for par in params:
            if par.GetName()=="al":
                par.setConstant()
            if par.GetName()=="ar":
                par.setConstant()
        

    # Bkg pdf
    alpha = RooRealVar("alpha", "alpha", -0.001, -1., -0.0000001)
    combin_bkg = RooExponential("combin_bkg", "Exponential model", x, alpha)

    ncombkg = RooRealVar("ncombkg", "", 80., 0., nentries)
    nsig = RooRealVar("nsig","",80.,0.,nentries)

    # Fit pdf
    model = RooAddPdf("model","signal+bkg", [signal, combin_bkg], [nsig, ncombkg])

    r = model.fitTo(data, Save=True)
    r.Print()
    output_params = model.getParameters(x)
    output_params.writeToFile(out_func)


    # Plot the fit results
    xframe = x.frame(Title="PDF fit", Bins=nbins)
    xframe.SetXTitle(xtitle[mode])
    xframe.SetYTitle("Events")
    data.plotOn(xframe, Name="data_fit", MarkerSize=0.8)
    model.plotOn(xframe, Components={signal}, Name="signal", LineColor="kBlack", LineStyle="--")
    model.plotOn(xframe, Components={combin_bkg}, Name="combin_bkg", LineColor="kMagenta", LineStyle="--")
    model.plotOn(xframe, Name="Total fit", LineColor="kRed", LineStyle="-")
    data.plotOn(xframe)

    def DrawAll(xframe, xx, output_path, drawleg=True):
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
            leg.AddEntry(xframe.findObject("data_fit"), "Data", "lpe")
            leg.AddEntry(xframe.findObject("Total fit"), "Total fit", "l")
            leg.AddEntry(xframe.findObject("signal"), "Signal", "l")
            leg.AddEntry(xframe.findObject("combin_bkg"), "Bkg", "l")
            leg.Draw()
        can.cd()
        pad2 = TPad("pad2", "pull", 0.0, 0.0, 1, 0.32)
        pad2.SetTopMargin(0.07)
        pad2.SetBottomMargin(0.6)
        pad2.Draw()
        pad2.cd()
        pull = draw_pull(xframe, xx,  "data_fit", "Total fit", xframe.GetXaxis().GetTitle())
        pull.Draw()
        ln = TLine()
        ln.SetLineColor(rt.kBlack)
        ln.DrawLine(xlow, 0., xup, 0.)
        # It seems that legend object will be deleted outside the DrawAll function, and won't appear in the figure. So I print the Canvas inside the function.
        can.Print(output_path)

    # Draw cfit results
    DrawAll(xframe, x, drawleg=True, output_path=cfit_figs)

    # calculate sweight
    sData = RooStats.SPlot("sData", "sData", data, model, [nsig, ncombkg])
    '''
    # This doesn't work because data is not a build-in variable in Rdataframe.
    # We cannot directly use dataframe.Filter().
    # Details in https://www.nevis.columbia.edu/~seligman/root-class/RootClass2023.pdf .
    @rt.Numba.Declare(["int"], "double")
    def get_sw(index):
        global data
        return data.get(index).find("nsig_sw").getVal()
    dataframe = dataframe.Filter("B_PVFitD_M[0]>{0} && B_PVFitD_M[0]<{1}".format(xlow, xup))\
                         .Define("sig_sw", "Numba::get_sw(i)")
    dataframe.Snapshot(output_tree_name, output_files)
    '''
    sw_file = TFile(output_files, "recreate")
    sw_tree = ch.CloneTree(0)
    sw = array("d", [0.])
    sw_tree.Branch("sig_sw", sw, "sig_sw/D")
    index = -1
    for evt in ch:
        if evt.B_PVF_M<xlow or evt.B_PVF_M>xup: continue
        index += 1
        sw[0] = data.get(index).find("nsig_sw").getVal()
        sw_tree.Fill()
    sw_tree.Write()       
    



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
    parser.add_argument('--cfit-figs',
                        help='Output file path of cfit figs')
    parser.add_argument('--output-files',
                        help='Output file of dataset with sWeight')
    parser.add_argument('--output-tree-name',
                        default='DecayTree',
                        help='Name of the tree')
    args = parser.parse_args()

    fit(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum / 60, 2)))
