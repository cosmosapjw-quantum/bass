//! BASS research-only source-pinned original REI coupled H/He stage.
#![forbid(unsafe_code)]
use std::{env,fs::File,io::{BufRead,BufReader,Write}};
use rei_microphysics::{Absorber,AtomicProvider,StepControl};
use rei_microphysics::coupled_primary::{
    PrimaryPacket,PrimaryStage,PrimaryState,primary_stage_step_conservative
};

const CHI:[f64;3]=[13.598434599702,24.587389011,54.41776];
const KBEV:f64=8.617333262145e-5;
const C:f64=29979245800.0;

#[derive(Debug)]
struct Case {
 id:String, branch:String, model:String, tick:usize, t:f64, dt:f64,
 nh:f64, fhe:f64, hubble:f64,
 x:[f64;3], w:f64, escape:f64,
 packets:Vec<PrimaryPacket>,
}
fn err(s:&str)->String{s.to_string()}
fn fl(s:&str)->Result<f64,String>{
 let x:f64=s.parse().map_err(|_|err("NONNUMERIC_INPUT"))?;
 if !x.is_finite(){return Err(err("NONFINITE_INPUT"));}
 Ok(x)
}
fn usize_parse(s:&str)->Result<usize,String>{
 s.parse().map_err(|_|err("NONINTEGER_INPUT"))
}
fn energy(s:&PrimaryState,fhe:f64)->f64{
 s.w_ev_per_h+CHI[0]*s.fractions[0]
 +fhe*(CHI[1]*s.fractions[1]+(CHI[1]+CHI[2])*s.fractions[2])
 +s.escape_ev_per_h+
 s.packets.iter().map(|p|p.energy_ev*p.per_h).sum::<f64>()
}
fn temp(s:&PrimaryState,fhe:f64)->f64{
 let x=s.fractions;
 let np=1.0+fhe+x[0]+fhe*(x[1]+2.0*x[2]);
 2.0*s.w_ev_per_h/(3.0*KBEV*np)
}
fn simulate(z:&Case)->Result<String,String>{
 if z.packets.is_empty() || z.packets.iter().any(|p|p.energy_ev<=0. || p.per_h<=0.) {
  return Err(err("PHOTON_INPUT_DOMAIN"));
 }
 let stage=PrimaryStage{n_h_cm3:z.nh,f_he:z.fhe,h_mean_per_s:z.hubble};
 let old=PrimaryState{fractions:z.x,w_ev_per_h:z.w,escape_ev_per_h:z.escape,packets:z.packets.clone()};
 let count0: f64=old.packets.iter().map(|p|p.per_h).sum();
 let u0:f64=old.packets.iter().map(|p|p.energy_ev*p.per_h).sum();
 let reference=energy(&old,z.fhe);
 let provider=AtomicProvider::reference();
 let mut photo_input_s=0.0;
 let mut photo_input_heat=0.0;
 let mut source_support_below=0.0;
 for p in &old.packets{
  let sig=provider.cross_section(Absorber::HI,p.energy_ev).map_err(|e|e.to_string())?;
  photo_input_s+=C*z.nh*sig*p.per_h;
  photo_input_heat+=C*z.nh*(1.0-z.x[0])*sig*p.per_h*(p.energy_ev-CHI[0]).max(0.);
  if p.energy_ev<13.7*(-1.01e-14*(z.t+z.dt)).exp(){
    source_support_below+=p.per_h;
  }
 }
 let ctl=StepControl{max_iterations:200,residual_tolerance:1e-15};
 let (step,wcomp)=primary_stage_step_conservative(&stage,&old,z.dt,ctl,0.)
   .map_err(|e|format!("NATIVE_REI_STAGE_{}",e.code()))?;
 let out=&step.state;
 let count1:f64=out.packets.iter().map(|p|p.per_h).sum();
 let u1:f64=out.packets.iter().map(|p|p.energy_ev*p.per_h).sum();
 let mut photo=[0.0_f64;3];
 let mut photo_heat=0.;
 for (e,p) in step.events.photo_per_h.iter().zip(&old.packets) {
  for a in 0..3{
   photo[a]+=e[a];
   photo_heat+=e[a]*(p.energy_ev-CHI[a]).max(0.);
  }
 }
 let photo_sum=photo.iter().sum::<f64>();
 let source_count_res=count0-count1-photo_sum;
 let e1=energy(out,z.fhe);
 let energy_res=reference-e1-step.events.thermal_work_ev_per_h;
 let x1=out.fractions;
 let helium_sum=x1[1]+x1[2];
 if x1.iter().any(|v|!v.is_finite()||*v<0.||*v>1.) || helium_sum>1.0 {
  return Err(err("NATIVE_HELIUM_SOURCE_DOMAIN"));
 }
 if source_count_res.abs()>1e-12*count0.max(1e-15){
  return Err(format!("NATIVE_PHOTON_NUMBER_LEDGER:{}",source_count_res));
 }
 if energy_res.abs()>1e-12*reference.max(1e-15){
  return Err(format!("NATIVE_TOTAL_ENERGY_LEDGER:{}",energy_res));
 }
 if photo.iter().any(|x|*x<0.) || photo_heat<0. || !step.residual.is_finite(){
  return Err(err("NATIVE_PHOTO_EVENT_DOMAIN"));
 }
 let floats=[z.t,z.dt,z.nh,count0,u0,temp(&old,z.fhe),photo_input_s,photo_input_heat,
     count1,u1,temp(out,z.fhe),photo[0],photo[1],photo[2],
     photo_heat,step.events.collision_per_h[0],step.events.recombination_per_h[0],
     x1[0],x1[1],x1[2],x1[0]-z.x[0],x1[1]-z.x[1],x1[2]-z.x[2],
     out.w_ev_per_h-z.w,out.w_ev_per_h,step.events.thermal_work_ev_per_h,
     out.escape_ev_per_h-z.escape,source_count_res,energy_res,wcomp,
     source_support_below,step.residual];
 let mut values=vec![z.id.clone(),z.branch.clone(),z.model.clone(),z.tick.to_string(),z.packets.len().to_string(),
  step.iterations.to_string()];
 values.extend(floats.iter().map(|v|format!("{v:.17e}")));
 Ok(values.join(","))
}
fn read_cases(path:&str)->Result<Vec<Case>,String>{
 let file=File::open(path).map_err(|e|e.to_string())?;
 let mut cases:Vec<Case>=vec![];
 for line in BufReader::new(file).lines(){
  let s=line.map_err(|e|e.to_string())?;
  if s.trim().is_empty() || s.starts_with('#'){continue;}
  let a=s.split('|').collect::<Vec<_>>();
  match a.first().copied(){
   Some("S")=>{
    if a.len()!=15{return Err(format!("STAGE_FIELDS_{}",a.len()));}
    cases.push(Case{
     id:a[1].to_string(),branch:a[2].to_string(),model:a[3].to_string(),
     tick:usize_parse(a[4])?,t:fl(a[5])?,dt:fl(a[6])?,
     nh:fl(a[7])?,fhe:fl(a[8])?,hubble:fl(a[9])?,
     x:[fl(a[10])?,fl(a[11])?,fl(a[12])?],
     w:fl(a[13])?,escape:fl(a[14])?,packets:vec![]
    });
   }
   Some("P")=>{
    if a.len()!=3{return Err(err("PACKET_FIELDS"));}
    let last=cases.last_mut().ok_or_else(||err("PACKET_WITHOUT_STAGE"))?;
    let e=fl(a[1])?;
    let n=fl(a[2])?;
    if n>0.0{
     last.packets.push(PrimaryPacket{energy_ev:e,per_h:n});
    }
   }
   _=>return Err(err("UNKNOWN_INPUT_LINE")),
  }
 }
 if cases.len()<2 {return Err(err("INSUFFICIENT_SOURCE_CASES"));}
 Ok(cases)
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args=env::args().collect::<Vec<_>>();
 if args.len()!=3{return Err(err("ARGS input.txt output.csv").into());}
 let cases=read_cases(&args[1])?;
 let mut f=File::create(&args[2])?;
 writeln!(f,"id,branch,model,tick,packets,iterations,t_s,dt_s,nH_cm3,N_before_per_H,U_before_eV_per_H,T_before_K,HI_gamma_in_s_inv,HI_excess_heat_rate_in_eV_per_H_s,N_after_per_H,U_after_eV_per_H,T_after_K,HI_abs_per_H,HeI_abs_per_H,HeII_abs_per_H,excess_photoheat_events_eV_per_H,HI_collision_per_H,HI_recombination_per_H,xHII_after,xHeII_after,xHeIII_after,dxHII,dxHeII,dxHeIII,dw_ev_per_H,w_after_ev_per_H,thermal_work_ev_per_H,escape_delta_ev_per_H,photon_count_residual,energy_residual_ev_per_H,compensation_ev_per_H,below_physical_support_N_per_H,stage_residual")?;
 for z in &cases{
  let row=simulate(z).map_err(|e|format!("{}: {}",z.id,e))?;
  writeln!(f,"{row}")?;
  eprintln!("NATIVE_COUPLED_REAL_SOURCE_PASS {} {} {} {} packets",z.id,z.branch,z.model,z.packets.len());
 }
 Ok(())
}
