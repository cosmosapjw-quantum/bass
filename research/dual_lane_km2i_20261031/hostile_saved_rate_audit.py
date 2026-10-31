"""Hostile independent arithmetic of saved chemistry data. NO original BASS RHS import."""
from pathlib import Path
import argparse,hashlib,json,math
import numpy as np
from scipy.integrate import simpson
PI=math.pi
M_E=9.1093837139e-31
K_B=1.380649e-23
H_P=6.62607015e-34
EV=1.602176634e-19
LAMBDA=121.567e-9
TSTAR_YEAR=365.25*86400

def audit(source,output):
    source=Path(source);s=json.loads(source.read_text());m={'max_abs_rate_residual':0.,'max_abs_C_residual':0.,'max_quadrupole_theory_abs':0.,'max_thick_mean_rel':0.,'max_binding_eV_residual':0.,'max_charge_number_diff':0.,'max_simpson_chemistry_integration_residual_41_nodes':0.,'max_opacity_scoped_delta':0.,'cases':0,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'RHS_FREE_SAVED_DATA_ARITHMETIC_NO_DISTINCT_AUTHOR_EINSTEIN_SOLVER'}
    for c in s['cases'].values():
        for md,d in c['chemical_modes'].items():
            m['cases']+=1
            rs=d['epochs']; u=np.array([r['u'] for r in rs]);dx=np.array([r['xprime_u'] for r in rs]);
            mismatch=abs((rs[-1]['x']-rs[0]['x'])-simpson(dx,x=u))
            m['max_simpson_chemistry_integration_residual_41_nodes']=max(m['max_simpson_chemistry_integration_residual_41_nodes'],mismatch)
            for r in rs:
                x=r['x'];T=r['T_m_K'];Tg=r['T_gamma_K'];nh=r['nH_rest_m3'];
                alph=4.309e-19*(T/1e4)**(-.6166)/(1+.6703*(T/1e4)**.53)
                at=4.309e-19*(Tg/1e4)**(-.6166)/(1+.6703*(Tg/1e4)**.53)
                beta=at*(2*PI*M_E*K_B*Tg/H_P**2)**1.5*math.exp(-3.4*EV/(K_B*Tg))
                lam=r['lambda_lya_s'];C=(lam+8.2245809)/(lam+8.2245809+beta)
                expected=r['nH_rest_m3'];tt=c['Tstar_Julian_years']*TSTAR_YEAR
                xp=tt*C*(beta*(1-x)*math.exp(-10.2*EV/(K_B*Tg))-alph*nh*x*x)
                m['max_abs_rate_residual']=max(m['max_abs_rate_residual'],abs(xp-r['xprime_u']))
                m['max_abs_C_residual']=max(m['max_abs_C_residual'],abs(C-r['C_factor']))
                if md=='angular':
                    quad=np.array(r['quad']);q0=np.array(r['quad_theory'])
                    m['max_quadrupole_theory_abs']=max(m['max_quadrupole_theory_abs'],float(np.max(abs(quad-q0))))
                    thick=8*PI*(r['H']/tt)/(LAMBDA**3*(1-x)*nh)
                    m['max_thick_mean_rel']=max(m['max_thick_mean_rel'],abs(lam/thick-1))
                m['max_charge_number_diff']=max(m['max_charge_number_diff'],abs(r['n_e_m3']-r['n_p_m3']))
                bind=13.6*(rs[0]['x']-x)
                m['max_binding_eV_residual']=max(m['max_binding_eV_residual'],abs(bind-r['binding_energy_change_eV_per_H']))
            m['max_opacity_scoped_delta']=max(m['max_opacity_scoped_delta'],abs(d['ray_optical_depth_difference_from_parent']))
    assert m['cases']==4
    assert m['max_abs_rate_residual']<1e-11
    assert m['max_abs_C_residual']<1e-14
    assert m['max_quadrupole_theory_abs']<5e-8
    assert m['max_thick_mean_rel']<1e-9
    assert m['max_charge_number_diff']==0
    assert m['max_binding_eV_residual']<1e-11
    assert m['max_simpson_chemistry_integration_residual_41_nodes']<3e-5
    assert m['max_opacity_scoped_delta']>5
    output=Path(output);output.parent.mkdir(exist_ok=True,parents=True);output.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    print('KM2I_HOSTILE_SAVED_RATES_PASS',json.dumps(m,sort_keys=True))
    return m
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args();audit(a.source,a.output)
