//! Fixed reference-energy photon moments with positive, threshold-cut spectra.
//!
//! Geometry changes the energy scale on each reference ray; it never remaps the
//! stored cells. Spectral reconstruction is a two-moment closure, not a claim
//! that the underlying spectrum is uniquely determined by those moments.
use crate::axbi_parallel::OrderedWorkerPool;
use crate::axbi_q_closure::positive_reconstruct;
use crate::axbi_sources::AxbiSource;
use crate::igm_thermal::IgmPhotoInput;
use crate::{
    Absorber, AtomicProvider, CharacteristicRay, ForwardError, GeometrySnapshot, HHeModel,
};
use std::sync::Arc;

pub const FIT_THRESHOLDS_EV: [f64; 3] = [13.60, 24.59, 54.42];
pub const MAX_NODES_PER_CELL: usize = 1024;
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
fn bad(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}
fn nonnegative(x: f64) -> bool {
    x.is_finite() && x >= 0.0
}
fn sum(xs: impl Iterator<Item = f64>) -> f64 {
    let (mut total, mut correction) = (0.0, 0.0);
    for x in xs {
        let y = x - correction;
        let next = total + y;
        correction = (next - total) - y;
        total = next;
    }
    total
}
fn compensated_add(total: &mut f64, correction: &mut f64, x: f64) {
    let y = x - *correction;
    let next = *total + y;
    *correction = (next - *total) - y;
    *total = next;
}
/// Evaluate the represented first moment relative to its nearer support end.
/// U == end*N forces an endpoint delta at binary64 moment resolution; this is
/// an exact equality branch, never a tolerance-based broad-support fallback.
fn support_mean(lo: f64, hi: f64, n: f64, u: f64) -> f64 {
    let lower_distance = u - lo * n;
    let upper_distance = hi * n - u;
    if lower_distance <= upper_distance {
        lo + lower_distance / n
    } else {
        hi - upper_distance / n
    }
}

/// All entries are ray-major, with fixed `cell_count()` length. Empty support
/// is exactly zero; occupied support is a physical envelope, not a full bin.
#[derive(Clone, Debug, PartialEq)]
pub struct PhotonState {
    pub number: Vec<f64>,
    pub energy_ref: Vec<f64>,
    pub support_lo: Vec<f64>,
    pub support_hi: Vec<f64>,
}
impl PhotonState {
    pub fn buffer_capacity_bytes(&self) -> usize {
        (self.number.capacity()
            + self.energy_ref.capacity()
            + self.support_lo.capacity()
            + self.support_hi.capacity())
            * std::mem::size_of::<f64>()
    }
}
#[derive(Clone, Copy, Debug)]
pub struct RayGeometry {
    pub scale: f64,
    pub mu: f64,
    /// Current locally isotropic source weight, normalized after one Jacobian.
    pub angular_weight: f64,
}
#[derive(Clone, Copy, Debug, Default)]
pub struct SourceLedger {
    pub added_photons_per_h: f64,
    pub added_energy_ev_per_h: f64,
}
#[derive(Clone, Copy, Debug, Default)]
pub struct QuadratureDiagnostics {
    pub max_count_relative_defect: f64,
    pub max_energy_relative_defect: f64,
    /// Explicit normalized exponential-tail bound for y > 48 (beta > 30).
    pub omitted_tail_number_bound_per_h: f64,
    pub omitted_tail_energy_bound_ev_per_h: f64,
    pub omitted_tail_endpoint_moment_bound_ev_per_h: f64,
    pub max_asymptotic_mean_defect_ev: f64,
}
#[derive(Clone, Debug)]
struct AbsorptionNode {
    cell: usize,
    q: f64,
    number: f64,
    sigma: [f64; 3],
    excess_ev: [f64; 3],
}
#[derive(Clone, Debug)]
pub struct PreparedAbsorption {
    template: PhotonState,
    nodes: Vec<AbsorptionNode>,
    pub diagnostics: QuadratureDiagnostics,
}
impl PreparedAbsorption {
    pub(crate) fn evaluate_for_cell_count(
        &self,
        cells: usize,
        absorber_cm3: [f64; 3],
        n_h_cm3: f64,
        dt_s: f64,
    ) -> Result<AbsorptionResult, ForwardError> {
        if self.template.number.len() != cells {
            return Err(bad("AXBI_COVARIANT_CACHE_SHAPE"));
        }
        self.evaluate(absorber_cm3, n_h_cm3, dt_s)
    }
    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }
    pub fn buffer_capacity_bytes(&self) -> usize {
        self.template.buffer_capacity_bytes()
            + self.nodes.capacity() * std::mem::size_of::<AbsorptionNode>()
    }
    /// Geometry and reconstruction are frozen; only trial opacities change.
    pub fn evaluate(
        &self,
        absorber_cm3: [f64; 3],
        n_h_cm3: f64,
        dt_s: f64,
    ) -> Result<AbsorptionResult, ForwardError> {
        if !absorber_cm3.iter().all(|&x| nonnegative(x))
            || !n_h_cm3.is_finite()
            || n_h_cm3 <= 0.0
            || !nonnegative(dt_s)
        {
            return Err(bad("AXBI_COVARIANT_OPACITY_DOMAIN"));
        }
        let model = HHeModel::controlled_fixture();
        let mut state = self.template.clone();
        state.number.fill(0.0);
        state.energy_ref.fill(0.0);
        let mut out = AbsorptionResult {
            state,
            photo: IgmPhotoInput::default(),
            absorbed_per_h: [0.0; 3],
            binding_ev_per_h: 0.0,
            heat_ev_per_h: 0.0,
        };
        let mut count_correction = vec![0.0; out.state.number.len()];
        let mut energy_correction = vec![0.0; out.state.number.len()];
        let upper_anchor: Vec<_> = (0..out.state.number.len())
            .map(|k| {
                self.template.energy_ref[k] - self.template.support_lo[k] * self.template.number[k]
                    > self.template.support_hi[k] * self.template.number[k]
                        - self.template.energy_ref[k]
            })
            .collect();
        for node in &self.nodes {
            let opacity = sum((0..3).map(|j| absorber_cm3[j] * node.sigma[j]));
            let denominator = 1.0 + dt_s * model.c_cm_s * opacity;
            if !denominator.is_finite() || denominator < 1.0 {
                return Err(bad("AXBI_COVARIANT_BE_DOMAIN"));
            }
            let surviving = node.number / denominator;
            compensated_add(
                &mut out.state.number[node.cell],
                &mut count_correction[node.cell],
                surviving,
            );
            let offset = if upper_anchor[node.cell] {
                self.template.support_hi[node.cell] - node.q
            } else {
                node.q - self.template.support_lo[node.cell]
            };
            compensated_add(
                &mut out.state.energy_ref[node.cell],
                &mut energy_correction[node.cell],
                surviving * offset,
            );
            for j in 0..3 {
                let rate = model.c_cm_s * n_h_cm3 * node.sigma[j] * surviving;
                out.photo.gamma_s[j] += rate;
                out.photo.heat_erg_per_absorber_s[j] += rate * node.excess_ev[j] * model.ev_erg;
                let event = dt_s * model.c_cm_s * absorber_cm3[j] * node.sigma[j] * surviving;
                out.absorbed_per_h[j] += event;
                out.binding_ev_per_h += event * model.threshold_ev[j];
                out.heat_ev_per_h += event * node.excess_ev[j];
            }
        }
        for k in 0..out.state.number.len() {
            if out.state.number[k] == 0.0 {
                out.state.support_lo[k] = 0.0;
                out.state.support_hi[k] = 0.0;
            } else if upper_anchor[k] {
                out.state.energy_ref[k] =
                    out.state.support_hi[k].mul_add(out.state.number[k], -out.state.energy_ref[k]);
            } else {
                out.state.energy_ref[k] =
                    out.state.support_lo[k].mul_add(out.state.number[k], out.state.energy_ref[k]);
            }
        }
        if !out
            .state
            .number
            .iter()
            .chain(&out.state.energy_ref)
            .all(|&x| nonnegative(x))
            || !out
                .photo
                .gamma_s
                .iter()
                .chain(&out.photo.heat_erg_per_absorber_s)
                .chain(&out.absorbed_per_h)
                .all(|&x| nonnegative(x))
            || !nonnegative(out.binding_ev_per_h)
            || !nonnegative(out.heat_ev_per_h)
        {
            return Err(bad("AXBI_COVARIANT_BE_NONFINITE"));
        }
        Ok(out)
    }
}
#[derive(Clone, Debug)]
pub struct AbsorptionResult {
    pub state: PhotonState,
    pub photo: IgmPhotoInput,
    pub absorbed_per_h: [f64; 3],
    pub binding_ev_per_h: f64,
    pub heat_ev_per_h: f64,
}
#[derive(Clone, Debug)]
pub struct CovariantTransport {
    reference: GeometrySnapshot,
    source: AxbiSource,
    edges: Vec<f64>,
    source_norms: Vec<f64>,
    prepare_pool: Arc<OrderedWorkerPool>,
}
fn shape(e: f64) -> f64 {
    let m = HHeModel::controlled_fixture();
    let kt = 50000.0 * m.kb_erg_k / m.ev_erg;
    e * e / (e / kt).exp_m1()
}
fn source_moments(lo: f64, hi: f64) -> (f64, f64) {
    let center = 0.5 * (lo + hi);
    let half = 0.5 * (hi - lo);
    let n = sum((0..8).map(|i| W8[i] * half * shape(center + half * X8[i])));
    let u = sum((0..8).map(|i| {
        let e = center + half * X8[i];
        W8[i] * half * shape(e) * e
    }));
    (n, u)
}
impl CovariantTransport {
    pub fn new(
        source: &AxbiSource,
        reference: GeometrySnapshot,
        n_energy: usize,
        q_min: f64,
        q_max: f64,
    ) -> Result<Self, ForwardError> {
        reference.volume_factor()?;
        if !(1..=1024).contains(&n_energy)
            || !q_min.is_finite()
            || q_min <= 0.0
            || !q_max.is_finite()
            || q_max <= q_min
            || q_max > 50000.0
            || source.angular_cells.is_empty()
            || source.spectral_cells.is_empty()
        {
            return Err(bad("AXBI_COVARIANT_GRID_DOMAIN"));
        }
        let span = (q_max / q_min).ln();
        let mut edges: Vec<_> = (0..=n_energy)
            .map(|i| q_min * (span * i as f64 / n_energy as f64).exp())
            .collect();
        edges[0] = q_min;
        edges[n_energy] = q_max;
        if edges.windows(2).any(|p| p[0] >= p[1]) {
            return Err(bad("AXBI_COVARIANT_GRID_RESOLUTION"));
        }
        let source_norms: Vec<_> = source
            .spectral_cells
            .iter()
            .map(|c| source_moments(c.lower_ev, c.upper_ev).0)
            .collect();
        if source_norms.iter().any(|n| !n.is_finite() || *n <= 0.0) {
            return Err(bad("AXBI_COVARIANT_SOURCE_DOMAIN"));
        }
        Ok(Self {
            reference,
            source: source.clone(),
            edges,
            source_norms,
            prepare_pool: Arc::new(OrderedWorkerPool::new(1)?),
        })
    }
    /// Construct the persistent pool once, before a production run. Clones share
    /// the bounded pool; Newton residuals never create worker threads.
    pub fn with_threads(mut self, width: usize) -> Result<Self, ForwardError> {
        self.prepare_pool = Arc::new(OrderedWorkerPool::new(width)?);
        Ok(self)
    }
    pub fn transport_threads(&self) -> usize {
        self.prepare_pool.width()
    }
    pub(crate) fn shared_pool(&self) -> Arc<OrderedWorkerPool> {
        Arc::clone(&self.prepare_pool)
    }
    pub fn n_energy(&self) -> usize {
        self.edges.len() - 1
    }
    pub fn cell_count(&self) -> usize {
        self.n_energy() * self.source.angular_cells.len()
    }
    pub fn edges(&self) -> &[f64] {
        &self.edges
    }
    pub fn empty_state(&self) -> PhotonState {
        PhotonState {
            number: vec![0.0; self.cell_count()],
            energy_ref: vec![0.0; self.cell_count()],
            support_lo: vec![0.0; self.cell_count()],
            support_hi: vec![0.0; self.cell_count()],
        }
    }
    pub fn validate_state(&self, state: &PhotonState) -> Result<(), ForwardError> {
        if [
            &state.number,
            &state.energy_ref,
            &state.support_lo,
            &state.support_hi,
        ]
        .iter()
        .any(|a| a.len() != self.cell_count())
        {
            return Err(bad("AXBI_COVARIANT_STATE_SHAPE"));
        }
        for k in 0..self.cell_count() {
            let (n, u, lo, hi) = (
                state.number[k],
                state.energy_ref[k],
                state.support_lo[k],
                state.support_hi[k],
            );
            if ![n, u, lo, hi].iter().all(|&v| nonnegative(v)) {
                return Err(bad("AXBI_COVARIANT_STATE_DOMAIN"));
            }
            if n == 0.0 {
                if u != 0.0 || lo != 0.0 || hi != 0.0 {
                    return Err(bad("AXBI_COVARIANT_EMPTY_SUPPORT"));
                }
            } else {
                let i = k % self.n_energy();
                let mean = support_mean(lo, hi, n, u);
                if lo < self.edges[i]
                    || hi > self.edges[i + 1]
                    || lo > hi
                    || !mean.is_finite()
                    || (lo == hi && u != lo * n)
                    || (lo != hi && (u < lo * n || u > hi * n || mean < lo || mean > hi))
                {
                    return Err(bad("AXBI_COVARIANT_SUPPORT_DOMAIN"));
                }
            }
        }
        Ok(())
    }
    pub fn ray_geometry(&self, now: &GeometrySnapshot) -> Result<Vec<RayGeometry>, ForwardError> {
        now.volume_factor()?;
        let isotropic = self
            .reference
            .scale_factors
            .windows(2)
            .all(|x| x[0] == x[1])
            && now.scale_factors.windows(2).all(|x| x[0] == x[1]);
        let mut result = Vec::with_capacity(self.source.angular_cells.len());
        for a in &self.source.angular_cells {
            let (scale, mu, jac) = if isotropic {
                (
                    self.reference.scale_factors[0] / now.scale_factors[0],
                    a.mu,
                    1.0,
                )
            } else {
                let ray =
                    CharacteristicRay::new(1.0, [(1.0 - a.mu * a.mu).sqrt(), 0.0, a.mu], 0.0)?;
                let moved = ray.pullback(&self.reference, now)?;
                (
                    moved.energy_ev,
                    moved.direction[2],
                    ray.solid_angle_jacobian(&self.reference, now)?,
                )
            };
            if !scale.is_finite() || scale <= 0.0 || !nonnegative(a.count_fraction * jac) {
                return Err(bad("AXBI_COVARIANT_GEOMETRY_DOMAIN"));
            }
            result.push(RayGeometry {
                scale,
                mu,
                angular_weight: a.count_fraction * jac,
            });
        }
        let norm = sum(result.iter().map(|g| g.angular_weight));
        if !norm.is_finite() || norm <= 0.0 {
            return Err(bad("AXBI_COVARIANT_ANGLE_DOMAIN"));
        }
        for g in &mut result {
            g.angular_weight /= norm;
        }
        Ok(result)
    }
    pub fn inventory(
        &self,
        state: &PhotonState,
        now: &GeometrySnapshot,
    ) -> Result<(f64, f64), ForwardError> {
        self.validate_state(state)?;
        let rays = self.ray_geometry(now)?;
        let n = sum(state.number.iter().copied());
        let u = sum(state
            .energy_ref
            .iter()
            .enumerate()
            .map(|(k, &u)| u * rays[k / self.n_energy()].scale));
        if !nonnegative(n) || !nonnegative(u) {
            return Err(bad("AXBI_COVARIANT_INVENTORY"));
        }
        Ok((n, u))
    }
    /// Test/point-source helper: a true delta keeps equal physical support.
    pub fn add_delta(
        &self,
        state: &mut PhotonState,
        ray: usize,
        q: f64,
        number: f64,
    ) -> Result<(), ForwardError> {
        self.validate_state(state)?;
        if ray >= self.source.angular_cells.len()
            || !nonnegative(number)
            || !q.is_finite()
            || q < self.edges[0]
            || q > *self.edges.last().unwrap()
        {
            return Err(bad("AXBI_COVARIANT_DELTA_DOMAIN"));
        }
        if number == 0.0 {
            return Ok(());
        }
        let i = self
            .edges
            .partition_point(|&e| e <= q)
            .saturating_sub(1)
            .min(self.n_energy() - 1);
        let k = ray * self.n_energy() + i;
        let mut next = state.clone();
        add_support(&mut next, k, number, q * number, q, q);
        self.validate_state(&next)?;
        *state = next;
        Ok(())
    }
    pub fn inject(
        &self,
        state: &mut PhotonState,
        now: &GeometrySnapshot,
        zbar: f64,
        dt_s: f64,
    ) -> Result<SourceLedger, ForwardError> {
        self.validate_state(state)?;
        if !nonnegative(dt_s) {
            return Err(bad("AXBI_COVARIANT_SOURCE_DT"));
        }
        let amount = self.source.at_redshift(zbar)?.per_h_s * dt_s;
        if !nonnegative(amount) {
            return Err(bad("AXBI_COVARIANT_SOURCE_AMOUNT"));
        }
        let rays = self.ray_geometry(now)?;
        // Check full emission support before any mutation or partial deposition.
        for ray in &rays {
            for c in &self.source.spectral_cells {
                if c.lower_ev / ray.scale < self.edges[0]
                    || c.upper_ev / ray.scale > *self.edges.last().unwrap()
                {
                    return Err(bad("AXBI_COVARIANT_SOURCE_OUTSIDE_GRID"));
                }
            }
        }
        let mut next = state.clone();
        let mut ledger = SourceLedger::default();
        for (j, ray) in rays.iter().enumerate() {
            for (s, c) in self.source.spectral_cells.iter().enumerate() {
                let amp = amount * ray.angular_weight * c.photon_fraction / self.source_norms[s];
                if amp == 0.0 {
                    continue;
                }
                for i in 0..self.n_energy() {
                    let lo = c.lower_ev.max(self.edges[i] * ray.scale);
                    let hi = c.upper_ev.min(self.edges[i + 1] * ray.scale);
                    if hi <= lo {
                        continue;
                    }
                    let (n, u) = source_moments(lo, hi);
                    let n = amp * n;
                    let u = amp * u;
                    // Grid-edge roundoff must not expand the cell's support.
                    let qlo = if lo == self.edges[i] * ray.scale {
                        self.edges[i]
                    } else {
                        lo / ray.scale
                    };
                    let qhi = if hi == self.edges[i + 1] * ray.scale {
                        self.edges[i + 1]
                    } else {
                        hi / ray.scale
                    };
                    add_support(
                        &mut next,
                        j * self.n_energy() + i,
                        n,
                        u / ray.scale,
                        qlo,
                        qhi,
                    );
                    ledger.added_photons_per_h += n;
                    ledger.added_energy_ev_per_h += u;
                }
            }
        }
        self.validate_state(&next)?;
        *state = next;
        Ok(ledger)
    }
    pub fn prepare(
        &self,
        state: &PhotonState,
        now: &GeometrySnapshot,
    ) -> Result<PreparedAbsorption, ForwardError> {
        if self.prepare_pool.width() == 1 {
            return self.prepare_legacy_serial(state, now);
        }
        self.validate_state(state)?;
        let rays = Arc::new(self.ray_geometry(now)?);
        let snapshot = Arc::new(state.clone());
        let work_state = Arc::clone(&snapshot);
        let n_energy = self.n_energy();
        let cells = self.prepare_pool.map_ordered(self.cell_count(), move |k| {
            prepare_cell(k, &work_state, rays[k / n_energy].scale)
        })?;
        let mut nodes = Vec::new();
        let mut diagnostics = QuadratureDiagnostics::default();
        // Original cell order and each cell's original node order. Each tail
        // diagnostic has exactly one += per cell in cell_quadrature; replaying
        // these individual terms preserves the original addition association.
        for cell in cells {
            diagnostics.max_count_relative_defect = diagnostics
                .max_count_relative_defect
                .max(cell.diagnostics.max_count_relative_defect);
            diagnostics.max_energy_relative_defect = diagnostics
                .max_energy_relative_defect
                .max(cell.diagnostics.max_energy_relative_defect);
            diagnostics.max_asymptotic_mean_defect_ev = diagnostics
                .max_asymptotic_mean_defect_ev
                .max(cell.diagnostics.max_asymptotic_mean_defect_ev);
            diagnostics.omitted_tail_number_bound_per_h +=
                cell.diagnostics.omitted_tail_number_bound_per_h;
            diagnostics.omitted_tail_energy_bound_ev_per_h +=
                cell.diagnostics.omitted_tail_energy_bound_ev_per_h;
            diagnostics.omitted_tail_endpoint_moment_bound_ev_per_h +=
                cell.diagnostics.omitted_tail_endpoint_moment_bound_ev_per_h;
            nodes.extend(cell.nodes);
        }
        Ok(PreparedAbsorption {
            template: Arc::unwrap_or_clone(snapshot),
            nodes,
            diagnostics,
        })
    }
    pub fn prepare_legacy_serial(
        &self,
        state: &PhotonState,
        now: &GeometrySnapshot,
    ) -> Result<PreparedAbsorption, ForwardError> {
        self.validate_state(state)?;
        let rays = self.ray_geometry(now)?;
        let mut prepared = PreparedAbsorption {
            template: state.clone(),
            nodes: Vec::new(),
            diagnostics: QuadratureDiagnostics::default(),
        };
        let provider = AtomicProvider::reference();
        let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
        let model = HHeModel::controlled_fixture();
        for k in 0..self.cell_count() {
            let n = state.number[k];
            if n == 0.0 {
                continue;
            }
            let r = rays[k / self.n_energy()].scale;
            let weights = cell_quadrature(
                state.support_lo[k],
                state.support_hi[k],
                n,
                state.energy_ref[k],
                r,
                &mut prepared.diagnostics,
            )?;
            for (q, number) in weights {
                let e = q * r;
                let mut sigma = [0.0; 3];
                let mut excess = [0.0; 3];
                for a in 0..3 {
                    sigma[a] = provider.cross_section(species[a], e)?;
                    if sigma[a] > 0.0 {
                        excess[a] = e - model.threshold_ev[a];
                    }
                }
                prepared.nodes.push(AbsorptionNode {
                    cell: k,
                    q,
                    number,
                    sigma,
                    excess_ev: excess,
                });
            }
        }
        Ok(prepared)
    }
    pub fn evaluate(
        &self,
        prepared: &PreparedAbsorption,
        absorber_cm3: [f64; 3],
        n_h_cm3: f64,
        dt_s: f64,
    ) -> Result<AbsorptionResult, ForwardError> {
        prepared.evaluate_for_cell_count(self.cell_count(), absorber_cm3, n_h_cm3, dt_s)
    }
}
struct PreparedCell {
    nodes: Vec<AbsorptionNode>,
    diagnostics: QuadratureDiagnostics,
}
fn prepare_cell(k: usize, state: &PhotonState, r: f64) -> Result<PreparedCell, ForwardError> {
    let mut diagnostics = QuadratureDiagnostics::default();
    let n = state.number[k];
    if n == 0.0 {
        return Ok(PreparedCell {
            nodes: Vec::new(),
            diagnostics,
        });
    }
    let weights = cell_quadrature(
        state.support_lo[k],
        state.support_hi[k],
        n,
        state.energy_ref[k],
        r,
        &mut diagnostics,
    )?;
    let provider = AtomicProvider::reference();
    let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
    let model = HHeModel::controlled_fixture();
    let mut nodes = Vec::with_capacity(weights.len());
    for (q, number) in weights {
        let e = q * r;
        let mut sigma = [0.0; 3];
        let mut excess = [0.0; 3];
        for a in 0..3 {
            sigma[a] = provider.cross_section(species[a], e)?;
            if sigma[a] > 0.0 {
                excess[a] = e - model.threshold_ev[a];
            }
        }
        nodes.push(AbsorptionNode {
            cell: k,
            q,
            number,
            sigma,
            excess_ev: excess,
        });
    }
    Ok(PreparedCell { nodes, diagnostics })
}

fn add_support(s: &mut PhotonState, k: usize, n: f64, u: f64, lo: f64, hi: f64) {
    if n == 0.0 {
        return;
    }
    if s.number[k] == 0.0 {
        s.support_lo[k] = lo;
        s.support_hi[k] = hi;
    } else {
        s.support_lo[k] = s.support_lo[k].min(lo);
        s.support_hi[k] = s.support_hi[k].max(hi);
    }
    s.number[k] += n;
    s.energy_ref[k] += u;
}

/// Positive quadrature of the bounded exponential, followed by a positive
/// discrete exponential tilt that reproduces the input number and energy.
fn cell_quadrature(
    lo: f64,
    hi: f64,
    n: f64,
    u: f64,
    r: f64,
    diagnostics: &mut QuadratureDiagnostics,
) -> Result<Vec<(f64, f64)>, ForwardError> {
    let mean = support_mean(lo, hi, n, u);
    if lo == hi {
        if u != lo * n {
            return Err(bad("AXBI_COVARIANT_DELTA_MOMENT"));
        }
        return Ok(vec![(lo, n)]);
    }
    if mean == lo || mean == hi {
        if mean < lo || mean > hi {
            return Err(bad("AXBI_COVARIANT_DELTA_MOMENT"));
        }
        return Ok(vec![(mean, n)]);
    }
    let width = hi - lo;
    let gap = (mean - lo).min(hi - mean);
    let beta = match positive_reconstruct(lo, hi, mean) {
        Ok(fit) => fit.beta,
        Err(_) => {
            // For |beta|>30, coth(beta)-1 differs from one by <1.76e-26.
            let b = width / (2.0 * gap);
            if !b.is_finite() || b <= 30.0 {
                return Err(bad("AXBI_COVARIANT_RECONSTRUCTION_DOMAIN"));
            }
            diagnostics.max_asymptotic_mean_defect_ev = diagnostics
                .max_asymptotic_mean_defect_ev
                .max(width * (-2.0 * b).exp() / -(-2.0 * b).exp_m1());
            if mean < 0.5 * (lo + hi) {
                -b
            } else {
                b
            }
        }
    };
    let steep = beta.abs();
    let mut points = Vec::new();
    points.push(lo);
    for cut in FIT_THRESHOLDS_EV {
        let q = cut / r;
        if q > lo && q < hi {
            points.push(q);
        }
    }
    points.push(hi);
    points.sort_by(f64::total_cmp);
    let mut base = Vec::new();
    if steep <= 30.0 {
        for pair in points.windows(2) {
            let panels = ((pair[1] - pair[0]) / width * 2.0 * steep / 3.0)
                .ceil()
                .max(1.0) as usize;
            for p in 0..panels {
                let a = pair[0] + (pair[1] - pair[0]) * p as f64 / panels as f64;
                let b = pair[0] + (pair[1] - pair[0]) * (p + 1) as f64 / panels as f64;
                let half = (b - a) * 0.5;
                for i in 0..8 {
                    let q = (a + b) * 0.5 + half * X8[i];
                    let x = 2.0 * (q - lo) / width - 1.0;
                    let weight = W8[i] * half / width * (beta * x - steep).exp();
                    if weight > 0.0 {
                        base.push((q, weight));
                    }
                }
            }
        }
    } else {
        let endpoint = if beta > 0.0 { hi } else { lo };
        let distance = width / (2.0 * steep);
        let ymax = (2.0 * steep).min(48.0);
        let mut ypoints = vec![0.0, ymax];
        for q in points {
            let y = (endpoint - q) * beta.signum() / distance;
            if y > 0.0 && y < ymax {
                ypoints.push(y);
            }
        }
        for p in 1..16 {
            let y = 3.0 * p as f64;
            if y < ymax {
                ypoints.push(y);
            }
        }
        ypoints.sort_by(f64::total_cmp);
        for pair in ypoints.windows(2) {
            let half = 0.5 * (pair[1] - pair[0]);
            for i in 0..8 {
                let y = 0.5 * (pair[0] + pair[1]) + half * X8[i];
                let q = endpoint - beta.signum() * distance * y;
                let weight = W8[i] * half * (-y).exp();
                if weight > 0.0 {
                    base.push((q, weight));
                }
            }
        }
        let tail = (-48.0_f64).exp() / -(-2.0 * steep).exp_m1();
        diagnostics.omitted_tail_number_bound_per_h += n * tail;
        diagnostics.omitted_tail_energy_bound_ev_per_h += n * hi * tail;
        diagnostics.omitted_tail_endpoint_moment_bound_ev_per_h += n * distance * 49.0 * tail;
    }
    if base.len() > MAX_NODES_PER_CELL || base.is_empty() {
        return Err(bad("AXBI_COVARIANT_QUADRATURE_CAP"));
    }
    let node_lo = base.iter().map(|x| x.0).fold(f64::INFINITY, f64::min);
    let node_hi = base.iter().map(|x| x.0).fold(f64::NEG_INFINITY, f64::max);
    if mean < node_lo || mean > node_hi {
        return Err(bad("AXBI_COVARIANT_QUADRATURE_CAP"));
    }
    let scale = gap;
    let eval = |lambda: f64| -> (Vec<f64>, f64, f64) {
        let logs: Vec<_> = base
            .iter()
            .map(|&(q, w)| w.ln() + lambda * (q - mean) / scale)
            .collect();
        let max = logs.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let weights: Vec<_> = logs.iter().map(|l| (l - max).exp()).collect();
        let total = sum(weights.iter().copied());
        let m = sum(base
            .iter()
            .zip(&weights)
            .map(|(&(q, _), w)| w * ((q - mean) / scale)))
            / total;
        let second = sum(base
            .iter()
            .zip(&weights)
            .map(|(&(q, _), w)| w * ((q - mean) / scale).powi(2)))
            / total;
        (weights, m, (second - m * m).max(0.0))
    };
    let (mut lower, mut upper) = (-1.0, 1.0);
    for _ in 0..32 {
        if eval(lower).1 <= 0.0 {
            break;
        }
        lower *= 2.0;
    }
    for _ in 0..32 {
        if eval(upper).1 >= 0.0 {
            break;
        }
        upper *= 2.0;
    }
    if eval(lower).1 > 0.0 || eval(upper).1 < 0.0 {
        return Err(bad("AXBI_COVARIANT_TILT_BRACKET"));
    }
    let mut lambda = 0.0;
    for _ in 0..80 {
        let (_, m, variance) = eval(lambda);
        if m.abs() < 8.0 * f64::EPSILON {
            break;
        }
        if m < 0.0 {
            lower = lambda;
        } else {
            upper = lambda;
        }
        let candidate = lambda - m / variance;
        lambda = if candidate.is_finite() && candidate > lower && candidate < upper {
            candidate
        } else {
            0.5 * (lower + upper)
        };
    }
    let (weights, _, _) = eval(lambda);
    let norm = sum(weights.iter().copied());
    let result: Vec<_> = base
        .iter()
        .zip(weights)
        .map(|(&(q, _), w)| (q, n * (w / norm)))
        .collect();
    let count_defect = (sum(result.iter().map(|x| x.1)) - n).abs();
    let energy_defect = (sum(result.iter().map(|x| x.0 * x.1)) - u).abs();
    let energy_scale = u.abs().max(n * width);
    if count_defect > 64.0 * f64::EPSILON * n || energy_defect > 128.0 * f64::EPSILON * energy_scale
    {
        return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
    }
    diagnostics.max_count_relative_defect =
        diagnostics.max_count_relative_defect.max(count_defect / n);
    diagnostics.max_energy_relative_defect = diagnostics
        .max_energy_relative_defect
        .max(energy_defect / energy_scale);
    Ok(result)
}

/// Diagnostic passive-compartment partition. Production callers are unchanged.
#[derive(Clone, Debug)]
pub struct HiPartition {
    pub active: PhotonState,
    pub inactive_number: Vec<f64>,
    pub inactive_energy_ref: Vec<f64>,
    pub diagnostics: QuadratureDiagnostics,
    pub quadrature_nodes: usize,
}
impl CovariantTransport {
    /// Pure restriction at actual HI fit energy. Below-HI photons retain their
    /// original reference cell and both moments; threshold equality is active.
    pub fn partition_below_hi(
        &self,
        state: &PhotonState,
        now: &GeometrySnapshot,
    ) -> Result<HiPartition, ForwardError> {
        self.validate_state(state)?;
        let rays = self.ray_geometry(now)?;
        let mut out = HiPartition {
            active: self.empty_state(),
            inactive_number: vec![0.0; self.cell_count()],
            inactive_energy_ref: vec![0.0; self.cell_count()],
            diagnostics: QuadratureDiagnostics::default(),
            quadrature_nodes: 0,
        };
        for k in 0..self.cell_count() {
            let (n, u, lo, hi) = (
                state.number[k],
                state.energy_ref[k],
                state.support_lo[k],
                state.support_hi[k],
            );
            if n == 0.0 {
                continue;
            }
            let r = rays[k / self.n_energy()].scale;
            if hi * r < FIT_THRESHOLDS_EV[0] {
                out.inactive_number[k] = n;
                out.inactive_energy_ref[k] = u;
                continue;
            }
            if lo * r >= FIT_THRESHOLDS_EV[0] {
                out.active.number[k] = n;
                out.active.energy_ref[k] = u;
                out.active.support_lo[k] = lo;
                out.active.support_hi[k] = hi;
                continue;
            }
            let cut = FIT_THRESHOLDS_EV[0] / r;
            let nodes = cell_quadrature(lo, hi, n, u, r, &mut out.diagnostics)?;
            out.quadrature_nodes += nodes.len();
            let active: Vec<_> = nodes
                .iter()
                .copied()
                .filter(|&(q, _)| q * r >= FIT_THRESHOLDS_EV[0])
                .collect();
            let passive: Vec<_> = nodes
                .iter()
                .copied()
                .filter(|&(q, _)| q * r < FIT_THRESHOLDS_EV[0])
                .collect();
            let (an, au) = restricted_moments(&active, lo.max(cut), hi);
            let (pn, pu) = restricted_moments(&passive, lo, hi.min(cut));
            let nd = (an + pn - n).abs();
            let uscale = u.abs().max(n * (hi - lo));
            let ud = (au + pu - u).abs();
            if nd > 64.0 * f64::EPSILON * n || ud > 128.0 * f64::EPSILON * uscale {
                return Err(bad("AXBI_HI_PARTITION_MOMENT_DEFECT"));
            }
            if an > 0.0 {
                out.active.number[k] = an;
                out.active.energy_ref[k] = au;
                out.active.support_lo[k] = lo.max(cut);
                out.active.support_hi[k] = hi;
            }
            if !nonnegative(pn) || !nonnegative(pu) || pu < lo * pn || pu > hi.min(cut) * pn {
                return Err(bad("AXBI_HI_PARTITION_PASSIVE_SUPPORT"));
            }
            out.inactive_number[k] = pn;
            out.inactive_energy_ref[k] = pu;
        }
        self.validate_state(&out.active)?;
        Ok(out)
    }
}
fn restricted_moments(nodes: &[(f64, f64)], lo: f64, hi: f64) -> (f64, f64) {
    let n = sum(nodes.iter().map(|&(_, n)| n));
    if n == 0.0 {
        return (0.0, 0.0);
    }
    let lower = sum(nodes.iter().map(|&(q, n)| (q - lo) * n));
    let upper = sum(nodes.iter().map(|&(q, n)| (hi - q) * n));
    let u = if lower <= upper {
        lo.mul_add(n, lower)
    } else {
        hi.mul_add(n, -upper)
    };
    (n, u)
}

impl CovariantTransport {
    /// Transactional repeated passive-pool addition in fixed reference cells.
    /// Centered moments preserve endpoint realizability without clipping.
    pub fn merge_inactive(
        &self,
        number: &mut Vec<f64>,
        energy_ref: &mut Vec<f64>,
        added_number: &[f64],
        added_energy_ref: &[f64],
    ) -> Result<(), ForwardError> {
        if [
            number.len(),
            energy_ref.len(),
            added_number.len(),
            added_energy_ref.len(),
        ]
        .iter()
        .any(|&n| n != self.cell_count())
        {
            return Err(bad("AXBI_INACTIVE_MERGE_SHAPE"));
        }
        let mut next_n = vec![0.0; self.cell_count()];
        let mut next_u = vec![0.0; self.cell_count()];
        for k in 0..self.cell_count() {
            let lo = self.edges[k % self.n_energy()];
            let hi = self.edges[k % self.n_energy() + 1];
            let (n0, u0, n1, u1) = (
                number[k],
                energy_ref[k],
                added_number[k],
                added_energy_ref[k],
            );
            if ![n0, u0, n1, u1].iter().all(|&v| nonnegative(v))
                || u0 < lo * n0
                || u0 > hi * n0
                || u1 < lo * n1
                || u1 > hi * n1
            {
                return Err(bad("AXBI_INACTIVE_MERGE_SUPPORT"));
            }
            if n1 == 0.0 {
                next_n[k] = n0;
                next_u[k] = u0;
                continue;
            }
            if n0 == 0.0 {
                next_n[k] = n1;
                next_u[k] = u1;
                continue;
            }
            let n = n0 + n1;
            let lower = (u0 - lo * n0) + (u1 - lo * n1);
            let upper = (hi * n0 - u0) + (hi * n1 - u1);
            let u = if lower <= upper {
                lo.mul_add(n, lower)
            } else {
                hi.mul_add(n, -upper)
            };
            if !nonnegative(n) || !nonnegative(u) || u < lo * n || u > hi * n {
                return Err(bad("AXBI_INACTIVE_MERGE_REALIZABILITY"));
            }
            let scale = (u0 + u1).abs().max(n * (hi - lo));
            if (u - (u0 + u1)).abs() > 128.0 * f64::EPSILON * scale {
                return Err(bad("AXBI_INACTIVE_MERGE_MOMENT_DEFECT"));
            }
            next_n[k] = n;
            next_u[k] = u;
        }
        *number = next_n;
        *energy_ref = next_u;
        Ok(())
    }
}
