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

from TensorFlowAnalysis.Interface import *
from TensorFlowAnalysis.Kinematics import *


def HelicityAmplitude(x, spin):
    """
    Helicity amplitude for a resonance in scalar-scalar state
      x    : cos(helicity angle)
      spin : spin of the resonance
    """
    if spin == 0:
        return Complex(Const(1.), Const(0.))
    if spin == 1:
        return Complex(x, Const(0.))
    if spin == 2:
        return Complex((3.*x**2-1.)/2., Const(0.))
    if spin == 3:
        return Complex((5.*x**3-3.*x)/2., Const(0.))
    if spin == 4:
        return Complex((35.*x**4-30.*x**2+3.)/8., Const(0.))
    return None


def RelativisticBreitWigner(m2, mres, wres):
    """
    Relativistic Breit-Wigner 
    """
    if wres.dtype is CType():
#        return 1./(CastComplex(mres*mres - m2) - Complex(Const(0.), mres)*wres)
        return tf.math.reciprocal(CastComplex(mres*mres - m2) - Complex(Const(0.), mres)*wres)
    if wres.dtype is FPType():
#        return 1./Complex(mres*mres - m2, -mres*wres)
        return tf.math.reciprocal(Complex(mres*mres - m2, -mres*wres))
    return None


def BlattWeisskopfFormFactor(q, q0, d, l):
    """
    Blatt-Weisskopf formfactor for intermediate resonance
    """
    z = q*d
    z0 = q0*d

    def hankel1(x):
        if l == 0:
            return Const(1.)
        if l == 1:
#            return 1 + x**2
            return 1 + x*x
        if l == 2:
#            x2 = x**2
            x2 = x*x
            return 9 + x2*(3. + x2)
        if l == 3:
#            x2 = x**2
            x2 = x*x
            return 225 + x2*(45 + x2*(6 + x2))
        if l == 4:
#            x2 = x**2
            x2 = x*x
            return 11025. + x2*(1575. + x2*(135. + x2*(10. + x2)))
        if l == 5:
            x2 = x**2
            return 893025. + x2*(99225. + x2*(6300. + x2*(315. + x2*(15.+x2))))
        if l == 6:
            x2 = x*x
            return 108056025. + x2*(9823275. + x2*(496125. + x2*(18900. + x2*(630. + x2*(21. + x2)))))
    return Sqrt(hankel1(z0)/hankel1(z))

def ComplexBlattWeisskopfTimesBarrier(q, q0, d, l):
    """
    Blatt-Weisskopf form factor times momentum barrier p^l for intermediate resonance
    """
    momentum_barrier = Complex(Const(1.),Const(0.))
    if l >= 1 : momentum_barrier = (q/q0)**l
    #z02 = (Real(q0)**2-Imaginary(q0)**2)*d**2
    #z2  = (Real(q)**2-Imaginary(q)**2)*d**2
    #print("type:",type(z2))
    z02 = q0**2*CastComplex(d**2)
    z2  = q**2*CastComplex(d**2)
    sign = Complex(tf.math.sign(tf.math.real(z2)),Const(0.))
    z2 = (z2+sign*z2)/CastComplex(Const(2.))

    def hankel1(x2):
        c1 = Complex(Const(1.),Const(0.))
        if l == 0:
            return c1
        if l == 1:
            return c1 + x2
        if l == 2:
            return c1 + x2*(Complex(Const(3.),Const(0.)) + x2)
    return Sqrt(hankel1(z02)/hankel1(z2)) * momentum_barrier

def ComplexPhaseSpace(q,sqs):

    return q/CastComplex(sqs)


def MassDependentWidth(m, m0, gamma0, p, p0, ff, l):
    """
    Mass-dependent width for BW amplitude
    """
#    return gamma0*((p/p0)**(2*l+1))*(m0/m)*(ff**2)
    if l == 0 : return gamma0*(p/p0)*(m0/m)*(ff*ff)
    if l == 1 : return gamma0*((p/p0)**3)*(m0/m)*(ff*ff)
    if l == 2 : return gamma0*((p/p0)**5)*(m0/m)*(ff*ff)
    if l >= 3 : return gamma0*((p/p0)**(2*l+1))*(m0/m)*(ff**2)


def OrbitalBarrierFactor(p, p0, l):
    """
    Orbital barrier factor
    """
    if l == 0 : return Ones(p)
    if l == 1 : return (p/p0)
    if l >= 2 : return (p/p0)**l



def BreitWignerLineShape(m2, m0, gamma0, ma, mb, mc, md, dr, dd, lr, ld, barrierFactor=True, ma0=None, md0=None):
    """
    Breit-Wigner amplitude with Blatt-Weisskopf formfactors, mass-dependent width and orbital barriers
    lr,ld: natural orbital angular momentum rather than twice of it
    """
    m = Sqrt(m2)
    q = TwoBodyMomentum(md, m, mc)
    q0 = TwoBodyMomentum(md if md0 is None else md0, m0, mc)
    p = TwoBodyMomentum(m, ma, mb)
    p0 = TwoBodyMomentum(m0, ma if ma0 is None else ma0, mb)
    ffr = BlattWeisskopfFormFactor(p, p0, dr, lr)
    ffd = BlattWeisskopfFormFactor(q, q0, dd, ld)
    width = MassDependentWidth(m, m0, gamma0, p, p0, ffr, lr)
    bw = RelativisticBreitWigner(m2, m0, width)
    ff = ffr*ffd
    if barrierFactor:
        b1 = OrbitalBarrierFactor(p, p0, lr) ### R -> 12
        b2 = OrbitalBarrierFactor(q, q0, ld) ### B -> R3
        ff *= b1*b2
    return bw*Complex(ff, Const(0.))

## B->R(Lcpi) p, (H_{p,p}: a_ls*p^l*B) *(R*h_{l}:q^l*B)
def myBreitWignerLineShapeSc(m2, m0, gamma0, ma, mb, dr, lr):
    """
    BW only for decay, decouple production and decay.
    """
    m = Sqrt(m2)
    p = TwoBodyMomentum(m, ma, mb)
    p0 = TwoBodyMomentum(m0,ma, mb)
    ffr = BlattWeisskopfFormFactor(p, p0, dr, lr)
    width = MassDependentWidth(m, m0, gamma0, p, p0, ffr, lr)
    bw = RelativisticBreitWigner(m2, m0, width)
    #bf = OrbitalBarrierFactor(p, p0, lr) ### R -> 12
    #ff = ffr*bf
    return bw#*Complex(ff, Const(0.))


def SubThresholdBreitWignerLineShape(m2, m0, gamma0, ma, mb, mc, md, dr, dd, lr, ld, barrierFactor=True):
    """
    Breit-Wigner amplitude (with the mass under kinematic threshold) 
    with Blatt-Weisskopf form factors, mass-dependent width and orbital barriers
    lr,ld: natural orbital angular momentum rather than twice of it
    """
    m = Sqrt(m2)
    mmin = ma+mb
    mmax = md-mc
    tanhterm = Tanh((m0 - ((mmin+mmax)/2.))/(mmax-mmin))
    m0eff = mmin + (mmax-mmin)*(1.+tanhterm)/2.
    q = TwoBodyMomentum(md, m, mc)
    q0 = TwoBodyMomentum(md, m0eff, mc)
    p = TwoBodyMomentum(m, ma, mb)
    p0 = TwoBodyMomentum(m0eff, ma, mb)
    ffr = BlattWeisskopfFormFactor(p, p0, dr, lr)
    ffd = BlattWeisskopfFormFactor(q, q0, dd, ld)
    width = MassDependentWidth(m, m0, gamma0, p, p0, ffr, lr)
    ###updated according to Liming
    width = gamma0
    bw = RelativisticBreitWigner(m2, m0, width)
    ff = ffr*ffd
    if barrierFactor:
        b1 = OrbitalBarrierFactor(p, p0, lr)
        b2 = OrbitalBarrierFactor(q, q0, ld)
        ff *= b1*b2
    return bw*Complex(ff, Const(0.))

def mySubThresholdBreitWignerLineShapeDs(m2, m0, gamma0):
    ###updated according to Liming
    return RelativisticBreitWigner(m2, m0, gamma0)

def myFlatRes(m2, m0, ma, mb, mc, md, dr, dd, lr, ld,barrierFactor=True):
    if barrierFactor:
        m = Sqrt(m2)
        q = TwoBodyMomentum(md, m, mc)
        q0 = TwoBodyMomentum(md, m0, mc)
        p = TwoBodyMomentum(m, ma, mb)
        p0 = TwoBodyMomentum(m0, ma, mb)
        b1 = OrbitalBarrierFactor(p, p0, lr)
        b2 = OrbitalBarrierFactor(q, q0, ld)
        ffr = BlattWeisskopfFormFactor(p, p0, dr, lr)
        ffd = BlattWeisskopfFormFactor(q, q0, dd, ld)
        return Complex(b1*b2*ffr*ffd*1., Const(0.))
    else :
        return Complex(Const(1.), Const(0.))



def ExponentialNonResonantLineShape(m2, m0, alpha, ma, mb, mc, md, lr, ld, dr,dd, barrierFactor=True):
    """
    Exponential nonresonant amplitude with orbital barriers
    lr,ld: natural orbital angular momentum rather than twice of it
    """
    if barrierFactor:
        m = Sqrt(m2)
        q = TwoBodyMomentum(md, m, mc)
        q0 = TwoBodyMomentum(md, m0, mc)
        p = TwoBodyMomentum(m, ma, mb)
        p0 = TwoBodyMomentum(m0, ma, mb)
        b1 = OrbitalBarrierFactor(p, p0, lr)
        b2 = OrbitalBarrierFactor(q, q0, ld)
        ffr = BlattWeisskopfFormFactor(p, p0, dr, lr)
        ffd = BlattWeisskopfFormFactor(q, q0, dd, ld)
        return Complex(ffr*b1*ffd*b2*Exp(-alpha*(m2-m0**2))/Sqrt(Exp(-2*alpha*(ma+mb)**2)-Exp(-2*alpha*(md-mc)**2)), Const(0.))
    else:
        return Complex(Exp(-alpha*(m2-m0**2)), Const(0.))
    
    
    
def ExponentialNonResonantLineShapeWithPhaseShift(m2, m0, alpha, beta, ma, mb, mc, md, lr, ld, dr,dd, barrierFactor=True):
    """
    Exponential nonresonant amplitude with orbital barriers and phase shift.
    lr,ld: natural orbital angular momentum rather than twice of it
    Note that here PDF is NOT normalized as we defined before.
    """
    if barrierFactor:
        m = Sqrt(m2)
        q = TwoBodyMomentum(md, m, mc)
        q0 = TwoBodyMomentum(md, m0, mc)
        p = TwoBodyMomentum(m, ma, mb)
        p0 = TwoBodyMomentum(m0, ma, mb)
        b1 = OrbitalBarrierFactor(p, p0, lr)
        b2 = OrbitalBarrierFactor(q, q0, ld)
        ffr = BlattWeisskopfFormFactor(p, p0, dr, lr)
        ffd = BlattWeisskopfFormFactor(q, q0, dd, ld)
        return Complex(ffr*b1*ffd*b2*Exp(-alpha*(m2-m0**2)), Const(0.)) * Complex(Cos(beta*(m2-m0**2)), -Sin(beta*(m2-m0**2)))
    else:
        return Complex(Exp(-alpha*(m2-m0**2)), Const(0.)) * Complex(Cos(beta*(m2-m0**2)), -Sin(beta*(m2-m0**2)), Const(0.))



def myExponentialNonResonantLineShapeSc(m2, m0, alpha):
    """
    only for decay, decouple production and decay.
    """
    m = Sqrt(m2)
    return Complex(Exp(-alpha*(m-m0)), Const(0.))
    return Complex(Exp(-alpha*(m2-m0**2)), Const(0.))

def myExponentialNonResonantLineShapeDs(m2, m0, alpha):
    """
    only for decay, decouple production and decay.
    """
    m = Sqrt(m2)
    return Complex(Exp(-alpha*(m-m0)), Const(0.))
    return Complex(Exp(-alpha*(m2-m0**2)), Const(0.))


def PolynomialNonResonantLineShape(m2, m0, coeffs, ma, mb, mc, md, lr, ld, barrierFactor=True):
    """
    2nd order polynomial nonresonant amplitude with orbital barriers
    coeffs: list of complex polynomial coefficients [a0, a1, a2]
    """
    #def poly(x, cs): return cs[0]*(1. + cs[1]*Complex(x, Const(0.)) + cs[2]*Complex(x**2, Const(0.)))
    def poly(x, cs): return (1. + cs[0]*Complex(x, Const(0.)) + cs[1]*Complex(x**2, Const(0.)))
    #print("poly coefficient",coeffs[0],coeffs[1])
    if barrierFactor:
        m = Sqrt(m2)
        q = TwoBodyMomentum(md, m, mc)
        q0 = TwoBodyMomentum(md, m0, mc)
        p = TwoBodyMomentum(m, ma, mb)
        p0 = TwoBodyMomentum(m0, ma, mb)
        b1 = OrbitalBarrierFactor(p, p0, lr) ##R -> 12
        b2 = OrbitalBarrierFactor(q, q0, ld)
        return poly(m - m0, coeffs) * Complex(b1*b2, Const(0.))
    else:
        return poly(m - m0, coeffs)

def myPolynomialNonResonantLineShapeSc(m2, m0, coeffs):
    """
    poly only for decay, decouple production and decay.
    """
    #def poly(x, cs): return cs[0]*(1. + cs[1]*Complex(x, Const(0.)) + cs[2]*Complex(x**2, Const(0.)))
    def poly(x, cs): return (1. + cs[0]*Complex(x, Const(0.)) + cs[1]*Complex(x**2, Const(0.)))
    #print("poly coefficient",coeffs[0],coeffs[1])
    m = Sqrt(m2)
    return poly(m - m0, coeffs)


def GounarisSakuraiLineShape(s, m, gamma, m_pi):
    """
      Gounaris-Sakurai shape for rho->pipi
        s     : squared pipi inv. mass
        m     : rho mass
        gamma : rho width
        m_pi  : pion mass
    """
    m2 = m*m
    m_pi2 = m_pi*m_pi
    ss = Sqrt(s)

    ppi2 = (s-4.*m_pi2)/4.
    p02 = (m2-4.*m_pi2)/4.
    p0 = Sqrt(p02)
    ppi = Sqrt(ppi2)

    hs = 2.*ppi/Pi()/ss*Log((ss+2.*ppi)/2./m_pi)
    hm = 2.*p0/Pi()/m*Log((m+2.*ppi)/2./m_pi)

    dhdq = hm*(1./8./p02 - 1./2./m2) + 1./2./Pi()/m2
    f = gamma*m2/(p0**3)*(ppi2*(hs-hm) - p02*(s-m2)*dhdq)

    gamma_s = gamma*m2*(ppi**3)/s/(p0**3)

    dr = m2-s+f
    di = ss*gamma_s

    r = dr/(dr**2+di**2)
    i = di/(dr**2+di**2)

    return Complex(r, i)


def FlatteLineShape(s, m, g1, g2, ma1, mb1, ma2, mb2):
    """
      Flatte line shape
        s : squared inv. mass
        m : resonance mass
        g1 : coupling to ma1, mb1
        g2 : coupling to ma2, mb2
    """
    mab = Sqrt(s)
    pab1 = TwoBodyMomentum(mab, ma1, mb1)
    rho1 = 2.*pab1/mab
    pab2 = ComplexTwoBodyMomentum(mab, ma2, mb2)
    rho2 = 2.*pab2/CastComplex(mab)
    gamma = (CastComplex(g1**2*rho1) + CastComplex(g2**2)*rho2)/CastComplex(m)
    return RelativisticBreitWigner(s, m, gamma)


def SpecialFlatteLineShape(m2, m0, gamma0, ma, mb, mc, md, dr, dd, lr, ld, barrierFactor=True):
    """
    Flatte amplitude with Blatt-Weisskopf formfactors, 2 component mass-dependent width and orbital barriers as done in Pentaquark analysis for L(1405) that peaks below pK threshold.
    ma = [ma1, ma2] and mb = [mb1, mb2]
    NB: The dominant decay for a given resonance should be the 2nd channel i.e. R -> a2 b2. 
    This is because (as done in pentaquark analysis) in calculating p0 (used in Blatt-Weisskopf FF) for both channels, the dominant decay is used.
    Another assumption made in pentaquark is equal couplings ie. gamma0_1 = gamma0_2 = gamma and only differ in phase space factors 
    """
    ma1, ma2 = ma[0], ma[1]
    mb1, mb2 = mb[0], mb[1]
    m = Sqrt(m2)
    # D->R c
    q = TwoBodyMomentum(md, m, mc)
    q0 = TwoBodyMomentum(md, m0, mc)
    ffd = BlattWeisskopfFormFactor(q, q0, dd, ld)
    # R -> a1 b1
    p_1 = TwoBodyMomentum(m,  ma1, mb1)
    p0_1 = TwoBodyMomentum(m0, ma1, mb1)
    ffr_1 = BlattWeisskopfFormFactor(p_1, p0_1, dr, lr)
    # R -> a2 b2
    p_2 = TwoBodyMomentum(m,  ma2, mb2)
    p0_2 = TwoBodyMomentum(m0, ma2, mb2)
    ffr_2 = BlattWeisskopfFormFactor(p_2, p0_2, dr, lr)
    # lineshape
    width_1 = MassDependentWidth(
        m, m0, gamma0, p_1, p0_2, BlattWeisskopfFormFactor(p_1, p0_2, dr, lr), lr)
    width_2 = MassDependentWidth(m, m0, gamma0, p_2, p0_2, ffr_2, lr)
    width = width_1 + width_2
    bw = RelativisticBreitWigner(m2, m0, width)
    # Form factor def
    ff = ffr_1*ffd
    if barrierFactor:
        b1 = OrbitalBarrierFactor(p_1, p0_1, lr)
        b2 = OrbitalBarrierFactor(q, q0, ld)
        ff *= b1*b2
    return bw*Complex(ff, Const(0.))


def NonresonantLASSLineShape(m2ab, a, r, ma, mb):
    """
      LASS line shape, nonresonant part
    """
    m = Sqrt(m2ab)
    q = TwoBodyMomentum(m, ma, mb)
    cot_deltab = 1./a/q + 1./2.*r*q
    ampl = CastComplex(m)/Complex(q*cot_deltab, -q)
    return ampl


def ResonantLASSLineShape(m2ab, m0, gamma0, a, r, ma, mb):
    """
      LASS line shape, resonant part
    """
    m = Sqrt(m2ab)
    q0 = TwoBodyMomentum(m0, ma, mb)
    q = TwoBodyMomentum(m, ma, mb)
    cot_deltab = 1./a/q + 1./2.*r*q
    phase = Atan(1./cot_deltab)
    width = gamma0*q/m*m0/q0
    ampl = RelativisticBreitWigner(
        m2ab, m0, width)*Complex(Cos(phase), Sin(phase))*CastComplex(m2ab*gamma0/q0)
    return ampl


def DabbaLineShape(m2ab, b, alpha, beta, ma, mb):
    """
      Dabba line shape
    """
    mSum = ma + mb
    m2a = ma**2
    m2b = mb**2
    sAdler = max(m2a, m2b) - 0.5*min(m2a, m2b)
    mSum2 = mSum*mSum
    mDiff = m2ab - mSum2
    rho = Sqrt(1. - mSum2/m2ab)
    realPart = 1.0 - beta*mDiff
    imagPart = b*Exp(-alpha*mDiff)*(m2ab-sAdler)*rho
    denomFactor = realPart*realPart + imagPart*imagPart
    ampl = Complex(realPart, imagPart)/CastComplex(denomFactor)
    return ampl


def ConstructHelicityCouplingFromLS_ProdSc(ja, jb, jc, lb, lc, L,S,mBu,mSq,mOther,m0Res,dd,cc):
    m = Sqrt(mSq)
    q = TwoBodyMomentum(mBu, m, mOther)
    q0 = TwoBodyMomentum(mBu, m0Res, mOther)
    ffd = BlattWeisskopfFormFactor(q, q0, dd, L/2)
    bf = OrbitalBarrierFactor(q, q0, L/2) ### R -> 12
    ff = ffd*bf
    coeff = math.sqrt((L+1)/(ja+1))*Clebsch(jb, lb, jc,   -lc,  S, lb-lc)* Clebsch( L,  0, S,  lb-lc, ja, lb-lc)
    #print("CG prod:",coeff,ja, jb, jc, lb, lc, L,S)
    return Complex(Const(float(coeff)), Const(0.))*cc*Complex(ff,Const(0.))

 
def ConstructHelicityCouplingFromLS_DecaySc(ja, jb, jc, lb, lc, l,s,mSq,mDau1,mDau2,m0Res,dr,cc):
    m = Sqrt(mSq)
    p = TwoBodyMomentum(m, mDau1, mDau2)
    p0 = TwoBodyMomentum(m0Res, mDau1, mDau2)
    ffd = BlattWeisskopfFormFactor(p, p0, dr, l/2)
    bf = OrbitalBarrierFactor(p, p0, l/2) 
    ff = ffd*bf
    coeff = math.sqrt((l+1)/(ja+1))*Clebsch(jb, lb, jc,   -lc,  s, lb-lc) *Clebsch( l,  0, s,  lb-lc, ja, lb-lc)
    #print("CG decay:",coeff,ja, jb, jc, lb, lc, l,s)
    return Complex(Const(float(coeff)), Const(0.))*cc*Complex(ff,Const(0.))

 
def ConstructHelicityCouplingFromLS_ProdDs(mBu,mSq,mOther,m0Res,dd,L,cc):
    m = Sqrt(mSq)
    q = TwoBodyMomentum(mBu, m, mOther)
    q0 = TwoBodyMomentum(mBu, m0Res, mOther)
    #print(q,q0,dd,L)
    ffd = BlattWeisskopfFormFactor(q, q0, dd, L/2)
    bf = OrbitalBarrierFactor(q, q0, L/2) ### R -> 12
    ff = ffd*bf
    return cc*Complex(ff,Const(0.))

 
def ConstructHelicityCouplingFromLS_DecayDs(ja, jb, jc, lb, lc, l,s,mSq,mDau1,mDau2,m0Res,dr,cc):
    m = Sqrt(mSq)
    p = TwoBodyMomentum(m, mDau1, mDau2)
    p0 = TwoBodyMomentum(m0Res, mDau1, mDau2)
    ffd = BlattWeisskopfFormFactor(p, p0, dr, l/2)
    bf = OrbitalBarrierFactor(p, p0, l/2) 
    ff = ffd*bf
    coeff = math.sqrt((l+1)/(ja+1))*Clebsch(jb, lb, jc,   -lc,  s, lb-lc) *Clebsch( l,  0, s,  lb-lc, ja, lb-lc)
    #print("CG Ds decay:",coeff,ja, jb, jc, lb, lc, l,s)
    return Complex(Const(float(coeff)), Const(0.))*cc*Complex(ff,Const(0.))

 
def KMatrix(s,
        betaR1,betaR2,  ## coupling of B->Ds2700, B->Ds2860 decay, w/o Bf factor, complex
        gammaR1bRatio, ## coupling of R1->channel a, R1->channel b
        gammaR2bRatio, ## coupling of R2->channel a, R2->channel b
        mR,wR, #masses and widths of resonances
        m1, m2,  # m1 = [m1a, m1b] and m2 = [m2a, m2b]
        m3, mB, dR, dB, lR, lB,
        Khatnonres={"aa": Const(0.), "ab": Const(0.), "bb": Const(0.)}, #nonresonant term
        Phatnonres={"aa": Complex(Const(0.),Const(0.)), "bb": Complex(Const(0.),Const(0.))},  ## nonresonant term
        barrierFactor=True,
       
):

    complex0 = Complex(Const(0.),Const(0.))
    complex1 = Complex(Const(1.),Const(0.))
    complexI = Complex(Const(0.),Const(1.))

    mR1,mR2 = mR[0],mR[1]
    wR1,wR2 = wR[0],wR[1]
    m1a, m1b = m1[0], m1[1]  #m1a=m(D+)  m1b=m(D+*)
    m2a, m2b = m2[0], m2[1]  #m2a=m(K0)  m2b=m(K0)
    sqs = Sqrt(s)
    mNRa = 0.5*(mB-m1a-m2a-m3)   # like the definition in flatnr, only need mB-mNR-m3>0
    mNRb = 0.5*(mB-m1b-m2b-m3)

    gammaR1a = 1/Sqrt(1+Pow(gammaR1bRatio,2))
    gammaR2a = 1/Sqrt(1+Pow(gammaR2bRatio,2))
    gammaR1b = gammaR1bRatio*gammaR1a
    gammaR2b = gammaR2bRatio*gammaR2a

    # break up momentum, force to be complex
    q_a  = ComplexTwoBodyMomentum(sqs,  m1a, m2a) #for (Ds12700)->D+ K0
    q_b  = ComplexTwoBodyMomentum(sqs,  m1b, m2b) ## take care for negative momentum   \ for (Ds12860)->D*+ K0

    q0_R1_a = ComplexTwoBodyMomentum(mR1, m1a, m2a) # for Ds12700->D+ K0
    q0_R1_b = ComplexTwoBodyMomentum(mR1, m1b, m2b) # for Ds12700->D*+ K0
    q0_R2_a = ComplexTwoBodyMomentum(mR2, m1a, m2a) # for Ds12860->D+ K0
    q0_R2_b = ComplexTwoBodyMomentum(mR2, m1b, m2b) # for Ds12860->D*+ K0
    q0_NR_a = ComplexTwoBodyMomentum(mNRa, m1a, m2a)
    q0_NR_b = ComplexTwoBodyMomentum(mNRb, m1b, m2b)

    #It causes problems ... ?????  
    B_R1_a = ComplexBlattWeisskopfTimesBarrier(q_a,q0_R1_a,dR,lR)
    B_R1_b = ComplexBlattWeisskopfTimesBarrier(q_b,q0_R1_b,dR,lR)
    B_R2_a = ComplexBlattWeisskopfTimesBarrier(q_a,q0_R2_a,dR,lR)
    B_R2_b = ComplexBlattWeisskopfTimesBarrier(q_b,q0_R2_b,dR,lR)
    B_NR_a = ComplexBlattWeisskopfTimesBarrier(q_a,q0_NR_a,dR,lR)
    B_NR_b = ComplexBlattWeisskopfTimesBarrier(q_b,q0_NR_b,dR,lR)

    #return B_R1_a, tested good

    #ghat
    rho0_R1_a = ComplexPhaseSpace(q0_R1_a,mR1)
    rho0_R1_b = ComplexPhaseSpace(q0_R1_b,mR1)
    rho0_R2_a = ComplexPhaseSpace(q0_R2_a,mR2)
    rho0_R2_b = ComplexPhaseSpace(q0_R2_b,mR2)

    ghat_R1_a = CastComplex(Sqrt(mR1*wR1)*gammaR1a)*B_R1_a/Sqrt(rho0_R1_a)
    ghat_R1_b = CastComplex(Sqrt(mR1*wR1)*gammaR1b)*B_R1_b/Sqrt(rho0_R1_b)
    ghat_R2_a = CastComplex(Sqrt(mR2*wR2)*gammaR2a)*B_R2_a/Sqrt(rho0_R2_a)
    ghat_R2_b = CastComplex(Sqrt(mR2*wR2)*gammaR2b)*B_R2_b/Sqrt(rho0_R2_b)

    # k-matrix, complex matrix
    mR1Sq_s = CastComplex(mR1**2-s)
    mR2Sq_s = CastComplex(mR2**2-s)
    Khat_aa = ghat_R1_a*ghat_R1_a/mR1Sq_s + ghat_R2_a*ghat_R2_a/mR2Sq_s + Complex(Khatnonres["aa"],Const(0.))   # Khatnonres is Real!!!  NEED CORRECT
    Khat_ab = ghat_R1_a*ghat_R1_b/mR1Sq_s + ghat_R2_a*ghat_R2_b/mR2Sq_s + Complex(Khatnonres["ab"],Const(0.))
    Khat_ba = ghat_R1_b*ghat_R1_a/mR1Sq_s + ghat_R2_b*ghat_R2_a/mR2Sq_s + Complex(Khatnonres["ab"],Const(0.))
    Khat_bb = ghat_R1_b*ghat_R1_b/mR1Sq_s + ghat_R2_b*ghat_R2_b/mR2Sq_s + Complex(Khatnonres["bb"],Const(0.))


    # rho
    rho_a = ComplexPhaseSpace(q_a,sqs)
    rho_b = ComplexPhaseSpace(q_b,sqs)

    ## 1-iKhat*rho n^2, complex

    Maa = complex1-complexI*Khat_aa*rho_a
    Mab = complex0-complexI*Khat_ab*rho_b
    Mba = complex0-complexI*Khat_ba*rho_a
    Mbb = complex1-complexI*Khat_bb*rho_b


    ## inverse 1-iK\rho n^2,
    """
    |a,b|  |d,-b|   |ad-bc,0|
    |c,d|x |-c,a| = |0,ad-bc|
    """
    det = Maa*Mbb-Mab*Mba
    #mReal,mImag = Real(det),Imaginary(det)
    #RSq = mReal**2 + mImag**2
    #iDet= Complex(mReal/Rsq,-mImag/Rsq)
    iDet = complex1/det

    iMaa = iDet*Mbb
    iMab = -iDet*Mab
    #iMba = -iDet*Mba
    #iMbb = iDet*Maa


    ### P-vector, complex?
    # B->R 3
    p = ComplexTwoBodyMomentum(mB, sqs, m3)
    p0_R1 = ComplexTwoBodyMomentum(mB, mR1, m3)
    p0_R2 = ComplexTwoBodyMomentum(mB, mR2, m3)
    p0_NR = ComplexTwoBodyMomentum(mB, mNRa, m3)  ###  can choose mNRa?? is mNRb ok ??? ... emmm it seems take mNRa will be consistent with single resonance form because single resonance calculates B+ -> NRpwave(D+ K0) D0b with barrier factor calculated by mNRa=0.5(md-mDp-mD0b-mK0) rather than mNRb=0.5(md-mDp*-mD0b-mK0)
    B_B_R1 = ComplexBlattWeisskopfTimesBarrier(p, p0_R1, dB, lB)
    B_B_R2 = ComplexBlattWeisskopfTimesBarrier(p, p0_R2, dB, lB)
    B_B_NR = ComplexBlattWeisskopfTimesBarrier(p, p0_NR, dB, lB) # produce barrier factor for nonres p-wave


    # Phat_a = betaR1*B_B_R1*ghat_R1_a/mR1Sq_s + betaR2*B_B_R2*ghat_R2_a/mR2Sq_s + Phatnonres*BBprod*BBdecay...   Phatnonres is complex
    Phat_a = betaR1*B_B_R1*ghat_R1_a/mR1Sq_s + betaR2*B_B_R2*ghat_R2_a/mR2Sq_s + B_B_NR*B_NR_a*Phatnonres["aa"]
    Phat_b = betaR1*B_B_R1*ghat_R1_b/mR1Sq_s + betaR2*B_B_R2*ghat_R2_b/mR2Sq_s + B_B_NR*B_NR_b*Phatnonres["bb"]


    ### amplitude
    Amp_a = iMaa*Phat_a + iMab*Phat_b

    return Amp_a



