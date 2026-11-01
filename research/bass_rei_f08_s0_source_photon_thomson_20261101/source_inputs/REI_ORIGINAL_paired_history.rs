//! Durable prospective S0 pilot/full driver. Scientific admission is external.
pub use rei_microphysics::*;
use rei_microphysics::coupled_primary::{PrimaryPacket,PrimaryState};
#[path="../src/paired_runtime.rs"] mod paired_runtime;
use paired_runtime::*;
use std::{env,fs::{self,File,OpenOptions},io::{self,Write},path::{Path,PathBuf}};

const SCENARIO:&str=include_str!("../../../configs/rei_fastest_v1/science_scenario_v1.json");
fn error(s:&str)->io::Error{io::Error::new(io::ErrorKind::InvalidData,s.to_string())}
fn ioerr(e:ForwardError)->io::Error{error(e.code())}
fn b(x:f64)->String{format!("{:016x}",x.to_bits())}
fn f(x:&str)->io::Result<f64>{Ok(f64::from_bits(u64::from_str_radix(x,16).map_err(|_|error("checkpoint float"))?))}
fn source_bytes()->Vec<u8>{
    let pieces:&[(&str,&str)]=&[
        ("scenario",SCENARIO),
        ("frozen-inputs",r########"{
  ".cuh/fastest-track/REI-F08-PAIRED/SCIENTIFIC_CONTRACT.md": "7c8b68894558de2000b1d78849b7988949cc0aa568dc599830f2ac3daee97ded",
  ".cuh/fastest-track/REI-F08-PAIRED/native_tests.rs": "d48a8a7494e6393871aa7f5f722ca43f103a95175551d91218f81c5f05b0b36e",
  ".cuh/fastest-track/REI-F08-PAIRED/verify_candidate.py": "5acf786b87173b12d31e5efcf2114bf647b20f5f7fea763e6cf188854a55a5d7",
  "configs/rei_fastest_v1/science_scenario_v1.json": "c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
  "rust/rei_microphysics/src/lift.rs": "632474da40f075051f77ed618b65af13fba133ea6bbee6e49325aeb2578d1871",
  "rust/rei_microphysics/src/atomic_provider.rs": "b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3",
  "rust/rei_microphysics/src/bianchi_i.rs": "4d7ec027e6074e37d355228c557cdfce54d5bb1da3657e062a556922d6c21f9a",
  "rust/rei_microphysics/src/ft03_controlled.rs": "61e11471482bb49d99e5d0eb79504d3f67538fbe6361653a0462d1abb0b672db",
  "rust/rei_microphysics/src/ft03_rates.rs": "1a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f",
  "rust/rei_microphysics/src/angular_photons.rs": "8da6478182f70b285e7456490469d7a7708c969d200ab93d4d468f34c0fe82db",
  "rust/rei_microphysics/src/interval_ad.rs": "b14a16a24ba55d1d915fc890348bbafccf3c9df4566c04bbf06d38cdac2ef2dd",
  "rust/rei_microphysics/src/microstep.rs": "e03cc1512cdd2b60735b1ab655c8e6657423c18ee4ad55ca1d30f24ad4974e53",
  "rust/rei_microphysics/src/ft03_interval.rs": "886580a810b8ec29c8f0b6199c0e35d82fde1f46d984a5f8f1da304326a42a42",
  "rust/rei_microphysics/src/homogeneous_rates.rs": "50000b7cd7b1f7c9536cfe92a1f932add545bb951cc32b8a63c4affecfca3f47",
  "rust/rei_microphysics/src/coupled_primary.rs": "85434c2c6257ce197c4c928d01c2095f83fc3cbac1c421e367c95fdafae46585",
  "rust/rei_microphysics/src/coverage.rs": "0c542eaf42cd8ece217a2f02cc7fbb500f0bea8b983c1f18d44c96d0aea050c1",
  "rust/rei_microphysics/src/thermal.rs": "6d7be31934bb33a46c0911d28b62e34d22027e08a8a1945c5d7d32bf32f79b8a",
  "rust/rei_microphysics/src/he_rct.rs": "e2e461d17c47f207108dc0b4f28b9a551ffd61f4fb1a061e35c94a2a5ad12173",
  "rust/rei_microphysics/src/hydrogen_step.rs": "d3a4515dd2cb4e723095db6c750531acc3999fe0d5fa856707e520ec93056fb6",
  "rust/rei_microphysics/src/hhe_events.rs": "c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290",
  "rust/rei_microphysics/src/lib.rs": "10d4a4d948cf014b47a0da862a99875979332b562c8a34a8064bb74b36d2ec24",
  "rust/rei_microphysics/src/interval_math.rs": "e4639a4386feee536dbe7e7ffb1260f26fa00697b6b05477083c182ddf03de18",
  "rust/rei_microphysics/src/joint_affine.rs": "5782ec4a2fdb8885af4056dca26e60bb31b585a7ce5de0c18cccbb143ae5f8b3",
  "rust/rei_microphysics/src/group_rates.rs": "393786f3c473d98dbf57752967ba63cf07f055dfff9027a1d00770d2ef73a6a4",
  "rust/rei_microphysics/src/flrw_three_equations.rs": "52b165f036bab9d008989d41889972245bf7cea4e2a64a07e561982dc90cfbf0",
  "rust/rei_microphysics/src/adaptive_history.rs": "88f85b00e8a4cb487c98c1a2e473a4c356c5558f5df0154502c4afcf585d5d73"
}
"########),
        ("paired_runtime",include_str!("../src/paired_runtime.rs")),
        ("paired_history",include_str!("paired_history.rs")),
        ("adaptive_history",include_str!("../src/adaptive_history.rs")),
        ("angular_photons",include_str!("../src/angular_photons.rs")),
        ("bianchi_i",include_str!("../src/bianchi_i.rs")),
        ("coupled_primary",include_str!("../src/coupled_primary.rs")),
        ("coverage",include_str!("../src/coverage.rs")),
        ("flrw_three_equations",include_str!("../src/flrw_three_equations.rs")),
        ("atomic_provider",include_str!("../src/atomic_provider.rs")),
        ("ft03_controlled",include_str!("../src/ft03_controlled.rs")),
        ("ft03_rates",include_str!("../src/ft03_rates.rs")),
        ("ft03_interval",include_str!("../src/ft03_interval.rs")),
        ("group_rates",include_str!("../src/group_rates.rs")),
        ("he_rct",include_str!("../src/he_rct.rs")),
        ("hydrogen_step",include_str!("../src/hydrogen_step.rs")),
        ("interval_math",include_str!("../src/interval_math.rs")),
        ("interval_ad",include_str!("../src/interval_ad.rs")),
        ("joint_affine",include_str!("../src/joint_affine.rs")),
        ("lift",include_str!("../src/lift.rs")),
        ("microstep",include_str!("../src/microstep.rs")),
        ("hhe_events",include_str!("../src/hhe_events.rs")),
        ("homogeneous_rates",include_str!("../src/homogeneous_rates.rs")),
        ("thermal",include_str!("../src/thermal.rs")),
        ("lib",include_str!("../src/lib.rs")),
    ];
    let mut out=Vec::new();for (name,s) in pieces {out.extend_from_slice(&(name.len() as u64).to_le_bytes());out.extend_from_slice(name.as_bytes());out.extend_from_slice(&(s.len() as u64).to_le_bytes());out.extend_from_slice(s.as_bytes());}out
}
fn sync_replace(path:&Path,bytes:&[u8])->io::Result<()> {
    let tmp=path.with_extension("tmp");
    {let mut file=File::create(&tmp)?;file.write_all(bytes)?;file.sync_all()?;}
    fs::rename(&tmp,path)?;File::open(path.parent().ok_or_else(||error("path parent"))?)?.sync_all()?;Ok(())
}
// One pending transaction contains the already computed result and its exact raw
// record. Resume completes these durable bytes; it never recomputes an outcome.
fn commit_transaction(dir:&Path,file:&mut File,cp:&Path,raw:&str,next:&str)->io::Result<()> {
    let mut bundle=(raw.len() as u64).to_le_bytes().to_vec();bundle.extend_from_slice(raw.as_bytes());bundle.extend_from_slice(next.as_bytes());
    let pending=dir.join("pending.transaction");sync_replace(&pending,&bundle)?;
    file.write_all(raw.as_bytes())?;file.sync_all()?;sync_replace(cp,next.as_bytes())?;
    fs::remove_file(pending)?;File::open(dir)?.sync_all()?;Ok(())
}
fn reconcile_transaction(dir:&Path,cp:&Path,log:&Path)->io::Result<()> {
    let pending=dir.join("pending.transaction");if !pending.exists(){return Ok(());}
    let bytes=fs::read(&pending)?;if bytes.len()<8{return Err(error("short pending transaction"));}
    let n=u64::from_le_bytes(bytes[..8].try_into().unwrap()) as usize;if n>bytes.len()-8{return Err(error("pending length"));}
    let raw=&bytes[8..8+n];let checkpoint=&bytes[8+n..];let text=std::str::from_utf8(checkpoint).map_err(|_|error("pending checkpoint encoding"))?;
    let v=text.lines().next().ok_or_else(||error("pending checkpoint"))?.split_whitespace().collect::<Vec<_>>();
    let end:u64=v.get(7).ok_or_else(||error("pending offset"))?.parse().map_err(|_|error("pending offset"))?;
    let base=end.checked_sub(n as u64).ok_or_else(||error("pending offset range"))?;
    let current=fs::read(log)?;if (current.len() as u64)<base || (current.len() as u64)>end || current[base as usize..]!=raw[..current.len()-base as usize]{return Err(error("durable pending suffix differs; evidence retained"));}
    let mut file=OpenOptions::new().append(true).open(log)?;file.write_all(&raw[current.len()-base as usize..])?;file.sync_all()?;
    sync_replace(cp,checkpoint)?;fs::remove_file(pending)?;File::open(dir)?.sync_all()?;Ok(())
}
#[derive(Clone,Copy)]struct Spec{label:&'static str,dt:f64,m:usize,mu:usize,phi:usize}
const SPECS:[Spec;7]=[
    Spec{label:"T0",dt:1.25e9,m:8,mu:8,phi:16},
    Spec{label:"T1",dt:6.25e8,m:8,mu:8,phi:16},
    Spec{label:"T2",dt:3.125e8,m:8,mu:8,phi:16},
    Spec{label:"S0",dt:6.25e8,m:4,mu:8,phi:16},
    Spec{label:"S2",dt:6.25e8,m:16,mu:8,phi:16},
    Spec{label:"A0",dt:6.25e8,m:8,mu:4,phi:8},
    Spec{label:"A2",dt:6.25e8,m:8,mu:16,phi:32},
];
fn h(label:&str)->[f64;3]{match label {"FLRW"|"EPS0"=>[1e-14;3],"BI"=>[1.01e-14,0.99e-14,1e-14],"EPS_HALF"=>[1.005e-14,0.995e-14,1e-14],_=>unreachable!()}}
fn checkpoint(c:&PairedConfig,s:&PairedState,accepted:usize,rejected:usize,dt:f64,offset:u64,metrics:[f64;3])->String{
    let mut out=format!("REI_F08_PAIRED_CHECKPOINT_V2 {} {} {} {} {} {} {} {} {} {}\n",c.spectral_subdivisions,c.n_mu,c.n_phi,accepted,rejected,b(dt),offset,b(metrics[0]),b(metrics[1]),b(metrics[2]));
    let g=&s.gas;
    for x in [s.time_s,g.fractions[0],g.fractions[1],g.fractions[2],g.w_ev_per_h,g.escape_ev_per_h,s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h]{out.push_str(&b(x));out.push(' ');}out.push('\n');
    for x in s.ledger_comp{out.push_str(&b(x));out.push(' ');}out.push_str(&b(s.energy_comp));out.push('\n');
    for z in &s.gas_box {out.push_str(&b(z.lo));out.push(' ');out.push_str(&b(z.hi));out.push(' ');}out.push('\n');
    out.push_str(&format!("{}\n",s.photons.len()));
    for (x,z) in s.photons.iter().zip(&s.photon_boxes){out.push_str(&b(*x));out.push(' ');out.push_str(&b(z.lo));out.push(' ');out.push_str(&b(z.hi));out.push('\n');}
    out.push_str(&format!("{}\n",s.lower_guard_n.len()));
    for d in 0..s.lower_guard_n.len(){for x in [s.lower_guard_n[d],s.lower_guard_u[d],s.lower_guard_n_box[d].lo,s.lower_guard_n_box[d].hi,s.lower_guard_u_box[d].lo,s.lower_guard_u_box[d].hi]{out.push_str(&b(x));out.push(' ');}out.push('\n');}
    out
}
fn read_checkpoint(path:&Path,c:&PairedConfig)->io::Result<(PairedState,usize,usize,f64,u64,[f64;3])>{
    let text=fs::read_to_string(path)?;let mut lines=text.lines();let first=lines.next().ok_or_else(||error("empty checkpoint"))?;let v=first.split_whitespace().collect::<Vec<_>>();
    if v.len()!=11 || v[0]!="REI_F08_PAIRED_CHECKPOINT_V2" || v[1].parse::<usize>().ok()!=Some(c.spectral_subdivisions) || v[2].parse::<usize>().ok()!=Some(c.n_mu) || v[3].parse::<usize>().ok()!=Some(c.n_phi){return Err(error("checkpoint identity"));}
    let accepted=v[4].parse().map_err(|_|error("accepted"))?;let rejected=v[5].parse().map_err(|_|error("rejected"))?;let dt=f(v[6])?;let offset=v[7].parse().map_err(|_|error("offset"))?;let metrics=[f(v[8])?,f(v[9])?,f(v[10])?];
    let x=lines.next().ok_or_else(||error("gas"))?.split_whitespace().map(f).collect::<io::Result<Vec<_>>>()?;if x.len()!=11{return Err(error("gas length"));}
    let comp=lines.next().ok_or_else(||error("ledger compensation"))?.split_whitespace().map(f).collect::<io::Result<Vec<_>>>()?;if comp.len()!=6{return Err(error("ledger compensation length"));}
    let z=lines.next().ok_or_else(||error("gas box"))?.split_whitespace().map(f).collect::<io::Result<Vec<_>>>()?;if z.len()!=8{return Err(error("gas box length"));}
    let n:usize=lines.next().ok_or_else(||error("photon length"))?.parse().map_err(|_|error("photon length"))?;
    let nodes=energy_nodes(c).map_err(ioerr)?;if n!=nodes.len()*c.n_mu*c.n_phi{return Err(error("photon grid length"));}
    let mut photons=Vec::with_capacity(n);let mut boxes=Vec::with_capacity(n);
    for _ in 0..n {let row=lines.next().ok_or_else(||error("photon row"))?.split_whitespace().map(f).collect::<io::Result<Vec<_>>>()?;if row.len()!=3{return Err(error("photon row length"));}photons.push(row[0]);boxes.push(Interval::new(row[1],row[2]).map_err(|_|error("photon box"))?);}
    let ng:usize=lines.next().ok_or_else(||error("guard length"))?.parse().map_err(|_|error("guard length"))?;
    if ng!=c.n_mu*c.n_phi{return Err(error("guard grid length"));}
    let mut guard_n=Vec::with_capacity(ng);let mut guard_u=Vec::with_capacity(ng);let mut guard_nb=Vec::with_capacity(ng);let mut guard_ub=Vec::with_capacity(ng);
    for _ in 0..ng{let row=lines.next().ok_or_else(||error("guard row"))?.split_whitespace().map(f).collect::<io::Result<Vec<_>>>()?;if row.len()!=6{return Err(error("guard row length"));}guard_n.push(row[0]);guard_u.push(row[1]);guard_nb.push(Interval::new(row[2],row[3]).map_err(|_|error("guard N box"))?);guard_ub.push(Interval::new(row[4],row[5]).map_err(|_|error("guard U box"))?);}
    if lines.next().is_some(){return Err(error("checkpoint suffix"));}
    let gas=PrimaryState{fractions:[x[1],x[2],x[3]],w_ev_per_h:x[4],escape_ev_per_h:x[5],packets:(0..nodes.len()).filter_map(|k|{let n=(0..c.n_mu*c.n_phi).map(|d|photons[d*nodes.len()+k]).sum::<f64>();if n>0.0{Some(PrimaryPacket{energy_ev:nodes[k],per_h:n})}else{None}}).collect()};
    let state=PairedState{time_s:x[0],gas,gas_box:[Interval::new(z[0],z[1]),Interval::new(z[2],z[3]),Interval::new(z[4],z[5]),Interval::new(z[6],z[7])].map(|q|q.map_err(|_|error("gas box"))).into_iter().collect::<io::Result<Vec<_>>>()?.try_into().map_err(|_|error("gas box"))?,photons,photon_boxes:boxes,lower_guard_n:guard_n,lower_guard_u:guard_u,lower_guard_n_box:guard_nb,lower_guard_u_box:guard_ub,redshift_work_ev_per_h:x[6],thermal_work_ev_per_h:x[7],source_photons_per_h:x[8],source_energy_ev_per_h:x[9],absorbed_photons_per_h:x[10],ledger_comp:[comp[0],comp[1],comp[2],comp[3],comp[4]],energy_comp:comp[5]};
    Ok((state,accepted,rejected,dt,offset,metrics))
}
fn gamma(s:&PairedState,c:&PairedConfig,h:[f64;3])->io::Result<[f64;3]>{
    let nodes=energy_nodes(c).map_err(ioerr)?;let provider=AtomicProvider::reference();let nh=1e-4*(-h.iter().sum::<f64>()*s.time_s).exp();let mut a=[0.0;3];
    for k in 0..nodes.len(){let n=(0..c.n_mu*c.n_phi).map(|d|s.photons[d*nodes.len()+k]).sum::<f64>();
        for (j,absorber) in [Absorber::HI,Absorber::HeI,Absorber::HeII].iter().enumerate(){a[j]+=29979245800.0*nh*n*provider.cross_section(*absorber,nodes[k]).map_err(ioerr)?;}}
    Ok(a)
}
fn cumulative(s:&PairedState,c:&PairedConfig)->io::Result<[f64;2]>{
 let nodes=energy_nodes(c).map_err(ioerr)?;let n=s.photons.iter().sum::<f64>()+s.lower_guard_n.iter().sum::<f64>();
 let u=s.photons.iter().enumerate().map(|(i,x)|x*nodes[i%nodes.len()]).sum::<f64>()+s.lower_guard_u.iter().sum::<f64>();
 let energy=|x:&PrimaryState|x.w_ev_per_h+13.598434599702*x.fractions[0]+0.083*(24.587389011*x.fractions[1]+(24.587389011+54.41776)*x.fractions[2])+x.escape_ev_per_h;
 let init=energy(&paired_initial(c).map_err(ioerr)?.gas)+0.05*13.7;
 Ok([(n+s.absorbed_photons_per_h-s.source_photons_per_h-0.05).abs()/(0.05+s.source_photons_per_h),(energy(&s.gas)+u+s.redshift_work_ev_per_h+s.thermal_work_ev_per_h-s.source_energy_ev_per_h-init).abs()/(init+s.source_energy_ev_per_h)])
}
fn summary_json(s:&PairedState,c:&PairedConfig,h:[f64;3],bound:f64,width:f64,ledger:f64)->io::Result<String>{
    let nodes=energy_nodes(c).map_err(ioerr)?;let guard_n=s.lower_guard_n.iter().sum::<f64>();let guard_u=s.lower_guard_u.iter().sum::<f64>();
    let n=s.photons.iter().sum::<f64>()+guard_n;let u=s.photons.iter().enumerate().map(|(i,x)|x*nodes[i%nodes.len()]).sum::<f64>()+guard_u;let g=gamma(s,c,h)?;
    let particles=1.0+0.083+s.gas.fractions[0]+0.083*(s.gas.fractions[1]+2.0*s.gas.fractions[2]);let t=2.0*s.gas.w_ev_per_h*1.602176634e-12/(3.0*1.380649e-16*particles);
    let mut out=format!("\"time_s\":{:.17e},\"fractions\":[{:.17e},{:.17e},{:.17e}],\"temperature_K\":{:.17e},\"photon_n\":{:.17e},\"photon_u_ev_per_h\":{:.17e},\"lower_guard_n\":{:.17e},\"lower_guard_u\":{:.17e},\"gamma_per_s\":[{:.17e},{:.17e},{:.17e}],\"escape_ev_per_h\":{:.17e},\"redshift_work_ev_per_h\":{:.17e},\"thermal_work_ev_per_h\":{:.17e},\"source_n\":{:.17e},\"source_u\":{:.17e},\"absorbed_n\":{:.17e},\"local_bound\":{:.17e},\"public_width\":{:.17e},\"ledger\":{:.17e}",s.time_s,s.gas.fractions[0],s.gas.fractions[1],s.gas.fractions[2],t,n,u,guard_n,guard_u,g[0],g[1],g[2],s.gas.escape_ev_per_h,s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h,bound,width,ledger);
    out.push_str(&format!(",\"w_ev_per_h\":{:.17e},\"gas_parent\":[[{:.17e},{:.17e}],[{:.17e},{:.17e}],[{:.17e},{:.17e}],[{:.17e},{:.17e}]]",s.gas.w_ev_per_h,s.gas_box[0].lo,s.gas_box[0].hi,s.gas_box[1].lo,s.gas_box[1].hi,s.gas_box[2].lo,s.gas_box[2].hi,s.gas_box[3].lo,s.gas_box[3].hi));
    let cumulative=cumulative(s,c)?;out.push_str(&format!(",\"cumulative_n_residual\":{:.17e},\"cumulative_u_residual\":{:.17e}",cumulative[0],cumulative[1]));
    Ok(out)
}
fn run_one(root:&Path,spec:Spec,label:&str,limit:Option<usize>,resume:bool)->io::Result<()> {
    let dir=root.join(format!("{}_{}",spec.label,label));let continuing=resume && dir.is_dir();
    if !continuing {fs::create_dir(&dir)?;}
    let c=PairedConfig{spectral_subdivisions:spec.m,n_mu:spec.mu,n_phi:spec.phi};let nodes=energy_nodes(&c).map_err(ioerr)?;let angles=(0..c.n_mu*c.n_phi).map(|d|{let q=qhat(&c,d);format!("[{:.17e},{:.17e},{:.17e}]",q[0],q[1],q[2])}).collect::<Vec<_>>();
    let header=format!("{{\"schema\":\"REI_F08_PAIRED_RAW_V1\",\"spec\":\"{}\",\"geometry\":\"{}\",\"dt_initial\":{:.17e},\"energy_nodes\":[{}],\"qhat\":[{}],\"claim\":\"HOLD\"}}\n",spec.label,label,spec.dt,nodes.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(","),angles.join(","));
    let hp=dir.join("header.jsonl");if continuing {if fs::read(&hp)?!=header.as_bytes(){return Err(error("run header identity"));}}else{sync_replace(&hp,header.as_bytes())?;}
    let cp=dir.join("checkpoint.dat");let log=dir.join("trials.jsonl");if continuing{reconcile_transaction(&dir,&cp,&log)?;}let (mut state,mut accepted,mut rejected,mut dt,offset,mut metrics)=if continuing{read_checkpoint(&cp,&c)?}else{(paired_initial(&c).map_err(ioerr)?,0,0,spec.dt,0,[0.0;3])};
    if !continuing {sync_replace(&cp,checkpoint(&c,&state,accepted,rejected,dt,0,metrics).as_bytes())?;File::create(&log)?.sync_all()?;}
    let mut file=OpenOptions::new().read(true).write(true).open(&log)?;if file.metadata()?.len()!=offset{return Err(error("durable log suffix requires reconciliation; evidence retained"));}use std::io::Seek;file.seek(std::io::SeekFrom::End(0))?;
    while state.time_s<1e13 && limit.map(|x|accepted<x).unwrap_or(true){let remaining=1e13-state.time_s;let attempt=dt.min(remaining);if attempt<1000.0{return Err(error("minimum trial interval"));}
        match paired_trial(&c,h(label),&state,attempt){
            Ok(trial)=>{let raw=format!("{{\"accepted\":true,\"dt_s\":{:.17e},\"accepted_index\":{}, {},\"audits\":[{}]}}\n",attempt,accepted+1,summary_json(&trial.state,&c,h(label),trial.local_bound,trial.public_width,trial.max_ledger)?,trial.audits.join(","));metrics=[metrics[0].max(trial.local_bound),metrics[1].max(trial.public_width),metrics[2].max(trial.max_ledger)];state=trial.state;accepted+=1;let end=file.metadata()?.len()+raw.len() as u64;commit_transaction(&dir,&mut file,&cp,&raw,&checkpoint(&c,&state,accepted,rejected,dt,end,metrics))?;if accepted%100==0{eprintln!("{} {} accepted={} t={:.17e}",spec.label,label,accepted,state.time_s);}}
            Err(e)=>{let raw=format!("{{\"accepted\":false,\"time_s\":{:.17e},\"dt_s\":{:.17e},\"reason\":\"{}\"}}\n",state.time_s,attempt,e.code());rejected+=1;dt=attempt/2.0;let end=file.metadata()?.len()+raw.len() as u64;commit_transaction(&dir,&mut file,&cp,&raw,&checkpoint(&c,&state,accepted,rejected,dt,end,metrics))?;if dt<1000.0{return Err(error("minimum trial interval after rejection"));}}
        }
    }
    let status=if state.time_s>=1e13{"COMPLETE_HISTORY_CANDIDATE"}else{"PILOT_ONLY"};let summary=format!("{{\"status\":\"{}\",\"spec\":\"{}\",\"geometry\":\"{}\",\"accepted\":{},\"rejected\":{}, {},\"scientific_admission\":\"HOLD\"}}\n",status,spec.label,label,accepted,rejected,summary_json(&state,&c,h(label),metrics[0],metrics[1],metrics[2])?);sync_replace(&dir.join("summary.json"),summary.as_bytes())?;
    let csv=format!("spec,geometry,status,accepted,rejected,time_s,xHII,xHeII,xHeIII\n{},{},{},{},{},{:.17e},{:.17e},{:.17e},{:.17e}\n",spec.label,label,status,accepted,rejected,state.time_s,state.gas.fractions[0],state.gas.fractions[1],state.gas.fractions[2]);sync_replace(&dir.join("summary.csv"),csv.as_bytes())?;if state.time_s>=1e13 && cumulative(&state,&c)?.iter().any(|v|*v>1e-12){return Err(error("final cumulative ledger gate; complete raw candidate retained"));}Ok(())
}
fn run()->io::Result<()> {let mut scenario=PathBuf::from("configs/rei_fastest_v1/science_scenario_v1.json");let mut output=None;let mut full=false;let mut resume=false;let mut selected:Option<(String,String)>=None;let args=env::args().skip(1).collect::<Vec<_>>();let mut i=0;
    while i<args.len(){match args[i].as_str(){"--scenario"=>{i+=1;scenario=PathBuf::from(args.get(i).ok_or_else(||error("missing scenario path"))?);},"--output"=>{i+=1;output=Some(PathBuf::from(args.get(i).ok_or_else(||error("missing output path"))?));},"--only"=>{i+=1;let (spec,geometry)=args.get(i).ok_or_else(||error("missing --only value"))?.split_once('_').ok_or_else(||error("--only needs SPEC_GEOMETRY"))?;if !SPECS.iter().any(|s|s.label==spec) || !["FLRW","BI","EPS_HALF"].contains(&geometry) || (geometry=="EPS_HALF" && spec!="T0"){return Err(error("unknown selected run"));}selected=Some((spec.to_string(),geometry.to_string()));},"--pilot"=>full=false,"--full"=>full=true,"--resume"=>resume=true,_=>return Err(error("unknown argument"))}i+=1;}
    if fs::read(&scenario)?!=SCENARIO.as_bytes(){return Err(error("scenario bytes differ from frozen input"));}
    let root=output.ok_or_else(||error("missing --output"))?;
    if resume {if !root.is_dir(){return Err(error("missing output directory"));}if fs::read(root.join("source_identity.bin"))?!=source_bytes(){return Err(error("source identity differs"));}let mode=fs::read_to_string(root.join("mode.txt"))?;if mode.trim()!=if full{"full"}else{"pilot"}{return Err(error("mode identity differs"));}}
    else {fs::create_dir(&root)?;sync_replace(&root.join("source_identity.bin"),&source_bytes())?;sync_replace(&root.join("mode.txt"),if full{b"full\n"}else{b"pilot\n"})?;}
    let specs=if full || selected.is_some() {SPECS.to_vec()}else{vec![SPECS[3]]};
    for spec in specs {
     if let Some((ref name,ref label))=selected {if spec.label==name{run_one(&root,spec,label,if full{None}else{Some(3)},resume)?;}continue;}
     for label in ["FLRW","BI"] {run_one(&root,spec,label,if full{None}else{Some(3)},resume)?;}
     if full && spec.label=="T0"{run_one(&root,spec,"EPS_HALF",None,resume)?;}
    }
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("paired_history: {e}");std::process::exit(2);}}

#[cfg(test)]
mod recovery_tests {
 use super::*;
 #[test]
 fn durable_suffix_is_completed_without_replay() {
  for written in [0usize,7,26] {
   let dir=std::env::temp_dir().join(format!("rei-f08-recovery-{}-{}",std::process::id(),written));fs::create_dir(&dir).unwrap();
   let raw=b"{\"accepted\":false,\"dt\":1}\n";let n=written.min(raw.len());let c=PairedConfig{spectral_subdivisions:1,n_mu:1,n_phi:1};let state=paired_initial(&c).unwrap();let cp=dir.join("checkpoint.dat");let log=dir.join("trials.jsonl");
   let before=checkpoint(&c,&state,0,0,1e9,0,[0.;3]);let after=checkpoint(&c,&state,0,1,5e8,raw.len() as u64,[0.;3]);sync_replace(&cp,before.as_bytes()).unwrap();sync_replace(&log,&raw[..n]).unwrap();
   let mut bundle=(raw.len() as u64).to_le_bytes().to_vec();bundle.extend_from_slice(raw);bundle.extend_from_slice(after.as_bytes());sync_replace(&dir.join("pending.transaction"),&bundle).unwrap();
   reconcile_transaction(&dir,&cp,&log).unwrap();assert_eq!(fs::read(&log).unwrap(),raw);assert_eq!(fs::read(&cp).unwrap(),after.as_bytes());assert!(!dir.join("pending.transaction").exists());
   reconcile_transaction(&dir,&cp,&log).unwrap();assert_eq!(fs::read(&log).unwrap(),raw);fs::remove_dir_all(dir).unwrap();
  }
 }
 #[test]
 fn unknown_durable_suffix_is_preserved() {
  let dir=std::env::temp_dir().join(format!("rei-f08-unknown-suffix-{}",std::process::id()));fs::create_dir(&dir).unwrap();let log=dir.join("trials.jsonl");sync_replace(&log,b"durable unknown evidence\n").unwrap();
  reconcile_transaction(&dir,&dir.join("checkpoint.dat"),&log).unwrap();assert_eq!(fs::read(&log).unwrap(),b"durable unknown evidence\n");fs::remove_dir_all(dir).unwrap();
 }
}

#[cfg(test)] mod compensation_recovery_test {
 use super::*;
 #[test] fn nonzero_energy_roundoff_is_preserved() {
  let c=PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16};let mut state=paired_initial(&c).unwrap();state.energy_comp=-1.3877787807814457e-16;
  let dir=std::env::temp_dir().join(format!("rei-energy-comp-{}",std::process::id()));fs::create_dir(&dir).unwrap();let path=dir.join("checkpoint.dat");fs::write(&path,checkpoint(&c,&state,0,0,3.125e8,0,[0.;3])).unwrap();let (recovered,_,_,_,_,_)=read_checkpoint(&path,&c).unwrap();assert_eq!(recovered.energy_comp.to_bits(),state.energy_comp.to_bits());fs::remove_dir_all(dir).unwrap();
 }
}
