from math import log,exp,sqrt
import sys



def getDivisions235(N):
    # 4^n=N
    maxN4  = int(log(N)/log(4))
    maxN9  = int(log(N)/log(9))
    maxN25 = int(log(N)/log(25))
    
    #print("*****"*10,N)
    #print(maxN4,maxN9,maxN25)
    minDiff = 100
    rlt=""
    for N4 in range(maxN4+1):
        for N9 in range(maxN9+1):
            for N25 in range(maxN25+1):
                diff = N+1 - (pow(4,N4)*pow(9,N9)*pow(25,N25))
                if diff<0: continue
                if minDiff > diff:
                    minDiff = diff
                    rlt = (N4,N9,N25)
    return rlt#,pow(4,rlt[0])*pow(9,rlt[1])*pow(25,rlt[2])
    
#for N in range(1,200):
#    rlt = getDivisions235(N)
#    print(N,rlt,pow(4,rlt[0])*pow(9,rlt[1])*pow(25,rlt[2]))
#
#print("*"*100)


def divideSub(binData,divisions):
    xl,xh,yl,yh,xys = binData
    if divisions[0]==1:
        result = []
        yIn=[]
        for x,y in xys:
            if x<xl or x>xh:continue
            if y<yl or y>yh:continue
            yIn.append(y)
        yIn.sort()
        binsY = [yl]+[yIn[int(1.*ii*len(yIn)/divisions[1])] for ii in range(1,divisions[1])]+[yh]
        for ii in range(len(binsY)-1):
            subXY2=[]
            for x,y in xys:
                if y<binsY[ii] or y>binsY[ii+1]:continue
                subXY2.append((x,y))
            result.append((xl,xh,binsY[ii],binsY[ii+1],subXY2))

        return result
    if divisions[0]>1:
        result=[]
        xIn=[]
        filterXY=[]
        for x,y in xys:
            if x<xl or x>xh:continue
            if y<yl or y>yh:continue
            filterXY.append((x,y))
            xIn.append(x)
        xIn.sort()
        binsX = [xl]+[xIn[int(1.*ii*len(xIn)/divisions[0])] for ii in range(1,divisions[1])]+[xh]
        for ii in range(len(binsX)-1):
            subXY1=[]
            for x,y in filterXY:
                if x< binsX[ii] or x>binsX[ii+1]:continue
                subXY1.append((x,y))
            result.extend(divideSub((binsX[ii],binsX[ii+1],yl,yh,subXY1),(1,divisions[1])))
        return result

final=""
##data0 = [(xl,xh,yl,yh,[(x,y)...])}
def iterDivide(data0,divisions,idi):
    global final
    totalInter = len(divisions)
    result=[]
    for dd in data0:
        #print("start:",idi,dd[0:-1],len(dd[-1]))
        data1=divideSub(dd,divisions[idi])
        #for xx in data1:
        #    print("result:",idi,xx[0:-1],len(xx[-1]))
        result.extend(data1)
    if idi==(totalInter-1): 
        final=result
    else:
        iterDivide(result,divisions,idi+1)


####################### #######################
####################### #######################
from ROOT import TRandom3,TH2Poly,TCanvas,TLine,gROOT,TFile,gPad
mB=5.27925000
mDp=1.86962000 #D+
mD0=1.86486000 #D0
mK0=0.49761400 #K0
m0=5.27925000
m1=1.86962000 #D+
m1p=2.01026
m2=1.86486000 #D0
m3=0.49761400 #K0

gROOT.SetBatch()

rF=TFile("../dataForTFFit/Data_Eff_Bkg_All.root")
trd=rF.Get("trDP")
rd=[(evt.m13Sq,evt.m12Sq) for evt in trd]

ndivisions = getDivisions235(int(len(rd)/100.))
maxUsed = max(ndivisions[0],max(ndivisions[1],ndivisions[2]))
divs=[]
for ii in range(maxUsed):
    if ii < ndivisions[0]:divs.append((2,2))
    if ii < ndivisions[1]:divs.append((3,3))
    if ii < ndivisions[2]:divs.append((5,5))
print(ndivisions,divs)


#### the main body to find the poly2
iterDivide([((m1+m3)**2,(m0-m2)**2,(m1+m2)**2,(m0-m3)**2,rd)],divs,0)

bins=[]
for ff in final:
    bins.append(ff[0:-1])
    #print("%0.2f:%0.2f:%0.2f:%0.2f"%tuple(ff[0:-1]),len(ff[-1]))


poly2Data=TH2Poly("Data","Data",(m1+m3)**2,(mB-m2)**2,(m1+m2)**2,(mB-m3)**2)
poly2Toy =TH2Poly("Toy","Toy",(m1+m3)**2,(mB-m2)**2,(m1+m2)**2,(mB-m3)**2)
poly2Pull=TH2Poly("Pull","Pull",(m1+m3)**2,(mB-m2)**2,(m1+m2)**2,(mB-m3)**2)
for bb in bins:
    print(bb)
    poly2Data.AddBin(bb[0],bb[2],bb[1],bb[3])
    poly2Toy.AddBin(bb[0],bb[2],bb[1],bb[3])
    poly2Pull.AddBin(bb[0],bb[2],bb[1],bb[3])
