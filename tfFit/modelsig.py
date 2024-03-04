from ROOT import TMath, RooStats
import sys

delNLL=float(sys.argv[1])
deldof=int(sys.argv[2])
pvalue=TMath.Prob(delNLL*2,deldof)
sig=RooStats.PValueToSignificance(TMath.Prob(delNLL*2,deldof)/2)
print("p-value=%20f   significance=%f"%(pvalue,sig))
print(pvalue)
