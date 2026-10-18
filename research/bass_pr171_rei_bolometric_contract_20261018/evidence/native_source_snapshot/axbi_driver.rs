//! Cold point coupled driver. Binary64 backward Euler with empirical adaptivity;
//! neither an inherited FT03 certificate nor a continuum proof.
use crate::axbi_background::{
    isotropic_initial_radiation_moments, AxbiBackground, BackgroundFamily, Cosmology,
};
use crate::axbi_covariant_transport::{CovariantTransport, PhotonState, PreparedAbsorption};
use crate::axbi_parallel::OrderedWorkerPool;
use crate::axbi_rates::AxbiProvider;
use crate::axbi_sources::AxbiSource;
use crate::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use crate::igm_state::{w_erg_per_h_to_ev, w_ev_per_h_to_erg, IgmGasState};
use crate::igm_thermal::IgmPointRhs;
use crate::{ForwardError, GeometrySnapshot, HHeModel};
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
    sync::{
        atomic::{AtomicUsize, Ordering},
        Arc,
    },
    time::Instant,
};
fn err(s: &'static str) -> ForwardError {
    ForwardError::InvalidInput(s)
}
fn ioerr(_: std::io::Error) -> ForwardError {
    err("AXBI_DRIVER_IO")
}
fn f(x: f64) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(err("AXBI_DRIVER_NONFINITE"))
    }
}
#[derive(Clone, Debug)]
pub struct DriverConfig {
    pub q_ref: f64,
    pub same_h: bool,
    pub end_zbar: f64,
    pub escape_fraction: f64,
    pub initial_x_hii: f64,
    pub initial_temperature_k: f64,
    pub energy_subdivisions: usize,
    /// Fixed reference-energy finite-volume cells, independent of source quadrature.
    pub transport_cells: usize,
    /// Persistent per-cell prepare workers; temporal/Newton ordering is serial.
    pub transport_threads: usize,
    /// Opt-in independent Jacobian columns on the same persistent worker pool.
    pub parallel_jacobian_columns: bool,
    /// FLRW-only passive compartment below the HI fit cutoff; explicit variant.
    pub inactive_hi_split: bool,
    pub n_mu: usize,
    pub background_panels: usize,
    pub local_target: f64,
    pub initial_dln_a: f64,
    pub max_steps: usize,
    pub max_attempts: usize,
    pub max_rhs: usize,
    pub max_wall_s: f64,
    pub spectra_every_accepted: usize,
    /// Explicit per-stage total output allocation; physical controls unchanged.
    pub output_budget_mib: usize,
}
impl DriverConfig {
    /// Exact choices frozen in SCENARIO_LOCK; callers select explicit variants.
    pub fn baseline() -> Self {
        Self {
            q_ref: 0.0,
            same_h: false,
            end_zbar: 4.0,
            escape_fraction: 0.2,
            initial_x_hii: 2e-4,
            initial_temperature_k: 2.7255 * 21.0_f64.powi(2)
                / (150.0 * (0.0224_f64 / 0.023).powf(0.4)),
            energy_subdivisions: 16,
            transport_cells: 128,
            transport_threads: 1,
            parallel_jacobian_columns: false,
            inactive_hi_split: false,
            n_mu: 8,
            background_panels: 4096,
            local_target: 1e-5,
            initial_dln_a: 1e-4,
            max_steps: 10000,
            max_attempts: 30000,
            max_rhs: 2000000,
            max_wall_s: 1200.0,
            spectra_every_accepted: 60,
            output_budget_mib: 256,
        }
    }
    pub fn read(text: &str) -> Result<Self, ForwardError> {
        let mut c = Self::baseline();
        for line in text
            .lines()
            .filter(|s| !s.trim().is_empty() && !s.starts_with('#'))
        {
            let (k, v) = line.split_once('=').ok_or(err("AXBI_CONFIG_FORMAT"))?;
            macro_rules! number {
                ($field:ident) => {
                    c.$field = v.parse().map_err(|_| err("AXBI_CONFIG_VALUE"))?
                };
            }
            match k.trim() {
                "q_ref" => number!(q_ref),
                "same_h" => {
                    c.same_h = match v.trim() {
                        "true" => true,
                        "false" => false,
                        _ => return Err(err("AXBI_CONFIG_VALUE")),
                    }
                }
                "end_zbar" => number!(end_zbar),
                "escape_fraction" => number!(escape_fraction),
                "initial_x_hii" => number!(initial_x_hii),
                "initial_temperature_k" => number!(initial_temperature_k),
                "energy_subdivisions" => number!(energy_subdivisions),
                "transport_cells" => number!(transport_cells),
                "transport_threads" => number!(transport_threads),
                "parallel_jacobian_columns" => {
                    c.parallel_jacobian_columns = match v.trim() {
                        "true" => true,
                        "false" => false,
                        _ => return Err(err("AXBI_CONFIG_VALUE")),
                    }
                }
                "inactive_hi_split" => {
                    c.inactive_hi_split = match v.trim() {
                        "true" => true,
                        "false" => false,
                        _ => return Err(err("AXBI_CONFIG_VALUE")),
                    }
                }
                "n_mu" => number!(n_mu),
                "background_panels" => number!(background_panels),
                "local_target" => number!(local_target),
                "initial_dln_a" => number!(initial_dln_a),
                "max_steps" => number!(max_steps),
                "max_attempts" => number!(max_attempts),
                "max_rhs" => number!(max_rhs),
                "max_wall_s" => number!(max_wall_s),
                "spectra_every_accepted" => number!(spectra_every_accepted),
                "output_budget_mib" => number!(output_budget_mib),
                _ => return Err(err("AXBI_CONFIG_KEY")),
            }
        }
        c.validate()?;
        Ok(c)
    }
    pub fn scientific_output_budget_bytes(&self) -> Result<u64, ForwardError> {
        match self.output_budget_mib {
            256 => Ok(224 * 1024 * 1024),
            2048 => Ok(1920 * 1024 * 1024),
            4096 => Ok(3968 * 1024 * 1024),
            12288 => Ok(12160 * 1024 * 1024),
            _ => Err(err("AXBI_OUTPUT_ALLOCATION")),
        }
    }
    pub fn launcher_reserve_bytes(&self) -> Result<u64, ForwardError> {
        match self.output_budget_mib {
            256 => Ok(32 * 1024 * 1024),
            2048 => Ok(128 * 1024 * 1024),
            4096 => Ok(128 * 1024 * 1024),
            12288 => Ok(128 * 1024 * 1024),
            _ => Err(err("AXBI_OUTPUT_ALLOCATION")),
        }
    }
    fn validate(&self) -> Result<(), ForwardError> {
        if ![256, 2048, 4096, 12288].contains(&self.output_budget_mib)
            || (self.inactive_hi_split && self.q_ref != 0.0)
            || !(1..=64).contains(&self.transport_threads)
            || !(8..=1024).contains(&self.transport_cells)
            || self.spectra_every_accepted == 0
            || !self.q_ref.is_finite()
            || !self.end_zbar.is_finite()
            || !(4.0..20.0).contains(&self.end_zbar)
            || !self.initial_x_hii.is_finite()
            || !(0.0..=1.0).contains(&self.initial_x_hii)
            || !self.local_target.is_finite()
            || self.local_target <= 0.0
            || self.local_target >= 2e-4
            || !self.initial_dln_a.is_finite()
            || !(1e-10..=0.005).contains(&self.initial_dln_a)
            || self.max_steps == 0
            || self.max_attempts == 0
            || self.max_rhs == 0
            || !self.max_wall_s.is_finite()
            || self.max_wall_s <= 0.0
        {
            return Err(err("AXBI_CONFIG_DOMAIN"));
        }
        Ok(())
    }
}
#[derive(Clone, Debug, Default)]
pub struct Ledgers {
    pub source_n: f64,
    pub source_u: f64,
    pub absorbed_n: f64,
    pub escaped_u: f64,
    pub boundary_n: f64,
    pub boundary_u: f64,
    pub thermal_work: f64,
    pub photon_work: f64,
    pub cmb_input: f64,
    pub rr_events: [f64; 3],
    pub ci_events: [f64; 3],
    pub photo_events: [f64; 3],
    pub dr_events: f64,
    pub ci_floor_events: [f64; 3],
    pub ce_cap_ev: f64,
    pub excluded_dr_ev: f64,
}
#[derive(Clone, Debug)]
pub struct DriverState {
    pub a: f64,
    pub gas: IgmGasState,
    /// Photon count per H; all four arrays together form the physical state.
    pub photons: Vec<f64>,
    pub photon_energy_ref: Vec<f64>,
    pub photon_support_lo: Vec<f64>,
    pub photon_support_hi: Vec<f64>,
    /// Passive photons retain their original q cell and both moments.
    pub photon_inactive_number: Vec<f64>,
    pub photon_inactive_energy_ref: Vec<f64>,
    pub ledgers: Ledgers,
    pub next_dln_a: f64,
    pub accepted: usize,
    pub attempts: usize,
    /// Adaptive full-versus-two-half comparisons, distinct from trial starts.
    pub comparisons: usize,
    pub rejects: usize,
    pub consecutive_rejects: usize,
    pub rhs_evaluations: usize,
    pub max_newton_residual: f64,
    pub last_error: f64,
    pub wall_elapsed_s: f64,
}

/// Immutable inputs shared by leaf residual evaluations. This context has no
/// worker-pool handle and cannot submit nested work or mutate the stage state.
#[derive(Clone)]
struct ResidualContext {
    gas: IgmGasState,
    a: f64,
    n_h0_cm3: f64,
    n_he0_cm3: f64,
    cells: usize,
    prepared: Arc<PreparedAbsorption>,
}
impl ResidualContext {
    fn evaluate(
        &self,
        unknown: [f64; 4],
        dt: f64,
    ) -> Result<([f64; 4], PhotonState, IgmPointRhs), ForwardError> {
        let gas = IgmGasState::new(
            [unknown[0], unknown[1], unknown[2]],
            w_ev_per_h_to_erg(unknown[3])?,
        )?;
        let nh = self.n_h0_cm3 / self.a.powi(3);
        let nhe = self.n_he0_cm3 / self.a.powi(3);
        let [x, y, z] = gas.fractions;
        let absorbers = [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y];
        let c = HHeModel::controlled_fixture();
        let absorption = self
            .prepared
            .evaluate_for_cell_count(self.cells, absorbers, nh, dt)?;
        let stocks = absorption.state;
        let photo = absorption.photo;
        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;
        let mut residual = [0.0; 4];
        for i in 0..3 {
            residual[i] = unknown[i] - self.gas.fractions[i] - dt * point.rhs.fraction_dt[i];
        }
        residual[3] = unknown[3]
            - w_erg_per_h_to_ev(self.gas.w_erg_per_h)?
            - dt * point.rhs.w_dt_erg_per_h_s / c.ev_erg;
        for &r in &residual {
            f(r)?;
        }
        Ok((residual, stocks, point.rhs))
    }
}

/// Jacobian scheduling seam used by the driver and focused injected controls.
/// Workers evaluate at most one column each, with its original +/- fallback.
/// Every started residual is charged, including discarded speculative results.
#[doc(hidden)]
pub fn jacobian_columns<F>(
    pool: &OrderedWorkerPool,
    parallel: bool,
    x: [f64; 4],
    residual: [f64; 4],
    counter: &mut usize,
    max_rhs: usize,
    evaluate: F,
) -> Result<[[f64; 4]; 4], ForwardError>
where
    F: Fn([f64; 4]) -> Result<[f64; 4], ForwardError> + Send + Sync + 'static,
{
    let use_parallel =
        parallel && pool.width() > 1 && max_rhs.checked_sub(*counter).is_some_and(|n| n >= 8);
    let charged = Arc::new(AtomicUsize::new(*counter));
    let worker_charged = Arc::clone(&charged);
    let column = move |j: usize| {
        let call = |unknown| {
            worker_charged
                .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |n| {
                    if n < max_rhs {
                        Some(n + 1)
                    } else {
                        None
                    }
                })
                .map_err(|_| err("AXBI_RHS_CAP"))?;
            evaluate(unknown)
        };
        let delta = 1e-7 * x[j].abs().max(if j == 3 { 1e-6 } else { 1e-4 });
        let mut xp = x;
        xp[j] += delta;
        let (rp, sign) = match call(xp) {
            Ok(r) => (r, 1.0),
            Err(_) => {
                xp = x;
                xp[j] -= delta;
                (call(xp)?, -1.0)
            }
        };
        Ok(std::array::from_fn::<_, 4, _>(|i| {
            (rp[i] - residual[i]) / (sign * delta)
        }))
    };
    let columns = if use_parallel {
        pool.map_ordered(4, column)
    } else {
        // Preserve serial j order, early failure and cap behavior near budget.
        (0..4).map(column).collect::<Result<Vec<_>, _>>()
    };
    // Merge before propagating any numerical or worker error.
    *counter = charged.load(Ordering::Relaxed);
    let columns = columns?;
    let mut jac = [[0.0; 4]; 4];
    for j in 0..4 {
        for i in 0..4 {
            jac[i][j] = columns[j][i];
        }
    }
    Ok(jac)
}

#[derive(Clone, Debug)]
pub struct Driver {
    pub config: DriverConfig,
    pub background: AxbiBackground,
    pub source: AxbiSource,
    pub energies: Vec<f64>,
    pub n_h0_cm3: f64,
    pub n_he0_cm3: f64,
    pub transport: CovariantTransport,
    initial_energy: f64,
}
impl Driver {
    pub fn new(config: DriverConfig) -> Result<(Self, DriverState), ForwardError> {
        config.validate()?;
        let h0 = 67.4 * 1e5 / 3.0856775814913673e24;
        let a_ref = 1.0_f64 / 21.0;
        let a_end = 1.0 / (1.0 + config.end_zbar);
        let flat = FlatFlrwBackground::new(FlatFlrwConfig {
            h0_per_s: h0,
            omega_r: 9.2e-5,
            omega_m: 0.315,
            omega_b: 0.0224 / 0.674_f64.powi(2),
            omega_lambda: 1.0 - 0.315 - 9.2e-5,
            helium_mass_fraction: 0.2454,
            tcmb0_k: 2.7255,
            ln_a_min: a_ref.ln(),
            ln_a_max: a_end.ln(),
            parameter_source: "AX01_SCENARIO_LOCK".into(),
        })?;
        let n_h0 = flat.n_h_comoving_cm3();
        let f_he = 0.2454 / (4.0 * (1.0 - 0.2454));
        let n_he0 = n_h0 * f_he;
        let bg = AxbiBackground::new(
            Cosmology {
                h0_per_s: h0,
                omega_m: 0.315,
                omega_r: 9.2e-5,
                omega_lambda: 1.0 - 0.315 - 9.2e-5,
            },
            a_ref,
            a_end,
            0.0,
            config.q_ref,
            if config.same_h {
                BackgroundFamily::SameHDiagnostic
            } else {
                BackgroundFamily::PhysicalDensityFixed
            },
            config.background_panels,
        )?;
        let source = AxbiSource::new(
            n_h0,
            config.escape_fraction,
            config.energy_subdivisions,
            config.n_mu,
        )?;
        let reference = bg.point_at_scale(a_ref)?.geometry()?;
        let transport =
            CovariantTransport::new(&source, reference, config.transport_cells, 13.6, 512.0)?
                .with_threads(config.transport_threads)?;
        let energies = (0..config.transport_cells)
            .map(|i| {
                13.6 * (512.0_f64 / 13.6).powf((i as f64 + 0.5) / config.transport_cells as f64)
            })
            .collect::<Vec<_>>();
        let gas = IgmGasState::from_temperature(
            [config.initial_x_hii, 0.0, 0.0],
            n_h0 / a_ref.powi(3),
            n_he0 / a_ref.powi(3),
            config.initial_temperature_k,
        )?;
        let photon_state = transport.empty_state();
        let state = DriverState {
            a: a_ref,
            gas,
            photons: photon_state.number,
            photon_energy_ref: photon_state.energy_ref,
            photon_support_lo: photon_state.support_lo,
            photon_support_hi: photon_state.support_hi,
            photon_inactive_number: vec![0.0; transport.cell_count()],
            photon_inactive_energy_ref: vec![0.0; transport.cell_count()],
            ledgers: Ledgers::default(),
            next_dln_a: config.initial_dln_a,
            accepted: 0,
            attempts: 0,
            comparisons: 0,
            rejects: 0,
            consecutive_rejects: 0,
            rhs_evaluations: 0,
            max_newton_residual: 0.0,
            last_error: 0.0,
            wall_elapsed_s: 0.0,
        };
        let mut driver = Self {
            config,
            background: bg,
            source,
            energies,
            n_h0_cm3: n_h0,
            n_he0_cm3: n_he0,
            transport,
            initial_energy: 0.0,
        };
        driver.initial_energy = driver.total_energy(&state)?;
        Ok((driver, state))
    }
    fn photon_state(&self, state: &DriverState) -> PhotonState {
        PhotonState {
            number: state.photons.clone(),
            energy_ref: state.photon_energy_ref.clone(),
            support_lo: state.photon_support_lo.clone(),
            support_hi: state.photon_support_hi.clone(),
        }
    }
    fn set_photon_state(state: &mut DriverState, photons: PhotonState) {
        state.photons = photons.number;
        state.photon_energy_ref = photons.energy_ref;
        state.photon_support_lo = photons.support_lo;
        state.photon_support_hi = photons.support_hi;
    }
    fn validate_inactive(
        &self,
        state: &DriverState,
        geometry: &GeometrySnapshot,
    ) -> Result<(), ForwardError> {
        let count = self.transport.cell_count();
        if state.photon_inactive_number.len() != count
            || state.photon_inactive_energy_ref.len() != count
        {
            return Err(err("AXBI_INACTIVE_SHAPE"));
        }
        let rays = self.transport.ray_geometry(geometry)?;
        let edges = self.transport.edges();
        for j in 0..count {
            let n = f(state.photon_inactive_number[j])?;
            let u = f(state.photon_inactive_energy_ref[j])?;
            if n < 0.0 || u < 0.0 || (!self.config.inactive_hi_split && (n != 0.0 || u != 0.0)) {
                return Err(err("AXBI_INACTIVE_DOMAIN_OR_MODE"));
            }
            if n == 0.0 {
                if u != 0.0 {
                    return Err(err("AXBI_INACTIVE_EMPTY_ENERGY"));
                }
            } else {
                let i = j % self.energies.len();
                let scale = rays[j / self.energies.len()].scale;
                let upper = edges[i + 1].min(13.6 / scale);
                if u < edges[i] * n || u > upper * n {
                    return Err(err("AXBI_INACTIVE_SUPPORT_OR_REACTIVATION"));
                }
            }
        }
        Ok(())
    }
    /// [active N, active physical U, passive N, passive physical U].
    pub fn photon_pool_inventory(&self, state: &DriverState) -> Result<[f64; 4], ForwardError> {
        let geometry = self.background.point_at_scale(state.a)?.geometry()?;
        self.pool_inventory_with_geometry(state, &geometry)
    }
    fn pool_inventory_with_geometry(
        &self,
        state: &DriverState,
        geometry: &GeometrySnapshot,
    ) -> Result<[f64; 4], ForwardError> {
        self.validate_inactive(state, geometry)?;
        let (n, u) = self
            .transport
            .inventory(&self.photon_state(state), geometry)?;
        let rays = self.transport.ray_geometry(geometry)?;
        let pn = state.photon_inactive_number.iter().sum::<f64>();
        let pu = state
            .photon_inactive_energy_ref
            .iter()
            .enumerate()
            .map(|(j, &v)| v * rays[j / self.energies.len()].scale)
            .sum::<f64>();
        Ok([n, u, f(pn)?, f(pu)?])
    }
    fn inventory_with_geometry(
        &self,
        state: &DriverState,
        geometry: &GeometrySnapshot,
    ) -> Result<(f64, f64), ForwardError> {
        let [n, u, pn, pu] = self.pool_inventory_with_geometry(state, geometry)?;
        Ok((f(n + pn)?, f(u + pu)?))
    }
    fn partition_inactive(
        &self,
        state: &mut DriverState,
        geometry: &GeometrySnapshot,
    ) -> Result<(), ForwardError> {
        if !self.config.inactive_hi_split {
            return Ok(());
        }
        self.validate_inactive(state, geometry)?;
        let partition = self
            .transport
            .partition_below_hi(&self.photon_state(state), geometry)?;
        let mut pn = state.photon_inactive_number.clone();
        let mut pu = state.photon_inactive_energy_ref.clone();
        self.transport.merge_inactive(
            &mut pn,
            &mut pu,
            &partition.inactive_number,
            &partition.inactive_energy_ref,
        )?;
        // Validate the complete candidate before committing either compartment.
        let mut next = state.clone();
        Self::set_photon_state(&mut next, partition.active);
        next.photon_inactive_number = pn;
        next.photon_inactive_energy_ref = pu;
        self.validate_inactive(&next, geometry)?;
        *state = next;
        Ok(())
    }
    /// Preserved infallible diagnostic API. Invalid photon state yields NaNs;
    /// every mutating production entry point validates the complete state.
    pub fn photon_inventory(&self, state: &DriverState) -> (f64, f64) {
        self.background
            .point_at_scale(state.a)
            .and_then(|p| p.geometry())
            .and_then(|g| self.inventory_with_geometry(state, &g))
            .unwrap_or((f64::NAN, f64::NAN))
    }
    /// Explicit delta fixture: q is reference-frame energy, with no redshift
    /// projection. This only seeds photon state; callers own source ledgers.
    pub fn seed_delta(
        &self,
        state: &mut DriverState,
        ray: usize,
        q: f64,
        count: f64,
    ) -> Result<(), ForwardError> {
        let mut photons = self.photon_state(state);
        self.transport.add_delta(&mut photons, ray, q, count)?;
        Self::set_photon_state(state, photons);
        Ok(())
    }
    fn binding(&self, gas: &IgmGasState) -> f64 {
        let chi = HHeModel::controlled_fixture().threshold_ev;
        let [x, y, z] = gas.fractions;
        chi[0] * x + self.n_he0_cm3 / self.n_h0_cm3 * (chi[1] * y + (chi[1] + chi[2]) * z)
    }
    pub fn total_energy(&self, s: &DriverState) -> Result<f64, ForwardError> {
        let (_, u) = self.photon_inventory(s);
        f(w_erg_per_h_to_ev(s.gas.w_erg_per_h)?
            + self.binding(&s.gas)
            + u
            + s.ledgers.escaped_u
            + s.ledgers.boundary_u
            + s.ledgers.thermal_work
            + s.ledgers.photon_work
            - s.ledgers.source_u
            - s.ledgers.cmb_input)
    }
    pub fn residuals(&self, s: &DriverState) -> Result<(f64, f64), ForwardError> {
        let (n, _) = self.photon_inventory(s);
        Ok((
            f(n + s.ledgers.absorbed_n + s.ledgers.boundary_n - s.ledgers.source_n)?,
            f(self.total_energy(s)? - self.initial_energy)?,
        ))
    }
    /// Legacy diagnostic nodal deposit only. Does not construct a physical
    /// DriverState: use seed_delta for complete N/U/support fixtures.
    /// Production injection/geometry/absorption never calls this method.
    pub fn deposit(
        &self,
        stocks: &mut [f64],
        ray: usize,
        energy: f64,
        count: f64,
    ) -> Result<(f64, f64), ForwardError> {
        if !energy.is_finite()
            || energy <= 0.0
            || !count.is_finite()
            || count < 0.0
            || ray >= self.source.angular_cells.len()
            || stocks.len() != self.energies.len() * self.source.angular_cells.len()
        {
            return Err(err("AXBI_DEPOSIT_DOMAIN"));
        }
        if energy < self.energies[0] {
            return Ok((count, count * energy));
        }
        if energy > *self.energies.last().unwrap() {
            return Err(err("AXBI_ABOVE_SUPPORT"));
        }
        let hi = self.energies.partition_point(|&e| e < energy);
        let offset = ray * self.energies.len();
        if hi == 0 || self.energies[hi] == energy {
            stocks[offset + hi] += count;
        } else {
            let lo = hi - 1;
            let w = (energy - self.energies[lo]) / (self.energies[hi] - self.energies[lo]);
            stocks[offset + lo] += count * (1.0 - w);
            stocks[offset + hi] += count * w;
        }
        Ok((0.0, 0.0))
    }
    pub fn geometry_map(&self, s: &mut DriverState, to: f64) -> Result<(), ForwardError> {
        if self.config.inactive_hi_split && to < s.a {
            return Err(err("AXBI_INACTIVE_REVERSE_GEOMETRY"));
        }
        let g0 = self.background.point_at_scale(s.a)?.geometry()?;
        let g1 = self.background.point_at_scale(to)?.geometry()?;
        let (_, old_u) = self.inventory_with_geometry(s, &g0)?;
        let (_, new_u) = self.inventory_with_geometry(s, &g1)?;
        self.partition_inactive(s, &g1)?;
        s.ledgers.photon_work += old_u - new_u;
        let old_w = w_erg_per_h_to_ev(s.gas.w_erg_per_h)?;
        s.gas = s.gas.adiabatic_to(s.a, to)?;
        s.ledgers.thermal_work += old_w - w_erg_per_h_to_ev(s.gas.w_erg_per_h)?;
        s.a = to;
        let eos = s
            .gas
            .eos(self.n_h0_cm3 / to.powi(3), self.n_he0_cm3 / to.powi(3))?;
        AxbiProvider.rates(eos.temperature_k)?;
        Ok(())
    }
    fn inject(&self, s: &mut DriverState, dt: f64) -> Result<(), ForwardError> {
        let geometry = self.background.point_at_scale(s.a)?.geometry()?;
        let mut photons = self.photon_state(s);
        let emitted = self
            .transport
            .inject(&mut photons, &geometry, 1.0 / s.a - 1.0, dt)?;
        s.ledgers.source_n += emitted.added_photons_per_h;
        s.ledgers.source_u += emitted.added_energy_ev_per_h;
        Self::set_photon_state(s, photons);
        Ok(())
    }
    fn evaluate(
        &self,
        context: &ResidualContext,
        unknown: [f64; 4],
        dt: f64,
        counter: &mut usize,
    ) -> Result<([f64; 4], PhotonState, IgmPointRhs), ForwardError> {
        if *counter >= self.config.max_rhs {
            return Err(err("AXBI_RHS_CAP"));
        }
        *counter += 1;
        context.evaluate(unknown, dt)
    }
    fn norm(&self, residual: [f64; 4], old_w: f64, new_w: f64) -> f64 {
        residual[0]
            .abs()
            .max(residual[1].abs())
            .max(residual[2].abs())
            .max(residual[3].abs() / old_w.abs().max(new_w.abs()).max(1e-6))
    }
    pub fn chemical_stage(
        &self,
        s: &mut DriverState,
        dt: f64,
        counter: &mut usize,
    ) -> Result<(), ForwardError> {
        if !dt.is_finite() || dt <= 0.0 {
            return Err(err("AXBI_STAGE_DT"));
        }
        let geometry = self.background.point_at_scale(s.a)?.geometry()?;
        let mut old = s.clone();
        self.partition_inactive(&mut old, &geometry)?;
        // Quadrature reconstruction is fixed across the Newton residual/Jacobian
        // evaluations; only trial absorber densities enter backward Euler.
        let prepared = self
            .transport
            .prepare(&self.photon_state(&old), &geometry)?;
        let context = ResidualContext {
            gas: old.gas,
            a: old.a,
            n_h0_cm3: self.n_h0_cm3,
            n_he0_cm3: self.n_he0_cm3,
            cells: self.transport.cell_count(),
            prepared: Arc::new(prepared),
        };
        let old_w = w_erg_per_h_to_ev(old.gas.w_erg_per_h)?;
        let mut x = [
            old.gas.fractions[0],
            old.gas.fractions[1],
            old.gas.fractions[2],
            old_w,
        ];
        for _ in 0..50 {
            let (residual, stocks, rhs) = self.evaluate(&context, x, dt, counter)?;
            let norm = self.norm(residual, old_w, x[3]);
            if norm <= 1e-11 {
                let nh = self.n_h0_cm3 / old.a.powi(3);
                let c = HHeModel::controlled_fixture();
                let nold = old.photons.iter().sum::<f64>();
                let nnew = stocks.number.iter().sum::<f64>();
                let events = rhs.photo_events_cm3_s.map(|e| e * dt / nh);
                let event_total = events.iter().sum::<f64>();
                if (nold - nnew - event_total).abs() > 1e-10 * old.ledgers.source_n.max(1.0) {
                    return Err(err("AXBI_ABSORPTION_LEDGER"));
                }
                let mut next = old.clone();
                next.gas = IgmGasState::new([x[0], x[1], x[2]], w_ev_per_h_to_erg(x[3])?)?;
                Self::set_photon_state(&mut next, stocks);
                next.ledgers.absorbed_n += event_total;
                for k in 0..3 {
                    next.ledgers.photo_events[k] += events[k];
                    next.ledgers.rr_events[k] += rhs.rr_events_cm3_s[k] * dt / nh;
                    next.ledgers.ci_events[k] += rhs.ci_events_cm3_s[k] * dt / nh;
                    next.ledgers.ci_floor_events[k] += rhs.ci_floor_events_cm3_s[k] * dt / nh;
                }
                next.ledgers.dr_events += rhs.dr_events_cm3_s * dt / nh;
                next.ledgers.ce_cap_ev +=
                    rhs.ce_cap_cooling_erg_cm3_s.iter().sum::<f64>() * dt / (nh * c.ev_erg);
                next.ledgers.excluded_dr_ev +=
                    rhs.excluded_dr_cooling_erg_cm3_s * dt / (nh * c.ev_erg);
                next.ledgers.escaped_u += rhs.escape_erg_cm3_s * dt / (nh * c.ev_erg);
                next.ledgers.cmb_input += rhs.cmb_to_gas_erg_cm3_s * dt / (nh * c.ev_erg);
                next.max_newton_residual = next.max_newton_residual.max(norm);
                *s = next;
                return Ok(());
            }
            let columns_context = context.clone();
            let jac = jacobian_columns(
                &self.transport.shared_pool(),
                self.config.parallel_jacobian_columns,
                x,
                residual,
                counter,
                self.config.max_rhs,
                move |unknown| columns_context.evaluate(unknown, dt).map(|v| v.0),
            )?;
            let direction = solve4(jac, residual.map(|r| -r))?;
            let mut alpha = 1.0;
            let mut accepted = None;
            for _ in 0..40 {
                let trial = std::array::from_fn(|i| x[i] + alpha * direction[i]);
                if let Ok((r, _, _)) = self.evaluate(&context, trial, dt, counter) {
                    if self.norm(r, old_w, trial[3]) < norm {
                        accepted = Some(trial);
                        break;
                    }
                }
                alpha *= 0.5;
            }
            x = accepted.ok_or(err("AXBI_NEWTON_LINESEARCH"))?;
        }
        Err(err("AXBI_NEWTON_ITERATIONS"))
    }
    fn tentative(
        &self,
        old: &DriverState,
        to: f64,
        counter: &mut usize,
    ) -> Result<DriverState, ForwardError> {
        let mut s = old.clone();
        let mid = (old.a * to).sqrt();
        let dt = self.background.interval_increment(old.a, to)?.proper_time_s;
        self.geometry_map(&mut s, mid)?;
        self.inject(&mut s, dt)?;
        self.chemical_stage(&mut s, dt, counter)?;
        self.geometry_map(&mut s, to)?;
        self.validate(&s, 1e-8)?;
        let (n0, u0) = self.residuals(old)?;
        let (n1, u1) = self.residuals(&s)?;
        if (n1 - n0).abs() > 1e-10 * s.ledgers.source_n.max(1.0)
            || (u1 - u0).abs() > 1e-10 * s.ledgers.source_u.max(1.0)
        {
            return Err(err("AXBI_STEP_LEDGER"));
        }
        Ok(s)
    }
    pub fn validate(&self, s: &DriverState, tolerance: f64) -> Result<(), ForwardError> {
        let eos = s
            .gas
            .eos(self.n_h0_cm3 / s.a.powi(3), self.n_he0_cm3 / s.a.powi(3))?;
        AxbiProvider.rates(eos.temperature_k)?;
        let geometry = self.background.point_at_scale(s.a)?.geometry()?;
        self.inventory_with_geometry(s, &geometry)?;
        for &n in &s.photons {
            if f(n)? < 0.0 {
                return Err(err("AXBI_STOCK_NEGATIVE"));
            }
        }
        let (n, u) = self.residuals(s)?;
        if n.abs() > tolerance * s.ledgers.source_n.max(1.0)
            || u.abs() > tolerance * s.ledgers.source_u.max(1.0)
        {
            return Err(err("AXBI_CUMULATIVE_LEDGER"));
        }
        let moments = self.moments(s)?;
        if moments[1].abs() > 1e-12 * moments[0].max(1e-30) {
            return Err(err("AXBI_PARITY"));
        }
        Ok(())
    }
    pub fn error_metric(
        &self,
        full: &DriverState,
        half: &DriverState,
    ) -> Result<f64, ForwardError> {
        self.transport.validate_state(&self.photon_state(full))?;
        self.transport.validate_state(&self.photon_state(half))?;
        let geometry = self.background.point_at_scale(half.a)?.geometry()?;
        self.validate_inactive(full, &geometry)?;
        self.validate_inactive(half, &geometry)?;
        let mut e = 0.0_f64;
        for i in 0..3 {
            e = e.max(
                (full.gas.fractions[i] - half.gas.fractions[i]).abs()
                    / half.gas.fractions[i].abs().max(1e-5),
            );
        }
        let w = w_erg_per_h_to_ev(half.gas.w_erg_per_h)?;
        e = e.max((w_erg_per_h_to_ev(full.gas.w_erg_per_h)? - w).abs() / w.abs().max(1e-6));
        let (n, u) = self.photon_inventory(half);
        if full.photons.len() != half.photons.len()
            || full.photon_energy_ref.len() != half.photon_energy_ref.len()
        {
            return Err(err("AXBI_PHOTON_SHAPE"));
        }
        let dn = full
            .photons
            .iter()
            .zip(&half.photons)
            .zip(
                full.photon_inactive_number
                    .iter()
                    .zip(&half.photon_inactive_number),
            )
            .map(|((a, b), (pa, pb))| (a - b).abs() + (pa - pb).abs())
            .sum::<f64>();
        let mut du = 0.0;
        let ne = self.energies.len();
        let rays = self.transport.ray_geometry(&geometry)?;
        for (k, ray) in rays.iter().enumerate() {
            for i in 0..ne {
                let j = k * ne + i;
                du += ((full.photon_energy_ref[j] - half.photon_energy_ref[j]).abs()
                    + (full.photon_inactive_energy_ref[j] - half.photon_inactive_energy_ref[j])
                        .abs())
                    * ray.scale;
            }
        }
        f(e.max(dn / n.max(1e-8)).max(du / u.max(1e-8)))
    }
    pub fn adaptive_step(&self, s: &mut DriverState) -> Result<bool, ForwardError> {
        if s.accepted >= self.config.max_steps || s.attempts >= self.config.max_attempts {
            return Err(err("AXBI_STEP_CAP"));
        }
        let endpoint = 1.0 / (1.0 + self.config.end_zbar);
        if s.a == endpoint {
            return Ok(true);
        }
        let to = (s.a * s.next_dln_a.exp()).min(endpoint);
        let mid = (s.a * to).sqrt();
        let mut counter = s.rhs_evaluations;
        let mut trial_starts = s.attempts;
        s.comparisons += 1;
        let result = (|| {
            let mut launch = |old: &DriverState, endpoint: f64| {
                if trial_starts >= self.config.max_attempts {
                    return Err(err("AXBI_TENTATIVE_CAP"));
                }
                trial_starts += 1;
                self.tentative(old, endpoint, &mut counter)
            };
            let full = launch(s, to)?;
            let first = launch(s, mid)?;
            let half = launch(&first, to)?;
            let metric = self.error_metric(&full, &half)?;
            Ok::<_, ForwardError>((half, metric))
        })();
        s.rhs_evaluations = counter;
        s.attempts = trial_starts;
        match result {
            Ok((mut next, e)) if e < self.config.local_target && e < 2e-4 => {
                next.accepted = s.accepted + 1;
                next.attempts = s.attempts;
                next.comparisons = s.comparisons;
                next.rejects = s.rejects;
                next.rhs_evaluations = counter;
                next.consecutive_rejects = 0;
                next.last_error = e;
                next.next_dln_a = if e < self.config.local_target * 0.25 {
                    (s.next_dln_a * 2.0).min(0.005)
                } else {
                    s.next_dln_a
                };
                next.wall_elapsed_s = s.wall_elapsed_s;
                *s = next;
                Ok(true)
            }
            outcome => {
                if let Ok((_, metric)) = &outcome {
                    s.last_error = *metric;
                }
                s.rejects += 1;
                s.consecutive_rejects += 1;
                s.next_dln_a *= 0.5;
                if let Err(e) = outcome {
                    return Err(e);
                }
                Ok(false)
            }
        }
    }
    pub fn moments(&self, s: &DriverState) -> Result<[f64; 3], ForwardError> {
        let gref = self.background.point_at_scale(1.0 / 21.0)?.geometry()?;
        let current = self.background.point_at_scale(s.a)?.geometry()?;
        self.moments_with_geometry(s, &gref, &current)
    }
    fn moments_with_geometry(
        &self,
        s: &DriverState,
        _reference: &GeometrySnapshot,
        current: &GeometrySnapshot,
    ) -> Result<[f64; 3], ForwardError> {
        let mut moments = [0.0; 3];
        let ne = self.energies.len();
        let rays = self.transport.ray_geometry(current)?;
        for (k, ray) in rays.iter().enumerate() {
            let mu = ray.mu;
            for i in 0..ne {
                let j = k * ne + i;
                let u = (s.photon_energy_ref[j] + s.photon_inactive_energy_ref[j]) * ray.scale;
                moments[0] += u;
                moments[1] += u * mu;
                moments[2] += u * (3.0 * mu * mu - 1.0) / 2.0;
            }
        }
        Ok(moments)
    }
}
fn solve4(mut a: [[f64; 4]; 4], mut b: [f64; 4]) -> Result<[f64; 4], ForwardError> {
    for k in 0..4 {
        let pivot = (k..4)
            .max_by(|&i, &j| a[i][k].abs().total_cmp(&a[j][k].abs()))
            .unwrap();
        if a[pivot][k].abs() < 1e-30 || !a[pivot][k].is_finite() {
            return Err(err("AXBI_SINGULAR_JACOBIAN"));
        }
        a.swap(k, pivot);
        b.swap(k, pivot);
        for i in k + 1..4 {
            let factor = a[i][k] / a[k][k];
            for j in k..4 {
                a[i][j] -= factor * a[k][j];
            }
            b[i] -= factor * b[k];
        }
    }
    let mut x = [0.0; 4];
    for i in (0..4).rev() {
        x[i] = f((b[i] - (i + 1..4).map(|j| a[i][j] * x[j]).sum::<f64>()) / a[i][i])?;
    }
    Ok(x)
}

/// Compiled source bytes; checked exactly with the saved record on resume.
/// This is a reproducibility binding, not an adversarial seal.
pub fn compiled_identity() -> String {
    [
        include_str!("axbi_driver.rs"),
        include_str!("axbi_covariant_transport.rs"),
        include_str!("axbi_parallel.rs"),
        include_str!("../../../research/flrw_jacobian_columns_20261016/CONTRACT.json"),
        include_str!("axbi_q_closure.rs"),
        include_str!("axbi_background.rs"),
        include_str!("axbi_sources.rs"),
        include_str!("axbi_rates.rs"),
        include_str!("igm_rates.rs"),
        include_str!("igm_thermal.rs"),
        include_str!("igm_state.rs"),
        include_str!("igm_background.rs"),
        include_str!("atomic_provider.rs"),
        include_str!("bianchi_i.rs"),
        include_str!("hhe_events.rs"),
        include_str!("../examples/axbi_reionization.rs"),
        include_str!("lib.rs"),
        include_str!("../Cargo.toml"),
        include_str!(
            "../../../docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json"
        ),
        include_str!("../../../research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json"),
        include_str!("../../../research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md"),
        include_str!("../../../research/flrw_covariant_transport_20261015/NATIVE_CONTRACT.md"),
        include_str!(
            "../../../research/flrw_covariant_transport_20261015/INACTIVE_POOL_CONTRACT.md"
        ),
        include_str!("../../../research/flrw_covariant_transport_20261015/HPC_CONTRACT.md"),
        include_str!(
            "../../../research/flrw_covariant_transport_20261015/BACKGROUND_CACHE_CONTRACT.md"
        ),
        include_str!(
            "../../../research/flrw_covariant_transport_20261015/OUTPUT_ALLOCATION_005_CONTRACT.md"
        ),
    ]
    .join("\nAXBI_SOURCE_BOUNDARY\n")
}
fn ledger_values(l: &Ledgers) -> Vec<f64> {
    let mut v = vec![
        l.source_n,
        l.source_u,
        l.absorbed_n,
        l.escaped_u,
        l.boundary_n,
        l.boundary_u,
        l.thermal_work,
        l.photon_work,
        l.cmb_input,
        l.dr_events,
        l.ce_cap_ev,
        l.excluded_dr_ev,
    ];
    for a in [l.rr_events, l.ci_events, l.photo_events, l.ci_floor_events] {
        v.extend(a);
    }
    v
}
fn ledger_from(v: &[f64]) -> Result<Ledgers, ForwardError> {
    if v.len() != 24 {
        return Err(err("AXBI_CHECKPOINT_LEDGER"));
    }
    for &x in v {
        f(x)?;
    }
    let array = |i| [v[i], v[i + 1], v[i + 2]];
    Ok(Ledgers {
        source_n: v[0],
        source_u: v[1],
        absorbed_n: v[2],
        escaped_u: v[3],
        boundary_n: v[4],
        boundary_u: v[5],
        thermal_work: v[6],
        photon_work: v[7],
        cmb_input: v[8],
        dr_events: v[9],
        ce_cap_ev: v[10],
        excluded_dr_ev: v[11],
        rr_events: array(12),
        ci_events: array(15),
        photo_events: array(18),
        ci_floor_events: array(21),
    })
}
fn list(v: &[f64]) -> String {
    v.iter()
        .map(|x| format!("{x:.17e}"))
        .collect::<Vec<_>>()
        .join(" ")
}
fn parse_list(s: &str) -> Result<Vec<f64>, ForwardError> {
    s.split_whitespace()
        .map(|t| {
            t.parse::<f64>()
                .map_err(|_| err("AXBI_CHECKPOINT_FORMAT"))
                .and_then(f)
        })
        .collect()
}
impl Driver {
    fn checkpoint_text(&self, s: &DriverState) -> Result<String, ForwardError> {
        self.transport.validate_state(&self.photon_state(s))?;
        let p = self.background.point_at_scale(s.a)?;
        self.validate_inactive(s, &p.geometry()?)?;
        let text = format!(
            "AXBI_CHECKPOINT_V4\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n",
            list(&[
                s.a,
                p.time_s,
                p.b,
                s.gas.fractions[0],
                s.gas.fractions[1],
                s.gas.fractions[2],
                s.gas.w_erg_per_h,
                s.next_dln_a,
                s.max_newton_residual,
                s.last_error,
                s.wall_elapsed_s
            ]),
            [
                s.accepted,
                s.attempts,
                s.rejects,
                s.consecutive_rejects,
                s.rhs_evaluations,
                s.comparisons
            ]
            .iter()
            .map(|n| n.to_string())
            .collect::<Vec<_>>()
            .join(" "),
            list(&ledger_values(&s.ledgers)),
            list(&s.photons),
            list(&s.photon_energy_ref),
            list(&s.photon_support_lo),
            list(&s.photon_support_hi),
            list(&s.photon_inactive_number),
            list(&s.photon_inactive_energy_ref),
            list(&[self.initial_energy])
        );
        Ok(text)
    }
    pub fn save_checkpoint(&self, path: &Path, s: &DriverState) -> Result<(), ForwardError> {
        let text = self.checkpoint_text(s)?;
        write_checkpoint(path, &text)
    }
    pub fn save_checkpoint_budget(
        &self,
        out: &Path,
        path: &Path,
        s: &DriverState,
    ) -> Result<(), ForwardError> {
        let text = self.checkpoint_text(s)?;
        // Existing destination remains during temporary write: include both.
        guard_output_bytes_with_limit(
            out,
            text.len() as u64,
            self.config.scientific_output_budget_bytes()?,
        )?;
        write_checkpoint(path, &text)
    }
    pub fn read_checkpoint(&self, path: &Path) -> Result<DriverState, ForwardError> {
        let text = fs::read_to_string(path).map_err(ioerr)?;
        let lines = text.lines().collect::<Vec<_>>();
        if lines.len() != 11 || lines[0] != "AXBI_CHECKPOINT_V4" {
            return Err(err("AXBI_CHECKPOINT_VERSION"));
        }
        let v = parse_list(lines[1])?;
        let counts = lines[2]
            .split_whitespace()
            .map(|s| s.parse::<usize>().map_err(|_| err("AXBI_CHECKPOINT_COUNT")))
            .collect::<Result<Vec<_>, _>>()?;
        let l = ledger_from(&parse_list(lines[3])?)?;
        let photons = parse_list(lines[4])?;
        let photon_energy_ref = parse_list(lines[5])?;
        let photon_support_lo = parse_list(lines[6])?;
        let photon_support_hi = parse_list(lines[7])?;
        let photon_inactive_number = parse_list(lines[8])?;
        let photon_inactive_energy_ref = parse_list(lines[9])?;
        let initial = parse_list(lines[10])?;
        if v.len() != 11
            || counts.len() != 6
            || photons.len() != self.energies.len() * self.source.angular_cells.len()
            || initial != vec![self.initial_energy]
        {
            return Err(err("AXBI_CHECKPOINT_SHAPE_OR_INITIAL"));
        }
        let p = self.background.point_at_scale(v[0])?;
        if p.time_s != v[1] || p.b != v[2] || !(1e-10..=0.005).contains(&v[7]) || v[10] < 0.0 {
            return Err(err("AXBI_CHECKPOINT_CLOCK_OR_STEP"));
        }
        let state = DriverState {
            a: v[0],
            gas: IgmGasState::new([v[3], v[4], v[5]], v[6])?,
            photons,
            photon_energy_ref,
            photon_support_lo,
            photon_support_hi,
            photon_inactive_number,
            photon_inactive_energy_ref,
            ledgers: l,
            next_dln_a: v[7],
            max_newton_residual: v[8],
            last_error: v[9],
            wall_elapsed_s: v[10],
            accepted: counts[0],
            attempts: counts[1],
            rejects: counts[2],
            consecutive_rejects: counts[3],
            rhs_evaluations: counts[4],
            comparisons: counts[5],
        };
        self.validate(&state, 1e-8)?;
        Ok(state)
    }
    pub fn output_row(
        &self,
        s: &DriverState,
        case: &str,
        history: &mut impl Write,
        abundances: &mut impl Write,
        spectra: &mut impl Write,
        ledgers: &mut impl Write,
        feedback: &mut impl Write,
    ) -> Result<(), ForwardError> {
        let p = self.background.point_at_scale(s.a)?;
        let nh = self.n_h0_cm3 / s.a.powi(3);
        let nhe = self.n_he0_cm3 / s.a.powi(3);
        let eos = s.gas.eos(nh, nhe)?;
        let [x, y, z] = s.gas.fractions;
        let gr = self.background.point_at_scale(1.0 / 21.0)?.geometry()?;
        let g = p.geometry()?;
        let m = self.moments_with_geometry(s, &gr, &g)?;
        let (n, u) = self.photon_inventory(s);
        let c = HHeModel::controlled_fixture();
        let ne = self.energies.len();
        // Zero-duration backward Euler leaves photons untouched and yields the
        // instantaneous photo rates using actual local energies and supports.
        let prepared = self.transport.prepare(&self.photon_state(s), &g)?;
        let gamma = self
            .transport
            .evaluate(
                &prepared,
                [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y],
                nh,
                0.0,
            )?
            .photo
            .gamma_s;
        writeln!(
            history,
            "{case},{},{},{},{},{},{},{},{},{x},{y},{z},{nh},{},{},{},{},{},{n},{u},{},{},{},{},{}",
            self.config.q_ref,
            p.sigma,
            p.time_s,
            s.a,
            1.0 / s.a - 1.0,
            p.b,
            p.h_per_s,
            p.s_per_s,
            eos.electron_density_cm3,
            eos.temperature_k,
            gamma[0],
            gamma[1],
            gamma[2],
            m[0],
            m[1],
            m[2],
            1.0 - x,
            1.0 - y - z
        )
        .map_err(ioerr)?;
        let nb = nh + 4.0 * nhe;
        for (id, a, z_nuc, charge, density, fraction) in [
            ("H_I", 1, 1, 0, nh * (1.0 - x), 1.0 - x),
            ("H_II", 1, 1, 1, nh * x, x),
            ("He_I", 4, 2, 0, nhe * (1.0 - y - z), 1.0 - y - z),
            ("He_II", 4, 2, 1, nhe * y, y),
            ("He_III", 4, 2, 2, nhe * z, z),
        ] {
            writeln!(abundances,"{case},{},{},{},{},{id},{a},{z_nuc},{charge},{density},{fraction},{},,BASELINE_H_HE_CHARGE_AND_BARYON_V1",p.time_s,1.0/s.a-1.0,eos.temperature_k,2.7255/s.a,density/nb).map_err(ioerr)?;
        }
        writeln!(
            abundances,
            "{case},{},{},{},{},electron,0,,-1,{},,{}, {},BASELINE_H_HE_CHARGE_AND_BARYON_V1",
            p.time_s,
            1.0 / s.a - 1.0,
            eos.temperature_k,
            2.7255 / s.a,
            eos.electron_density_cm3,
            eos.electron_density_cm3 / nb,
            eos.electron_density_cm3 / nh
        )
        .map_err(ioerr)?;
        let rays = self.transport.ray_geometry(&g)?;
        for (k, ray) in rays.iter().enumerate() {
            let mu = ray.mu;
            for i in 0..ne {
                let j = k * ne + i;
                let stock = s.photons[j] + s.photon_inactive_number[j];
                let mut lo = s.photon_support_lo[j] * ray.scale;
                let mut hi = s.photon_support_hi[j] * ray.scale;
                if s.photon_inactive_number[j] > 0.0 {
                    let plo = self.transport.edges()[i] * ray.scale;
                    let phi = (self.transport.edges()[i + 1] * ray.scale).min(13.6);
                    lo = if s.photons[j] == 0.0 {
                        plo
                    } else {
                        lo.min(plo)
                    };
                    hi = hi.max(phi);
                }
                let energy = (s.photon_energy_ref[j] + s.photon_inactive_energy_ref[j]) * ray.scale;
                writeln!(
                    spectra,
                    "{case},{},{},{},{},{},{lo},{hi},{mu},{},{stock},{energy}",
                    self.config.q_ref,
                    p.sigma,
                    p.time_s,
                    s.a,
                    1.0 / s.a - 1.0,
                    4.0 * std::f64::consts::PI * ray.angular_weight
                )
                .map_err(ioerr)?;
            }
        }
        let (nr, ur) = self.residuals(s)?;
        for (name, residual, tol) in [
            ("photon_count", nr, 1e-8 * s.ledgers.source_n.max(1.0)),
            (
                "augmented_energy_eV_per_H",
                ur,
                1e-8 * s.ledgers.source_u.max(1.0),
            ),
            ("J1_eV_per_H", m[1], 1e-12 * m[0].max(1e-30)),
        ] {
            writeln!(
                ledgers,
                "{case},{},{name},{residual},{tol},{}",
                p.time_s,
                if residual.abs() <= tol {
                    "PASS"
                } else {
                    "FAIL"
                }
            )
            .map_err(ioerr)?;
        }
        let pools = self.pool_inventory_with_geometry(s, &g)?;
        for (name, value) in [
            ("active_photon_N_per_H", pools[0]),
            ("active_photon_U_eV_per_H", pools[1]),
            ("inactive_photon_N_per_H", pools[2]),
            ("inactive_photon_U_eV_per_H", pools[3]),
            ("source_N_per_H", s.ledgers.source_n),
            ("source_U_eV_per_H", s.ledgers.source_u),
            ("absorbed_N_per_H", s.ledgers.absorbed_n),
            ("escape_U_eV_per_H", s.ledgers.escaped_u),
            ("boundary_N_per_H", s.ledgers.boundary_n),
            ("boundary_U_eV_per_H", s.ledgers.boundary_u),
            ("thermal_work_eV_per_H", s.ledgers.thermal_work),
            ("photon_work_eV_per_H", s.ledgers.photon_work),
            ("signed_CMB_input_eV_per_H", s.ledgers.cmb_input),
            ("DR_events_per_H", s.ledgers.dr_events),
            ("CE_cap_eV_per_H", s.ledgers.ce_cap_ev),
            ("excluded_DR_eV_per_H", s.ledgers.excluded_dr_ev),
        ] {
            writeln!(ledgers, "{case},{},{name},{value},,VALUE", p.time_s).map_err(ioerr)?;
        }
        for k in 0..3 {
            for (name, value) in [
                ("RR_events", s.ledgers.rr_events[k]),
                ("CI_events", s.ledgers.ci_events[k]),
                ("photo_events", s.ledgers.photo_events[k]),
                ("CI_floor_events", s.ledgers.ci_floor_events[k]),
            ] {
                writeln!(
                    ledgers,
                    "{case},{},{name}_{k}_per_H,{value},,VALUE",
                    p.time_s
                )
                .map_err(ioerr)?;
            }
        }
        let h0 = 67.4 * 1e5 / 3.0856775814913673e24;
        let g_si = 6.67430e-11;
        let c_si = 299792458.0;
        let coupling = 8.0 * std::f64::consts::PI * g_si / (3.0 * c_si * c_si);
        let eps_ref = h0 * h0 / coupling * 9.2e-5 / (1.0_f64 / 21.0).powi(4);
        let rad = isotropic_initial_radiation_moments(s.a, p.b, 1.0 / 21.0, 0.0, eps_ref, 4096)?;
        // erg/cm3 -> J/m3 is 0.1. eV/H -> erg/cm3 uses proper nH.
        let ion_stress = nh * m[2] * c.ev_erg * 0.1;
        let extra = nh * (m[0] * c.ev_erg + s.gas.w_erg_per_h) * 0.1
            + rad.signed_energy_correction_j_m3.abs();
        writeln!(
            feedback,
            "{case},{},{},{},{},{},{},{},{},{}",
            p.time_s,
            s.a,
            p.h_per_s,
            rad.pressure_anisotropy_j_m3,
            ion_stress,
            rad.signed_energy_correction_j_m3,
            extra,
            extra * coupling / p.h_flrw_per_s.powi(2),
            rad.pressure_anisotropy_j_m3 + ion_stress
        )
        .map_err(ioerr)?;
        Ok(())
    }
}
pub const SCIENCE_OUTPUT_BUDGET_BYTES: u64 = 224 * 1024 * 1024;
fn directory_bytes(out: &Path) -> Result<u64, ForwardError> {
    let mut total = 0_u64;
    for entry in fs::read_dir(out).map_err(ioerr)? {
        let entry = entry.map_err(ioerr)?;
        let metadata = entry.metadata().map_err(ioerr)?;
        let bytes = if metadata.is_dir() {
            directory_bytes(&entry.path())?
        } else {
            metadata.len()
        };
        total = total
            .checked_add(bytes)
            .ok_or(err("AXBI_OUTPUT_BYTES_OVERFLOW"))?;
    }
    Ok(total)
}
/// Legacy pilot guard:224MiB scientific and32MiB launcher. Driver methods
/// use their explicit stage allocation (full1920MiB plus128MiB).
/// Reject before any batch write; include nested raw/checkpoint directories.
pub fn guard_output_bytes(out: &Path, new_bytes: u64) -> Result<(), ForwardError> {
    guard_output_bytes_with_limit(out, new_bytes, SCIENCE_OUTPUT_BUDGET_BYTES)
}
/// The resource allocation is bound by DriverConfig; this guard has no role
/// in solver/model/tolerance selection.
pub fn guard_output_bytes_with_limit(
    out: &Path,
    new_bytes: u64,
    scientific_bytes: u64,
) -> Result<(), ForwardError> {
    if directory_bytes(out)?
        .checked_add(new_bytes)
        .ok_or(err("AXBI_OUTPUT_BYTES_OVERFLOW"))?
        > scientific_bytes
    {
        return Err(err("AXBI_OUTPUT_CAP"));
    }
    Ok(())
}
fn write_checkpoint(path: &Path, text: &str) -> Result<(), ForwardError> {
    let tmp = path.with_extension("tmp");
    fs::write(&tmp, text).map_err(ioerr)?;
    fs::rename(tmp, path).map_err(ioerr)
}
impl Driver {
    pub fn output_batch(
        &self,
        s: &DriverState,
        case: &str,
        out: &Path,
        save_spectrum: bool,
        h: &mut impl Write,
        a: &mut impl Write,
        p: &mut impl Write,
        l: &mut impl Write,
        fb: &mut impl Write,
    ) -> Result<(), ForwardError> {
        let (mut hv, mut av, mut pv, mut lv, mut fv) =
            (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
        self.output_row(s, case, &mut hv, &mut av, &mut pv, &mut lv, &mut fv)?;
        let terminal_spectrum_reserve = if save_spectrum { 0 } else { pv.len() };
        if !save_spectrum {
            pv.clear();
        }
        h.flush().map_err(ioerr)?;
        a.flush().map_err(ioerr)?;
        p.flush().map_err(ioerr)?;
        l.flush().map_err(ioerr)?;
        fb.flush().map_err(ioerr)?;
        let bytes = hv.len() + av.len() + pv.len() + lv.len() + fv.len();
        // Reserve exact bytes for next snapshot plus atomic current checkpoint.
        let checkpoint_bytes = self.checkpoint_text(s)?.len();
        guard_output_bytes_with_limit(
            out,
            (bytes + terminal_spectrum_reserve + 2 * checkpoint_bytes) as u64,
            self.config.scientific_output_budget_bytes()?,
        )?;
        h.write_all(&hv).map_err(ioerr)?;
        a.write_all(&av).map_err(ioerr)?;
        p.write_all(&pv).map_err(ioerr)?;
        l.write_all(&lv).map_err(ioerr)?;
        fb.write_all(&fv).map_err(ioerr)?;
        Ok(())
    }
}
impl Driver {
    pub fn spectrum_due(
        &self,
        accepted: usize,
        seconds_since_checkpoint: f64,
        terminal: bool,
    ) -> bool {
        accepted == 0
            || accepted % self.config.spectra_every_accepted == 0
            || seconds_since_checkpoint >= 30.0
            || terminal
    }
    pub fn saved_spectrum_time(&self, out: &Path) -> Result<Option<f64>, ForwardError> {
        let text = fs::read_to_string(out.join("spectra.csv")).map_err(ioerr)?;
        let mut last = None;
        let mut rows = 0_usize;
        let full_rows = self.energies.len() * self.source.angular_cells.len();
        for line in text.lines().skip(1) {
            let t = line
                .split(',')
                .nth(3)
                .and_then(|x| x.parse::<f64>().ok())
                .ok_or(err("AXBI_SPECTRUM_TIME"))?;
            f(t)?;
            if Some(t) != last {
                if last.is_some() && rows != full_rows {
                    return Err(err("AXBI_SPECTRUM_SHAPE"));
                }
                if last.is_some_and(|previous| t <= previous) {
                    return Err(err("AXBI_SPECTRUM_ORDER"));
                }
                last = Some(t);
                rows = 0;
            }
            rows += 1;
        }
        if last.is_some() && rows != full_rows {
            return Err(err("AXBI_SPECTRUM_SHAPE"));
        }
        Ok(last)
    }
    /// A resume or controlled stop adds exactly one missing checkpoint-time
    /// full grid, never duplicates the main every-accepted-state tables.
    pub fn ensure_spectrum_snapshot(
        &self,
        s: &DriverState,
        case: &str,
        out: &Path,
        last: &mut Option<f64>,
        spectra: &mut impl Write,
    ) -> Result<bool, ForwardError> {
        let time = self.background.point_at_scale(s.a)?.time_s;
        if last.is_some_and(|t| t > time) {
            return Err(err("AXBI_SPECTRUM_AHEAD_CHECKPOINT"));
        }
        if *last == Some(time) {
            return Ok(false);
        }
        let mut pv = Vec::new();
        let (mut h, mut a, mut l, mut fb) = (
            std::io::sink(),
            std::io::sink(),
            std::io::sink(),
            std::io::sink(),
        );
        self.output_row(s, case, &mut h, &mut a, &mut pv, &mut l, &mut fb)?;
        spectra.flush().map_err(ioerr)?;
        let checkpoint_bytes = self.checkpoint_text(s)?.len();
        guard_output_bytes_with_limit(
            out,
            (pv.len() + 2 * checkpoint_bytes) as u64,
            self.config.scientific_output_budget_bytes()?,
        )?;
        spectra.write_all(&pv).map_err(ioerr)?;
        *last = Some(time);
        Ok(true)
    }
}
fn open_output(
    path: &Path,
    resume: bool,
    header: &str,
) -> Result<BufWriter<fs::File>, ForwardError> {
    let exists = path.exists();
    let mut f = BufWriter::new(
        fs::OpenOptions::new()
            .create(true)
            .write(true)
            .append(resume)
            .truncate(!resume)
            .open(path)
            .map_err(ioerr)?,
    );
    if !resume || !exists {
        writeln!(f, "{header}").map_err(ioerr)?;
    }
    Ok(f)
}
/// Bound execution entry point. Actual science invocations are separately
/// admitted by the controller; unit tests do not run a cosmological history.
pub fn run(config_text: &str, out: &Path, case: &str, resume: bool) -> Result<(), ForwardError> {
    if case.is_empty() || case.contains(',') || case.contains('\n') || case.contains('\r') {
        return Err(err("AXBI_CASE_ID"));
    }
    let cfg = DriverConfig::read(config_text)?;
    let (driver, mut state) = Driver::new(cfg)?;
    if resume {
        if fs::read_to_string(out.join("config.cfg")).map_err(ioerr)? != config_text
            || fs::read_to_string(out.join("source_identity.txt")).map_err(ioerr)?
                != compiled_identity()
        {
            return Err(err("AXBI_RESUME_IDENTITY"));
        }
        if fs::read_to_string(out.join("case_id.txt")).map_err(ioerr)? != case {
            return Err(err("AXBI_RESUME_CASE"));
        }
        state = driver.read_checkpoint(&out.join("checkpoint.txt"))?;
        reconcile_outputs(out, driver.background.point_at_scale(state.a)?.time_s)?;
    } else {
        if out.exists() {
            return Err(err("AXBI_OUTPUT_EXISTS"));
        }
        fs::create_dir_all(out.join("raw")).map_err(ioerr)?;
        fs::create_dir(out.join("checkpoints")).map_err(ioerr)?;
        fs::write(out.join("config.cfg"), config_text).map_err(ioerr)?;
        fs::write(out.join("source_identity.txt"), compiled_identity()).map_err(ioerr)?;
        fs::write(out.join("case_id.txt"), case).map_err(ioerr)?;
        fs::write(out.join("transport_variant.txt"), format!("inactive_hi_split={}\npassive_scope=q0_forward_monotonic_only\ncheckpoint_version=V4\ntransport_threads={}\nparallel_scope=persistent_cell_prepare_and_opt_in_jacobian_columns\nparallel_jacobian_columns={}\n", driver.config.inactive_hi_split, driver.config.transport_threads, driver.config.parallel_jacobian_columns)).map_err(ioerr)?;
        fs::write(out.join("metadata.txt"),"clock=elapsed proper seconds since zbar20\nframe=non-tilted normal tetrad\nmethod=binary64 BE split step-doubling empirical\nspectrum=fixed reference-q two-moment transport; total N/U includes active and passive source photons; support columns are conservative active-support/passive-cell envelope union, not a recovered density or exact populated support; Gamma uses active photons only; radiation stress includes both pools; legacy boundary outflow remains zero\nsolid_angle_weight_sr=normalized current quadrature for locally isotropic source; do not multiply stocks again\nspectra_cadence=initial; configured accepted-step interval(default60); each30wallsecondcheckpoint; terminal; fullgrid noaveraging\nuncertainty=no covariance/posterior supplied\ntail_tau=UNKNOWN\nscientific_admission=NOT_ISSUED\n").map_err(ioerr)?;
    }
    let mut h=open_output(&out.join("history.csv"),resume,"case_id,q_ref,Sigma,time_s,a,zbar,b,H_per_s,s_per_s,x_HII,x_HeII,x_HeIII,nH_proper_cm3,ne_proper_cm3,temperature_K,Gamma_HI_per_s,Gamma_HeI_per_s,Gamma_HeII_per_s,photon_n_per_H,photon_u_eV_per_H,J0_photon_u_eV_per_H,J1_photon_u_eV_per_H,J2_photon_u_eV_per_H,x_HI,x_HeI")?;
    let mut a=open_output(&out.join("abundances.csv"),resume,"run_id,time_s,zbar,Tgas_K,background_Tref_K,species_id,A,Z,charge,nproper,element_fraction,Ybaryon,electron_xe,normalization_registry")?;
    let mut p=open_output(&out.join("spectra.csv"),resume,"case_id,q_ref,Sigma,time_s,a,zbar,energy_low_eV,energy_high_eV,mu_center,solid_angle_weight_sr,photon_n_per_H,photon_u_eV_per_H")?;
    let mut l = open_output(
        &out.join("ledgers.csv"),
        resume,
        "case_id,time_s,ledger_name,residual,tolerance,status",
    )?;
    let mut fb=open_output(&out.join("feedback.csv"),resume,"case_id,time_s,a,H_per_s,effective_radiation_DeltaP_J_m3,ionizing_DeltaP_J_m3,effective_radiation_signed_deltaepsilon_J_m3,extra_energy_J_m3,extra_energy_ratio,total_DeltaP_J_m3")?;
    let mut rejects = open_output(
        &out.join("raw/rejections.csv"),
        true,
        "attempt,a,dln_a,error",
    )?;
    let mut last_spectrum_time = if resume {
        driver.saved_spectrum_time(out)?
    } else {
        None
    };
    if !resume {
        driver.output_batch(
            &state, case, out, true, &mut h, &mut a, &mut p, &mut l, &mut fb,
        )?;
        last_spectrum_time = Some(driver.background.point_at_scale(state.a)?.time_s);
    }
    if !resume {
        for writer in [&mut h, &mut a, &mut p, &mut l, &mut fb, &mut rejects] {
            writer.flush().map_err(ioerr)?;
        }
        driver.save_checkpoint_budget(out, &out.join("checkpoint.txt"), &state)?;
    }
    if resume {
        driver.ensure_spectrum_snapshot(&state, case, out, &mut last_spectrum_time, &mut p)?;
    }
    let started = Instant::now();
    let prior_wall = state.wall_elapsed_s;
    let mut last_save = Instant::now();
    let end = 1.0 / (1.0 + driver.config.end_zbar);
    let outcome = (|| {
        while state.a < end {
            state.wall_elapsed_s = prior_wall + started.elapsed().as_secs_f64();
            if state.wall_elapsed_s >= driver.config.max_wall_s
                || state.accepted >= driver.config.max_steps
                || state.attempts >= driver.config.max_attempts
                || state.rhs_evaluations >= driver.config.max_rhs
            {
                return Err(err("AXBI_RUNTIME_CAP"));
            }
            let previous = state.clone();
            let accepted = match driver.adaptive_step(&mut state) {
                Ok(value) => value,
                Err(e) => {
                    writeln!(
                        rejects,
                        "{},{},{},{e:?}",
                        state.attempts, state.a, state.next_dln_a
                    )
                    .map_err(ioerr)?;
                    rejects.flush().map_err(ioerr)?;
                    if state.consecutive_rejects >= 30
                        || state.next_dln_a < 1e-10
                        || state.rhs_evaluations >= driver.config.max_rhs
                    {
                        return Err(e);
                    }
                    false
                }
            };
            if !accepted {
                writeln!(
                    rejects,
                    "{},{},{},local_metric={}",
                    state.attempts, state.a, state.next_dln_a, state.last_error
                )
                .map_err(ioerr)?;
                if state.consecutive_rejects >= 30 || state.next_dln_a < 1e-10 {
                    return Err(err("AXBI_REJECT_CAP"));
                }
                continue;
            }
            let checkpoint_due = driver.spectrum_due(
                state.accepted,
                last_save.elapsed().as_secs_f64(),
                state.a == end,
            );
            if let Err(error) = driver.output_batch(
                &state,
                case,
                out,
                checkpoint_due,
                &mut h,
                &mut a,
                &mut p,
                &mut l,
                &mut fb,
            ) {
                let failed = state.clone();
                state = previous;
                state.attempts = failed.attempts;
                state.comparisons = failed.comparisons;
                state.rhs_evaluations = failed.rhs_evaluations;
                state.rejects = failed.rejects;
                state.wall_elapsed_s = failed.wall_elapsed_s;
                return Err(error);
            }
            if checkpoint_due {
                last_spectrum_time = Some(driver.background.point_at_scale(state.a)?.time_s);
                for writer in [&mut h, &mut a, &mut p, &mut l, &mut fb, &mut rejects] {
                    writer.flush().map_err(ioerr)?;
                }
                state.wall_elapsed_s = prior_wall + started.elapsed().as_secs_f64();
                driver.save_checkpoint_budget(
                    out,
                    &out.join(format!("checkpoints/{:08}.txt", state.accepted)),
                    &state,
                )?;
                driver.save_checkpoint_budget(out, &out.join("checkpoint.txt"), &state)?;
                check_resources(out, driver.config.output_budget_mib as u64 * 1024 * 1024)?;
                last_save = Instant::now();
            }
        }
        Ok(())
    })();
    state.wall_elapsed_s = prior_wall + started.elapsed().as_secs_f64();
    for writer in [&mut h, &mut a, &mut p, &mut l, &mut fb, &mut rejects] {
        writer.flush().map_err(ioerr)?;
    }
    driver.ensure_spectrum_snapshot(&state, case, out, &mut last_spectrum_time, &mut p)?;
    p.flush().map_err(ioerr)?;
    driver.save_checkpoint_budget(out, &out.join("checkpoint.txt"), &state)?;
    summarize_feedback(out)?;
    fs::write(out.join("RETURN.txt"),format!("status={}\na={}\naccepted={}\nattempts={}\nrejections={}\nrhs_evaluations={}\nwall_s={}\nmax_newton_residual={}\nlast_error={}\nresult={outcome:?}\nscientific_admission=NOT_ISSUED\n",if outcome.is_ok(){"COMPLETE_REPRESENTED_INTERVAL"}else{"STOPPED_CHECKPOINTED"},state.a,state.accepted,state.attempts,state.rejects,state.rhs_evaluations,state.wall_elapsed_s,state.max_newton_residual,state.last_error)).map_err(ioerr)?;
    outcome
}
fn check_resources(out: &Path, total_output_bytes: u64) -> Result<(), ForwardError> {
    let mut bytes = 0_u64;
    for e in fs::read_dir(out).map_err(ioerr)? {
        let e = e.map_err(ioerr)?;
        if e.path().is_file() {
            bytes += e.metadata().map_err(ioerr)?.len();
        }
    }
    if bytes > total_output_bytes {
        return Err(err("AXBI_OUTPUT_CAP"));
    }
    if let Ok(status) = fs::read_to_string("/proc/self/status") {
        if let Some(line) = status.lines().find(|s| s.starts_with("VmHWM:")) {
            if line
                .split_whitespace()
                .nth(1)
                .and_then(|s| s.parse::<u64>().ok())
                .unwrap_or(0)
                > 2 * 1024 * 1024
            {
                return Err(err("AXBI_RSS_CAP"));
            }
        }
    }
    Ok(())
}
/// Restore tables to the durable checkpoint; preserve discarded rows as raw
/// crash-tail evidence. Never append later rows to an earlier resumed state.
fn reconcile_outputs(out: &Path, time: f64) -> Result<(), ForwardError> {
    for (name, time_col) in [
        ("history.csv", 3),
        ("spectra.csv", 3),
        ("abundances.csv", 1),
        ("ledgers.csv", 1),
        ("feedback.csv", 1),
    ] {
        let file = out.join(name);
        let text = fs::read_to_string(&file).map_err(ioerr)?;
        let mut kept = String::new();
        let mut tail = String::new();
        for (i, line) in text.lines().enumerate() {
            let t = if i == 0 {
                0.0
            } else {
                line.split(',')
                    .nth(time_col)
                    .and_then(|s| s.parse::<f64>().ok())
                    .ok_or(err("AXBI_RESUME_TABLE"))?
            };
            if i == 0 || t <= time {
                kept.push_str(line);
                kept.push('\n');
            } else {
                tail.push_str(line);
                tail.push('\n');
            }
        }
        if !tail.is_empty() {
            let epoch = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_err(|_| err("AXBI_SYSTEM_CLOCK"))?
                .as_nanos();
            fs::write(out.join(format!("raw/crash_tail_{epoch}_{name}")), tail).map_err(ioerr)?;
            fs::write(file, kept).map_err(ioerr)?;
        }
    }
    Ok(())
}
fn summarize_feedback(out: &Path) -> Result<(), ForwardError> {
    let text = fs::read_to_string(out.join("feedback.csv")).map_err(ioerr)?;
    let coupling = 8.0 * std::f64::consts::PI * 6.67430e-11 / (3.0 * 299792458.0_f64.powi(2));
    let mut prev = None;
    let mut integral = 0.0;
    let mut max_ds = 0.0_f64;
    let mut max_energy = 0.0_f64;
    for line in text.lines().skip(1) {
        let cols = line.split(',').collect::<Vec<_>>();
        if cols.len() != 10 {
            return Err(err("AXBI_FEEDBACK_TABLE"));
        }
        let get = |i: usize| {
            cols[i]
                .parse::<f64>()
                .map_err(|_| err("AXBI_FEEDBACK_TABLE"))
        };
        let t = get(1)?;
        let a = get(2)?;
        let h = get(3)?;
        let stress = get(9)?;
        max_energy = max_energy.max(get(8)?);
        if let Some((pt, pa, ps)) = prev {
            integral += 0.5 * coupling * (a.powi(3) * stress + pa * ps) * (t - pt);
        }
        max_ds = max_ds.max((integral / a.powi(3) / h).abs());
        prev = Some((t, a.powi(3), stress));
    }
    fs::write(out.join("feedback_summary.txt"),format!("max_abs_delta_s_over_H={max_ds}\nmax_extra_energy_ratio={max_energy}\nthreshold=0.0001\nstatus={}\nkind=sampled_trapezoidal_perturbative_estimate_not_rigorous_bound\n",if max_ds<=1e-4&&max_energy<=1e-4{"WITHIN_DECLARED_DIAGNOSTIC_CEILING"}else{"EXCEEDS_DECLARED_DIAGNOSTIC_CEILING"})).map_err(ioerr)
}
