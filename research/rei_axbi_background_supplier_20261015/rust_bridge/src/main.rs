//! Read-only physical Rust source parity: actual rei_microphysics::AxbiBackground.
//! Inputs CLI [H0 Om Or Ol a_ref a_end panels] are supplied from pinned JSON.
//! This program creates no gas or ionization history and writes no owner file.
use rei_microphysics::axbi_background::{AxbiBackground,BackgroundFamily,Cosmology};
fn fail() -> ! {panic!("REI_CROSSCHECK_ARGS_INVALID")}
fn main() {
 let arg: Vec<String> = std::env::args().skip(1).collect();
 if arg.len()!=7 {fail();}
 let f=|i:usize| -> f64 {arg[i].parse::<f64>().unwrap_or_else(|_|fail())};
 let (h0,om,or,ol,a0,aend)=(f(0),f(1),f(2),f(3),f(4),f(5));
 let panels:usize=arg[6].parse().unwrap_or_else(|_|fail());
 let cos=Cosmology{h0_per_s:h0,omega_m:om,omega_r:or,omega_lambda:ol};
 let mut cases:Vec<(f64,BackgroundFamily,&str)>=vec![
  (0.0,BackgroundFamily::PhysicalDensityFixed,"PhysicalDensityFixed"),
  (0.005,BackgroundFamily::PhysicalDensityFixed,"PhysicalDensityFixed"),
  (-0.005,BackgroundFamily::PhysicalDensityFixed,"PhysicalDensityFixed"),
  (0.01,BackgroundFamily::PhysicalDensityFixed,"PhysicalDensityFixed"),
  (-0.01,BackgroundFamily::PhysicalDensityFixed,"PhysicalDensityFixed"),
  (0.01,BackgroundFamily::SameHDiagnostic,"SameHDiagnostic")];
 println!("family,q,fraction,a,t_s,b,H_flrw,H_mean,s,sigma,a_perp,a_parallel,H_perp,H_parallel");
 for (q,fam,name) in cases.drain(..) {
  let bg=AxbiBackground::new(cos,a0,aend,0.,q,fam,panels).unwrap();
  for i in 0..=4 {
   let alpha=i as f64/4.0;
   let a=if i==0 {a0} else if i==4 {aend} else {a0*((aend/a0).ln()*alpha).exp()};
   let p=bg.point_at_scale(a).unwrap();
   let g=p.geometry().unwrap();
   println!("{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
     name,q,alpha,a,p.time_s,p.b,p.h_flrw_per_s,p.h_per_s,p.s_per_s,p.sigma,
     g.scale_factors[0],g.scale_factors[2],g.hubble_per_s[0],g.hubble_per_s[2]);
  }
 }
}
