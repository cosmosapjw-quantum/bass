//! Stored finite rest-frame history only; no chemistry or reference integration.
use bianchi_rustcore::microphysics::visibility::{compare_opacity, integrate_rest_frame_sampled_visibility, ElectronState};
use std::io::{self, Read};
fn receive(y: &[f64]) -> Result<ElectronState, String> {
    if y.len()!=19 { return Err("STATE_WIDTH".into()); }
    if y.iter().any(|x|!x.is_finite()) || y[0]<=0. || y[1..15].iter().any(|x|*x<0.) { return Err("STATE_DOMAIN".into()); }
    for i in [1,4,5,6,7,8,9,10,12,13] { if y[i]!=0. { return Err(format!("UNSUPPORTED_SPECIES_{i}")); } }
    let nh=y[2]+y[3];
    if !nh.is_finite() || nh<=0. { return Err("HYDROGEN_DOMAIN".into()); }
    ElectronState::new(nh,y[11],y[3]/nh,0.,0.).map_err(|e|format!("{e:?}"))
}
fn emit(name:&str,v:&[f64]) { print!("{name}"); for x in v {print!(" {x:.17e}");} println!(); }
fn main()->Result<(),Box<dyn std::error::Error>> {
    let mut input=String::new(); io::stdin().read_to_string(&mut input)?;
    let mut lines=input.lines();
    let tail:f64=lines.next().ok_or("tail")?.parse()?;
    let edges:Vec<f64>=lines.next().ok_or("edges")?.split_whitespace().map(str::parse).collect::<Result<_,_>>()?;
    let samples:Vec<ElectronState>=lines.map(|s| {let y:Vec<f64>=s.split_whitespace().map(str::parse).collect::<Result<_,_>>().map_err(|e|format!("{e}"))?; receive(&y)}).collect::<Result<_,_>>()?;
    let r=integrate_rest_frame_sampled_visibility(&edges,&samples,tail).map_err(|e|format!("{e:?}"))?;
    emit("ne",&samples.iter().map(|s|s.number_density_m3()).collect::<Vec<_>>());
    emit("q",&r.edge_rates_s_inverse); emit("qbar",&r.cell_average_rates_s_inverse);
    emit("tau",&r.visibility.optical_depth); emit("survival",&r.visibility.survival); emit("mass",&r.visibility.interval_probability);
    let doubled:Vec<f64>=r.cell_average_rates_s_inverse.iter().map(|q|2.*q).collect();
    let c=compare_opacity(&edges,&r.cell_average_rates_s_inverse,&doubled).map_err(|e|format!("{e:?}"))?;
    emit("l1",&c.opacity_l1_tail); emit("survival_bound",&c.survival_error_bound); emit("mass_bound",&c.interval_probability_error_bound);
    Ok(())
}
#[cfg(test)] mod tests {
 use super::*;
 #[test] fn malformed_snapshot_guards() {
  let mut y=[0.;19]; y[0]=0.05; y[2]=100.; y[3]=1.; y[11]=8.; y[14]=1e-20;
  assert!(receive(&y).is_ok()); assert!(receive(&y[..18]).is_err());
  let mut z=y; z[4]=1.; assert!(receive(&z).is_err());
  z=y; z[14]=-1.; assert!(receive(&z).is_err());
  z=y; z[0]=f64::NAN; assert!(receive(&z).is_err());
  z=y; z[2]=0.; z[3]=0.; assert!(receive(&z).is_err());
 }
}
