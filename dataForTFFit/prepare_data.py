import ROOT as rt
from ROOT import TChain, TFile, TTree, TList
from ROOT import RDataFrame as rdf

vars=["m12Sq", "m13Sq", "m23Sq", "m12", "m13", "m23", "cosHel12", "cosHel13", "cosHel23", "sig_sw", "B_PVF_M","pq13"]

filenames=["/home/zhoutw/workdir/B2DDbarpi/snakemake_chain/selection/output/massfit/data/B2D0D0pi2b2b/data_sw.root", "/home/zhoutw/workdir/B2DDbarpi/snakemake_chain/selection/output/massfit/data/B2D0D0pi2b4b_manual/data_sw.root"]
tr_list=TList()
i=0
for n in filenames:
    data = rdf("DecayTree", n)
    data = data.Filter("m13>2.1")
    data.Snapshot("DecayTree", "data_sw%i.root"%(i), vars)
    i+=1

    
    
