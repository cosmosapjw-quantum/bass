#[path="c4i_jet/sidecar.rs"] mod sidecar;
use bianchi_rustcore::kinetic::{owned_thomson::ThomsonOwner,spin_sht::{index,C64}};
fn interp(x:&[Vec<f64>],u:f64)->f64{let i=x.partition_point(|r|r[0]<=u);if i==0{return x[0][1]}if i==x.len(){return x[i-1][1]}let(a,b)=(&x[i-1],&x[i]);a[1]+(b[1]-a[1])*(u-a[0])/(b[0]-a[0])}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let p=std::env::args().skip(1).collect::<Vec<_>>();if p.len()!=6{return Err("clock control steps nr nm lmax".into())}
 let clock=std::fs::read_to_string(&p[0])?.lines().skip(1).map(|l|l.split(',').map(str::parse::<f64>).collect::<Result<Vec<_>,_>>()).collect::<Result<Vec<_>,_>>()?;
 let c:Vec<f64>=std::fs::read_to_string(&p[1])?.split_whitespace().map(str::parse::<f64>).collect::<Result<_,_>>()?;
 if c.len()!=38{return Err("3 masses and seven STF controls".into())}
 let n:usize=p[2].parse()?;let nr:usize=p[3].parse()?;let nm:usize=p[4].parse()?;let lm:usize=p[5].parse()?;let vec=|k:usize|->[f64;5]{c[3+5*k..3+5*k+5].try_into().unwrap()};
 let spec=std::array::from_fn::<_,3,_>(|j|(c[j],1./3.,vec(1+2*j),vec(2+2*j)));
 let m=ThomsonOwner::with_radial_species(&spec,nr,nm,2*nm,lm,lm+4,2*lm+8)?;
 // Test exact constant-profile embedding and zero amplitude constructor on native moments.
 let const_spec=std::array::from_fn::<_,3,_>(|j|(c[j],1./3.,vec(1+2*j),vec(1+2*j)));
 let old=std::array::from_fn::<_,3,_>(|j|(c[j],1./3.,vec(1+2*j)));
 let a0=1./1601.;let om=ThomsonOwner::with_species(&old,nr,nm,2*nm,lm,lm+4,2*lm+8)?;
 let rm=ThomsonOwner::with_radial_species(&const_spec,nr,nm,2*nm,lm,lm+4,2*lm+8)?;
 let (r,o)=(rm.matter(&rm.initial(a0,vec(0))?)?,om.matter(&om.initial(a0,vec(0))?)?);
 let const_err=(r.rho-o.rho).abs()/o.rho+(r.pressure-o.pressure).norm()/o.pressure.norm();
 if const_err>1e-13{return Err(format!("constant radial embedding {const_err}").into())}
 let mut jet=sidecar::Companion::open(&std::env::var("C4I_TABLE")?);
 let cut=(1./21./a0).ln();let end=(0.2/a0).ln();let mut s=m.initial(a0,vec(0))?;let mut t=0.;let mut maxg:f64=0.;let mut minscreen:f64=1.;
 println!("epoch,ell,m,Ire,Iim,Ere,Eim,Bre,Bim");eprintln!("u,a,h,S0,S1,S2,S3,S4,gauss,rho,traceP");
 for (part,nn,left,right) in [(0,n,0.,cut),(1,n/4,cut,end)]{
 for i in 0..=nn {
  let g=m.constraint(&s)?;maxg=maxg.max(g.abs());
  if i==0||i==nn{let mat=m.matter(&s)?;eprintln!("{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",t,s.geometry.a,s.geometry.h,s.geometry.s[0],s.geometry.s[1],s.geometry.s[2],s.geometry.s[3],s.geometry.s[4],g,mat.rho,mat.pressure.trace());}
  if i==nn {
   jet.report(part);
   for p in s.sky.photons()?{let z=p.screen();let e=nalgebra::Matrix3::from_fn(|i,j|z[i][j]).symmetric_eigen().eigenvalues;let mut a=e.as_slice().to_vec();a.sort_by(f64::total_cmp);if a[0]< -1e-10{return Err("negative screen".into())}minscreen=minscreen.min(a[1]);}
   let y=&s.sky.coefficients;let norm=y[0][0].re;
   for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);let ii=y[0][k]/norm;let e=-(y[1][k]+y[2][k])*0.5/norm;let b=C64::new(0.,0.5)*(y[1][k]-y[2][k])/norm;println!("{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",ii.re,ii.im,e.re,e.im,b.re,b.im);}}break
  }
  let tar=left+(right-left)*(i+1)as f64/nn as f64;let du=tar-t;let ne0=interp(&clock,t);let nem=interp(&clock,t+du/2.);let(q,_)=m.step(&s,du,ne0,nem)?;jet.advance(du,ne0,nem);s=q;t=tar;
 }}
 jet.finish();
 eprintln!("max_gauss={maxg:.17e},min_screen={minscreen:.17e},const_err={const_err:.17e}");Ok(())
}
