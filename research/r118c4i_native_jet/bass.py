"""C4I pinned nonlinear native example with a synchronized DD Taylor companion."""
from pathlib import Path
import os,sys,json,subprocess,tarfile,io,gzip,hashlib,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;X=P/'r118c3x_native_coefficients';H=P/'r118c4h_rust_jet';G=P/'r118c4g_discrete_quadratic';F=P/'r118c4f_robust_transfer';SH=Path.home()/'r118c4i_bass_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 b=json.loads((X/'ops/BUILD_ID.json').read_text());i=b['identity'];assert not SH.exists();SH.mkdir()
 ar=subprocess.check_output(['git','-C',str(R),'archive',i['base'],'_rustcore','generated/rust/typeii','runtime/rust/typeii','research/r109_native_sky/hyrec_1100'])
 assert sha(ar)==i['archive_sha']
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(SH,filter='data')
 for name,hs in i['patched_sha'].items():
  p=SH/name;assert sha(p.read_bytes())==i['original_sha'][name];raw=gzip.decompress((X/'ops'/(p.name+'.gz')).read_bytes());assert sha(raw)==hs;p.write_bytes(raw)
 assert sha((SH/'_rustcore/Cargo.lock').read_bytes())==i['cargo_lock']
 old=(H/'jet_dd.rs').read_text();a=old.index('fn main(){');old=old[:a]
 companion=old+'''
pub struct Companion {r:BufReader<std::fs::File>, n:usize, k:usize, ol:D,k0:D, j:[[[D;5];5];14], c:[[D;7];5], x:State,h:D}
impl Companion{
 pub fn open(path:&str)->Self{
 let mut r=BufReader::new(std::fs::File::open(path).unwrap());let n=take(&mut r).val() as usize;assert_eq!(take(&mut r).val(),1.);let ol=take(&mut r);let k0=take(&mut r);
 let j=std::array::from_fn(|_|std::array::from_fn(|_|std::array::from_fn(|_|take(&mut r))));
 let c:[[D;7];5]=std::array::from_fn(|_|std::array::from_fn(|_|take(&mut r)));
 let x=State{s:std::array::from_fn(|i|c[i][0]),b:[D::Z;5],i:[D::Z;5],p:[D::Z;5],bb:[D::Z;14]};
 Self{r,n,k:0,ol,k0,j,c,x,h:D::Z}
 }
 pub fn advance(&mut self,du:f64,ne0:f64,nem:f64){
 assert!(self.k<self.n);let dt=take(&mut self.r);assert!((dt.val()-du).abs()<2e-14);let mut a=stage(&mut self.r);let mut m=stage(&mut self.r);
 assert!((a.ne.val()-ne0).abs()<1e-10*ne0.abs().max(1.));assert!((m.ne.val()-nem).abs()<1e-10*nem.abs().max(1.));a.ne=D(ne0,0.);m.ne=D(nem,0.);
 if self.k==0{self.h=(a.rho+self.ol).sqrt();}
 let x=self.x;let h=self.h;let q=(a.rho+a.tr-2.*self.ol)/(2.*h*h);let hm=h*(-dt/2.*(D::ONE+q)).exp();let qm=(m.rho+m.tr-2.*self.ol)/(2.*hm*hm);
 let (_,f)=rhs(a,h,x,&self.c,self.ol);let sm=add(x.s,f,dt/2.);let bm=add(x.b,x.s,dt/2.);
 let mut mid=stream(x,x.s,dt/2.,self.k0*(a.ne+m.ne)/2./h*dt/2.,&self.j);mid.s=sm;mid.b=bm;
 let (_,fm)=rhs(m,hm,mid,&self.c,self.ol);let mut y=stream(x,sm,dt,self.k0*m.ne/hm*dt,&self.j);y.s=add(x.s,fm,dt);y.b=add(x.b,sm,dt);self.x=y;self.h=h*(-dt*(D::ONE+qm)).exp();self.k+=1;
 }
 pub fn report(&self,part:usize){let mut s=format!("C4I_JET,{part},{},{}",self.k,self.h.val());for v in self.x.bb{s.push_str(&format!(",{:.17e}",v.val()));}eprintln!("{s}");}
 pub fn finish(&mut self){assert_eq!(self.k,self.n);let mut b=[0;1];assert_eq!(self.r.read(&mut b).unwrap(),0);}
}
'''
 src=(X/'native.rs').read_text();assert sha(src.encode())==i['example_sha']
 src='#[path="c4i_jet/sidecar.rs"] mod sidecar;\n'+src
 def rep(a,b):
  nonlocal src
  assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b)
 rep(' let cut=(1./21./a0).ln();',' let mut jet=sidecar::Companion::open(&std::env::var("C4I_TABLE")?);\n let cut=(1./21./a0).ln();')
 rep('  if i==nn {\n   for p','  if i==nn {\n   jet.report(part);\n   for p')
 rep('let(q,_)=m.step(&s,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;t=tar;', 'let ne0=interp(&clock,t);let nem=interp(&clock,t+du/2.);let(q,_)=m.step(&s,du,ne0,nem)?;jet.advance(du,ne0,nem);s=q;t=tar;')
 rep(' eprintln!("max_gauss=', ' jet.finish();\n eprintln!("max_gauss=')
 p=SH/'_rustcore/examples/c4i_jet';p.mkdir();(p/'sidecar.rs').write_text(companion);(SH/'_rustcore/examples/c3x_radial.rs').write_text(src)
 (D/'sidecar.rs').write_text(companion);(D/'native.rs').write_text(src)
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'_rustcore/Cargo.toml'),'--example','c3x_radial']
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=420)
 assert r.returncode==0
 bin=SH/'_rustcore/target/release/examples/c3x_radial';raw=bin.read_bytes();(D/'native_jet.gz').write_bytes(gzip.compress(raw,mtime=0))
 write('BUILD_ID.json',dict(base=i['base'],archive_sha=sha(ar),patches=i['patched_sha'],native_sha=sha(src.encode()),sidecar_sha=sha(companion.encode()),binary_sha=sha(raw),binary_archive_sha=sha((D/'native_jet.gz').read_bytes()),cargo_lock=i['cargo_lock'],cmd=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def tables(n,nr,ctrl):
 g={'__file__':str(G/'bass.py'),'__name__':'prior'};exec(compile((G/'bass.py').read_text(),str(G/'bass.py'),'exec'),g)
 ld=np.longdouble;J=g['J'][1];J=np.concatenate([J.real,J.imag],axis=0);a0,cut,end=g['a0'],g['cut'],g['end'];clk=g['clock'];OL,K0,OG=g['OL'],g['K0'],g['OG']
 # use the actual native f64 time loop target calculation, not independent linspace rounding
 a=float(1./1601.);cut0=np.log(1./21./a);end0=np.log(.2/a)
 tt=np.r_[[cut0*i/n for i in range(n+1)],[cut0+(end0-cut0)*i/(n//4) for i in range(1,n//4+1)]].astype(ld)
 dt=np.diff(tt);mid=(tt[:-1]+tt[1:])/2;ts=np.empty(2*len(dt),ld);ts[::2]=tt[:-1];ts[1::2]=mid;bg,src=g['bg_table'](ts,nr)
 ne=np.interp(ts.astype(float),clk['u'],clk['ne_m3']);rad=ld(2)/15*OG/(a0*np.exp(ts))**4;stage=np.column_stack([bg,src.reshape(-1,6),rad,ne]);data=np.column_stack([dt,stage[::2],stage[1::2]])
 q=SH/f'table_{n}_{nr}.bin'
 with q.open('wb') as f:
  for a in [np.array([len(dt),1,OL,K0],ld),J,ctrl,data]:
   a=np.asarray(a,ld);hi=a.astype('<f8');lo=(a-hi.astype(ld)).astype('<f8');f.write(np.stack([hi,lo],axis=-1).tobytes())
 return q
def native():
 bin=SH/'_rustcore/target/release/examples/c3x_radial';bid=json.loads((D/'BUILD_ID.json').read_text());assert sha(bin.read_bytes())==bid['binary_sha']
 ctrl=np.load(F/'TRAIN_CONTROLS.npz')['control_new'];clock=P/'r118c3l_reachable_sky/clock.csv';nr=192
 tb={n:tables(n,nr,ctrl) for n in [4096,8192,16384]}
 # 14 finite-amplitude cases plus independent byte-for-byte replay against C4F existing robust +0.02.
 jobs=[(n,e) for n in [4096,8192] for e in [0.,-.01,.01,-.02,.02,-.04,.04]]+[(16384,.02)]
 def job(v):
  n,e=v;tag=f'n{n}_{e:g}';p=D/(tag+'.ctrl');np.savetxt(p,np.r_[[.001,.006,.05],(e*ctrl.T).ravel()][None],fmt='%.17e')
  env=os.environ.copy();env['C4I_TABLE']=str(tb[n]);tm=time.monotonic()
  with (D/(tag+'.csv')).open('w') as f,(D/(tag+'.geom')).open('w') as g:r=subprocess.run([str(bin),str(clock),str(p),str(n),str(nr),'8','8'],env=env,stdout=f,stderr=g,timeout=300)
  raw=(D/(tag+'.geom')).read_text();assert r.returncode==0 and 'max_gauss=' in raw
  lines=[l.split(',') for l in raw.splitlines() if l.startswith('C4I_JET,')];assert len(lines)==2 and int(lines[-1][2])==n+n//4
  if n==16384:
   old=F/'new_0.02_16384.csv';assert old.is_file()
   assert (D/(tag+'.csv')).read_bytes()==old.read_bytes()
  return dict(n=n,eps=e,tag=tag,exit=r.returncode,seconds=time.monotonic()-tm,sidecar=[list(map(float,l[4:])) for l in lines],native_replay=(n==16384),table_sha=sha(tb[n].read_bytes()),ctrl_sha=sha(p.read_bytes()))
 rows=[]
 with cf.ThreadPoolExecutor(max_workers=4) as ex:
  for x in ex.map(job,jobs):rows.append(x);print(x['tag'],x['seconds'],flush=True);write('NATIVE_RUNS.json',rows)
 out=[]
 for n in [4096,8192]:
  rr=[r for r in rows if r['n']==n];s=np.array(rr[0]['sidecar']);assert all(np.array_equal(s,np.array(x['sidecar'])) for x in rr)
  def read(e,epoch):
   a=np.genfromtxt(D/f'n{n}_{e:g}.csv',names=True,delimiter=',');m=(a['epoch']==epoch)&(a['ell']==3);return a['Bre'][m]+1j*a['Bim'][m]
  for epoch in [0,1]:
   zero=read(0,epoch);ee=[.01,.02,.04];y=np.array([(read(e,epoch)+read(-e,epoch)-2*zero)/(2*e*e) for e in ee]);fit=np.linalg.solve(np.vander(np.array(ee)**2,3,increasing=True),y);v=s[epoch,:7]+1j*s[epoch,7:]
   out.append(dict(n=n,epoch=epoch,sidecar_norm=float(np.linalg.norm(v)),native_B2_norm=float(np.linalg.norm(fit[0])),vector_gap=float(np.linalg.norm(fit[0]-v)),B4_norm=float(np.linalg.norm(fit[1])),B6_norm=float(np.linalg.norm(fit[2])),native_B2_re=fit[0].real.tolist(),native_B2_im=fit[0].imag.tolist(),sidecar_re=v.real.tolist(),sidecar_im=v.imag.tolist()))
 write('COUPLED_NATIVE_JET.json',dict(rows=out,native_runs=len(rows),replay_16384=rows[-1]['native_replay'],clock_sha=sha(clock.read_bytes()),control_sha=sha((F/'TRAIN_CONTROLS.npz').read_bytes()),scope='DD Taylor companion called inside actual nonlinear owner example step loop, same native ne and time grid, separate radial table; not full differentiation of production nonlinear state'))
 print(out,flush=True)
if __name__=='__main__':{'build':build,'native':native}[sys.argv[1]]()
