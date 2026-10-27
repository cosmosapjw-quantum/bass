"""Four new edge-bin inversions; qualified prior scalar helper reused only.

The interval model is assumed 32 ulps, with independent boxes discarding
correlations. It is a numerical sensitivity diagnostic, never a physical radius.
"""
import math
import mpmath as mp
from native import radiative

def interval(lo,hi):return [math.nextafter(lo,-math.inf),math.nextafter(hi,math.inf)]
def add(a,b):return interval(a[0]+b[0],a[1]+b[1])
def sub(a,b):return interval(a[0]-b[1],a[1]-b[0])
def mul(a,b):
    v=[x*y for x in a for y in b];return interval(min(v),max(v))
def div(a,b):
    if b[0]<=0<=b[1]:raise ValueError('interval divisor contains zero')
    v=[x/y for x in a for y in b];return interval(min(v),max(v))
def box(v):return interval(v-32*math.ulp(v),v+32*math.ulp(v))
def F(t):
    if t<=0:raise ValueError('positive tau required')
    if t<.05:
        q=t*t;return .5+t*(1/12+q*(-1/720+q*(1/30240+q*(-1/1209600+q/47900160))))
    return 1/(-math.expm1(-t))-1/t
def derivative(t):
    if t<.05:
        q=t*t;return 1/12+q*(-1/240+q*(1/6048+q*(-1/172800+q/5322240)))
    if t>700:return 1/(t*t)
    return 1/(t*t)-1/(4*math.sinh(t/2)**2)
def solve_ratio(r):
    if not .5<r<1:raise ValueError('inadmissible ratio; no clipping')
    lo,hi=0.,1.
    while F(hi)<r:
        hi*=2
        if hi>1e9:raise ValueError('unresolved opacity bracket')
    for _ in range(100):
        mid=(lo+hi)/2
        if mid in (lo,hi):break
        if F(mid)<r:lo=mid
        else:hi=mid
    return (lo+hi)/2,[lo,hi]

def reference70(knot,b,twog,c):
    """Independent bisection and radiative arithmetic at 70 decimal digits.

    Binary64 normalized table entries are the exact native-normalization inputs;
    no validation snapshot is read. Native constants are exact binary64 inputs.
    """
    with mp.workdps(70):
        m=mp.mpf;i,v,o=[m(knot[n][b]) for n in ['incoming_virtual','average_virtual','outgoing_virtual']]
        r=(v-i)/(o-i);lo=m(0);hi=m(1)
        fun=lambda t:1/(-mp.expm1(-t))-1/t
        while fun(hi)<r:hi*=2
        for _ in range(260):
            mid=(lo+hi)/2
            if fun(mid)<r:lo=mid
            else:hi=mid
        t=(lo+hi)/2;st=knot['inherited_completed_inverse_values'];TR=m(st['TR_eV'])
        E,A1,A2,A3,A4=map(m,twog[b]);db=mp.exp((E-m(c['E21']))/TR)
        Ts=-A2/abs(mp.expm1((E-m(c['E21']))/TR))
        Tp=-mp.exp(-m(c['E32'])/TR)/3*A3/abs(mp.expm1((E-m(c['E31']))/TR))-mp.exp(-m(c['E42'])/TR)/3*A4/abs(mp.expm1((E-m(c['E41']))/TR))
        rad=-(Ts+3*Tp)*db;lam=m(c['hPc'])/E
        gamma=8*mp.pi*m(st['H_s_inv'])*t/(m(st['x1s'])*m(st['nH_cm3'])*lam**3)
        de=abs(m(twog[b+1 if b==100 else b-1,0])-E)
        TM=(gamma-rad)*m(c['mH'])*de**2/(2*m(c['E21'])**2*A1)
        return {k:mp.nstr(x,70) for k,x in dict(r=r,tau=t,Gamma=gamma,Gamma_rad=rad,Tm_eV=TM).items()}

def reconstruct(knot,b,twog,c):
    st=knot['inherited_completed_inverse_values'];i,v,o=[float(knot[n][b]) for n in ['incoming_virtual','average_virtual','outgoing_virtual']]
    D=o-i
    if D==0:raise ValueError('zero trace jump')
    r=(v-i)/D;t,bracket=solve_ratio(r)
    if t<=1e-6:raise ValueError('edge inverse outside native exponential branch')
    _,rv=radiative(st['TR_eV'],twog,c);rad=-float(rv[0,b]+rv[1,b]);E,A1=map(float,twog[b,:2]);lam=c['hPc']/E
    gamma=8*math.pi*st['H_s_inv']*t/(st['x1s']*st['nH_cm3']*lam**3)
    de=abs(float(twog[b+1 if b==100 else b-1,0])-E)
    boundary=gamma-rad
    if not boundary>0:raise ValueError('nonpositive inferred boundary diffusion coefficient')
    TM=boundary*c['mH']*de**2/(2*c['E21']**2*A1)
    Di=sub(box(o),box(i));ri=div(sub(box(v),box(i)),Di)
    if not .5<ri[0]<=ri[1]<1:raise ValueError('assumed-roundoff ratio interval inadmissible')
    ti=interval(solve_ratio(ri[0])[1][0],solve_ratio(ri[1])[1][1])
    xi=st['rounding_model']['x1s_interval'];li=div(box(c['hPc']),box(E))
    gi=div(mul(mul(box(8*math.pi),box(st['H_s_inv'])),ti),mul(mul(xi,box(st['nH_cm3'])),mul(mul(li,li),li)))
    bi=sub(gi,box(rad));dei=sub(box(float(twog[b+1 if b==100 else b-1,0])),box(E))
    # The difference is squared using its definite sign; no zero-containing
    # power or reciprocal shortcuts are used.
    tmi=div(mul(mul(bi,box(c['mH'])),mul(dei,dei)),mul(mul(box(2.),mul(box(c['E21']),box(c['E21']))),box(A1)))
    ref=reference70(knot,b,twog,c)
    return dict(index=knot['index'],bin=b,incoming=i,average=v,outgoing=o,jump=D,ratio=r,tau=t,tau_bracket=bracket,
      ratio_relative_condition=r/(t*derivative(t)),Gamma=gamma,Gamma_rad=rad,boundary_diffusion=boundary,
      subtraction_condition=(abs(gamma)+abs(rad))/abs(boundary),lambda_cm=lam,DeltaE_eV=de,Tm_eV=TM,
      reference70=ref,relative_to_reference70={n:abs(float(ref[n])-val)/abs(float(ref[n])) for n,val in [('tau',t),('Tm_eV',TM)]},
      assumed_roundoff=dict(model='32_ULPS_EACH_BINARY64_TRACE_AND_RECONSTRUCTED_INPUT; INHERITED_X1S_BOX; NOT_PHYSICAL_CERTIFICATE',
        discarded_correlations=True,ratio_interval=ri,tau_interval=ti,Gamma_interval=gi,Gamma_rad_interval=box(rad),Tm_interval=tmi),
      validation_snapshot_used=False)
