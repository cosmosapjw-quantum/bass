//! C4 bounded-memory, angularly faithful covariant-photon compression pilot.
//!
//! Within a common ray, positive number-weighted momentum merging preserves
//! photon number, three covariant spatial momentum moments, and energy for
//! every Bianchi-I geometry (up to floating arithmetic). Different q-directions
//! MUST NOT be merged under the same theorem. No coupled EoR error certificate.
//! Time-varying opacity events after this instantaneous compression require
//! separate validation; sampled frozen-neutral error is a local diagnostic.
use crate::axbi_q_reference::{absorb_frozen_gas, CovariantPhoton};
use crate::{ForwardError, GeometrySnapshot};

fn invalid() -> ForwardError {
    ForwardError::InvalidInput("AXBI_Q_CAP_DOMAIN")
}
fn finite_nonnegative(x: f64) -> bool {
    x.is_finite() && x >= 0.
}
#[derive(Clone, Copy, Debug)]
pub struct TaggedPhoton {
    pub angular_key: usize,
    pub photon: CovariantPhoton,
}
#[derive(Clone, Copy, Debug)]
pub struct CapacityPolicy {
    pub cap: usize,
    pub max_events_per_h: [f64; 3],
    pub max_heat_ev_per_h: f64,
    pub neutral_cm3: [f64; 3],
    pub duration_s: f64,
}
impl CapacityPolicy {
    fn check(&self) -> Result<(), ForwardError> {
        if !(1..=65536).contains(&self.cap)
            || !finite_nonnegative(self.duration_s)
            || !finite_nonnegative(self.max_heat_ev_per_h)
            || !self.max_events_per_h.iter().all(|v| finite_nonnegative(*v))
            || !self.neutral_cm3.iter().all(|v| finite_nonnegative(*v))
        {
            return Err(invalid());
        }
        Ok(())
    }
}
#[derive(Clone, Debug)]
pub struct PairAssessment {
    pub accepted: bool,
    pub reason: &'static str,
    pub merged: Option<TaggedPhoton>,
    /// Nonnegative discrete energy deficit after preserving vector k.
    pub energy_deficit_now_ev_per_h: f64,
    pub energy_deficit_future_ev_per_h: f64,
    pub event_abs_error_per_h: [f64; 3],
    pub heat_abs_error_ev_per_h: f64,
}
fn rejected(reason: &'static str, now: f64, future: f64) -> PairAssessment {
    PairAssessment {
        accepted: false,
        reason,
        merged: None,
        energy_deficit_now_ev_per_h: now,
        energy_deficit_future_ev_per_h: future,
        event_abs_error_per_h: [0.; 3],
        heat_abs_error_ev_per_h: 0.,
    }
}
fn norm(v: [f64; 3]) -> f64 {
    v[0].hypot(v[1]).hypot(v[2])
}
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
fn cross(a: [f64; 3], b: [f64; 3]) -> f64 {
    let x = a[1] * b[2] - a[2] * b[1];
    let y = a[2] * b[0] - a[0] * b[2];
    let z = a[0] * b[1] - a[1] * b[0];
    x.hypot(y).hypot(z)
}

/// Pair validation is *not* a global future readout error certificate.
/// The only proven energy equivalence uses exactly collinear q vectors. The
/// numerical parallel test uses 1e-12 relative collinearity and energy slack
/// guards for representable source data. The caller must separately establish
/// monotone expansion between now and future: endpoint snapshots alone cannot
/// rule out an intermediate nonmonotone energy excursion. Reaction errors are
/// measured ONLY at the frozen current geometry, under numerical budgets.
pub fn assess_merge(
    a: &TaggedPhoton,
    b: &TaggedPhoton,
    now: &GeometrySnapshot,
    future: &GeometrySnapshot,
    policy: CapacityPolicy,
) -> Result<PairAssessment, ForwardError> {
    policy.check()?;
    now.volume_factor()?;
    future.volume_factor()?;
    if a.angular_key != b.angular_key {
        return Ok(rejected("HOLD_DIFFERENT_ANGULAR_CELL", 0., 0.));
    }
    let n1 = a.photon.photons_per_h;
    let n2 = b.photon.photons_per_h;
    if !n1.is_finite() || !n2.is_finite() || n1 <= 0. || n2 <= 0. || !((n1 + n2).is_finite()) {
        return Err(invalid());
    }
    let k1 = a.photon.k_ev;
    let k2 = b.photon.k_ev;
    let nk1 = norm(k1);
    let nk2 = norm(k2);
    if !(nk1.is_finite() && nk2.is_finite() && nk1 > 0. && nk2 > 0.) {
        return Err(invalid());
    }
    let n = n1 + n2;
    let k = std::array::from_fn(|i| (n1 * k1[i] + n2 * k2[i]) / n);
    let merged = TaggedPhoton {
        angular_key: a.angular_key,
        photon: CovariantPhoton {
            k_ev: k,
            photons_per_h: n,
        },
    };
    let e1 = a.photon.energy_at(now)?;
    let e2 = b.photon.energy_at(now)?;
    let ef1 = a.photon.energy_at(future)?;
    let ef2 = b.photon.energy_at(future)?;
    let em = merged.photon.energy_at(now)?;
    let emf = merged.photon.energy_at(future)?;
    let total_e = n1 * e1 + n2 * e2;
    let total_ef = n1 * ef1 + n2 * ef2;
    if !total_e.is_finite()
        || !total_ef.is_finite()
        || !(n * em).is_finite()
        || !(n * emf).is_finite()
    {
        return Err(invalid());
    }
    let slack = (total_e - n * em).max(0.);
    let slack_future = (total_ef - n * emf).max(0.);
    let ksin = cross(k1, k2) / (nk1 * nk2);
    if !ksin.is_finite() {
        return Err(invalid());
    }
    if dot(k1, k2) <= 0.
        || ksin > 1e-12
        || slack > 1e-12 * total_e
        || slack_future > 1e-12 * total_ef
    {
        return Ok(rejected("HOLD_Q_DIRECTION", slack, slack_future));
    }
    if ef1 > e1 * (1. + 1e-12) || ef2 > e2 * (1. + 1e-12) {
        return Ok(rejected("HOLD_NONMONOTONE_FORECAST", slack, slack_future));
    }
    let low = ef1.min(ef2);
    let high = e1.max(e2);
    for threshold in [13.60, 24.59, 54.42] {
        if low < threshold && threshold <= high {
            return Ok(rejected("HOLD_THRESHOLD_TUBE", slack, slack_future));
        }
    }
    // Real owner AtomicProvider, actual frozen proper densities and elapsed s.
    let old1 = absorb_frozen_gas(&a.photon, now, policy.neutral_cm3, policy.duration_s)?;
    let old2 = absorb_frozen_gas(&b.photon, now, policy.neutral_cm3, policy.duration_s)?;
    let new = absorb_frozen_gas(&merged.photon, now, policy.neutral_cm3, policy.duration_s)?;
    let errors = std::array::from_fn(|i| {
        (old1.absorbed_per_h[i] + old2.absorbed_per_h[i] - new.absorbed_per_h[i]).abs()
    });
    let heat_err = (old1.heat_ev_per_h + old2.heat_ev_per_h - new.heat_ev_per_h).abs();
    if errors
        .iter()
        .zip(policy.max_events_per_h)
        .any(|(v, b)| *v > b)
        || heat_err > policy.max_heat_ev_per_h
    {
        return Ok(rejected("HOLD_LOCAL_REACTION_BUDGET", slack, slack_future));
    }
    Ok(PairAssessment {
        accepted: true,
        reason: "ACCEPTED_SCOPED",
        merged: Some(merged),
        energy_deficit_now_ev_per_h: slack,
        energy_deficit_future_ev_per_h: slack_future,
        event_abs_error_per_h: errors,
        heat_abs_error_ev_per_h: heat_err,
    })
}
#[derive(Debug, Clone)]
pub struct CapacityHold {
    pub reason: &'static str,
    pub current_packets: usize,
    pub requested_cap: usize,
}
#[derive(Debug, Clone)]
pub struct CapacityOutput {
    pub packets: Vec<TaggedPhoton>,
    pub initial_packets: usize,
    pub merges: usize,
    pub event_spent_per_h: [f64; 3],
    pub heat_spent_ev_per_h: f64,
    pub maximum_energy_slack_ev_per_h: f64,
    /// No global trajectory bound follows from these local frozen readouts.
    pub scope: &'static str,
}
/// A smallest-adjacent-energy-gap reducer with independent group guards.
/// O((N-cap)*N logN), intended as a C4 small reference/feasibility test, NOT
/// the full production fixed-memory algorithm. A failed cap is transactional.
pub fn cap_packets(
    packets: &[TaggedPhoton],
    now: &GeometrySnapshot,
    future: &GeometrySnapshot,
    policy: CapacityPolicy,
) -> Result<CapacityOutput, CapacityHold> {
    let hold = |reason: &'static str, current: usize| CapacityHold {
        reason,
        current_packets: current,
        requested_cap: policy.cap,
    };
    if policy.check().is_err()
        || now.volume_factor().is_err()
        || future.volume_factor().is_err()
        || packets.len() > 65536
        || packets.iter().any(|p| {
            !p.photon.photons_per_h.is_finite()
                || p.photon.photons_per_h <= 0.
                || !p.photon.k_ev.iter().all(|v| v.is_finite())
                || p.photon.energy_at(now).is_err()
                || p.photon.energy_at(future).is_err()
        })
    {
        return Err(hold("INVALID_CAP_INPUT", packets.len()));
    }
    let mut bank = packets.to_vec();
    let mut spent = [0.; 3];
    let mut heat_spent = 0.;
    let mut maximum_slack: f64 = 0.;
    let mut merges = 0;
    while bank.len() > policy.cap {
        bank.sort_by(|a, b| {
            a.angular_key.cmp(&b.angular_key).then_with(|| {
                a.photon
                    .energy_at(now)
                    .unwrap_or(f64::INFINITY)
                    .total_cmp(&b.photon.energy_at(now).unwrap_or(f64::INFINITY))
            })
        });
        let mut best: Option<(usize, f64, PairAssessment)> = None;
        for i in 0..bank.len() - 1 {
            if bank[i].angular_key != bank[i + 1].angular_key {
                continue;
            }
            let candidate = assess_merge(&bank[i], &bank[i + 1], now, future, policy)
                .map_err(|_| hold("INVALID_PAIR", bank.len()))?;
            if !candidate.accepted {
                continue;
            }
            if (0..3)
                .any(|k| spent[k] + candidate.event_abs_error_per_h[k] > policy.max_events_per_h[k])
                || heat_spent + candidate.heat_abs_error_ev_per_h > policy.max_heat_ev_per_h
            {
                continue;
            }
            let e1 = bank[i]
                .photon
                .energy_at(now)
                .map_err(|_| hold("INVALID_ENERGY", bank.len()))?;
            let e2 = bank[i + 1]
                .photon
                .energy_at(now)
                .map_err(|_| hold("INVALID_ENERGY", bank.len()))?;
            let gap = (e2 - e1).abs();
            if best.as_ref().is_none_or(|x| gap < x.1) {
                best = Some((i, gap, candidate));
            }
        }
        let Some((i, _, candidate)) = best else {
            return Err(hold("HOLD_BUDGET_THRESHOLD_OR_DIRECTION", bank.len()));
        };
        for (k, v) in spent.iter_mut().enumerate() {
            *v += candidate.event_abs_error_per_h[k];
        }
        heat_spent += candidate.heat_abs_error_ev_per_h;
        maximum_slack = maximum_slack
            .max(candidate.energy_deficit_now_ev_per_h)
            .max(candidate.energy_deficit_future_ev_per_h);
        bank.splice(i..i + 2, [candidate.merged.unwrap()]);
        merges += 1;
    }
    Ok(CapacityOutput {
        packets: bank,
        initial_packets: packets.len(),
        merges,
        event_spent_per_h: spent,
        heat_spent_ev_per_h: heat_spent,
        maximum_energy_slack_ev_per_h: maximum_slack,
        scope: "LOCAL_FROZEN_GAS_AND_TWO_ENDPOINTS_ONLY",
    })
}
