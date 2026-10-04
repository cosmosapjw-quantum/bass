use crate::{ForwardError, HHeModel, HHeRhs, HHeState};

/// Solve the backward Euler thermal balance with its endpoint recombination sink.
pub(crate) fn endpoint_thermal(
    model: &HHeModel,
    old: &HHeState,
    candidate: &HHeState,
    rates: &HHeRhs,
    dt: f64,
) -> Result<(f64, f64), ForwardError> {
    let mut heating = 0.0;
    let mut recombination_sum = 0.0;
    let mut escape_binding = 0.0;
    for a in 0..3 {
        for g in 0..3 {
            heating += rates.photo_per_cm3_s[a][g]
                * (model.photon_energy_ev[g] - model.threshold_ev[a])
                * model.ev_erg;
        }
        heating -= rates.collision_per_cm3_s[a] * model.threshold_ev[a] * model.ev_erg;
        recombination_sum += rates.recombination_per_cm3_s[a];
        escape_binding += rates.recombination_per_cm3_s[a] * model.threshold_ev[a] * model.ev_erg;
    }
    let ne = model.electron_density(candidate)?;
    let npart = model.n_h_cm3 + model.n_he_cm3 + ne;
    let numerator = old.u_erg_cm3 + dt * heating;
    let denominator = 1.0 + dt * recombination_sum / npart;
    let u = numerator / denominator;
    let temperature = 2.0 * u / (3.0 * model.kb_erg_k * npart);
    let escaped = old.escaped_erg_cm3
        + dt * (escape_binding + 1.5 * model.kb_erg_k * temperature * recombination_sum);
    if !u.is_finite() || u < 0.0 || !escaped.is_finite() || escaped < 0.0 {
        return Err(ForwardError::InvalidInput("HHE_THERMAL_DOMAIN"));
    }
    Ok((u, escaped))
}
