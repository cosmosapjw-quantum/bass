"""Exactly one actual vendor core RHS call, only after transaction checks."""
import sys
import numpy as np
from mp_b import *


def consume(data, fin, owner, result):
    """Keep stress and four-force separate; use the newly bounded duration."""
    if result.get('new_B3i_rhs_invocations',0)!=0:
        raise ValueError('new endpoint consumer already invoked')
    if not CHECKS or not all(record['passed'] for record in CHECKS):
        raise ValueError('transaction checks must pass before the one RHS call')
    sys.path.insert(0,str(ROOT/'vendor'))
    import core
    from geometry import si_to_core
    energy=owner['final_sector_energy_J_m3'];event=owner['event_sector_energy_J_m3']
    duration=fin['T_new'];duration_error=fin['T_error'];Vratio=mp.exp(3*fin['h'])
    check('new proper duration positive before finite four-force conversion',duration>duration_error,
          dict(new_duration=duration,new_duration_error=duration_error))
    T=np.zeros((5,4,4));cq=np.zeros((5,4));pressure_factors=[ZERO,ZERO,m(2)/3,m(1)/3,m(1)/3]
    mpforce=[event[i]/duration/Vratio for i in range(5)]
    force_errors=[owner['event_sector_energy_conditional_errors'][i]/((duration-duration_error)*Vratio)
                  +abs(event[i])*duration_error/(duration*(duration-duration_error)*Vratio)
                  +ARITH*abs(mpforce[i]) for i in range(5)]
    for i in range(5):
        T[i,0,0]=float(energy[i]);T[i,1:,1:]=np.eye(3)*float(pressure_factors[i]*energy[i])
        cq[i,0]=float(mpforce[i])
    gross=mp.fsum(abs(x) for x in mpforce)
    # Event cancellation is bounded on the actual pre-cancellation gross owner
    # scale; a small net transfer is not its own rounding scale.
    force_bound=(owner['event_energy_arithmetic_bound']+ARITH*sum(abs(x) for x in event))/duration/Vratio
    check('five-sector MP finite four-force balance before conversion',abs(sum(mpforce))<=force_bound,
          dict(residual=sum(mpforce),derived_arithmetic_bound=force_bound,gross=gross))
    double_residual=float(np.sum(cq[:,0]));double_gross=float(np.sum(np.abs(cq[:,0])))
    double_bound=512*np.finfo(float).eps*double_gross+float(force_bound)
    check('separate four-force binary64 conversion roundoff',abs(double_residual)<=double_bound,double_residual,double_bound)
    scale=core.FixedScale(1.);rho,flux,source=si_to_core(scale,T,cq,core)
    # Bound the values actually returned to the caller, including their
    # binary64 representation.  Q0's difference includes both cQ rounding and
    # the binary division by c, so it is added once to the pre-binary MP bound.
    cq_representation_errors=[abs(m(float(cq[i,0]))-mpforce[i]) for i in range(5)]
    q0=cq[:,0]/scale.c
    q0_representation_errors=[abs(m(float(q0[i]))-mpforce[i]/m(scale.c)) for i in range(5)]
    returned_cq_errors=[force_errors[i]+cq_representation_errors[i] for i in range(5)]
    returned_q0_errors=[force_errors[i]/m(scale.c)+q0_representation_errors[i] for i in range(5)]
    H=float(fin['right_H_s_inv']);hh=H*scale.time_s
    state=core.State(hh,np.zeros((3,3)),np.zeros((3,3)),np.zeros(3),0.,rho,flux);packed=state.pack()
    pressure,pi,transfer,momentum=source.arrays(5,balanced=True)
    expected=core.State(-hh*hh-(sum(rho)+3*sum(pressure))/6,
                        np.zeros((3,3)),np.zeros((3,3)),np.zeros(3),hh,
                        -3*hh*(rho+pressure)+transfer,np.zeros((5,3))).pack()
    # This assignment immediately precedes the only actual new RHS invocation.
    result['new_B3i_rhs_invocations']=1
    actual=core.rhs(0.,packed,source)
    errors=[abs(a-b)/abs(b) if b else (0. if a==0 else float('inf')) for a,b in zip(actual,expected)]
    check('one actual core RHS vs independent isotropic algebraic formulas',max(errors)<=5e-12,max(errors),5e-12)
    return dict(sector_order=owner['sector_order'],T_SI_J_m3=T.tolist(),cQ_SI_J_m3_s=cq.tolist(),
                Q0_SI_J_m4=q0.tolist(),
                transfer_model='finite-step common-V0 event energy / newly bounded native proper duration / exp(3h), at right geometry',
                new_proper_duration_s=duration,new_proper_duration_error_s=duration_error,right_volume_ratio=Vratio,
                conditional_duration_relative_error_bound=duration_error/(duration-duration_error),
                prebinary_conditional_cQ0_error_J_m3_s=force_errors,
                prebinary_conditional_Q0_error_J_m4=[x/m(scale.c) for x in force_errors],
                actual_cQ0_representation_difference_J_m3_s=cq_representation_errors,
                actual_Q0_full_representation_difference_J_m4=q0_representation_errors,
                conditional_cQ0_error_J_m3_s=returned_cq_errors,
                conditional_Q0_error_J_m4=returned_q0_errors,
                event_sector_energy_common_V0_J_m3=event,
                FixedScale=dict(length_m=scale.length_m,c=scale.c,G=scale.G,density_factor=scale.density_factor,time_s=scale.time_s),
                right_H_s_inv=H,state_core=packed.tolist(),
                source_core=dict(pressure=pressure.tolist(),pi=pi.tolist(),energy_transfer=transfer.tolist(),momentum_transfer=momentum.tolist()),
                actual_rhs=actual.tolist(),independent_expected_rhs=expected.tolist(),own_nonzero_relative_errors=errors,
                zero_expected_components_exact=all(a==0 for a,b in zip(actual,expected) if b==0),actual_rhs_calls=1,
                Friedmann_closure_required=False,spatial_Q_zero_is_not_spatial_T_zero=True,
                physical_radii=dict(eS=None,en=None,eE=None,geometry=None,temporal=None,total=None),global_radius=None,L4=False)
