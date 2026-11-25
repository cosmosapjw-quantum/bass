"""One-way owned REI history -> BASS FLRW Thomson consumer, no feedback to chemistry."""
import argparse,csv,hashlib,json,math,subprocess,time
from pathlib import Path
import numpy as np
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--history',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=a.binary.resolve()
q=json.loads(a.donor.read_text());b=q['background'];ini=q['initial'];rows=[]
with a.history.open() as f:
    for r in csv.DictReader(f):rows.append([float(r[k]) for k in ('a','H_per_s','time_s','nH_proper_cm3','ne_proper_cm3')])
x=np.array(rows);eta=np.log(x[:,0]/x[0,0]);xe=x[:,4]/x[:,3]
assert np.all(np.diff(eta)>0) and eta[0]==0 and x[-1,0]==.2
assert abs(x[0,3]*1e6/ini['n_H_m3']-1)<2e-14 and abs(x[0,1]/ini['H_s']-1)<2e-14
a0=x[0,0];m=b['Omega_m']*a0**-3;r=b['Omega_r']*a0**-4;L=b['Omega_lambda'];dust=m/(m+r);ol=L/(m+r+L)
H=lambda t:b['H0_s']*np.sqrt(m*np.exp(-3*t)+r*np.exp(-4*t)+L)
assert np.max(abs(x[:,1]/H(eta)-1))<2e-13
sigma_c=299792458.*6.6524587051e-29
tau=float(np.trapezoid(x[:,4]*1e6*sigma_c,x[:,2]))
result=[]
for n in (1024,2048):
    knots=np.linspace(0,eta[-1],n+1);val=np.interp(knots,eta,xe)
    table=root/f'xe_{n}.tsv';np.savetxt(table,np.column_stack([knots,val]),fmt='%.17e',header='eta xe_per_H',comments='')
    sampled_tau=float(np.trapezoid(sigma_c*ini['n_H_m3']*np.exp(-3*knots)*val/H(knots),knots))
    for steps in (128,256,512):
        name=f'knots{n}_steps{steps}';out=root/name
        cmd=[str(exe),'--out',str(out),'--family','FLRW','--shear','0','--duration',repr(float(eta[-1])),'--steps',str(steps),'--nmu','4','--nphi','8','--lmax','2','--feedback','recoil','--dust-fraction',repr(float(dust)),'--baryon-fraction',repr(b['Omega_b']/b['Omega_m']),'--dust-beta','0,0,0','--omega-lambda',repr(float(ol)),'--expansion-equation','gauss-reduced','--lie-update','congruence','--collision','sdirk2','--ionization',str(table),'--n-h-emit-m3',repr(ini['n_H_m3']),'--h-emit-s',repr(ini['H_s'])]
        t=time.monotonic();proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        if proc.returncode:
            print(name,proc.stderr[-2000:],flush=True);raise RuntimeError('BASS execution failed')
        d=np.genfromtxt(out/'diagnostics.tsv',names=True,delimiter='\t')
        bt=float(d['proper_depth'][-1]);hgap=float(np.max(abs(d['hubble_ratio']/(H(d['eta'])/H(0))-1)))
        assert bt>0 and abs(bt/tau-1)<.02 and hgap<.001
        o=dict(case=name,n_intervals=n,steps=steps,tau=bt,tau_relative=abs(bt/tau-1),sampled_tau=sampled_tau,sampled_tau_relative=abs(sampled_tau/tau-1),hubble_relative=hgap,wall_s=time.monotonic()-t,command=cmd,table_sha256=sha(table),hashes={str(f.relative_to(out)):sha(f) for f in sorted(out.rglob('*')) if f.is_file()})
        result.append(o);print(name,bt,o['tau_relative'],hgap,flush=True)
        (root/'RESULTS.json').write_text(json.dumps(dict(status='PASS_SCOPED',scope='one_way_REI_owned_history_BASS_FLRW_consumer',binary_sha256=sha(exe),source_history_sha256=sha(a.history),donor_sha256=sha(a.donor),source_tau=tau,cases=result),indent=2)+'\n')
