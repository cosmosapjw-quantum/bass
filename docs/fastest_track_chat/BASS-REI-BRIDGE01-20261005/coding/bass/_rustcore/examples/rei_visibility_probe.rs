//! Actual REI snapshot and controlled-history probe; no fabricated histories.
use bianchi_rustcore::microphysics::{
    frame::MaterialFrame,
    rei_visibility::{electron_state_from_ft03, electron_state_from_hhe, integrate_rei_visibility, ReiOpacityCell},
    visibility::C_M_S,
};
use rei_microphysics::{ft03_adaptive_step, Ft03Model, HHeModel, HHeState, StepControl};
use std::io::{self, BufRead, Write};

fn fail(s: impl std::fmt::Debug) -> String {
    let text=format!("{s:?}").replace('\\',"\\\\").replace('"',"\\\"").replace('\n',"\\n");
    format!("{{\"ok\":false,\"error\":\"{text}\"}}")
}
fn snapshot(args: &[&str]) -> Result<String,String> {
    if args.len()!=18 { return Err("snapshot expects kind and 16 numbers".into()); }
    let v:Vec<f64>=args[2..].iter().map(|x|x.parse::<f64>()).collect::<Result<_,_>>().map_err(|e|format!("{e:?}"))?;
    let is_ft=match args[1] {"HHE"=>false,"FT03"=>true,_=>return Err("unknown source kind".into())};
    let mut g=if is_ft {Ft03Model::controlled().map_err(|e|format!("{e:?}"))?.gas}else{HHeModel::controlled_fixture()};
    g.n_h_cm3=v[0];g.n_he_cm3=v[1];
    let state=HHeState{fractions:[v[2],v[3],v[4]],u_erg_cm3:v[5],photon_cm3:[v[6],v[7],v[8]],escaped_erg_cm3:v[9]};
    let beta=[v[10],v[11],v[12]];let direction=[v[13],v[14],v[15]];
    let f=MaterialFrame::new(beta).map_err(|e|format!("{e:?}"))?;
    let e=if is_ft {electron_state_from_ft03(&Ft03Model{gas:g},&state)}else{electron_state_from_hhe(&g,&state)}.map_err(|e|format!("{e:?}"))?;
    let q=e.scattering_rate_per_normal_second(f,direction).map_err(|e|format!("{e:?}"))?;
    let d=f.doppler(direction).map_err(|e|format!("{e:?}"))?;
    let ne=g.electron_density(&state).map_err(|e|format!("{e:?}"))?;
    Ok(format!("{{\"ok\":true,\"kind\":\"{}\",\"n_h_cm3\":{:?},\"n_he_cm3\":{:?},\"fractions\":{:?},\"u_erg_cm3\":{:?},\"photon_cm3\":{:?},\"escaped_erg_cm3\":{:?},\"beta\":{:?},\"direction\":{:?},\"ne_source_cm3\":{:?},\"ne_m3\":{:?},\"doppler\":{:?},\"q_s_inverse\":{:?},\"physical_admission\":false}}",args[1],g.n_h_cm3,g.n_he_cm3,state.fractions,state.u_erg_cm3,state.photon_cm3,state.escaped_erg_cm3,beta,direction,ne,e.number_density_m3(),d,q))
}
fn history(args:&[&str])->Result<String,String>{
    if args.len()!=3{return Err("history expects n_intervals and observer_tail".into());}
    let n:usize=args[1].parse().map_err(|e|format!("{e:?}"))?;
    if n==0 || n>1_000_000{return Err("history interval count outside 1..1000000".into());}
    let tail:f64=args[2].parse().map_err(|e|format!("{e:?}"))?;
    if !tail.is_finite() || tail<0.0{return Err("invalid observer tail".into());}
    let model=Ft03Model::controlled().map_err(|e|format!("{e:?}"))?;
    if model.gas.c_cm_s != 100.0*C_M_S{return Err("fixture c mismatch".into());}
    let mut states=Vec::with_capacity(n+1);states.push(model.initial_state());
    let edges:Vec<f64>=(0..=n).map(|i|1e14*(i as f64)/(n as f64)).collect();
    let mut max_residual:f64=0.0;let mut max_local:f64=0.0;let mut iterations=0usize;
    for i in 0..n{
        let step=ft03_adaptive_step(&model,&states[i],edges[i+1]-edges[i],StepControl::default()).map_err(|e|format!("history cell {i}: {e:?}"))?;
        max_residual=max_residual.max(step.residual_norm);max_local=max_local.max(step.local_error);iterations+=step.iterations;
        states.push(step.state);
    }
    let frame=MaterialFrame::new([0.0;3]).map_err(|e|format!("{e:?}"))?;
    let cells:Vec<_>=states[..n].iter().map(|state|ReiOpacityCell::Ft03{model:&model,state,frame,e_normal:[1.0,0.0,0.0]}).collect();
    let schedule=integrate_rei_visibility(&edges,&cells,tail).map_err(|e|format!("{e:?}"))?;
    let state_json=states.iter().map(|s|{
        let temp=model.gas.temperature(s).map_err(|e|format!("{e:?}"))?;
        let ne=model.gas.electron_density(s).map_err(|e|format!("{e:?}"))?;
        let nm=electron_state_from_ft03(&model,s).map_err(|e|format!("{e:?}"))?.number_density_m3();
        Ok(format!("{{\"fractions\":{:?},\"u_erg_cm3\":{:?},\"photon_cm3\":{:?},\"escaped_erg_cm3\":{:?},\"temperature_k\":{:?},\"ne_cm3\":{:?},\"ne_m3\":{:?}}}",s.fractions,s.u_erg_cm3,s.photon_cm3,s.escaped_erg_cm3,temp,ne,nm))
    }).collect::<Result<Vec<_>,String>>()?.join(",");
    Ok(format!("{{\"ok\":true,\"kind\":\"FT03_CONTROLLED_NUMERICAL_COUPLING\",\"n_intervals\":{n},\"time_edges_seconds\":{edges:?},\"states\":[{state_json}],\"interval_rates_s_inverse\":{:?},\"optical_depth\":{:?},\"survival\":{:?},\"interval_probability\":{:?},\"observer_optical_depth\":{tail:?},\"max_step_residual\":{max_residual:?},\"max_step_local_error\":{max_local:?},\"total_iterations\":{iterations},\"c_constants_match\":true,\"physical_admission\":false,\"rct_enabled\":false,\"sampling\":\"left_endpoint\",\"frame\":\"rest\"}}",schedule.interval_rates_s_inverse,schedule.visibility.optical_depth,schedule.visibility.survival,schedule.visibility.interval_probability))
}
fn main(){
    let stdin=io::stdin();let mut stdout=io::BufWriter::new(io::stdout());
    for line in stdin.lock().lines(){
        let line=match line{Ok(v)=>v,Err(e)=>{writeln!(stdout,"{}",fail(e)).unwrap();break}};
        let args:Vec<_>=line.split_whitespace().collect();
        let result=match args.first().copied(){Some("snapshot")=>snapshot(&args),Some("history")=>history(&args),_=>Err("unknown command".into())};
        writeln!(stdout,"{}",result.unwrap_or_else(fail)).unwrap();stdout.flush().unwrap();
    }
}
