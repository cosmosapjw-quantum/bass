//! Bounded original AXBI owner consumer. No new science or controller formula.
#![allow(unexpected_cfgs)]
use rei_microphysics::{axbi_driver::{Driver,DriverConfig,DriverState,compiled_identity},ForwardError};
use std::{env,fs::{self,File},io::{Write,BufWriter},path::Path,time::Instant};
type E=Box<dyn std::error::Error>;
fn put_f(w:&mut impl Write,x:f64)->std::io::Result<()>{w.write_all(&x.to_bits().to_le_bytes())}
fn put_u(w:&mut impl Write,x:usize)->std::io::Result<()>{w.write_all(&(x as u64).to_le_bytes())}
fn state_bits(w:&mut impl Write,s:&DriverState)->std::io::Result<()>{
 for x in [s.a,s.gas.fractions[0],s.gas.fractions[1],s.gas.fractions[2],s.gas.w_erg_per_h,s.next_dln_a,s.max_newton_residual,s.last_error,s.wall_elapsed_s]{put_f(w,x)?;}
 for x in [s.accepted,s.attempts,s.comparisons,s.rejects,s.consecutive_rejects,s.rhs_evaluations,s.photons.len()]{put_u(w,x)?;}
 let l=&s.ledgers;
 for x in [l.source_n,l.source_u,l.absorbed_n,l.escaped_u,l.boundary_n,l.boundary_u,l.thermal_work,l.photon_work,l.cmb_input,l.dr_events,l.ce_cap_ev,l.excluded_dr_ev]{put_f(w,x)?;}
 for a in [&l.rr_events,&l.ci_events,&l.photo_events,&l.ci_floor_events]{for &x in a{put_f(w,x)?;}}
 for &x in &s.photons{put_f(w,x)?;}
 Ok(())
}
fn output(driver:&Driver,s:&DriverState,case:&str,out:&Path,terminal:bool,elapsed:f64,
          h:&mut impl Write,a:&mut impl Write,p:&mut impl Write,l:&mut impl Write,f:&mut impl Write)->Result<bool,ForwardError>{
 let due=driver.spectrum_due(s.accepted,elapsed,terminal);
 driver.output_batch(s,case,out,due,h,a,p,l,f)?;Ok(due)
}
fn main()->Result<(),E>{
 let args:Vec<String>=env::args().collect();
 if args.len()!=6{return Err("ARGS mode case early|plateau inputs output".into());}
 let (mode,case,window)=(&args[1],&args[2],&args[3]);let inputs=Path::new(&args[4]);let out=Path::new(&args[5]);
 if out.exists(){return Err("OUTPUT_ALREADY_EXISTS".into())}
 if !["original","profile_uncached","exact_reuse"].contains(&mode.as_str())||!["ZERO","SHEAR_PLUS"].contains(&case.as_str())||!["early","plateau"].contains(&window.as_str()){return Err("INVALID_BENCH_MODE".into())}
 #[cfg(not(bass_geometry_reuse))]
 if mode!="original"{return Err("BASELINE_CANNOT_ENABLE_CACHE".into())}
 fs::create_dir_all(out)?;
 fs::write(out.join("native_source_identity.txt"),compiled_identity())?;
 let config_text=fs::read_to_string(inputs.join(case).join("config.cfg"))?;
 let mut timing=File::create(out.join("TIMING.csv"))?;
 writeln!(timing,"rep,mode,case,window,wall_ns,adaptive_ns,output_ns,checkpoint_ns,background_calls,background_misses,background_hits,reference_hits,quadrature_ns,cache_ns,new_accepted,new_comparisons,new_attempts,new_rhs,new_rejects,final_a,final_xHII,final_xHeII,final_xHeIII,final_w_erg_H,number_residual,energy_residual,initial_a,initial_accepted,initial_attempts,initial_rhs,prior_wall_s")?;
 let process_start=Instant::now();let(mut total_comparisons,mut total_attempts,mut total_rhs,mut total_accepted)=(0usize,0usize,0usize,0usize);
 for rep in 0..3 {
  let mut config=DriverConfig::read(&config_text)?;
  let (probe,init)=Driver::new(config.clone())?;
  let mut state=if window=="early"{init}else{probe.read_checkpoint(&inputs.join(case).join("checkpoint.txt"))?};
  let initial=state.clone();
  config.max_steps=initial.accepted+96;config.max_attempts=initial.attempts+768;config.max_rhs=initial.rhs_evaluations+12000;
  config.max_wall_s=initial.wall_elapsed_s+60.0;
  let (driver,_)=Driver::new(config)?;
  #[cfg(bass_geometry_reuse)]
  driver.background.configure_exact_reuse(mode=="exact_reuse")?;
  let dir=out.join(format!("rep{rep}"));fs::create_dir(&dir)?;
  let mut h=BufWriter::new(File::create(dir.join("history.csv"))?);
  let mut a=BufWriter::new(File::create(dir.join("abundances.csv"))?);
  let mut p=BufWriter::new(File::create(dir.join("spectra.csv"))?);
  let mut l=BufWriter::new(File::create(dir.join("ledgers.csv"))?);
  let mut f=BufWriter::new(File::create(dir.join("feedback.csv"))?);
  let mut bits=BufWriter::new(File::create(dir.join("states.bin"))?);
  let mut mask=BufWriter::new(File::create(dir.join("cadence.csv"))?);
  driver.save_checkpoint_budget(&dir,&dir.join("initial_checkpoint.txt"),&state)?;
  state_bits(&mut bits,&state)?;
  output(&driver,&state,case,&dir,true,0.0,&mut h,&mut a,&mut p,&mut l,&mut f)?;
  #[cfg(bass_geometry_reuse)]
  let profile_before=driver.background.exact_reuse_profile()?;
  let started=Instant::now();let mut last_checkpoint=Instant::now();
  let(mut adaptive_ns,mut output_ns,mut checkpoint_ns)=(0u128,0u128,0u128);
  let mut previous_counts=(state.comparisons,state.attempts,state.rhs_evaluations,state.accepted);
  while state.accepted<initial.accepted+32 {
   if process_start.elapsed().as_secs_f64()>=58.0||total_comparisons>=256||total_attempts>=768||total_rhs>=12000||total_accepted>=96{return Err("BOUNDED_PROFILE_CAP".into())}
   let t=Instant::now();let result=driver.adaptive_step(&mut state);adaptive_ns+=t.elapsed().as_nanos();
   total_comparisons+=state.comparisons-previous_counts.0;total_attempts+=state.attempts-previous_counts.1;total_rhs+=state.rhs_evaluations-previous_counts.2;total_accepted+=state.accepted-previous_counts.3;
   previous_counts=(state.comparisons,state.attempts,state.rhs_evaluations,state.accepted);
   state_bits(&mut bits,&state)?;
   let accepted=match result {Ok(v)=>v,Err(e)=>{fs::write(dir.join("FIRST_FAILURE.txt"),format!("{e:?}\n"))?;driver.save_checkpoint_budget(&dir,&dir.join("last_checkpoint.txt"),&state)?;return Err(e.into());}};
   if accepted {
    let terminal=state.accepted==initial.accepted+32;
    let t=Instant::now();let due=output(&driver,&state,case,&dir,terminal,last_checkpoint.elapsed().as_secs_f64(),&mut h,&mut a,&mut p,&mut l,&mut f)?;output_ns+=t.elapsed().as_nanos();
    writeln!(mask,"{},{}",state.accepted,due)?;
    if due {let t=Instant::now();driver.save_checkpoint_budget(&dir,&dir.join("checkpoint.txt"),&state)?;checkpoint_ns+=t.elapsed().as_nanos();last_checkpoint=Instant::now();}
   }
  }
  for writer in [&mut h,&mut a,&mut p,&mut l,&mut f,&mut bits,&mut mask]{writer.flush()?;}
  let wall_ns=started.elapsed().as_nanos();
  let (nc,ne)=driver.residuals(&state)?;
  #[cfg(bass_geometry_reuse)]
  let pr=driver.background.exact_reuse_profile()?;
  #[cfg(bass_geometry_reuse)]
  let prof=(pr.calls-profile_before.calls,pr.misses-profile_before.misses,pr.hits-profile_before.hits,pr.reference_hits-profile_before.reference_hits,pr.quadrature_ns-profile_before.quadrature_ns,pr.cache_ns-profile_before.cache_ns);
  #[cfg(not(bass_geometry_reuse))]
  let prof=(0u64,0u64,0u64,0u64,0u128,0u128);
  writeln!(timing,"{rep},{mode},{case},{window},{wall_ns},{adaptive_ns},{output_ns},{checkpoint_ns},{},{},{},{},{},{},{},{},{},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{},{},{:.17e}",prof.0,prof.1,prof.2,prof.3,prof.4,prof.5,state.accepted-initial.accepted,state.comparisons-initial.comparisons,state.attempts-initial.attempts,state.rhs_evaluations-initial.rhs_evaluations,state.rejects-initial.rejects,state.a,state.gas.fractions[0],state.gas.fractions[1],state.gas.fractions[2],state.gas.w_erg_per_h,nc,ne,initial.a,initial.accepted,initial.attempts,initial.rhs_evaluations,initial.wall_elapsed_s)?;
  eprintln!("OWNER_WINDOW mode={mode} case={case} window={window} rep={rep} accepted={} comparisons={} wall_ms={:.3}",state.accepted-initial.accepted,state.comparisons-initial.comparisons,wall_ns as f64/1e6);
 }
 Ok(())
}
