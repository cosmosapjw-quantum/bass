from pathlib import Path
import hashlib,json,subprocess,numpy as np
D=Path(__file__).resolve().parent;H=Path.home();S=H/'worktrees/rei-htt-thomson-20261124/research/r118c4f_external_stress'
p=S/'1024_4_base_external.csv';q=S/'1024_4_base_history.csv';a=np.genfromtxt(p,names=True,delimiter=',');h=np.genfromtxt(q,names=True,delimiter=',');assert a[-1]['a']==h[-1]['a']
v=np.array([a[-1]['rho_stable'],*[a[-1]['owner_P'+k] for k in ['xx','yy','zz','xy','xz','yz']]])/h[-1]['h']**2
inp=D/'stress.txt';np.savetxt(inp,v[None],fmt='%.17e');exe=H/'r118c4l_bass_shadow/_rustcore/target/release/examples/c4l_lie'
assert hashlib.sha256(exe.read_bytes()).hexdigest()==json.loads((D/'BUILD_ID.json').read_text())['lie_sha']
with (D/'LIE_STRESS.csv').open('w') as f:r=subprocess.run([str(exe),str(inp)],stdout=f,stderr=subprocess.PIPE,text=True,timeout=60)
assert r.returncode==0,r.stderr
a=np.genfromtxt(D/'LIE_STRESS.csv',names=True,delimiter=',',dtype=None,encoding='utf8');assert len(a)==48
mx={k:float(np.max(a[k])) for k in ['dlnh_gap','ds_gap','n_gap','a_gap']}
assert max(mx.values())<1e-8,mx
out=dict(cases=len(a),families=sorted(set(a['family'])),max_gaps=mx,max_jacobi={k:float(max(a['jacobi'][a['mode']==k])) for k in set(a['mode'])},physical_stress=v.tolist(),source_sha={p.name:hashlib.sha256(p.read_bytes()).hexdigest(),q.name:hashlib.sha256(q.read_bytes()).hexdigest()},physical_dq=float(a[0]['physical_dq']),physical_ds_norm=float(a[0]['physical_ds_norm']),scope='actual REI terminal external stress normalized by actual h², amplified controlled local fixed-geometry matter perturbation in native Raychaudhuri geometry update; not a self-consistent Lie radiation/metric trajectory')
(D/'LIE_STRESS.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
