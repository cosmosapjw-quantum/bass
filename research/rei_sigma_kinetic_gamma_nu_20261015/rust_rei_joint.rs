//! Actual rei_microphysics BackgroundPoint/GeometrySnapshot intake for the
//! gamma+masslessnu+massive-FD kinetic Einstein Bianchi-I external table.
//! This is a source type/physics gate, not native production driver adoption.
use rei_microphysics::axbi_background::BackgroundPoint;
use std::{env,fs::File,io::{BufRead,BufReader},collections::BTreeMap};
fn fail(msg:&str)->!{eprintln!("AXBI_JOINT_KINETIC_REJECT:{msg}");std::process::exit(3);}
fn v(c:&[&str],n:&[String],k:&str)->f64{
 let i=n.iter().position(|x|x==k).unwrap_or_else(||fail("MISSING_FIELD"));
 let x=c[i].parse::<f64>().unwrap_or_else(|_|fail("PARSE_FLOAT"));
 if !x.is_finite(){fail("NONFINITE");}x
}
fn main(){
 let args:Vec<_>=env::args().skip(1).collect();
 if args.len()!=5{fail("ARGS_CSV_H0_OM_OL_AREF");}
 let h0=args[1].parse::<f64>().unwrap();let om=args[2].parse::<f64>().unwrap();
 let ol=args[3].parse::<f64>().unwrap();let ar=args[4].parse::<f64>().unwrap();
 let mut iter=BufReader::new(File::open(&args[0]).unwrap_or_else(|_|fail("MISSING_TABLE"))).lines();
 let header=iter.next().unwrap_or_else(||fail("NO_HEADER")).unwrap();
 let keys:Vec<String>=header.split(',').map(str::to_owned).collect();
 let get=|c:&[&str],key:&str|v(c,&keys,key);
 const G:f64=6.67430e-11;const C:f64=299792458.0;
 let conv=8.*std::f64::consts::PI*G/(3.*C*C);
 let names=["FLRW_CONTROL","RADIATION_ONLY","MASSIVE_ONLY","BOTH_PRIMORDIAL",
            "BOTH_THOMSON_AX08","SIGNED_PLUS","SIGNED_MINUS","GAMMA_ONLY_THOMSON"];
 let mut cases=BTreeMap::<String,(usize,f64)>::new();
 let mut rows=0usize;
 let mut max_constraint=0.0_f64;
 let mut max_sigma=0.0_f64;
 for line in iter{
  let text=line.unwrap_or_else(|_|fail("IO"));
  let c:Vec<&str>=text.split(',').collect();
  if c.len()!=keys.len(){fail("NUM_FIELDS");}
  let id=c[keys.iter().position(|x|x=="case").unwrap_or_else(||fail("CASE_COLUMN"))];
  if !names.contains(&id){fail("UNEXPECTED_CASE");}
  let a=get(&c,"a");let b=get(&c,"b");let t=get(&c,"proper_elapsed_s");
  let h=get(&c,"H_mean_per_s");let s=get(&c,"s_per_s");let sigma=get(&c,"Sigma");
  let pr=get(&c,"radiation_rho_J_m3");let pm=get(&c,"massive_rho_J_m3");
  let pg=get(&c,"pi_gamma_J_m3");let pn=get(&c,"pi_nu_J_m3");
  let pi=get(&c,"pi_massive_J_m3");let pit=get(&c,"pi_total_J_m3");
  let e0=get(&c,"gamma_energy_J0");let n0=get(&c,"gamma_number_N0");
  let en=get(&c,"nu_energy_J0");let nn=get(&c,"nu_number_N0");
  let gp=get(&c,"GammaT_per_s");let ne=get(&c,"n_e_cm3");
  let fm=if id=="FLRW_CONTROL"||id=="RADIATION_ONLY"{0.0}else{0.1};
  if !(a>=ar&&a<=0.2+1e-15&&t>=0.0&&h>0.0&&sigma>=0.0&&
        pr>0.0&&pm>=0.0&&e0>0.0&&en>0.0&&gp>=0.0&&ne>=0.0){
      fail("PHYSICAL_DOMAIN");
  }
  if (n0-1.0).abs()>1e-10||(nn-1.).abs()>1e-10{fail("NUMBER_CONSERVATION");}
  let pred=(h0*h0*(om*(1.0-fm)/a.powi(3)+ol)+conv*(pr+pm)+s*s).sqrt();
  let herr=(h/pred-1.).abs();
  max_constraint=max_constraint.max(herr);
  if herr>2e-12{fail("EINSTEIN_HAMILTONIAN");}
  let sr=(sigma-(3.0_f64).sqrt()*s.abs()/h).abs();
  max_sigma=max_sigma.max(sr);
  if sr>3e-12{fail("SIGMA_SHEAR_CONVENTION");}
  if (pit-pg-pn-pi).abs()>3e-12*(pit.abs()+pg.abs()+pn.abs()+pi.abs()).max(1e-16){
     fail("TENSOR_PI_SUM");}
  if id=="FLRW_CONTROL"&&(s!=0.0||b!=0.0||sigma!=0.0||pi.abs()>1e-22){
     fail("FLRW_ZERO_LIMIT");}
  if (id=="BOTH_THOMSON_AX08"||id=="GAMMA_ONLY_THOMSON")&&(gp==0.0||ne==0.0){
     fail("THOMSON_DONOR_ABSENT");}
  if id!="BOTH_THOMSON_AX08"&&id!="GAMMA_ONLY_THOMSON"&&(gp!=0.0||ne!=0.0){
     fail("NEUTRINO_THOMSON_OR_SPURIOUS_GAMMA");}
  let f=BackgroundPoint{a,b,time_s:t,h_flrw_per_s:pred,
        h_per_s:h,s_per_s:s,sigma:s/h};
  if f.geometry().is_err(){fail("ORIGINAL_REI_GEOMETRY");}
  let entry=cases.entry(id.to_owned()).or_insert((0,-1.0));
  if entry.0==0 && (t!=0.0||b!=0.0){fail("INITIAL_TB_ZERO");}
  if entry.0>0 && t<=entry.1{fail("PROPER_CLOCK_NONMONOTONIC");}
  entry.0+=1;entry.1=t;rows+=1;
 }
 if rows!=8*401||cases.len()!=8||cases.values().any(|x|x.0!=401){
  fail("MISSING_SOURCE_HISTORY");}
 println!("{{\"schema\":\"rei.axbi.gamma_nu_massive_real_Rust_bridge.v1\",\
 \"rows\":{},\"cases\":{},\"max_constraint_relative\":{:.17e},\
 \"max_sigma_absolute\":{:.17e},\"source\":\"real rei_microphysics BackgroundPoint geometry\",\
 \"native_source_chemistry_changed\":false}}",
 rows,cases.len(),max_constraint,max_sigma);
}
