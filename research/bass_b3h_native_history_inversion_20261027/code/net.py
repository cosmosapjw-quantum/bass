"""New finite net measure; reuses saved incoming totals and original B3g map."""
import bisect
import math
import sys
from pathlib import Path
from inverse import hx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
from transport import diagonal_bound,determinant_bound

def primitive(a,b,fa,fb,p):
    z=p*(b-a);term=1.;left=right=0.
    for n in range(24):
        left+=term/((n+1)*(n+2));right+=term/(n+2);term*=z/(n+1)
        if abs(term)<1e-30:break
    return (b-a)*math.exp(p*a)*(fa*left+fb*right)

def tensor(U):return [[U if i==j==0 else U/3 if i==j else 0. for j in range(4)] for i in range(4)]

def evaluate(packet,lyman,saved):
    s=packet['selection'];inc=packet['incoming'];p=packet['native_cosmology'];k=s['cell_indices'][0]
    h=float.fromhex(s['dlna_hex']);E=float.fromhex(inc['target_energy_eV_hex']);Es=float.fromhex(inc['source_energy_eV_hex'])
    lag=math.log1p((Es-E)/E);knots=[(n-k)*h+lag for n in inc['source_indices']]
    if s['cell_indices'] != [5126,5127] or not lag>h>0 or not knots[0]<=0<h<=knots[-1]:
        raise ValueError('frozen adjacent interval / strict-past coverage changed')
    if [r['index'] for r in lyman['records']] != s['cell_indices']:
        raise ValueError('outgoing knot identity mismatch')
    values=[float.fromhex(v) for v in inc['departure_hex']]
    outgoing=[hx(r['outgoing_lyman_departures'][0]) for r in lyman['records']]
    edges=[0.]+[x for x in knots if 0<x<h]+[h]
    def incoming(u):
        n=min(max(bisect.bisect_right(knots,u)-1,0),len(knots)-2)
        return values[n]+(values[n+1]-values[n])*(u-knots[n])/h
    def j(u):return outgoing[0]+(outgoing[1]-outgoing[0])*u/h-incoming(u)
    seg=[dict(a=a,b=b,j_a=j(a),j_b=j(b)) for a,b in zip(edges[:-1],edges[1:])]
    I={n:math.fsum(primitive(x['a'],x['b'],x['j_a'],x['j_b'],n) for x in seg) for n in [3,4]}
    G=3e6*p['LYA_FACT_cm3_inv'];EJ=E*p['EV_J'];dN=G*I[3];dU=G*EJ*I[4]
    Nin=saved['primary']['N_in_m3'];Uin=saved['primary']['U0_J_m3'];dt=saved['primary']['proper_duration_s']
    R=diagonal_bound([h]*3,None);r=float(R['Rhat_diagonal'][0]);det=determinant_bound(h,None,beta_exactly_stf=True)['Dhat']
    Nout=Nin+dN;Uout=Uin+dU
    event=EJ*dN;W0=G*EJ*(I[4]-I[3]);W1=G*EJ*(math.exp(-h)*I[4]-I[3])
    dU1=det*r*dU
    return dict(segments=seg,split_u=edges,strict_past_margin=lag-h,DeltaN0=dN,DeltaU0=dU,I3=I[3],I4=I[4],
      Nin0_saved=Nin,Uin0_saved=Uin,Nout0=Nout,Uout0=Uout,
      incoming_70digit_strings_reused=saved['independent_reference'],
      Nout1=det*Nout,Uout1=det*r*Uout,DeltaN1=det*dN,DeltaU1=dU1,
      R_diagonal=R['Rhat_diagonal'].tolist(),detR=det,
      T_out0_J_m3=tensor(Uout),T_out1_J_m3=tensor(det*r*Uout),DeltaT0_J_m3=tensor(dU),DeltaT1_J_m3=tensor(dU1),
      event_photon_energy_per_V0_J_m3=event,left_pullback_work_J_m3=W0,event_to_end_work_J_m3=W1,
      common_volume_integrated_cQ_rad_J_m3=[event,0.,0.,0.],
      common_volume_time_average_cQ_rad_J_m3_s=[event/dt,0.,0.,0.],
      common_volume_time_average_Q_rad_J_m4=[event/dt/299792458.,0.,0.,0.],
      proper_duration_saved_s=dt,source_rate_convention='cQ_rad0=E21_J*G*H*j; common-volume integral=E21_J*DeltaN0',
      force_vs_tensor='spatial isotropic source four-force is zero; spatial tensor diagonal is pressure U/3',
      energy_identity_residual_J_m3=math.exp(3*h)*dU1-event-W1,
      transport_residual_N=(det*dN-math.exp(-3*h)*dN)/abs(dN),
      transport_residual_U=(dU1-math.exp(-4*h)*dU)/abs(dU),
      B3i_RHS_invocations=0,complete_atomic_transaction=False,
      physical_radii={k:None for k in ['eS','en','eE','geometry','temporal','total']})
