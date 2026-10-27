"""Selected effective successful-channel Maxwellian energy-moment closure.

The TR partial derivative is deliberately absent. Higher-level cascades are
represented by the original effective interpolation, not resolved heat output.
"""
import math
import mpmath as mp
import numpy as np

def independent_partial70(rates,TR,TM,level):
    """Differentiate the explicit log polynomial at fixed TR, in its native cell.

    Source binary64 log table and generated grid values are exact coefficients
    in this independent 70-digit polynomial evaluation. TR/ratio cell selection
    is frozen to the exact source-selected cell, also at the upper boundary.
    """
    tm,tr,_,_=rates.stencil(TR,TM)
    with mp.workdps(70):
        m=mp.mpf;trv=m(TR);dt=m(rates.dt);dl=m(rates.dlog)
        g=(mp.log(trv)-m(math.log(rates.c['TR_MIN'])))/dl-tr
        def cubic(f):return [f*(f-1)*(2-f)/6,(1+f)*(1-f)*(2-f)/2,(1+f)*f*(2-f)/2,(1+f)*f*(f-1)/6]
        wt=cubic(g)
        temp=[sum(m(float(rates.logs[level,tm-1+k,tr-1+j]))*wt[j] for j in range(4)) for k in range(4)]
        def poly(T):
            f=(T/trv-m(rates.c['TM_TR_MIN']))/dt-tm;w=cubic(f)
            return sum(temp[k]*w[k] for k in range(4))
        deriv=mp.diff(poly,m(TM));K=m('1.5')*m(TM)+m(TM)**2*deriv
        return dict(dlogAlpha_dTm=mp.nstr(deriv,70),K_eV=mp.nstr(K,70),fixed_TR=True,iTM=tm,iTR=tr)

def moments(op,rates,c,nH_reference):
    TM=op['Tm'];TR=op['TR'];at=op['rates'];eq=rates.evaluate(TR,TR)
    rec=np.array([1.5*TM+TM*TM*d for d in at['dlogAlpha_dTm']])
    ion=np.array([1.5*TR+TR*TR*d for d in eq['dlogAlpha_dTm']])
    R=op['nH_cm3']*op['xe']*op['xHII']*np.array(at['Alpha']);I=np.array(at['Beta'])*op['absolute_population']
    chi=c['EI']-c['E21'];qa=-chi*(R-I);qk=-rec*R+ion*I;qr=(chi+rec)*R-(chi+ion)*I
    # Six positive gross energies supply the scale before cancellation.
    gross=np.stack([chi*R,chi*I,rec*R,ion*I,(chi+rec)*R,(chi+ion)*I])
    total=qa+qk+qr;scale=np.sum(np.abs(gross),axis=0);factor=nH_reference*1.602176634e-19
    refs=[dict(recombination=independent_partial70(rates,TR,TM,i),ionization=independent_partial70(rates,TR,TR,i)) for i in range(2)]
    return dict(closure='selected source-effective successful-cascade interpolation; unselected continuum-return null cycles excluded',
      derivative_direction='partial Tm holding TR fixed; source binary64 log-table polynomial',Krec_eV=rec,Kion_eV=ion,
      derivative_at_Tm=at['dlogAlpha_dTm'],derivative_at_TR=eq['dlogAlpha_dTm'],reference70=refs,
      recombination_events_per_H_proper_s=R,ionization_events_per_H_proper_s=I,chi_eV=chi,
      Q_atom_eV_per_H_s=qa,Q_kin_eV_per_H_s=qk,Q_rad_eV_per_H_s=qr,individual_positive_gross_energy_terms_eV_per_H_s=gross,
      sum_zero_residual_eV_per_H_s=total,sum_zero_gross_relative=np.abs(total)/scale,
      SI_conversion=dict(nH_reference_m3=nH_reference,eV_J=1.602176634e-19,factor=factor,units='J per common reference m^3 per proper s'),
      Q_atom_J_per_V0_s=qa*factor,Q_kin_J_per_V0_s=qk*factor,Q_rad_J_per_V0_s=qr*factor,
      physical_energy_radius=None,independent_native_heat_export=False)

def synthetic_control():
    # alpha(TR,TM)=TR^q TM^a has electron energy moment (a+3/2)TM.
    # Independent Maxwellian gamma-integral identity; q must not enter it.
    with mp.workdps(70):
        a=mp.mpf('0.7');q=mp.mpf('1.2');T=mp.mpf('0.3');TR=mp.mpf('0.4')
        partial=mp.diff(lambda x:mp.log(TR**q*x**a),T)
        moment=mp.mpf('1.5')*T+T*T*partial
        known=T*mp.gamma(a+mp.mpf('2.5'))/mp.gamma(a+mp.mpf('1.5'))
        wrong=mp.mpf('1.5')*T+T*T*mp.diff(lambda x:mp.log(x**q*x**a),T)
        return dict(a=str(a),q=str(q),Tm_eV=str(T),TR_eV=str(TR),fixed_TR_moment_eV=str(moment),
          gamma_integral_moment_eV=str(known),relative_error=float(abs(moment-known)/known),
          wrong_diagonal_moment_eV=str(wrong),wrong_direction_detected=abs(wrong-known)>mp.mpf('0.1')*known)
