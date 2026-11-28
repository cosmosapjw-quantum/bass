use bianchi_rustcore::kinetic::lie_hierarchy::LieHierarchy;
use bianchi_rustcore::geom::lie::{LieData,photon_potentials};
type V=Vec<Vec<C64>>;
type Jet=[V;3];
fn ax(y:&Jet,k:&Jet,h:f64)->Jet{std::array::from_fn(|i|y[i].iter().zip(&k[i]).map(|(a,b)|a.iter().zip(b).map(|(u,v)|u+h*v).collect()).collect())}
fn rhs(h:&LieHierarchy,d:&LieData,g:&LieData,y:&Jet)->Jet{
 let p=photon_potentials(d);let q=photon_potentials(g);
 let mut z:Jet=std::array::from_fn(|_|h.zero_state());for i in 0..3{h.rhs(&p,&y[i],&mut z[i]);if i>0{let mut w=h.zero_state();h.rhs(&q,&y[i-1],&mut w);for(a,b)in z[i].iter_mut().zip(w){for(x,v)in a.iter_mut().zip(b){*x+=v;}}}}z
}
fn norm(v:&V)->f64{v.iter().flatten().map(|v|v.norm_sqr()).sum::<f64>().sqrt()}
fn diff(a:&V,b:&V)->f64{a.iter().zip(b).flat_map(|(a,b)|a.iter().zip(b)).map(|(a,b)|(a-b).norm_sqr()).sum::<f64>().sqrt()}
fn c4j_stream(t:&bianchi_rustcore::kinetic::owned_thomson::ThomsonState,lmax:usize,case:usize)->Result<(),String>{
 let h=LieHierarchy::new(lmax,true,4.)?;
 let s=bianchi_rustcore::kinetic::memory_mixture::stf_matrix(t.geometry.s);
 let mut d=LieData{shear:std::array::from_fn(|i|std::array::from_fn(|j|s[(i,j)])),..Default::default()};
 // extra generator checks: fixed Lie geometry at one slice, not evolution solutions.
 if case==1{d.n=[[0.,0.,0.],[0.,0.3,0.],[0.,0.,0.3]];}
 if case==2{d.a=[0.2,0.,0.];d.n=[[0.,0.,0.],[0.,0.25,0.],[0.,0.,-0.25]];}
 let g=LieData{shear:[[0.12,0.04,-0.03],[0.04,-0.05,0.02],[-0.03,0.02,-0.07]],..Default::default()};
 let dt=0.02;let y0=t.sky.coefficients.clone();let y:Jet=[y0.clone(),h.zero_state(),h.zero_state()];
 // bound <= 0.5 so exact native count=1 for tested +/- states.
 let bound=dt*(lmax as f64+6.)*(d.shear.iter().flatten().map(|v|v*v).sum::<f64>().sqrt()+d.n.iter().flatten().map(|v|v*v).sum::<f64>().sqrt()+d.a.iter().map(|v|v*v).sum::<f64>().sqrt()+0.01*g.shear.iter().flatten().map(|v|v*v).sum::<f64>().sqrt());assert!(bound<0.5);
 let k1=rhs(&h,&d,&g,&y);let k2=rhs(&h,&d,&g,&ax(&y,&k1,dt/2.));let k3=rhs(&h,&d,&g,&ax(&y,&k2,dt/2.));let k4=rhs(&h,&d,&g,&ax(&y,&k3,dt));
 let mut out=ax(&ax(&ax(&ax(&y,&k1,dt/6.),&k2,dt/3.),&k3,dt/3.),&k4,dt/6.);
 for w in &mut out{for v in w.iter_mut().flatten(){*v*=(-4.*dt).exp();}}
 let mut base=y0.clone();h.stream(&mut base,&d,&d,dt)?;
 assert!(diff(&base,&out[0])/norm(&base)<1e-13);
 for eps in [0.01,0.003,0.001]{
 let shift=|e:f64|{let mut p=d;for i in 0..3{for j in 0..3{p.shear[i][j]+=e*g.shear[i][j];}}p};
 let p=shift(eps);let m=shift(-eps);let mut up=y0.clone();let mut um=y0.clone();h.stream(&mut up,&p,&p,dt)?;h.stream(&mut um,&m,&m,dt)?;
 let a:V=up.iter().zip(&um).map(|(a,b)|a.iter().zip(b).map(|(x,y)|(x-y)/(2.*eps)).collect()).collect();
 let b:V=up.iter().zip(&um).zip(&base).map(|((a,b),c)|a.iter().zip(b).zip(c).map(|((x,y),z)|(x+y-2.*z)/(2.*eps*eps)).collect()).collect();
 eprintln!("C4J_STREAM,{:.17e},{case},{eps:.17e},{bound:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",t.geometry.a,diff(&base,&out[0])/norm(&base),norm(&out[1])/norm(&base),norm(&out[2])/norm(&base),diff(&a,&out[1])/norm(&out[1]),diff(&b,&out[2])/norm(&out[2]));
 }
 Ok(())
}

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
 let cut=(1./21./a0).ln();let end=(0.2/a0).ln();let mut s=m.initial(a0,vec(0))?;let mut t=0.;let mut maxg:f64=0.;let mut minscreen:f64=1.;
 println!("epoch,ell,m,Ire,Iim,Ere,Eim,Bre,Bim");eprintln!("u,a,h,S0,S1,S2,S3,S4,gauss,rho,traceP");
 for (part,nn,left,right) in [(0,n,0.,cut),(1,n/4,cut,end)]{
 for i in 0..=nn {
  let g=m.constraint(&s)?;maxg=maxg.max(g.abs());
  if i==0||i==nn{let mat=m.matter(&s)?;eprintln!("{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",t,s.geometry.a,s.geometry.h,s.geometry.s[0],s.geometry.s[1],s.geometry.s[2],s.geometry.s[3],s.geometry.s[4],g,mat.rho,mat.pressure.trace());}
  if i==nn {
   eprintln!("C4J_KIND,coframe,{part}");
   let g=nalgebra::Matrix3::new(0.12,0.04,-0.03,0.04,-0.05,0.02,-0.03,0.02,-0.07);
   m.c4j_matter_probe(&s,&g)?;
   eprintln!("C4J_KIND,rotation,{part}");
   let r=nalgebra::Matrix3::new(0.,-0.2,0.1,0.2,0.,-0.05,-0.1,0.05,0.);
   m.c4j_matter_probe(&s,&r)?;
   for case in 0..3{c4j_stream(&s,lm,case)?;}
   for p in s.sky.photons()?{let z=p.screen();let e=nalgebra::Matrix3::from_fn(|i,j|z[i][j]).symmetric_eigen().eigenvalues;let mut a=e.as_slice().to_vec();a.sort_by(f64::total_cmp);if a[0]< -1e-10{return Err("negative screen".into())}minscreen=minscreen.min(a[1]);}
   let y=&s.sky.coefficients;let norm=y[0][0].re;
   for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);let ii=y[0][k]/norm;let e=-(y[1][k]+y[2][k])*0.5/norm;let b=C64::new(0.,0.5)*(y[1][k]-y[2][k])/norm;println!("{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",ii.re,ii.im,e.re,e.im,b.re,b.im);}}break
  }
  let tar=left+(right-left)*(i+1)as f64/nn as f64;let du=tar-t;let(q,_)=m.step(&s,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;t=tar;
 }}
 eprintln!("max_gauss={maxg:.17e},min_screen={minscreen:.17e},const_err={const_err:.17e}");Ok(())
}
