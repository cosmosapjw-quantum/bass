"""Native second Taylor coefficient, source locked C4K. Independent Lie stress probe."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io,gzip,os,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;K=P/'r118c4k_composite_tangent';SH=Path.home()/'r118c4l_bass_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 prev=json.loads((K/'BUILD_ID.json').read_text());SH.mkdir(exist_ok=os.environ.get('C4L_REBUILD')=='1')
 ar=subprocess.check_output(['git','-C',str(R),'archive',prev['base'],'_rustcore','generated/rust/typeii','runtime/rust/typeii','research/r109_native_sky/hyrec_1100']);assert sha(ar)==prev['archive_sha']
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(SH,filter='data')
 changes={}
 for name,v in prev['changes'].items():
  p=SH/name;s=(K/v['file']).read_text();assert sha(s.encode())==v['sha']
  if p.name=='owned_vlasov.rs':
   tok='    pub fn initial(';assert s.count(tok)==1;s=s.replace(tok,(D/'matter.rs.txt').read_text()+'\n'+tok)
  elif p.name=='owned_thomson.rs':s+='\n'+(D/'thomson.rs.txt').read_text()
  else:
   a='let tangent=std::env::var_os("C4K_TANGENT").is_some();'
   assert s.count(a)==1;s=s.replace(a,'let jet2=std::env::var_os("C4L_JET2").is_some();let tangent=jet2||std::env::var_os("C4K_TANGENT").is_some();')
   a='let dw=m.c4k_weights(&spec,nr,nm,2*nm)?;';assert s.count(a)==1;s=s.replace(a,a+'\n let w2=m.c4l_weights2(&spec,nr,nm,2*nm)?;')
   a='let mut d=m.c4k_initial_d(&s,&dw)?;';assert s.count(a)==1;s=s.replace(a,a+'let mut b=m.c4l_initial2(&s,&d,&dw,&w2)?;if jet2{eprintln!("C4L_INIT,{:.17e}",m.c4l_constraint2(&s,&d,&b,&dw,&w2)?);}')
   a='  if i==nn {\n   if tangent{';assert s.count(a)==1;s=s.replace(a,'''  if i==nn {
   if jet2 {
    use bianchi_rustcore::kinetic::memory_mixture::stf_components;
    let mat=m.matter(&s)?;let m2=m.c4l_matter2(&s,&d,&b,&dw,&w2)?;let inv=s.geometry.f.try_inverse().unwrap();let a=inv*d.f;let det=(inv*b.f).trace()-0.5*(a*a).trace();
    eprint!("C4L_GEOM,{part},{:.17e},{:.17e},{:.17e},{:.17e}",b.h/s.geometry.h-0.5*(d.h/s.geometry.h).powi(2),m.c4l_constraint2(&s,&d,&b,&dw,&w2)?,det,m2.rho/mat.rho);
    for v in stf_components(b.s){eprint!(",{v:.17e}");}for v in b.f.iter(){eprint!(",{v:.17e}");}eprintln!();
    let y=&s.sky.coefficients;let d1=&d.sky;let d2=&b.sky;let n=y[0][0].re;let n1=d1[0][0].re;let n2=d2[0][0].re;
    let norm=|j:usize,k:usize|d2[j][k]/n-d1[j][k]*(n1/n.powi(2))+y[j][k]*(n1*n1/n.powi(3)-n2/n.powi(2));
    for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);let ii=norm(0,k);let ee=-(norm(1,k)+norm(2,k))*0.5;let bb=C64::new(0.,0.5)*(norm(1,k)-norm(2,k));eprintln!("C4L_SKY,{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",ii.re,ii.im,ee.re,ee.im,bb.re,bb.im);}}
   }
   if tangent{''')
   a='if tangent{let (q,nd)=m.c4k_step';assert s.count(a)==1;s=s.replace(a,'if jet2{let(q,nd,nb)=m.c4l_step(&s,&d,&b,&dw,&w2,&hierarchy,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;d=nd;b=nb;}else if tangent{let (q,nd)=m.c4k_step')
  p.write_text(s);(D/v['file']).write_text(s);changes[name]=dict(file=v['file'],sha=sha(s.encode()),prior_sha=v['sha'])
 p=SH/'_rustcore/examples/c4l_lie.rs';s=(D/'lie.rs.txt').read_text();p.write_text(s);changes[str(p.relative_to(SH))]=dict(file='lie.rs.txt',sha=sha(s.encode()),prior_sha=None)
 assert sha((SH/'_rustcore/Cargo.lock').read_bytes())==prev['cargo_lock'];env=os.environ.copy();env['CARGO_BUILD_JOBS']='3'
 cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'_rustcore/Cargo.toml'),'--example','c3x_radial','--example','c4l_lie']
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 bins={}
 for exe,archive in [('c3x_radial','jet2.gz'),('c4l_lie','lie.gz')]:
  raw=(SH/'_rustcore/target/release/examples'/exe).read_bytes();(D/archive).write_bytes(gzip.compress(raw,mtime=0));bins[exe]=sha(raw)
 write('BUILD_ID.json',dict(base=prev['base'],archive_sha=prev['archive_sha'],changes=changes,binary_sha=bins['c3x_radial'],lie_sha=bins['c4l_lie'],cargo_lock=prev['cargo_lock'],command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def run():
 p=SH/'_rustcore/target/release/examples/c3x_radial';b=json.loads((D/'BUILD_ID.json').read_text());assert sha(p.read_bytes())==b['binary_sha']
 clk=P/'r118c3l_reachable_sky/clock.csv';base=np.loadtxt(K/'p0.ctrl').reshape(-1)
 jobs=[('jet4096',4096,0.,True),('jet2048',2048,0.,True),('jet8192',8192,0.,True),('p-0.01',4096,-.01,False),('p0.01',4096,.01,False),('p-0.003',4096,-.003,False),('p0.003',4096,.003,False)]
 def job(q):
  tag,n,ep,jet=q;c=base.copy();c[3:]*=1+ep;ctrl=D/(tag+'.ctrl');np.savetxt(ctrl,c[None],fmt='%.17e')
  env=os.environ.copy();env['C4K_TANGENT']='1'
  if jet:env['C4L_JET2']='1'
  else:env.pop('C4L_JET2',None)
  cmd=[str(p),str(clk),str(ctrl),str(n),'192','8','8'];t=time.monotonic()
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run(cmd,env=env,stdout=f,stderr=g,timeout=400)
  row=dict(tag=tag,steps=n,param=ep,jet2=jet,exit=r.returncode,seconds=time.monotonic()-t,cmd=cmd,control_sha=sha(ctrl.read_bytes()));print(row,flush=True);return row
 with cf.ThreadPoolExecutor(max_workers=3) as ex:rr=list(ex.map(job,jobs))
 write('RUNS.json',rr);assert all(r['exit']==0 for r in rr)
def parse(tag,prefix):
 raw=(D/(tag+'.geom')).read_text();g=np.array([list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith(prefix+'_GEOM,')]);s=np.array([list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith(prefix+'_SKY,')])
 assert g.shape==(2,19) and s.shape==(162,9);return g,s[:,:3],s[:,3::2]+1j*s[:,4::2]
def analyze():
 g,idx,y=parse('jet4096','C4L');g1,ii,d1=parse('jet4096','C4K');assert np.array_equal(ii,idx)
 kraw=(K/'p0.geom').read_text();r1=np.array([list(map(float,l.split(',')[1:])) for l in kraw.splitlines() if l.startswith('C4K_SKY,')]);prev=r1[:,3::2]+1j*r1[:,4::2]
 same=(D/'jet4096.csv').read_bytes()==(K/'p0.csv').read_bytes();d1gap=float(np.linalg.norm(d1-prev)/np.linalg.norm(prev));assert same and d1gap<1e-12
 rows=[]
 def primal(tag):
  a=np.genfromtxt(K/(tag+'.csv'),names=True,delimiter=',');return np.stack([a[k+'re']+1j*a[k+'im'] for k in ['I','E','B']],axis=1)
 y0=primal('p0')
 for h in [.01,.003]:
  gp,ip,yp=parse(f'p{h:g}','C4K');gm,im,ym=parse(f'p{-h:g}','C4K');assert np.array_equal(ip,idx) and np.array_equal(im,idx)
  f=(yp/(1+h)-ym/(1-h))/(4*h);fg=(gp[:,1:]/(1+h)-gm[:,1:]/(1-h))/(4*h)
  f0=(primal(f'p{h:g}')+primal(f'p{-h:g}')-2*y0)/(2*h*h)
  for ep in [0,1]:
   mask=(idx[:,0]==ep)&(idx[:,1]>0);row=dict(h=h,epoch=ep,lnH2=g[ep,1],lnH2_tangent_secant=fg[ep,0],shear2_relative=float(np.linalg.norm(g[ep,5:10]-fg[ep,4:9])/np.linalg.norm(g[ep,5:10])))
   for j,k in enumerate(['I','E','B']):
    a=y[mask,j];row[k]=dict(norm=float(np.linalg.norm(a)),tangent_secant_relative=float(np.linalg.norm(a-f[mask,j])/max(np.linalg.norm(a),1e-300)),primal_FD_relative=float(np.linalg.norm(a-f0[mask,j])/max(np.linalg.norm(a),1e-300)))
   rows.append(row)
 refine=[]
 data=[parse(f'jet{n}','C4L') for n in [2048,4096,8192]]
 for ep in [0,1]:
  r=dict(epoch=ep,gauss2=[float(a[0][ep,2]) for a in data],det2=[float(a[0][ep,3]) for a in data])
  for j,k in enumerate(['I','E','B']):
   m=(idx[:,0]==ep)&(idx[:,1]>0);v=[a[2][m,j] for a in data];d=[float(np.linalg.norm(v[1]-v[0])),float(np.linalg.norm(v[2]-v[1]))];r[k]=dict(differences=d,ratio=d[0]/max(d[1],1e-300))
  refine.append(r)
 init=float(next(l.split(',')[1] for l in (D/'jet4096.geom').read_text().splitlines() if l.startswith('C4L_INIT,')))
 np.savez_compressed(D/'JET2.npz',geometry=g,indices=idx,sky2=y,sky1=d1)
 out=dict(base_byte_replay=same,first_order_relative=d1gap,initial_gauss2=init,geometry=g.tolist(),rows=rows,refinement=refine,scope='second Taylor coefficient Y2=Y doubleprime/2 of full represented fixed-clock Bianchi I native midpoint/Strang; independent first tangent and primal secants, finite time and radial grid.')
 write('JET2.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':{'build':build,'run':run,'analyze':analyze}[sys.argv[1]]()
