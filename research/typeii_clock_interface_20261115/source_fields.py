"""Original BASS TypeII geometry to explicit clock/radiation interface fields."""
from pathlib import Path
import ast,math,json,hashlib,subprocess
import numpy as np
from scipy.integrate import solve_ivp
from clocks import kinematics,radiation_moments
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def check(v,s):
    if not bool(v):raise RuntimeError(s)
parent='27a3c7cfb57e145ed35526d4613de2e9d613d4ea'
rel='compiler/validation/generate_typeii_fixture.py';src=ROOT/rel
check(subprocess.check_output(['git','hash-object',str(src)],text=True).strip()==subprocess.check_output(['git','rev-parse',parent+':'+rel],cwd=ROOT,text=True).strip(),'source RHS drift')
fs=[n for n in ast.parse(src.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='typeii_rhs'];check(len(fs)==1,'RHS missing');ns={'math':math};exec(compile(ast.Module(body=fs,type_ignores=[]),str(src),'exec'),ns);rhs=ns['typeii_rhs']
fx=json.loads((ROOT/'compiler/validation/typeii_fixture_canonical.json').read_text())['trajectory']['samples'];x0=np.array(fx[0]['state'])
end=math.log(1701);sol=solve_ivp(lambda t,x:rhs(list(x),1.3),(0,end),x0,method='DOP853',rtol=2e-12,atol=1e-13,max_step=.004,dense_output=True);check(sol.success,'source integration')
z=np.arange(2248)*8000/2248;t=np.maximum(0,np.log(1701/(1+z)));x=sol.sol(t).T;xp=np.array([rhs(list(a),1.3) for a in x])
# Above z1700 retain the anchor beta in the table so interpolation below the
# boundary never blends in a synthetic zero. The C interface itself applies
# the explicit identity-clock rule at z>=1700.
np.savetxt(HERE/'CLOCK_GRID.dat',np.column_stack((x[:,4],xp[:,4])),fmt='%.17e',header='beta beta_prime on fixed 2248 original Hubble grid')
inside=(z>=300)&(z<=1700);k=kinematics(np.ones_like(z),x[:,4],xp[:,4]);m=radiation_moments(x[:,4]);G0=1/np.sqrt(1-x0[4]**2)
Omega=1-np.sum(x[:,:3]**2,axis=1)-x[:,3]**2/12;C=-np.sqrt(3)*x[:,3]*x[:,2]-3*1.3*Omega*x[:,4]/(1+.3*x[:,4]**2)
check(max(abs(C))<5e-12 and min(Omega)>0,'TypeII chart')
np.savetxt(HERE/'CLOCK_AND_RADIATION_FIELDS.csv',np.column_stack([z,x[:,4],xp[:,4],k['Gamma'],k['L'],k['A'],m['energy_ratio'],m['number_ratio'],m['flux_ratio']]),delimiter=',',header='z_mean,beta,beta_prime,Gamma,L,A,u_e_over_u_n,ngamma_e_over_ngamma_n,F_e_over_cu_n',comments='',fmt='%.17e')
summary={'parent_sha':parent,'source_model':'original gamma_fluid=1.3 TypeII','grid_points':2248,'domain_z_science':[300,1700],
 'max_Codazzi':float(max(abs(C))),'Gamma_range':[float(min(k['Gamma'][inside])),float(max(k['Gamma'][inside]))],
 'L_range':[float(min(k['L'][inside])),float(max(k['L'][inside]))],
 'A_range':[float(min(k['A'][inside])),float(max(k['A'][inside]))],
 'max_energy_density_boost':float(max(m['energy_ratio'][inside]-1)),
 'max_number_density_boost':float(max(m['number_ratio'][inside]-1)),
 'max_abs_flux_ratio':float(max(abs(m['flux_ratio'][inside]))),
 'max_energy_temperature_number_mismatch':float(max(abs(m['energy_ratio'][inside]**.75/m['number_ratio'][inside]-1))),
 'clock_grid_sha256':hashlib.sha256((HERE/'CLOCK_GRID.dat').read_bytes()).hexdigest(),
 'radiation_status':'EXACT_LOCAL_LORENTZ_MOMENTS_FOR_PRESCRIBED_ISOTROPIC_NORMAL_PLANCK_FIELD; NOT_COUPLED_TO_NATIVE_ATOMS'}
(HERE/'SOURCE_FIELDS.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
