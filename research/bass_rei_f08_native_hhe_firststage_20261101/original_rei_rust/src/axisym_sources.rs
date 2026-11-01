//! Manufactured source/closure accounting.  It is deliberately not wired to H/He RHS.
use crate::ForwardError;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PhotonRouting {
    ExplicitTransport,
    EliminatedByOts,
    AlreadyDeposited,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ExcessPartition {
    pub heat: f64,
    pub secondary_ionization: f64,
    pub excitation: f64,
    pub escape: f64,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PrimaryPhotoEvent {
    pub rate_m3_s: f64,
    pub photon_energy_j: f64,
    pub threshold_j: f64,
    pub partition: ExcessPartition,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhotoEventLedger {
    pub photon_loss_m3_s: f64,
    pub primary_ionization_m3_s: f64,
    pub threshold_power_j_m3_s: f64,
    pub excess_power_j_m3_s: f64,
    pub heat_power_j_m3_s: f64,
    pub secondary_power_j_m3_s: f64,
    pub excitation_power_j_m3_s: f64,
    pub escape_power_j_m3_s: f64,
}
fn bad() -> ForwardError {
    ForwardError::InvalidInput("AXISYM_SOURCE_CONTRACT")
}
impl PrimaryPhotoEvent {
    pub fn ledger(self) -> Result<PhotoEventLedger, ForwardError> {
        let p = self.partition;
        if ![
            self.rate_m3_s,
            self.photon_energy_j,
            self.threshold_j,
            p.heat,
            p.secondary_ionization,
            p.excitation,
            p.escape,
        ]
        .iter()
        .all(|x| x.is_finite())
            || self.rate_m3_s < 0.
            || self.threshold_j <= 0.
            || self.photon_energy_j < self.threshold_j
            || [p.heat, p.secondary_ionization, p.excitation, p.escape]
                .iter()
                .any(|x| *x < 0.)
        {
            return Err(bad());
        }
        let sum = p.heat + p.secondary_ionization + p.excitation + p.escape;
        if (sum - 1.).abs() > 64. * f64::EPSILON {
            return Err(bad());
        }
        let excess = self.rate_m3_s * (self.photon_energy_j - self.threshold_j);
        let out = PhotoEventLedger {
            photon_loss_m3_s: -self.rate_m3_s,
            primary_ionization_m3_s: self.rate_m3_s,
            threshold_power_j_m3_s: self.rate_m3_s * self.threshold_j,
            excess_power_j_m3_s: excess,
            heat_power_j_m3_s: excess * p.heat,
            secondary_power_j_m3_s: excess * p.secondary_ionization,
            excitation_power_j_m3_s: excess * p.excitation,
            escape_power_j_m3_s: excess * p.escape,
        };
        if [
            out.threshold_power_j_m3_s,
            out.excess_power_j_m3_s,
            out.heat_power_j_m3_s,
            out.secondary_power_j_m3_s,
            out.excitation_power_j_m3_s,
            out.escape_power_j_m3_s,
        ]
        .iter()
        .all(|x| x.is_finite())
        {
            Ok(out)
        } else {
            Err(bad())
        }
    }
}
pub fn validate_routing(routing: PhotonRouting, reinject: bool) -> Result<(), ForwardError> {
    if reinject && routing != PhotonRouting::ExplicitTransport {
        Err(bad())
    } else {
        Ok(())
    }
}
