//! Opt-in BASS PR164 geometry table -> actual rei_microphysics::BackgroundPoint.
//!
//! SOURCE STATUS: Rust adapter candidate, NOT built in this ChatGPT session.
//! First execute the Python source/receipt SHA, units and Einstein physics gates.
//! This program checks Rust type parity; it does NOT enable native H/He reactions
//! or authorize AX08 old checkpoint resume.
use rei_microphysics::axbi_background::BackgroundPoint;
use std::collections::BTreeMap;
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};

fn fail(msg:&str)->! { eprintln!("BASS_REI_PR165_REJECT:{msg}"); std::process::exit(3); }
fn approximate(x:f64, y:f64, atol:f64, rtol:f64)->bool {
    x.is_finite() && y.is_finite() && (x-y).abs() <= atol+rtol*y.abs()
}
fn num(fields:&[&str], header:&[&str], name:&str)->f64 {
    let j=header.iter().position(|&key|key==name).unwrap_or_else(||fail("COLUMN_MISSING"));
    let y=fields[j].parse::<f64>().unwrap_or_else(|_|fail("COLUMN_FLOAT_PARSE"));
    if !y.is_finite(){fail("COLUMN_NONFINITE");} y
}
fn main(){
    let args:Vec<String>=env::args().collect();
    if args.len()!=2 {fail("USAGE_NATIVE_GEOMETRY_CSV");}
    let input=File::open(&args[1]).unwrap_or_else(|_|fail("CSV_IO"));
    let mut lines=BufReader::new(input).lines();
    let first=lines.next().unwrap_or_else(||fail("CSV_EMPTY"))
        .unwrap_or_else(|_|fail("CSV_HEADER_IO"));
    let columns:Vec<&str>=first.split(',').collect();
    let required=["case","x","a","b","time_s","h_flrw_per_s","h_per_s","s_per_s",
        "sigma_signed","Sigma","h_perp_per_s","h_parallel_per_s"];
    if columns.as_slice() != required.as_slice() {fail("CSV_HEADER_SCHEMA");}
    let names=["COLD_FLRW","WARM_ISOTROPIC","MASSIVE_A_PLUS","MASSIVE_A_MINUS",
        "MASS3_A_PLUS","MASS300_A_PLUS","SIGNED_PLUS","SIGNED_MINUS"];
    let mut cases:BTreeMap<String,(usize,f64,f64)>=BTreeMap::new();
    let mut n=0usize;
    let mut max_abs_signed=0.0_f64;
    let mut max_abs_sigma=0.0_f64;
    let mut max_relative_volume=0.0_f64;
    const H0:f64=2.1842852410855026e-18;
    const AREF:f64=1.0/21.0;
    for line in lines {
        let line=line.unwrap_or_else(|_|fail("CSV_ROW_IO"));
        let line=line.trim();
        if line.is_empty(){fail("CSV_EMPTY_ROW");}
        let values:Vec<&str>=line.split(',').collect();
        if values.len()!=required.len(){fail("CSV_ROW_WIDTH");}
        let id=values[0];
        if !names.contains(&id){fail("UNKNOWN_CASE");}
        if n/121>=names.len() || id!=names[n/121]{fail("CASE_ORDER");}
        let x=num(&values,&columns,"x");
        let a=num(&values,&columns,"a");
        let b=num(&values,&columns,"b");
        let t=num(&values,&columns,"time_s");
        let h=num(&values,&columns,"h_per_s");
        let s=num(&values,&columns,"s_per_s");
        let hf=num(&values,&columns,"h_flrw_per_s");
        let signed=num(&values,&columns,"sigma_signed");
        let sigma=num(&values,&columns,"Sigma");
        let hp=num(&values,&columns,"h_perp_per_s");
        let hz=num(&values,&columns,"h_parallel_per_s");
        if !(a>0.0 && h>0.0 && t>=0.0 && sigma>=0.0) {fail("GEOMETRY_DOMAIN");}
        if !approximate(a,AREF*x.exp(),1e-15,3e-12){fail("X_A_RELATION");}
        let expected=H0*(0.315/a.powi(3)+0.000092/a.powi(4)+0.684908).sqrt();
        if !approximate(hf,expected,1e-30,3e-12){fail("FLRW_REFERENCE_MISMATCH");}
        if !approximate(signed,s/h,1e-13,3e-12){fail("SIGNED_SHEAR_BAD");}
        if !approximate(sigma,3.0_f64.sqrt()*s.abs()/h,2e-13,3e-12){fail("MAGNITUDE_SIGMA_BAD");}
        if !approximate(hp,h-s,1e-30,3e-12) || !approximate(hz,h+2.0*s,1e-30,3e-12) {
            fail("DIRECTIONAL_H_BAD");
        }
        let physical=BackgroundPoint{a,b,time_s:t,h_flrw_per_s:hf,
            h_per_s:h,s_per_s:s,sigma:signed};
        let geo=physical.geometry().unwrap_or_else(|_|fail("ACTUAL_RUST_GEOMETRY"));
        let v=geo.scale_factors[0]*geo.scale_factors[1]*geo.scale_factors[2];
        let rel=(v/a.powi(3)-1.).abs();
        max_relative_volume=max_relative_volume.max(rel);
        if rel>5e-12 {fail("PHYSICAL_VOLUME");}
        max_abs_signed=max_abs_signed.max((signed-s/h).abs());
        max_abs_sigma=max_abs_sigma.max((sigma-3f64.sqrt()*s.abs()/h).abs());
        let entry=cases.entry(id.to_owned()).or_insert((0,-1.0,-1.0));
        if entry.0==0 && (x!=0.0 || t!=0.0 || b!=0.0){fail("CASE_INITIAL_ORIGIN");}
        if entry.0>0 && (x<=entry.1 || t<=entry.2){fail("GEOMETRY_CLOCK_NONMONOTONIC");}
        entry.0+=1;entry.1=x;entry.2=t;n+=1;
    }
    if n!=968 || cases.len()!=8 || cases.values().any(|z|z.0!=121){fail("INCOMPLETE_COHORT");}
    println!("{{\"schema\":\"bass.rei.native_geometry_pr165.v1\",\"rows\":{},\"cases\":{},\"max_sigma_signed_abs\":{:.17e},\"max_Sigma_abs\":{:.17e},\"max_relative_volume\":{:.17e},\"native_background_point_type_checked\":true,\"native_chemistry_driver_changed\":false}}",
        n,cases.len(),max_abs_signed,max_abs_sigma,max_relative_volume);
}
