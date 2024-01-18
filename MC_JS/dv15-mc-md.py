#### For B->DDbarpi 
from os import environ
from GaudiKernel.SystemOfUnits import *
from Gaudi.Configuration import *
from Configurables import GaudiSequencer, CombineParticles
from Configurables import DecayTreeTuple, EventTuple, TupleToolTrigger, TupleToolTISTOS,FilterDesktop
from Configurables import BackgroundCategory, TupleToolDecay, TupleToolVtxIsoln,TupleToolPid,EventCountHisto,TupleToolRecoStats,TupleToolDecayTreeFitter,SubstitutePID
from Configurables import LoKi__Hybrid__TupleTool, TupleToolVeto,TriggerTisTos
from DecayTreeTuple.Configuration import *
from PhysConf.Selections import AutomaticData, MomentumScaling, TupleSelection,SelectionSequence
# Unit
#http://lhcbdoc.web.cern.ch/lhcbdoc/stripping/
#Find the latest stripping version for each year that have B2D0DKSDDBeauty2CharmLine, for example, for 2018 it is striping 34
conf_mc_mdst_restrip={
        "year":"2015",
        "stripping":"stripping24r2",
        "condb":"sim-20161124-vc-%s100",
        "dddb":'dddb-20170721-3',
        "polarity":'md'
        }
the_year = conf_mc_mdst_restrip['year']

mtl= [
        "L0HadronDecision",
        "L0PhotonDecision",
        "L0MuonDecision",
        "L0ElectronDecision",
        "L0DiMuonDecision",

        "Hlt1TrackMVADecision",
        "Hlt1TwoTrackMVADecision",
        "Hlt1TrackAllL0Decision",

        "Hlt2Topo2BodyDecision",
        "Hlt2Topo3BodyDecision",
        "Hlt2Topo4BodyDecision",
]

from Configurables import BackgroundCategory, TupleToolDecay, TupleToolVtxIsoln,TupleToolPid,EventCountHisto,TupleToolRecoStats,TupleToolDecayTreeFitter,TupleToolMCTruth

MCTruth = TupleToolMCTruth() 
MCTruth.ToolList = [ 	"MCTupleToolKinematic" , 	"MCTupleToolHierarchy" ]
#

########### ########### ###########
ttl= [ "TupleToolKinematic", "TupleToolPid" ,"TupleToolTrackInfo","TupleToolDira"  ,"TupleToolPrimaries" ,"TupleToolPropertime","TupleToolEventInfo" ,"TupleToolRecoStats","TupleToolGeometry","TupleToolL0Calo","TupleToolMCTruth" ,"TupleToolMCBackgroundInfo","TupleToolL0Data"]
dtts=[]
flts=[]
mct=[]

loc="Phys/B2DDPiBeauty2CharmLine/Particles"
FltB2DdDdPi= FilterDesktop("FltB2DdDdPi")
FltB2DdDdPi.Code = "(INTREE((ID=='D+')&(M<1949.61)&(M>1789.61)))&(INTREE((ID=='D-')&(M<1949.61)&(M>1789.61)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2DdDdPi.Inputs = [loc]
FltB2DdDdPi.Output= "Phys/FltB2DdDdPi/Particles" 
flts.append(FltB2DdDdPi)

dtts.append(DecayTreeTuple("B2DdDdPi"))
dtts[-1].Inputs = ["Phys/FltB2DdDdPi/Particles"]
dtts[-1].Decay = "[B+ -> ^(D+ -> ^K- ^pi+ ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^pi+]CC" 
dtts[-1].Branches = {
        "B"        :"[B+ -> (D+ -> K- pi+ pi+) (D- -> K+ pi- pi-) pi+]CC", 
        "BH"       :"[B+ -> (D+ -> K- pi+ pi+) (D- -> K+ pi- pi-) ^pi+]CC", 
        "D1"       :"[B+ -> ^(D+ -> K- pi+ pi+) (D- -> K+ pi- pi-) pi+]CC", 
        "D1K"       :"[B+ -> (D+ -> ^K- pi+ pi+) (D- -> K+ pi- pi-) pi+]CC", 
        "D1H"       :"[B+ -> (D+ -> K- ^pi+ pi+) (D- -> K+ pi- pi-) pi+]CC", 
        "D1h"       :"[B+ -> (D+ -> K- pi+ ^pi+) (D- -> K+ pi- pi-) pi+]CC", 
        "D2"       :"[B+ -> (D+ -> K- pi+ pi+) ^(D- -> K+ pi- pi-) pi+]CC", 
        "D2K"       :"[B+ -> (D+ -> K- pi+ pi+) (D- -> ^K+ pi- pi-) pi+]CC", 
        "D2H"       :"[B+ -> (D+ -> K- pi+ pi+) (D- -> K+ ^pi- pi-) pi+]CC", 
        "D2h"       :"[B+ -> (D+ -> K- pi+ pi+) (D- -> K+ pi- ^pi-) pi+]CC", 
    }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D+","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D+"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True


#------------------->>>>>>>>>
loc="Phys/B2DstDPiBeauty2CharmLine/Particles"
FltB2DstDdPi2b= FilterDesktop("FltB2DstDdPi2b")
FltB2DstDdPi2b.Code = "(INTREE(('D*(2010)+'==ABSID)&(M<2050.26)&(M>1970.26)))&(INTREE(('D+'==ABSID)&(M<1949.61)&(M>1789.61)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2DstDdPi2b.Inputs = [loc]
FltB2DstDdPi2b.Output= "Phys/FltB2DstDdPi2b/Particles" 
flts.append(FltB2DstDdPi2b)

dtts.append(DecayTreeTuple("B2DstDdPi2b"))
dtts[-1].Inputs = ["Phys/FltB2DstDdPi2b/Particles"]
dtts[-1].Decay = "[Beauty -> ^(D*(2010)+ -> ^(Charm -> ^K- ^pi+) ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^X]CC" 
dtts[-1].Branches = {
            "B"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D- -> K+ pi- pi-) X]CC", 
            "BH"       :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D- -> K+ pi- pi-) ^X]CC", 
            "Dst"       :"[Beauty -> ^(D*(2010)+ -> (Charm -> K- pi+) pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0"     :"[Beauty -> (D*(2010)+ -> ^(Charm -> K- pi+) pi+) (D- -> K+ pi- pi-) X]CC",      
            "DstH"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) ^pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0K"    :"[Beauty -> (D*(2010)+ -> (Charm -> ^K- pi+) pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0H"    :"[Beauty -> (D*(2010)+ -> (Charm -> K- ^pi+) pi+) (D- -> K+ pi- pi-) X]CC", 
            "Dd"       :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) ^(D- -> K+ pi- pi-) X]CC", 
            "DdK"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D- -> ^K+ pi- pi-) X]CC", 
            "DdH"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D- -> K+ ^pi- pi-) X]CC", 
            "Ddh"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D- -> K+ pi- ^pi-) X]CC", 
    }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D+","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D+"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True



##############################
loc="Phys/B2DstDPiDstarD02K3PiBeauty2CharmLine/Particles"
FltB2DstDdPi4b= FilterDesktop("FltB2DstDdPi4b")
FltB2DstDdPi4b.Code = "(INTREE(('D*(2010)+'==ABSID)&(M<2050.26)&(M>1970.26)))&(INTREE(('D+'==ABSID)&(M<1949.61)&(M>1789.61)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(7==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2DstDdPi4b.Inputs = [loc]
FltB2DstDdPi4b.Output= "Phys/FltB2DstDdPi4b/Particles" 
flts.append(FltB2DstDdPi4b)


dtts.append(DecayTreeTuple("B2DstDdPi4b"))
dtts[-1].Inputs = ["Phys/FltB2DstDdPi4b/Particles"]
dtts[-1].Decay = "[Beauty -> ^(D*(2010)+ -> ^(Charm -> ^K- ^pi+ ^pi+ ^pi-) ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^X]CC" 
dtts[-1].Branches = {
            "B"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) (D- -> K+ pi- pi-) X]CC", 
            "BH"       :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) (D- -> K+ pi- pi-) ^X]CC", 
            "Dst"       :"[Beauty -> ^(D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0"     :"[Beauty -> (D*(2010)+ -> ^(Charm -> K- pi+ pi+ pi-) pi+) (D- -> K+ pi- pi-) X]CC",      
            "DstH"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) ^pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0K"    :"[Beauty -> (D*(2010)+ -> (Charm -> ^K- pi+ pi+ pi-) pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0Hm"    :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ ^pi-) pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0Hp1"    :"[Beauty -> (D*(2010)+ -> (Charm -> K- ^pi+ pi+ pi-) pi+) (D- -> K+ pi- pi-) X]CC", 
            "DstD0Hp2"    :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ ^pi+ pi-) pi+) (D- -> K+ pi- pi-) X]CC", 
            "Dd"       :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) ^(D- -> K+ pi- pi-) X]CC", 
            "DdK"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) (D- -> ^K+ pi- pi-) X]CC", 
            "DdH"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) (D- -> K+ ^pi- pi-) X]CC", 
            "Ddh"      :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+ pi+ pi-) pi+) (D- -> K+ pi- ^pi-) X]CC", 
            }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D+","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D+"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True


##############################
loc="Phys/B2D0D0PiD02HHD02HHBeauty2CharmLine/Particles"
FltB2D0D0Pi2b2b= FilterDesktop("FltB2D0D0Pi2b2b")
FltB2D0D0Pi2b2b.Code = "(2==NINTREE(('D0'==ABSID)&(M<1944.83)&(M>1784.83)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(3==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2D0D0Pi2b2b.Inputs = [loc]
FltB2D0D0Pi2b2b.Output= "Phys/FltB2D0D0Pi2b2b/Particles" 
flts.append(FltB2D0D0Pi2b2b)


dtts.append(DecayTreeTuple("B2D0D0Pi2b2b"))
dtts[-1].Inputs = ["Phys/FltB2D0D0Pi2b2b/Particles"]
dtts[-1].Decay = "[B+ -> ^(Charm -> ^K- ^pi+ ) ^(Charm -> ^K+ ^pi- ) ^pi+]CC"
dtts[-1].Branches = {
            "B"        :"[B+ -> (Charm -> K- pi+ ) (Charm -> K+ pi- ) pi+]CC",
            "BH"       :"[B+ -> (Charm -> K- pi+ ) (Charm -> K+ pi- ) ^pi+]CC",
            "D1"       :"[B+ -> ^(Charm -> K- pi+ ) (Charm -> K+ pi- ) pi+]CC",
            "D1K"       :"[B+ -> (Charm -> ^K- pi+) (Charm -> K+ pi- ) pi+]CC",
            "D1H"       :"[B+ -> (Charm -> K- ^pi+) (Charm -> K+ pi- ) pi+]CC",
            "D2"        :"[B+ -> (Charm -> K- pi+) ^(Charm -> K+ pi- ) pi+]CC",
            "D2K"       :"[B+ -> (Charm -> K- pi+) (Charm -> ^K+ pi- ) pi+]CC",
            "D2H"       :"[B+ -> (Charm -> K- pi+) (Charm -> K+ ^pi- ) pi+]CC",
            }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D0"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D0"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True

'''
##############################
loc="Phys/B2D0D0PiD02HHD02K3PiBeauty2CharmLine/Particles"
FltB2D0D0Pi2b4b= FilterDesktop("FltB2D0D0Pi2b4b")
FltB2D0D0Pi2b4b.Code = "(2==NINTREE(('D0'==ABSID)&(M<1944.83)&(M>1784.83)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2D0D0Pi2b4b.Inputs = [loc]
FltB2D0D0Pi2b4b.Output= "Phys/FltB2D0D0Pi2b4b/Particles" 
flts.append(FltB2D0D0Pi2b4b)


subIDB2D0D0Pi2b4b= SubstitutePID("subIDB2D0D0Pi2b4b",
        Code = "DECTREE('[B+ -> Charm Charm pi+]CC')",
        Substitutions={
            "B+ -> (Charm -> K- pi+) ^(Charm -> K+ pi- pi- pi+) pi+":  "Lambda_c~-",
            "B- -> (Charm -> K+ pi-) ^(Charm -> K- pi+ pi+ pi-) pi-":  "Lambda_c+",
            "B- -> (Charm -> K- pi+) ^(Charm -> K+ pi- pi- pi+) pi-":  "Lambda_c~-",
            "B+ -> (Charm -> K+ pi-) ^(Charm -> K- pi+ pi+ pi-) pi+":  "Lambda_c+",
           }
        )
subIDB2D0D0Pi2b4b.Inputs =  ["Phys/FltB2D0D0Pi2b4b/Particles"]
flts.append(subIDB2D0D0Pi2b4b)

dtts.append(DecayTreeTuple("B2D0D0Pi2b4b"))
dtts[-1].Inputs = ["Phys/subIDB2D0D0Pi2b4b/Particles"]
dtts[-1].Decay = "[Beauty -> ^(Charm -> ^K- ^pi+) ^(Charm -> ^K+ ^pi- ^pi+ ^pi-) ^X]CC"
dtts[-1].Branches = {
            "B"        :"[Beauty -> (Charm -> K- pi+) (Charm -> K+ pi- pi+ pi-) X]CC" ,
            "BH"       :"[Beauty -> (Charm -> K- pi+) (Charm -> K+ pi- pi+ pi-) ^X]CC",
            "D2b"       :"[Beauty -> ^(Charm -> K- pi+) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D2bK"      :"[Beauty -> (Charm -> ^K- pi+) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D2bH"      :"[Beauty -> (Charm -> K- ^pi+) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D4b"       :"[Beauty -> (Charm -> K- pi+) ^(Charm -> K+ pi- pi+ pi-) X]CC",
            "D4bK"      :"[Beauty -> (Charm -> K- pi+) (Charm -> ^K+ pi- pi+ pi-) X]CC",
            "D4bHm1"    :"[Beauty -> (Charm -> K- pi+) (Charm -> K+ ^pi- pi+ pi-) X]CC",
            "D4bHp"     :"[Beauty -> (Charm -> K- pi+) (Charm -> K+ pi- ^pi+ pi-) X]CC",
            "D4bHm2"    :"[Beauty -> (Charm -> K- pi+) (Charm -> K+ pi- pi+ ^pi-) X]CC",
            }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D0","Lambda_c+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D0","Lambda_c+"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True

'''
##############################
loc="Phys/B2D0D0PiD02K3PiD02K3PiBeauty2CharmLine/Particles"
FltB2D0D0Pi4b4b= FilterDesktop("FltB2D0D0Pi4b4b")
FltB2D0D0Pi4b4b.Code = "(2==NINTREE(('D0'==ABSID)&(M<1944.83)&(M>1784.83)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(7==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2D0D0Pi4b4b.Inputs = [loc]
FltB2D0D0Pi4b4b.Output= "Phys/FltB2D0D0Pi4b4b/Particles" 
flts.append(FltB2D0D0Pi4b4b)


dtts.append(DecayTreeTuple("B2D0D0Pi4b4b"))
dtts[-1].Inputs = ["Phys/FltB2D0D0Pi4b4b/Particles"]
dtts[-1].Decay = "[Beauty -> ^(Charm -> ^K- ^pi+ ^pi+ ^pi-) ^(Charm -> ^K+ ^pi- ^pi+ ^pi-) ^X]CC"
dtts[-1].Branches = {
            "B"        :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC" ,
            "BH"       :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) ^X]CC",
            "D1"       :"[Beauty -> ^(Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1K"      :"[Beauty -> (Charm -> ^K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1Hp1"    :"[Beauty -> (Charm -> K- ^pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1Hm"     :"[Beauty -> (Charm -> K- pi+ pi+ ^pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1Hp2"    :"[Beauty -> (Charm -> K- pi+ ^pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D2"       :"[Beauty -> (Charm -> K- pi+ pi+ pi-) ^(Charm -> K+ pi- pi+ pi-) X]CC",
            "D2K"      :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> ^K+ pi- pi+ pi-) X]CC",
            "D2Hm1"    :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ ^pi- pi+ pi-) X]CC",
            "D2Hp"     :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- ^pi+ pi-) X]CC",
            "D2Hm2"    :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ ^pi-) X]CC",
            }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D0"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D0"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True


##############################

loc="Phys/B2DstDstPiBeauty2CharmLine/Particles"
FltB2DstDstPi2b2b= FilterDesktop("FltB2DstDstPi2b2b")
FltB2DstDstPi2b2b.Code = "(2==NINTREE(('D*(2010)+'==ABSID)&(M<2050.26)&(M>1970.26))) & (1==NINTREE(('K+'==ID)  & ( PROBNNk>-0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>-0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>-0.05)))"
FltB2DstDstPi2b2b.Inputs = [loc]
FltB2DstDstPi2b2b.Output= "Phys/FltB2DstDstPi2b2b/Particles" 
flts.append(FltB2DstDstPi2b2b)


dtts.append(DecayTreeTuple("B2DstDstPi2b2b"))
dtts[-1].Inputs = ["Phys/FltB2DstDstPi2b2b/Particles"]
dtts[-1].Decay = "[Beauty -> ^(D*(2010)+ -> ^(Charm -> ^K- ^pi+) ^pi+) ^(D*(2010)- -> ^(Charm -> ^K+ ^pi-) ^pi-) ^X]CC"
dtts[-1].Branches = {
            "B"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "BH"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) ^X]CC", 
            "Dst1"        :"[Beauty -> ^(D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "Dst1D0"        :"[Beauty -> (D*(2010)+ -> ^(Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "Dst1H"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) ^pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "Dst1D0K"        :"[Beauty -> (D*(2010)+ -> (Charm -> ^K- pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "Dst1D0H"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- ^pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "Dst2"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) ^(D*(2010)- -> (Charm -> K+ pi-) pi-) X]CC", 
            "Dst2D0"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> ^(Charm -> K+ pi-) pi-) X]CC", 
            "Dst2H"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> K+ pi-) ^pi-) X]CC", 
            "Dst2D0K"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> ^K+ pi-) pi-) X]CC", 
            "Dst2D0H"        :"[Beauty -> (D*(2010)+ -> (Charm -> K- pi+) pi+) (D*(2010)- -> (Charm -> K+ ^pi-) pi-) X]CC", 
            }


dtts[-1].addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB"))
dtts[-1].B.PVFitB.Verbose = True
dtts[-1].B.PVFitB.UpdateDaughters= True
dtts[-1].B.PVFitB.constrainToOriginVertex = True
dtts[-1].B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitD"))
dtts[-1].B.PVFitD.Verbose = True
dtts[-1].B.PVFitD.UpdateDaughters= True
dtts[-1].B.PVFitD.constrainToOriginVertex = True
dtts[-1].B.PVFitD.daughtersToConstrain = ["D0"]
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
dtts[-1].B.PVFitB2DDK.Verbose = True
dtts[-1].B.PVFitB2DDK.UpdateDaughters= True
dtts[-1].B.PVFitB2DDK.constrainToOriginVertex = True
dtts[-1].B.PVFitB2DDK.daughtersToConstrain = ["D0"]
dtts[-1].B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
dtts[-1].B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
dtts[-1].B.addTool(TupleToolDecayTreeFitter("PVFit"))
dtts[-1].B.PVFit.Verbose = True
dtts[-1].B.PVFit.UpdateDaughters= True
dtts[-1].B.PVFit.constrainToOriginVertex = True



for i in dtts:
    i.ToolList += ttl
    i.addTool(MCTruth)

    i.ToolList+=[ "TupleToolTISTOS" ]
    i.addTool(TupleToolTISTOS, name="TupleToolTISTOS" )
    i.TupleToolTISTOS.Verbose=True
    i.TupleToolTISTOS.VerboseHlt1=True
    i.TupleToolTISTOS.VerboseHlt2=True
    i.TupleToolTISTOS.TriggerList = mtl



MessageSvc().Format = "% F%60W%S%7W%R%T %0W%M"

######################################################
mct.append(MCDecayTreeTuple("mctB2DdDdPi"))
mct[-1].Decay = "[Beauty => ^(D+ ==> ^K- ^pi+ ^pi+) ^(D- ==> ^K+ ^pi- ^pi-) ^pi+]CC" 
mct[-1].Branches = {
        "B"        :"[B+ => (D+ => K- pi+ pi+) (D- => K+ pi- pi-) pi+]CC", 
        "BH"       :"[B+ => (D+ => K- pi+ pi+) (D- => K+ pi- pi-) ^pi+]CC", 
        "D1"       :"[B+ => ^(D+ => K- pi+ pi+) (D- => K+ pi- pi-) pi+]CC", 
        "D1K"       :"[B+ => (D+ => ^K- pi+ pi+) (D- => K+ pi- pi-) pi+]CC", 
        "D1H"       :"[B+ => (D+ => K- ^pi+ pi+) (D- => K+ pi- pi-) pi+]CC", 
        "D1h"       :"[B+ => (D+ => K- pi+ ^pi+) (D- => K+ pi- pi-) pi+]CC", 
        "D2"       :"[B+ => (D+ => K- pi+ pi+) ^(D- => K+ pi- pi-) pi+]CC", 
        "D2K"       :"[B+ => (D+ => K- pi+ pi+) (D- => ^K+ pi- pi-) pi+]CC", 
        "D2H"       :"[B+ => (D+ => K- pi+ pi+) (D- => K+ ^pi- pi-) pi+]CC", 
        "D2h"       :"[B+ => (D+ => K- pi+ pi+) (D- => K+ pi- ^pi-) pi+]CC", 
            }
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']

######################################################
mct.append(MCDecayTreeTuple("mctB2DstDdPi2b"))
mct[-1].Decay = "[Beauty => ^(D*(2010)+ => ^(Charm => ^K- ^pi+) ^pi+) ^(D- => ^K+ ^pi- ^pi-) ^X]CC" 
mct[-1].Branches = {
            "B"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D- => K+ pi- pi-) X]CC", 
            "BH"       :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D- => K+ pi- pi-) ^X]CC", 
            "Dst"       :"[Beauty => ^(D*(2010)+ => (Charm => K- pi+) pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0"     :"[Beauty => (D*(2010)+ => ^(Charm => K- pi+) pi+) (D- => K+ pi- pi-) X]CC",      
            "DstH"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+) ^pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0K"    :"[Beauty => (D*(2010)+ => (Charm => ^K- pi+) pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0H"    :"[Beauty => (D*(2010)+ => (Charm => K- ^pi+) pi+) (D- => K+ pi- pi-) X]CC", 
            "Dd"       :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) ^(D- => K+ pi- pi-) X]CC", 
            "DdK"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D- => ^K+ pi- pi-) X]CC", 
            "DdH"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D- => K+ ^pi- pi-) X]CC", 
            "Ddh"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D- => K+ pi- ^pi-) X]CC", 
    }
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']



mct.append(MCDecayTreeTuple("mctB2DstDdPi4b"))
mct[-1].Decay = "[Beauty => ^(D*(2010)+ => ^(Charm => ^K- ^pi+ ^pi+ ^pi-) ^pi+) ^(D- => ^K+ ^pi- ^pi-) ^X]CC" 
mct[-1].Branches = {
            "B"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) (D- => K+ pi- pi-) X]CC", 
            "BH"       :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) (D- => K+ pi- pi-) ^X]CC", 
            "Dst"       :"[Beauty => ^(D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0"     :"[Beauty => (D*(2010)+ => ^(Charm => K- pi+ pi+ pi-) pi+) (D- => K+ pi- pi-) X]CC",      
            "DstH"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) ^pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0K"    :"[Beauty => (D*(2010)+ => (Charm => ^K- pi+ pi+ pi-) pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0Hm"    :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ ^pi-) pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0Hp1"    :"[Beauty => (D*(2010)+ => (Charm => K- ^pi+ pi+ pi-) pi+) (D- => K+ pi- pi-) X]CC", 
            "DstD0Hp2"    :"[Beauty => (D*(2010)+ => (Charm => K- pi+ ^pi+ pi-) pi+) (D- => K+ pi- pi-) X]CC", 
            "Dd"       :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) ^(D- => K+ pi- pi-) X]CC", 
            "DdK"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) (D- => ^K+ pi- pi-) X]CC", 
            "DdH"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) (D- => K+ ^pi- pi-) X]CC", 
            "Ddh"      :"[Beauty => (D*(2010)+ => (Charm => K- pi+ pi+ pi-) pi+) (D- => K+ pi- ^pi-) X]CC", 
            }
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']


##############################

mct.append(MCDecayTreeTuple("mctB2D0D0Pi2b2b"))
mct[-1].Decay = "[B+ => ^(Charm => ^K- ^pi+ ) ^(Charm => ^K+ ^pi- ) ^pi+]CC"
mct[-1].Branches = {
            "B"        :"[B+ => (Charm => K- pi+ ) (Charm => K+ pi- ) pi+]CC",
            "BH"       :"[B+ => (Charm => K- pi+ ) (Charm => K+ pi- ) ^pi+]CC",
            "D1"       :"[B+ => ^(Charm => K- pi+ ) (Charm => K+ pi- ) pi+]CC",
            "D1K"       :"[B+ => (Charm => ^K- pi+) (Charm => K+ pi- ) pi+]CC",
            "D1H"       :"[B+ => (Charm => K- ^pi+) (Charm => K+ pi- ) pi+]CC",
            "D2"        :"[B+ => (Charm => K- pi+) ^(Charm => K+ pi- ) pi+]CC",
            "D2K"       :"[B+ => (Charm => K- pi+) (Charm => ^K+ pi- ) pi+]CC",
            "D2H"       :"[B+ => (Charm => K- pi+) (Charm => K+ ^pi- ) pi+]CC",
            }
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']

'''
##############################
mct.append(MCDecayTreeTuple("mctB2D0D0Pi2b4b"))
mct[-1].Decay = "[Beauty => ^(Charm => ^K- ^pi+) ^(Charm => ^K+ ^pi- ^pi+ ^pi-) ^X]CC"
mct[-1].Branches = {
            "B"        :"[Beauty => (Charm => K- pi+) (Charm => K+ pi- pi+ pi-) X]CC" ,
            "BH"       :"[Beauty => (Charm => K- pi+) (Charm => K+ pi- pi+ pi-) ^X]CC",
            "D2b"       :"[Beauty => ^(Charm => K- pi+) (Charm => K+ pi- pi+ pi-) X]CC",
            "D2bK"      :"[Beauty => (Charm => ^K- pi+) (Charm => K+ pi- pi+ pi-) X]CC",
            "D2bH"      :"[Beauty => (Charm => K- ^pi+) (Charm => K+ pi- pi+ pi-) X]CC",
            "D4b"       :"[Beauty => (Charm => K- pi+) ^(Charm => K+ pi- pi+ pi-) X]CC",
            "D4bK"      :"[Beauty => (Charm => K- pi+) (Charm => ^K+ pi- pi+ pi-) X]CC",
            "D4bHm1"    :"[Beauty => (Charm => K- pi+) (Charm => K+ ^pi- pi+ pi-) X]CC",
            "D4bHp"     :"[Beauty => (Charm => K- pi+) (Charm => K+ pi- ^pi+ pi-) X]CC",
            "D4bHm2"    :"[Beauty => (Charm => K- pi+) (Charm => K+ pi- pi+ ^pi-) X]CC",
            }
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']

##############################

'''
mct.append(MCDecayTreeTuple("mctB2D0D0Pi4b4b"))
mct[-1].Decay = "[Beauty => ^(Charm => ^K- ^pi+ ^pi+ ^pi-) ^(Charm => ^K+ ^pi- ^pi+ ^pi-) ^X]CC"
mct[-1].Branches = {
            "B"        :"[Beauty => (Charm => K- pi+ pi+ pi-) (Charm => K+ pi- pi+ pi-) X]CC" ,
            "BH"       :"[Beauty => (Charm => K- pi+ pi+ pi-) (Charm => K+ pi- pi+ pi-) ^X]CC",
            "D1"       :"[Beauty => ^(Charm => K- pi+ pi+ pi-) (Charm => K+ pi- pi+ pi-) X]CC",
            "D1K"      :"[Beauty => (Charm => ^K- pi+ pi+ pi-) (Charm => K+ pi- pi+ pi-) X]CC",
            "D1Hp1"    :"[Beauty => (Charm => K- ^pi+ pi+ pi-) (Charm => K+ pi- pi+ pi-) X]CC",
            "D1Hm"     :"[Beauty => (Charm => K- pi+ pi+ ^pi-) (Charm => K+ pi- pi+ pi-) X]CC",
            "D1Hp2"    :"[Beauty => (Charm => K- pi+ ^pi+ pi-) (Charm => K+ pi- pi+ pi-) X]CC",
            "D2"       :"[Beauty => (Charm => K- pi+ pi+ pi-) ^(Charm => K+ pi- pi+ pi-) X]CC",
            "D2K"      :"[Beauty => (Charm => K- pi+ pi+ pi-) (Charm => ^K+ pi- pi+ pi-) X]CC",
            "D2Hm1"    :"[Beauty => (Charm => K- pi+ pi+ pi-) (Charm => K+ ^pi- pi+ pi-) X]CC",
            "D2Hp"     :"[Beauty => (Charm => K- pi+ pi+ pi-) (Charm => K+ pi- ^pi+ pi-) X]CC",
            "D2Hm2"    :"[Beauty => (Charm => K- pi+ pi+ pi-) (Charm => K+ pi- pi+ ^pi-) X]CC",
            }

mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']


##############################

mct.append(MCDecayTreeTuple("mctB2DstDstPi2b2b"))
mct[-1].Decay = "[Beauty => ^(D*(2010)+ => ^(Charm => ^K- ^pi+) ^pi+) ^(D*(2010)- => ^(Charm => ^K+ ^pi-) ^pi-) ^X]CC"
mct[-1].Branches = {
            "B"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "BH"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => (Charm => K+ pi-) pi-) ^X]CC", 
            "Dst1"        :"[Beauty => ^(D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "Dst1D0"        :"[Beauty => (D*(2010)+ => ^(Charm => K- pi+) pi+) (D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "Dst1H"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) ^pi+) (D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "Dst1D0K"        :"[Beauty => (D*(2010)+ => (Charm => ^K- pi+) pi+) (D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "Dst1D0H"        :"[Beauty => (D*(2010)+ => (Charm => K- ^pi+) pi+) (D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "Dst2"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) ^(D*(2010)- => (Charm => K+ pi-) pi-) X]CC", 
            "Dst2D0"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => ^(Charm => K+ pi-) pi-) X]CC", 
            "Dst2H"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => (Charm => K+ pi-) ^pi-) X]CC", 
            "Dst2D0K"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => (Charm => ^K+ pi-) pi-) X]CC", 
            "Dst2D0H"        :"[Beauty => (D*(2010)+ => (Charm => K- pi+) pi+) (D*(2010)- => (Charm => K+ ^pi-) pi-) X]CC", 
            }
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']



from Configurables import LHCb__ParticlePropertySvc as PPS 
svc = PPS ()
#nominal mass is 1.96849000
#new mass is 1.96869000
svc.Particles += [#D0 Mass
        "Lambda_c+              62        4122   1.0      1.86486000      4.101011e-13                 Lambda_c+        4122      0.00000000",
        "Lambda_c~-             63       -4122  -1.0      1.86486000      4.101011e-13           anti-Lambda_c-       -4122      0.00000000"
        ]



########################################################################
from Configurables import DaVinci
#DaVinci().EventPreFilters = evtFilters.filters ('Filters')
DaVinci().EvtMax = -1
DaVinci().PrintFreq = 1000
DaVinci().SkipEvents = 0                       # Events to skip
DaVinci().DataType = the_year
DaVinci().Simulation   = True
DaVinci().TupleFile = "Tuple.root"             # Ntuple#
DaVinci().InputType = "MDST"
DaVinci().RootInTES = '/Event/AllStreams'
DaVinci().UserAlgorithms = flts + dtts + mct
DaVinci().CondDBtag = conf_mc_mdst_restrip['condb']%(conf_mc_mdst_restrip['polarity'])
DaVinci().DDDBtag = conf_mc_mdst_restrip['dddb']

#DaVinci().Input=["root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/2018/ALLSTREAMS.MDST/00207257/0000/00207257_00000008_1.allstreams.mdst"]  # B+->D+D-pi+ sqDalitz
#DaVinci().Input=["root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/2018/ALLSTREAMS.MDST/00207254/0000/00207254_00000012_1.allstreams.mdst"]  # B+->D0D0barpi+ 2b2b phsp
#DaVinci().Input=["root://eoslhcb.cern.ch//eos/lhcb/grid/prod//lhcb/MC/2018/ALLSTREAMS.MDST/00207233/0000/00207233_00000006_1.allstreams.mdst"]  # B+->Dst+ Dst- pi 2b2b phsp
