"""Preserved SI adapter and exactly one new core.rhs, after transaction PASS."""
import sys
import numpy as np
from mp_b import *

def consume(owner,clock,op_right,result):
    sys.path.insert(0,str(ROOT/'vendor'))
    import core
    from geometry import si_to_core
    energy=owner['final_sector_energy_J_m3'];event=owner['event_sector_energy_J_m3'];h=clock.h
    T=np.zeros((5,4,4));cq=np.zeros((5,4));pressures=[ZERO,ZERO,m(2)/3,m(1)/3,m(1)/3]
    for i in range(5):
        T[i,0,0]=float(energy[i]);p=float(pressures[i]*energy[i]);T[i,1:,1:]=np.eye(3)*p
        cq[i,0]=float(event[i]/clock.duration/mp.exp(3*h))
    mpforce=[event[i]/clock.duration/mp.exp(3*h) for i in range(5)];forcegross=sum(abs(x) for x in mpforce)
    check('five-sector MP four-force sum before SI conversion',abs(sum(mpforce))<=ARITH*forcegross,sum(mpforce),ARITH*forcegross)
    double_residual=float(np.sum(cq[:,0]));double_gross=float(np.sum(np.abs(cq[:,0])))
    check('separate four-force binary64 conversion roundoff',abs(double_residual)<=512*np.finfo(float).eps*double_gross,double_residual,512*np.finfo(float).eps*double_gross)
    scale=core.FixedScale(1.);rho,flux,source=si_to_core(scale,T,cq,core);H=float(op_right['H_s_inv']);hh=H*scale.time_s
    state=core.State(hh,np.zeros((3,3)),np.zeros((3,3)),np.zeros(3),0.,rho,flux);packed=state.pack()
    pressure,pi,transfer,momentum=source.arrays(5,balanced=True)
    expected=core.State(-hh*hh-(sum(rho)+3*sum(pressure))/6,np.zeros((3,3)),np.zeros((3,3)),np.zeros(3),hh,-3*hh*(rho+pressure)+transfer,np.zeros((5,3))).pack()
    result['new_B3i_rhs_invocations']=1
    actual=core.rhs(0.,packed,source)
    errors=[]
    for a,b in zip(actual,expected):errors.append(abs(a-b)/abs(b) if b else (0. if a==0 else float('inf')))
    check('one actual core RHS vs independent isotropic algebraic identities',max(errors)<=5e-12,max(errors),5e-12)
    return dict(sector_order=owner['sector_order'],T_SI_J_m3=T.tolist(),cQ_SI_J_m3_s=cq.tolist(),Q0_SI_J_m4=(cq[:,0]/scale.c).tolist(),
      transfer_model='finite-step common-volume event energy / saved duration / exp(3h), applied at right geometry',
      FixedScale=dict(length_m=scale.length_m,c=scale.c,G=scale.G,density_factor=scale.density_factor,time_s=scale.time_s),
      right_H_s_inv=H,state_core=packed.tolist(),source_core=dict(pressure=pressure.tolist(),pi=pi.tolist(),energy_transfer=transfer.tolist(),momentum_transfer=momentum.tolist()),
      actual_rhs=actual.tolist(),independent_expected_rhs=expected.tolist(),own_nonzero_relative_errors=errors,
      zero_expected_components_exact=all(a==0 for a,b in zip(actual,expected) if b==0),actual_rhs_calls=1,
      Friedmann_closure_required=False,spatial_Q_zero_is_not_spatial_T_zero=True)
