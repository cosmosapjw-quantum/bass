#!/usr/bin/env python3
"""Scoped BASS CE1-P physical Einstein-Vlasov histories, not observational/CMB data.

No source, equations, or initial inputs changed. GL24/40 are independent
numerical quadratures of the *same continuum angular measure*, not certified
continuum source bounds. Stored ref8/ref16 use the pinned BASS implementation.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, os, struct, sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

MU = np.asarray([0., .5, 1.],dtype='<f8')
PHI = np.asarray([0., .25, .75, 1.],dtype='<f8')
ENERGY = np.asarray([[.1,.25,.05],[.2,.15,.15]],dtype='<f8')
SHEAR = np.asarray([.2,-.13,-.07],dtype='<f8')
END=0.08
N_TIMES=41
SOURCE_GIT_BLOB='fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf'
INTERVAL_GIT_BLOB='abbab0990fdefaf535ccbf5191ae3e060cb19214'
EV_GIT_BLOB='fb620ab8ea3c21e9b636cca48ab40761cab8ae2b'


def git_blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def source_identity(module):
    folder=Path(module.__file__).resolve().parent
    paths={'einstein_tabulated_source.py':SOURCE_GIT_BLOB,
           'einstein_interval.py':INTERVAL_GIT_BLOB,
           'einstein_vlasov.py':EV_GIT_BLOB}
    got={}
    for name,expected in paths.items():
        present=git_blob(folder/name)
        if present!=expected: raise RuntimeError(f'source-blob mismatch {name}: got {present}, pinned {expected}')
        got[name]=present
    return got


class GLContinuum:
    """Separate GL integration of exactly the same six physical angular cells."""
    def __init__(self,n_per_cell):
        from numpy.polynomial.legendre import leggauss
        q,wx=leggauss(n_per_cell)
        n_list=[];w_list=[]
        for i in range(2):
            for j in range(3):
                mm=.5*(MU[i]+MU[i+1])+.5*(MU[i+1]-MU[i])*q
                tt=.5*(PHI[j]+PHI[j+1])+.5*(PHI[j+1]-PHI[j])*q
                m,t=np.meshgrid(mm,tt,indexing='ij')
                phi=.5*np.pi*t
                n=np.stack([np.sqrt(1.-m*m)*np.cos(phi),
                            np.sqrt(1.-m*m)*np.sin(phi),m],axis=-1).reshape(-1,3)
                # The physical cell energy already includes all eight sign octants.
                # The normalized GL weight inside each mu-phi cell sums to unity.
                weights=(.25*ENERGY[i,j]*np.outer(wx,wx)).reshape(-1)
                n_list.append(n);w_list.append(weights)
        self.n=np.concatenate(n_list,axis=0)
        self.mass=np.concatenate(w_list,axis=0)
        self.n2=self.n*self.n
        self.energy0=float(np.sum(self.mass))
        self.n_per_cell=n_per_cell
        assert np.max(abs(self.n2.sum(axis=1)-1))<2e-14
        assert abs(self.energy0-.9)<2e-14

    def moments(self,ell):
        ell=np.asarray(ell,dtype=float)
        b=np.exp(-2*ell)
        q=self.n2*b
        r=np.sqrt(np.sum(q,axis=1))
        V_inv=np.exp(-np.sum(ell))
        E=V_inv*np.dot(self.mass,r)
        P=V_inv*np.einsum('n,ni->i',self.mass/r,q)
        return float(E),P

    def analytic_energy_derivative(self,ell,h):
        ell=np.asarray(ell,dtype=float);h=np.asarray(h,dtype=float)
        b=np.exp(-2*ell)
        q=self.n2*b
        r=np.sqrt(np.sum(q,axis=1))
        V_inv=np.exp(-np.sum(ell))
        erate=V_inv*np.dot(self.mass, -h.sum()*r -np.sum(q*h,axis=1)/r)
        return float(erate)


def rhs(src,u,y):
    ell,h=y[:3],y[3:]
    E,P=src.moments(ell)
    return np.r_[h,-h.sum()*h+P]


def constraint(h,E):
    return float(h[0]*h[1]+h[0]*h[2]+h[1]*h[2]-E)


def state0(E0):
    mean=math.sqrt((E0+.5*np.dot(SHEAR,SHEAR))/3)
    return np.r_[np.zeros(3),mean+SHEAR]


def integrate(src,t_grid):
    init=state0(src.energy0)
    out=solve_ivp(lambda u,y:rhs(src,u,y),(0.,END),init,method='DOP853',
                  rtol=3e-12,atol=3e-14,dense_output=True)
    if not out.success: raise RuntimeError(out.message)
    return np.asarray(out.sol(t_grid).T,dtype=float), {'nfev':out.nfev,'status':out.message,'rtol':3e-12,'atol':3e-14}


def rk4(src,nsteps):
    y=state0(src.energy0)
    dt=END/nsteps
    for k in range(nsteps):
        t=k*dt
        a=rhs(src,t,y)
        b=rhs(src,t+.5*dt,y+.5*dt*a)
        c=rhs(src,t+.5*dt,y+.5*dt*b)
        d=rhs(src,t+dt,y+dt*c)
        y=y+dt*(a+2*b+2*c+d)/6
    return y


def make_records(src,times,states,name):
    records=[]
    for u,y in zip(times,states):
        ell,h=y[:3],y[3:]
        E,P=src.moments(ell)
        theta=float(sum(h));sigma=h-theta/3
        pi=P-E/3
        C=constraint(h,E)
        # original source carries no blackbody spectrum or polarization
        redshift=np.exp(-ell)
        record={'channel':name,'u':float(u),
                'ell1':float(ell[0]),'ell2':float(ell[1]),'ell3':float(ell[2]),
                'h1':float(h[0]),'h2':float(h[1]),'h3':float(h[2]),
                'theta':theta,'H_mean':theta/3,
                'E':E,'P1':float(P[0]),'P2':float(P[1]),'P3':float(P[2]),
                'pi1':float(pi[0]),'pi2':float(pi[1]),'pi3':float(pi[2]),
                'sigma1':float(sigma[0]),'sigma2':float(sigma[1]),'sigma3':float(sigma[2]),
                'sigma2_scalar':float(np.dot(sigma,sigma)/2),
                'H_constraint_C':C,
                'trace_E_minus_P':float(E-sum(P)),
                'energy_ratio_x':float(redshift[0]),'energy_ratio_y':float(redshift[1]),'energy_ratio_z':float(redshift[2]),
                'energy_ratio_min':float(min(redshift)), 'energy_ratio_max':float(max(redshift))}
        if hasattr(src,'analytic_energy_derivative'):
            derivative=src.analytic_energy_derivative(ell,h)
            record['continuity_residual']=derivative+theta*E+float(np.dot(h,P))
        records.append(record)
    return records


def write_csv(path,records):
    fields=list(records[0].keys())
    if any('continuity_residual' in x for x in records) and 'continuity_residual' not in fields:fields.append('continuity_residual')
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(records)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    parser.add_argument('--quick',action='store_true')
    args=parser.parse_args(argv)
    output=Path(args.output).resolve();output.mkdir(exist_ok=True,parents=True)
    from bianchi.nonperturbative import einstein_tabulated_source as tab
    from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
    ident=source_identity(tab)
    times=np.linspace(0.,END,N_TIMES)
    cases={}
    for refine in ((8,) if args.quick else (1,4,8,16)):
        src=TabulatedRadiation(MU,PHI,ENERGY,refinement=refine,backend='python_oracle')
        assert len(src.n)==6*refine*refine
        states,solver=integrate(src,times)
        rec=make_records(src,times,states,f'STORED_REF{refine}')
        cases[f'stored_ref{refine}']={'source':src,'states':states,'solver':solver,'records':rec}
        write_csv(output/f'stored_ref{refine}_history.csv',rec)
    for order in ((24,) if args.quick else (24,40)):
        src=GLContinuum(order)
        states,solver=integrate(src,times)
        rec=make_records(src,times,states,f'CONTINUUM_GL{order}_NONCERTIFIED')
        cases[f'gl{order}']={'source':src,'states':states,'solver':solver,'records':rec}
        write_csv(output/f'continuum_GL{order}_history.csv',rec)
    gl_hi='gl24' if args.quick else 'gl40'
    ref='stored_ref8'
    actual=np.abs(cases[ref]['states']-cases[gl_hi]['states'])
    # norm absolute path mismatch; GL reference is not an exact source enclosure.
    comparison=[]
    for name,case in cases.items():
        arr=case['states']
        rec=case['records']
        E0=case['source'].energy0
        errs=[abs(v['H_constraint_C']) for v in rec]
        trace=[abs(v['trace_E_minus_P']) for v in rec]
        cont=[abs(v.get('continuity_residual',0)) for v in rec]
        comp={'channel':name,'source_rays':len(case['source'].n),
              'E0':E0,'source_integral':'stored rays' if name.startswith('stored') else 'independent Gauss-Legendre continuum quadrature',
              'max_Hamiltonian_abs':max(errs),'max_trace_abs':max(trace),
              'max_continuity_analytic_abs':max(cont),
              'max_source_h_gap_vs_GL_reference':float(np.max(abs(arr[:,3:]-cases[gl_hi]['states'][:,3:]))),
              'max_source_ell_gap_vs_GL_reference':float(np.max(abs(arr[:,:3]-cases[gl_hi]['states'][:,:3]))),
              'final_E':rec[-1]['E'],'final_theta':rec[-1]['theta'],
              'final_sigma2':rec[-1]['sigma2_scalar'],
              'final_pi': [rec[-1]['pi1'],rec[-1]['pi2'],rec[-1]['pi3']],
              'final_energy_ratios': [rec[-1]['energy_ratio_x'],rec[-1]['energy_ratio_y'],rec[-1]['energy_ratio_z']],
              'nfev':case['solver']['nfev']}
        comparison.append(comp)
    rk={}
    src=cases['stored_ref8']['source']
    for n in (32,64,128):
        v=rk4(src,n)
        rk[str(n)]={'max_h_error_vs_DOP853':float(np.max(abs(v[3:]-cases['stored_ref8']['states'][-1,3:]))),
                    'max_ell_error_vs_DOP853':float(np.max(abs(v[:3]-cases['stored_ref8']['states'][-1,:3])))}
    # Exact inputs as binary64 bytes and raw bytes SHA; source ref8 source/path certificate remained unmodified.
    source_sha=hashlib.sha256(MU.tobytes()+PHI.tobytes()+ENERGY.tobytes()+SHEAR.tobytes()).hexdigest()
    obj={'schema':'BASS.CE1P.PHYSICAL_HISTORIES.V1','simulation_not_observation':True,
         'physics':'positive massless collisionless reflection-even diagonal expanding Bianchi I Lambda0',
         'signature':'(-,+,+,+)','clock':'u=t/Tstar',
         'energy_units':'E=8*pi*G*Tstar^2*rho_energy/c^2; matching P_i units',
         'source_git_blobs':ident,'source_input_binary64_sha256':source_sha,
         'mu_bits':[float(x).hex() for x in MU],
         'phi_fraction_bits':[float(x).hex() for x in PHI],
         'cell_energy_bits':[[float(x).hex() for x in row] for row in ENERGY],
         'shear_bits':[float(x).hex() for x in SHEAR],
         'u_end':END,'sample_count':N_TIMES,'time_grid':[float(u) for u in times],
         'continuum_quadrature_reference':'GL24/GL40, not mathematically certified; angular integration same original 6-cell piecewise constant dW',
         'geometry_certificate_scope':'PR255 CE1-N n32 ref8 9.28056365759593e-6 is for frozen four-panel RK4/Hermite path, not claimed for DOP853 output',
         'summary':comparison,'rk4_ref8':rk,
         'max_ref8_vs_GL40_h':float(np.max(actual[:,3:])),
         'max_ref8_vs_GL40_ell':float(np.max(actual[:,:3])),
         'production_ready':False,'upper_dag':'9/15',
         'claim':'numerically checked physically modeled history, not observational CMB data or production certified solver'}
    (output/'results.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'MODEL_HISTORY_GENERATED','summary':comparison,'rk4_ref8':rk,'upper_dag':'9/15'},indent=2))
    return 0

if __name__=='__main__':sys.exit(main())