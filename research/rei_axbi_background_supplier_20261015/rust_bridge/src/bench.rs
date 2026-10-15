use rei_microphysics::axbi_background::{AxbiBackground,BackgroundFamily,Cosmology};
use std::time::Instant;
fn fail() -> ! {panic!("MISSING_PHYSICAL_COSMO_INPUT")}
fn main() {
 let arg:Vec<String>=std::env::args().skip(1).collect();
 if arg.len()!=7{fail();}
 let f=|i:usize| ->f64{arg[i].parse().unwrap_or_else(|_|fail())};
 let h0=f(0);let om=f(1);let or=f(2);let ol=f(3);let a0=f(4);let ae=f(5);
 let panels:usize=arg[6].parse().unwrap_or_else(|_|fail());
 let c=Cosmology{h0_per_s:h0,omega_m:om,omega_r:or,omega_lambda:ol};
 let cs=[(0.0,BackgroundFamily::PhysicalDensityFixed),(0.005,BackgroundFamily::PhysicalDensityFixed),
 (-0.005,BackgroundFamily::PhysicalDensityFixed),(0.01,BackgroundFamily::PhysicalDensityFixed),
 (-0.01,BackgroundFamily::PhysicalDensityFixed),(0.01,BackgroundFamily::SameHDiagnostic)];
 let bg:Vec<_>=cs.iter().map(|(q,f)|AxbiBackground::new(c,a0,ae,0.0,*q,*f,panels).unwrap()).collect();
 let logspan=(ae/a0).ln();
 let aa:Vec<_>=(0..501).map(|i|if i==0 {a0}else if i==500{ae}else{a0*(logspan*i as f64/500.0).exp()}).collect();
 let mut elapsed=Vec::<f64>::new();
 let mut sums=Vec::<f64>::new();
 for _ in 0..3 {
  let t=Instant::now();
  let mut checksum=0.0;
  for b in &bg {for a in &aa {
   let p=b.point_at_scale(*a).unwrap();
   checksum+=p.time_s*1e-16+p.b+p.h_per_s*1e15;
  }}
  elapsed.push(t.elapsed().as_secs_f64());sums.push(checksum);
 }
 elapsed.sort_by(|a,b|a.partial_cmp(b).unwrap());
 assert!(sums.iter().all(|x|*x==sums[0]));
 println!("{{\"schema\":\"real_rei_owner_axbi_simpson_4096_benchmark\",\"n_cases\":6,\"n_points_per_case\":501,\"source_impl\":\"original AxbiBackground.point_at_scale\",\"median_wall_s\":{:.17e},\"samples_wall_s\":[{:.17e},{:.17e},{:.17e}],\"checksum\":{:.17e}}}",
 elapsed[1],elapsed[0],elapsed[1],elapsed[2],sums[0]);
}
