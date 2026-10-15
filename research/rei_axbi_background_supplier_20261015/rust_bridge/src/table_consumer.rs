//! Native portable REI-side streaming check for SOURCE-LOCKED AX03_BACKGROUND.csv.
//! Rust stdlib only. No atmosphere/solver invocation or mutation.
use std::{env,fs::File,io::{BufRead,BufReader}};
fn abort(msg:&str)->!{eprintln!("REI_AXBI_TABLE_REJECT:{}",msg);std::process::exit(3)}
fn val(row:&[&str],names:&[String],key:&str)->f64 {
 let index=names.iter().position(|v|v==key).unwrap_or_else(||abort("MISSING_FIELD"));
 let x=row[index].parse::<f64>().unwrap_or_else(|_|abort("NOT_FINITE_NUMBER"));
 if !x.is_finite(){abort("NONFINITE_SAMPLE");}x
}
fn main() {
 let args:Vec<_>=env::args().skip(1).collect();
 if args.len()!=1{abort("EXPECTED_ONE_CSV_PATH");}
 let file=File::open(&args[0]).unwrap_or_else(|_|abort("CANNOT_OPEN"));
 let mut lines=BufReader::new(file).lines();
 let first=lines.next().unwrap_or_else(||abort("NO_HEADER")).unwrap();
 let fields:Vec<String>=first.split(',').map(str::to_owned).collect();
 let mut rows=0usize; let mut bycase=std::collections::BTreeMap::<String,(usize,f64)>::new();
 let mut checksum=0.0f64;
 for line in lines {
  let l=line.unwrap_or_else(|_|abort("READ_FAILURE"));
  let cols:Vec<&str>=l.split(',').collect();
  if cols.len()!=fields.len(){abort("CSV_FIELD_COUNT");}
  let fam_idx=fields.iter().position(|v|v=="family").unwrap_or_else(||abort("NO_FAMILY"));
  let fam=cols[fam_idx];
  if fam!="PhysicalDensityFixed" && fam!="SameHDiagnostic"{abort("WRONG_FAMILY");}
  let q=val(&cols,&fields,"q_ref");
  if ![0.0,0.005,-0.005,0.01,-0.01].contains(&q){abort("UNKNOWN_SIGNED_Q");}
  if fam=="SameHDiagnostic"&&q!=0.01{abort("SAME_H_WRONG_CASE");}
  let a=val(&cols,&fields,"a");
  let t=val(&cols,&fields,"proper_elapsed_s");
  let b=val(&cols,&fields,"b");
  let hf=val(&cols,&fields,"H_flrw_per_s");
  let h=val(&cols,&fields,"H_mean_per_s");
  let s=val(&cols,&fields,"shear_s_per_s");
  let ap=val(&cols,&fields,"a_perp");
  let al=val(&cols,&fields,"a_parallel");
  let nh=val(&cols,&fields,"n_H_cm3");
  let nhe=val(&cols,&fields,"n_He_cm3");
  let temp=val(&cols,&fields,"Tbar_CMB_K");
  let sig=val(&cols,&fields,"sigma_s_over_H");
  let vol=ap*ap*al;
  if !(a>0.0&&h>0.0&&hf>0.0&&nh>0.0&&nhe>0.0&&temp>0.0)
    {abort("POSITIVE_PHYSICAL_DOMAIN");}
  if ((vol/(a*a*a))-1.0).abs()>1e-12{abort("GEOMETRY_VOLUME_INVALID");}
  let expected=if fam=="SameHDiagnostic"{hf}else{hf.hypot(s)};
  if (expected/h-1.0).abs()>2e-13{abort("HAMILTONIAN_SHEAR_CONSTRAINT");}
  if (s/h-sig).abs()>3e-15{abort("INSTANTANEOUS_SIGMA_INVALID");}
  let tag=format!("{}:{:.5}",fam,q);
  let ent=bycase.entry(tag).or_insert((0,-1.0));
  if ent.0==0 && (t!=0.0||b!=0.0){abort("NOT_ZERO_ELAPSED_ORIGIN");}
  if ent.0>0 && t<=ent.1{abort("NONMONOTONE_PROPER_CLOCK");}
  ent.0+=1;ent.1=t; rows+=1;
  checksum+=t*1e-16+b+h*1e15;
 }
 if rows!=3006||bycase.len()!=6||!bycase.values().all(|v|v.0==501){abort("INCOMPLETE_TABLE");}
 println!("{{\"schema\":\"rei.axbi.source_background_table_consumer.v1\",\"rows\":{},\"cases\":{},\"n_per_case\":501,\"constraint_checks\":\"PASS\",\"checksum\":{:.17e},\"owner_REI_source_modified\":false}}",rows,bycase.len(),checksum);
}
