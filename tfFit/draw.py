from ROOT import TH1F, TH2F, TCanvas, TFile, gStyle, gROOT, TMath, RDataFrame,gPad, TLatex, TH1D, TLine, TF1, TPad
import ROOT
from math import sqrt
gROOT.ProcessLine(".x ~/lhcbStyle.C")

import sys

"""
python3 draw.py toys/toy_Ds12700_Ds12860_Ds22573_NonRes0_449241858_5_14_22_12_
"""

m0=5.27925000 #B+
m1=1.86484000  #D0
m2=1.86486000 #D0bar
m3=0.13957018 #pi+

gROOT.SetBatch()

root=sys.argv[1]
allnames= root.replace(".root","").split("_")[1:-1]
print(allnames)
allnames=[nn if nn=="bkg" else nn for nn in allnames if not nn[0].isdigit()]
print(allnames)
bkktag=root.split("/")[1].replace(".root","").replace("toy_","")

min12,max12 = m1+m2, m0-m3
min13,max13 = m1+m3, m0-m2
min23,max23 = m2+m3, m0-m1

if len(sys.argv)>2:
    min12,max12 = float(sys.argv[2]), float(sys.argv[3])
    min23,max23 = float(sys.argv[4]), float(sys.argv[5])
    min13,max13 = float(sys.argv[6]), float(sys.argv[7])


min122=min12*min12
min132=min13*min13
min232=min23*min23
max122=max12*max12
max132=max13*max13
max232=max23*max23

margin=0.05
nbins=30
min12 = max(min12,m1+m2)
max12 = min(max12,m0-m3)
min13 = max(min13,m1+m3)
max13 = min(max13,m0-m2)
min23 = max(min23,m2+m3)
max23 = min(max23,m0-m1)


def draw(trs1,trs2,var,minV,maxV):
    h1=TH1D(var+"_d","",nbins,minV,maxV)
    h2=TH1D(var+"_t","",nbins,minV,maxV)
    htmp=TH1D(var+"_tmp","",nbins,minV,maxV)
    more_h={}
    print("1",allnames)
    for nn in allnames:
        more_h[nn] = TH1D(var+"_t"+nn,nn,nbins,minV,maxV)
    for key in trs1.keys():
        trs1[key].Draw(var+">>+"+h1.GetName(), "sig_sw")
        #wt1 = trs1[key].GetEntries()
        trs1[key].Draw(var+">>"+htmp.GetName(), "sig_sw")
        wt1 = htmp.Integral()
        wt2 = trs2[key].GetEntries()
        if var[0] == "m" and var[-2:]!="Sq": var = "sqrt(%sSq)"%(var,)
        #if var[-2:]=="Sq":    var="m12Sq"
        trs2[key].Draw(var+">>+"+h2.GetName(),"%f*wAll"%(1.*wt1/wt2,))
        for nn in allnames:
            ww="w"+nn+"_"+nn
            trs2[key].Draw(var+">>+"+more_h[nn].GetName(),"%f*%s"%(1.*wt1/wt2,ww))
        """
        for evt in trs1[key]: h1.Fill(getattr(evt,var))
        for evt in trs2[key]: 
            h2.Fill(getattr(evt,var),wt1/wt2*getattr(evt,"wAll"))
            for nn in allnames:
                ww="w"+nn+"_"+nn
                more_h[nn].Fill(getattr(evt,var),wt1/wt2*getattr(evt,ww))
        """
    return (h1,h2,more_h)


tmp={}
trD={}
tmp2={}
trT={}

tmp["ALL"]= TFile("/home/zhoutw/workdir/B2DDbarpi/snakemake_chain/dataForTFFit/data_sw.root","r")
trD["ALL"] = tmp["ALL"].Get("DecayTree")

tmp2["ALL"]=TFile(root+"%s.root"%("ALL",))
trT["ALL"] = tmp2["ALL"].Get("toy")



cosHel12 = draw(trD,trT,"cosHel12",-1,1)
cosHel13 = draw(trD,trT,"cosHel13",-1,1)
cosHel23 = draw(trD,trT,"cosHel23",-1,1)
m12    = draw(trD,trT,"m12",min12,max12)
m13    = draw(trD,trT,"m13",min13,max13)
m23    = draw(trD,trT,"m23",min23,max23)
m12Sq    = draw(trD,trT,"m12Sq",min122,max122)
m13Sq    = draw(trD,trT,"m13Sq",min132,max132)
m23Sq    = draw(trD,trT,"m23Sq",min232,max232)


print("####: drawing")
from ROOT import kBlack, kRed, kBlue, kGreen, kCyan, kYellow, kMagenta
colors=[49,kBlue+1, kGreen+2, kCyan+1, kMagenta+1,38,39,46, 48, kRed-9]   
for hhs in [cosHel12[2],cosHel13[2],cosHel23[2],m12[2],m13[2],m23[2],m12Sq[2],m13Sq[2],m23Sq[2]]:
    for ii in range(len(allnames)):
        hhs[allnames[ii]].SetLineColor(colors[ii])
        hhs[allnames[ii]].SetMarkerColor(colors[ii])
        hhs[allnames[ii]].SetMarkerStyle(20+ii)

m12[0].SetXTitle("m_{D^{0}#bar{D}^{0}} [GeV]"    )
m13[0].SetXTitle("m_{D^{0}#pi^{+}} [GeV]")
m23[0].SetXTitle("m_{#bar{D}^{0}#pi^{+}} [GeV]")
cosHel12[0].SetXTitle("cos#theta_{D^{0}#bar{D}^{0}}"    )
cosHel13[0].SetXTitle("cos#theta_{D^{0}#pi^{+}}")
cosHel23[0].SetXTitle("cos#theta_{#bar{D}^{0}#pi^{+}}")
m12Sq[0].SetXTitle("m^{2}_{D^{0}#bar{D}^{0}} [GeV]"    )
m13Sq[0].SetXTitle("m^{2}_{D^{0}#pi^{+}} [GeV]")
m23Sq[0].SetXTitle("m^{2}_{#bar{D}^{0}#pi^{+}} [GeV]")

cosHel12[1].SetLineColor(2)
cosHel13[1].SetLineColor(2)
cosHel23[1].SetLineColor(2)
m12   [1].SetLineColor(2)
m13   [1].SetLineColor(2)
m23   [1].SetLineColor(2)
m12Sq   [1].SetLineColor(2)
m13Sq   [1].SetLineColor(2)
m23Sq   [1].SetLineColor(2)
cosHel12[1].SetMarkerColor(2)
cosHel13[1].SetMarkerColor(2)
cosHel23[1].SetMarkerColor(2)
m12   [1].SetMarkerColor(2)
m13   [1].SetMarkerColor(2)
m23   [1].SetMarkerColor(2)
m12Sq   [1].SetMarkerColor(2)
m13Sq   [1].SetMarkerColor(2)
m23Sq   [1].SetMarkerColor(2)
cosHel12[1].SetMarkerStyle(24)
cosHel13[1].SetMarkerStyle(24)
cosHel23[1].SetMarkerStyle(24)
m12   [1].SetMarkerStyle(24)
m13   [1].SetMarkerStyle(24)
m23   [1].SetMarkerStyle(24)
m12Sq   [1].SetMarkerStyle(24)
m13Sq   [1].SetMarkerStyle(24)
m23Sq   [1].SetMarkerStyle(24)

legend=ROOT.TLegend(0.3,0.0,0.9,1.0)
legend.SetTextFont(132)
legend.SetTextSize(0.06)
legend.SetLineWidth(3)
def drawall(hhs,leg=False):
    h0,h1,hh=hhs
    global legend
    can=TCanvas("c"+h0.GetName(),"",600,550)
    can.cd()
    pad1=TPad("pad1"+h0.GetName(),"",0.0,0.27,1,1.0)
    pad1.SetBottomMargin(0.02)
    pad1.Draw()
    pad1.cd()

    scale = h0.Integral()/h1.Integral()
    h0.Draw("e")
    h0.SetMinimum(0.)
    h0.SetMaximum(h0.GetMaximum()*1.2)
    #h1.Scale(scale);
    h1.Draw("same,hist")
    if leg: legend.AddEntry(h0,"Data","LPE")
    if leg: legend.AddEntry(h1,"Fit","L")
    for h in hh:
        #h.Scale(scale);
        hh[h].Draw("same,hist")
        if leg: 
            legend.AddEntry(hh[h],"Fit "+hh[h].GetTitle(),"L")

    # draw pull for this variable distribution
    can.cd()
    pad2=TPad("pad2"+h0.GetName(),"",0.0,0.0,1,0.25)
    pad2.SetTopMargin(0.07) #0.07
    pad2.SetBottomMargin(0.55)

    pad2.Draw()
    pad2.cd()
    hpull=TH1F("pull"+h0.GetName(),"",h0.GetNbinsX(), h0.GetBinLowEdge(1), h0.GetBinLowEdge(1)+h0.GetNbinsX()*h0.GetBinWidth(1))
    hpull.SetFillColor(1)
    hpull.GetXaxis().SetTitle(h0.GetXaxis().GetTitle())
    hpull.GetYaxis().SetTitle("pull")
    hpull.GetYaxis().SetRangeUser(-5,5)
    hpull.GetXaxis().SetTitleSize(0.2) #0.15
    hpull.GetXaxis().SetTitleOffset(1.10)
    hpull.GetXaxis().SetLabelSize(0.15)
    hpull.GetYaxis().SetTitleSize(0.2)
    hpull.GetYaxis().SetTitleOffset(0.22)
    hpull.GetYaxis().SetNdivisions(502)
    hpull.GetYaxis().SetLabelSize(0.15)
    #hpull.GetXaxis().CenterTitle()
    hpull.GetYaxis().CenterTitle()

    for i in range(h0.GetNbinsX()):
        if h0.GetBinError(i+1)==0:
            err=0
        else:
            err=(h0.GetBinContent(i+1)-h1.GetBinContent(i+1))/h0.GetBinError(i+1)
        hpull.SetBinContent(i+1, err)

    hpull.Draw("BX")

    can.Print("pdf/%s_%s.pdf"%(bkktag,h0.GetName()))


drawall(cosHel12,1)
canx=TCanvas("canx","",600,500)
canx.cd()
legend.Draw()
canx.Print("pdf/B2D0D0pi_%s_LEGEND.pdf"%(bkktag,))


drawall(cosHel13)
drawall(cosHel23)
drawall(m12)
drawall(m13)
drawall(m23)

#drawall(m12Sq)
#drawall(m13Sq)
#drawall(m23Sq)




'''
from chi2 import bins, poly2Data, poly2Toy, poly2Pull
scatterData=ROOT.TH2D("scatterData","scatter",nbins,min13**2,max13**2,nbins,min12**2,max12**2)
scatterData.SetMarkerStyle(6)
def draw2D(trs1,trs2,minV,maxV):
    for key in trs1.keys():
        htmp1=TH1D("htmp1","",nbins,minV,maxV)
        htmp2=TH1D("htmp2","",nbins,minV,maxV)
        trs1[key].Draw("m23>>"+htmp1.GetName())
        trs2[key].Draw("sqrt(m23Sq)>>"+htmp2.GetName(),"wAll")
        wt=1.*htmp1.Integral()/htmp2.Integral()
        for evt in trs1[key]:
            poly2Data.Fill(evt.m13Sq,evt.m12Sq)
            scatterData.Fill(evt.m13Sq,evt.m12Sq)
        for evt in trs2[key]:
            poly2Toy.Fill(evt.m13Sq,evt.m12Sq,evt.wAll*wt)

        #trs1[key].Draw("m12Sq:m13Sq>>+"+poly2Data.GetName())
        #trs2[key].Draw("m12Sq:m13Sq>>+"+poly2Toy.GetName(),"%f*wAll"%(wt,))
draw2D(trD,trT,min23,max23)


def kine_max(x,par):
    m12=sqrt(x[0])

    M, m1, m2, m3 = m0, mK0, mDp, mD0

    if m12<m1+m2:
        m12 = m1 + m2 + 0.0000000001
    if m12>M-m3:
        m12 = M - m3 - 0.0000000001
    E2st = 0.5 * (m12 * m12 - m1 * m1 + m2 * m2) / m12
    E3st = 0.5 * (M * M - m12 * m12 - m3 * m3) / m12
    mmax = (E2st + E3st) * (E2st + E3st) - (sqrt(E2st * E2st - m2 * m2) - sqrt(E3st * E3st - m3 * m3))**2
    return mmax


def kine_min(x,par):
    m12=sqrt(x[0])

    M, m1, m2, m3 = m0, mK0, mDp, mD0

    if m12<m1+m2:
        m12 = m1 + m2 + 0.0000000001
    if m12>M-m3:
        m12 = M - m3 - 0.0000000001

    E2st = 0.5 * (m12 * m12 - m1 * m1 + m2 * m2) / m12
    E3st = 0.5 * (M * M - m12 * m12 - m3 * m3) / m12
    mmin = (E2st + E3st) * (E2st + E3st) - (sqrt(E2st * E2st - m2 * m2) + sqrt(E3st * E3st - m3 * m3))**2
    return mmin

    
    

# draw boundaries
#fmax = TF1("fmax",kine_max,min13**2,max13**2,0)
#fmin = TF1("fmin",kine_min,min13**2,max13**2,0)
#fmax.SetLineColor(2)
#fmin.SetLineColor(2)



#data
ln=TLine()
ln.SetLineWidth(1)
can=TCanvas("can","",600,450)
can.SetRightMargin(0.16)
poly2Data.Draw("colz")
scatterData.Draw("same")
#fmin.Draw("same")
#fmax.Draw("same")
poly2Data.SetXTitle("m^{2}_{D^{0}#pi^{+}} [GeV^{2}]")
poly2Data.SetYTitle("m^{2}_{D^{0}#bar{D}^{0}} [GeV^{2}]")
poly2Data.SetMinimum(0)
poly2Data.SetMaximum(200)
for bb in bins:
    xl,xh,yl,yh=bb
    ln.DrawLine(xl,yl,xh,yl)
    ln.DrawLine(xl,yl,xl,yh)
    ln.DrawLine(xl,yh,xh,yh)
    ln.DrawLine(xh,yl,xh,yh)
can.SaveAs("pdf/%s-adaptiveData.pdf"%(bkktag,))
#for ii in range(len(bins)):
#    print(poly2Data.GetBinContent(ii))


#####toys
can=TCanvas("can","",600,450)
can.SetRightMargin(0.16)
poly2Toy.Draw("colz")
poly2Toy.SetXTitle("m^{2}_{D^{0}#pi^{+}} [GeV^{2}]")
poly2Toy.SetYTitle("m^{2}_{D^{0}#bar{D}^{0}} [GeV^{2}]")
poly2Toy.SetMinimum(0)
for bb in bins:
    xl,xh,yl,yh=bb
    ln.DrawLine(xl,yl,xh,yl)
    ln.DrawLine(xl,yl,xl,yh)
    ln.DrawLine(xl,yh,xh,yh)
    ln.DrawLine(xh,yl,xh,yh)
can.SaveAs("pdf/%s-adaptiveToy.pdf"%(bkktag,))

#####pulls
can=TCanvas("can","",600,450)
can.SetRightMargin(0.16)
scale = 1.*poly2Data.Integral()/poly2Toy.Integral()
pullsum=0
for ii in range(1,len(bins)+1):
    a=poly2Toy.GetBinContent(ii)*scale
    b=poly2Data.GetBinContent(ii)
    poly2Pull.SetBinContent(ii,(a-b)/sqrt(a))
    pullsum+=((a-b)/sqrt(a))**2
    print(a,b,(a-b)/sqrt(a))
poly2Pull.Draw("colz")
poly2Pull.SetXTitle("m^{2}_{D^{0}#pi^{+}} [GeV^{2}]")
poly2Pull.SetYTitle("m^{2}_{D^{0}#bar{D}^{0}} [GeV^{2}]")
poly2Pull.SetMinimum(-5)
poly2Pull.SetMaximum(+5)
for bb in bins:
    xl,xh,yl,yh=bb
    ln.DrawLine(xl,yl,xh,yl)
    ln.DrawLine(xl,yl,xl,yh)
    ln.DrawLine(xl,yh,xh,yh)
    ln.DrawLine(xh,yl,xh,yh)
can.SaveAs("pdf/%s-pull.pdf"%(bkktag,))

nbinspoly=poly2Data.GetBins().GetSize()
print(f"sum of pull = {pullsum}, nbins= {nbinspoly}")

'''

