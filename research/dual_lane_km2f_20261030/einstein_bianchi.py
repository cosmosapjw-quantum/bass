"""KM2F: Einstein Bianchi I coevolution with original BASS polarized photons and cold electron dust.

The full KM2A angular collision and KM1 P8 normal-tetrad propagation are
unchanged.  Exact Bianchi-I initial momentum/Hamiltonian constraints are solved
before the IVP.  The metric and trace-free shear evolve with *total* stress.
Nothing is claimed for frequency-dependent, thermally broad or inhomogeneous matter.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[2]
KM2C=ROOT/'research/dual_lane_km2c_20261028'
KM2D=ROOT/'research/dual_lane_km2d_20261030'
KM2E=ROOT/'research/dual_lane_km2e_20261030'
sys.path[:0]=[str(KM2C/'vendor'),str(KM2C/'code')]
from curved_tilt import FieldProfile, P8, linear_collision
from tilted_collision import TiltedThomson, radiation_tensor, expected_fourforce
from research.dual_lane_km2e_20261030.coupled_electron_photon import CoupledColdElectronPhoton,source_guards

EXPECTED_GIT={
 KM2C/'code/curved_tilt.py':'05aade3aab7e9a32c11608882c943e4d3cb6f379',
 KM2C/'vendor/tilted_collision.py':'92660768f4719d78261fed1cb44f186d2821629d',
 KM2C/'vendor/source_memory.py':'9d500e36fefaa4ddc22300a2f03d9eb9cfe98403',
 KM2D/'accelerating_tilt.py':'b599d3842e843d8de1de1499b73e6849374bf8f8',
 KM2E/'coupled_electron_photon.py':'12fbce8109fc07b1fbf60d9a066d8aa1c57ea9c1',
}


def full_source_guard():
    source_guards() # Parent self-audits all existing Git blobs.
    output={}
    for path,sha in EXPECTED_GIT.items():
        raw=path.read_bytes(); digest=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if digest!=sha: raise ValueError('IMMUTABLE_ORIGINAL_PHYSICS_BLOB_MISMATCH '+str(path))
        output[str(path.relative_to(ROOT))]=digest
    return output


def sym_traceless(v):
    s=(v+v.T)*0.5
    return s-np.eye(3)*(np.trace(s)/3)


def sigma_from5(z):
    xx,yy,xy,xz,yz=z
    return np.array([[xx,xy,xz],[xy,yy,yz],[xz,yz,-xx-yy]],float)


def sigma_to5(s):
    return np.array([s[0,0],s[1,1],s[0,1],s[0,2],s[1,2]],float)


class EinsteinCoupledBianchi:
    """Bianchi I Fermi normal tetrad with 8piG*rho_unit*Tstar² dimensionless kappa.

    Photon initial source: exact unmodified KM2E source sampled with the same
    normal direction and screen; ONLY the synthetic electron initial state is
    changed to solve the *homogeneous Bianchi-I momentum constraint* Q=0.
    """
    def __init__(self,ntheta=12,end=.25,kappa=.003,inertia_ratio=3.,nu0=1.3,
                 source_seed=(.3,-.4,.2),state_mode='p',sigma_initial_scale=1.):
        self.original_blobs=full_source_guard()
        self.ntheta=int(ntheta);self.end=float(end);self.kappa=float(kappa)
        self.ratio=float(inertia_ratio);self.nu0=float(nu0)
        self.state_mode=state_mode
        self.sigma_initial_scale=float(sigma_initial_scale)
        if (not 6<=self.ntheta<=32 or not 0<self.end<=.6 or self.kappa<0
            or self.ratio<=0 or self.nu0<0 or self.state_mode not in ('p','beta')
            or not np.isfinite(self.sigma_initial_scale) or self.sigma_initial_scale<0):
            raise ValueError('Original bounded source, positive Einstein coupling and matter inertia required')
        donor=CoupledColdElectronPhoton(n=self.ntheta,end=self.end,nu0=nu0,
                                        inertia_ratio=.75,beta0=source_seed)
        self.j0=donor.J0.copy()
        self.n0=donor.geo.grid.n.copy();self.w0=donor.geo.grid.w.copy()
        self.screen0=donor.geo.screen0.copy()
        self.N=len(self.w0);self.Jsize=self.j0.size;self.Esize=self.screen0.size
        self.t0=radiation_tensor(self.n0,self.w0,self.j0)
        self.rho0=float(self.t0[0,0]);self.q0=self.t0[0,1:].copy()
        self.Re0=self.ratio*self.rho0
        self.beta0=-self.q0/self.Re0
        if not np.isfinite(self.beta0).all() or self.beta0@self.beta0>=1:
            raise ValueError('NO_FEASIBLE_SINGLE_COLD_ELECTRON_MOMENTUM_CONSTRAINT')
        self.gamma0=1/np.sqrt(1-self.beta0@self.beta0)
        self.p0=self.gamma0*self.beta0
        self.M0=self.Re0/self.gamma0
        self.sigma0=sym_traceless(FieldProfile('main',nu0).fields(0)[1])*self.sigma_initial_scale
        self.sigma2_0=.5*np.sum(self.sigma0*self.sigma0)
        self.H0=np.sqrt((self.kappa*(self.rho0+self.Re0)+self.sigma2_0)/3)
        self.zero=np.zeros(3);self.Z=np.zeros((3,3))
        self.slice_A=slice(0,9)
        self.slice_screen=slice(9,9+self.Esize)
        self.slice_J=slice(self.slice_screen.stop,self.slice_screen.stop+self.Jsize)
        k=self.slice_J.stop
        self.slice_p=slice(k,k+3);self.idx_zeta=k+3;self.idx_H=k+4
        self.slice_sigma=slice(k+5,k+10)
        self.total_size=k+10

    def initial(self):
        return np.r_[np.eye(3).ravel(),self.screen0.ravel(),self.j0.ravel(),
                     self.p0 if self.state_mode=='p' else self.beta0,
                     1.,self.H0,sigma_to5(self.sigma0)]

    def decode(self,y):
        v=np.asarray(y,float)
        if v.shape!=(self.total_size,) or not np.isfinite(v).all():
            raise ValueError('Complete Einstein-photon-electron state has wrong shape')
        A=v[self.slice_A].reshape(3,3)
        E=v[self.slice_screen].reshape(self.N,3,2)
        J=v[self.slice_J].reshape(self.N,3,3)
        var=v[self.slice_p]
        zeta=float(v[self.idx_zeta]);H=float(v[self.idx_H]);sigma=sigma_from5(v[self.slice_sigma])
        if not zeta>0: raise ValueError('Electron normal-slice number must stay positive')
        if self.state_mode=='p':
            p=var;gamma=np.sqrt(1+p@p);beta=p/gamma
        else:
            beta=var
            if beta@beta>=1:raise ValueError('Electron beta became superluminal')
            gamma=1/np.sqrt(1-beta@beta);p=gamma*beta
        return A,E,J,p,zeta,H,sigma,gamma,beta

    def fields(self,t,y,derivative=False):
        if not 0<=t<=self.end+1e-12:raise ValueError('Invalid u proper-time support')
        A,E,J,p,zeta,H,sigma,gamma,beta=self.decode(y)
        det=float(np.linalg.det(A))
        if not det>0:raise ValueError('Physical tetrad volume determinant must remain positive')
        raw=self.n0@A.T
        mu=np.linalg.norm(raw,axis=1)
        if np.min(mu)<=0: raise ValueError('Degenerate photon momentum')
        n=raw/mu[:,None]
        w=self.w0*det/mu**3
        nu=self.nu0*zeta*self.gamma0/gamma
        op=TiltedThomson(n,w,beta)
        T=radiation_tensor(n,w,J)
        rho_gamma=float(T[0,0]); q_gamma=T[0,1:]; Pgamma=T[1:,1:]
        Re=self.M0*zeta*gamma;Qe=self.M0*zeta*p;Pe=Re*np.outer(beta,beta)
        rho=rho_gamma+Re; q=q_gamma+Qe; P=Pgamma+Pe
        p_iso=float(np.trace(P)/3)
        anis=sym_traceless(P)
        shear2=.5*np.sum(sigma*sigma)
        B=H*np.eye(3)+sigma
        cf=expected_fourforce(T,beta,nu)
        streaming=None;coll=None;force_raw=None
        if derivative:
            s=np.einsum('ni,ij,nj->n',n,sigma,n)
            streaming=-4*(H+s)[:,None,None]*J+P8.tensor_rate(J,n,H,sigma,self.zero,self.Z,self.zero)
            coll=linear_collision(op,J,nu)
            icoll=np.trace(coll,axis1=1,axis2=2)
            force_raw=np.r_[np.dot(w,icoll),np.einsum('n,n,ni->i',w,icoll,n)]
        return locals()

    def rhs(self,t,y):
        z=self.fields(t,y,True)
        A,E,J,p,zeta,H,sigma,gamma,beta=[z[k] for k in
                              ('A','E','J','p','zeta','H','sigma','gamma','beta')]
        B=z['B'];n=z['n'];cf=z['cf'];nu=z['nu'];anis=z['anis']
        Aprime=-B@A
        ndot=-n@sigma.T+np.einsum('ni,ij,nj->n',n,sigma,n)[:,None]*n
        Omega=np.einsum('ni,nj->nij',ndot,n)-np.einsum('ni,nj->nij',n,ndot)
        Eprime=np.einsum('nij,nja->nia',Omega,E)
        Jprime=z['streaming']+z['coll']
        pprime=-B@p-cf[1:]/(self.M0*zeta)
        if self.state_mode=='beta':
            Re=self.M0*zeta*gamma
            pprime=-(np.eye(3)-np.outer(beta,beta))@(B@beta+cf[1:]/Re)
        zetaprime=-3*H*zeta
        Hprime=-self.kappa*(z['rho']+z['p_iso'])/2-z['shear2']
        sigmaprime=-3*H*sigma+self.kappa*anis
        return np.r_[Aprime.ravel(),Eprime.ravel(),Jprime.ravel(),pprime,
                     zetaprime,Hprime,sigma_to5(sigmaprime)]

    def solve(self,rtol=1.5e-11,atol=2e-13):
        sol=solve_ivp(self.rhs,(0,self.end),self.initial(),method='DOP853',
                      rtol=rtol,atol=atol,dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        return sol

    def measure(self,t,y,with_force=True):
        d=self.fields(t,y,with_force)
        H=d['H'];sigma=d['sigma'];rho=d['rho'];q=d['q'];P=d['P'];B=d['B']
        shear2=d['shear2'];p_iso=d['p_iso'];anis=d['anis']
        Hprime=-.5*self.kappa*(rho+p_iso)-shear2
        sigma_prime=-3*H*sigma+self.kappa*anis
        c=3*H*H-self.kappa*rho-shear2
        Rgeo=6*Hprime+12*H*H+2*shear2
        Rmatter=self.kappa*(rho-3*p_iso)
        basic={
            'u':float(t),'H':H,'H_prime':float(Hprime),'sigma':sigma.tolist(),
            'sigma2':float(shear2),'anisotropic_pressure':anis.tolist(),
            'noncommuting_shear_commutator_norm':float(np.linalg.norm(self.sigma0@sigma-sigma@self.sigma0)),
            'rho_photon':d['rho_gamma'],'rho_electron':float(d['Re']),
            'rho_total':float(rho),'q_photon':d['q_gamma'].tolist(),
            'q_electron':d['Qe'].tolist(),'q_total':q.tolist(),
            'P_photon':d['Pgamma'].tolist(),'P_electron':d['Pe'].tolist(),
            'P_total':P.tolist(),'p_total':p_iso,
            'beta_electron':d['beta'].tolist(),'gamma_electron':float(d['gamma']),
            'electron_zeta':float(d['zeta']),'nu_rest_tstar':float(d['nu']),
            'source_electron_M':d['op'].source(d['J']).tolist(),
            'A_momentum_tetrad':d['A'].tolist(),
            'detA':float(d['det']),
            'electron_number_vs_tetrad_detA_error':float(d['zeta']-d['det']),
            'screen_normal_orthogonality':float(np.max(abs(np.einsum('ni,nia->na',d['n'],d['E'])))),
            'screen_unit_gram_residual':float(np.max(abs(np.einsum('nia,nib->nab',d['E'],d['E'])-np.eye(2)))),
            'spacelike_photon_norm_error':float(np.max(abs(np.linalg.norm(d['n'],axis=1)-1.))),
            'photon_screen_transversality':float(np.max(abs(np.einsum('nij,nj->ni',d['J'],d['n'])))),
            'hamiltonian_constraint':float(c),
            'hamiltonian_normalized':float(abs(c)/(self.kappa*rho+shear2)) if (self.kappa*rho+shear2)>0 else float(abs(c)),
            'momentum_constraint_normalized':float(np.linalg.norm(q)/rho),
            'Ricci_scalar_from_geom':float(Rgeo),
            'Ricci_scalar_from_matter':float(Rmatter),
            'Ricci_trace_constraint':float(Rgeo-Rmatter),
            'photon_covariant_force':d['cf'].tolist(),
            'metric_spatial_covariant':np.linalg.inv(d['A'].T@d['A']).tolist(),
            'metric_volume':float(1/d['det']),
        }
        if with_force:
            rawF=d['force_raw'];gap=rawF-d['cf']
            basic.update({
                'photon_raw_force':rawF.tolist(),
                'photon_force_discrete_gap':gap.tolist(),
                'force_gap_relative':float(np.max(abs(gap))/max(1.,np.max(abs(d['cf'])))),
                'Hamiltonian_propagation_source':float(-self.kappa*gap[0]),
                'total_energy_geom_rate':float(-3*H*rho-np.sum(B*P)),
                'total_momentum_geom_rate':(-(4*H*np.eye(3)+sigma)@q).tolist(),
            })
        return basic

    def conservation_integrals(self,sol,order=24):
        x,w=leggauss(order)
        ts=self.end*(x+1)/2;ws=self.end*w/2
        a=[self.measure(float(t),sol.sol(float(t))) for t in ts]
        start=self.measure(0.,sol.sol(0.));finish=self.measure(self.end,sol.sol(self.end))
        deltaC=finish['hamiltonian_constraint']-start['hamiltonian_constraint']
        intdC=float(np.dot(ws,[z['Hamiltonian_propagation_source'] for z in a]))
        qdot=-np.array([(4*z['H']*np.eye(3)+np.asarray(z['sigma']))@np.asarray(z['q_total'])
                         -np.asarray(z['photon_force_discrete_gap'][1:]) for z in a])
        predQ=np.einsum('n,ni->i',ws,qdot)
        dq=np.asarray(finish['q_total'])-np.asarray(start['q_total'])
        # Tracefree shear source: d(sigma/zeta)/du=kappa*pi/zeta.
        integrand=[np.asarray(z['anisotropic_pressure'])/z['electron_zeta'] for z in a]
        sourced=self.kappa*np.einsum('n,nij->ij',ws,integrand)
        observed=np.asarray(finish['sigma'])/finish['electron_zeta']-self.sigma0
        return{
            'time_GL_nodes':order,
            'Hamiltonian_delta_actual':float(deltaC),
            'Hamiltonian_integrated_discrete_source':intdC,
            'Hamiltonian_source_balance_abs':abs(deltaC-intdC),
            'Q_total_delta_actual':dq.tolist(),
            'Q_total_delta_predicted':predQ.tolist(),
            'momentum_constraint_balance_max_abs':float(np.max(abs(dq-predQ))),
            'sourced_shear_integral':sourced.tolist(),
            'sourced_shear_observed':observed.tolist(),
            'sourced_shear_integral_error':float(np.max(abs(sourced-observed))),
            'sourced_shear_difference_from_unsourced_dilution':float(np.linalg.norm(np.asarray(finish['sigma'])-finish['electron_zeta']*self.sigma0)),
            'max_normalized_source_force_gap':max(z['force_gap_relative'] for z in a),
            'force_gap_time_rows':[{ 'u':z['u'],'gap':z['photon_force_discrete_gap'] } for z in a],
        }


def run(output:Path,orders=(12,16),end=.25):
    runs={}
    for n in orders:
        model=EinsteinCoupledBianchi(ntheta=n,end=end)
        sol=model.solve()
        records=[model.measure(float(u),sol.sol(float(u))) for u in np.linspace(0,end,5)]
        checks=model.conservation_integrals(sol)
        last=records[-1];first=records[0]
        limits={'hamiltonian_normalized':1e-8,'momentum_constraint_normalized':1e-8,
                'electron_number_vs_tetrad_detA_error':1e-8,'screen_unit_gram_residual':1e-8,
                'screen_normal_orthogonality':1e-8,'photon_screen_transversality':1e-8}
        bad={field:max(abs(r[field]) for r in records) for field in limits
             if max(abs(r[field]) for r in records)>limits[field]}
        if bad:raise ArithmeticError('Einstein physics constraint fails '+str(bad))
        if checks['Hamiltonian_source_balance_abs']>1e-8 or checks['momentum_constraint_balance_max_abs']>1e-8 or checks['sourced_shear_integral_error']>1e-8:
            raise ArithmeticError('Einstein constraint propagation vs actual source integration failed '+str(checks))
        if checks['sourced_shear_difference_from_unsourced_dilution']<1e-5:
            raise ArithmeticError('Physical anisotropic stress fails to source Einstein shear')
        runs[str(n)]={
            'n_theta':n,'ray_count':model.N,'Einstein_kappa':model.kappa,
            'electron_inertia_ratio':model.ratio,'initial_momentum_cancel_beta':model.beta0.tolist(),
            'initial_H_from_Hamiltonian':model.H0,'initial_sigma':model.sigma0.tolist(),
            'physics_epochs':records,'integrated_balances':checks,
            'max_abs_normalized_hamiltonian':max(r['hamiltonian_normalized'] for r in records),
            'max_abs_normalized_momentum':max(r['momentum_constraint_normalized'] for r in records),
            'runtime_nfev':int(sol.nfev),
        }
        print('KM2F_EINSTEIN_PHYSICS_PASS',n,'H0',model.H0,'Hfinal',last['H'],
              'beta',last['beta_electron'],'ham',runs[str(n)]['max_abs_normalized_hamiltonian'],
              'mom',runs[str(n)]['max_abs_normalized_momentum'],
              'shear_source',checks['sourced_shear_difference_from_unsourced_dilution'],flush=True)
    # The alternative beta parametrization integrates its OWN full photon,
    # coframe and Einstein evolution, not a post-processed p history.
    alt=EinsteinCoupledBianchi(ntheta=orders[0],end=end,state_mode='beta')
    sal=alt.solve()
    baseline=EinsteinCoupledBianchi(ntheta=orders[0],end=end)
    sb=baseline.solve()
    comparison={}
    for t in (0.,end/2,end):
        one=baseline.measure(t,sb.sol(t));two=alt.measure(t,sal.sol(t))
        comparison[str(t)]={
           'max_electron_beta_abs':float(np.max(abs(np.asarray(one['beta_electron'])-np.asarray(two['beta_electron'])))),
           'Einstein_H_abs':abs(one['H']-two['H']),
           'max_shear_abs':float(np.max(abs(np.asarray(one['sigma'])-np.asarray(two['sigma'])))),
           'total_density_abs':abs(one['rho_total']-two['rho_total']),
           'full_photon_J_abs':float(np.max(abs(sb.sol(t)[baseline.slice_J]-sal.sol(t)[alt.slice_J]))),
        }
    if any(max(r.values())>2e-8 for r in comparison.values()):
        raise ArithmeticError('Independent full photon+Einstein beta-vs-p physical ODE failed')
    # Flat limit: set all GR sources and initial shear to zero, but preserve
    # identical original polarized photon angular source and reciprocal dust.
    flat=EinsteinCoupledBianchi(ntheta=orders[-1],end=end,kappa=0,sigma_initial_scale=0.)
    sflat=flat.solve()
    f0=flat.measure(0.,sflat.sol(0.));f1=flat.measure(end,sflat.sol(end))
    control={
      'normal_total_E_change':float(f1['rho_total']-f0['rho_total']),
      'total_Q_max_change':float(np.max(abs(np.asarray(f1['q_total'])-np.asarray(f0['q_total'])))),
      'H_final':f1['H'],'sigma2_final':f1['sigma2'],
      'trace_curvature_final':f1['Ricci_scalar_from_geom'],
      'screen_orthogonality_final':f1['screen_normal_orthogonality'],
    }
    if (abs(control['normal_total_E_change'])>2e-8 or
        control['total_Q_max_change']>2e-8 or
        abs(control['H_final'])>1e-14 or control['sigma2_final']>1e-14):
        raise ArithmeticError('Minkowski reciprocal Thomson control did not conserve E,Q')
    v={
      'schema':'bass.km2f.constraint_coupled_full_polarized_photon_cold_electron.v1',
      'scope':'selfconsistent homogeneous Bianchi I normal Einstein geometry; original polarized P8 photons + cold electron dust, no electron temperature or spectral recoil',
      'parent_pr276_head':'58277dab1af10850ff0a86c74673743b2c0a8a5a',
      'original_sources':runs[str(orders[0])].get('source', 'original immutable parent code checked'),
      'time':'u=t/Tstar, (-,+,+,+), Lambda=0',
      'original_photon_seed_beta':[.3,-.4,.2],
      'electron_initial_beta':'derived from momentum constraint = -q_gamma/R_e rather than fixed KM2E electron input',
      'Einstein_coupling_kappa':.003,
      'electron_inertia_ratio':3.,
      'model_interpretation':'synthetic normalized cold electron density selected for Bianchi-I momentum constraint and finite quadrature stability, NOT observational abundance',
      'new_Einstein_constraints':'3H²=kappa*rho+sigma²; total momentum q_total=0',
      'new_Einstein_evolution':'Hprime=-kappa(rho+p)/2-sigma²; sigma_prime=-3H sigma + kappa pi',
      'full_independent_beta_vs_p_dynamical_comparison':comparison,
      'Minkowski_no_Einstein_feedback_control':control,
      'cases':runs,'upper_dag':'9/15','km2':'PARTIAL','new_upper_nodes':0,
      'production_ready':False,'merge_ready':False,'auto_next':False,
      'Einstein_full_formal_program_verification':'NOT_RUN',
      'angular_continuum_certificate':'NOT_RUN',
    }
    output.parent.mkdir(exist_ok=True,parents=True);output.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return v


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();run(a.output)
