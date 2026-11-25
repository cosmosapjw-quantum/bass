//! BASS research-only original source S0 photon-to-interval-root comparison.
//! Calls immutable REI primary_stage_root and primary_stage_step_conservative.
#![forbid(unsafe_code)]
use std::{env,fs::{self,File},io::{BufRead,BufReader,Write},path::Path};
use rei_microphysics::{Interval,StepControl};
use rei_microphysics::coupled_primary::{
 PrimaryPacket,PrimaryStage,PrimaryState,PrimaryBox,
 primary_stage_root,primary_stage_step_conservative
};
fn value(s:&str)->Result<f64,Box<dyn std::error::Error>>{
 let a:f64=s.parse()?;
 if !a.is_finite(){return Err("NONFINITE".into())}
 Ok(a)
}
fn read(p:&Path)->Result<(PrimaryStage,PrimaryState,f64),Box<dyn std::error::Error>> {
 let mut stage=None;let mut state=None;let mut dt=0.;
 for l in BufReader::new(File::open(p)?).lines(){
  let line=l?;
  if line.is_empty()||line.starts_with('#'){continue;}
  let a=line.split('|').collect::<Vec<_>>();
  match a[0] {
   "S"=>{
    if a.len()!=11||stage.is_some(){return Err("STAGE_SCHEMA".into());}
    stage=Some(PrimaryStage{n_h_cm3:value(a[1])?,f_he:value(a[2])?,h_mean_per_s:value(a[3])?});
    dt=value(a[4])?;
    state=Some(PrimaryState{fractions:[value(a[5])?,value(a[6])?,value(a[7])?],
      w_ev_per_h:value(a[8])?,escape_ev_per_h:value(a[9])?,packets:Vec::new()});
    let _clock=value(a[10])?;
   },
   "P"=>{
    if a.len()!=3{return Err("PACKET_SCHEMA".into());}
    let e=value(a[1])?;let n=value(a[2])?;
    if e<=0.||n<=0.{return Err("NEGATIVE_OR_ZERO_PHOTON_SOURCE".into());}
    state.as_mut().ok_or("NO_STATE")?.packets.push(PrimaryPacket{energy_ev:e,per_h:n});
   },
   _=>return Err("UNKNOWN_SOURCE_LINE".into())
  }
 }
 Ok((stage.ok_or("NO_STAGE")?,state.ok_or("NO_STATE")?,dt))
}
fn fmt(x:f64)->String{format!("{x:.17e}")}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a=env::args().collect::<Vec<_>>();
 if a.len()!=3{return Err("ARGS input_dir output_csv".into());}
 let mut files=fs::read_dir(&a[1])?.filter_map(|x|x.ok()).map(|x|x.path())
    .filter(|p|p.extension().is_some_and(|x|x=="txt") && p.file_stem().is_some_and(|x|x.to_string_lossy().starts_with("S0_"))).collect::<Vec<_>>();
 files.sort();
 if files.is_empty(){return Err("NO_SOURCE_CASES".into())}
 let ctl=StepControl{max_iterations:200,residual_tolerance:1e-15};
 let mut out=File::create(&a[2])?;
 writeln!(out,"case_id,packets,n_H_cm3,dt_s,Nin_per_H,Uin_ev_per_H,root_status,root_error_code,conservative_xHII,conservative_xHeII,conservative_xHeIII,conservative_w_ev_per_H,point_iterations,point_residual,root_q,root_width_xHII,root_width_xHeII,root_width_xHeIII,root_width_w_ev_per_H,root_contains_conservative,centre_vs_conservative_max_abs,photons_contain_conservative,photon_sum_interval_width_per_H,root_max_relative_gas_width")?;
 for p in files {
  let id=p.file_stem().ok_or("NO_FILENAME")?.to_string_lossy().to_string();
  let (stage,old,dt)=read(&p)?;
  let in_n=old.packets.iter().map(|p|p.per_h).sum::<f64>();
  let in_u=old.packets.iter().map(|p|p.energy_ev*p.per_h).sum::<f64>();
  let (state,_comp)=primary_stage_step_conservative(&stage,&old,dt,ctl,0.)?;
  let parent=PrimaryBox{
    gas:[Interval::point(old.fractions[0]).map_err(|_| "INTERVAL_INPUT")?,Interval::point(old.fractions[1]).map_err(|_| "INTERVAL_INPUT")?,
         Interval::point(old.fractions[2]).map_err(|_| "INTERVAL_INPUT")?,Interval::point(old.w_ev_per_h).map_err(|_| "INTERVAL_INPUT")?],
    photons:old.packets.iter().map(|p|Interval::point(p.per_h))
       .collect::<Result<Vec<_>,_>>().map_err(|_| "INTERVAL_INPUT")?
  };
  let gaspoint=[state.state.fractions[0],state.state.fractions[1],state.state.fractions[2],state.state.w_ev_per_h];
  let pre=vec![id.clone(),old.packets.len().to_string(),fmt(stage.n_h_cm3),fmt(dt),
               fmt(in_n),fmt(in_u)];
  match primary_stage_root(&stage,&old,&parent,dt,ctl) {
   Err(e)=>{
     let mut row=pre;
     row.push("BLOCKED".into());row.push(e.code().into());
     row.extend(gaspoint.iter().map(|x|fmt(*x)));
     row.push(state.iterations.to_string());row.push(fmt(state.residual));
     row.extend(std::iter::repeat("nan".to_string()).take(10));
     writeln!(out,"{}",row.join(","))?;
     eprintln!("NATIVE_ROOT_BLOCKED {} {}",id,e.code());
   },
   Ok(root)=>{
     let gas=[root.gas[0],root.gas[1],root.gas[2],root.gas[3]];
     let widths=gas.map(|b|b.hi-b.lo);
     let includes=gas.iter().zip(gaspoint.iter()).all(|(b,x)|b.lo<=*x&&*x<=b.hi);
     let centre_offset=root.centre.iter().zip(gaspoint.iter())
        .map(|(u,v)|(*u-*v).abs()).fold(0.,f64::max);
     let phot_contains=root.photons.iter().zip(state.state.packets.iter())
        .all(|(b,p)|b.lo<=p.per_h&&p.per_h<=b.hi);
     let phot_width=root.photons.iter().map(|b|b.hi-b.lo).sum::<f64>();
     let rel_width=widths.iter().zip(root.centre.iter())
        .map(|(w,c)|w/c.abs().max(1.0e-10)).fold(0.,f64::max);
     let mut row=pre;
     row.extend(["PASS".to_string(),"NONE".to_string()]);
     row.extend(gaspoint.iter().map(|x|fmt(*x)));
     row.push(state.iterations.to_string());row.push(fmt(state.residual));
     row.push(fmt(root.q));
     row.extend(widths.iter().map(|x|fmt(*x)));
     row.push(includes.to_string());row.push(fmt(centre_offset));
     row.push(phot_contains.to_string());row.push(fmt(phot_width));row.push(fmt(rel_width));
     writeln!(out,"{}",row.join(","))?;
     eprintln!("NATIVE_ROOT_PROBE {} q={:.5e} gas_contain={} photons_contain={} maxwidth={:.3e}",
       id,root.q,includes,phot_contains,rel_width);
   }
  }
 }
 Ok(())
}
