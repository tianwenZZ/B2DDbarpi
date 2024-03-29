#### For Lb0 => Xi_c+ D_s-, MCEvtID 15296003
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
        "year":"2018",
        "stripping":"stripping34",
        "condb":"sim-20190430-vc-%s100",
        "dddb":'dddb-20170721-3',
        "polarity":'mu'
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

        "Hlt2Topo2BodyDecision",
        "Hlt2Topo3BodyDecision",
        "Hlt2Topo4BodyDecision",
]

from Configurables import BackgroundCategory, TupleToolDecay, TupleToolVtxIsoln,TupleToolPid,EventCountHisto,TupleToolRecoStats,TupleToolDecayTreeFitter,TupleToolMCTruth

MCTruth = TupleToolMCTruth() 
MCTruth.ToolList = [ 	"MCTupleToolKinematic" , 	"MCTupleToolHierarchy" ]
def fillDecayTreeFitter(dtt,constr):
    i=dtt
    i.addTool(TupleToolDecay, name = 'B')
    i.ToolList += ["TupleToolRecoStats","TupleToolL0Calo", "TupleToolKinematic" ,"TupleToolGeometry" ,"TupleToolDira" ,"TupleToolPid" ,"TupleToolPropertime" ,"TupleToolEventInfo" ,"TupleToolTrackInfo" , "TupleToolMCTruth" ,"TupleToolMCBackgroundInfo","TupleToolL0Data"]

    i.B.ToolList+=[ "TupleToolTISTOS" ]
    i.B.addTool(TupleToolTISTOS, name="TupleToolTISTOS" )
    i.B.TupleToolTISTOS.Verbose=True
    i.B.TupleToolTISTOS.VerboseHlt1=True
    i.B.TupleToolTISTOS.VerboseHlt2=True
    i.B.TupleToolTISTOS.TriggerList = mtl

    i.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit0"]       
    i.B.addTool(TupleToolDecayTreeFitter("PVFit0"))
    i.B.PVFit0.Verbose = True
    i.B.PVFit0.UpdateDaughters= True
    i.B.PVFit0.constrainToOriginVertex = True

    i.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFit"]       
    i.B.addTool(TupleToolDecayTreeFitter("PVFit"))
    i.B.PVFit.Verbose = True
    i.B.PVFit.UpdateDaughters= True
    i.B.PVFit.constrainToOriginVertex = True
    i.B.PVFit.daughtersToConstrain = constr[1:]

    i.B.ToolList +=  [ "TupleToolDecayTreeFitter/PVFitB"]       
    i.B.addTool(TupleToolDecayTreeFitter("PVFitB"))
    i.B.PVFitB.Verbose = True
    i.B.PVFitB.UpdateDaughters= True
    i.B.PVFitB.constrainToOriginVertex = True
    i.B.PVFitB.daughtersToConstrain = constr

    i.addTool(MCTruth)
#

dtts=[]
flts=[]
mct=[]

########### ########### ###########
loc="Phys/B2DDKBeauty2CharmLine/Particles"
FltB2DDK= FilterDesktop("FltB2DDK")
FltB2DDK.Code = "ALL"
FltB2DDK.Inputs = [loc]
FltB2DDK.Output= "Phys/FltB2DDK/Particles" 
flts.append(FltB2DDK)

dtts.append( DecayTreeTuple("B2DDK"))
dtts[-1].Inputs = ["Phys/FltB2DDK/Particles"]
dtts[-1].Decay = "[Beauty -> ^(D+  -> ^K- ^pi+ ^pi+) ^(D- -> ^K+ ^pi- ^pi-) ^K+]CC" 
dtts[-1].Branches = {
        "B"          :"[Beauty -> (D+  -> K- pi+ pi+) (D- -> K+ pi- pi-) K+]CC", 
        "D1"          :"[Beauty -> ^(D+  -> K- pi+ pi+) (D- -> K+ pi- pi-) K+]CC", 
        "D1K"         :"[Beauty -> (D+  -> ^K- pi+ pi+) (D- -> K+ pi- pi-) K+]CC", 
        "D1H1"       :"[Beauty -> (D+  -> K- pi+ ^pi+) (D- -> K+ pi- pi-) K+]CC", 
        "D1H2"       :"[Beauty -> (D+  -> K- ^pi+ pi+) (D- -> K+ pi- pi-) K+]CC", 
        "D2"         :"[Beauty -> (D+  -> K- pi+ pi+) ^(D- -> K+ pi- pi-) K+]CC", 
        "D2H1"       :"[Beauty -> (D+  -> K- pi+ pi+) (D- -> K+ ^pi- pi-) K+]CC", 
        "D2K"        :"[Beauty -> (D+  -> K- pi+ pi+) (D- -> ^K+ pi- pi-) K+]CC", 
        "D2H2"        :"[Beauty -> (D+  -> K- pi+ pi+) (D- -> K+ pi- ^pi-) K+]CC", 
        "K"        :"[Beauty -> (D+  -> K- pi+ pi+) (D- -> K+ pi- pi-) ^K+]CC", 
    }
fillDecayTreeFitter(dtts[-1],["B+","K+","D+","D-"])

###########
MessageSvc().Format = "% F%60W%S%7W%R%T %0W%M"

########### ########### ###########
loc="Phys/B2DstDstKBeauty2CharmLine/Particles"
FltB2DstDstK= FilterDesktop("FltB2DstDstK")
FltB2DstDstK.Code = "ALL"
FltB2DstDstK.Inputs = [loc]
FltB2DstDstK.Output= "Phys/FltB2DstDstK/Particles" 
flts.append(FltB2DstDstK)

dtts.append( DecayTreeTuple("B2DstDstK"))
dtts[-1].Inputs = ["Phys/FltB2DstDstK/Particles"]
dtts[-1].Decay = "[Beauty -> ^(D*(2010)+  -> ^(D0 -> ^K+ ^pi-) ^pi+) ^(D*(2010)- -> ^(D~0 -> ^K- ^pi+) ^pi-) ^K+]CC" 
dtts[-1].Branches = {
        "B"          :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D1"          :"[Beauty -> ^(D*(2010)+  -> (D0 -> K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D1pi"         :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) ^pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D1D0"         :"[Beauty -> (D*(2010)+  -> ^(D0 -> K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D1D0K"         :"[Beauty -> (D*(2010)+  -> (D0 -> ^K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D1D0pi"         :"[Beauty -> (D*(2010)+  -> (D0 -> K+ ^pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D2"          :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+) ^(D*(2010)- -> (D~0 -> K- pi+) pi-) K+]CC", 
        "D2pi"         :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) ^pi-) K+]CC", 
        "D2D0"         :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+) (D*(2010)- -> ^(D~0 -> K- pi+) pi-) K+]CC", 
        "D2D0K"         :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+)(D*(2010)- -> (D~0 -> ^K- pi+) pi-) K+]CC", 
        "D2D0pi"         :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- ^pi+) pi-) K+]CC", 
        "K"          :"[Beauty -> (D*(2010)+  -> (D0 -> K+ pi-) pi+) (D*(2010)- -> (D~0 -> K- pi+) pi-) ^K+]CC", 
    }
fillDecayTreeFitter(dtts[-1],["B+","K+","D*(2010)+","D*(2010)-"])


########### ########### ###########
loc="Phys/B2D0D0KD02HHD02HHBeauty2CharmLine/Particles"
FltB2D0D0bK= FilterDesktop("FltB2D0D0bK")
FltB2D0D0bK.Code = "ALL"
FltB2D0D0bK.Inputs = [loc]
FltB2D0D0bK.Output= "Phys/FltB2D0D0bK/Particles" 
flts.append(FltB2D0D0bK)

dtts.append( DecayTreeTuple("B2D0D0bK"))
dtts[-1].Inputs = ["Phys/FltB2D0D0bK/Particles"]
dtts[-1].Decay = "[Beauty -> ^(Charm  -> ^K- ^pi+) ^(Charm -> ^K+ ^pi-) ^K+]CC" 
dtts[-1].Branches = {
        "B"          :"[Beauty -> ^(Charm  -> ^K- ^pi+) ^(Charm -> ^K+ ^pi-) ^K+]CC", 
        "D1"          :"[Beauty -> ^(Charm  -> K- pi+) (Charm -> K+ pi-) K+]CC", 
        "D1K"          :"[Beauty -> (Charm  -> ^K- pi+) (Charm -> K+ pi-) K+]CC", 
        "D1H"          :"[Beauty -> (Charm  -> K- ^pi+) (Charm -> K+ pi-) K+]CC", 
        "D2"          :"[Beauty -> (Charm  -> K- pi+) ^(Charm -> K+ pi-) K+]CC", 
        "D2H"          :"[Beauty -> (Charm  -> K- pi+) (Charm -> K+ ^pi-) K+]CC", 
        "D2K"          :"[Beauty -> (Charm  -> K- pi+) (Charm -> ^K+ pi-) K+]CC", 
        "K"          :"[Beauty -> (Charm  -> K- pi+) (Charm -> K+ pi-) ^K+]CC", 
    }
fillDecayTreeFitter(dtts[-1],["B+","K+","D0"])
######################################################

##############################
loc="Phys/B2D0D0KD02HHD02K3PiBeauty2CharmLine/Particles"
FltB2D0D0K2b4b= FilterDesktop("FltB2D0D0K2b4b")
FltB2D0D0K2b4b.Code = "ALL"
FltB2D0D0K2b4b.Inputs = [loc]
FltB2D0D0K2b4b.Output= "Phys/FltB2D0D0K2b4b/Particles" 
flts.append(FltB2D0D0K2b4b)


subIDB2D0D0K2b4b= SubstitutePID("subIDB2D0D0K2b4b",
        Code = "DECTREE('[B+ -> Charm Charm K+]CC')",
        Substitutions={
            "B+ -> (Charm -> K- pi+) ^(Charm -> K+ pi- pi- pi+) K+":  "Lambda_c~-",
            "B- -> (Charm -> K+ pi-) ^(Charm -> K- pi+ pi+ pi-) K-":  "Lambda_c+",
            "B- -> (Charm -> K- pi+) ^(Charm -> K+ pi- pi- pi+) K-":  "Lambda_c~-",
            "B+ -> (Charm -> K+ pi-) ^(Charm -> K- pi+ pi+ pi-) K+":  "Lambda_c+",
           }
        )
subIDB2D0D0K2b4b.Inputs =  ["Phys/FltB2D0D0K2b4b/Particles"]
flts.append(subIDB2D0D0K2b4b)

dtts.append(DecayTreeTuple("B2D0D0K2b4b"))
dtts[-1].Inputs = ["Phys/subIDB2D0D0K2b4b/Particles"]
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


######################################################################
mct.append(MCDecayTreeTuple("mctDDK"))
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']
mct[-1].Decay = "[Beauty => ^(D+  ==> ^K- ^pi+ ^pi+) ^(D- ==> ^K+ ^pi- ^pi-) ^K+]CC" 
mct[-1].Branches = {
        "B"          :"[Beauty => (D+  => K- pi+ pi+) (D- => K+ pi- pi-) K+]CC", 
        "D1"          :"[Beauty => ^(D+  => K- pi+ pi+) (D- => K+ pi- pi-) K+]CC", 
        "D1K"         :"[Beauty => (D+  => ^K- pi+ pi+) (D- => K+ pi- pi-) K+]CC", 
        "D1H1"       :"[Beauty => (D+  => K- pi+ ^pi+) (D- => K+ pi- pi-) K+]CC", 
        "D1H2"       :"[Beauty => (D+  => K- ^pi+ pi+) (D- => K+ pi- pi-) K+]CC", 
        "D2"         :"[Beauty => (D+  => K- pi+ pi+) ^(D- => K+ pi- pi-) K+]CC", 
        "D2H1"       :"[Beauty => (D+  => K- pi+ pi+) (D- => K+ ^pi- pi-) K+]CC", 
        "D2K"        :"[Beauty => (D+  => K- pi+ pi+) (D- => ^K+ pi- pi-) K+]CC", 
        "D2H2"        :"[Beauty => (D+  => K- pi+ pi+) (D- => K+ pi- ^pi-) K+]CC", 
        "K"        :"[Beauty => (D+  => K- pi+ pi+) (D- => K+ pi- pi-) ^K+]CC", 
    }


mct.append(MCDecayTreeTuple("mctD0D0bK"))
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']
mct[-1].Decay = "[Beauty => ^(Charm  => ^K- ^pi+) ^(Charm => ^K+ ^pi-) ^K+]CC"  # => : have a gamma
# for mc decaytree, use =>
# =>: directly decay to these particles; ==>: may have intermediate state
# for reconstruction, use =>
mct[-1].Branches = {
        "B"          :"[Beauty => ^(Charm  => ^K- ^pi+) ^(Charm => ^K+ ^pi-) ^K+]CC", 
        "D1"          :"[Beauty => ^(Charm  => K- pi+) (Charm => K+ pi-) K+]CC", 
        "D1K"          :"[Beauty => (Charm  => ^K- pi+) (Charm => K+ pi-) K+]CC", 
        "D1H"          :"[Beauty => (Charm  => K- ^pi+) (Charm => K+ pi-) K+]CC", 
        "D2"          :"[Beauty => (Charm  => K- pi+) ^(Charm => K+ pi-) K+]CC", 
        "D2H"          :"[Beauty => (Charm  => K- pi+) (Charm => K+ ^pi-) K+]CC", 
        "D2K"          :"[Beauty => (Charm  => K- pi+) (Charm => ^K+ pi-) K+]CC", 
        "K"          :"[Beauty => (Charm  => K- pi+) (Charm => K+ pi-) ^K+]CC", 
    }


mct.append(MCDecayTreeTuple("mctDstDstK"))
mct[-1].ToolList+=[ 'MCTupleToolHierarchy', 'MCTupleToolKinematic']
mct[-1].Decay = "[Beauty => ^(D*(2010)+  => ^(D0 => ^K+ ^pi-) ^pi+) ^(D*(2010)- => ^(D~0 => ^K- ^pi+) ^pi-) ^K+]CC" 
mct[-1].Branches = {
        "B"          :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+) (D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D1"          :"[Beauty => ^(D*(2010)+  => (D0 => K+ pi-) pi+) (D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D1pi"         :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) ^pi+) (D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D1D0"         :"[Beauty => (D*(2010)+  => ^(D0 => K+ pi-) pi+) (D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D1D0K"         :"[Beauty => (D*(2010)+  => (D0 => ^K+ pi-) pi+) (D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D1D0pi"         :"[Beauty => (D*(2010)+  => (D0 => K+ ^pi-) pi+) (D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D2"          :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+) ^(D*(2010)- => (D~0 => K- pi+) pi-) K+]CC", 
        "D2pi"         :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+) (D*(2010)- => (D~0 => K- pi+) ^pi-) K+]CC", 
        "D2D0"         :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+) (D*(2010)- => ^(D~0 => K- pi+) pi-) K+]CC", 
        "D2D0K"         :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+)(D*(2010)- => (D~0 => ^K- pi+) pi-) K+]CC", 
        "D2D0pi"         :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+) (D*(2010)- => (D~0 => K- ^pi+) pi-) K+]CC", 
        "K"          :"[Beauty => (D*(2010)+  => (D0 => K+ pi-) pi+) (D*(2010)- => (D~0 => K- pi+) pi-) ^K+]CC", 
    }
########################################################################


mct.append(MCDecayTreeTuple("mctB2D0D0K2b4b"))
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


from Configurables import LHCb__ParticlePropertySvc as PPS 
svc = PPS ()
#nominal mass is 1.96849000
#new mass is 1.96869000
svc.Particles += [#D0 Mass
        "Lambda_c+              62        4122   1.0      1.86486000      4.101011e-13                 Lambda_c+        4122      0.00000000",
        "Lambda_c~-             63       -4122  -1.0      1.86486000      4.101011e-13           anti-Lambda_c-       -4122      0.00000000"
        ]


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
DaVinci().UserAlgorithms = flts+dtts+mct
DaVinci().CondDBtag = conf_mc_mdst_restrip['condb']%(conf_mc_mdst_restrip['polarity'])
DaVinci().DDDBtag = conf_mc_mdst_restrip['dddb']

# for B+=>D0D0bK+ 4b2b
#DaVinci().Input=["root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/2018/ALLSTREAMS.MDST/00125303/0000/00125303_00000012_7.AllStreams.mdst"]
