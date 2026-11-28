use bianchi_rustcore::kinetic::{owned_thomson::{ThomsonOwner,C4MExternal},memory_mixture::stf_components,lie_hierarchy::LieHierarchy,spin_sht::{index,C64}};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let p=std::env::args().skip(1).collect::<Vec<_>>();assert_eq!(p.len(),8);
 let clock=std::fs::read_to_string(&p[0])?.lines().skip(1).map(|l|l.split(',').map(str::parse::<f64>).collect::<Result<Vec<_>,_>>()).collect::<Result<Vec<_>,_>>()?;
 let mut c:Vec<f64>=std::fs::read_to_string(&p[1])?.split_whitespace().map(str::parse).collect::<Result<_,_>>()?;assert_eq!(c.len(),38);
 let n:usize=p[2].parse()?;let nr:usize=p[3].parse()?;let nm:usize=p[4].parse()?;let lm:usize=p[5].parse()?;let par:f64=p[6].parse()?;let jet=p[7]=="jet";
 let scale=1.+par;for x in &mut c[3..]{*x*=scale}
 let vec=|k:usize|->[f64;5]{c[3+5*k..3+5*k+5].try_into().unwrap()};
 let spec=std::array::from_fn::<_,3,_>(|j|(c[j],1./3.,vec(1+2*j),vec(2+2*j)));
 let owner=ThomsonOwner::with_radial_species(&spec,nr,nm,2*nm,lm,lm+4,2*lm+8)?;
 let h=LieHierarchy::new(lm,true,4.)?;let a0=1./1601.;let mut ext=C4MExternal{clock,scale,a0,weight:2e-6,mass:50.};
 let w1=owner.c4k_weights(&spec,nr,nm,2*nm)?;let w2=owner.c4l_weights2(&spec,nr,nm,2*nm)?;
 let mut s=owner.initial(a0,vec(0))?;let mut d=owner.c4k_initial_d(&s,&w1)?;let mut b=owner.c4l_initial2(&s,&d,&w1,&w2)?;owner.c4m_init(&mut s,&mut d,&mut b,&w1,&w2,&ext)?;
 let g0=owner.c4m_constraint(&s,&d,&b,&w1,&w2,&ext)?;eprintln!("INIT,{:.17e},{:.17e},{:.17e}",g0[0],g0[1],g0[2]);
 let cut=(1./21./a0).ln();let end=(0.2/a0).ln();let mut t=0.;
 println!("epoch,ell,m,I0re,I0im,E0re,E0im,B0re,B0im,I1re,I1im,E1re,E1im,B1re,B1im,I2re,I2im,E2re,E2im,B2re,B2im");
 for (part,nn,l,r) in [(0,n,0.,cut),(1,n/4,cut,end)]{
  for i in 0..=nn{
   if i==nn{
    let g=if jet{owner.c4m_constraint(&s,&d,&b,&w1,&w2,&ext)?}else{[owner.constraint_external(&s,&(),&mut ext)?,0.,0.]};
    let m=owner.c4m_matter(&s,&d,&b,&w1,&w2,&ext)?;
    let inv=s.geometry.f.try_inverse().unwrap();let f1=inv*d.f;let det2=(inv*b.f).trace()-0.5*(f1*f1).trace();
    eprint!("GEOM,{part},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",s.geometry.h.ln(),d.h/s.geometry.h,b.h/s.geometry.h-0.5*(d.h/s.geometry.h).powi(2),g[0],g[1],g[2],det2,ext.continuity(&s.geometry)?,m[0].rho);
    for x in s.geometry.s{eprint!(",{x:.17e}")}for x in stf_components(d.s){eprint!(",{x:.17e}")}for x in stf_components(b.s){eprint!(",{x:.17e}")}eprintln!();
    let y=&s.sky.coefficients;let a=&d.sky;let b=&b.sky;let n=y[0][0].re;let n1=a[0][0].re;let n2=b[0][0].re;
    let val=|j:usize,k:usize|[y[j][k]/n,a[j][k]/n-y[j][k]*n1/n.powi(2),b[j][k]/n-a[j][k]*n1/n.powi(2)+y[j][k]*(n1*n1/n.powi(3)-n2/n.powi(2))];
    for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);let ii=val(0,k);let ee=val(1,k);let bb=val(2,k);print!("{part},{ll},{mm}");
     for j in 0..3{let e=-(ee[j]+bb[j])*0.5;let b=C64::new(0.,0.5)*(ee[j]-bb[j]);for v in [ii[j],e,b]{print!(",{:.17e},{:.17e}",v.re,v.im);}}println!();}}
    break
   }
   let tar=l+(r-l)*(i+1)as f64/nn as f64;let du=tar-t;
   if jet{let(q,a,b2)=owner.c4m_step(&s,&d,&b,&w1,&w2,&h,du,&ext)?;s=q;d=a;b=b2;}
   else{let(q,_,_)=owner.step_external(&s,&(),&mut ext,du)?;s=q;}
   t=tar;
  }
 }Ok(())
}
