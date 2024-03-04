import ROOT
from ROOT import TFile, TCanvas, TH1F
import sys, os
import subprocess
import math
import time




def ResultsExtractor(comp):
    filename="parameters/result_"
    #for res in resonance:
    #    filename+=res+"_"
    filename+=comp

    cmd="ls "+filename+ " > tmp.txt"
    #cmd="ls "+filename+"[0-9]*_6_* > tmp.txt"

    subprocess.Popen(cmd,shell=True)

    time.sleep(1)
    with open("tmp.txt", "r", encoding='UTF-8') as f:
        fpath=f.read()

    fpath=fpath.split('\n')[:-1]

    NLL={}
    nll=[]
    for path in fpath:
        with open(path,"r",encoding='UTF-8') as f:
            initseed=path[path.find("_",-27,-1)+1:-4]  #find the underline("_") before the initseed term
            #print(initseed)
            nll.append([float(i) for i in ( (((f.read()).split('\n'))[-2]).split(' ')[-2:]) ] )
            #print(nll)
            NLL[initseed]=nll[-1]


    xmin=min([nll[i][0] for i in range(len(nll))] )
    xmax=max([nll[i][0] for i in range(len(nll))] )
    print("%f  %f " %(xmin,xmax))
    nbins=10
    h=TH1F("h",filename,nbins,xmin-1,xmax+1)
    for initseed in NLL.keys():
        if NLL[initseed][1] !=  3:  # 3 is converged
            continue
        h.Fill(NLL[initseed][0])


    #c=TCanvas("c")
    #h.SetXTitle("nll")
    #h.Draw()

    out=[]
    out2=[]
    print("##### total fit: %d" %(len(NLL.keys())))
    print("#### converged fit: %d" %(h.GetEntries()))
    for i in NLL.keys():
        out.append([NLL[i][0],NLL[i][1],i])
    #print(sorted(nll))
    out.sort()

    for i in out:
        print("%f   %f  %s" %(i[0],i[1],i[2]))
    #subprocess.Popen("rm tmp.txt", shell=True)




if __name__=='__main__':
    #resonance = ["Dst02300", "Dst22460", "Dst12600", "Dst12640"]
    #resonance = ["Dst02300" ,"Dst22460", "Dst12600"]
    resonance = []
    for i in sys.argv[1:-1]:
        print(i)
        resonance.append(i)
    print(resonance)
    resonance.sort()

    comp=""
    for res in resonance:
        comp+=res+"_"
    comp+="[0-9]*"+sys.argv[-1]+"*"
    ResultsExtractor(comp)
