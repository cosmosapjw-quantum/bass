//! Source-owned REI external table replay, and independent nonlinear Lie transport.
use bianchi_rustcore::{kinetic::{owned_thomson::{ThomsonOwner,ExternalMatter,ExternalContribution},owned_vlasov::OwnedState,lie_history::{RayNode,LieInitial,initial_lie_node},radiation_feedback::{advance_mixture_with_options,refresh_mixture,ExpansionEquation,LieUpdate},spin_sht::{index,C64}},geom::lie::canonical_diagonal,homogeneous_sky::field::HarmonicSky};
struct Table{rows:Vec<Vec<f64>>}
impl ExternalMatter for Table{
 type State=usize;
 fn contribution(&mut self,k:&usize,g:&OwnedState)->Result<ExternalContribution,String>{
  let r=&self.rows[*k];if (r[0]-g.a).abs()>2e-15{return Err(format!("table clock {} {}",r[0],g.a))}
  Ok(ExternalContribution{rho:r[1],pressure:[[r[2],r[5],r[6]],[r[5],r[3],r[7]],[r[6],r[7],r[4]]],ne_m3:r[8],photon_rho:r[9]})
 }
 fn advance(&mut self,k:&usize,_:&OwnedState,_:&OwnedState,end:&OwnedState)->Result<usize,String>{
  let j=(*k+1..=(*k+2).min(self.rows.len()-1)).find(|&i|(self.rows[i][0]-end.a).abs()<2e-15).ok_or("table advance clock")?;Ok(j)
 }
}
fn replay(path:&str)->Result<(),Box<dyn std::error::Error>>{
 let rows=std::fs::read_to_string(path)?.lines().map(|l|l.split(',').map(str::parse::<f64>).collect::<Result<Vec<_>,_>>()).collect::<Result<Vec<_>,_>>()?;
 let mut t=Table{rows};assert_eq!(t.rows.len(),9);let owner=ThomsonOwner::new(0.03,32,8,16,4,8,16)?;
 let mut s=owner.initial(1./21.,[0.01,0.,0.,0.,0.0075])?;let mut k=0;
 println!("a,h,S0,S1,S2,S3,S4,F00,F01,F02,F10,F11,F12,F20,F21,F22,gauss,I2,E2,B3");
 for i in 0..=4{
  let g=&s.geometry;let gauss=owner.constraint_external(&s,&k,&mut t)?;
  let a=&s.sky.coefficients;let norm=a[0][0].re;
  let norm_l=|l:usize,j:usize|{(-(l as i64)..=l as i64).map(|m|{let k=index(l,m);let v=match j{0=>a[0][k],1=>-(a[1][k]+a[2][k])*0.5,_=>C64::new(0.,0.5)*(a[1][k]-a[2][k])};v.norm_sqr()/norm.powi(2)}).sum::<f64>().sqrt()};
  print!("{:.17e},{:.17e}",g.a,g.h);for v in g.s{print!(",{v:.17e}")}for j in 0..3{for l in 0..3{print!(",{:.17e}",g.f[(j,l)])}}
  println!(",{gauss:.17e},{:.17e},{:.17e},{:.17e}",norm_l(2,0),norm_l(2,1),norm_l(3,2));
  if i==4{break}let du=t.rows[k][10];let (next,j,_)=owner.step_external(&s,&k,&mut t,du)?;assert_eq!(j,k+2);s=next;k=j;
 }Ok(())
}
fn mag(v:[f64;3])->f64{v.iter().map(|v|v*v).sum::<f64>().sqrt()}
fn fixed(s:&HarmonicSky,g:&RayNode,dt:f64)->Result<HarmonicSky,String>{let mut z=s.clone();let mut r=g.clone();r.eta+=dt;z.stream(g,&r)?;Ok(z)}
fn lie()->Result<(),Box<dyn std::error::Error>>{
 println!("family,steps,initial_codazzi,max_codazzi,max_gauss,max_jacobi,h,omega,S_norm,B3,E2,energy,seconds");
 for family in ["I","II","III","IV","V","VI0","VIstar","VII0","VIh:-0.25","VIIh:0.25","VIII","IX"]{
  for steps in [64,128,256]{
   let tm=std::time::Instant::now();let(n,a)=canonical_diagonal(family)?;let sc=0.1;let n=std::array::from_fn(|i|std::array::from_fn(|j|if i==j{sc*n[i]}else{0.}));
   let mut g=initial_lie_node(&LieInitial{shear:[[0.02,0.,0.],[0.,-0.012,0.],[0.,0.,-0.008]],n,a:[sc*a,0.,0.]})?;
   let mut y=HarmonicSky::isotropic(6,10,16,true)?;y.coefficients[1][index(2,0)]=C64::new(-0.003,0.);y.coefficients[2][index(2,0)]=C64::new(-0.003,0.);
   let scale=g.omega_radiation/y.moments()?.energy;
   let initial_cod=mag(g.codazzi_residual);let(mut cod,mut gauss,mut jac)=(initial_cod,g.gauss_residual.abs(),mag(g.jacobi_residual));let du=0.2/steps as f64;
   for _ in 0..steps{
    let m=y.moments()?;let omega=scale*m.energy/g.hubble_ratio.powi(2);
    let mut mid=advance_mixture_with_options(&g,&g,du/2.,omega,m.pressure,m.flux,ExpansionEquation::Raychaudhuri,LieUpdate::Congruence)?;
    let ym=fixed(&y,&g,du/2.)?;let mm=ym.moments()?;let om=scale*mm.energy/mid.hubble_ratio.powi(2);mid.omega_radiation=om;refresh_mixture(&mut mid,om,mm.flux)?;
    let mut end=advance_mixture_with_options(&g,&mid,du,om,mm.pressure,mm.flux,ExpansionEquation::Raychaudhuri,LieUpdate::Congruence)?;
    y=fixed(&y,&mid,du)?;let m=y.moments()?;let om=scale*m.energy/end.hubble_ratio.powi(2);end.omega_radiation=om;refresh_mixture(&mut end,om,m.flux)?;
    cod=cod.max(mag(end.codazzi_residual));gauss=gauss.max(end.gauss_residual.abs());jac=jac.max(mag(end.jacobi_residual));g=end;
   }
   let z=&y.coefficients;let norm=z[0][0].re;
   let b=(-3..=3).map(|m|{let k=index(3,m);(z[1][k]-z[2][k]).norm_sqr()/4.}).sum::<f64>().sqrt()/norm;
   let e=(-2..=2).map(|m|{let k=index(2,m);(z[1][k]+z[2][k]).norm_sqr()/4.}).sum::<f64>().sqrt()/norm;
   let s=g.shear.iter().flatten().map(|v|v*v).sum::<f64>().sqrt();
   println!("{family},{steps},{initial_cod:.17e},{cod:.17e},{gauss:.17e},{jac:.17e},{:.17e},{:.17e},{s:.17e},{b:.17e},{e:.17e},{:.17e},{:.6}",g.hubble_ratio,g.omega_radiation,y.moments()?.energy,tm.elapsed().as_secs_f64());
  }
 }Ok(())
}
fn main()->Result<(),Box<dyn std::error::Error>>{let p=std::env::args().nth(1).ok_or("table path or lie")?;if p=="lie"{lie()}else{replay(&p)}}
