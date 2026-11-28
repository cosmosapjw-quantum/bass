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
 let jet2=std::env::var_os("C4L_JET2").is_some();let tangent=jet2||std::env::var_os("C4K_TANGENT").is_some();
 let hierarchy=bianchi_rustcore::kinetic::lie_hierarchy::LieHierarchy::new(lm,true,4.)?;
 let dw=m.c4k_weights(&spec,nr,nm,2*nm)?;
 let w2=m.c4l_weights2(&spec,nr,nm,2*nm)?;
 let cut=(1./21./a0).ln();let end=(0.2/a0).ln();let mut s=m.initial(a0,vec(0))?;let mut d=m.c4k_initial_d(&s,&dw)?;let mut b=m.c4l_initial2(&s,&d,&dw,&w2)?;if jet2{eprintln!("C4L_INIT,{:.17e}",m.c4l_constraint2(&s,&d,&b,&dw,&w2)?);}let mut t=0.;if tangent{eprintln!("C4K_INIT,{:.17e}",m.c4k_constraint_d(&s,&d,&dw)?);}let mut maxg:f64=0.;let mut minscreen:f64=1.;
 println!("epoch,ell,m,Ire,Iim,Ere,Eim,Bre,Bim");eprintln!("u,a,h,S0,S1,S2,S3,S4,gauss,rho,traceP");
 for (part,nn,left,right) in [(0,n,0.,cut),(1,n/4,cut,end)]{
 for i in 0..=nn {
  let g=m.constraint(&s)?;maxg=maxg.max(g.abs());
  if i==0||i==nn{let mat=m.matter(&s)?;eprintln!("{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",t,s.geometry.a,s.geometry.h,s.geometry.s[0],s.geometry.s[1],s.geometry.s[2],s.geometry.s[3],s.geometry.s[4],g,mat.rho,mat.pressure.trace());}
  if i==nn {
   if jet2 {
    use bianchi_rustcore::kinetic::memory_mixture::stf_components;
    let mat=m.matter(&s)?;let m2=m.c4l_matter2(&s,&d,&b,&dw,&w2)?;let inv=s.geometry.f.try_inverse().unwrap();let a=inv*d.f;let det=(inv*b.f).trace()-0.5*(a*a).trace();
    eprint!("C4L_GEOM,{part},{:.17e},{:.17e},{:.17e},{:.17e}",b.h/s.geometry.h-0.5*(d.h/s.geometry.h).powi(2),m.c4l_constraint2(&s,&d,&b,&dw,&w2)?,det,m2.rho/mat.rho);
    for v in stf_components(b.s){eprint!(",{v:.17e}");}for v in b.f.iter(){eprint!(",{v:.17e}");}eprintln!();
    let y=&s.sky.coefficients;let d1=&d.sky;let d2=&b.sky;let n=y[0][0].re;let n1=d1[0][0].re;let n2=d2[0][0].re;
    let norm=|j:usize,k:usize|d2[j][k]/n-d1[j][k]*(n1/n.powi(2))+y[j][k]*(n1*n1/n.powi(3)-n2/n.powi(2));
    for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);let ii=norm(0,k);let ee=-(norm(1,k)+norm(2,k))*0.5;let bb=C64::new(0.,0.5)*(norm(1,k)-norm(2,k));eprintln!("C4L_SKY,{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",ii.re,ii.im,ee.re,ee.im,bb.re,bb.im);}}
   }
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
   for p in s.sky.photons()?{let z=p.screen();let e=nalgebra::Matrix3::from_fn(|i,j|z[i][j]).symmetric_eigen().eigenvalues;let mut a=e.as_slice().to_vec();a.sort_by(f64::total_cmp);if a[0]< -1e-10{return Err("negative screen".into())}minscreen=minscreen.min(a[1]);}
   let y=&s.sky.coefficients;let norm=y[0][0].re;
   for ll in 0..=lm{for mm in -(ll as i64)..=ll as i64{let k=index(ll,mm);let ii=y[0][k]/norm;let e=-(y[1][k]+y[2][k])*0.5/norm;let b=C64::new(0.,0.5)*(y[1][k]-y[2][k])/norm;println!("{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",ii.re,ii.im,e.re,e.im,b.re,b.im);}}break
  }
  let tar=left+(right-left)*(i+1)as f64/nn as f64;let du=tar-t;if jet2{let(q,nd,nb)=m.c4l_step(&s,&d,&b,&dw,&w2,&hierarchy,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;d=nd;b=nb;}else if tangent{let (q,nd)=m.c4k_step(&s,&d,&dw,&hierarchy,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;d=nd;}else{let(q,_)=m.step(&s,du,interp(&clock,t),interp(&clock,t+du/2.))?;s=q;}t=tar;
 }}
 eprintln!("max_gauss={maxg:.17e},min_screen={minscreen:.17e},const_err={const_err:.17e}");Ok(())
}
