import os
import time
from subprocess import Popen
import subprocess
import sys

#from resonanceTemplate import resonances,collectInits

from ROOT import TRandom3, TMath


for i in ['logs']:
    if not os.path.exists(i):
        os.mkdir(i)

njobsPerGPU=1
#njobs=40
njobs=int(sys.argv[1])


jobs=[]
stat=[0,0,0,0]
initseed_=[]

date = "%i_%i_%i_%i"%tuple(time.localtime(time.time())[1:5])


for ifit in range(njobs):
    ######initiate random seed tag
    rnd=TRandom3()
    rnd.SetSeed(0)
    InitSeed=str(rnd.GetSeed())+"_"+date
    if not os.path.exists('logs/log_{0}.txt'.format(InitSeed)):
        print('logs/log_{0}.txt'.format(InitSeed))
        initseed_.append(InitSeed)
        #command = 'python3 1.B2DpD0K0_bkg.py {0} {2} > logs/log_{1}.txt 2>&1'.format(InitSeed,InitSeed,ifit%4)



nps=njobsPerGPU*len(stat)
nrest=njobs
ndone=0
ntask=0
task_list=[]
print(njobs, ndone)


# stat[igpu]= 1 True, is working 
# stat[igpu]=0 False, is not working

def findrest(stat):
    for i in range(len(stat)):
        if stat[i] < njobsPerGPU:
            return i
    if i==len(stat):
        print("#######no gpu at rest!!! ")
        return -999

RUN = True
while RUN:
    time.sleep(1)
    if nps>0 and nrest>0:
        igpu=findrest(stat)
        #igpu=3
        #print("rest gpu is %f" %(igpu))
        nps = nps-1
        nrest = nrest-1
        command = 'python3 1.B2D0D0pi.py {0} {1} > logs/log_{2}.txt 2>&1'.format(initseed_[ntask], igpu, initseed_[ntask])
        #command = 'python3 2.B2DpD0K0_bkg_kMatrix.py {0} {1} > logs/log_{2}.txt 2>&1'.format(initseed_[ntask], igpu, initseed_[ntask])

        ps = Popen(command, shell=True)
        print(command)
        stat[igpu] +=1
        task_list.append((ps, ntask, command))
        ntask+=1
    for proc,num,cmd in task_list:
        if proc.poll() is not None:
            nps += 1
            ndone += 1
            igpu=int((cmd.split(' '))[3])
            task_list.remove((proc,num,cmd))
            proc.terminate()
            stat[igpu]-=1
            print("fit #{0} finished, {1} jobs to do...".format(num,njobs-ndone))

    if nrest==0 and ndone==njobs:
        RUN = False


from ResultsExtractor import ResultsExtractor
from resonanceTemplate import resonances
#from resonanceTemplateKMatrix import resonances
#from resonanceTemplateX23200_X2900 import resonances
#from resonanceTemplateKMatrix_FlatNRpwave_X12900 import resonances

# Return the list of resonance names from the dictionary above
def listComponentNames(res) : 
    return sorted(res.keys())


tmp=""
for name in listComponentNames(resonances):
    tmp+=(name+"_")
tmp+="[0-9]*_"+date+"*"
ResultsExtractor(tmp)
