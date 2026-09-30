use bianchi_rustcore::microphysics::population::FrozenPopulation;
use bianchi_rustcore::kinetic::realizability::{check_moments,MomentKind};
fn main(){
 let g=FrozenPopulation::new(&[2.0,1.0],&[vec![0.0,3.0],vec![1.0,0.0]]).unwrap();
 println!("mu,m,weighted_l1_error,reported_bound,inventory_error");
 for mu in [1e-18_f64,1e-6,0.1,1.0,16.0,64.0]{for m in [0,1,8,64,128,1024]{
 let a=g.advance(&[0.5,0.0],mu/3.0,m).unwrap();
 let w1=0.25*-(-4.0*mu/3.0).exp_m1();
 let err=(2.0*a.populations[0]-(1.0-w1)).abs()+(a.populations[1]-w1).abs();
 let inv=(2.0*a.populations[0]+a.populations[1]-1.0).abs();
 assert!(a.populations.iter().all(|x|x.is_finite()&&*x>=0.0));assert!(inv<5e-13);
 assert!(err<=a.weighted_l1_error_bound+5e-13);
 println!("{mu:.17e},{m},{err:.17e},{:.17e},{inv:.17e}",a.weighted_l1_error_bound);
 }}
 let mut count=0;
 for seed in 1..=32{let mut rho=0.0;let mut q=[0.0;3];let mut s=[[0.0;3];3];
 for k in 0..9{let a=(seed*17+k*7) as f64;let v=[a.sin()*0.5,a.cos()*0.5,0.25];let w=(k+1) as f64/10.0;rho+=w;for i in 0..3{q[i]+=w*v[i];for j in 0..3{s[i][j]+=w*v[i]*v[j];}}}
 for scale in [1e-300,1.0,1e300]{let mut qs=q;let mut ss=s;for i in 0..3{qs[i]*=scale;for j in 0..3{ss[i][j]*=scale;}}assert!(check_moments(rho*scale,qs,ss,MomentKind::MassiveOrMixed,1e-12).unwrap().admissible);count+=1;}
 }
 eprintln!("moment_particle_scale_cases={count}");
}
