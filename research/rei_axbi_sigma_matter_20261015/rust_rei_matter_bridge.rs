//! Explicit REI-native ABI adapter for BASS Σ + radiation/massive-Vlasov
//! background table. Does NOT inject kinetic sources into existing REI driver.
//! Validates the ORIGINAL REI BackgroundPoint/GeometrySnapshot using unchanged
//! Rust microphysics crate + independent Hamiltonian source and tensor identities.
use rei_microphysics::axbi_background::{AxbiBackground,BackgroundFamily,BackgroundPoint,Cosmology};
use std::{env,fs::File,io::{BufRead,BufReader},collections::BTreeMap};
fn fail(msg:&str)->!{eprintln!("AXBI_SIGMA_MASSIVE_REJECT:{msg}");std::process::exit(3)}
fn value(cols:&[&str],names:&[String],name:&str)->f64{
 let idx=names.iter().position(|n|n==name).unwrap_or_else(||fail("MISSING_FIELD"));
 let a=cols[idx].parse::<f64>().unwrap_or_else(|_|fail("INVALID_NUMBER"));
 if !a.is_finite(){fail("NONFINITE")}a
}
fn main(){
 let args:Vec<_>=env::args().skip(1).collect();
 if args.len()!=7{fail("ARGS_CSV_H0_OM_OR_OL_AREF_AEND")}
 let float=|i:usize|->f64{args[i].parse().unwrap_or_else(|_|fail("PARAM_PARSE"))};
 let h0=float(1);let om=float(2);let orad=float(3);let ol=float(4);
 let ar=float(5);let ae=float(6);
 let c=Cosmology{h0_per_s:h0,omega_m:om,omega_r:orad,omega_lambda:ol};
 let original=AxbiBackground::new(c,ar,ae,0.,0.01,BackgroundFamily::PhysicalDensityFixed,4096).unwrap();
 let file=BufReader::new(File::open(&args[0]).unwrap_or_else(|_|fail("CSV_READ")));
 let mut lines=file.lines();
 let header=lines.next().unwrap_or_else(||fail("NO_HEADER")).unwrap();
 let keys:Vec<String>=header.split(',').map(str::to_owned).collect();
 let mut rows=0usize;
 let mut cases=BTreeMap::<String,(usize,f64)>::new();
 let mut max_baseline_b=0.0_f64;
 let mut max_baseline_h=0.0_f64;
 let mut original_pass=0usize;
 const G:f64=6.67430e-11;
 const LIGHT:f64=299792458.0;
 let convert=(8.0*std::f64::consts::PI*G)/(3.0*LIGHT*LIGHT);
 for line in lines{
  let line=line.unwrap_or_else(|_|fail("READ_DATA"));
  let cols:Vec<&str>=line.split(',').collect();
  if cols.len()!=keys.len(){fail("FIELD_COUNT")}
  let v=|k:&str|value(&cols,&keys,k);
  let id=cols[keys.iter().position(|n|n=="case_id").unwrap_or_else(||fail("CASE_ID"))].to_owned();
  let a=v("a");let b=v("b");let t=v("proper_elapsed_s");
  let s=v("s_per_s");let h=v("H_mean_per_s");let sig=v("Sigma");
  let sign=v("shear_orientation");let sig0=v("Sigma_ref");
  let fr=v("radiation_fraction");let fm=v("massive_matter_fraction");
  let Hfid=v("H_FLRW_ref_per_s");
  let rad=v("radiation_kinetic_energy_J_m3");
  let mat=v("matter_kinetic_energy_J_m3");
  let pir=v("Pi_r_J_m3");let pim=v("Pi_m_J_m3");
  let rho_bg=h0*h0*(om*(1.-fm)/a.powi(3)+orad*(1.-fr)/a.powi(4)+ol);
  let h_pred=(rho_bg+convert*(rad+mat)+s*s).sqrt();
  if !(h>0.&&a>=ar&&a<=ae&&t>=0.0&&sig>=0.&&sig0>=0.&&sign.abs()==1.&&
        (h_pred/h-1.).abs()<8e-13){fail("EINSTEIN_HAMILTONIAN")}
  if (sig-(3.0_f64).sqrt()*s.abs()/h).abs()>5e-14{fail("SIGMA_NORMALIZATION")}
  if (v("pi_m_perp_J_m3")+pim).abs()>1e-20 ||
     (v("pi_m_parallel_J_m3")-2.*pim).abs()>1e-20 ||
     (v("pi_r_perp_J_m3")+pir).abs()>1e-20 ||
     (v("pi_r_parallel_J_m3")-2.*pir).abs()>1e-20{fail("KINETIC_STRESS_TRACE")}
  if (v("Pi_total_J_m3")-pir-pim).abs()>1e-19{fail("TOTAL_PI_IDENTITY")}
  if (v("a_perp")*v("a_perp")*v("a_parallel")/a.powi(3)-1.).abs()>1e-12{
     fail("VOLUME_TRACE")
  }
  let bg=BackgroundPoint{
    a,b,time_s:t,h_flrw_per_s:Hfid,h_per_s:h,s_per_s:s,sigma:s/h
  };
  if bg.geometry().is_err(){fail("ORIGINAL_REI_GEOMETRY_REJECT")}
  let e=cases.entry(id.clone()).or_insert((0,-1.0));
  if e.0==0 && (t!=0.||b!=0.){fail("INITIAL_TIME_B")}
  if e.0>0&&t<=e.1{fail("NONMONOTONIC_SI_CLOCK")}
  e.0+=1;e.1=t;
  let row=v("row") as usize;
  if id=="SHEAR_PLUS_SIGMA"&&row%125==0{
   let orig=original.point_at_scale(a).unwrap();
   let ed=(orig.b-b).abs();
   let hd=(orig.h_per_s/h-1.).abs();
   max_baseline_b=max_baseline_b.max(ed);
   max_baseline_h=max_baseline_h.max(hd);
   if ed>3e-12||hd>3e-13{fail("AX03_SOURCE_PARITY_FAIL")}
   original_pass+=1;
  }
  rows+=1;
 }
 if rows!=7014||cases.len()!=14||!cases.values().all(|(n,_)|*n==501)||original_pass!=5{
  fail("INCOMPLETE_CASE_TABLE");
 }
 println!("{{\"schema\":\"rei.axbi.sigma_matter_original_crate_bridge.v1\",\"rows\":{},\"cases\":{},\"original_Rust_AX03_parity_samples\":{},\"max_original_b_abs_diff\":{:.17e},\"max_original_H_relative_diff\":{:.17e},\"science_claim\":\"READ_ONLY_BACKGROUND_SUPPLIER_NOT_NATIVE_CHEMISTRY\"}}",
 rows,cases.len(),original_pass,max_baseline_b,max_baseline_h);
}