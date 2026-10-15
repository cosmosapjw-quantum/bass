//! REI source ABI bridge: read/validate supplied physical Bianchi-I stress table
//! and instantiate original public rei_microphysics::axbi_background::BackgroundPoint.
 //! Source-locked snapshot; no production Driver or full H/He source change.
use rei_microphysics::axbi_background::{BackgroundPoint,AxbiBackground,BackgroundFamily,Cosmology};
use std::{env,fs::File,io::{BufRead,BufReader}};
fn invalid(s:&str)->!{eprintln!("AXBI_PI_BRIDGE_REJECT:{s}");std::process::exit(3)}
fn value(z:&[&str],keys:&[String],n:&str)->f64{
 let k=keys.iter().position(|s|s==n).unwrap_or_else(||invalid("MISSING_COLUMN"));
 let v=z[k].parse::<f64>().unwrap_or_else(|_|invalid("BAD_INPUT_NUMBER"));
 if !v.is_finite(){invalid("NONFINITE")}v
}
fn main(){
 let a:Vec<String>=env::args().skip(1).collect();
 if a.len()!=7{invalid("ARGS_CSV_H0_OM_OR_OL_AR_AEND")}
 let float=|i:usize|->f64{a[i].parse().unwrap_or_else(|_|invalid("SOURCE_PARAM_PARSE"))};
 let c=Cosmology{h0_per_s:float(1),omega_m:float(2),omega_r:float(3),omega_lambda:float(4)};
 let ar=float(5);let ae=float(6);
 let base=AxbiBackground::new(c,ar,ae,0.0,0.01,BackgroundFamily::PhysicalDensityFixed,4096).unwrap();
 let read=BufReader::new(File::open(&a[0]).unwrap_or_else(|_|invalid("CSV_OPEN")));
 let mut lines=read.lines();
 let first=lines.next().unwrap_or_else(||invalid("HEADER")).unwrap();
 let names:Vec<String>=first.split(',').map(str::to_owned).collect();
 let mut rows=0_usize;let mut geometry_count=0_usize;let mut original_stressfree_compared=0_usize;
 let mut max_b=0_f64;let mut max_H=0_f64;
 for line in lines{
  let text=line.unwrap_or_else(|_|invalid("READ"));
  let cols:Vec<&str>=text.split(',').collect();
  if cols.len()!=names.len(){invalid("ROW_FIELDS")}
  let get=|key:&str| value(&cols,&names,key);
  let z=BackgroundPoint{
   a:get("a"),b:get("b"),
   time_s:get("t_elapsed_proper_s"),
   h_flrw_per_s:get("Hflrw_per_s"),
   h_per_s:get("H_per_s"),
   s_per_s:get("s_per_s"),
   sigma:get("s_over_H")
  };
  if z.geometry().is_err(){invalid("PHYSICAL_REI_BACKGROUNDPOINT_GEOMETRY")}
  rows+=1;geometry_count+=1;
  let q=get("q_ref");let A=get("A");let eta=get("eta");
  let i=get("row") as usize;
  if q==0.01 && A==0.0 && eta==0.0 && i%125==0{
   let previous=base.point_at_scale(z.a).unwrap();
   let bd=(previous.b-z.b).abs();
   let Hd=(previous.h_per_s/z.h_per_s-1.0).abs();
   max_b=max_b.max(bd);max_H=max_H.max(Hd);
   if bd>2e-12||Hd>2e-13{invalid("ORIGINAL_SOURCE_STRESSFREE_PARITY")}
   original_stressfree_compared+=1;
  }
 }
 if rows!=8517||original_stressfree_compared!=5{invalid("INCOMPLETE_ABI_BRIDGE")}
 println!("{{\"schema\":\"rei.axbi.initial_pi.native_backgroundpoint_interface.v1\",\"rows\":{},\"reconstructed_original_geometry\":{},\"original_stressfree_Rust_samples\":{},\"max_b_abs\":{:.17e},\"max_H_rel\":{:.17e},\"compiled_with_original_rei_microphysics\":true,\"production_driver_replaced\":false}}",
  rows,geometry_count,original_stressfree_compared,max_b,max_H);
}
