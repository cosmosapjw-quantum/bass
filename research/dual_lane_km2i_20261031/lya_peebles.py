"""KM2I: rate-dynamic hydrogen Peebles chemistry + anisotropic Ly-alpha escape.

Research boundary: ONE-WAY chemistry on actually solved, immutable parent
Einstein-Bianchi I P8 photon backgrounds; no chemical heat/spectral source returned
into Einstein/P8. A normal-observer Sobolev proxy with isotropic line emitters,
NOT tilted-baryon full line transfer or observable CMB transfer function.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from research.dual_lane_km2h_20261030.external_opacity_bianchi import (ExternalFLRWOpacityBianchi, exact_source_guards)
from research.dual_lane_km2g_20261030.neutral_baryons import JULIAN_YEAR_S, SIGMA_T_M2, C_M_S, M_E_KG

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REF_BASS_HEAD='75f9dca9907cbc62af837547c2ba8591ad72bdee'
REF_SRC='research/dual_lane_km2h_20261030/external_opacity_bianchi.py'
REF_BLOB='fc9d96112305699ceba71032a1b119bc7e55549a'
E_CHARGE = 1.602176634e-19 # C exact
K_B = 1.380649e-23 # J/K exact
H_PLANCK = 6.62607015e-34 # J s exact
LAMBDA_ALPHA_M = 121.567e-9
A21 = 6.265e8 # s^-1; first-order H 2p-1s resonance model
TWO_PHOTON=8.2245809 # s^-1; original CLASS wrap_recfast.h
CHI2_EV = 3.4 # approximate H n=2 continuum threshold
E_ALPHA_EV = 10.2 # approx Lyman alpha
CHI_H_EV = 13.6 # approx H binding
T_CMB0 = 2.7255
ORIGINAL_RECFAST_BLOBS={
  'wrap_recfast.c':'e5ea80edd4652eb1a752cb4a2b835f4b74db91ca90248e5b5d04a8a3eada7cd5',
  'wrap_recfast.h':'1e5609a3e5b1ddd8f7ad99df336311a9f769867e52f203e0cb6481b617e2de73',
}


def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def gitblob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def source_guards():
    origin=exact_source_guards()
    if gitblob(ROOT/REF_SRC)!=REF_BLOB:raise ValueError('KM2H_PARENT_GIT_BLOB_CHANGED')
    origin[REF_SRC]=REF_BLOB
    for p,expect in ORIGINAL_RECFAST_BLOBS.items():
        actual=sha256(HERE/'source_data'/p)
        if actual!=expect:raise ValueError(f'ORIGINAL_CLASS_RECFAST_BYTES_CHANGED {p} {actual}')
        origin['source_data/'+p]=actual
    hdr=(HERE/'source_data/wrap_recfast.h').read_text()
    pairs={'_a_PPB_':'4.309','_b_PPB_':'-0.6166','_c_PPB_':'0.6703','_d_PPB_':'0.5300','_Lambda_':'8.2245809'}
    for key,v in pairs.items():
        if not re.search(r'#define\s+'+key+r'\s+'+re.escape(v)+r'\b',hdr):
            raise ValueError('RECFAST_RATE_COEFFICIENT_SOURCE_MISMATCH '+key)
    ccode=(HERE/'source_data/wrap_recfast.c').read_text()
    if not all(s in ccode for s in ('Rdown = 1.e-19*_a_PPB_','Rup = 1.e-19*_a_PPB_','pre->CK/Hz','*dxH_dz')):
        raise ValueError('RECFAST_ORIGINAL_RATE_FORMULA_CHANGED')
    return origin


def alpha_caseB(T):
    if T<=0 or not np.isfinite(T):raise ValueError('Nonphysical baryon temperature')
    t=T/1.e4
    return 1.e-19 * 4.309*t**(-.6166)/(1.+.6703*t**.5300)


def beta_caseB(T):
    """Per-excited H beta_B using original RecfastCLASS 'Trad' mode."""
    if T<=0 or not np.isfinite(T):raise ValueError('Nonphysical photon temperature')
    return alpha_caseB(T)*(2*math.pi*M_E_KG*K_B*T/H_PLANCK**2)**1.5*math.exp(-CHI2_EV*E_CHARGE/(K_B*T))


def sobolev_directional(H_dimless,sigma,n,w,nH,x,Tstar,*,sigma_switch=1.):
    """Return original-ray-grid local normal-frame Ly-alpha scalar and quadrupole.

    The weights are local isotropic normal-frame quadrature weights, not the
    transported polarised CMB photon ray energy weights.
    """
    if not 0<x<1:raise ValueError('Hydrogen fraction out of open physical interval')
    H=H_dimless/Tstar
    sigma=np.asarray(sigma)
    if sigma.shape!=(3,3) or abs(np.trace(sigma))>1e-11:
        raise ValueError('Shear must be symmetric tracefree')
    nn=np.asarray(n); weights=np.asarray(w)/np.sum(w)
    directional=H+sigma_switch*np.einsum('ni,ij,nj->n',nn,sigma,nn)/Tstar
    if np.min(directional)<=0:raise ValueError('Negative directional expansion invalid Sobolev escape')
    n1=(1-x)*nH
    tau=3*LAMBDA_ALPHA_M**3*A21*n1/(8*math.pi*directional)
    pesc=-np.expm1(-tau)/tau
    La=3*A21*pesc
    mean=float(np.dot(weights,La))
    quadrupole=np.einsum('n,ni,nj,n->ij',weights,nn,nn,La)/mean-np.eye(3)/3
    # quadrature is geometrically near isotropic but not byte-exact
    avgH=float(np.dot(weights,directional))
    ref=8*math.pi*H/(LAMBDA_ALPHA_M**3*n1)
    lim_theory=(2/15)*np.asarray(sigma)/H_dimless if sigma_switch else np.zeros((3,3))
    return {'mean_s':mean,'iso_s':float(3*A21*(-math.expm1(-3*LAMBDA_ALPHA_M**3*A21*n1/(8*math.pi*H)))/(3*LAMBDA_ALPHA_M**3*A21*n1/(8*math.pi*H))),
            'thick_mean_s':float(ref),'quadrupole':quadrupole,
            'quadrupole_thick_theory':lim_theory,'tau_min':float(tau.min()),'tau_max':float(tau.max()),
            'pesc_min':float(pesc.min()),'pesc_max':float(pesc.max()),
            'mean_H_physical':avgH,'H_physical':float(H),'min_H_parallel':float(directional.min()),
            'max_H_parallel':float(directional.max()),'weights_moment_error':float(np.max(np.abs(np.einsum('n,ni,nj->ij',weights,nn,nn)-np.eye(3)/3)))}


def chemistry_state(model,sol,u,x,mode):
    d=model.fields(float(u),sol.sol(float(u)),False)
    Tstar=model.Tstar_seconds
    zvol=model.zvol(d['zeta'])
    if not 900<=zvol<=1200:raise ValueError('Native HYREC table boundary exceeded')
    nh=model.nH_rest0*d['zeta']*model.gamma0/d['gamma']
    Tm=float(model.external.Tm(zvol));Tg=T_CMB0*(1+zvol)
    alpha=alpha_caseB(Tm);beta=beta_caseB(Tg)
    line=sobolev_directional(d['H'],d['sigma'],model.n0,model.w0,nh,x,Tstar,
                             sigma_switch=1. if mode=='angular' else 0.)
    La=line['mean_s']
    C=(La+TWO_PHOTON)/(La+TWO_PHOTON+beta)
    ion=beta*(1-x)*math.exp(-E_ALPHA_EV*E_CHARGE/(K_B*Tg))
    recomb=alpha*nh*x*x
    xp=Tstar*C*(ion-recomb)
    return {'u':float(u),'x':float(x),'xprime_u':float(xp),'z_volume':float(zvol),'H':float(d['H']),
            'nH_rest_m3':float(nh),'T_m_K':Tm,'T_gamma_K':Tg,'alpha_B_m3s':alpha,'beta_B_s':beta,
            'C_factor':C,'photoion_s_per_H':C*ion,'recomb_s_per_H':C*recomb,'Q_photon_ionization_J_m3_s_DIAGNOSTIC':float(-CHI_H_EV*E_CHARGE*nh*xp/Tstar),
            'lambda_lya_s':La,'lambda_lya_H_only_s':line['iso_s'],'tau_sob_min':line['tau_min'],'tau_sob_max':line['tau_max'],
            'lya_quadrupole_norm':float(np.linalg.norm(line['quadrupole'])),
            'lya_quad_vs_theory_max':float(np.max(np.abs(line['quadrupole']-line['quadrupole_thick_theory']))),
            'quad':line['quadrupole'].tolist(),'quad_theory':line['quadrupole_thick_theory'].tolist(),
            'H_parallel_min_s':line['min_H_parallel'],'Pescape_min':line['pesc_min'],'Pescape_max':line['pesc_max'],
            'normal_sobolev_line_source':True,'binding_energy_change_eV_per_H':CHI_H_EV*(model.external.xe(1200,'hyrec')-x),
            'n_e_m3':float(x*nh),'n_p_m3':float(x*nh),'n_H0_m3':float((1-x)*nh),'charge_source_C_m3':float(E_CHARGE*((x*nh)-(x*nh)))}


def run_case(ntheta,end=.25,rtol=1e-10):
    model=ExternalFLRWOpacityBianchi(ntheta=ntheta,end=end,opacity_mode='hyrec')
    sol=model.solve(rtol=1e-11,atol=1.5e-13)
    x0=float(model.external.xe(1200,'hyrec'))
    results={}
    for mode in ('angular','isotropic'):
        def rate(u,y):
            x=float(y[0]);return [chemistry_state(model,sol,u,x,mode)['xprime_u']]
        sx=solve_ivp(rate,(0,end),[x0],method='DOP853',rtol=rtol,atol=2e-12,dense_output=True)
        if not sx.success:raise RuntimeError('Peebles actual chemistry integration failed '+sx.message)
        points=[]
        for tt in np.linspace(0,end,41):
            xx=float(sx.sol(float(tt))[0])
            if not 0<xx<1:raise ArithmeticError('Physical chemical x outside bounds')
            rec=chemistry_state(model,sol,float(tt),xx,mode)
            rec['xe_hyrec_prescribed']=float(model.external.xe(rec['z_volume'],'hyrec'))
            rec['xe_difference_vs_prescribed']=xx-rec['xe_hyrec_prescribed']
            points.append(rec)
        # Counterfactual ray Thomson depths on the identical original Einstein/P8
        # trajectory: chemistry x changes scalar opacity but is NOT fed back.
        nodes,weights=leggauss(24)
        tt=end*(nodes+1.)/2; ww=end*weights/2
        depth=np.zeros(model.N)
        for t_i,w_i in zip(tt,ww):
            d=model.fields(float(t_i),sol.sol(float(t_i)),False)
            zref=model.zvol(d['zeta'])
            chem_x=float(sx.sol(float(t_i))[0])
            old_x=model.external.xe(zref,'hyrec')
            depth+=w_i*d['nu']*(chem_x/old_x)*d['op'].D
        depth_parent=model.optical_depth(sol,order=24)
        if min(depth)<=0:raise ArithmeticError('chemical optical depth must be positive')
        last=points[-1]
        last['binding_energy_release_eV_per_H']=CHI_H_EV*(x0-last['x'])
        # Physical missing energy relative to actual original P8 bolometric photons.
        end_d=model.fields(end,sol.sol(end),False)
        missing_binding_J_m3=last['nH_rest_m3']*CHI_H_EV*E_CHARGE*(x0-last['x'])
        last['unreturned_binding_release_to_P8_J_m3']=float(missing_binding_J_m3)
        last['missing_binding_to_photon_energy_ratio']=float(missing_binding_J_m3/(end_d['rho_gamma']*model.energy_unit_J_m3))
        results[mode]={'ray_optical_depth_mean':float(np.mean(depth)),
                       'ray_optical_depth_min':float(depth.min()),
                       'ray_optical_depth_max':float(depth.max()),
                       'ray_optical_depths':depth.tolist(),
                       'parent_prescribed_ray_optical_depth_mean':float(np.mean(depth_parent)),
                       'ray_optical_depth_difference_from_parent':float(np.mean(depth-depth_parent)),
                       'epochs':points,'rhs_evals':sx.nfev,'steps':len(sx.t),'xe_end':points[-1]['x'],'quad_end':points[-1]['quad'],
                       'max_line_quad_vs_analytic':max(z['lya_quad_vs_theory_max'] for z in points),
                       'max_C_difference_from_H_only':None}
    a=results['angular'];b=results['isotropic']
    comparison={'max_xe_abs':float(max(abs(x['x']-y['x']) for x,y in zip(a['epochs'],b['epochs']))),
                'initial_lya_quad_F':a['epochs'][0]['lya_quadrupole_norm'],
                'final_lya_quad_F':a['epochs'][-1]['lya_quadrupole_norm'],
                'initial_line_tau_range':[a['epochs'][0]['tau_sob_min'],a['epochs'][0]['tau_sob_max']],
                'final_line_tau_range':[a['epochs'][-1]['tau_sob_min'],a['epochs'][-1]['tau_sob_max']],
                'dx_vs_HYREC_external_at_end':a['epochs'][-1]['xe_difference_vs_prescribed'],
                'chemical_vs_prescribed_tau_mean':a['ray_optical_depth_difference_from_parent'],
                'lyalpha_angular_vs_isotropic_tau_mean':a['ray_optical_depth_mean']-b['ray_optical_depth_mean'],
                'max_C_angular_vs_isotropic':max(abs(x['C_factor']-y['C_factor']) for x,y in zip(a['epochs'],b['epochs']))}
    # Actual initial and final directional escape maps, for scientific plots/diagnostics.
    grids=[]
    for u in (0.,end):
        x=float(np.interp(u,[0,end],[a['epochs'][0]['x'],a['epochs'][-1]['x']]))
        d=model.fields(u,sol.sol(u),False)
        nH=model.nH_rest0*d['zeta']*model.gamma0/d['gamma']
        l=sobolev_directional(d['H'],d['sigma'],model.n0,model.w0,nH,x,model.Tstar_seconds)
        # keep direct sampled ray directions for raw rank-2 emission
        h=d['H']/model.Tstar_seconds+np.einsum('ni,ij,nj->n',model.n0,d['sigma'],model.n0)/model.Tstar_seconds
        tau=3*LAMBDA_ALPHA_M**3*A21*(1-x)*nH/(8*math.pi*h)
        lam=3*A21*(-np.expm1(-tau))/tau
        grids.append({'u':float(u),'n':model.n0.tolist(),'lambda_s':lam.tolist(),'tau':tau.tolist(),'weights':model.w0.tolist()})
    return {'n_theta':ntheta,'n_phi':2*ntheta,'rays':model.N,'nH0_m3':model.nH_rest0,
            'Tstar_Julian_years':model.Tstar_years,'initial_parent_original_J_source_SHA':hashlib.sha256(model.j0.tobytes()).hexdigest(),
            'parent_ode_nfev':sol.nfev,'chemical_modes':results,'comparison':comparison,'directional_line_maps':grids}


def run_science(output,orders=(12,16),end=.25):
    sources=source_guards(); runs={}
    for n in orders:
        data=run_case(n,end=end);runs[f'GL{n}']=data
        print('KM2I_LYA_CHEM_PHYSICS',n,'xe',data['chemical_modes']['angular']['xe_end'],
              'lyaQinit',data['comparison']['initial_lya_quad_F'],'maxXeDeltaIso',data['comparison']['max_xe_abs'],flush=True)
    # One bounded scope, case aggregation; not a fabricated independent radiation IVP.
    result={'schema':'bass.km2i.peebles_directional_sobolev_bianchi_oneway.v1',
            'parent_pr':285,'parent_head':REF_BASS_HEAD,'upper_dag':'9/15','km2':'PARTIAL','new_upper_nodes':0,
            'source_blobs':sources,'atomic_rates':'original CLASS RecfastCLASS wrap_recfast.c/h exact copies, no fudge',
            'model':'original Einstein Bianchi I HYREC-opacity photon backgrounds + real one-way Peebles hydrogen ODE + normal-frame anisotropic Lya Sobolev angular escape',
            'scope':'LIVE_PEebles_CHEMICAL_IVP_FIXED_ORIGINAL_EINSTEIN_P8_BACKGROUND_NO_CHEMICAL_FEEDBACK',
            'cases':runs,'not_implemented':['fully selfconsistent anisotropic recombination','chemistry to P8 opacity feedback','line photon frequency redistribution','binding energy returned to Einstein stress','tilted baryon emission-frame source','realistic CLASS-matched baryon abundance'],
            'production_ready':False,'merge_ready':False,'auto_next':False,'distinct_author_R6_C9':'NOT_RUN','native_subagent':'NOT_RUN'}
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    p.add_argument('--orders',default='12,16');args=p.parse_args()
    run_science(args.output,orders=tuple(map(int,args.orders.split(','))))
