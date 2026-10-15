//! Standalone real Rust AX03 physical Gauss-4 short-step reference evaluator.
//! No external crates, no native science solver, no owner worktree mutation.
//! CLI: program INPUT.csv H0 Om Or Ol a_ref a_end
//! CSV family,q,a0,a1; all q and cosmology must match frozen caller source.
use std::{env,fs::File,io::{BufRead,BufReader}};
fn reject(msg:&str)->!{eprintln!("AXBI_SHORTSTEP_REJECT:{msg}");std::process::exit(3)}
fn f(s:&str)->f64{
 let x=s.parse::<f64>().unwrap_or_else(|_|reject("BAD_NUMBER"));
 if !x.is_finite(){reject("NONFINITE")}x
}
fn main(){
 let args:Vec<String>=env::args().skip(1).collect();
 if args.len()!=7{reject("ARGS_INPUT_H0_OM_OR_OL_AR_AEND")}
 let h0=f(&args[1]);let om=f(&args[2]);let orad=f(&args[3]);let ol=f(&args[4]);let aref=f(&args[5]);let aend=f(&args[6]);
 if !(h0>0.&&om>=0.&&orad>=0.&&ol>=0.&&aref>0.&&aend>aref){reject("COSMO_DOMAIN")}
 let hf=|a:f64|->f64{h0*(om/a.powi(3)+orad/a.powi(4)+ol).sqrt()};
 let hr=hf(aref);
 let reader=BufReader::new(File::open(&args[0]).unwrap_or_else(|_|reject("INPUT_FILE")));
 let mut lines=reader.lines();
 let header=lines.next().unwrap_or_else(||reject("HEADER")).unwrap();
 if header.trim()!="family,q,a0,a1"{reject("INPUT_SCHEMA")}
 // 4-point GL on [0,1], sorted pair weights.
 let roots=[-0.861136311594052575223946488893,-0.339981043584856264802665759103,
             0.339981043584856264802665759103, 0.861136311594052575223946488893];
 let weights=[0.173927422568726928686531974611,0.326072577431273071313468025389,
              0.326072577431273071313468025389,0.173927422568726928686531974611];
 println!("family,q,a0,a1,dt_s,db");
 let mut count=0usize;
 for l in lines{
  let s=l.unwrap_or_else(|_|reject("READ_FAILED"));
  let cols:Vec<&str>=s.trim().split(',').collect();
  if cols.len()!=4{reject("ROW_SHAPE")}
  let family=cols[0];let q=f(cols[1]);let a0=f(cols[2]);let a1=f(cols[3]);
  if ![0.0,0.005,-0.005,0.01,-0.01].contains(&q){reject("Q_NOT_FROZEN")}
  if family!="PhysicalDensityFixed" && family!="SameHDiagnostic"{reject("FAMILY")}
  if family=="SameHDiagnostic"&&q!=0.01{reject("SAME_H_SCOPE")}
  if !(a0>=aref&&a1<=aend&&a1>a0){reject("SCALE_ORDER")}
  let dx=((a1-a0)/a0).ln_1p();
  let panels=1_usize.max((dx/0.0028).ceil() as usize);
  if panels>2048{reject("PANELS")}
  let mut sumt=0.0_f64;let mut sumb=0.0_f64;
  let mut compt=0.0_f64;let mut compb=0.0_f64;
  for j in 0..panels{
   for k in 0..4{
    let lam=(j as f64+(roots[k]+1.)/2.)/panels as f64;
    let a=a0*(dx*lam).exp();
    let sh=q*hr*(aref/a).powi(3);
    let h=if family=="SameHDiagnostic"{hf(a)}else{hf(a).hypot(sh)};
    let t=(weights[k]/panels as f64)/h;
    let b=(weights[k]/panels as f64)*sh/h;
    let yt=t-compt;let tt=sumt+yt;compt=(tt-sumt)-yt;sumt=tt;
    let yb=b-compb;let tb=sumb+yb;compb=(tb-sumb)-yb;sumb=tb;
   }
  }
  let dt=dx*sumt;let db=dx*sumb;
  if !(dt.is_finite()&&dt>0.&&db.is_finite()){reject("RESULT_DOMAIN")}
  println!("{family},{q:.17e},{a0:.17e},{a1:.17e},{dt:.17e},{db:.17e}");
  count+=1;
 }
 if count==0{reject("EMPTY")}
 eprintln!("AXBI_SHORTSTEP_RUST_GL4_SUCCESS rows={count}");
}