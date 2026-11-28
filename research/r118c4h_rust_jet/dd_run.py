"""Same source data in double-double Rust, against C4G extended-precision coefficients."""
from pathlib import Path
import json,hashlib,time,subprocess,numpy as np,gzip
D=Path(__file__).resolve().parent;P=D.parent;G=P/'r118c4g_discrete_quadratic';SH=Path.home()/'r118c4h_bass_scratch'/'dd'
g={'__file__':str(G/'bass.py'),'__name__':'prior'};exec(compile((G/'bass.py').read_text(),str(G/'bass.py'),'exec'),g)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SH.mkdir(exist_ok=False);src=D/'jet_dd.rs';b=SH/'jet_dd';tb=SH/'jet_dd_test'
for cmd in [['rustc','--edition=2021','--test',str(src),'-o',str(tb)],[str(tb)],['rustc','--edition=2021','-C','opt-level=3',str(src),'-o',str(b)]]:subprocess.run(cmd,check=True)
(D/'jet_dd_binary.gz').write_bytes(gzip.compress(b.read_bytes(),mtime=0))
labels=['old','new','generic','collinear','zero'];ld=np.longdouble;J=g['J'][1];J=np.concatenate([J.real,J.imag],axis=0);controls=np.stack([g['controls'][k] for k in labels]);a0,cut,end=g['a0'],g['cut'],g['end'];clk=g['clock'];OL,K0,OG=g['OL'],g['K0'],g['OG']
ref=np.load(G/'DISCRETE_B2.npz');tr=np.load(G/'TIME_REFINEMENT.npz');rows=[];out=[]
for n,nr in [(16384,192),(65536,192),(131072,192),(65536,320)]:
 t=time.monotonic();tt=np.r_[np.linspace(ld(0),cut,n+1),np.linspace(cut,end,n//4+1)[1:]];dt=np.diff(tt);mid=(tt[:-1]+tt[1:])/2;ts=np.empty(2*len(dt),ld);ts[::2]=tt[:-1];ts[1::2]=mid;bg,src0=g['bg_table'](ts,nr)
 ne=np.interp(ts.astype(float),clk['u'],clk['ne_m3']);rad=ld(2)/15*OG/(a0*np.exp(ts))**4;stage=np.column_stack([bg,src0.reshape(-1,6),rad,ne]);data=np.column_stack([dt,stage[::2],stage[1::2]])
 q=SH/f'n{n}_r{nr}.bin'
 with q.open('wb') as f:
  for a in [np.array([len(dt),len(labels),OL,K0],ld),J,controls,data]:
   a=np.asarray(a,ld);hi=a.astype('<f8');lo=(a-hi.astype(ld)).astype('<f8');f.write(np.stack([hi,lo],axis=-1).tobytes())
 dig=sha(q);tm=time.monotonic();p=subprocess.run([str(b),str(q)],check=True,capture_output=True,text=True);runtime=time.monotonic()-tm;(D/f'dd_n{n}_r{nr}.csv').write_text(p.stdout)
 ss=p.stdout.splitlines();v=np.array([[float(k) for k in l.split(',')[1:]] for l in ss[1:]]);B=v[:,:7]+1j*v[:,7:];assert np.all(np.isfinite(B)) and np.linalg.norm(B[-1])==0
 if nr==192 and n in ref['n']:x=ref['B2'][list(ref['n']).index(n)];ln=labels
 elif nr==192:x=tr['B2'][list(tr['n']).index(n)];ln=labels[:2]
 else:x,*_=g['solve'](n,nr,labels);ln=labels
 diff=np.linalg.norm(B[:len(x)]-x,axis=1);norm=np.linalg.norm(B,axis=1);xn=np.linalg.norm(x,axis=1)
 row=dict(n=n,nr=nr,stage_table_sha=dig,table_bytes=q.stat().st_size,rust_seconds=runtime,total_seconds=time.monotonic()-t,B2_norm=dict(zip(labels,norm.tolist())),extended_norm=dict(zip(ln,xn.astype(float).tolist())),vector_gap=dict(zip(ln,diff.astype(float).tolist())))
 assert max(diff[:2])<1e-20 and (len(x)<3 or diff[2]/xn[2]<1e-11)
 rows.append(row);out.append(B);print(row,flush=True)
np.savez_compressed(D/'RUST_DD_B2.npz',B2=np.array(out),labels=np.array(labels),grid=np.array([[x['n'],x['nr']] for x in rows]))
(D/'RUST_DD_JET.json').write_text(json.dumps(dict(rows=rows,binary_sha=sha(b),binary_archive_sha=sha(D/'jet_dd_binary.gz'),source_sha=sha(src),scope='double-double research coefficient recurrence, source stage tables hi+lo from longdouble, small-exponent polynomial; compare actual prior extended results, no native full nonlinear AD'),indent=2)+'\n')

