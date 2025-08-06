import time
import argparse
import yaml
import numpy as np
from math import sqrt, pow
from array import array


import ROOT as rt
from ROOT import TFile, gROOT, TGraphErrors, vector, RDataFrame, RooFit, TCanvas
from ROOT import RooRealVar, RooAddPdf, RooExponential, RooStats, RooGaussian, RooDataSet, RooArgSet, RooArgList


def read_from_yaml(mode, selection_files):
    selection_dict = dict()
    for file in selection_files:
        with open(file, 'r') as stream:
            selection_dict.update(yaml.safe_load(stream)[mode])
    return selection_dict


def load_data(input_tree_name, input_files):
    rt.EnableImplicitMT()
    names = vector('string')()
    for n in input_files:
        names.push_back(n if n.endswith('.root') else n+'*.root')
    dataframe = RDataFrame(input_tree_name, names)
    return dataframe.AsNumpy()


def EffMap(input_files, input_tree_name,
           method_config,
           mmin, mmax):
    arr0 = load_data(input_tree_name, input_files)
    graphs = {}
    for m in method_config.keys():
        t0 = method_config[m]
        arr_mass = arr0["B_PVF_M"]
        arr = arr0[m][(arr_mass > mmin) & (arr_mass < mmax)]
        N0 = arr[arr > t0].size
        x = list(np.arange(t0, arr.max(), 0.01))
        y = []
        xerr = []
        yerr = []
        # npoints = 30
        for t in x:
            N = arr[arr > t].size
            if N == 0:
                break
            eff = N/N0
            efferr = eff*sqrt((1.-N/arr.size)/N + (1.-N0/arr.size)/N0)
            y.append(eff), xerr.append(0), yerr.append(efferr)
        graphs[m] = TGraphErrors(len(x), array('d', x), array(
            'd', y), array('d', xerr), array('d', yerr))
        graphs[m].GetXaxis().SetTitle(m)
        graphs[m].GetYaxis().SetTitle("Cut efficiency")
    return graphs


def Fit(input_files, input_tree,
        method_config, fit_params_path,
        mmin, mmax):
    gROOT.ProcessLine(".x ~/lhcbStyle.C")
    xlow, xup = 5250, 5400
    mB = RooRealVar("mB", "", xlow, xup)
    mB.setRange("SignalWindow", mmin, mmax)
    arr = load_data(input_tree, input_files)
    arr_mass = arr["B_PVF_M"]

    def myIntegral(pdf, x, nfull, range=""):
        intfull = pdf.createIntegral(x, RooFit.Range("")).getVal()
        intcut = pdf.createIntegral(x, RooFit.Range(range)).getVal()
        return nfull/intfull*intcut

    params_underpeak = {}
    for m in method_config.keys():
        arr_mass = arr_mass[(arr_mass > xlow) & (
            arr_mass < xup) & (arr[m] > method_config[m])]
        data = RooDataSet.from_numpy({"mB": arr_mass}, [mB])
        nentries = data.numEntries()
        print(f"{nentries} events to be fit...")

        mean = RooRealVar("mean", "mean of Gaussian", 5279, 5270, 5300)
        sigma = RooRealVar("sigma", "sigma of Gaussian", 6., 0.1, 15)
        signal = RooGaussian("Gaussian", "", mB, mean, sigma)

        alpha = RooRealVar(
            "alpha", "slope of exponential", -0.001, -1., -0.0000001)
        bkg = RooExponential("bkg", "Exponential model", mB, alpha)

        nsig = RooRealVar("nsig", "number of signal",
                          0.7*nentries, 0.1, nentries)
        nbkg = RooRealVar("nbkg", "number of bkg", 0.2*nentries, 0.1, nentries)

        model = RooAddPdf("model", "sig+bkg",
                          RooArgList(signal, bkg), RooArgList(nsig, nbkg))
        r = model.fitTo(data, RooFit.Save())
        r.Print()
        params = model.getParameters(RooArgSet(mB))
        params.writeToFile(fit_params_path+"/"+m+".txt")

        xframe = mB.frame(RooFit.Title(
            "Gaussian+Exponential pdf fit"), RooFit.Bins(40))
        xframe.GetXaxis().SetTitle("B_PVFit_M/MeV")
        data.plotOn(xframe)
        model.plotOn(xframe, RooFit.Components(
            bkg), RooFit.LineStyle(rt.kDashed))
        model.plotOn(xframe, RooFit.Components(signal),
                     RooFit.LineStyle(rt.kDotted), RooFit.LineColor(rt.kRed))
        model.plotOn(xframe)
        can = TCanvas("can", "", 800, 600)
        xframe.Draw()
        can.Print(fit_params_path+"/fitt0.pdf")
        can.Close()

        nsig_underpeak = myIntegral(
            signal, mB, nsig.getVal(), range="SignalWindow")
        nsig_underpeak_err = myIntegral(
            signal, mB, nsig.getError(), range="SignalWindow")
        nbkg_underpeak = myIntegral(
            bkg, mB, nbkg.getVal(), range="SignalWindow")
        nbkg_underpeak_err = myIntegral(
            bkg, mB, nbkg.getError(), range="SignalWindow")

        params_underpeak[m] = (
            (nsig_underpeak, nsig_underpeak_err), (nbkg_underpeak, nbkg_underpeak_err))
        print(params_underpeak)

    return params_underpeak


def optimize(input_files_mc, input_tree_name_mc, input_files_data, input_tree_name_data,
             output_file, fit_params_path,
             method_config):
    gROOT.ProcessLine(".x ~/lhcbStyle.C")
    methods = {}
    Use = read_from_yaml("MVAmethods", method_config)
    for key in Use.keys():
        if Use[key]:
            methods[key] = -9999
    methods["BDT"] = -0.1   # starter cut of BDT

    ofile = TFile(output_file, "recreate")

    print("### Fit at very loose cut ...")
    fitresults = Fit(input_files_data, input_tree_name_data,
                     methods, fit_params_path, 5259, 5299)

    print("### Generating signal cut efficiency ...")
    sig_eff = EffMap(input_files_mc, input_tree_name_mc,
                     methods, mmin=5259, mmax=5299)
    print("### Generating bkg cut retentention rate ...")
    bkg_retention = EffMap(input_files_data, input_tree_name_data,
                           methods, mmin=5500, mmax=99999)

    print("### Calculating FoM ...")
    gr_fom = {}
    for m in methods.keys():
        x, y, xerr, yerr = [], [], [], []
        ((S0, S0err), (B0, B0err)) = fitresults[m]
        n = min(sig_eff[m].GetN(), bkg_retention[m].GetN())
        print(f"### Total {n} points to be looped ...")
        for idata in range(0, n):
            eff, efferr = sig_eff[m].GetPointY(
                idata), sig_eff[m].GetErrorY(idata)
            retention, retentionerr = bkg_retention[m].GetPointY(
                idata), bkg_retention[m].GetErrorY(idata)
            # definded in the form of significance: S/sqrt(S+B)
            fom = S0*eff/sqrt(B0*retention+S0*eff)

            parf_parS0_sq = (eff/sqrt(S0*eff+B0*retention) -
                             S0*eff**2/2/pow(S0*eff+B0*retention, 1.5))**2
            parf_pareff_sq = (S0/sqrt(S0*eff+B0*retention) -
                              eff*S0**2/2/pow(S0*eff+B0*retention, 1.5))**2
            parf_parB0_sq = (-S0*eff/2*retention *
                             pow(S0*eff+B0*retention, -1.5))**2
            parf_parr_sq = (-S0*eff/2*B0*pow(S0*eff+B0*retention, -1.5))**2
            fomerr = sqrt(parf_parS0_sq*S0err**2+parf_pareff_sq*efferr **
                          2+parf_parB0_sq*B0err**2+parf_parr_sq*retentionerr**2)

            x.append(sig_eff[m].GetPointX(idata))
            y.append(fom)
            xerr.append(0.)
            yerr.append(fomerr)

        gr_fom[m] = TGraphErrors(n, array('d', x), array(
            'd', y), array('d', xerr), array('d', yerr))
        gr_fom[m].SetTitle("fom curve S/#sqrt{S+B} for method "+m)
        gr_fom[m].SetName("fom_"+m)
        gr_fom[m].SetMarkerStyle(21)
        gr_fom[m].SetMarkerColor(4)
        gr_fom[m].GetXaxis().SetTitle(m)
        gr_fom[m].GetYaxis().SetTitle("S/#sqrt{S+B}")
        # gr_fom[m].GetXaxis().SetRangeUser(-0.25,0.55555)

    for m in methods.keys():
        gr_fom[m].Write()
        sig_eff[m].SetName("signaleff_"+m)
        sig_eff[m].Write()
        bkg_retention[m].SetName("bkgretention_"+m)
        bkg_retention[m].Write()
    ofile.Close()


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files-mc', nargs='+',
                        help='Path to the input MC file')
    parser.add_argument('--input-tree-name-mc',
                        default='DecayTree', help='Name of the tree of MC file')
    parser.add_argument('--input-files-data', nargs='+',
                        help='Path to the input data file')
    parser.add_argument('--input-tree-name-data',
                        default='DecayTree', help='Name of the tree of data file')
    parser.add_argument('--output-file', help='Output ROOT file of FoM curve')
    parser.add_argument('--fit-params-path', help='Output path of fit prams')
    parser.add_argument('--method-config', nargs='+',
                        help='Yaml files of training methods and their configuration')
    # parser.add_argument('--mode', help='Name of the decay modes to be trained')
    args = parser.parse_args()

    optimize(**vars(args))

    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
