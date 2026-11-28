"""C4J actual C3X native operator derivative probe; isolated pinned shadow."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,io,gzip,os,time,numpy as np
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;X=P/'r118c3x_native_coefficients';I=P/'r118c4i_native_jet';SH=Path.home()/'r118c4j_bass_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 b=json.loads((X/'ops/BUILD_ID.json').read_text());i=b['identity'];SH.mkdir(exist_ok=False)
 ar=subprocess.check_output(['git','-C',str(R),'archive',i['base'],'_rustcore','generated/rust/typeii','runtime/rust/typeii','research/r109_native_sky/hyrec_1100']);assert sha(ar)==i['archive_sha']
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(SH,filter='data')
 changes={}
 for name,hs in i['patched_sha'].items():
  p=SH/name;assert sha(p.read_bytes())==i['original_sha'][name];raw=gzip.decompress((X/'ops'/(p.name+'.gz')).read_bytes());assert sha(raw)==hs
  s=raw.decode();tag='    pub fn initial('
  assert s.count(tag)==1
  patch='matter.rs.txt' if p.name=='owned_vlasov.rs' else 'thomson.rs.txt'
  s=s.replace(tag,(D/patch).read_text()+'\n'+tag)
  p.write_text(s);dst='instrumented_'+p.name;(D/dst).write_text(s);changes[name]=dict(file=dst,sha=sha(s.encode()),prior_sha=hs)
 src=(X/'native.rs').read_text();assert sha(src.encode())==i['example_sha']
 src=(D/'stream.rs.txt').read_text()+'\n'+src
 a='  if i==nn {\n   for p';b='''  if i==nn {
   eprintln!("C4J_KIND,coframe,{part}");
   let g=nalgebra::Matrix3::new(0.12,0.04,-0.03,0.04,-0.05,0.02,-0.03,0.02,-0.07);
   m.c4j_matter_probe(&s,&g)?;
   eprintln!("C4J_KIND,rotation,{part}");
   let r=nalgebra::Matrix3::new(0.,-0.2,0.1,0.2,0.,-0.05,-0.1,0.05,0.);
   m.c4j_matter_probe(&s,&r)?;
   for case in 0..3{c4j_stream(&s,lm,case)?;}
   for p'''
 assert src.count(a)==1;src=src.replace(a,b)
 p=SH/'_rustcore/examples/c3x_radial.rs';p.write_text(src);(D/'native.rs').write_text(src);changes[str(p.relative_to(SH))]=dict(file='native.rs',sha=sha(src.encode()),prior_sha=i['example_sha'])
 assert sha((SH/'_rustcore/Cargo.lock').read_bytes())==i['cargo_lock']
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'_rustcore/Cargo.toml'),'--example','c3x_radial']
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 bin=SH/'_rustcore/target/release/examples/c3x_radial';raw=bin.read_bytes();(D/'operator_jet.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(base=i['base'],archive_sha=i['archive_sha'],changes=changes,binary_sha=sha(raw),cargo_lock=i['cargo_lock'],cmd=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def run():
 b=SH/'_rustcore/target/release/examples/c3x_radial';bid=json.loads((D/'BUILD_ID.json').read_text());assert sha(b.read_bytes())==bid['binary_sha']
 ctrl=I/'n4096_0.02.ctrl';clk=P/'r118c3l_reachable_sky/clock.csv';t=time.monotonic();cmd=[str(b),str(clk),str(ctrl),'4096','192','8','8']
 with (D/'native.csv').open('w') as f,(D/'native.geom').open('w') as g:r=subprocess.run(cmd,stdout=f,stderr=g,timeout=220)
 assert r.returncode==0
 raw=(D/'native.geom').read_text();same=(D/'native.csv').read_bytes()==(I/'n4096_0.02.csv').read_bytes();assert same
 old=[l for l in (I/'n4096_0.02.geom').read_text().splitlines() if not l.startswith('C4I_JET,')]
 now=[l for l in raw.splitlines() if not l.startswith('C4J_')]
 assert old==now
 mat=[];stream=[];kind=None
 for l in raw.splitlines():
  v=l.split(',')
  if v[0]=='C4J_KIND':kind=v[1];epoch=int(v[2])
  elif v[0]=='C4J_MAT':
   a,eps,r1,r2,e1,e2,p1,p2,pe1,pe2=map(float,v[1:]);mat.append(dict(kind=kind,epoch=epoch,a=a,eps=eps,rho1=r1,rho2=r2,rho1_scaled_gap=e1,rho2_scaled_gap=e2,P1_norm=p1,P2_norm=p2,P1_scaled_gap=pe1,P2_scaled_gap=pe2))
  elif v[0]=='C4J_STREAM':
   a,c,eps,bnd,b0,s1,s2,e1,e2=map(float,v[1:]);stream.append(dict(a=a,case=int(c),eps=eps,bound=bnd,baseline_gap=b0,jet1_norm=s1,jet2_norm=s2,jet1_relative_gap=e1,jet2_relative_gap=e2))
 assert len(mat)==12 and len(stream)==18
 assert max(x['baseline_gap'] for x in stream)<1e-13
 assert max(abs(x['rho1'])+abs(x['rho2']) for x in mat if x['kind']=='rotation')<1e-12
 assert max(x['jet1_relative_gap'] for x in stream)<1e-5 and max(x['jet2_relative_gap'] for x in stream)<1e-3
 write('OPERATOR_JET.json',dict(matter=mat,stream=stream,byte_replay=same,geometry_replay=old==now,seconds=time.monotonic()-t,cmd=cmd,control_sha=sha(ctrl.read_bytes()),clock_sha=sha(clk.read_bytes()),scope='actual finite-amplitude nonlinear C3X endpoint states, fixed particle weights and a, exact first and second coframe coefficient; actual LieHierarchy RK4 fixed one-substep polynomial jet at three local Lie generator configurations; not entire coupled evolution derivative'))
 print('MAT',mat,flush=True);print('STREAM',stream,flush=True)
if __name__=='__main__':{'build':build,'run':run}[sys.argv[1]]()
