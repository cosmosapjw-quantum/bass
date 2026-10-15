"""Reproducible BASS PR164 isotropic-radiation + massive-Vlasov tangent study."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
from scipy.integrate import simpson
from kinetic_tangent import (EinsteinTangent,MassiveFD96,AREF,AEND,H0,
                             OMEGA_M,OMEGA_B,OMEGA_R,OMEGA_L,XMAX)

def study():
    cases=[]
    for mass in (3.,30.,300.):
        for A in (-.5,0.,.5):
            start=time.perf_counter()
            model=EinsteinTangent(mass=mass,A=A,Sigma_ref=0.)
            result=model.endpoint()
            result.update({'mass_over_Tref':mass,'A':A,'Sigma_ref':0.,
                           'runtime_s':time.perf_counter()-start})
            cases.append(result)
    qlegacy=.01
    sigma0=math.sqrt(3)*qlegacy/math.hypot(1,qlegacy)
    for sign in (1,-1):
        m=EinsteinTangent(mass=30.,A=.5,Sigma_ref=sigma0,orientation=sign)
        res=m.endpoint()
        res.update({'mass_over_Tref':30.,'A':.5,'Sigma_ref':sigma0,
                    'signed_orientation':sign})
        cases.append(res)
    source=[]
    for mass in (3.,30.,300.):
        m=EinsteinTangent(mass=mass,A=0,Sigma_ref=0.)
        _,h,_,_=m.field(XMAX,0.,0.)
        href_flrw=H0*math.sqrt(OMEGA_M/AEND**3+OMEGA_R/AEND**4+OMEGA_L)
        source.append({'m_over_Tref':mass,'reference_norm':m.fd.norm,
             'reference_v2':m.fd.initial_v2,
             'isotropic_massive_H_end_over_cold_flrw_minus_1':h/href_flrw-1,
             'chi_at_x0':m.fd.moments(0,0,0).chi,
             'dDelta_dA_at_initial':m.fd.moments(0,0,0).delta_A})
    errors=[]
    eps=4e-4
    for mass in (3.,30.,300.):
        A=.4
        m=EinsteinTangent(mass=mass,A=A,Sigma_ref=.01,orientation=-1)
        y=m.solution(rtol=4e-12,atol=3e-14,n=41)
        up=EinsteinTangent(mass=mass,A=A+eps,Sigma_ref=.01,orientation=-1).solution(rtol=4e-12,atol=3e-14,n=41)
        dn=EinsteinTangent(mass=mass,A=A-eps,Sigma_ref=.01,orientation=-1).solution(rtol=4e-12,atol=3e-14,n=41)
        observed=(up.y[:3,-1]-dn.y[:3,-1])/(2*eps)
        predicted=y.y[3:,-1]
        errors.append({'mass_over_Tref':mass,
               'finite_difference':observed.tolist(),
               'tangent':predicted.tolist(),
               'abs_error':abs(predicted-observed).tolist()})
    return {'schema':'bass.rei.einstein_vlasov_tangent_reference.v1',
      'runtime':'isolated ChatGPT Python compute container, NOT user-local Ubuntu/NCP',
      'source_provenance':{
        'git_parent':'9ea46052358ba3e190317347d7f0001bab23c398',
        'original_freestream_source_blob':'8467932c3281f9d426712b3a582f2aae3a484692',
        'source_grid_recipe':'BASS compact Gauss-Legendre FD96/GL32 recreated from published source; grid_m30 reference norm checked',
        'cosmology_lock_blob':'7bfd190fe4cc722c2813c70e036d0279a0d83641',
        'cosmology_clock':'zbar20 -> zbar4; isotropic photon/neutrino FLRW contribution only'},
      'settings':{'H0_per_s':H0,'Omega_m':OMEGA_M,'Omega_b':OMEGA_B,'Omega_r':OMEGA_R,
                  'Omega_lambda':OMEGA_L,'a_ref':AREF,'a_end':AEND,'massive_fraction':.1},
      'cases':cases,'source_crosschecks':source,'variational_finite_diff':errors,
      'limitations':['no evolving gamma/nu Boltzmann tower; unlike PR161','no polarized Thomson','no HHe chemistry','no real REI production driver','no NCP execution in this follow-up','isotropic massive kinetic thermodynamics differs from original cold Omega_m baseline'],
      'scientific_admission':'SCOPED_ISOTROPIC_RADIATION_BIANCHI_I_MASSIVE_EINSTEIN_VLASOV_TANGENT_ONLY'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.out.exists():raise FileExistsError('cannot overwrite published evidence')
    r=study();args.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print('cases',len(r['cases']))
    for x in r['source_crosschecks']:print('isotropic H/cold difference',x['m_over_Tref'],x['isotropic_massive_H_end_over_cold_flrw_minus_1'])
    for x in r['variational_finite_diff']:print('variational abs max',x['mass_over_Tref'],max(x['abs_error']))
