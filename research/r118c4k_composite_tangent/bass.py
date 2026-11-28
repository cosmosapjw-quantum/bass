"""C4K full composed first-order native discrete tangent, actual radial control path."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io,gzip,os,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;X=P/'r118c3x_native_coefficients';I=P/'r118c4i_native_jet';J=P/'r118c4j_operator_jet';SH=Path.home()/'r118c4k_bass_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 i=json.loads((X/'ops/BUILD_ID.json').read_text())['identity'];prev=json.loads((J/'BUILD_ID.json').read_text());SH.mkdir(exist_ok=os.environ.get("C4K_REBUILD")=="1")
 ar=subprocess.check_output(['git','-C',str(R),'archive',i['base'],'_rustcore','generated/rust/typeii','runtime/rust/typeii','research/r109_native_sky/hyrec_1100']);assert sha(ar)==i['archive_sha']
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(SH,filter='data')
 changes={}
 for name,hs in i['patched_sha'].items():
  p=SH/name;v=prev['changes'][name];s=(J/v['file']).read_text();assert sha(s.encode())==v['sha']
  if p.name=='owned_vlasov.rs':
   tok='    pub fn initial(';assert s.count(tok)==1;s=s.replace(tok,(D/'matter.rs.txt').read_text()+'\n'+tok)
  else:s+='\n'+(D/'thomson.rs.txt').read_text()
  p.write_text(s);dst='instrumented_'+p.name;(D/dst).write_text(s);changes[name]=dict(file=dst,sha=sha(s.encode()),prior_sha=v['sha'])
 src=(X/'native.rs').read_text();assert sha(src.encode())==i['example_sha']
 a=' let cut=(1./21./a0).ln();'
 b=''' let tangent=std::env::var_os("C4K_TANGENT").is_some();
 let hierarchy=bianchi_rustcore::kinetic::lie_hierarchy::LieHierarchy::new(lm,true,4.)?;
 let dw=m.c4k_weights(&spec,nr,nm,2*nm)?;
 let cut=(1./21./a0).ln();'''
 assert src.count(a)==1;src=src.replace(a,b)
 a='let mut s=m.initial(a0,vec(0))?;let mut t=0.;'
 b='let mut s=m.initial(a0,vec(0))?;let mut d=m.c4k_initial_d(&s,&dw)?;let mut t=0.;if tangent{eprintln!("C4K_INIT,{:.17e}",m.c4k_constraint_d(&s,&d,&dw)?);}'
 assert src.count(a)==1;src=src.replace(a,b)
 a='  if i==nn {\n   for p'
 b='''  if i==nn {
   if tangent{
    use bianchi_rustcore::kinetic::memory_mixture::stf_components;
    let mat=m.matter(&s)?;let dm=m.c4k_matter_d(&s,&d,&dw)?;let det=(s.geometry.f.try_inverse().unwrap()*d.f).trace();
    eprint!("C4K_GEOM,{part},{:.17e},{:.17e},{:.17e},{:.17e}",d.h/s.geometry.h,m.c4k_constraint_d(&s,&d,&dw)?,det,dm.rho/mat.rho);
    for v in stf_components(d.s){eprint!(",{v:.17e}");}for v in d.f.iter(){eprint!(",{v:.17e}");}eprintln!();
    // independent fixed-coframe matter weight and continuity test.
    let dm=m.c4k_weight_only(&s,&dw)?;let bm=m.c4k_fixed_matter(s.geometry.a,&s.geometry.f)?;
    for ep in [0.01,0.003,0.001]{
     let ss=|x:f64|spec.map(|(m,f,a,b)|(m,f,a.map(|v|v*(1.+x)),b.map(|v|v*(1.+x))));
     let p=ThomsonOwner::with_radial_species(&ss(ep),nr,nm,2*nm,lm,lm+4,2*lm+8)?;
     let q=ThomsonOwner::with_radial_species(&ss(-ep),nr,nm,2*nm,lm,lm+4,2*lm+8)?;
     let a=p.c4k_fixed_matter(s.geometry.a,&s.geometry.f)?;let b=q.c4k_fixed_matter(s.geometry.a,&s.geometry.f)?;
     let dr=(a.rho-b.rho)/(2.*ep);let dp=(a.pressure-b.pressure)/(2.*ep);
     eprintln!("C4K_WEIGHT,{part},{ep:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",dm.rho/bm.rho,dm.pressure.norm()/bm.pressure.norm(),(dr-dm.rho).abs()/bm.rho,(dp-dm.pressure).norm()/bm.pressure.norm());
    }
    let mut a=s.clone();let mut b=s.clone();let ep=1e-4;
    a.geometry.a*=f64::exp(ep);b.geometry.a*=f64::exp(-ep);
    let p=m.c4k_weight_only(&a,&dw)?;let q=m.c4k_weight_only(&b,&dw)?;let dr=(p.rho-q.rho)/(2.*ep);
    eprintln!("C4K_CONT,{part},{:.17e}",(dr+3.*dm.rho+dm.pressure.trace()).abs()/bm.rho);
    let y=&s.sky.coefficients;let dy=&d.sky;let norm=y[0][0].re;let dn=dy[0][0].re;
    for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);
     let ii=dy[0][k]/norm-y[0][k]*dn/norm.powi(2);
     let ee=-(dy[1][k]+dy[2][k])*0.5/norm+(y[1][k]+y[2][k])*0.5*dn/norm.powi(2);
     let bb=C64::new(0.,0.5)*((dy[1][k]-dy[2][k])/norm-(y[1][k]-y[2][k])*dn/norm.powi(2));
     eprintln!("C4K_SKY,{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",ii.re,ii.im,ee.re,ee.im,bb.re,bb.im);
    }}
   }
   for p'''
 assert src.count(a)==1;src=src.replace(a,b)
 a='let(q,_)=m.step(&s,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;t=tar;'
 b='if tangent{let (q,nd)=m.c4k_step(&s,&d,&dw,&hierarchy,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;d=nd;}else{let(q,_)=m.step(&s,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;}t=tar;'
 assert src.count(a)==1;src=src.replace(a,b)
 p=SH/'_rustcore/examples/c3x_radial.rs';p.write_text(src);(D/'native.rs').write_text(src);changes[str(p.relative_to(SH))]=dict(file='native.rs',sha=sha(src.encode()),prior_sha=i['example_sha'])
 assert sha((SH/'_rustcore/Cargo.lock').read_bytes())==i['cargo_lock']
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'_rustcore/Cargo.toml'),'--example','c3x_radial']
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 bin=SH/'_rustcore/target/release/examples/c3x_radial';raw=bin.read_bytes();(D/'composite_jet.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(base=i['base'],archive_sha=i['archive_sha'],changes=changes,binary_sha=sha(raw),cargo_lock=i['cargo_lock'],cmd=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def run():
 b=SH/'_rustcore/target/release/examples/c3x_radial';bid=json.loads((D/'BUILD_ID.json').read_text());assert sha(b.read_bytes())==bid['binary_sha']
 base=np.loadtxt(I/'n4096_0.02.ctrl').reshape(-1);clk=P/'r118c3l_reachable_sky/clock.csv'
 jobs=[0.,-.01,.01,-.003,.003]
 def job(e):
  tag=f'p{e:g}';c=base.copy();c[3:]*=1+e;p=D/(tag+'.ctrl');np.savetxt(p,c[None],fmt='%.17e')
  env=os.environ.copy()
  if e==0:env['C4K_TANGENT']='1'
  else:env.pop('C4K_TANGENT',None)
  t=time.monotonic();cmd=[str(b),str(clk),str(p),'4096','192','8','8']
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run(cmd,env=env,stdout=f,stderr=g,timeout=350)
  assert r.returncode==0
  print(tag,r.returncode,time.monotonic()-t,flush=True);return dict(tag=tag,param=e,exit=r.returncode,seconds=time.monotonic()-t,control_sha=sha(p.read_bytes()),cmd=cmd)
 with cf.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(job,jobs))
 write('RUNS.json',rows)
 raw=(D/'p0.geom').read_text();old=(I/'n4096_0.02.geom').read_text()
 pure=lambda s:[l for l in s.splitlines() if not l.startswith('C4')]
 same=(D/'p0.csv').read_bytes()==(I/'n4096_0.02.csv').read_bytes();geom_same=pure(raw)==pure(old)
 # Actual arithmetic association may vary by tiny roundoff if implementation changed; quantify instead of treating approximate as byte match.
 def read(e):return np.genfromtxt(D/f'p{e:g}.csv',names=True,delimiter=',')
 def sky(a):return np.stack([a[k+'re']+1j*a[k+'im'] for k in ['I','E','B']],axis=1)
 a=read(0);ref=np.genfromtxt(I/'n4096_0.02.csv',names=True,delimiter=',');base_gap=float(np.linalg.norm(sky(a)-sky(ref))/np.linalg.norm(sky(ref)));assert base_gap<1e-13
 sr=np.array([list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith('C4K_SKY,')]);assert len(sr)==len(a) and np.array_equal(sr[:,:3],np.stack([a['epoch'],a['ell'],a['m']],axis=1))
 dy=sr[:,3::2]+1j*sr[:,4::2];gr=np.array([list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith('C4K_GEOM,')]);assert gr.shape==(2,19)
 init=float(next(l.split(',')[1] for l in raw.splitlines() if l.startswith('C4K_INIT,')))
 def geom(e):
  r=[list(map(float,l.split(','))) for l in pure((D/f'p{e:g}.geom').read_text()) if l and l[0].isdigit()];return np.array(r)[[1,3]]
 bg=geom(0);fd=[]
 for e in [.01,.003]:
  up,um=read(e),read(-e);y=(sky(up)-sky(um))/(2*e);gp,gm=geom(e),geom(-e);dg=(gp-gm)/(2*e)
  for ep in [0,1]:
   row=dict(eps=e,epoch=ep,lnh_tangent=gr[ep,1],lnh_FD=dg[ep,2]/bg[ep,2],lnh_gap=float(abs(gr[ep,1]-dg[ep,2]/bg[ep,2])),shear_relative=float(np.linalg.norm(gr[ep,5:10]-dg[ep,3:8])/np.linalg.norm(gr[ep,5:10])))
   for j,k in enumerate(['I','E','B']):
    mask=(a['epoch']==ep)&(a['ell']>0);x=dy[mask,j];v=y[mask,j];row[k+'_relative']=float(np.linalg.norm(x-v)/max(np.linalg.norm(x),1e-300));row[k+'_norm']=float(np.linalg.norm(x))
   fd.append(row)
 weight=[list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith('C4K_WEIGHT,')];cont=[list(map(float,l.split(',')[1:])) for l in raw.splitlines() if l.startswith('C4K_CONT,')]
 assert len(weight)==6 and len(cont)==2
 np.savez_compressed(D/'COMPOSITE.npz',geometry=gr,sky_index=sr[:,:3],sky_tangent=dy)
 write('COMPOSITE.json',dict(runs=rows,base_byte_replay=same,geometry_byte_replay=geom_same,base_sky_relative_gap=base_gap,initial_gauss_tangent=init,geometry=gr.tolist(),fd=fd,weight_fixed_coframe=weight,continuity_fixed_coframe=cont,scope='first-order tangent of actual fixed-clock Bianchi-I native midpoint/Strang discrete step, all 5120 steps, radial amplitude and initial shear scaled together; no second order or external matter tangent'))
 print('RESULT',json.loads((D/'COMPOSITE.json').read_text()),flush=True)
if __name__=='__main__':{'build':build,'run':run}[sys.argv[1]]()
