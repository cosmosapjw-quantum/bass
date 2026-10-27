"""Source-bound binary64 saved-triple inverse; no native solver invocation."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def hx(v): return float.fromhex(v['binary64_hex'])
def load(name): return json.loads((ROOT/'inputs'/name).read_text())

def interval(lo,hi):
    return [math.nextafter(lo,-math.inf),math.nextafter(hi,math.inf)]
def add(a,b):return interval(a[0]+b[0],a[1]+b[1])
def sub(a,b):return interval(a[0]-b[1],a[1]-b[0])
def mul(a,b):
    v=[x*y for x in a for y in b]
    return interval(min(v),max(v))
def div(a,b):
    if b[0]<=0<=b[1]:raise ValueError('division interval contains zero')
    v=[x/y for x in a for y in b]
    return interval(min(v),max(v))
def ulp_interval(v):
    e=32*math.ulp(v)
    return interval(v-e,v+e)

def F(t):
    if t <= 0: raise ValueError('positive tau required')
    if t < .05:
        q=t*t
        return .5+t*(1/12+q*(-1/720+q*(1/30240+q*(-1/1209600+q/47900160))))
    return 1/(-math.expm1(-t))-1/t

def derivative(t):
    if t < .05:
        q=t*t
        return 1/12+q*(-1/240+q*(1/6048+q*(-1/172800+q/5322240)))
    if t > 700: return 1/(t*t)
    return 1/(t*t)-1/(4*math.sinh(t/2)**2)

def solve_ratio(r):
    if not .5 < r < 1: raise ValueError('inadmissible ratio; no clipping')
    lo,hi=0.,1.
    while F(hi)<r:
        hi*=2
        if hi>1e9: raise ValueError('unresolved opacity bracket')
    for _ in range(100):
        mid=(lo+hi)/2
        if mid in (lo,hi): break
        if F(mid)<r:lo=mid
        else:hi=mid
    return (lo+hi)/2,[lo,hi]

def background(packet,index):
    c={k:hx(v) for k,v in packet['constants'].items()}
    h=hx(packet['clock']['dlna']); z=8001.*math.exp(-h*(packet['clock']['izH0']+index))-1.
    a=1.+z
    TR=c['kBoltz_eV_per_K']*c['T0_K']*a/(c['fsR']*c['fsR']*c['meR'])
    n0=c['nH0_coefficient']*c['obh2']*(1.-c['Y'])
    nH=1e-6*n0*a*a*a
    rad=c['photon_density_coefficient']*c['T0_K']*c['T0_K']*c['T0_K']*c['T0_K']
    rho=[c['omh2']*a*a*a,c['okh2']*a*a,
         c['odeh2']*a**(3*(1+c['w0']))*math.exp(3*c['wa']*(math.log(a)-1+1/a)),
         rad*a*a*a*a,0.]
    rho[4]=c['neutrino_coefficient']*rho[3]*c['Nnueff']
    density=0.
    for v in rho:density+=v
    H=c['Hubble_coefficient_s_inv']*math.sqrt(density)
    return dict(native_z=z,TR=TR,nH_cm3=nH,H_s_inv=H,constants=c)

def coefficient(packet,bg,bin_number):
    row=next(x for x in packet['table_rows'] if x['bin']==bin_number)
    r={k:hx(v) for k,v in row['fields'].items()};c=bg['constants'];TR=bg['TR'];E=r['Eb_eV']
    rr=(c['fsR']*c['fsR']*c['fsR']*c['fsR'])**2*c['meR']
    db=math.exp((E-c['E21_eV'])/TR)
    Ts=-rr*r['A2s']/abs(math.exp((E-c['E21_eV'])/TR)-1.)
    Tp=-math.exp(-c['E32_eV']/TR)/3.*rr*r['A3s3d']/abs(math.exp((E-c['E31_eV'])/TR)-1.)
    Tp-=math.exp(-c['E42_eV']/TR)/3.*rr*r['A4s4d']/abs(math.exp((E-c['E41_eV'])/TR)-1.)
    Gamma=-(Ts*db+Tp*3.*db)
    lam=c['hPc_eV_cm']/E/c['fsR']/c['fsR']/c['meR']
    scale=8*math.pi*bg['H_s_inv']/(Gamma*lam**3*bg['nH_cm3'])
    return dict(Gamma=Gamma,Cs=-Ts,Cp=-Tp,lambda_cm=lam,x1s_per_tau=scale)

def reconstruct(packet,lyman,trace):
    i=hx(trace['incoming_derived_from_saved_prefix']);v=hx(trace['average_stored']);o=hx(trace['outgoing_stored'])
    D=o-i;B=v-i
    if D==0:raise ValueError('unresolved jump')
    r=B/D;t,bracket=solve_ratio(r)
    if t<=1e-6:raise ValueError('selected inverse enters native quadratic branch')
    bg=background(packet,trace['index']);co=coefficient(packet,bg,trace['bin']);x1s=t*co['x1s_per_tau']
    ly=next(x for x in lyman['records'] if x['index']==trace['index'])
    da,db,dg=[hx(x) for x in ly['outgoing_lyman_departures']]
    c=bg['constants'];yp=3*da
    ys_b=db*math.exp(c['E32_eV']/bg['TR']);ys_g=dg*math.exp(c['E42_eV']/bg['TR'])
    A=-math.expm1(-t);feq=i+D/A
    p1=co['Gamma']*feq;p2=co['Cp']*yp
    ys_v=(p1-p2)/co['Cs']
    cancellation=(abs(p1)+abs(p2))/abs(p1-p2) if p1!=p2 else None
    w=math.exp(-c['E21_eV']/bg['TR'])
    # 32 ulps is an assumed trace/coefficient arithmetic model, not physics.
    ei,ev,eo=[32*math.ulp(x) for x in [i,v,o]]
    eD=ei+eo;eB=ei+ev
    if abs(D)<=eD:raise ValueError('jump unresolved under assumed rounding model')
    er=(eB+abs(r)*eD)/(abs(D)-eD)
    if not .5<r-er<r+er<1:raise ValueError('rounding-model ratio interval inadmissible')
    tl=solve_ratio(r-er)[1][0];tu=solve_ratio(r+er)[1][1]
    H,G,L,n=bg['H_s_inv'],co['Gamma'],co['lambda_cm'],bg['nH_cm3']
    eH,eG,eL,en=[32*math.ulp(x) for x in [H,G,L,n]]
    xl=8*math.pi*(H-eH)*tl/((G+eG)*(L+eL)**3*(n+en))
    xu=8*math.pi*(H+eH)*tu/((G-eG)*(L-eL)**3*(n-en))
    # Conservatively decouple correlated trace/tau/feq quantities. The source
    # intervals below assume32ulps for each represented trace/coefficient.
    ii=ulp_interval(i);oo=ulp_interval(o);Di=sub(oo,ii)
    Ai=interval(-math.expm1(-tl),-math.expm1(-tu))
    feqi=add(ii,div(Di,Ai))
    Gi=ulp_interval(G);Cpi=ulp_interval(co['Cp']);Csi=ulp_interval(co['Cs']);ypi=ulp_interval(yp)
    numerator_i=sub(mul(Gi,feqi),mul(Cpi,ypi));ysi=div(numerator_i,Csi)
    virtual_assumed_rel=max(abs(ysi[0]-ys_v),abs(ysi[1]-ys_v))/abs(ys_v) if ys_v else None
    virtual_qualified=virtual_assumed_rel is not None and ysi[0]>0 and virtual_assumed_rel<=2e-10
    return dict(index=trace['index'],bin=trace['bin'],incoming=i,average=v,outgoing=o,D=D,B=B,r=r,tau=t,
      root_bracket=bracket,root_residual=F(t)-r,tau_branch='native_exponential_gt_1e_minus6',
      Gamma=G,TR_eV=bg['TR'],nH_cm3=n,H_s_inv=H,native_z=bg['native_z'],lambda_cm=L,
      x1s=x1s,yp=yp,ys_beta=ys_b,ys_gamma=ys_g,ys_virtual=ys_v,
      virtual_numerator_terms=[p1,p2],virtual_cancellation_condition=cancellation,
      virtual_rounding_model_relative_estimate=virtual_assumed_rel,
      virtual_well_conditioned_under_assumed_model=virtual_qualified,
      ys_virtual_assumed_interval=ysi,
      virtual_interval_propagation=dict(incoming=ii,outgoing=oo,D=Di,A=Ai,feq=feqi,
        Gamma=Gi,Cp=Cpi,Cs=Csi,yp=ypi,numerator=numerator_i,
        correlation='trace,tau,feq correlations conservatively discarded; independent interval enclosure',
        model='ASSUMED_32_ULPS_PER_TRACE_AND_RECONSTRUCTED_COEFFICIENT; NOT_PHYSICAL_CERTIFICATE'),
      x2s=x1s*(ys_b+w),x2p=x1s*(yp+3*w),moving_Wien_reference=w,
      source_normalization_excess=x1s*(ys_b+yp+4*w),
      absolute_inverse_sensitivity=1/derivative(t),relative_ratio_condition=r/(t*derivative(t)),
      rounding_model=dict(label='ASSUMED_32_BINARY64_ULPS_NOT_PHYSICAL_CERTIFICATE',trace_abs=[ei,ev,eo],
        ratio_error=er,tau_interval=[tl,tu],x1s_interval=[xl,xu],coefficient_abs=dict(H=eH,Gamma=eG,lambda_cm=eL,nH_cm3=en)),
      input_snapshot_used_by_inverse=False)
