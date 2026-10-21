//! A bounded changed-adapter campaign against the exact original REI owner.
#![forbid(unsafe_code)]
#[path="balance.rs"] mod balance;
#[path="balance_p24.rs"] mod balance_p24;
mod native_adapter;
use native_adapter::{Constraints, Declaration, inject_new_isotropic, p2, p4, sum};
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
fn setup(nmu:usize,ne:usize,b:f64)->R<(AxbiSource,CovariantTransport,GeometrySnapshot,f64)> {
    let source=native(AxbiSource::new(1.88e-7,0.2,16,nmu))?;
    let reference=native(GeometrySnapshot::new([AREF;3],[1e-16;3]))?;
    let transport=native(CovariantTransport::new(&source,reference,ne,0.01,5000.0))?;
    let now=native(native(AxisymmetricPoint::new(AREF*0.5_f64.exp(),b,1e-16,1e-18))?.snapshot())?;
    Ok((source,transport,now,21.0*(-0.5_f64).exp()-1.0))
}
fn alpha(t:&CovariantTransport,g:&GeometrySnapshot,c:Constraints)->R<Vec<f64>> {
    let rays=native(t.ray_geometry(g))?;
    let mu:Vec<f64>=rays.iter().map(|r|r.mu).collect();
    let prior:Vec<f64>=rays.iter().map(|r|r.angular_weight).collect();
    match c {
        Constraints::P2=>balance::project(&mu,&prior,3e-15).map(|r|r.weights).map_err(str::to_string),
        Constraints::P2P4=>balance_p24::project(&mu,&prior,3e-15).map(|r|r.weights).map_err(str::to_string),
    }
}
fn new_birth(t:&CovariantTransport,s:&mut PhotonState,g:&GeometrySnapshot,z:f64,c:Constraints)
    ->R<native_adapter::BirthReceipt> {
    let w=alpha(t,g,c)?;
    native(inject_new_isotropic(t,s,g,z,DT,Declaration::locally_isotropic_non_tilted(),c,&w))
}
fn future_stress(t:&CovariantTransport,s:&PhotonState,b:f64,d:f64)->R<f64> {
    let g=native(native(AxisymmetricPoint::new(AREF*0.5_f64.exp(),b+d,1e-16,1e-18))?.snapshot())?;
    let rays=native(t.ray_geometry(&g))?;let ne=t.n_energy();
    Ok(sum(s.energy_ref.iter().enumerate().map(|(k,u)|u*rays[k/ne].scale*p2(rays[k/ne].mu))))
}
fn row(nmu:usize,ne:usize,b:f64,c:Constraints)->R<String> {
    let (source,t,g,z)=setup(nmu,ne,b)?;let mut birth=t.empty_state();
    let q=new_birth(&t,&mut birth,&g,z,c)?;native(t.validate_state(&birth))?;
    let (n,u)=native(t.inventory(&birth,&g))?;
    // Independent nonempty-stock ledger: do not compare an inventory to the
    // identical inventory used to create its receipt.
    let mut stock=t.empty_state();
    native(t.add_delta(&mut stock,0,1.0,0.01))?;
    native(t.add_delta(&mut stock,nmu-1,40.0,0.005))?;
    let old=native(t.inventory(&stock,&g))?;
    let combined=new_birth(&t,&mut stock,&g,z,c)?;
    let after=native(t.inventory(&stock,&g))?;
    let rn=after.0-old.0-combined.added.added_photons_per_h;
    let ru=after.1-old.1-combined.added.added_energy_ev_per_h;
    if rn.abs()>1e-11*q.added.added_photons_per_h.max(1e-30) ||
       ru.abs()>1e-11*q.added.added_energy_ev_per_h.max(1e-30) {
        return Err("ADAPTER_NATIVE_LEDGER".into());
    }
    let amount=native(source.at_redshift(z))?.per_h_s*DT;
    let source_mean=sum(source.spectral_cells.iter().map(|x|x.photon_fraction*x.energy_ev));
    let h=1e-5;
    let derivative=(future_stress(&t,&birth,b,h)?-future_stress(&t,&birth,b,-h)?)/(2.0*h*u);
    let analytic=-8.0/5.0-10.0/7.0*q.energy_moments[0]+36.0/35.0*q.energy_moments[1];
    let rays=native(t.ray_geometry(&g))?;
    let prior_p2=sum(rays.iter().map(|r|r.angular_weight*p2(r.mu)));
    let prior_p4=sum(rays.iter().map(|r|r.angular_weight*p4(r.mu)));
    let mode=if c==Constraints::P2 {"P2"}else{"P2P4"};
    Ok(format!(concat!("{{\"schema\":\"bass.angular.native.s3.v1\",\"mode\":\"{}\",",
        "\"n_mu\":{},\"n_energy\":{},\"b_birth\":{:.17e},\"source_panels_per_segment\":16,",
        "\"inventory_n\":{:.17e},\"inventory_u\":{:.17e},\"ledger_n_residual\":{:.17e},\"ledger_u_residual\":{:.17e},",
        "\"original_native_n\":{:.17e},\"original_native_u\":{:.17e},",
        "\"photon_vs_source_relative\":{:.17e},\"energy_vs_source_moment_relative\":{:.17e},",
        "\"prior_p2\":{:.17e},\"prior_p4\":{:.17e},",
        "\"weight_p2\":{:.17e},\"weight_p4\":{:.17e},",
        "\"photon_p2\":{:.17e},\"photon_p4\":{:.17e},",
        "\"energy_p2\":{:.17e},\"energy_p4\":{:.17e},",
        "\"derivative_central\":{:.17e},\"derivative_legendre\":{:.17e},\"derivative_h\":{:.17e},",
        "\"min_weight\":{:.17e},\"max_ray_rescaling\":{:.17e}}}"),
        mode,nmu,ne,b,n,u,rn,ru,q.original_ledger.added_photons_per_h,q.original_ledger.added_energy_ev_per_h,
        n/amount-1.0,u/(amount*source_mean)-1.0,prior_p2,prior_p4,
        q.weight_moments[0],q.weight_moments[1],q.photon_moments[0],q.photon_moments[1],
        q.energy_moments[0],q.energy_moments[1],derivative,analytic,h,q.min_weight,q.max_ray_rescaling))
}
fn run(output:&str)->R<usize> {
    let mut rows=Vec::new();
    for n in [8,16,32] { for b in [-0.3,0.0,0.3] { for c in [Constraints::P2,Constraints::P2P4] {
        rows.push(row(n,96,b,c)?);
    }}}
    // Fixed angular grid and source spectrum: only the fixed energy bin count
    // changes. These rows isolate the native finite-bin obligation.
    for c in [Constraints::P2,Constraints::P2P4] {rows.push(row(8,24,0.3,c)?);}
    let count=rows.len();let mut f=OpenOptions::new().write(true).create_new(true).open(output).map_err(|e|e.to_string())?;
    for r in rows {writeln!(f,"{r}").map_err(|e|e.to_string())?;}
    writeln!(f,"{{\"schema\":\"bass.angular.native.s3.complete.v1\",\"rows\":{count},\"owner_commit\":\"{OWNER}\",\"source_id\":\"{SOURCE_ID}\",\"adapter_id\":\"{}\"}}",native_adapter::ADAPTER_ID).map_err(|e|e.to_string())?;
    f.flush().map_err(|e|e.to_string())?;Ok(count)
}
fn main(){let a:Vec<String>=std::env::args().collect();let r=if a.len()==2 {run(&a[1])}else{Err("USAGE native_probe OUTPUT.jsonl".into())};
    match r {Ok(n)=>println!("NATIVE_ADAPTER_COMPLETE rows={n}"),Err(e)=>{eprintln!("NATIVE_ADAPTER_FAIL:{e}");std::process::exit(3);}}}

#[cfg(test)] mod native_tests {
    use super::*;
    use native_adapter::{EmissionKind,EmissionFrame};
    #[test] fn old_anisotropic_stock_is_added_without_rescaling() {
        let (_,t,g,z)=setup(8,96,0.3).unwrap();let mut old=t.empty_state();
        t.add_delta(&mut old,0,1.0,0.25).unwrap();t.add_delta(&mut old,7,40.0,0.1).unwrap();
        let frozen=old.clone();let mut born=t.empty_state();
        new_birth(&t,&mut born,&g,z,Constraints::P2).unwrap();
        new_birth(&t,&mut old,&g,z,Constraints::P2).unwrap();
        let mut occupied_untouched=0;
        for k in 0..t.cell_count() {
            assert_eq!(old.number[k],frozen.number[k]+born.number[k]);
            assert_eq!(old.energy_ref[k],frozen.energy_ref[k]+born.energy_ref[k]);
            if born.number[k]==0.0 {
                assert_eq!(old.support_lo[k],frozen.support_lo[k]);assert_eq!(old.support_hi[k],frozen.support_hi[k]);
                if frozen.number[k]>0.0 {occupied_untouched+=1;}
            }
        }
        assert!(occupied_untouched>0);t.validate_state(&old).unwrap();
    }
    #[test] fn spectral_owner_and_supports_are_identical_per_ray() {
        let (_,t,g,z)=setup(8,96,0.3).unwrap();let w=alpha(&t,&g,Constraints::P2).unwrap();
        let mut original=t.empty_state();t.inject(&mut original,&g,z,DT).unwrap();
        let mut changed=t.empty_state();let receipt=new_birth(&t,&mut changed,&g,z,Constraints::P2).unwrap();
        let rays=t.ray_geometry(&g).unwrap();let ne=t.n_energy();let mut positive=0;
        for k in 0..t.cell_count() {
            let f=w[k/ne]/rays[k/ne].angular_weight;
            assert_eq!(changed.number[k],original.number[k]*f);
            assert_eq!(changed.energy_ref[k],original.energy_ref[k]*f);
            assert_eq!(changed.support_lo[k],original.support_lo[k]);assert_eq!(changed.support_hi[k],original.support_hi[k]);
            if changed.number[k]>0.0 {positive+=1;}
        }
        assert!(positive>16);assert!(receipt.added.added_photons_per_h>0.0);
    }
    #[test] fn anisotropic_and_unspecified_sources_reject_even_symmetric_weights() {
        let (_,t,g,z)=setup(8,96,0.3).unwrap();let w=alpha(&t,&g,Constraints::P2).unwrap();let mut s=t.empty_state();
        t.add_delta(&mut s,0,1.0,0.25).unwrap();let frozen=s.clone();
        for kind in [EmissionKind::PhysicallyAnisotropic,EmissionKind::Unspecified] {
            let declaration=Declaration{kind,frame:EmissionFrame::NonTiltedLocalOrthonormal};
            assert_eq!(inject_new_isotropic(&t,&mut s,&g,z,DT,declaration,Constraints::P2,&w).unwrap_err().code(),"ANGULAR_SOURCE_DECLARATION_REQUIRED");assert_eq!(s,frozen);
        }
        let declaration=Declaration{kind:EmissionKind::LocallyIsotropicNewBirth,frame:EmissionFrame::OtherOrUnspecified};
        assert_eq!(inject_new_isotropic(&t,&mut s,&g,z,DT,declaration,Constraints::P2,&w).unwrap_err().code(),"ANGULAR_SOURCE_FRAME_REQUIRED");assert_eq!(s,frozen);
    }
    #[test] fn infeasible_native_support_has_no_partial_mutation() {
        let (_,t,g,z)=setup(8,96,0.9).unwrap();let mut s=t.empty_state();t.add_delta(&mut s,0,1.0,0.2).unwrap();let frozen=s.clone();
        assert_eq!(new_birth(&t,&mut s,&g,z,Constraints::P2).unwrap_err(),"INFEASIBLE_ANGULAR_SUPPORT");assert_eq!(s,frozen);
    }
    #[test] fn rejected_weights_and_native_failure_are_transactional() {
        let (_,t,g,z)=setup(8,96,0.3).unwrap();let w=alpha(&t,&g,Constraints::P2).unwrap();let mut s=t.empty_state();
        t.add_delta(&mut s,0,1.0,0.2).unwrap();let frozen=s.clone();
        let mut invalid=w.clone();invalid[0]=-1.0;
        assert!(inject_new_isotropic(&t,&mut s,&g,z,DT,Declaration::locally_isotropic_non_tilted(),Constraints::P2,&invalid).is_err());assert_eq!(s,frozen);
        assert_eq!(inject_new_isotropic(&t,&mut s,&g,z,-DT,Declaration::locally_isotropic_non_tilted(),Constraints::P2,&w).unwrap_err().code(),"AXBI_COVARIANT_SOURCE_DT");assert_eq!(s,frozen);
    }
    #[test] fn zero_birth_preserves_old_state_bitwise() {
        let (_,t,g,z)=setup(8,96,0.3).unwrap();let w=alpha(&t,&g,Constraints::P2).unwrap();let mut s=t.empty_state();t.add_delta(&mut s,0,1.0,0.2).unwrap();let frozen=s.clone();
        let r=inject_new_isotropic(&t,&mut s,&g,z,0.0,Declaration::locally_isotropic_non_tilted(),Constraints::P2,&w).unwrap();
        assert_eq!(s,frozen);assert_eq!(r.added.added_photons_per_h,0.0);assert_eq!(r.added.added_energy_ev_per_h,0.0);
    }
    #[test] fn p24_native_birth_is_positive_reflection_even_and_measured() {
        let (_,t,g,z)=setup(8,96,0.3).unwrap();let mut s=t.empty_state();let r=new_birth(&t,&mut s,&g,z,Constraints::P2P4).unwrap();
        assert!(r.min_weight>0.0);assert!(r.weight_moments.iter().all(|x|x.abs()<=3e-15));
        let ne=t.n_energy();let n=t.cell_count()/ne;
        for j in 0..n {for k in 0..ne {
            let a=s.number[j*ne+k];let b=s.number[(n-1-j)*ne+k];assert!((a-b).abs()<=1e-12*a.abs().max(b.abs()).max(1e-30));
        }}
        t.validate_state(&s).unwrap();
    }
}
