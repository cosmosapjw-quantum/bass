//! S6c: source-panel / energy-bin refinement against the exact original REI owner.
//! Angular rule and birth geometry are held fixed in the panel-bin block; a
//! separate block varies only the angular rule at a non-default panel count.
//! Owner files are compiled unchanged; only AxbiSource::new's public
//! cells_per_segment argument and CovariantTransport::new's n_energy vary.
#![forbid(unsafe_code)]
#[path="balance.rs"] mod balance;
#[path="balance_p24.rs"] mod balance_p24;
#[path="native_adapter.rs"] mod native_adapter;
use native_adapter::{Constraints, Declaration, inject_new_isotropic, p2, sum};
use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState};
use rei_microphysics::axbi_sources::{AxbiSource, SOURCE_ID};
use rei_microphysics::{AxisymmetricPoint, GeometrySnapshot};
use std::fs::OpenOptions;
use std::io::Write;

const AREF:f64=1.0/21.0;
const OWNER:&str="0e25846433170d0f420c4cda44a0bedbf02cd177";
const DT:f64=1e12;
type R<T>=Result<T,String>;
fn native<T>(r:Result<T,rei_microphysics::ForwardError>)->R<T>{r.map_err(|e|e.to_string())}
fn setup(nmu:usize,ne:usize,cps:usize,b:f64)->R<(AxbiSource,CovariantTransport,GeometrySnapshot,f64)> {
    let source=native(AxbiSource::new(1.88e-7,0.2,cps,nmu))?;
    let reference=native(GeometrySnapshot::new([AREF;3],[1e-16;3]))?;
    let transport=native(CovariantTransport::new(&source,reference,ne,0.01,5000.0))?;
    let now=native(native(AxisymmetricPoint::new(AREF*0.5_f64.exp(),b,1e-16,1e-18))?.snapshot())?;
    Ok((source,transport,now,21.0*(-0.5_f64).exp()-1.0))
}
fn new_birth(t:&CovariantTransport,s:&mut PhotonState,g:&GeometrySnapshot,z:f64)->R<native_adapter::BirthReceipt> {
    let rays=native(t.ray_geometry(g))?;
    let mu:Vec<f64>=rays.iter().map(|r|r.mu).collect();
    let prior:Vec<f64>=rays.iter().map(|r|r.angular_weight).collect();
    let w=balance_p24::project(&mu,&prior,3e-15).map(|r|r.weights).map_err(str::to_string)?;
    native(inject_new_isotropic(t,s,g,z,DT,Declaration::locally_isotropic_non_tilted(),Constraints::P2P4,&w))
}
fn future_stress(t:&CovariantTransport,s:&PhotonState,b:f64,d:f64)->R<f64> {
    let g=native(native(AxisymmetricPoint::new(AREF*0.5_f64.exp(),b+d,1e-16,1e-18))?.snapshot())?;
    let rays=native(t.ray_geometry(&g))?;let ne=t.n_energy();
    Ok(sum(s.energy_ref.iter().enumerate().map(|(k,u)|u*rays[k/ne].scale*p2(rays[k/ne].mu))))
}
fn row(block:&str,nmu:usize,ne:usize,cps:usize,b:f64)->R<String> {
    let (source,t,g,z)=setup(nmu,ne,cps,b)?;let mut birth=t.empty_state();
    let q=new_birth(&t,&mut birth,&g,z)?;native(t.validate_state(&birth))?;
    let (n,u)=native(t.inventory(&birth,&g))?;
    let mut stock=t.empty_state();
    native(t.add_delta(&mut stock,0,1.0,0.01))?;
    native(t.add_delta(&mut stock,nmu-1,40.0,0.005))?;
    let old=native(t.inventory(&stock,&g))?;
    let combined=new_birth(&t,&mut stock,&g,z)?;
    let after=native(t.inventory(&stock,&g))?;
    let rn=after.0-old.0-combined.added.added_photons_per_h;
    let ru=after.1-old.1-combined.added.added_energy_ev_per_h;
    let amount=native(source.at_redshift(z))?.per_h_s*DT;
    let source_mean=sum(source.spectral_cells.iter().map(|x|x.photon_fraction*x.energy_ev));
    let h=1e-5;
    let derivative=(future_stress(&t,&birth,b,h)?-future_stress(&t,&birth,b,-h)?)/(2.0*h*u);
    let analytic=-8.0/5.0-10.0/7.0*q.energy_moments[0]+36.0/35.0*q.energy_moments[1];
    Ok(format!(concat!("{{\"schema\":\"bass.angular.native.s6c.v1\",\"block\":\"{}\",\"mode\":\"P2P4\",",
        "\"n_mu\":{},\"n_energy\":{},\"cells_per_segment\":{},\"b_birth\":{:.17e},",
        "\"inventory_n\":{:.17e},\"inventory_u\":{:.17e},\"ledger_n_residual\":{:.17e},\"ledger_u_residual\":{:.17e},",
        "\"photon_vs_source_relative\":{:.17e},\"energy_vs_source_moment_relative\":{:.17e},",
        "\"source_mean_ev\":{:.17e},\"weight_p2\":{:.17e},\"weight_p4\":{:.17e},",
        "\"energy_p2\":{:.17e},\"energy_p4\":{:.17e},",
        "\"derivative_central\":{:.17e},\"derivative_legendre\":{:.17e},\"derivative_h\":{:.17e},",
        "\"min_weight\":{:.17e}}}"),
        block,nmu,ne,cps,b,n,u,rn,ru,n/amount-1.0,u/(amount*source_mean)-1.0,source_mean,
        q.weight_moments[0],q.weight_moments[1],q.energy_moments[0],q.energy_moments[1],
        derivative,analytic,h,q.min_weight))
}
fn run(output:&str)->R<usize> {
    let mut rows=Vec::new();
    for cps in [4,8,16,32,64] { for ne in [24,48,96,192] { rows.push(row("panel_bin",8,ne,cps,0.3)?); } }
    for nmu in [8,16,32] { for b in [-0.3,0.3] { rows.push(row("angular_cps64",nmu,96,64,b)?); } }
    let count=rows.len();let mut f=OpenOptions::new().write(true).create_new(true).open(output).map_err(|e|e.to_string())?;
    for r in rows {writeln!(f,"{r}").map_err(|e|e.to_string())?;}
    writeln!(f,"{{\"schema\":\"bass.angular.native.s6c.complete.v1\",\"rows\":{count},\"owner_commit\":\"{OWNER}\",\"source_id\":\"{SOURCE_ID}\",\"adapter_id\":\"{}\"}}",native_adapter::ADAPTER_ID).map_err(|e|e.to_string())?;
    f.flush().map_err(|e|e.to_string())?;Ok(count)
}
fn main(){let a:Vec<String>=std::env::args().collect();let r=if a.len()==2 {run(&a[1])}else{Err("USAGE spectral_probe OUTPUT.jsonl".into())};
    match r {Ok(n)=>println!("SPECTRAL_REFINEMENT_COMPLETE rows={n}"),Err(e)=>{eprintln!("SPECTRAL_REFINEMENT_FAIL:{e}");std::process::exit(3);}}}
