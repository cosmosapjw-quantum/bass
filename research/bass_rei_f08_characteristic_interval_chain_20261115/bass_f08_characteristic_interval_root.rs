//! BASS-only driver: exact original Rust PrimaryBox interval propagation
//! across supplied source-born characteristic packets (point energy).
//! No changes to REI owner microphysics / root operator or acceptance gates.
#![forbid(unsafe_code)]
use std::{env,fs::File,io::{BufRead,BufReader,Write}};
use rei_microphysics::{Interval,StepControl};
use rei_microphysics::coupled_primary::{
    PrimaryPacket,PrimaryStage,PrimaryState,PrimaryBox,
    primary_stage_root,primary_stage_step_conservative
};
type E = Box<dyn std::error::Error>;
fn val(s:&str)->Result<f64,E>{
    let x:f64=s.parse()?;if !x.is_finite(){return Err("NONFINITE".into())}Ok(x)
}
fn ib(lo:&str,hi:&str)->Result<Interval,E>{
    Interval::new(val(lo)?,val(hi)?).map_err(|_|"BAD_INTERVAL".into())
}
fn s(x:f64)->String{format!("{x:.17e}")}
fn main()->Result<(),E>{
    let a:Vec<String>=env::args().collect();if a.len()!=3{return Err("ARGS INPUT OUTPUT".into())}
    let mut stage:Option<PrimaryStage>=None;
    let mut gas:Option<PrimaryState>=None;
    let mut dt=0_f64;
    let mut rates:Option<(f64,f64)>=None;
    let mut gb=Vec::new();let mut pb=Vec::new();let mut eb=Vec::new();
    for l in BufReader::new(File::open(&a[1])?).lines(){
        let l=l?;if l.is_empty()||l.starts_with('#'){continue}
        let f=l.split('|').collect::<Vec<_>>();
        match f[0]{
            "S"=>{
                if f.len()!=11 || gas.is_some(){return Err("STAGE_SCHEMA".into())}
                stage=Some(PrimaryStage{n_h_cm3:val(f[1])?,f_he:val(f[2])?,h_mean_per_s:val(f[3])?});
                dt=val(f[4])?;
                gas=Some(PrimaryState{
                    fractions:[val(f[5])?,val(f[6])?,val(f[7])?],
                    w_ev_per_h:val(f[8])?,escape_ev_per_h:val(f[9])?,packets:Vec::new()
                });let _t=val(f[10])?;
            },
            "H"=>{
                if f.len()!=3 || rates.is_some(){return Err("HUBBLE_RANGE_SCHEMA".into())}
                let hmin=val(f[1])?;let hmax=val(f[2])?;
                if hmin<0.||hmax<hmin{return Err("HUBBLE_RANGE_DOMAIN".into())}
                rates=Some((hmin,hmax));
            },
            "G"=>{
                if f.len()!=3 || gas.is_none()||gb.len()>=4{return Err("GAS_BOX_SCHEMA".into())}
                gb.push(ib(f[1],f[2])?);
            },
            "P"=>{
                if f.len()!=6 || gas.is_none()||gb.len()!=4||rates.is_none(){return Err("PHOTON_BOX_SCHEMA".into())}
                let age=val(f[1])?;
                let e=val(f[2])?;let n=val(f[3])?;
                if age<0. {return Err("BIRTH_AGE_DOMAIN".into())}
                if e<=0. || n<=0. {return Err("NONPOSITIVE_PHOTON".into())}
                let b=ib(f[4],f[5])?;
                let (hmin,hmax)=rates.unwrap();
                let negative_exp=|h:f64|->Result<Interval,E>{
                    Interval::point(-h).map_err(|_|"AGE_EXP_H")?
                        .mul(&Interval::point(age).map_err(|_|"AGE_EXP_T")?)
                        .map_err(|_|"AGE_EXP_MUL")?
                        .exp().map_err(|_|"AGE_EXP")?
                        .mul(&Interval::point(13.7).map_err(|_|"AGE_SOURCE")?)
                        .map_err(|_|"AGE_SOURCE_MUL".into())
                };
                let bounds=Interval::new(negative_exp(hmax)?.lo,negative_exp(hmin)?.hi)
                    .map_err(|_|"PHOTON_ENERGY_BOUND")?;
                if !(bounds.lo<=e && e<=bounds.hi) {return Err("CHARACTERISTIC_ENERGY_OUT_OF_SUPPORT".into())}
                eb.push(bounds);
                if b.lo<0.|| !(b.lo<=n&&n<=b.hi){return Err("PHOTON_PARENT_BOX_EXCLUDES_POINT".into())}
                gas.as_mut().unwrap().packets.push(PrimaryPacket{energy_ev:e,per_h:n});
                pb.push(b);
            },
            _=>return Err("UNKNOWN_LINE".into())
        }
    }
    let old=gas.ok_or("NO_GAS")?;
    let stage=stage.ok_or("NO_STAGE")?;
    if gb.len()!=4||pb.is_empty(){return Err("PARENT_BOX_INCOMPLETE".into())}
    let g=[gb[0],gb[1],gb[2],gb[3]];
    let point=[old.fractions[0],old.fractions[1],old.fractions[2],old.w_ev_per_h];
    if !(0..4).all(|j|g[j].lo<=point[j]&&point[j]<=g[j].hi){return Err("GAS_PARENT_BOX_EXCLUDES_POINT".into())}
    let parent=PrimaryBox{gas:g,photons:pb};
    let ctrl=StepControl{max_iterations:200,residual_tolerance:1e-15};
    let (step,_comp)=primary_stage_step_conservative(&stage,&old,dt,ctrl,0.)?;
    let root=primary_stage_root(&stage,&old,&parent,dt,ctrl)?;
    let gp=[step.state.fractions[0],step.state.fractions[1],
            step.state.fractions[2],step.state.w_ev_per_h];
    if !(0..4).all(|j|root.gas[j].lo<=gp[j]&&gp[j]<=root.gas[j].hi){
        return Err("ROOT_GAS_EXCLUDES_CONSERVATIVE".into())
    }
    if root.photons.len()!=step.state.packets.len()||root.photons.len()!=eb.len(){return Err("ROOT_PHOTON_LENGTH".into())}
    if !root.photons.iter().zip(&step.state.packets).all(|(b,p)|b.lo<=p.per_h&&p.per_h<=b.hi){
        return Err("ROOT_PHOTON_EXCLUDES_CONSERVATIVE".into())
    }
    let maxgw=root.gas.iter().map(|b|b.hi-b.lo).fold(0.0_f64,f64::max);
    let sum_pw=root.photons.iter().map(|b|b.hi-b.lo).sum::<f64>();
    let nend=step.state.packets.iter().map(|p|p.per_h).sum::<f64>();
    let photo=[0,1,2].map(|a|step.events.photo_per_h.iter().map(|r|r[a]).sum::<f64>());
    let absorbed: f64=photo.iter().sum();
    let temp=2.0*step.state.w_ev_per_h*1.602176634e-12/
        (3.0*1.380649e-16*(1.+stage.f_he+gp[0]+stage.f_he*(gp[1]+2.*gp[2])));
    if !(temp.is_finite() && temp>0.){return Err("TEMPERATURE_DOMAIN".into())}
    let mut out=File::create(&a[2])?;
    writeln!(out,"S|{}",[s(gp[0]),s(gp[1]),s(gp[2]),s(gp[3]),
       s(step.state.escape_ev_per_h),s(temp),s(nend),step.iterations.to_string(),
       s(step.residual),s(step.events.thermal_work_ev_per_h),s(absorbed),
       s(photo[0]),s(photo[1]),s(photo[2]),s(root.q),
       s(maxgw),s(sum_pw)].join("|"))?;
    for b in &root.gas {writeln!(out,"G|{}|{}",s(b.lo),s(b.hi))?;}
    for ((pkt,b),energy) in step.state.packets.iter().zip(&root.photons).zip(&eb){
        writeln!(out,"P|{}|{}|{}|{}|{}",s(pkt.per_h),s(b.lo),s(b.hi),s(energy.lo),s(energy.hi))?;
    }
    Ok(())
}
