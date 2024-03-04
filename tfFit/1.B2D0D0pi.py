# Copyright 2017 CERN for the benefit of the LHCb collaboration
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

#
# Example of three-body amplitude fit for baryonic decay B+ -> Lc+ p- pi-
# Lc+ is used a final state particle, so only two degrees of freedom remain, the fit is two-dimensional. 
# So the Lc+ and p- helicities are summed incoherently.
# The fit model includes realistic treatment of non-uniform acceptance (defined by the 
# 2D histogram in square Dalitz plot coordinates) and background (assumed to be constant 
# over phase space)
#
#https://gitlab.cern.ch/apiucci/toast/-/blob/master/amplitude_fits/KMatrix.py
#https://ampform.readthedocs.io/en/stable/usage/dynamics/k-matrix.html

import tensorflow as tf
import tensorflow.compat.v1 as tf1

from timeit import default_timer as timer
import sys, os
import pandas
import numpy as np
from TensorFlowAnalysis import *
from math import sqrt
from ROOT import TH1F, TH2F, TCanvas, TFile, gStyle, gROOT, TMath, RDataFrame,gPad, TLatex,TTree,TBranch,TLegend,TStyle,TRandom3
import time
#from resonanceTemplate import resonances,collectInits
from resonanceTemplate_setinit import resonances,collectInits

########### ########### ########### ########### ########### ###########
### config input output
########### ########### ########### ########### ########### ###########

bkktag="1"

sys.path.append("../")
#os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Do not use GPU
#os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3'
#os.environ['CUDA_VISIBLE_DEVICES'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = sys.argv[2] 
print("#######CUDA_VISIBLE_DEVICES ##############!!!!!!!!")
print(os.environ['CUDA_VISIBLE_DEVICES'])


#date = "%i_%i_%i_%i"%tuple(time.localtime(time.time())[1:5])
#InitSeed=os.environ["SEED"]+"_"+date
InitSeed=sys.argv[1]
gROOT.SetBatch()
gROOT.ProcessLine(".x ~/lhcbStyle.C")
tf.compat.v1.disable_eager_execution()
########### #########e# ########### ########### ########### ###########

gStyle.SetLegendTextSize(.02)
# Masses of initial and final state particles
m0=5.27925000 #B+
m1=1.86484000  #D0
m2=1.86486000 #D0bar
m3=0.13957018 #pi+
pi=TMath.Pi()

# Blatt-Weisskopf radii
rB = Const(4.) # For B->RZ
rR = Const(4.) # For R->12

# Flag to control caching of helicity tensors
cache = True



# Return the list of resonance names from the dictionary above
def listComponentNames(res) : 
    return sorted(res.keys())

# Return the number of resonance components in the dictionary above
def numberOfComponents(res) : 
    return len(listComponentNames(res))

# Return the amplitude for a single resonance contribution
# Input parameters: 
#   res : a dictionary representing a single resonance  (name, width, coupling etc)
#   var : dictionary of kinematic (observables) variables characterising a particular candidate 
#   sw  : list of boolean "switches" to turn components on/off for fit fraction calculation
def getHelicityAmplitudes(res, var, sw) : 
    channel = res["channel"]
    lineshape=Complex(Const(1.),Const(0.))

    # Determine lineshape function
    lineShapeFunc = BreitWignerLineShape
    if "lineshape" in res.keys() : lineShapeFunc = res["lineshape"]
    #print("lineshape:channel ",lineShapeFunc,channel)
    spin=res["spin"]
    lineshape=""
    if (lineShapeFunc == BreitWignerLineShape):
        if channel == 0 : 
            lineshape = lineShapeFunc(var["m13Sq"], res["mass"], res["width"], 
                    Const(m1), Const(m3),Const(m2),Const(m0), rR,rB, spin,spin)
        if channel == 1 : 
            lineshape = lineShapeFunc(var["m12Sq"], res["mass"], res["width"], 
                    Const(m1), Const(m2),Const(m3),Const(m0), rR,rB, spin,spin)
        if channel == 2 : 
            lineshape = lineShapeFunc(var["m23Sq"], res["mass"], res["width"], 
                    Const(m2), Const(m3),Const(m1),Const(m0), rR,rB, spin,spin)
    if lineShapeFunc == ExponentialNonResonantLineShape:
        if channel == 0 : 
            lineshape = lineShapeFunc(var["m13Sq"],Const(0.),res["slope"],
                    Const(m1), Const(m3),Const(m2),Const(m0),0,0,rR,rB) 
        if channel == 1 : 
            lineshape = lineShapeFunc(var["m12Sq"],Const(0.),res["slope"],
                    Const(m1), Const(m2),Const(m3),Const(m0),0,0,rR,rB) 
        if channel == 2 : 
            lineshape = lineShapeFunc(var["m23Sq"],Const(0.),res["slope"],
                    Const(m2), Const(m3),Const(m1),Const(m0),0,0,rR,rB) 
    
    if lineShapeFunc == ExponentialNonResonantLineShapeWithPhaseShift:
        if channel == 0 : 
            lineshape = lineShapeFunc(var["m13Sq"],Const(0.),res["NonRes0alpha"], res["NonRes0beta"],
                    Const(m1), Const(m3),Const(m2),Const(m0),0,0,rR,rB) 
        if channel == 1 : 
            lineshape = lineShapeFunc(var["m12Sq"],Const(0.),res["NonRes0alpha"], res["NonRes0beta"],
                    Const(m1), Const(m2),Const(m3),Const(m0),0,0,rR,rB) 
        if channel == 2 : 
            lineshape = lineShapeFunc(var["m23Sq"],Const(0.),res["NonRes0alpha"], res["NonRes0beta"],
                    Const(m2), Const(m3),Const(m1),Const(m0),0,0,rR,rB) 



    if lineShapeFunc == myFlatRes:
        if channel == 0 :
            lineshape = lineShapeFunc(var["m13Sq"],Const(0.5*(m0-m1-m2-m3)) , Const(m1), Const(m3), Const(m2),Const(m0), rR, rB, spin, spin )
        if channel == 1 :
            lineshape = lineShapeFunc(var["m12Sq"],Const(0.5*(m0-m1-m2-m3)) , Const(m1), Const(m2), Const(m3),Const(m0), rR, rB, spin, spin )
        if channel == 2 :
            lineshape = lineShapeFunc(var["m23Sq"],Const(0.5*(m0-m1-m2-m3)) , Const(m2), Const(m3), Const(m1),Const(m0), rR, rB, spin, spin )



    # better not use this module
    # if do KMatrix fit please use 2.B2DpD0K0_bkg_KMatrix.py !!
    """
    if (lineShapeFunc == KMatrix):
        if channel == 0 : 
            betaR1,betaR2 = res["betaProd"]
            gammaR1a,gammaR1bRatio = res["gammaR1toAB"]
            gammaR2a,gammaR2bRatio = res["gammaR2toAB"]
            mR= res["mass"]
            wR= res["width"]
            lineshape = lineShapeFunc(var["m13Sq"],
                    betaR1,betaR2,
                    gammaR1a,gammaR1bRatio,
                    gammaR2a,gammaR2bRatio,
                    mR, wR,
                    [Const(m1),Const(m1p)],[Const(m3),Const(m3)],Const(m2),Const(m0),
                    rR,rB,spin,spin,barrierFactor=False
                    )

    """

    ampl = ""

    cpl=res["coupling"]
    if channel==0: ## B-> (D+K0) D0
        ampl = sw*cpl*lineshape*DalitzAmplitude3Body(var["theta13"],2.*spin,0.,0.,0., cache = cache)
    if channel==1: ## B-> (D+D0) K0
        ampl = sw*cpl*lineshape*DalitzAmplitude3Body(var["theta12"],2.*spin,0.,0.,0., cache = cache)
    if channel==2: ## B-> (D0K0) D+
        ampl = sw*cpl*lineshape*DalitzAmplitude3Body(var["theta23"],2.*spin,0.,0.,0., cache = cache)

    return ampl


############## ############## ############## ##############
#phsp = DalitzPhaseSpace(mL, mH, mP, mB, range12, range23, range13)
print(":::::: create dalitzphasespace")
range12=[m1+m2,1.E6]
range23=[m2+m3,1.E6]
range13=[m1+m3,1.E6]
phsp = DalitzPhaseSpace(m1, m2, m3, m0,range12,range23,range13)
############## ############## ############## ##############

# Create the list of boolean switches for amplitude components
#  "+1" for an additional switch corresponding to background component
switches = Switches(numberOfComponents(resonances))


# Function that returns the TF graph for a set of decay amplitudes for a phase space tensor "x"
def amp_model(x) :  ## x= [[m2ab,m2bc,m2ac ....]] = [[mSc, mDe, mDs....]]

    # Calculate invariant masses at the phasespace point "x"
    m12Sq = phsp.M2ab(x)
    m23Sq = phsp.M2bc(x)
    m13Sq = phsp.M2ac(x)
    cosHel12   = x[:,3]
    cosHel23   = x[:,4]
    cosHel13   = x[:,5]


    # Dictionary of all kinematic variables characterising a candidate
    var = {
            "m12Sq" : m12Sq, 
            "m23Sq" : m23Sq, 
            "m13Sq" : m13Sq, 
            "theta12" : Acos(cosHel12), 
            "theta23" : Acos(cosHel23), 
            "theta13" : Acos(cosHel13), 
            }

    sumAmpl = Complex(Const(0.), Const(0.))

    # Loop over all resonances, add up amplitudes corresponding to 
    # initial and final state polarisations coherently
    for i,n in enumerate(listComponentNames(resonances)) : 
        res = resonances[n]
        sw = Complex(switches[i], Const(0.))

        #print(":::::::: Starting adding res: ",res["name"],"J^P=(",res["spin"],")")
        sumAmpl += getHelicityAmplitudes(res, var, sw)
        #print(":::::::: Ending adding res: ",res["name"],"\n")

    return sumAmpl

def dens_model(x) : 
    return Density(amp_model(x))


# Placeholders for data and normalisation samples
data_ph = tf1.placeholder(FPType(), shape=(None, None),name="Data")
norm_ph = tf1.placeholder(FPType(), shape=(None, None),name="Norm")

def sig_pdf(x):
    #print ("Signal Model")
    return dens_model(x)
'''
def sig_pdf_times_eff(x):
    #print ("Signal Model * Efficiency")
    return dens_model(x) * x[:,6]
'''

# TF graphs for decay density as functions of data and normalisation placeholders
#sig_real_model = sig_pdf_times_eff(data_ph)
#sig_norm_model = sig_pdf_times_eff(norm_ph)
sig_norm_model = sig_pdf(norm_ph)
sig_data_model = sig_pdf          (data_ph)

sig_norm       = Integral(sig_norm_model)

# construct the actual fit model (total PDF), Background magnitude is a fixed parameter
def fit_pdf(x,normS):
    return sig_pdf(x)/normS


fit_model =  fit_pdf(data_ph,sig_norm)

# Assume the weight is the last element in the list
def event_weight(datapoint, norm = 1.):
    return tf.transpose(datapoint)[-1] * norm


weight_model = event_weight(data_ph)


# Set random seed and create TF session
print(":::::::: creating TF session")
SetSeed(1)
sess = tf1.Session()

# Initialise TF
print("::::::: starting initialising TF")
init = tf1.global_variables_initializer()
sess.run(init)

### if you want to have more variables loaded, just append them in the list


varsInTree_data      = [ "m12Sq", "m23Sq", "m13Sq", "cosHel12", "cosHel23", "cosHel13","pq13","sig_sw"]
varsInTree_norm      = [ "m12Sq", "m23Sq", "m13Sq", "cosHel12", "cosHel23", "cosHel13","pq13"]

def loadData(tree, filepath,variables,name=""):
    rdf=RDataFrame(tree,filepath).AsNumpy(variables)
    rf=np.stack( np.array([rdf[key].tolist() for key in variables]),   axis=1)
    sample1=tf1.constant(rf,dtype=fptype)
    sample=sess.run(phsp.Filter(sample1))
    #print("loading data ",name," of ",sample.shape,"events",sample)
    return sample


norm_samples = loadData("tree","~/workdir/B2DDbarpi/snakemake_chain/dataForTFFit/flat-toy.root",varsInTree_norm,"Norm")
                                                                        
data_samples = loadData("DecayTree","~/workdir/B2DDbarpi/snakemake_chain/dataForTFFit/data_sw.root",varsInTree_data,"Fit")


samples_feeder = {}  #feed-back data samples
samples_feeder[data_ph]=data_samples
samples_feeder[norm_ph]=norm_samples


# Create the TF graph for unbinned NLL from the data 
nll=Const(0.)
nll += UnbinnedWeightedNLL( fit_model, Const(1.), weight_model )


def applyConstraint(par, vv, ss):
    return (par-Const(vv))**2/(Const(ss))**2/Const(2.)



print("::::::: starting runminuit")
# Run minimisation and store results
tmp=""
for name in listComponentNames(resonances):
    tmp+=("_"+name)
tmp=tmp[1:]
bkktag=tmp+"_"+InitSeed
options = None
run_metadata = None
doFit=1
start = timer()
if doFit:
    print("start minimization")
    print("Number of components",len(switches),listComponentNames(resonances),len(listComponentNames(resonances)))
    result = RunMinuit(sess, nll, samples_feeder, useGradient = True, options = options, run_metadata = run_metadata )
    print("end running")
    print("start writing results")
    WriteFitResults(result, "parameters/result_%s.txt"%(bkktag))
    print("Fit result is written into parameters/result_%s.txt"%(bkktag))
    with open("log.txt","a") as file:
        file.write("log: "+str(result["loglh"])+"\n")
    print("loglh:",result["loglh"])
    print("end writing results")
end = timer()
print("time used:",end - start) 


# Calculate and store fit fractions
ff = CalculateFitFractions   (sess, sig_data_model, data_ph, switches, norm_sample = norm_samples)
_ff = CalculateFitFractionsIJ(sess, sig_data_model, data_ph, switches, norm_sample = norm_samples)
WriteFitFractions  (ff, listComponentNames(resonances) , "parameters/fitfractions_%s_%s.txt"%(bkktag, "ALL"))
WriteFitFractionsIJ(_ff, "parameters/fitfractionsIJ_%s_%s.txt"%(bkktag,"ALL"))

# Create toy MC sample corresponding to the fit result
def exp_pdf(x,normalization_sig):
    return sig_pdf(x)/normalization_sig
def genToysExp(sess):
    global phsp, switches,norm_ph,norm_samples

    print("  "*100)
    print("Gen toys: ")
    normalization_sig = sess.run(sig_norm,{norm_ph : norm_samples})
    print("--> normalization integral of signal ",normalization_sig)

    exp_model =  exp_pdf(norm_ph,normalization_sig)
    names=listComponentNames(resonances)
    #print("names:",len(names),len(switches))
    
    fit_sample = RunToyMC_weightedInter(sess, exp_model, norm_ph, phsp, 1000000, chunk = 100000, switches = switches,norm_sample=norm_samples )
    f = TFile.Open("toys/toy_%s_%s.root"%(bkktag,"ALL"), "RECREATE")
    FillNTuple("toy", fit_sample, varsInTree_norm+ ["wAll"]+[ "w%s_%s" %(names[n],names[m])  for n in range(len(switches)) for m in range(n,len(switches)) ] )
    f.Close()


"""
def ideal_pdf(x,normalization_sig):
    return sig_pdf(x)/normalization_sig 
def genToys(sess,name):
    global phsp, switches,norm_ph,norm_samples

    print("Gen toys for ",name)
    normalization_sig = sess.run(sig_norm[name],{norm_ph[name] : norm_samples[name]})
    print("normalization integral of signal",normalization_sig)

    ideal_model =  ideal_pdf(norm_ph[name],normalization_sig)
    names=listComponentNames(resonances)+["null"]
    print("names:",len(names),len(switches))
    
    fit_sample = RunToyMC_weightedInter(sess, ideal_model, norm_ph[name], phsp, 1000000, chunk = 100000, switches = switches,norm_sample=norm_samples[name] )
    f = TFile.Open("toys/toy_%s_%s.root"%(bkktag,name), "RECREATE")
    FillNTuple("toy", fit_sample, varsInTree + ["wAll"]+[ "w%s_%s" %(names[n],names[m])  for n in range(len(switches)) for m in range(n,len(switches)) ] )
    f.Close()
"""

genToysExp(sess)



print("time used:",end - start) 
sys.exit()
sys.exit()
sys.exit()
sys.exit()
