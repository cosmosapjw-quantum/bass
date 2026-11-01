//! C5 fixed-reference-q finite-volume photon number/energy-moment grid.
//!
//! The selected MD14 source is integrated within each ORIGINAL spectral cell
//! and clipped at moving source/helium boundaries. All injection is in physical
//! gas-frame energy, mapped to conserved q energy with R*J_Omega exactly once.
//! Within a q cell (N,U_ref), photoabsorption uses the positive cell centroid
//! (U_ref/N) and therefore has an energy/threshold closure error requiring
//! convergence checks. This is not the canonical coupled EoR Driver.
use crate::axbi_q_advance::advance_frozen_expanding;
use crate::axbi_q_closure::absorb_positive_bin;
use crate::axbi_q_reference::CovariantPhoton;
use crate::axbi_sources::{AngularCell, AxbiSource, SpectralCell};
use crate::{
    Absorber, AtomicProvider, CharacteristicRay, ForwardError, GeometrySnapshot, HHeModel,
};

const MIN_REFERENCE_MAX_EV: f64 = 432.230;
const LOG_ENERGY_MIN_EV: f64 = 13.6;
const X8: [f64; 8] = [
    -0.9602898564975363,
    -0.7966664774136267,
    -0.5255324099163290,
    -0.1834346424956498,
    0.1834346424956498,
    0.5255324099163290,
    0.7966664774136267,
    0.9602898564975363,
];
const W8: [f64; 8] = [
    0.1012285362903763,
    0.2223810344533745,
    0.3137066458778873,
    0.3626837833783619,
    0.3626837833783619,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763,
];
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("AXBI_Q_GRID_SOURCE_DOMAIN")
}
fn nonnegative(x: f64) -> bool {
    x.is_finite() && x >= 0.
}
fn shape(e: f64, kt: f64) -> f64 {
    e * e / (e / kt).exp_m1()
}
fn shape_moments(lo: f64, hi: f64, kt: f64) -> (f64, f64) {
    if hi <= lo {
        return (0., 0.);
    }
    let middle = (lo + hi) * 0.5;
    let half = (hi - lo) * 0.5;
    let mut number = 0.;
    let mut energy = 0.;
    for i in 0..8 {
        let e = middle + half * X8[i];
        let weighted = W8[i] * shape(e, kt);
        number += weighted;
        energy += weighted * e;
    }
    (number * half, energy * half)
}
#[derive(Clone, Copy, Debug, Default)]
pub struct QMoments {
    pub photon_number_per_h: f64,
    pub photon_energy_ev_per_h: f64,
}
#[derive(Clone, Copy, Debug, Default)]
pub struct QSourceLedger {
    pub added_photons_per_h: f64,
    pub added_energy_ev_per_h: f64,
}
#[derive(Clone, Copy, Debug, Default)]
pub struct QReactionLedger {
    pub absorbed_per_h: [f64; 3],
    pub binding_ev_per_h: f64,
    pub heat_ev_per_h: f64,
    pub redshift_work_ev_per_h: f64,
    pub photon_number_residual_per_h: f64,
    pub photon_energy_residual_ev_per_h: f64,
}
#[derive(Clone, Debug)]
pub struct QFixedGrid {
    reference: GeometrySnapshot,
    source: AxbiSource,
    edges: Vec<f64>,
    source_integrals: Vec<f64>,
    number: Vec<f64>,
    moment_ref_ev: Vec<f64>,
    // Envelopes of actual emitted reference-q source support; zero if empty.
    support_lower_ref_ev: Vec<f64>,
    support_upper_ref_ev: Vec<f64>,
    n_energy: usize,
    k_t_ev: f64,
}
impl QFixedGrid {
    /// The full selected shear family must have an emission support guard
    /// beyond the analytically sufficient 432.229372... eV bound.
    pub fn new(
        source: &AxbiSource,
        reference: GeometrySnapshot,
        n_energy: usize,
        max_e_ref: f64,
    ) -> Result<Self, ForwardError> {
        reference.volume_factor()?;
        source.at_redshift(20.0)?;
        if !(16..=512).contains(&n_energy)
            || !max_e_ref.is_finite()
            || max_e_ref < MIN_REFERENCE_MAX_EV
            || max_e_ref > 50000.0
            || ![8, 16, 32].contains(&source.angular_cells.len())
            || source.spectral_cells.is_empty()
        {
            return Err(invalid());
        }
        let kt = 50000.0 * HHeModel::controlled_fixture().kb_erg_k
            / HHeModel::controlled_fixture().ev_erg;
        let norms: Vec<f64> = source
            .spectral_cells
            .iter()
            .map(|s| shape_moments(s.lower_ev, s.upper_ev, kt).0)
            .collect();
        if norms.iter().any(|x| !x.is_finite() || *x <= 0.0) {
            return Err(invalid());
        }
        let log_span = (max_e_ref / LOG_ENERGY_MIN_EV).ln();
        let edges: Vec<f64> = (0..=n_energy)
            .map(|i| LOG_ENERGY_MIN_EV * (log_span * i as f64 / n_energy as f64).exp())
            .collect();
        let n_cells = n_energy * source.angular_cells.len();
        Ok(Self {
            reference,
            source: source.clone(),
            edges,
            source_integrals: norms,
            number: vec![0.; n_cells],
            moment_ref_ev: vec![0.; n_cells],
            support_lower_ref_ev: vec![0.; n_cells],
            support_upper_ref_ev: vec![0.; n_cells],
            n_energy,
            k_t_ev: kt,
        })
    }
    pub fn cell_count(&self) -> usize {
        self.number.len()
    }
    pub fn number(&self) -> &[f64] {
        &self.number
    }
    pub fn ref_energy_moment(&self) -> &[f64] {
        &self.moment_ref_ev
    }
    pub fn support_bounds(&self) -> (&[f64], &[f64]) {
        (&self.support_lower_ref_ev, &self.support_upper_ref_ev)
    }
    pub fn buffer_capacity_bytes(&self) -> usize {
        (self.number.capacity()
            + self.moment_ref_ev.capacity()
            + self.support_lower_ref_ev.capacity()
            + self.support_upper_ref_ev.capacity()
            + self.edges.capacity()
            + self.source_integrals.capacity())
            * std::mem::size_of::<f64>()
    }
    fn angle_scale(
        &self,
        now: &GeometrySnapshot,
        ang: &AngularCell,
    ) -> Result<(f64, f64), ForwardError> {
        let mu = ang.mu;
        if !mu.is_finite() || mu.abs() >= 1.0 {
            return Err(invalid());
        }
        let ray = CharacteristicRay::new(1.0, [(1. - mu * mu).sqrt(), 0., mu], 0.0)?;
        let r = ray.pullback(&self.reference, now)?.energy_ev;
        let jac = ray.solid_angle_jacobian(&self.reference, now)?;
        if !(r.is_finite() && r > 0. && jac.is_finite() && jac > 0.) {
            return Err(invalid());
        }
        Ok((r, jac))
    }
    pub fn observe(&self, now: &GeometrySnapshot) -> Result<QMoments, ForwardError> {
        now.volume_factor()?;
        let mut totals = QMoments::default();
        for (j, ang) in self.source.angular_cells.iter().enumerate() {
            let (r, _) = self.angle_scale(now, ang)?;
            for i in 0..self.n_energy {
                let k = j * self.n_energy + i;
                totals.photon_number_per_h += self.number[k];
                totals.photon_energy_ev_per_h += r * self.moment_ref_ev[k];
            }
        }
        if !nonnegative(totals.photon_number_per_h) || !nonnegative(totals.photon_energy_ev_per_h) {
            return Err(invalid());
        }
        Ok(totals)
    }
    /// Only two dynamically growing arrays of FIXED size are stored.
    /// One extra same-sized scratch allocation allows transactional injection.
    pub fn inject(
        &mut self,
        now: &GeometrySnapshot,
        zbar: f64,
        dt_s: f64,
        threads: usize,
    ) -> Result<QSourceLedger, ForwardError> {
        now.volume_factor()?;
        if !nonnegative(dt_s) || ![1, 2, 4].contains(&threads) {
            return Err(invalid());
        }
        let source_rate = self.source.at_redshift(zbar)?.per_h_s;
        // Fail closed if a new geometry would move the physical source
        // outside the configured fixed-q domain. Partial deposition would
        // otherwise conserve the *truncated* photon count deceptively.
        for ang in &self.source.angular_cells {
            let (r, _) = self.angle_scale(now, ang)?;
            let emission_lo_ref = 13.6 / r;
            let emission_hi_ref = 100.0 / r;
            if emission_lo_ref < self.edges[0] * (1.0 - 2e-12)
                || emission_hi_ref > self.edges[self.n_energy] * (1.0 + 2e-12)
            {
                return Err(invalid());
            }
        }
        let mut add_n = vec![0.0; self.cell_count()];
        let mut add_u = vec![0.0; self.cell_count()];
        let nmu = self.source.angular_cells.len();
        let groups = if threads > 1 && self.cell_count() >= 2048 {
            threads.min(nmu)
        } else {
            1
        };
        let angular_stride = nmu.div_ceil(groups);
        let span = self.n_energy * angular_stride;
        let integrals = &self.source_integrals;
        let spectral = &self.source.spectral_cells;
        let edges = &self.edges;
        let angles = &self.source.angular_cells;
        let reference = self.reference;
        let kt = self.k_t_ev;
        std::thread::scope(|scope| -> Result<(), ForwardError> {
            let mut handles = Vec::new();
            for ((n, u), ang) in add_n
                .chunks_mut(span)
                .zip(add_u.chunks_mut(span))
                .zip(angles.chunks(angular_stride))
            {
                handles.push(scope.spawn(move || {
                    deposit_chunk(
                        n,
                        u,
                        ang,
                        reference,
                        now,
                        edges,
                        spectral,
                        integrals,
                        kt,
                        source_rate * dt_s,
                    )
                }));
            }
            for handle in handles {
                handle.join().map_err(|_| invalid())??;
            }
            Ok(())
        })?;
        let mut ledger = QSourceLedger::default();
        let mut next_lo = self.support_lower_ref_ev.clone();
        let mut next_hi = self.support_upper_ref_ev.clone();
        for j in 0..nmu {
            let (r, _) = self.angle_scale(now, &angles[j])?;
            for i in 0..self.n_energy {
                let k = j * self.n_energy + i;
                let n = add_n[k];
                let u = add_u[k];
                if !nonnegative(n)
                    || !nonnegative(u)
                    || !(self.number[k] + n).is_finite()
                    || !(self.moment_ref_ev[k] + u).is_finite()
                {
                    return Err(invalid());
                }
                if n > 0.0 {
                    let lo = self.edges[i].max(13.6 / r);
                    let hi = self.edges[i + 1].min(100.0 / r);
                    if !(lo.is_finite() && hi.is_finite() && lo < hi) {
                        return Err(invalid());
                    }
                    if self.number[k] > 0.0 {
                        next_lo[k] = next_lo[k].min(lo);
                        next_hi[k] = next_hi[k].max(hi);
                    } else {
                        next_lo[k] = lo;
                        next_hi[k] = hi;
                    }
                    let after_n = self.number[k] + n;
                    let after_mean = (self.moment_ref_ev[k] + u) / after_n;
                    if after_mean < next_lo[k] * (1.0 - 1e-10)
                        || after_mean > next_hi[k] * (1.0 + 1e-10)
                    {
                        return Err(invalid());
                    }
                }
                ledger.added_photons_per_h += n;
                ledger.added_energy_ev_per_h += r * u;
            }
        }
        for k in 0..self.cell_count() {
            self.number[k] += add_n[k];
            self.moment_ref_ev[k] += add_u[k];
        }
        self.support_lower_ref_ev = next_lo;
        self.support_upper_ref_ev = next_hi;
        Ok(ledger)
    }

    /// Snapshot-frozen exact exponential loss per positive centroid cell.
    /// Angle chunks are independent, serial and bounded (up to four threads).
    /// Original grid arrays commit only when all chunks pass validation.
    pub fn absorb_frozen(
        &mut self,
        now: &GeometrySnapshot,
        neutral_cm3: [f64; 3],
        dt_s: f64,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        now.volume_factor()?;
        if !nonnegative(dt_s)
            || !neutral_cm3.iter().all(|x| nonnegative(*x))
            || ![1, 2, 4].contains(&threads)
        {
            return Err(invalid());
        }
        let before = self.observe(now)?;
        let mut new_n = self.number.clone();
        let mut new_u = self.moment_ref_ev.clone();
        let nmu = self.source.angular_cells.len();
        let groups = if threads > 1 && self.cell_count() >= 2048 {
            threads.min(nmu)
        } else {
            1
        };
        let stride = nmu.div_ceil(groups);
        let span = self.n_energy * stride;
        let reference = self.reference;
        let n_energy = self.n_energy;
        let angles = &self.source.angular_cells;
        let parts = std::thread::scope(|scope| -> Result<Vec<QReactionLedger>, ForwardError> {
            let mut handles = Vec::new();
            for ((n, u), a) in new_n
                .chunks_mut(span)
                .zip(new_u.chunks_mut(span))
                .zip(angles.chunks(stride))
            {
                handles.push(scope.spawn(move || {
                    absorb_chunk(n, u, a, n_energy, reference, now, neutral_cm3, dt_s)
                }));
            }
            let mut results = Vec::new();
            for handle in handles {
                results.push(handle.join().map_err(|_| invalid())??);
            }
            Ok(results)
        })?;
        let mut response = QReactionLedger::default();
        for p in parts {
            for a in 0..3 {
                response.absorbed_per_h[a] += p.absorbed_per_h[a];
            }
            response.binding_ev_per_h += p.binding_ev_per_h;
            response.heat_ev_per_h += p.heat_ev_per_h;
        }
        self.number = new_n;
        self.moment_ref_ev = new_u;
        let after = self.observe(now)?;
        response.photon_number_residual_per_h = before.photon_number_per_h
            - after.photon_number_per_h
            - response.absorbed_per_h.iter().sum::<f64>();
        response.photon_energy_residual_ev_per_h = before.photon_energy_ev_per_h
            - after.photon_energy_ev_per_h
            - response.binding_ev_per_h
            - response.heat_ev_per_h;
        Ok(response)
    }
    /// An independent finite-duration, source-free constant-log-H reference:
    /// actual geometry endpoints are mapped to effective nonnegative H_i,
    /// and each positive bin-centroid photon uses the earlier C3 threshold
    /// event-split frozen-gas solver. N/U arrays have FIXED length.
    /// This is NOT an exact integral over a variable-H physical history.
    pub fn advance_frozen(
        &mut self,
        now: &GeometrySnapshot,
        end: &GeometrySnapshot,
        neutral_cm3: [f64; 3],
        duration_s: f64,
        slices: usize,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        now.volume_factor()?;
        end.volume_factor()?;
        if !nonnegative(duration_s)
            || duration_s == 0.
            || !neutral_cm3.iter().all(|v| nonnegative(*v))
            || !(1..=256).contains(&slices)
            || ![1, 2, 4].contains(&threads)
        {
            return Err(invalid());
        }
        let mut hubble = [0.; 3];
        for (i, h) in hubble.iter_mut().enumerate() {
            *h = (end.scale_factors[i] / now.scale_factors[i]).ln() / duration_s;
            if !nonnegative(*h) {
                return Err(invalid());
            }
        }
        let before = self.observe(now)?;
        let mut new_n = self.number.clone();
        let mut new_u = self.moment_ref_ev.clone();
        let nmu = self.source.angular_cells.len();
        let groups = if threads > 1 && self.cell_count() >= 2048 {
            threads.min(nmu)
        } else {
            1
        };
        let stride = nmu.div_ceil(groups);
        let span = self.n_energy * stride;
        let reference = self.reference;
        let nenergy = self.n_energy;
        let parts = std::thread::scope(|scope| -> Result<Vec<QReactionLedger>, ForwardError> {
            let mut handles = Vec::new();
            for ((n, u), angles) in new_n
                .chunks_mut(span)
                .zip(new_u.chunks_mut(span))
                .zip(self.source.angular_cells.chunks(stride))
            {
                handles.push(scope.spawn(move || {
                    advance_chunk(
                        n,
                        u,
                        angles,
                        nenergy,
                        reference,
                        now,
                        hubble,
                        neutral_cm3,
                        duration_s,
                        slices,
                    )
                }));
            }
            let mut parts = Vec::new();
            for h in handles {
                parts.push(h.join().map_err(|_| invalid())??);
            }
            Ok(parts)
        })?;
        let mut response = QReactionLedger::default();
        for part in parts {
            for i in 0..3 {
                response.absorbed_per_h[i] += part.absorbed_per_h[i];
            }
            response.binding_ev_per_h += part.binding_ev_per_h;
            response.heat_ev_per_h += part.heat_ev_per_h;
            response.redshift_work_ev_per_h += part.redshift_work_ev_per_h;
        }
        self.number = new_n;
        self.moment_ref_ev = new_u;
        let after = self.observe(end)?;
        response.photon_number_residual_per_h = before.photon_number_per_h
            - after.photon_number_per_h
            - response.absorbed_per_h.iter().sum::<f64>();
        response.photon_energy_residual_ev_per_h = before.photon_energy_ev_per_h
            - after.photon_energy_ev_per_h
            - response.binding_ev_per_h
            - response.heat_ev_per_h
            - response.redshift_work_ev_per_h;
        Ok(response)
    }
}
fn deposit_chunk(
    numbers: &mut [f64],
    moments: &mut [f64],
    angles: &[AngularCell],
    reference: GeometrySnapshot,
    now: &GeometrySnapshot,
    edges: &[f64],
    spectrum: &[SpectralCell],
    normalizers: &[f64],
    kt: f64,
    source_amount: f64,
) -> Result<(), ForwardError> {
    let n_energy = edges.len() - 1;
    if numbers.len() != n_energy * angles.len() || moments.len() != numbers.len() {
        return Err(invalid());
    }
    for (j, angle) in angles.iter().enumerate() {
        let mu = angle.mu;
        if !(mu.is_finite() && mu.abs() < 1.0 && nonnegative(angle.count_fraction)) {
            return Err(invalid());
        }
        let ray = CharacteristicRay::new(1., [(1. - mu * mu).sqrt(), 0., mu], 0.)?;
        let r = ray.pullback(&reference, now)?.energy_ev;
        let jac = ray.solid_angle_jacobian(&reference, now)?;
        let amp = source_amount * angle.count_fraction * jac;
        for i in 0..n_energy {
            let e_lo = edges[i] * r;
            let e_hi = edges[i + 1] * r;
            if e_hi <= 13.6 || e_lo >= 100.0 {
                continue;
            }
            let mut n = 0.;
            let mut u = 0.;
            for (k, segment) in spectrum.iter().enumerate() {
                let l = e_lo.max(segment.lower_ev);
                let h = e_hi.min(segment.upper_ev);
                if h <= l {
                    continue;
                }
                let (a, b) = shape_moments(l, h, kt);
                let factor = amp * segment.photon_fraction / normalizers[k];
                n += factor * a;
                u += factor * b / r;
            }
            let index = j * n_energy + i;
            numbers[index] += n;
            moments[index] += u;
        }
    }
    Ok(())
}

/// In-place scratch absorption of one contiguous set of q-angle lanes.
fn absorb_chunk(
    numbers: &mut [f64],
    moments: &mut [f64],
    angles: &[AngularCell],
    n_energy: usize,
    reference: GeometrySnapshot,
    now: &GeometrySnapshot,
    neutrals: [f64; 3],
    dt_s: f64,
) -> Result<QReactionLedger, ForwardError> {
    if numbers.len() != angles.len() * n_energy || moments.len() != numbers.len() {
        return Err(invalid());
    }
    let provider = AtomicProvider::reference();
    let model = HHeModel::controlled_fixture();
    let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
    let mut ledger = QReactionLedger::default();
    for (j, angle) in angles.iter().enumerate() {
        let mu = angle.mu;
        let ray = CharacteristicRay::new(1., [(1. - mu * mu).sqrt(), 0., mu], 0.)?;
        let r = ray.pullback(&reference, now)?.energy_ev;
        for i in 0..n_energy {
            let k = j * n_energy + i;
            let n = numbers[k];
            if n <= 0.0 {
                continue;
            }
            let u = moments[k];
            let e = r * u / n;
            if !(e.is_finite() && e > 0.0 && e <= 50000.) {
                return Err(invalid());
            }
            let mut rates = [0.; 3];
            for a in 0..3 {
                if neutrals[a] > 0. && e >= [13.6, 24.59, 54.42][a] {
                    rates[a] =
                        model.c_cm_s * neutrals[a] * provider.cross_section(species[a], e)?;
                }
            }
            let lambda: f64 = rates.iter().sum();
            if !nonnegative(lambda) {
                return Err(invalid());
            }
            if lambda == 0.0 {
                continue;
            }
            let frac = -(-lambda * dt_s).exp_m1();
            if !frac.is_finite() || !(0.0..=1.0).contains(&frac) {
                return Err(invalid());
            }
            let lost = n * frac;
            numbers[k] = n * (1.0 - frac);
            moments[k] = u * (1.0 - frac);
            for a in 0..3 {
                let gain = lost * rates[a] / lambda;
                ledger.absorbed_per_h[a] += gain;
                ledger.binding_ev_per_h += gain * model.threshold_ev[a];
                ledger.heat_ev_per_h += gain * (e - model.threshold_ev[a]);
            }
        }
    }
    Ok(ledger)
}

fn advance_chunk(
    numbers: &mut [f64],
    moments: &mut [f64],
    angles: &[AngularCell],
    nenergy: usize,
    reference: GeometrySnapshot,
    now: &GeometrySnapshot,
    hubble: [f64; 3],
    neutrals: [f64; 3],
    dt: f64,
    slices: usize,
) -> Result<QReactionLedger, ForwardError> {
    if numbers.len() != nenergy * angles.len() || moments.len() != numbers.len() {
        return Err(invalid());
    }
    let mut out = QReactionLedger::default();
    for (j, angle) in angles.iter().enumerate() {
        let mu = angle.mu;
        let direction = [(1. - mu * mu).sqrt(), 0., mu];
        for i in 0..nenergy {
            let k = j * nenergy + i;
            let n = numbers[k];
            if n <= 0. {
                continue;
            }
            let mean_ref = moments[k] / n;
            let packet = CovariantPhoton::from_local(&reference, mean_ref, direction, n)?;
            let step = advance_frozen_expanding(&packet, now, hubble, neutrals, dt, slices)?;
            let survive = step.final_packet.photons_per_h / n;
            if !nonnegative(survive) || survive > 1.0 {
                return Err(invalid());
            }
            numbers[k] *= survive;
            moments[k] *= survive;
            for a in 0..3 {
                out.absorbed_per_h[a] += step.absorbed_per_h[a];
            }
            out.binding_ev_per_h += step.binding_ev_per_h;
            out.heat_ev_per_h += step.heat_ev_per_h;
            out.redshift_work_ev_per_h += step.redshift_work_ev_per_h;
        }
    }
    Ok(out)
}

impl QFixedGrid {
    /// Alternative positivity-preserving spectral closure with threshold-split
    /// H/He absorption, no chemistry feedback or spectrum uniqueness claim.
    /// Transactional scratch and at most four independent angular workers.
    pub fn absorb_reconstructed(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        self.absorb_reconstructed_impl(now, neutrals, duration_s, threads, false)
    }
    /// Optional C7 support-limited closure. The support envelope is valid
    /// for the original continuously-positive broad MD14 source in the
    /// selected expanding background; no arbitrary spectral hardness bound.
    pub fn absorb_reconstructed_support(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        self.absorb_reconstructed_impl(now, neutrals, duration_s, threads, true)
    }
    fn absorb_reconstructed_impl(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
        restricted: bool,
    ) -> Result<QReactionLedger, ForwardError> {
        now.volume_factor()?;
        if !nonnegative(duration_s)
            || !neutrals.iter().all(|v| nonnegative(*v))
            || ![1, 2, 4].contains(&threads)
        {
            return Err(invalid());
        }
        let before = self.observe(now)?;
        let mut new_n = self.number.clone();
        let mut new_u = self.moment_ref_ev.clone();
        let nmu = self.source.angular_cells.len();
        let groups = if threads > 1 && self.cell_count() >= 2048 {
            threads.min(nmu)
        } else {
            1
        };
        let per_group = nmu.div_ceil(groups);
        let span = per_group * self.n_energy;
        let nenergy = self.n_energy;
        let reference = self.reference;
        let edges = &self.edges;
        let lows = &self.support_lower_ref_ev;
        let highs = &self.support_upper_ref_ev;
        let chunks = std::thread::scope(|scope| -> Result<Vec<QReactionLedger>, ForwardError> {
            let mut handles = Vec::new();
            for ((((n, u), low), high), a) in new_n
                .chunks_mut(span)
                .zip(new_u.chunks_mut(span))
                .zip(lows.chunks(span))
                .zip(highs.chunks(span))
                .zip(self.source.angular_cells.chunks(per_group))
            {
                handles.push(
                    scope.spawn(move || -> Result<QReactionLedger, ForwardError> {
                        let mut sum = QReactionLedger::default();
                        for (j, ang) in a.iter().enumerate() {
                            let mu = ang.mu;
                            let ray =
                                CharacteristicRay::new(1., [(1. - mu * mu).sqrt(), 0., mu], 0.)?;
                            let r = ray.pullback(&reference, now)?.energy_ev;
                            for i in 0..nenergy {
                                let k = j * nenergy + i;
                                if n[k] == 0.0 {
                                    continue;
                                }
                                let left = if restricted { low[k] } else { edges[i] };
                                let right = if restricted { high[k] } else { edges[i + 1] };
                                if !(left > 0.0 && right > left) {
                                    return Err(invalid());
                                }
                                let loss = absorb_positive_bin(
                                    left, right, n[k], u[k], r, neutrals, duration_s,
                                )?;
                                n[k] = loss.surviving_photons_per_h;
                                u[k] = loss.surviving_energy_moment_ev_per_h;
                                for x in 0..3 {
                                    sum.absorbed_per_h[x] += loss.absorbed_per_h[x];
                                }
                                sum.binding_ev_per_h += loss.binding_ev_per_h;
                                sum.heat_ev_per_h += loss.heat_ev_per_h;
                            }
                        }
                        Ok(sum)
                    }),
                );
            }
            let mut out = Vec::new();
            for h in handles {
                out.push(h.join().map_err(|_| invalid())??);
            }
            Ok(out)
        })?;
        let mut result = QReactionLedger::default();
        for part in chunks {
            for x in 0..3 {
                result.absorbed_per_h[x] += part.absorbed_per_h[x];
            }
            result.binding_ev_per_h += part.binding_ev_per_h;
            result.heat_ev_per_h += part.heat_ev_per_h;
        }
        self.number = new_n;
        self.moment_ref_ev = new_u;
        let after = self.observe(now)?;
        result.photon_number_residual_per_h = before.photon_number_per_h
            - after.photon_number_per_h
            - result.absorbed_per_h.iter().sum::<f64>();
        result.photon_energy_residual_ev_per_h = before.photon_energy_ev_per_h
            - after.photon_energy_ev_per_h
            - result.binding_ev_per_h
            - result.heat_ev_per_h;
        Ok(result)
    }
}
