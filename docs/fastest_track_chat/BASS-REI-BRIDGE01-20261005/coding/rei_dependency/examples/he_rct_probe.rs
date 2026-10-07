//! Line protocol documented in coding/INTERFACE.json; no third-party dependencies.
use std::io::{self, BufRead, Write};
use rei_microphysics::{hhe_rhs,HHeModel,HHeState,ForwardError};
use rei_microphysics::he_rct::*;
fn number(s:&str)->Result<f64,ForwardError>{s.parse().map_err(|_|ForwardError::InvalidInput("PROBE_NUMBER"))}
fn source(s:&str)->Result<RctSource,ForwardError>{match s {"KF96"=>Ok(RctSource::Kf96Nominal),"GM25"=>Ok(RctSource::Gm25Constant),_=>Err(ForwardError::InvalidInput("PROBE_SOURCE"))}}
fn array(v:&[f64])->String {format!("[{}]",v.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(","))}
fn optional(v:Option<f64>)->String {v.map(|x|format!("{:.17e}",x)).unwrap_or_else(||"null".into())}
fn fixture(v:&[&str])->Result<(HHeModel,HHeState,f64),ForwardError>{
    let mut m=HHeModel::controlled_fixture();m.n_h_cm3=number(v[0])?;m.n_he_cm3=number(v[1])?;
    let x=[number(v[2])?,number(v[3])?,number(v[4])?];let t=number(v[5])?;
    let ne=m.n_h_cm3*x[0]+m.n_he_cm3*(x[1]+2.0*x[2]);
    let s=HHeState{fractions:x,u_erg_cm3:1.5*m.kb_erg_k*t*(m.n_h_cm3+m.n_he_cm3+ne),photon_cm3:[2e-5,2e-6,2e-7],escaped_erg_cm3:0.0};
    Ok((m,s,t))
}
fn run(line:&str)->Result<String,ForwardError>{
    let v:Vec<_>=line.split_whitespace().collect();
    match v.first().copied(){
        Some("rate") if v.len()==3=>{
            let src=source(v[1])?;let t=number(v[2])?;
            let p=RctProvider::new(src,RctScenario::W82GroundStateCommonTemperatureZeroDrift,true)?;
            let k=p.coefficient_cm3_s(t)?;
            Ok(format!("{{\"ok\":true,\"kind\":\"rate\",\"source\":\"{}\",\"temperature_k\":{:.17e},\"k_cm3_s\":{:.17e},\"physical_admission\":false}}",v[1],t,k))
        },
        Some("off") if v.len()==7=>{
            let(m,s,_)=fixture(&v[1..])?;let o=combined_hhe_rhs(&m,&s,RctSelection::default())?;
            Ok(format!("{{\"ok\":true,\"kind\":\"off\",\"baseline_derivative\":{},\"combined_derivative\":{},\"baseline_escaped_energy_rate\":{:.17e},\"combined_escaped_energy_rate\":{:.17e}}}",array(&o.baseline.derivative),array(&o.combined.derivative),o.baseline.escaped_energy_rate,o.combined.escaped_energy_rate))
        },
        Some("ft03") if v.len()==4=>{
            let src=source(v[1])?;let fm=rei_microphysics::Ft03Model::controlled()?;
            let m=fm.gas;let mut s=fm.initial_state();let requested_t=number(v[2])?;
            let ne=m.electron_density(&s)?;
            s.u_erg_cm3=1.5*m.kb_erg_k*requested_t*(m.n_h_cm3+m.n_he_cm3+ne);
            let p=RctProvider::new(src,RctScenario::W82GroundStateCommonTemperatureZeroDrift,true)?;
            let base=rei_microphysics::ft03_rhs(&fm,&s)?;let e=p.events(&m,&s)?;
            let out=if v[3]=="COUNT"{None}else{Some(combined_ft03_rhs(&fm,&s,RctSelection::Escaping{provider:p,closure:EscapingMeanPhotonEnergy::research_input_ev(number(v[3])?)?})?)};
            let closed=out.and_then(|o|o.rct);
            Ok(format!(concat!("{{\"ok\":true,\"kind\":\"ft03\",\"source\":\"{}\",",
                "\"requested_temperature_k\":{:.17e},\"temperature_k\":{:.17e},\"n_h_cm3\":{:.17e},\"n_he_cm3\":{:.17e},\"fractions\":{},",
                "\"k_cm3_s\":{:.17e},\"n_hi_cm3\":{:.17e},\"n_heiii_cm3\":{:.17e},\"event_rate_cm3_s\":{:.17e},",
                "\"species_rate_cm3_s\":{},\"fraction_rate_s\":{},\"free_electron_rate_cm3_s\":{:.17e},\"emitted_photon_count_cm3_s\":{:.17e},",
                "\"q_ev\":{:.17e},\"ev_erg\":{:.17e},\"chemical_energy_rate_erg_cm3_s\":{:.17e},",
                "\"mean_escaped_photon_energy_ev\":{},\"thermal_energy_rate_erg_cm3_s\":{},\"escaped_energy_rate_erg_cm3_s\":{},",
                "\"baseline_derivative\":{},\"combined_derivative\":{},\"baseline_escaped_energy_rate\":{:.17e},\"combined_escaped_energy_rate\":{},",
                "\"closure_complete\":{},\"closure_input_origin\":{},\"physical_admission\":false,\"baseline_recombination_per_cm3_s\":{},\"baseline_collision_per_cm3_s\":{},\"baseline_dr_per_cm3_s\":{},\"combined_recombination_per_cm3_s\":{},\"combined_collision_per_cm3_s\":{},\"combined_dr_per_cm3_s\":{}}}"),
                v[1],requested_t,e.temperature_k,m.n_h_cm3,m.n_he_cm3,array(&s.fractions),e.coefficient_cm3_s,e.n_hi_cm3,e.n_heiii_cm3,e.event_rate_cm3_s,
                array(&e.species_rate_cm3_s),array(&e.fraction_rate_s),e.free_electron_rate_cm3_s,e.emitted_photon_count_cm3_s,
                e.q_ev,m.ev_erg,e.chemical_energy_rate_erg_cm3_s,
                optional(closed.map(|c|c.mean_escaped_photon_energy_ev)),optional(closed.map(|c|c.thermal_energy_rate_erg_cm3_s)),optional(closed.map(|c|c.escaped_energy_rate_erg_cm3_s)),
                array(&base.derivative),out.map(|o|array(&o.combined.derivative)).unwrap_or_else(||"null".into()),base.escaped_energy_rate,
                optional(out.map(|o|o.combined.escaped_energy_rate)),closed.is_some(),if closed.is_some(){"\"CALLER_SUPPLIED_NO_ATOMIC_MOMENT\""}else{"null"},array(&base.recombination_per_cm3_s),array(&base.collision_per_cm3_s),array(&base.dr_per_cm3_s),out.map(|o|array(&o.combined.recombination_per_cm3_s)).unwrap_or_else(||"null".into()),out.map(|o|array(&o.combined.collision_per_cm3_s)).unwrap_or_else(||"null".into()),out.map(|o|array(&o.combined.dr_per_cm3_s)).unwrap_or_else(||"null".into())))
        },
        Some("event") if v.len()==9=>{
            let src=source(v[1])?;let(m,s,requested_t)=fixture(&v[2..8])?;
            let p=RctProvider::new(src,RctScenario::W82GroundStateCommonTemperatureZeroDrift,true)?;
            let e=p.events(&m,&s)?;let base=hhe_rhs(&m,&s)?;
            let out=if v[8]=="COUNT"{None}else{Some(combined_hhe_rhs(&m,&s,RctSelection::Escaping{provider:p,closure:EscapingMeanPhotonEnergy::research_input_ev(number(v[8])?)?})?)};
            let closed=out.and_then(|o|o.rct);
            Ok(format!(concat!("{{\"ok\":true,\"kind\":\"event\",\"source\":\"{}\",",
                "\"requested_temperature_k\":{:.17e},\"temperature_k\":{:.17e},\"n_h_cm3\":{:.17e},\"n_he_cm3\":{:.17e},\"fractions\":{},",
                "\"k_cm3_s\":{:.17e},\"n_hi_cm3\":{:.17e},\"n_heiii_cm3\":{:.17e},\"event_rate_cm3_s\":{:.17e},",
                "\"species_rate_cm3_s\":{},\"fraction_rate_s\":{},\"free_electron_rate_cm3_s\":{:.17e},\"emitted_photon_count_cm3_s\":{:.17e},",
                "\"q_ev\":{:.17e},\"ev_erg\":{:.17e},\"chemical_energy_rate_erg_cm3_s\":{:.17e},",
                "\"mean_escaped_photon_energy_ev\":{},\"thermal_energy_rate_erg_cm3_s\":{},\"escaped_energy_rate_erg_cm3_s\":{},",
                "\"baseline_derivative\":{},\"combined_derivative\":{},\"baseline_escaped_energy_rate\":{:.17e},\"combined_escaped_energy_rate\":{},",
                "\"closure_complete\":{},\"closure_input_origin\":{},\"physical_admission\":false}}"),
                v[1],requested_t,e.temperature_k,m.n_h_cm3,m.n_he_cm3,array(&s.fractions),e.coefficient_cm3_s,e.n_hi_cm3,e.n_heiii_cm3,e.event_rate_cm3_s,
                array(&e.species_rate_cm3_s),array(&e.fraction_rate_s),e.free_electron_rate_cm3_s,e.emitted_photon_count_cm3_s,
                e.q_ev,m.ev_erg,e.chemical_energy_rate_erg_cm3_s,
                optional(closed.map(|c|c.mean_escaped_photon_energy_ev)),optional(closed.map(|c|c.thermal_energy_rate_erg_cm3_s)),optional(closed.map(|c|c.escaped_energy_rate_erg_cm3_s)),
                array(&base.derivative),out.map(|o|array(&o.combined.derivative)).unwrap_or_else(||"null".into()),base.escaped_energy_rate,
                optional(out.map(|o|o.combined.escaped_energy_rate)),closed.is_some(),if closed.is_some(){"\"CALLER_SUPPLIED_NO_ATOMIC_MOMENT\""}else{"null"}))
        },
        _=>Err(ForwardError::InvalidInput("PROBE_COMMAND")),
    }
}
fn main(){
    let stdin=io::stdin();let mut stdout=io::BufWriter::new(io::stdout());
    for line in stdin.lock().lines(){
        match line {Ok(line)=>{let response=run(&line).unwrap_or_else(|e|format!("{{\"ok\":false,\"error\":\"{}\"}}",e.code()));writeln!(stdout,"{}",response).unwrap();stdout.flush().unwrap();},Err(_)=>break}
    }
}
