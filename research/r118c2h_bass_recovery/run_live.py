"""Native live source packets on accepted BASS geometry; independent LRS
Killing-momentum oracle, event/inventory and live opacity checks."""
import argparse,hashlib,json,subprocess,math,time
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--only',default='');a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=a.binary.resolve()
d=json.loads(a.donor.read_text());q=d['initial'];fhe=d['background']['f_He']
assert d['schema']=='rec_bianchi.rei_initial_state/1' and q['z']==20 and q['x_HeII']==q['x_HeIII']==0.
cases=[]
for shear in (0.,.01,-.01):
    for steps in (64,128,256):
        cases.append((19.98,steps,shear,4,8))
cases.extend([(19.98,128,0.,8,8),(19.98,128,.01,4,16),(19.9,256,0.,4,8)])
rows=[]
for end,steps,shear,sub,mu in cases:
    name=f'z{end:g}_q{shear:+g}_n{steps}_s{sub}_a{mu}'
    if not name.startswith(a.only):continue
    out=root/name;cmd=[str(exe),str(out),str(end),str(steps),str(shear),str(sub),str(mu),str(q['x_HII']),str(q['T_m_K'])]
    print('start',name,flush=True);t=time.monotonic();proc=subprocess.run(cmd,text=True,capture_output=True,timeout=150)
    row=dict(case=name,end=end,steps=steps,q_ref=shear,subcells=sub,n_mu=mu,command=cmd,wall_s=time.monotonic()-t,returncode=proc.returncode)
    if proc.returncode:
        row.update(status='REJECTED_NATIVE',stderr=proc.stderr[-1800:]);rows.append(row);print(row,flush=True)
    else:
        h=np.genfromtxt(out/'history.tsv',names=True,delimiter='\t')
        g=np.genfromtxt(out/'geometry.tsv',names=True,delimiter='\t')
        pk=np.genfromtxt(out/'packets.tsv',names=True,delimiter='\t')
        cmb=np.genfromtxt(out/'cmb.tsv',names=True,delimiter='\t')
        assert len(h)==steps+1 and len(g)==steps+1
        assert np.all(np.diff(h['time_s'])>0) and abs(h['eta'][-1]-math.log(21/(1+end)))<2e-15
        assert np.min(h['x_HII'])>=0 and np.max(h['x_HII'])<=1
        assert np.min(h['x_HeII'])>=0 and np.min(h['x_HeIII'])>=0 and np.max(h['x_HeII']+h['x_HeIII'])<=1
        assert np.min(h['Tm_K'])>0 and np.min(pk['N_per_H'])>=0 and np.min(pk['energy_eV'])>=13.6
        assert np.max(pk['energy_eV']/pk['birth_energy_eV'])<=1+1e-14
        assert abs(h['nH_m3'][0]/q['n_H_m3']-1)<2e-14
        assert abs(h['x_HII'][0]/q['x_HII']-1)<2e-14
        assert abs(h['Tm_K'][0]/q['T_m_K']-1)<2e-14
        ne=h['nH_m3']*h['xe'];rate=299792458.*6.6524587051e-29*ne/h['H_s']
        tau=float(np.trapezoid(rate,h['eta']));taugap=abs(tau/h['tau'][-1]-1)
        assert np.max(abs(h['opacity']-rate)/rate)<2e-8 and taugap<2e-8
        assert np.max(abs(h['xe']-h['x_HII']-fhe*(h['x_HeII']+2*h['x_HeIII'])))<2e-14
        assert np.max(abs(h['number_defect']))<1e-8 and np.max(abs(h['energy_defect']))<1e-8
        assert np.max(abs(g['Gauss']))<2e-6 and np.max(abs(g['Codazzi_max']))<2e-6
        # Exact diagonal Bianchi I geodesic on piecewise-linear Sigma_zz:
        # b'=Sigma_zz/2; integrate b exactly over partial segments.
        eta=g['eta'];sig=g['Sigma_zz']/2
        b=np.r_[0.,cumulative_trapezoid(sig,eta)]
        be=pk['birth_eta'];i=np.searchsorted(eta,be,side='right')-1;i=np.clip(i,0,len(eta)-2)
        dl=be-eta[i];slope=(sig[i+1]-sig[i])/(eta[i+1]-eta[i])
        bb=b[i]+sig[i]*dl+.5*slope*dl*dl
        m0=leggauss(mu)[0][pk['ray'].astype(int)]
        def fac(beta):return np.sqrt((1-m0*m0)*np.exp(2*beta)+m0*m0*np.exp(-4*beta))
        pred=pk['birth_energy_eV']*np.exp(-(eta[-1]-be))*fac(b[-1])/fac(bb)
        predmu=m0*np.exp(-2*b[-1])/fac(b[-1])
        eerr=float(np.max(abs(pred/pk['energy_eV']-1)));muerr=float(np.max(abs(predmu-pk['mu_final'])))
        assert eerr<2e-7 and muerr<2e-7,(eerr,muerr)
        assert abs(np.sum(pk['N_per_H'])-h['N'][-1])<1e-12 and abs(np.dot(pk['N_per_H'],pk['energy_eV'])-h['U_eV'][-1])<1e-11
        assert np.min(cmb['I'])>0 and np.min(cmb['weight_sr'])>0
        if shear==0:assert np.max(abs(cmb['I']/np.exp(-4*eta[-1])-1))<1e-10
        row.update(status='PASS_SCOPED',tau=float(h['tau'][-1]),tau_independent=tau,tau_relative=taugap,characteristic_error=eerr,direction_error=muerr,max_number_defect=float(np.max(abs(h['number_defect']))),max_energy_defect=float(np.max(abs(h['energy_defect']))),max_root_residual=float(np.max(h['root_residual'])),terminal={k:float(h[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','xe','Tm_K','N','U_eV','packets','boundary_N','absorbed_N','emitted_N','redshift_work')},hashes={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()})
        rows.append(row);print(name,row['status'],row['terminal'],eerr,muerr,flush=True)
    (root/'RESULTS.json').write_text(json.dumps(dict(scope='live REI on accepted BASS LRS I; independent source births, gas and opacity, no geometry feedback',binary_sha256=sha(exe),donor_sha256=sha(a.donor),cases=rows),indent=2,allow_nan=False)+'\n')
