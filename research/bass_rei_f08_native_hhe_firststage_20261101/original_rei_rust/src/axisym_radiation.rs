//! Collisionless prescribed-axisymmetric packet ledger; no source or absorber is coupled here.
use crate::{ForwardError, GeometrySnapshot, PhotonBins, PhotonGrid, RadiationState};
#[derive(Clone, Debug, PartialEq)]
pub struct AxisymPhotonLedgerContract {
    pub grid: PhotonGrid,
}
#[derive(Clone, Debug, PartialEq)]
pub struct AxisymPhotonStep {
    pub before: PhotonBins,
    pub after: PhotonBins,
    pub transported: RadiationState,
    pub number_change_cm3: f64,
    /// Difference induced by finite bin deposition only; not a transport loss.
    pub remap_count_residual_cm3: f64,
    /// Signed net packet-count transfer toward higher energy across each finite grid face.
    pub number_face_transfer_cm3: Vec<f64>,
    /// The same face transfer weighted by the fixed face energy.
    pub energy_face_transfer_ev_cm3: Vec<f64>,
    pub energy_change_ev_cm3: f64,
}
fn finite(x: f64) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(ForwardError::InvalidInput("AXISYM_RADIATION_OVERFLOW"))
    }
}
fn compensated_add(sum: &mut f64, correction: &mut f64, value: f64) {
    let next = *sum + value;
    if sum.abs() >= value.abs() {
        *correction += (*sum - next) + value;
    } else {
        *correction += (value - next) + *sum;
    }
    *sum = next;
}
impl AxisymPhotonLedgerContract {
    pub fn new(energy_edges_ev: Vec<f64>, mu_edges: Vec<f64>) -> Result<Self, ForwardError> {
        Ok(Self {
            grid: PhotonGrid::new(energy_edges_ev, mu_edges, 1)?,
        })
    }
    pub fn collisionless_step(
        &self,
        state: &RadiationState,
        to: GeometrySnapshot,
    ) -> Result<AxisymPhotonStep, ForwardError> {
        let before = state.remap(&self.grid)?;
        let transported = state.transport(to)?;
        let after = transported.remap(&self.grid)?;
        let packet_n0 = state.comoving_photon_count()?;
        let packet_n1 = transported.comoving_photon_count()?;
        if packet_n0.to_bits() != packet_n1.to_bits() {
            return Err(ForwardError::InvalidInput("AXISYM_PHOTON_NUMBER"));
        }
        let n0 = before.total_count()?;
        let n1 = after.total_count()?;
        let e0 = before.total_energy_ev_cm3()?;
        let e1 = after.total_energy_ev_cm3()?;
        let mut number_face_transfer_cm3 = vec![0.0; self.grid.energy_edges_ev.len()];
        let mut number_face_correction_cm3 = vec![0.0; self.grid.energy_edges_ev.len()];
        for (before_packet, after_packet) in state.packets.iter().zip(&transported.packets) {
            let final_face = self.grid.energy_edges_ev.len() - 1;
            for (face_index, (face, total)) in self
                .grid
                .energy_edges_ev
                .iter()
                .zip(&mut number_face_transfer_cm3)
                .enumerate()
            {
                let above_before = if face_index == final_face {
                    before_packet.ray.energy_ev > *face
                } else {
                    before_packet.ray.energy_ev >= *face
                };
                let above_after = if face_index == final_face {
                    after_packet.ray.energy_ev > *face
                } else {
                    after_packet.ray.energy_ev >= *face
                };
                let contribution = before_packet.comoving_count_cm3
                    * (above_after as u8 as f64 - above_before as u8 as f64);
                compensated_add(
                    total,
                    &mut number_face_correction_cm3[face_index],
                    contribution,
                );
            }
        }
        for (total, correction) in number_face_transfer_cm3
            .iter_mut()
            .zip(number_face_correction_cm3)
        {
            *total = finite(*total + correction)?;
        }
        if number_face_transfer_cm3.iter().any(|x| !x.is_finite()) {
            return Err(ForwardError::InvalidInput("AXISYM_RADIATION_OVERFLOW"));
        }
        let energy_face_transfer_ev_cm3 = self
            .grid
            .energy_edges_ev
            .iter()
            .zip(&number_face_transfer_cm3)
            .map(|(e, n)| e * n)
            .collect::<Vec<_>>();
        if energy_face_transfer_ev_cm3.iter().any(|x| !x.is_finite()) {
            return Err(ForwardError::InvalidInput("AXISYM_RADIATION_OVERFLOW"));
        }
        Ok(AxisymPhotonStep {
            before,
            after,
            transported,
            number_change_cm3: finite(packet_n1 - packet_n0)?,
            remap_count_residual_cm3: finite(n1 - n0)?,
            number_face_transfer_cm3,
            energy_face_transfer_ev_cm3,
            energy_change_ev_cm3: finite(e1 - e0)?,
        })
    }
}
