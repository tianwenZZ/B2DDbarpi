import sys, os
sys.path.append("../")
from TensorFlowAnalysis import *
import tensorflow as tf
import tensorflow.compat.v1 as tf1
tf.compat.v1.disable_eager_execution()
from ROOT import TRandom3, TMath



# Masses of initial and final state particles
m0=5.27925000 #B+
m1=1.86484000  #D0
m2=1.86486000 #D0bar
m3=0.13957018 #pi+

randomize = 1 
rnd=TRandom3()
#rnd.SetSeed(0)
rnd.SetSeed(0)
os.environ["SEED"] = str(rnd.GetSeed())

collectInits={}


def buildLineParameter(name,fromSettings):
    if len(fromSettings)>3: print("SOMETHING WRONG IN THE CONFIGURATION")
    if len(fromSettings) ==1: return Const(fromSettings[0])
    sCentral, sWidth=fromSettings[0],fromSettings[1]
    rmin,rmax = sCentral-sWidth, sCentral+sWidth 
    getVal=sCentral
    step=sWidth/1000.
    if len(fromSettings) ==3: step = fromSettings[2]
    if randomize: getVal = rnd.Uniform(rmin+step,rmax-step)
    collectInits[name] =getVal
    return  FitParameter(name,getVal,rmin,rmax,step)

def buildCoupling(name,fromSettings,fix=False):
    if fix: return Complex( Const(1),  Const(0))

    if len(fromSettings)==1:
        print("SOMETHING WRONG IN THE CONFIGURATION! WILL SET RANDOM AMPLITUDE!")
    if len(fromSettings)==2:     # fromSettings: (  IsSetInit,  Re(sCentral, sWidth, step), Im(sCentral, sWidth, step),)
        return Complex(
                buildLineParameter(name+"R",fromSettings[0]),
                buildLineParameter(name+"I",fromSettings[1])
                )
    # len(fromSettings)=0 means do not set amplitude initials
    collectInits[name+"R"] = rnd.Uniform(-10,10)
    collectInits[name+"I"] = rnd.Uniform(-10,10)
    
    return Complex(
            FitParameter(name+"R",collectInits[name+"R"],-1000,1000,0.001),
            FitParameter(name+"I",collectInits[name+"I"],-1000,1000,0.001)
            )

# Dictionary to describe the amplitude structure
# The dictionary has the structure 
#   "Resonance name" : Resonance
# where Resonance is again a dictionary describing a single resonance
# with the following properties: 
#   "channel"   : resonance channel 
#                     (0 for D+K0 resonance, 
#                      1 for D+D0 resonance, 
#                      2 for D0K0 resonance)
#   "name"      : the name for a state
#   "lineshape" : optional line shape class. By default, BreitWignerLineShape is used. 
#   "mass"      : Mass of the resonance 
#   "width"     : Width of the resonance. 
#                 Mass and width should be TF graphs, e.g. Const(...), FitParameter(...) etc.
#   "spin"      : spin of the resonance 
#   "amp"       : amplitude of the resonance
lineshapes={
        "BW":BreitWignerLineShape,
        "Poly":PolynomialNonResonantLineShape,
        "SBW":SubThresholdBreitWignerLineShape, 
        }

useKmatrix=False


def loadparam(bkk):
        path="parameters/result_"+bkk+".txt"
        param={}
        with open(path,"r",encoding='UTF-8') as f:
                for mypar in (f.read()).split('\n')[:-1]:
                        tmp=mypar.split(' ')
                        print(tmp)
                        param[tmp[0]]=[float(ii) for ii in tmp[1:-1]]
        return param



resData =[
        [0, "Dst02300","BW",(2.334, 0.06, 0.0001 ),(0.21049, 0.1),0, () ],    # if set amplitude initials, set amp=( Re(sCentral,sWidth, step), Im(.. ,.. ,.. )), otherwise set : () , and the amp will be random from (-10,10)
        #[0, "Dst22460","BW",(2.4611,),(0.0473,), 2, () ],
        [0, "Dst12600","BW", (2.643212, 0.05, 0.0001), (0.04,0.03, 0.0001), 1, () ],
        [0, "Dst12640","BW",(2.637, 0.1, 0.0001),(0.141, 0.14, 0.0001 ),1,()],   
        #[1, "X", "BW", (3.7781,), (0.0272,), 1, ()],
]


'''
NonRes0 = {
        "channel"   : 0,            
        "name"   : "NonRes0",            
        "lineshape"   : ExponentialNonResonantLineShape,
        "spin"      : 0, 
        #"slope" :   buildLineParameter("NonRes0Slope",(param["NonRes0Slope"][0], 5*param["NonRes0Slope"][1], 0.00001)),
        #"coupling"  :   Complex(buildLineParameter("NonRes0R",(param["NonRes0R"][0],5*param["NonRes0R"][1], 0.00001)),
        #                        buildLineParameter("NonRes0I",(param["NonRes0I"][1],5*param["NonRes0I"][1], 0.00001))
        #                        )
        } 
        

collectInits["NonRes0Slope"] = rnd.Uniform(0.,1.)
collectInits["NonRes0R"] = rnd.Uniform(-1.,1.)
collectInits["NonRes0I"] = rnd.Uniform(-1.,1.)
NonRes0["slope"]= FitParameter("NonRes0Slope",  collectInits["NonRes0Slope"], 0., 1., 0.001)
NonRes0["coupling"]= Complex(
        FitParameter("NonRes0R",  collectInits["NonRes0R"], -1000., 1000., 0.001), 
        FitParameter("NonRes0I",  collectInits["NonRes0I"], -1000., 1000., 0.001) 
        ) 

NonRes1 = {
        "channel" : 1,
        "name": "FlatNRpwave",
        #"name": "FlatNRswave",
        "lineshape" : myFlatRes,
        "spin": 1,
        "coupling": Complex(
            FitParameter("FlatNRR",rnd.Uniform(-1.,1.),-1000.,1000.,0.01),
            FitParameter("FlatNRI",rnd.Uniform(-1.,1.),-1000.,1000.,0.01)
       # "coupling": Complex(buildLineParameter("FlatNRR",(4.92489e-01,5*3.62825e-02)),
       #                         buildLineParameter("FlatNRI",(3.64805e-01,5*1.10264e-01))
                                )
            
}
'''


########## ########## ##########
## add the nonresonant
########## ########## ##########
resonances = {
        #NonRes0["name"]:NonRes0,
        #NonRes1["name"]:NonRes1,
        }
########## ########## ##########



for dt in resData:
    channel = dt[0]
    name = dt[1]

    lineshape = dt[2]
    if not(lineshape =="BW"): lineshape = lineshapes[lineshape]

    mass_dt = dt[3]
    mass = buildLineParameter("m"+name,mass_dt)

    width_dt = dt[4]
    width = buildLineParameter("g"+name,width_dt)

    spin = dt[5] ## int variable, note it is the natural spin, instead of twice of it
    print("type of spin: ",type(spin))


    amp = dt[6]
    fixed = False
    if name == "Dst02300": fixed=True
    coupling = buildCoupling(name,amp,fixed)

    resonances [name] = {
            "channel"   : channel,            
            "name"      : name,            
            "mass"      : mass, 
            "width"     : width, 
            "spin"      : spin, 
            "coupling" : coupling
            } 
    if not(lineshape =="BW"): 
        resonances [name] ["lineshape"] = lineshape

if useKmatrix:
    ### k-matrix
    resonances["Ds1Kmatrix"]={
            "channel": 0,
            "name"   : "Ds1Kmatrix",            
            "spin"   : 1,  
            "mass":  [Const(2.714),Const(2.859)],
            "width": [
                Const(0.122),Const(0.160)],
                #FitParameter("w2700",0.122,0.05,0.3,0.01),
                #FitParameter("w2860",0.160,0.05,0.3,0.01),
            "coupling":Complex(Const(1.),Const(0.)),
            "betaProd":[ #for production coupling
                Complex(Const(1.),Const(0.)),
                #Complex(Const(0.3),Const(0.)),
                Complex(FitParameter("Ds2860_Prod_Real",0.3,-10.,10.,0.1),FitParameter("Ds2860_Prod_Imag",0.,-10,10.,0.1))
                ],
            }
    from math import sqrt
    gammaR1a = 0.7  ### gammaR1a**2 = 0.5
    resonances["Ds1Kmatrix"]["gammaR1toAB"]=[
            Const(gammaR1a),Const(1.)
            #FitParameter("gammaR1a",gammaR1a,gammaR1a*0.2,gammaR1a*5,gammaR1a*0.01),
            #FitParameter("gammaR1b_over_gammaR1a",1.,0.001,10.,0.1)
            ]
    gammaR2a = 0.7  ### gammaR2a**2 = 0.5
    resonances["Ds1Kmatrix"]["gammaR2toAB"]=[
            Const(gammaR2a),Const(1.)
            #FitParameter("gammaR2a",gammaR2a,gammaR2a*0.2,gammaR2a*5,gammaR2a*0.01),
            #FitParameter("gammaR2b_over_gammaR2a",1.,0.001,10.,0.1)
            ]
    resonances ["Ds1Kmatrix"] ["lineshape"] = KMatrix

for key in resonances:
    print(key,resonances[key])
for key in collectInits:
    print(key,collectInits[key])



