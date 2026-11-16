pub use rei_microphysics::{AxisymmetricPoint,ForwardError,GeometryBackground,GeometrySnapshot};
#[path="../src/bass_ax11_reference_background.rs"]
mod raw;
use rei_microphysics::axbi_background as new;
fn cosine()->new::Cosmology{new::Cosmology{h0_per_s:67.4*1e5/3.0856775814913673e24,omega_m:0.315,omega_r:9.2e-5,omega_lambda:1.-0.315-9.2e-5}}
fn pair(q:f64,same:bool)->(new::AxbiBackground,raw::AxbiBackground){
 let c=cosine();let a=1.0/21.0;
 let n=new::AxbiBackground::new(c,a,0.2,0.,q,if same{new::BackgroundFamily::SameHDiagnostic}else{new::BackgroundFamily::PhysicalDensityFixed},4096).unwrap();
 let r=raw::AxbiBackground::new(raw::Cosmology{h0_per_s:c.h0_per_s,omega_m:c.omega_m,omega_r:c.omega_r,omega_lambda:c.omega_lambda},a,0.2,0.,q,if same{raw::BackgroundFamily::SameHDiagnostic}else{raw::BackgroundFamily::PhysicalDensityFixed},4096).unwrap();
 n.configure_exact_reuse(true).unwrap();(n,r)
}
fn nb(p:new::BackgroundPoint)->Vec<u64>{[p.a,p.b,p.time_s,p.h_flrw_per_s,p.h_per_s,p.s_per_s,p.sigma].map(f64::to_bits).to_vec()}
fn rb(p:raw::BackgroundPoint)->Vec<u64>{[p.a,p.b,p.time_s,p.h_flrw_per_s,p.h_per_s,p.s_per_s,p.sigma].map(f64::to_bits).to_vec()}
#[test]fn all_physical_components_bit_exact_at_original_4097_nodes(){
 for q in [0.,0.005,-0.005,0.01,-0.01]{let(n,r)=pair(q,false);for a in [1.0/21.0,0.048,0.08873654701704167,0.10752752205956843,0.2]{let b=rb(r.point_at_scale(a).unwrap());assert_eq!(nb(n.point_at_scale(a).unwrap()),b);assert_eq!(nb(n.point_at_scale(a).unwrap()),b);}}
}
#[test]fn reference_first_evaluates_then_survives_ring_eviction(){
 let(n,r)=pair(0.01,false);let a=1.0/21.;assert_eq!(nb(n.point_at_scale(a).unwrap()),rb(r.point_at_scale(a).unwrap()));assert_eq!(n.exact_reuse_profile().unwrap().misses,1);
 for i in 0..40{n.point_at_scale(0.05+i as f64*0.003).unwrap();}
 let before=n.exact_reuse_profile().unwrap();n.point_at_scale(a).unwrap();let after=n.exact_reuse_profile().unwrap();assert_eq!(after.misses,before.misses);assert_eq!(after.reference_hits,1);
}
#[test]fn adjacent_float_is_a_miss_not_approximate_key(){
 let(n,r)=pair(0.01,false);let a=0.1_f64;let b=f64::from_bits(a.to_bits()+1);n.point_at_scale(a).unwrap();assert_eq!(nb(n.point_at_scale(b).unwrap()),rb(r.point_at_scale(b).unwrap()));assert_eq!(n.exact_reuse_profile().unwrap().misses,2);
}
#[test]fn no_cross_model_or_same_h_cache_alias(){
 let(p,rp)=pair(0.01,false);let(m,rm)=pair(-0.01,false);let(s,rs)=pair(0.01,true);
 for _ in 0..3{assert_eq!(nb(p.point_at_scale(0.1).unwrap()),rb(rp.point_at_scale(0.1).unwrap()));assert_eq!(nb(m.point_at_scale(0.1).unwrap()),rb(rm.point_at_scale(0.1).unwrap()));assert_eq!(nb(s.point_at_scale(0.1).unwrap()),rb(rs.point_at_scale(0.1).unwrap()));}
 assert_ne!(p.point_at_scale(0.1).unwrap().b.to_bits(),m.point_at_scale(0.1).unwrap().b.to_bits());assert_ne!(p.point_at_scale(0.1).unwrap().h_per_s.to_bits(),s.point_at_scale(0.1).unwrap().h_per_s.to_bits());
}
#[test]fn invalid_inputs_keep_original_failure_and_are_not_cached(){
 let(n,r)=pair(0.01,false);for a in [f64::NAN,f64::INFINITY,-0.,0.,-1.,0.04,0.21]{assert_eq!(format!("{:?}",n.point_at_scale(a).unwrap_err()),format!("{:?}",r.point_at_scale(a).unwrap_err()));}assert_eq!(n.exact_reuse_profile().unwrap().calls,0);
}
#[test]fn opt_out_preserves_original_and_every_call_recomputes(){
 let(n,r)=pair(0.01,false);n.configure_exact_reuse(false).unwrap();for _ in 0..3{assert_eq!(nb(n.point_at_scale(0.1).unwrap()),rb(r.point_at_scale(0.1).unwrap()));}let p=n.exact_reuse_profile().unwrap();assert_eq!((p.calls,p.misses,p.hits),(3,3,0));
}
#[test]fn thread_traits_and_clone_preserve_model_ownership(){
 fn check<T:Send+Sync>(){}check::<new::AxbiBackground>();let(n,r)=pair(0.01,false);let c=n.clone();n.point_at_scale(0.1).unwrap();assert_eq!(nb(c.point_at_scale(0.1).unwrap()),rb(r.point_at_scale(0.1).unwrap()));assert_eq!(c.exact_reuse_profile().unwrap().hits,1);
}
