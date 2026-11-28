"""C4M native external beam + opacity-family Taylor2 and all-Lie streaming test."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io,gzip,os,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;K=P/'r118c4l_composite_jet2';SH=Path.home()/'r118c4m_bass_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 prev=json.loads((K/'BUILD_ID.json').read_text());SH.mkdir(exist_ok=os.environ.get('C4M_REBUILD')=='1')
 ar=subprocess.check_output(['git','-C',str(R),'archive',prev['base'],'_rustcore','generated/rust/typeii','runtime/rust/typeii','research/r109_native_sky/hyrec_1100']);assert sha(ar)==prev['archive_sha']
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(SH,filter='data')
 changes={}
 for name,v in prev['changes'].items():
  p=SH/name;s=(K/v['file']).read_text();assert sha(s.encode())==v['sha']
  if p.name=='owned_thomson.rs':s+='\n'+(D/'external.rs.txt').read_text()
  p.write_text(s);(D/v['file']).write_text(s);changes[name]=dict(file=v['file'],sha=sha(s.encode()),prior_sha=v['sha'])
 for name,dst in [('external_native.rs','c4m_external.rs'),('lie_native.rs','c4m_lie.rs')]:
  p=SH/'_rustcore/examples'/dst;s=(D/name).read_text();p.write_text(s);changes[str(p.relative_to(SH))]=dict(file=name,sha=sha(s.encode()),prior_sha=None)
 assert sha((SH/'_rustcore/Cargo.lock').read_bytes())==prev['cargo_lock']
 cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'_rustcore/Cargo.toml'),'--example','c4m_external','--example','c4m_lie'];env=os.environ.copy();env['CARGO_BUILD_JOBS']='3'
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 bins={}
 for n in ['c4m_external','c4m_lie']:
  b=(SH/'_rustcore/target/release/examples'/n).read_bytes();(D/(n+'.gz')).write_bytes(gzip.compress(b,mtime=0));bins[n]=sha(b)
 write('BUILD_ID.json',dict(base=prev['base'],archive_sha=prev['archive_sha'],changes=changes,bins=bins,cargo_lock=prev['cargo_lock'],command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def run():
 p=SH/'_rustcore/target/release/examples/c4m_external';b=json.loads((D/'BUILD_ID.json').read_text());assert sha(p.read_bytes())==b['bins']['c4m_external']
 clk=P/'r118c3l_reachable_sky/clock.csv';ctrl=P/'r118c4k_composite_tangent/p0.ctrl'
 jobs=[('jet1024',1024,0.,'jet'),('jet2048',2048,0.,'jet'),('jet4096',4096,0.,'jet'),('base',2048,0.,'primal'),('m01',2048,-.01,'primal'),('p01',2048,.01,'primal'),('m003',2048,-.003,'jet'),('p003',2048,.003,'jet')]
 def job(q):
  tag,n,ep,kind=q;cmd=[str(p),str(clk),str(ctrl),str(n),'96','6','8',str(ep),kind];t=time.monotonic()
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run(cmd,stdout=f,stderr=g,timeout=350)
  row=dict(tag=tag,steps=n,param=ep,kind=kind,exit=r.returncode,seconds=time.monotonic()-t,cmd=cmd,clock_sha=sha(clk.read_bytes()),control_sha=sha(ctrl.read_bytes()));print(row,flush=True);return row
 with cf.ThreadPoolExecutor(max_workers=3) as ex:rr=list(ex.map(job,jobs))
 write('RUNS.json',rr);assert all(r['exit']==0 for r in rr)
def parse(tag):
 a=np.genfromtxt(D/(tag+'.csv'),names=True,delimiter=',');idx=np.stack([a[k] for k in ['epoch','ell','m']],axis=1)
 y=np.stack([np.stack([a[f'{k}{i}re']+1j*a[f'{k}{i}im'] for k in ['I','E','B']],axis=-1) for i in range(3)])
 g=np.array([list(map(float,l.split(',')[1:])) for l in (D/(tag+'.geom')).read_text().splitlines() if l.startswith('GEOM,')]);assert y.shape==(3,162,3) and g.shape==(2,25);return idx,y,g
def analyze():
 idx,y,g=parse('jet2048');_,z,g0=parse('base');same=bool(np.array_equal(y[0],z[0]));gap=float(np.linalg.norm(y[0]-z[0]));assert gap<1e-13
 rows=[]
 for h,t1,t2 in [(.01,'p01','m01'),(.003,'p003','m003')]:
  _,p,gp=parse(t1);_,m,gm=parse(t2);fd1=(p[0]-m[0])/(2*h);fd2=((p[0]-y[0])+(m[0]-y[0]))/(2*h*h);df2=(p[1]/(1+h)-m[1]/(1-h))/(4*h)
  for ep in [0,1]:
   mask=(idx[:,0]==ep)&(idx[:,1]>0);r=dict(h=h,epoch=ep,lnH1=float(g[ep,2]),lnH2=float(g[ep,3]),lnH1_FD=float((gp[ep,1]-gm[ep,1])/(2*h)),lnH2_FD=float((gp[ep,1]+gm[ep,1]-2*g[ep,1])/(2*h*h)))
   for j,k in enumerate(['I','E','B']):
    def rel(a,b):return float(np.linalg.norm(a-b)/max(np.linalg.norm(a),1e-300))
    a=y[1,mask,j];b=y[2,mask,j];r[k]=dict(first_norm=float(np.linalg.norm(a)),second_norm=float(np.linalg.norm(b)),first_FD=rel(a,fd1[mask,j]),second_FD=rel(b,fd2[mask,j]),second_tangent_FD=rel(b,df2[mask,j]) if h==.003 else None)
   rows.append(r)
 refine=[]
 dd=[parse('jet'+str(n)) for n in [1024,2048,4096]]
 for ep in [0,1]:
  msk=(idx[:,0]==ep)&(idx[:,1]>0);row=dict(epoch=ep,gauss=[a[2][ep,4:7].tolist() for a in dd],det2=[float(a[2][ep,7]) for a in dd],continuity=[float(a[2][ep,8]) for a in dd])
  for j,k in enumerate(['I','E','B']):
   v=[a[1][2,msk,j] for a in dd];r=[float(np.linalg.norm(v[1]-v[0])),float(np.linalg.norm(v[2]-v[1]))];row[k]=dict(differences=r,ratio=r[0]/max(r[1],1e-300))
  refine.append(row)
 np.savez_compressed(D/'EXTERNAL_JET2.npz',indices=idx,sky=y,geometry=g)
 write('EXTERNAL_JET2.json',dict(primal_array_equal=same,primal_gap=gap,geometry_gap=float(np.linalg.norm(g[:,[1,4,9]]-g0[:,[1,4,9]])),rows=rows,refinement=refine,scope='native step_external with separately conserved six canonical massive beam pairs and prescribed density-scaled REC ne clock. Relative p scales radial controls, initial shear, beam weight, electron clock. Actual native primal at p=0 and +/-0.01; shifted native jet at +/-0.003. Finite represented Bianchi I, not coupled atomic feedback.'))
 print((D/'EXTERNAL_JET2.json').read_text(),flush=True)
def lie():
 p=SH/'_rustcore/target/release/examples/c4m_lie';b=json.loads((D/'BUILD_ID.json').read_text());assert sha(p.read_bytes())==b['bins']['c4m_lie']
 with (D/'LIE.csv').open('w') as f:r=subprocess.run([str(p)],stdout=f,stderr=subprocess.PIPE,text=True,timeout=60)
 assert r.returncode==0,r.stderr
 a=np.genfromtxt(D/'LIE.csv',names=True,delimiter=',',dtype=None,encoding='utf8');assert len(a)==36
 rows=[dict(family=str(x['family']),eps=float(x['eps']),primal_gap=float(x['primal_gap']),first_rel=float(x['first_rel']),second_rel=float(x['second_rel']),B3second_norm=float(x['B3second_norm'])) for x in a]
 assert max(x['primal_gap'] for x in rows)<1e-13
 write('LIE_JET2.json',dict(rows=rows,scope='Actual native general Lie hierarchy one RK4 step, canonical scaling of N,A,S (Jacobi preserved); prescribed metric, lmax8, independent native stream_centered finite differences. Not whole autonomous non-I Einstein evolution.'))
 print(rows,flush=True)
if __name__=='__main__':{'build':build,'run':run,'analyze':analyze,'lie':lie}[sys.argv[1]]()
