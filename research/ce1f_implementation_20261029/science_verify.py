"""One bounded scientific campaign for CE1-F. Uses independent original-cell angular integration."""
import os,sys,time,json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parent/'package'))
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation, certified_tabulated_energy,certified_tabulated_pressure,certified_tabulated_geometry
root=Path(__file__).resolve().parent
from numpy.polynomial.legendre import leggauss

MU=('0','.5','1'); PHI=('0','1/3','2/3','1')
WEIGHTS=(('0.09','0.15','0.06'),('0.20','0.12','0.18'))


def independent_continuum(source,ell,nt=32):
    """GL of each physical ORIGINAL cell (not sampled barycentric solver)."""
    xi,wi=leggauss(nt)
    ell=np.asarray(ell,float);b=np.exp(-2*ell);V=np.exp(-sum(ell));rho=0.;pp=np.zeros(3)
    for (a,z),(c,d),w in source.original_cells:
        mu=float(a)+(xi+1)*(float(z-a))/2
        phi=(float(c)+(xi+1)*float(d-c)/2)*np.pi/2
        mu2=mu[:,None]**2
        x=(1-mu2)*np.cos(phi[None,:])**2
        y=(1-mu2)*np.sin(phi[None,:])**2
        zed=np.broadcast_to(mu2,x.shape)
        Q=np.stack((x,y,zed),axis=-1)
        r=np.sqrt(Q@b)
        ww=wi[:,None]*wi[None,:]/4
        rho+=float(w)*V*np.sum(ww*r)
        pp+=float(w)*V*b*np.einsum('ij,ijk->k',ww/r,Q)
    return rho,pp


def run():
    result={'unit':'CE1-F','progress':'9/15','source_type':'POSITIVE_EIGHT_REFLECTED_PIECEWISE_CONSTANT','inputs':{'mu_edges':MU,'az_fraction_edges':PHI,'cell_energies':WEIGHTS},'runs':[],'measured_falsification_only':True,'time_integrator_certified':False}
    base=TabulatedRadiation(MU,PHI,WEIGHTS,backend='python_oracle')
    st=time.monotonic()
    solvers=[]
    for refine in [1,2,4,8]:
        source=TabulatedRadiation(MU,PHI,WEIGHTS,refinement=refine,backend='python_oracle')
        energy=certified_tabulated_energy(source)
        bound=certified_tabulated_pressure(source,[0,0,0],[.075,.075,.075])
        coupled=certified_tabulated_geometry(source,end=.08)
        probes=[]
        for ell in [[0,0,0],[.02,.01,.04],[.045,.02,.062],[.075,.075,.075]]:
            rho,press=independent_continuum(source,ell,nt=40)
            measured=np.max(np.abs(source.moments(ell)[1]-press))
            if measured>bound['max_pressure_upper']:
                raise AssertionError(f'Cell source upper violated: ref {refine} {ell} {measured} > {bound["max_pressure_upper"]}')
            probes.append({'ell':ell,'independent_energy':float(rho),'pressure_gap':float(measured),'bound':bound['max_pressure_upper']})
        ode=solve_ivp(source.rhs,(0,.08),source.initial_state(),t_eval=np.linspace(0,.08,9),method='DOP853',rtol=3e-12,atol=3e-14)
        if not ode.success:raise RuntimeError(ode.message)
        hmax=np.max(np.abs(ode.y[3:,-1]-ode.y[3:,0]))
        result['runs'].append({'refinement':refine,'rays':len(source.mass),'exact_continuum_energy':str(source.exact_energy),'stored_initial_energy':source.energy0,'energy_error_upper':energy['energy_error_upper'],'source_upper':bound['max_pressure_upper'],'geometry_h_upper':coupled['geometry_h_upper'],'initial_rate_upper':coupled['initial_rate_upper'],'box':coupled['geometry_box_upper'],'probes':probes,'end_h':ode.y[3:,-1].tolist(),'constraint_max':max(abs((ode.y[3,i]*ode.y[4,i]+ode.y[3,i]*ode.y[5,i]+ode.y[4,i]*ode.y[5,i])-source.moments(ode.y[:3,i])[0]) for i in range(ode.y.shape[1]))})
        solvers.append(ode)
    ref=solvers[-1]
    for r,ode in zip(result['runs'],solvers):
        r['refine8_endpoint_h_gap']=float(np.max(abs(ode.y[3:,-1]-ref.y[3:,-1])))
        if r['refine8_endpoint_h_gap']>r['geometry_h_upper']+result['runs'][-1]['geometry_h_upper']:
            raise AssertionError('Coupled observed gap exceeds conservative triangle geometry bounds')
    result['science_elapsed_seconds']=time.monotonic()-st
    # Independent mutation: geometric midpoint of full first octant gives z²=1/4,
    # but exact spherical cell barycenter gives z²=1/3.
    s=TabulatedRadiation(('0','1'),('0','1'),(('0.8',),),backend='python_oracle')
    result['midpoint_mutation']={'exact_isotropic_pz':float(s.exact_energy)/3,'wrong_midpoint_pz':float(s.exact_energy)/4,'correct_barycenter_pz':s.moments([0,0,0])[1][2]}
    (root/'evidence/CE1F_RESULTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    for r in result['runs']:
        print(f"REF{r['refinement']} rays={r['rays']} source_upper={r['source_upper']:.9g} geom_upper={r['geometry_h_upper']:.9g} obs_ref8={r['refine8_endpoint_h_gap']:.9g}")
    print('SCIENCE_PASS elapsed',result['science_elapsed_seconds'])
if __name__=='__main__':run()
