#![forbid(unsafe_code)]
use std::{env,fs::{self,File},io::Write};
use rei_microphysics::{Interval,paired_runtime::{paired_initial,paired_trial,energy_nodes,PairedConfig,PairedState}};
const BIRTH:f64=13.7;
const FH:f64=0.083;
const CHI:[f64;3]=[13.598_434_599_702,24.587_389_011,54.417_76];
fn f(x:f64)->String{format!("{x:.17e}")}
fn energy_m(s:&PairedState)->f64{
 let g=&s.gas;
 g.w_ev_per_h+CHI[0]*g.fractions[0]+FH*(CHI[1]*g.fractions[1]+(CHI[1]+CHI[2])*g.fractions[2])+g.escape_ev_per_h
}
fn lower_physical_energy(h:[f64;3],t:f64)->Result<f64,Box<dyn std::error::Error>>{
 let mx=h.into_iter().fold(0_f64,f64::max);
 let exponent=Interval::point(-mx).map_err(|_|"SUPPORT_MX")?
     .mul(&Interval::point(t).map_err(|_|"SUPPORT_T")?).map_err(|_|"SUPPORT_EXPONENT")?;
 let e=Interval::point(BIRTH).map_err(|_|"SUPPORT_BIRTH")?
     .mul(&exponent.exp().map_err(|_|"SUPPORT_EXP")?).map_err(|_|"SUPPORT_ENERGY")?;
 Ok(e.lo)
}
fn bounds_n(s:&PairedState)->(f64,f64) {
 (s.photon_boxes.iter().chain(&s.lower_guard_n_box).map(|b|b.lo).sum(),
  s.photon_boxes.iter().chain(&s.lower_guard_n_box).map(|b|b.hi).sum())
}
fn photon_e(s:&PairedState,nodes:&[f64])->f64{
 let nk=nodes.len();
 s.photons.iter().enumerate().map(|(i,v)|v*nodes[i%nk]).sum::<f64>()
 +s.lower_guard_u.iter().sum::<f64>()
}
fn photon_n(s:&PairedState)->f64{s.photons.iter().sum::<f64>()+s.lower_guard_n.iter().sum::<f64>()}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a=env::args().collect::<Vec<_>>();if a.len()!=3{return Err("ARGS OUTDIR N_STEPS".into());}
 let nsteps:usize=a[2].parse()?;if nsteps==0||nsteps>160{return Err("N_STEPS_RANGE".into());}
 fs::create_dir_all(&a[1])?;
 let mut csv=File::create(format!("{}/original_paired_trajectory.csv",a[1]))?;
 writeln!(csv,"geometry,step,t_s,status,error,local_bound,public_width,max_ledger,photon_n,photon_box_lo,photon_box_hi,spurious_support_n,spurious_support_frac,spurious_support_box_lo,physical_energy_lower_ev,gas_xhii,gas_xheii,gas_xheiii,gas_w_ev_h,gas_width_max,gas_t_kelvin,source_n,absorbed_n,redshift_work_ev,thermal_work_ev,photon_global_number_residual,photon_global_energy_residual")?;
 let cfg=PairedConfig{spectral_subdivisions:4,n_mu:8,n_phi:16};
 let nodes=energy_nodes(&cfg)?;let dt=625_000_000.;
 for (geom,h) in [("S0_BI",[1.01e-14,0.99e-14,1.0e-14]),("S0_FLRW",[1.0e-14,1.0e-14,1.0e-14])] {
  let mut s=paired_initial(&cfg)?;
  let einitial=energy_m(&s)+photon_e(&s,&nodes);
  for step in 1..=nsteps {
   match paired_trial(&cfg,h,&s,dt){
    Err(e)=>{writeln!(csv,"{geom},{step},{},BLOCKED,{}",f(s.time_s+dt),e.code())?;
      eprintln!("{geom} BLOCKED step {step}: {}",e.code());break;}
    Ok(tr)=>{
     s=tr.state;
     let (nlo,nhi)=bounds_n(&s);
     let pmin=lower_physical_energy(h,s.time_s)?;
     let nbad=s.photons.iter().enumerate().filter(|(i,_)|nodes[i%nodes.len()]<pmin).map(|(_,v)|*v).sum::<f64>();
     let nbad_lo=s.photon_boxes.iter().enumerate().filter(|(i,_)|nodes[i%nodes.len()]<pmin).map(|(_,v)|v.lo).sum::<f64>();
     let n=photon_n(&s);
     let nres=n+s.absorbed_photons_per_h-0.05-s.source_photons_per_h;
     let eres=energy_m(&s)+photon_e(&s,&nodes)+s.redshift_work_ev_per_h+s.thermal_work_ev_per_h
         -einitial-s.source_energy_ev_per_h;
     let g=&s.gas;
     let particles=1.0+FH+g.fractions[0]+FH*(g.fractions[1]+2.0*g.fractions[2]);
     let temp=2.0*g.w_ev_per_h*1.602176634e-12/(3.0*1.380649e-16*particles);
     let gas_width=s.gas_box.iter().map(|b|b.hi-b.lo).fold(0.,f64::max);
     writeln!(csv,"{geom},{step},{},PASS,NONE,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
       f(s.time_s),f(tr.local_bound),f(tr.public_width),f(tr.max_ledger),
       f(n),f(nlo),f(nhi),f(nbad),f(nbad/n),f(nbad_lo),f(pmin),
       f(g.fractions[0]),f(g.fractions[1]),f(g.fractions[2]),f(g.w_ev_per_h),f(gas_width),f(temp),
       f(s.source_photons_per_h),f(s.absorbed_photons_per_h),f(s.redshift_work_ev_per_h),
       f(s.thermal_work_ev_per_h),f(nres),f(eres))?;
     if step==1||step==nsteps{
       for (k,audit) in tr.audits.iter().enumerate(){
        fs::write(format!("{}/{}_step{:03}_native_endpoint{}.json",a[1],geom,step,k),audit)?;
       }
     }
     if step==1 || step%16==0 || step==nsteps{
       eprintln!("{geom} step{step} local={:.3e} width={:.3e} ledger={:.3e} support_defect={:.6}",tr.local_bound,tr.public_width,tr.max_ledger,nbad/n);
     }
    }
   }
  }
 }
 Ok(())
}
