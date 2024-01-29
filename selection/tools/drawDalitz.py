import time
import argparse
import yaml

from ROOT import TCanvas, TTree, TFile, TChain, TF1, gROOT, TH2F, TH1F
from math import sqrt
import ROOT
from ROOT import kBird

from utilities import DalitzPhaseSpace, read_from_yaml


mB = 5.27925000   # B+
mDp = 1.86962000  # D+
mD0 = 1.86486000  # D0
mK0 = 0.49761400  # K0
mpi = 0.13957039  # pi+
margin = 0.05
nbins = 40

phsp = {"B2DDpi": DalitzPhaseSpace(mB, mDp, mDp, mpi),
        "B2D0D0pi2b2b": DalitzPhaseSpace(mB, mD0, mD0, mpi)
        }

axis_title_2d = {"B2DDpi":
                 {"m12": "m_{D^{+}D^{-}}^{2} [GeV^{2}]",
                  "m13": "m_{D^{+}#pi^{+}}^{2} [GeV^{2}]",
                  "m23": "m_{D^{-}#pi^{+}}^{2} [GeV^{2}]"},
                 "B2D0D0pi2b2b":
                 {"m12": "m_{D^{0}#bar{D^{0}}}^{2} [GeV^{2}]",
                     "m13": "m_{D^{0}#pi^{+}}^{2} [GeV^{2}]",
                     "m23": "m_{#bar{D}^{0}#pi^{+}}^{2} [GeV^{2}]"}
                 }

axis_title_1d = {"B2DDpi":
                 {"m12": "m_{D^{+}D^{-}} [GeV/c^{2}]",
                  "m13": "m_{D^{+}#pi^{+}} [GeV/c^{2}]",
                  "m23": "m_{D^{-}#pi^{+}} [GeV/c^{2}]"},
                 "B2D0D0pi2b2b":
                 {"m12": "m_{D^{0}#bar{D^{0}}} [GeV/c^{2}]",
                     "m13": "m_{D^{0}#pi^{+}} [GeV/c^{2}]",
                     "m23": "m_{#bar{D}^{0}#pi^{+}} [GeV/c^{2}]"}
                 }

gROOT.ProcessLine(".x ~/lhcbStyle.C")
ROOT.gStyle.SetPalette(kBird)
gROOT.SetBatch(1)


def drawDalitz(input_files, input_tree_name, output_file_path,
               mode, sw, dalitz_vars, resonances):
    input_files = [input_files] if type(
        input_files) != type([]) else input_files
    chain = TChain(input_tree_name)
    for n in input_files:
        chain.Add(n)
    print("Total number : %f" % (chain.GetEntries()))

    # Set text attributes
    tex = ROOT.TLatex()
    tex.SetTextSize(0.05)
    tex.SetTextAlign(11)

    yv, xv = dalitz_vars[0], dalitz_vars[1]
    assert yv == "m12" or yv == "m13" or yv == "m23", "Unexpected Dalitz variable name for y-axis!"
    assert xv == "m12" or xv == "m13" or xv == "m23", "Unexpected Dalitz variable name for x-axis!"

    # Initialize histograms
    hist = {
        "m12": TH1F("hm12", "", nbins, sqrt(phsp[mode].lowerLimit("12"))-0.2, sqrt(phsp[mode].upperLimit("12"))+0.2),
        "m13": TH1F("hm13", "", nbins, sqrt(phsp[mode].lowerLimit("13"))-0.2, sqrt(phsp[mode].upperLimit("13"))+0.2),
        "m23": TH1F("hm23", "", nbins, sqrt(phsp[mode].lowerLimit("23"))-0.2, sqrt(phsp[mode].upperLimit("23"))+0.2),
        "scatter": TH2F("hscatter", "scatter",
                        1000, phsp[mode].lowerLimit(
                            xv[1:])-0.5, phsp[mode].upperLimit(xv[1:])+0.5,
                        1000, phsp[mode].lowerLimit(yv[1:])-0.5, phsp[mode].upperLimit(yv[1:])+0.5)
    }
    hist["scatter"].SetMarkerSize(0.5)
    hist["scatter"].SetXTitle(axis_title_2d[mode][xv])
    hist["scatter"].SetYTitle(axis_title_2d[mode][yv])

    if not sw:
        sw = ""
    # The unit of m12/m13/m23 in tree branches is MeV by default. Convert MeV to GeV.
    expr = f"{yv}*{yv}/1000000:{xv}*{xv}/1000000"
    chain.Project("hscatter", expr)   # Draw with sw will cause PROBLEMS !!!
    for m1d in ["m12", "m13", "m23"]:
        chain.Project("h"+m1d, m1d+"/1000", sw)
        hist[m1d].SetXTitle(axis_title_1d[mode][m1d])

    def get_bachelor(ind_x, ind_y):
        # A small function to get the bachelor particle index w.r.t the frst
        # param pair.
        # The first variable is for reference, and the second variable is
        # another dimention of dalitz variable.
        # e.g: m13 in X-axis and m23 in Y-axis. Looping among "2" and "3", the
        # index not appearing in "1,3" is the bachelor index w.r.t X-axis (that
        # is 2).
        for index in ind_y:
            if index not in ind_x:
                return index

    # draw boundaries
    def kine_max(x, par):
        m12 = sqrt(x[0])
        M, m1, m2, m3 = phsp[mode].m0, getattr(phsp[mode], "m"+xv[1]), getattr(
            phsp[mode], "m"+xv[2]), getattr(phsp[mode], "m"+get_bachelor(xv, yv))
        if m12 < m1+m2:
            m12 = m1 + m2 + 0.0000000001
        if m12 > M-m3:
            m12 = M - m3 - 0.0000000001
        E2st = 0.5 * (m12 * m12 - m1 * m1 + m2 * m2) / m12
        E3st = 0.5 * (M * M - m12 * m12 - m3 * m3) / m12
        mmax = (E2st + E3st) * (E2st + E3st) - \
            (sqrt(E2st * E2st - m2 * m2) - sqrt(E3st * E3st - m3 * m3))**2
        return mmax

    def kine_min(x, par):
        m12 = sqrt(x[0])
        M, m1, m2, m3 = phsp[mode].m0, getattr(phsp[mode], "m"+xv[1]), getattr(
            phsp[mode], "m"+xv[2]), getattr(phsp[mode], "m"+get_bachelor(xv, yv))
        if m12 < m1+m2:
            m12 = m1 + m2 + 0.0000000001
        if m12 > M-m3:
            m12 = M - m3 - 0.0000000001
        E2st = 0.5 * (m12 * m12 - m1 * m1 + m2 * m2) / m12
        E3st = 0.5 * (M * M - m12 * m12 - m3 * m3) / m12
        mmin = (E2st + E3st) * (E2st + E3st) - \
            (sqrt(E2st * E2st - m2 * m2) + sqrt(E3st * E3st - m3 * m3))**2
        return mmin

    fmax = TF1("fmax", kine_max, phsp[mode].lowerLimit(
        xv[1:]), phsp[mode].upperLimit(xv[1:]), 0)
    fmin = TF1("fmin", kine_min, phsp[mode].lowerLimit(
        xv[1:]), phsp[mode].upperLimit(xv[1:]), 0)
    fmax.SetLineColor(2)
    fmin.SetLineColor(2)
    fmax.SetNpx(100000)
    fmin.SetNpx(100000)

    if resonances:
        # TBC...
        '''
        mDs12700 = 2.714
        mDs12860 = 2.859
        mDs22573 = 2.569
        mDs3200 = 3.2
        mDs03200 = 3.05
        mX2900 = 2.9

        def funX2900(x, par):
            return m0**2+m1**2+m2**2+m3**2-mX2900**2-x[0]

        fX2900 = TF1("fX2900", funX2900, min13**2+0.5, max13**2-0.5, 0)
        fX2900.SetLineColor(ROOT.kRed)
        fX2900.Draw("same")

        ln = ROOT.TLine()
        ln.SetLineColor(ROOT.kRed)
        ln.DrawLine(mDs12700**2, fmin(mDs12700**2)+0.5,
                    mDs12700**2, fmax(mDs12700**2)-0.5)
        ln.DrawLine(mDs12860**2, fmin(mDs12860**2)+0.5,
                    mDs12860**2, fmax(mDs12860**2)-0.5)
        ln.DrawLine(mDs22573**2, fmin(mDs22573**2)+0.5,
                    mDs22573**2, fmax(mDs22573**2)-0.5)
        # ln.DrawLine(mDs03200**2,fmin(mDs03200**2)+0.5,mDs03200**2,fmax(mDs03200**2)-0.5)

        lt = ROOT.TLatex()
        lt.SetTextColor(ROOT.kRed)
        lt.SetTextSize(0.04)
        lt.SetTextFont(22)
        lt.DrawLatex(mDs12700**2-0.5, 15.5, "D_{s1}^{+}(2700)")
        lt.DrawLatex(mDs12860**2-0.5, 14.5, "D_{s1}^{+}(2860)")
        lt.DrawLatex(mDs22573**2-0.5, 16.5, "D_{s2}^{+}(2573)")
        # lt.DrawLatex(mDs03200**2+0.1,20.5,"D_{s0}^{+}(3200)")
        lt.DrawLatex(10, 15.5, "X(2900)")
        '''

    can = TCanvas("can_scatter", "", 800, 600)
    # can.SetRightMargin(0.13)
    hist["scatter"].Draw()
    fmax.Draw("same")
    fmin.Draw("same")
    can.Print(output_file_path+"/Dalitz2D_"+yv+"_"+xv+".pdf")
    for n in ["m12", "m13", "m23"]:
        can1d = TCanvas("can1d_"+n, "", 800, 600)
        hist[n].Draw()
        can1d.Print(output_file_path+"/data_"+n+".pdf")


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files', nargs='+',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree', help='Name of the tree')
    parser.add_argument('--output-file-path', help='Output file path')
    parser.add_argument('--mode', help='Mode name')
    parser.add_argument('--sw', help='Name of sw branch')
    parser.add_argument('--dalitz-vars', nargs="+",
                        default=["m12", "m13"], help='Name of Dalitz variables to draw. First var for Y-axis, second var for X-axis.')
    parser.add_argument('--resonances', nargs="+",
                        help="Resonances desired to be drawn.")
    args = parser.parse_args()
    drawDalitz(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
