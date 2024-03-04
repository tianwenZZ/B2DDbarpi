from math import sqrt,exp

rd = 4.
rp = 4.

def getp(mm,m1,m2):
    #print(mm,m1,m2)
    return sqrt((mm**2-(m1+m2)**2)*(mm**2-(m1-m2)**2)/(4*mm**2))

def BlattWeisskopf(p,p0,L,rd=3.):
    if L==0: return 1
    zp2=pow(p*rd ,2.)
    z02=pow(p0*rd,2.)
    if L==1: return sqrt((1+z02)/(1+zp2))
    zp4=pow(zp2,2.)
    z04=pow(z02,2.)
    if L==2: return sqrt((z04+3*z02+9)/(zp4+3*zp2+9))
    zp6=pow(zp2,3.)
    z06=pow(z02,3.)
    if L==3: return sqrt((z06+6*z04+45*z02+225)/(zp6+6*zp4+45*zp2+225))

def Angular0(ct,L): return 1.
def Angular1(ct,L): return -2.*ct
def Angular2(ct,L): return 4./3*(3*pow(ct,2)-1)
def Angular3(ct,L): return -8./5*(5*pow(ct,3)-3.*ct)
def Angular4(ct,L): return 16./35*(35*pow(ct,4)-30*pow(ct,2)+3)

def Angular(ct,L):
    if L==0: return Angular0(ct,L)
    if L==1: return Angular1(ct,L)
    if L==2: return Angular2(ct,L)
    if L==3: return Angular3(ct,L)
    if L==4: return Angular4(ct,L)


def RBW(m,m0,g0,md1,md2,spin=0):
    """
    arxiv:1711.09854,p5
    """
    L = spin
    q =getp(m,md1,md2)
    q0=getp(m0,md1,md2)

    gm = g0*pow(q/q0,2.*L+1.)*(m0/m)*pow(BlattWeisskopf(q,q0,L,rd),2.)

    module = (m0**2-m**2)**2 + (-m0*gm)**2

    return ((m0**2-m**2)/module,m0*gm/module) 

def AngularPart(m,ct,m0,spin,md1,md2,mB,md3):
    p =getp(mB,m ,md3)
    p0=getp(mB,m0,md3)
    q =getp(m,md1,md2)
    q0=getp(m0,md1,md2)
    L=spin
    angle = pow(p*q,L)*Angular(ct,L)
    Xp = BlattWeisskopf(p,p0,L,rp)
    Xq = BlattWeisskopf(q,q0,L,rd)

    return angle*Xp*Xq

def ExpM1(m,slope):
    return (exp(-slope*m),0)
def ExpM2(m,slope):
    try:
        return (exp(-slope*m**2)/(exp(-slope*2.3**2)-exp(-slope*3.4**2)),0)
    except:
        print("ERROR",m,slope)


def AmpRBW(m,ct,m0,g0,spin,md1,md2,mB,md3):
    lineshape = RBW(m,m0,g0,md1,md2,spin)
    angular = AngularPart(m,ct,m0,spin,md1,md2,mB,md3)
    return (lineshape[0]*angular,lineshape[1]*angular)

def AmpExpM2(m,ct,m0,slope,spin,md1,md2,mB,md3):
    lineshape = ExpM2(m,slope)
    angular = AngularPart(m,ct,m0,spin,md1,md2,mB,md3)
    return (lineshape[0]*angular,lineshape[1]*angular)

def AmpExpM1(m,ct,m0,slope,spin,md1,md2,mB,md3):
    lineshape = ExpM1(m,slope)
    angular = AngularPart(m,ct,m0,spin,md1,md2,mB,md3)
    return (lineshape[0]*angular,lineshape[1]*angular)


