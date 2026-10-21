//! Opt-in angular reweighting of a new isotropic emission increment only.
//! The exact upstream CovariantTransport owns every spectral integral and bin.
//! Stocks: photons / total-H nucleus and eV / total-H nucleus.
use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState, SourceLedger};
use rei_microphysics::{ForwardError, GeometrySnapshot};

pub const ADAPTER_ID: &str = "BASS_NEW_ISOTROPIC_SOURCE_ANGULAR_ADAPTER_V1";
pub const MOMENT_ATOL: f64 = 3e-15;
pub const PARITY_ATOL: f64 = 5e-14;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum EmissionKind { LocallyIsotropicNewBirth, PhysicallyAnisotropic, Unspecified }
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum EmissionFrame { NonTiltedLocalOrthonormal, OtherOrUnspecified }
#[derive(Clone, Copy, Debug)]
pub struct Declaration { pub kind: EmissionKind, pub frame: EmissionFrame }
impl Declaration {
    /// A caller's explicit physical declaration; parity does not establish it.
    pub fn locally_isotropic_non_tilted() -> Self {
        Self { kind: EmissionKind::LocallyIsotropicNewBirth,
               frame: EmissionFrame::NonTiltedLocalOrthonormal }
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Constraints { P2, P2P4 }
#[derive(Debug)]
pub struct BirthReceipt {
    pub original_ledger: SourceLedger,
    pub added: SourceLedger,
    pub weight_moments: [f64; 2],
    pub photon_moments: [f64; 2],
    pub energy_moments: [f64; 2],
    pub min_weight: f64,
    pub max_ray_rescaling: f64,
}
pub fn p2(mu: f64) -> f64 { (3.0 * mu * mu - 1.0) / 2.0 }
pub fn p4(mu: f64) -> f64 { let y=mu*mu; (35.0*y*y-30.0*y+3.0)/8.0 }
pub fn sum(xs: impl Iterator<Item=f64>) -> f64 {
    let (mut s, mut c)=(0.0_f64,0.0_f64);
    for x in xs { let t=s+x; c+=if s.abs()>=x.abs(){(s-t)+x}else{(x-t)+s};s=t; }
    s+c
}
fn bad(s: &'static str) -> ForwardError { ForwardError::InvalidInput(s) }

/// Validate the declared source, form an empty-state native birth, reweight its
/// rays, and merge it transactionally. The original source and old state are
/// borrowed immutably until every new cell has passed the owner's validator.
/// Alpha changes neither the spectral owner nor ray coordinates/supports.
pub fn inject_new_isotropic(
    transport: &CovariantTransport, state: &mut PhotonState,
    now: &GeometrySnapshot, zbar: f64, dt_s: f64,
    declaration: Declaration, constraints: Constraints, alpha: &[f64],
) -> Result<BirthReceipt, ForwardError> {
    if declaration.kind != EmissionKind::LocallyIsotropicNewBirth {
        return Err(bad("ANGULAR_SOURCE_DECLARATION_REQUIRED"));
    }
    if declaration.frame != EmissionFrame::NonTiltedLocalOrthonormal {
        return Err(bad("ANGULAR_SOURCE_FRAME_REQUIRED"));
    }
    if now.scale_factors[0] != now.scale_factors[1] ||
       now.hubble_per_s[0] != now.hubble_per_s[1] {
        return Err(bad("AXISYMMETRIC_GEOMETRY_REQUIRED"));
    }
    transport.validate_state(state)?;
    let rays=transport.ray_geometry(now)?;
    let nr=rays.len();
    if alpha.len()!=nr || nr<2 || alpha.iter().any(|a| !a.is_finite() || *a<=0.0) {
        return Err(bad("ANGULAR_INPUT_DOMAIN"));
    }
    if (sum(alpha.iter().copied())-1.0).abs()>MOMENT_ATOL {
        return Err(bad("ANGULAR_NORMALIZATION"));
    }
    for j in 0..nr {
        if !rays[j].angular_weight.is_finite() || rays[j].angular_weight<=0.0 ||
           !rays[j].mu.is_finite() || rays[j].mu.abs()>1.0 ||
           (j>0 && rays[j].mu<=rays[j-1].mu) {
            return Err(bad("ANGULAR_NATIVE_RAY_DOMAIN"));
        }
        if (rays[j].mu+rays[nr-1-j].mu).abs()>PARITY_ATOL ||
           (alpha[j]-alpha[nr-1-j]).abs()>PARITY_ATOL {
            return Err(bad("REFLECTION_SOURCE_REQUIRED"));
        }
    }
    let weights=[sum(rays.iter().zip(alpha).map(|(r,a)| a*p2(r.mu))),
                 sum(rays.iter().zip(alpha).map(|(r,a)| a*p4(r.mu)))];
    if weights[0].abs()>MOMENT_ATOL ||
       (constraints==Constraints::P2P4 && weights[1].abs()>MOMENT_ATOL) {
        return Err(bad("ANGULAR_MOMENT_TOLERANCE"));
    }
    let mut birth=transport.empty_state();
    let original=transport.inject(&mut birth,now,zbar,dt_s)?;
    let ne=transport.n_energy();
    let mut max_scale=0.0_f64;
    for j in 0..nr {
        let factor=alpha[j]/rays[j].angular_weight;
        if !factor.is_finite() || factor<=0.0 { return Err(bad("NUMERIC_RAY_RESCALING")); }
        max_scale=max_scale.max(factor);
        for k in j*ne..(j+1)*ne {
            if birth.number[k]>0.0 {
                birth.number[k]*=factor;
                birth.energy_ref[k]*=factor;
                if birth.number[k]<=0.0 || birth.energy_ref[k]<=0.0 {
                    return Err(bad("NUMERIC_NEWBORN_POSITIVE_SUPPORT_LOSS"));
                }
            }
        }
    }
    transport.validate_state(&birth)?;
    let (n,u)=transport.inventory(&birth,now)?;
    let mut photon=[0.0_f64;2];
    let mut energy=[0.0_f64;2];
    for ell in 0..2 {
        let moment=|mu| if ell==0 {p2(mu)} else {p4(mu)};
        photon[ell]=sum(birth.number.iter().enumerate().map(|(k,x)|x*moment(rays[k/ne].mu)));
        energy[ell]=sum(birth.energy_ref.iter().enumerate().map(|(k,x)|
            x*rays[k/ne].scale*moment(rays[k/ne].mu)));
        photon[ell]=if n>0.0 {photon[ell]/n} else {0.0};
        energy[ell]=if u>0.0 {energy[ell]/u} else {0.0};
    }
    let mut next=state.clone();
    for k in 0..next.number.len() {
        if birth.number[k]==0.0 { continue; }
        if next.number[k]==0.0 {
            next.support_lo[k]=birth.support_lo[k];
            next.support_hi[k]=birth.support_hi[k];
        } else {
            next.support_lo[k]=next.support_lo[k].min(birth.support_lo[k]);
            next.support_hi[k]=next.support_hi[k].max(birth.support_hi[k]);
        }
        next.number[k]+=birth.number[k];
        next.energy_ref[k]+=birth.energy_ref[k];
    }
    transport.validate_state(&next)?;
    *state=next;
    Ok(BirthReceipt {
        original_ledger:original,
        added:SourceLedger{added_photons_per_h:n,added_energy_ev_per_h:u},
        weight_moments:weights,photon_moments:photon,energy_moments:energy,
        min_weight:alpha.iter().copied().fold(f64::INFINITY,f64::min),
        max_ray_rescaling:max_scale,
    })
}
