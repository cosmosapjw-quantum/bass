//! Standalone Rust stdlib original source-locked stress background CSV consumer.
 //! Validates positivity, Hamiltonian, s/H, pi trace, pressure sum, q/A/eta,
 //! proper-time monotonicity, H/He density; it is NOT REI chemical solver.
use std::{env,fs::File,io::{BufRead,BufReader},collections::BTreeMap};
fn fail(s:&str)->!{eprintln!("ANISOSTRESS_CSV_REJECT:{s}");std::process::exit(3)}
fn main(){
 let args:Vec<String>=env::args().skip(1).collect();
 if args.len()!=3{fail("INPUT_CSV_SOURCE_H0_SOURCE_OMEGAR")}
 let h0=args[1].parse::<f64>().unwrap_or_else(|_|fail("SOURCE_H0_INVALID"));
 let orad=args[2].parse::<f64>().unwrap_or_else(|_|fail("SOURCE_OMEGAR_INVALID"));
 if !(h0.is_finite()&&h0>0.0&&orad.is_finite()&&orad>0.0){fail("SOURCE_COSMO_DOMAIN")}
 let mut rd=BufReader::new(File::open(&args[0]).unwrap_or_else(|_|fail("CANNOT_OPEN"))).lines();
 let header=rd.next().unwrap_or_else(||fail("EMPTY")).unwrap();
 let names:Vec<&str>=header.split(',').collect();
 let mut indices=BTreeMap::new();
 for (i,&n) in names.iter().enumerate(){indices.insert(n.to_owned(),i);}
 let get=|z:&Vec<&str>,n:&str|->f64{
  let v=*indices.get(n).unwrap_or_else(||fail("MISSING_COLUMN"));
  let f=z[v].parse::<f64>().unwrap_or_else(|_|fail("INVALID_FLOAT"));
  if !f.is_finite(){fail("NONFINITE")}f
 };
 let id_index=*indices.get("case_id").unwrap_or_else(||fail("NO_CASE"));
 let mut t_by_case=BTreeMap::<String,(usize,f64)>::new();
 let mut rows=0usize;
 for row in rd{
  let s=row.unwrap_or_else(|_|fail("READ_ERROR"));
  let cols:Vec<&str>=s.split(',').collect();
  if cols.len()!=names.len(){fail("ROW_SHAPE")}
  let q=get(&cols,"q_ref");let a=get(&cols,"a");let t=get(&cols,"t_elapsed_proper_s");
  let A=get(&cols,"A");let eta=get(&cols,"eta");
  if ![0.0,0.005,-0.005,0.01,-0.01].contains(&q){fail("Q_SOURCE_NOT_FROZEN")}
  if !(-1.0..=2.0).contains(&A)||!(0.0..=1.0).contains(&eta){fail("INVALID_VLASOV_DISTRIBUTION")}
  let H=get(&cols,"H_per_s");let hf=get(&cols,"Hflrw_per_s");
  let shear=get(&cols,"s_per_s");
  let M0=get(&cols,"radiation_M0");let Mdiff=get(&cols,"radiation_Mdelta");
  let eps=get(&cols,"aniso_epsilon_J_m3");let delta=get(&cols,"delta_Pparallel_minus_Pperp_J_m3");
  let pi1=get(&cols,"pi_perp_J_m3");let pi3=get(&cols,"pi_parallel_J_m3");
  let p1=get(&cols,"aniso_Pperp_J_m3");let p3=get(&cols,"aniso_Pparallel_J_m3");
  let nH=get(&cols,"n_H_cm3");let nHe=get(&cols,"n_He_cm3");
  let ap=get(&cols,"a_perp");let al=get(&cols,"a_parallel");
  let err=get(&cols,"Hamiltonian_residual_s2");
  if !(a>0.0&&H>0.0&&hf>0.0&&M0>0.0&&eps>=0.0&&nH>0.0&&nHe>0.0){fail("POSITIVE_SOURCE_DOMAIN")}
  if (err/(H*H)).abs()>1e-12{fail("PRECOMPUTED_HAMILTONIAN_RESIDUAL")}
  let source_d=h0*h0*orad*eta/a.powi(4);
  let inferred=hf*hf+shear*shear+source_d*(M0-1.0);
  if (H*H/inferred-1.0).abs()>2e-12{fail("NATIVE_EINSTEIN_HAMILTONIAN")}
  let expected_density=3.0*299792458.0_f64.powi(2)*source_d/(8.0*std::f64::consts::PI*6.67430e-11);
  if (eps-expected_density*M0).abs()>2e-12*eps.abs().max(1e-30){fail("STRESS_ENERGY_SOURCE_NORMALIZATION")}
  if (delta-expected_density*Mdiff).abs()>2e-12*eps.abs().max(1e-30){fail("STRESS_PRESSURE_SOURCE_NORMALIZATION")}
  if (ap*ap*al/(a*a*a)-1.0).abs()>1e-12{fail("BINARY_VOLUME_CONSTRAINT")}
  if (get(&cols,"s_over_H")-shear/H).abs()>2e-13{fail("SHEAR_VALUE")}
  if (2.0*pi1+pi3).abs()>1e-12*eps.max(1e-20){fail("PI_TRACE_NONZERO")}
  if (p3-p1-delta).abs()>1e-12*eps.max(1e-20){fail("PRESSURE_DIFF")}
  if (2.0*p1+p3-eps).abs()>1e-12*eps.max(1e-20){fail("STRESS_ENERGY_TRACE")}
  if (eta==0.0 && (eps!=0.0||pi1!=0.0||pi3!=0.0)){fail("STRESSFREE_LIMIT")}
  if !(Mdiff.is_finite()&&t>=0.0){fail("INPUT_DOMAIN")}
  let name=cols[id_index].to_owned();
  let state=t_by_case.entry(name).or_insert((0,-1.0));
  if state.0==0 && t!=0.0{fail("INCORRECT_INITIAL_PROPER_TIME")}
  if state.0>0 && t<=state.1{fail("NONMONOTONIC_CLOCK")}
  state.0+=1;state.1=t;rows+=1;
 }
 if rows!=8517||t_by_case.len()!=17||t_by_case.values().any(|x|x.0!=501){fail("CASE_COUNT")}
 println!("{{\"schema\":\"rei.axbi.initial_pi.standalone_consumer.v1\",\"rows\":{},\"cases\":{},\"n_per_case\":501,\"physical_checks\":\"PASS\",\"original_REI_production_modified\":false}}",rows,t_by_case.len());
}