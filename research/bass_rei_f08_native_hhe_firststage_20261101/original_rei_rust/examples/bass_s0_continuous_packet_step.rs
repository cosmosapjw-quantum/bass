//! BASS-only orchestration adapter. All physical operators remain the immutable
//! original REI Rust primary_stage_step_conservative and reference AtomicProvider.
#![forbid(unsafe_code)]
use std::{env,fs::File,io::{BufRead,BufReader,Write}};
use rei_microphysics::{StepControl};
use rei_microphysics::coupled_primary::{PrimaryPacket,PrimaryStage,PrimaryState,primary_stage_step_conservative};

const CHI:[f64;3]=[13.598434599702,24.587389011,54.41776];
const KB_EV:f64=1.380649e-16/1.602176634e-12;
fn val(s:&str)->Result<f64,String>{
 let v:f64=s.parse().map_err(|_|"BAD_FLOAT")?;
 if !v.is_finite() {return Err("NONFINITE".into());}
 Ok(v)
}
fn energy(s:&PrimaryState,he:f64)->f64 {
 s.w_ev_per_h+CHI[0]*s.fractions[0]
 +he*(CHI[1]*s.fractions[1]+(CHI[1]+CHI[2])*s.fractions[2])
 +s.escape_ev_per_h+s.packets.iter().map(|p|p.energy_ev*p.per_h).sum::<f64>()
}
fn main()->Result<(),Box<dyn std::error::Error>> {
 let a=env::args().collect::<Vec<_>>();
 if a.len()!=3{return Err("ARGS input output".into());}
 let mut stage:Option<PrimaryStage>=None;
 let mut old:Option<PrimaryState>=None;
 let mut dt=0.0;
 for line in BufReader::new(File::open(&a[1])?).lines(){
  let line=line?;
  if line.starts_with('#')||line.is_empty(){continue;}
  let bits=line.split('|').collect::<Vec<_>>();
  match bits[0] {
   "S"=>{
    if bits.len()!=11||stage.is_some(){return Err("STAGE_INPUT_SCHEMA".into());}
    stage=Some(PrimaryStage{n_h_cm3:val(bits[1])?,f_he:val(bits[2])?,h_mean_per_s:val(bits[3])?});
    dt=val(bits[4])?;
    old=Some(PrimaryState{
     fractions:[val(bits[5])?,val(bits[6])?,val(bits[7])?],
     w_ev_per_h:val(bits[8])?,escape_ev_per_h:val(bits[9])?,packets:Vec::new()});
    let _clock=val(bits[10])?;
   },
   "P"=>{
    if bits.len()!=3{return Err("PACKET_INPUT_SCHEMA".into());}
    let e=val(bits[1])?;let n=val(bits[2])?;
    if e<=0.0||n<=0.0{return Err("BAD_PACKET".into());}
    old.as_mut().ok_or("NO_PARENT")?.packets.push(PrimaryPacket{energy_ev:e,per_h:n});
   },
   _=>return Err("UNKNOWN_INPUT".into())
  }
 }
 let stage=stage.ok_or("NO_STAGE")?;
 let old=old.ok_or("NO_STATE")?;
 if old.packets.is_empty(){return Err("EMPTY_SOURCE".into());}
 let (out,comp)=primary_stage_step_conservative(
  &stage,&old,dt,StepControl{max_iterations:200,residual_tolerance:1e-15},0.)?;
 let x=&out.state;
 if out.iterations>200||out.residual>1e-15 {return Err("ORIGINAL_ROOT_CONVERGENCE".into());}
 let n0=old.packets.iter().map(|p|p.per_h).sum::<f64>();
 let n1=x.packets.iter().map(|p|p.per_h).sum::<f64>();
 let abs=out.events.photo_per_h.iter().map(|a|a.iter().sum::<f64>()).sum::<f64>();
 let e0=energy(&old,stage.f_he);
 let e1=energy(x,stage.f_he);
 let photon_res=n0-n1-abs;
 let energy_res=e0-e1-out.events.thermal_work_ev_per_h;
 if photon_res.abs()>1e-12*n0.max(0.05) ||
    energy_res.abs()>1e-12*e0.max(1.0) {
  return Err("NATIVE_LEDGER_FAIL".into())
 }
 let hii=out.events.photo_per_h.iter().map(|a|a[0]).sum::<f64>();
 let hei=out.events.photo_per_h.iter().map(|a|a[1]).sum::<f64>();
 let heii=out.events.photo_per_h.iter().map(|a|a[2]).sum::<f64>();
 let heat=out.events.photo_per_h.iter().zip(old.packets.iter())
   .map(|(a,p)|a.iter().enumerate().map(|(j,w)|w*(p.energy_ev-CHI[j]).max(0.)).sum::<f64>()).sum::<f64>();
 let n_particle=1.0+stage.f_he+x.fractions[0]+stage.f_he*(x.fractions[1]+2.0*x.fractions[2]);
 let temp=2.0*x.w_ev_per_h/(3.0*KB_EV*n_particle);
 let mut output=File::create(&a[2])?;
 writeln!(output,"S|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}|{:.17e}",
   x.fractions[0],x.fractions[1],x.fractions[2],x.w_ev_per_h,x.escape_ev_per_h,temp,n1,
   out.iterations,out.residual,photon_res,energy_res,
   hii,hei,heii,heat,
   out.events.thermal_work_ev_per_h,
   out.events.collision_per_h[0],out.events.recombination_per_h[0],
   comp,abs)?;
 for p in &x.packets {
  writeln!(output,"P|{:.17e}",p.per_h)?;
 }
 Ok(())
}
