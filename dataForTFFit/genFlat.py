mb=5.27925000
m1=1.86484000  #D0
m2=1.86486000 #D0bar
m3=0.13957018 #pi+


from ROOT import *

from utils import getp
from math import sqrt,acos
from array import array



vb = TLorentzVector(0,0,0,mb)

masses = [m1,m2,m3]
masses = array("d",[m1,m2,m3])

event= TGenPhaseSpace()
event.SetDecay(vb, 3, masses)
rnd=TRandom3()
maxWt=0.

ntoys=850000


f=TFile("flat-toy.root","recreate")
tr=TTree("tree","")


cosHel13=array("d",[0.]);  tr.Branch("cosHel13",cosHel13,"cosHel13/D")
m13=array("d",[0.]);       tr.Branch("m13",m13,"m13/D")
m13Sq=array("d",[0.]);     tr.Branch("m13Sq",m13Sq,"m13Sq/D")
pq13=array("d",[0.]);      tr.Branch("pq13",pq13,"pq13/D")
mp13=array("d",[0.]);      tr.Branch("mp13",mp13,"mp13/D")
thetap13=array("d",[0.]);  tr.Branch("thetap13",thetap13,"thetap13/D")

cosHel12=array("d",[0.]);  tr.Branch("cosHel12",cosHel12,"cosHel12/D")
m12=array("d",[0.]);       tr.Branch("m12",m12,"m12/D")
m12Sq=array("d",[0.]);     tr.Branch("m12Sq",m12Sq,"m12Sq/D")
pq12=array("d",[0.]);      tr.Branch("pq12",pq12,"pq12/D")
mp12=array("d",[0.]);      tr.Branch("mp12",mp12,"mp12/D")
thetap12=array("d",[0.]);  tr.Branch("thetap12",thetap12,"thetap12/D")


cosHel23=array("d",[0.]);  tr.Branch("cosHel23",cosHel23,"cosHel23/D")
m23=array("d",[0.]);       tr.Branch("m23",m23,"m23/D")
m23Sq=array("d",[0.]);     tr.Branch("m23Sq",m23Sq,"m23Sq/D")
pq23=array("d",[0.]);      tr.Branch("pq23",pq23,"pq23/D")
mp23=array("d",[0.]);      tr.Branch("mp23",mp23,"mp23/D")
thetap23=array("d",[0.]);  tr.Branch("thetap23",thetap23,"thetap23/D")

def cosHel(v1,v2,v3):
    v12=v1+v2
    va=TLorentzVector(v1)
    vb=TLorentzVector(v3)
    va.Boost(-v12.BoostVector())
    vb.Boost(-v12.BoostVector())

    vap3 = va.Vect()
    vbp3 = vb.Vect()

    return vap3.Dot(vbp3)/vap3.Mag()/vbp3.Mag()

for n in range(ntoys):
    weight = event.Generate()
    v1 = event.GetDecay(0)
    v2 = event.GetDecay(1)
    v3 = event.GetDecay(2)
    if weight>maxWt: maxWt = weight
    if weight < rnd.Uniform(0.,1.):continue
    m12[0] = (v1+v2).M()
    m13[0] = (v1+v3).M()
    m23[0] = (v2+v3).M()
    m12Sq[0] = m12[0]*m12[0]
    m13Sq[0] = m13[0]*m13[0]
    m23Sq[0] = m23[0]*m23[0]
    pq12[0]=getp(m12[0],m1,m2)*getp(mb,m12[0],m3)
    pq13[0]=getp(m13[0],m1,m3)*getp(mb,m13[0],m2)
    pq23[0]=getp(m23[0],m2,m3)*getp(mb,m23[0],m1)
    ##12: d1^d3 in 12
    cosHel12[0] = cosHel(v1,v2,v3)
    mp12[0] = 1./TMath.Pi()*acos(2*(m12[0]-(m1+m2))/(mb-m3-m1-m2)-1);
    thetap12[0]=1./TMath.Pi()*acos(cosHel12[0]);
    ##23: d1^d3 in 23
    cosHel23[0] = cosHel(v3,v2,v1)
    mp23[0] = 1./TMath.Pi()*acos(2*(m23[0]-(m2+m3))/(mb-m3-m1-m2)-1);
    thetap23[0]=1./TMath.Pi()*acos(cosHel23[0]);
    ##13: d2^d3 in 13
    cosHel13[0] = cosHel(v3,v1,v2)
    mp13[0] = 1./TMath.Pi()*acos(2*(m13[0]-(m1+m3))/(mb-m3-m1-m2)-1);
    thetap13[0]=1./TMath.Pi()*acos(cosHel13[0]);
    tr.Fill()

    if n%100000 == 0:
        print("%d events finished!"%(n))

print(maxWt)
tr.Write()


