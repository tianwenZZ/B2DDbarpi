from os import environ
from GaudiKernel.SystemOfUnits import *
from Gaudi.Configuration import *
from Configurables import GaudiSequencer, CombineParticles
from Configurables import DecayTreeTuple, EventTuple, TupleToolTrigger, TupleToolTISTOS,FilterDesktop
from Configurables import BackgroundCategory, TupleToolDecay, TupleToolVtxIsoln,TupleToolPid,EventCountHisto,TupleToolRecoStats,TupleToolDecayTreeFitter,SubstitutePID
from Configurables import LoKi__Hybrid__TupleTool, TupleToolVeto,TriggerTisTos
from DecayTreeTuple.Configuration import *
# Unit
mtl= [
        "L0HadronDecision",
        "L0MuonDecision",
        "L0DiMuonDecision",
        "L0ElectronDecision",
        "L0PhotonDecision",
        "Hlt1TrackMVADecision",
        "Hlt1TwoTrackMVADecision",
        "Hlt1TrackAllL0Decision",

        "Hlt2Topo2BodyDecision",
        "Hlt2Topo3BodyDecision",
        "Hlt2Topo4BodyDecision",
]
#
from PhysConf.Selections import AutomaticData, MomentumScaling, TupleSelection
ttl= [ "TupleToolKinematic", "TupleToolPid" ,"TupleToolTrackInfo","TupleToolDira"  ,"TupleToolPrimaries" ,"TupleToolPropertime","TupleToolEventInfo" ,"TupleToolRecoStats","TupleToolGeometry","TupleToolL0Calo"]
dtt=[]
seq=[]
flt=[]
from PhysConf.Selections import SelectionSequence
#1
################### ################### ################### ###################
loc="Phys/B2DDPiBeauty2CharmLine/Particles"
FltB2DdDdPi= FilterDesktop("FltB2DdDdPi")
FltB2DdDdPi.Code = "(INTREE((ID=='D+')&(M<1949.61)&(M>1789.61)))&(INTREE((ID=='D-')&(M<1949.61)&(M>1789.61)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2DdDdPi.Inputs = [loc]
FltB2DdDdPi.Output= "Phys/FltB2DdDdPi/Particles" 
FltB2DdDdPi.RootInTES = "/Event/Bhadron" 
flt.append(FltB2DdDdPi)

FltB2DdDdPi_data = AutomaticData("Phys/FltB2DdDdPi/Particles")
FltB2DdDdPi_data = MomentumScaling(FltB2DdDdPi_data)
B2DdDdPi_tuple = TupleSelection ( 'B2DdDdPi' ,
        [FltB2DdDdPi_data] ,
        Decay = "[B+ -> ^(D+ -> ^K- ^pi+ ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^pi+]CC",
        Branches = {
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
        )
tpl= B2DdDdPi_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D+","B+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D+"]
tpl.B.PVFitB2DDK.Substitutions={
                'Beauty -> Charm Charm ^pi+': 'K+',
                'Beauty -> Charm Charm ^pi-': 'K-'
                }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2DdDdPi', B2DdDdPi_tuple))
################### ################### ################### ###################
################### ################### ################### ###################
loc="Phys/B2DstDPiBeauty2CharmLine/Particles"
FltB2DstDdPi2b= FilterDesktop("FltB2DstDdPi2b")
FltB2DstDdPi2b.Code = "(INTREE(('D*(2010)+'==ABSID)&(M<2050.26)&(M>1970.26)))&(INTREE(('D+'==ABSID)&(M<1949.61)&(M>1789.61)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2DstDdPi2b.Inputs = [loc]
FltB2DstDdPi2b.Output= "Phys/FltB2DstDdPi2b/Particles" 
FltB2DstDdPi2b.RootInTES = "/Event/Bhadron" 
flt.append(FltB2DstDdPi2b)

FltB2DstDdPi2b_data = AutomaticData("Phys/FltB2DstDdPi2b/Particles")
FltB2DstDdPi2b_data = MomentumScaling(FltB2DstDdPi2b_data)
B2DstDdPi2b_tuple = TupleSelection ( 'B2DstDdPi2b' ,
        [FltB2DstDdPi2b_data] ,
        Decay = "[Beauty -> ^(D*(2010)+ -> ^(Charm -> ^K- ^pi+) ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^X]CC",
        Branches = {
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
        )
tpl= B2DstDdPi2b_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D+","D0","B+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D+","D0"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D+","D0"]
tpl.B.PVFitB2DDK.Substitutions={
        'Beauty -> Charm Charm ^pi+': 'K+',
        'Beauty -> Charm Charm ^pi-': 'K-'
        }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2DstDdPi2b', B2DstDdPi2b_tuple))
################### ################### ################### ###################
loc="Phys/B2DstDPiDstarD02K3PiBeauty2CharmLine/Particles"
FltB2DstDdPi4b= FilterDesktop("FltB2DstDdPi4b")
FltB2DstDdPi4b.Code = "(INTREE(('D*(2010)+'==ABSID)&(M<2050.26)&(M>1970.26)))&(INTREE(('D+'==ABSID)&(M<1949.61)&(M>1789.61)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(7==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2DstDdPi4b.Inputs = [loc]
FltB2DstDdPi4b.Output= "Phys/FltB2DstDdPi4b/Particles" 
FltB2DstDdPi4b.RootInTES = "/Event/Bhadron" 
flt.append(FltB2DstDdPi4b)

FltB2DstDdPi4b_data = AutomaticData("Phys/FltB2DstDdPi4b/Particles")
FltB2DstDdPi4b_data = MomentumScaling(FltB2DstDdPi4b_data)
B2DstDdPi4b_tuple = TupleSelection ( 'B2DstDdPi4b' ,
        [FltB2DstDdPi4b_data] ,
        Decay = "[Beauty -> ^(D*(2010)+ -> ^(Charm -> ^K- ^pi+ ^pi+ ^pi-) ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^X]CC",
        Branches = {
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
        )
tpl= B2DstDdPi4b_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D+","D0","B+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D+","D0"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D+","D0"]
tpl.B.PVFitB2DDK.Substitutions={
        'Beauty -> Charm Charm ^pi+': 'K+',
        'Beauty -> Charm Charm ^pi-': 'K-'
        }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2DstDdPi4b', B2DstDdPi4b_tuple))
################### ################### ################### ###################
loc="Phys/B2D0D0PiD02HHD02HHBeauty2CharmLine/Particles"
FltB2D0D0Pi2b2b= FilterDesktop("FltB2D0D0Pi2b2b")
FltB2D0D0Pi2b2b.Code = "(2==NINTREE(('D0'==ABSID)&(M<1944.83)&(M>1784.83)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(3==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2D0D0Pi2b2b.Inputs = [loc]
FltB2D0D0Pi2b2b.Output= "Phys/FltB2D0D0Pi2b2b/Particles" 
FltB2D0D0Pi2b2b.RootInTES = "/Event/Bhadron" 
flt.append(FltB2D0D0Pi2b2b)

FltB2D0D0Pi2b2b_data = AutomaticData("Phys/FltB2D0D0Pi2b2b/Particles")
FltB2D0D0Pi2b2b_data = MomentumScaling(FltB2D0D0Pi2b2b_data)
B2D0D0Pi2b2b_tuple = TupleSelection ( 'B2D0D0Pi2b2b' ,
        [FltB2D0D0Pi2b2b_data] ,
        Decay = "[B+ -> ^(Charm -> ^K- ^pi+ ) ^(Charm -> ^K+ ^pi- ) ^pi+]CC",
        Branches = {
            "B"        :"[B+ -> (Charm -> K- pi+ ) (Charm -> K+ pi- ) pi+]CC",
            "BH"       :"[B+ -> (Charm -> K- pi+ ) (Charm -> K+ pi- ) ^pi+]CC",
            "D1"       :"[B+ -> ^(Charm -> K- pi+ ) (Charm -> K+ pi- ) pi+]CC",
            "D1K"       :"[B+ -> (Charm -> ^K- pi+) (Charm -> K+ pi- ) pi+]CC",
            "D1H"       :"[B+ -> (Charm -> K- ^pi+) (Charm -> K+ pi- ) pi+]CC",
            "D2"        :"[B+ -> (Charm -> K- pi+) ^(Charm -> K+ pi- ) pi+]CC",
            "D2K"       :"[B+ -> (Charm -> K- pi+) (Charm -> ^K+ pi- ) pi+]CC",
            "D2H"       :"[B+ -> (Charm -> K- pi+) (Charm -> K+ ^pi- ) pi+]CC",
            }
        )
tpl= B2D0D0Pi2b2b_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D0"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D0"]
tpl.B.PVFitB2DDK.Substitutions={
        'Beauty -> Charm Charm ^pi+': 'K+',
        'Beauty -> Charm Charm ^pi-': 'K-'
        }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2D0D0Pi2b2b', B2D0D0Pi2b2b_tuple))
################### ################### ################### ###################
################### ################### ################### ###################
loc="Phys/B2D0D0PiD02HHD02K3PiBeauty2CharmLine/Particles"
FltB2D0D0Pi2b4b= FilterDesktop("FltB2D0D0Pi2b4b")
FltB2D0D0Pi2b4b.Code = "(2==NINTREE(('D0'==ABSID)&(M<1944.83)&(M>1784.83)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2D0D0Pi2b4b.Inputs = [loc]
FltB2D0D0Pi2b4b.Output= "Phys/FltB2D0D0Pi2b4b/Particles" 
FltB2D0D0Pi2b4b.RootInTES = "/Event/Bhadron" 
flt.append(FltB2D0D0Pi2b4b)

####subs:1
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
subIDB2D0D0Pi2b4b.RootInTES = "/Event/Bhadron"
flt.append(subIDB2D0D0Pi2b4b)

FltB2D0D0Pi2b4b_data = AutomaticData("Phys/subIDB2D0D0Pi2b4b/Particles")
FltB2D0D0Pi2b4b_data = MomentumScaling(FltB2D0D0Pi2b4b_data)
B2D0D0Pi2b4b_tuple = TupleSelection ( 'B2D0D0Pi2b4b' ,
        [FltB2D0D0Pi2b4b_data] ,
        Decay = "[Beauty -> ^(Charm -> ^K- ^pi+) ^(Charm -> ^K+ ^pi- ^pi+ ^pi-) ^X]CC",
        Branches = {
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
        )
tpl= B2D0D0Pi2b4b_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D0","B+","Lambda_c+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D0","Lambda_c+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D0","Lambda_c+"]
tpl.B.PVFitB2DDK.Substitutions={
        'Beauty -> Charm Charm ^pi+': 'K+',
        'Beauty -> Charm Charm ^pi-': 'K-'
        }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2D0D0Pi2b4b', B2D0D0Pi2b4b_tuple))
################### ################### ################### ###################
loc="Phys/B2D0D0PiD02K3PiD02K3PiBeauty2CharmLine/Particles"
FltB2D0D0Pi4b4b= FilterDesktop("FltB2D0D0Pi4b4b")
FltB2D0D0Pi4b4b.Code = "(2==NINTREE(('D0'==ABSID)&(M<1944.83)&(M>1784.83)))&(1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(7==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2D0D0Pi4b4b.Inputs = [loc]
FltB2D0D0Pi4b4b.Output= "Phys/FltB2D0D0Pi4b4b/Particles" 
FltB2D0D0Pi4b4b.RootInTES = "/Event/Bhadron" 
flt.append(FltB2D0D0Pi4b4b)

FltB2D0D0Pi4b4b_data = AutomaticData("Phys/FltB2D0D0Pi4b4b/Particles")
FltB2D0D0Pi4b4b_data = MomentumScaling(FltB2D0D0Pi4b4b_data)
B2D0D0Pi4b4b_tuple = TupleSelection ( 'B2D0D0Pi4b4b' ,
        [FltB2D0D0Pi4b4b_data] ,
        Decay = "[Beauty -> ^(Charm -> ^K- ^pi+ ^pi+ ^pi-) ^(Charm -> ^K+ ^pi- ^pi+ ^pi-) ^X]CC",
        Branches = {
            "B"        :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC" ,
            "BH"       :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) ^X]CC",
            "D1"       :"[Beauty -> ^(Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1K"      :"[Beauty -> (Charm -> ^K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1Hp1"    :"[Beauty -> (Charm -> K- ^pi+ pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1Hm"     :"[Beauty -> (Charm -> K- pi+ pi+ ^pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1Hp2"    :"[Beauty -> (Charm -> K- pi+ ^pi+ pi-) (Charm -> K+ pi- pi+ pi-) X]CC",
            "D1"       :"[Beauty -> (Charm -> K- pi+ pi+ pi-) ^(Charm -> K+ pi- pi+ pi-) X]CC",
            "D2K"      :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> ^K+ pi- pi+ pi-) X]CC",
            "D2Hm1"    :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ ^pi- pi+ pi-) X]CC",
            "D2Hp"     :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- ^pi+ pi-) X]CC",
            "D2Hm2"    :"[Beauty -> (Charm -> K- pi+ pi+ pi-) (Charm -> K+ pi- pi+ ^pi-) X]CC",
            }
        )
tpl= B2D0D0Pi4b4b_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D0"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D0"]
tpl.B.PVFitB2DDK.Substitutions={
        'Beauty -> Charm Charm ^pi+': 'K+',
        'Beauty -> Charm Charm ^pi-': 'K-'
        }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2D0D0Pi4b4b', B2D0D0Pi4b4b_tuple))
################### ################### ################### ###################

loc="Phys/B2DstDstPiBeauty2CharmLine/Particles"
FltB2DstDstPi2b2b= FilterDesktop("FltB2DstDstPi2b2b")
FltB2DstDstPi2b2b.Code = "(2==NINTREE(('D*(2010)+'==ABSID)&(M<2050.26)&(M>1970.26))) & (1==NINTREE(('K+'==ID)  & ( PROBNNk>0.1)))&(1==NINTREE(('K-'==ID)  & ( PROBNNk>0.1)))&(5==NINTREE(('pi+'==ABSID)  & ( PROBNNpi>0.05)))"
FltB2DstDstPi2b2b.Inputs = [loc]
FltB2DstDstPi2b2b.Output= "Phys/FltB2DstDstPi2b2b/Particles" 
FltB2DstDstPi2b2b.RootInTES = "/Event/Bhadron" 
flt.append(FltB2DstDstPi2b2b)

FltB2DstDstPi2b2b_data = AutomaticData("Phys/FltB2DstDstPi2b2b/Particles")
FltB2DstDstPi2b2b_data = MomentumScaling(FltB2DstDstPi2b2b_data)
B2DstDstPi2b2b_tuple = TupleSelection ( 'B2DstDstPi2b2b' ,
        [FltB2DstDstPi2b2b_data] ,
        Decay = "[Beauty -> ^(D*(2010)+ -> ^(Charm -> ^K- ^pi+) ^pi+) ^(D*(2010)- -> ^(Charm -> ^K+ ^pi-) ^pi-) ^X]CC",
        Branches = {
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
        )
tpl= B2DstDstPi2b2b_tuple.algorithm()
dtt.append(tpl)
tpl.addTool(TupleToolDecay, name = 'B')

#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
tpl.B.PVFitB.Verbose = True
tpl.B.PVFitB.UpdateDaughters= True
tpl.B.PVFitB.constrainToOriginVertex = True
tpl.B.PVFitB.daughtersToConstrain = ["D0","B+"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitD" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitD"))
tpl.B.PVFitD.Verbose = True
tpl.B.PVFitD.UpdateDaughters= True
tpl.B.PVFitD.constrainToOriginVertex = True
tpl.B.PVFitD.daughtersToConstrain = ["D0"]
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB2DDK" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFitB2DDK"))
tpl.B.PVFitB2DDK.Verbose = True
tpl.B.PVFitB2DDK.UpdateDaughters= True
tpl.B.PVFitB2DDK.constrainToOriginVertex = True
tpl.B.PVFitB2DDK.daughtersToConstrain = ["D0"]
tpl.B.PVFitB2DDK.Substitutions={
        'Beauty -> Charm Charm ^pi+': 'K+',
        'Beauty -> Charm Charm ^pi-': 'K-'
        }
#---------------->>>>>
tpl.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit" ]
tpl.B.addTool(TupleToolDecayTreeFitter("PVFit"))
tpl.B.PVFit.Verbose = True
tpl.B.PVFit.UpdateDaughters= True
tpl.B.PVFit.constrainToOriginVertex = True

#---------------->>>>>
seq.append(SelectionSequence('SEQB2DstDstPi2b2b', B2DstDstPi2b2b_tuple))



for i in dtt:
    i.ToolList += ttl

    i.ToolList+=[ "TupleToolTISTOS" ]
    i.addTool(TupleToolTISTOS, name="TupleToolTISTOS" )
    i.TupleToolTISTOS.Verbose=True
    i.TupleToolTISTOS.VerboseHlt1=True
    i.TupleToolTISTOS.VerboseHlt2=True
    i.TupleToolTISTOS.TriggerList = mtl

from Configurables import LHCb__ParticlePropertySvc as PPS 
svc = PPS ()
#nominal mass is 1.96849000
#new mass is 1.96869000
svc.Particles += [#D0 Mass
        "Lambda_c+              62        4122   1.0      1.86486000      4.101011e-13                 Lambda_c+        4122      0.00000000",
        "Lambda_c~-             63       -4122  -1.0      1.86486000      4.101011e-13           anti-Lambda_c-       -4122      0.00000000"
        ]

########################################################################
from Configurables import DaVinci #local test
#DaVinci().EventPreFilters = evtFilters.filters ('Filters')
DaVinci().EvtMax = -1
DaVinci().PrintFreq = 1000
DaVinci().SkipEvents = 0                       # Events to skip
DaVinci().DataType = "2016"
DaVinci().Simulation   = False 
DaVinci().Lumi =True 
DaVinci().HistogramFile = "DVHistos.root"      # Histogram file
DaVinci().TupleFile = "Tuple.root"             # Ntuple#
DaVinci().InputType = "MDST"
DaVinci().RootInTES = "/Event/Bhadron"
DaVinci().UserAlgorithms = flt+[ss.sequence() for ss in seq]
#DaVinci().Input=["root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/LHCb/Collision18/BHADRON.MDST/00077054/0000/00077054_00009881_1.bhadron.mdst"]
