//! Source bound, temperature dependent FT03 controlled H/He successor.
//! Photon number and thermal energy use proper cm^-3 units throughout.
use crate::{
    ft03_rates::ft03_coefficients, Absorber, AtomicProvider, ForwardError, HHeModel, HHeState,
    StepControl,
};

pub const FT03_MODEL_ID: &str = "REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1";

#[derive(Clone, Copy, Debug)]
pub struct Ft03Model {
    pub gas: HHeModel,
}

impl Ft03Model {
    pub fn controlled() -> Result<Self, ForwardError> {
        let provider = AtomicProvider::reference();
        let mut gas = HHeModel::controlled_fixture();
        gas.photon_energy_ev = [20.0, 35.0, 70.0];
        gas.alpha_cm3_s = [0.0; 3];
        gas.beta_cm3_s = [0.0; 3];
        for (a, absorber) in [Absorber::HI, Absorber::HeI, Absorber::HeII]
            .into_iter()
            .enumerate()
        {
            for g in 0..3 {
                gas.sigma_cm2[a][g] = provider.cross_section(absorber, gas.photon_energy_ev[g])?;
            }
        }
        gas.validate()?;
        Ok(Self { gas })
    }

    pub fn initial_state(&self) -> HHeState {
        let fractions = [0.9, 0.3, 0.6];
        let ne = self.gas.n_h_cm3 * fractions[0]
            + self.gas.n_he_cm3 * (fractions[1] + 2.0 * fractions[2]);
        HHeState {
            fractions,
            u_erg_cm3: 1.5
                * self.gas.kb_erg_k
                * 50_000.0
                * (self.gas.n_h_cm3 + self.gas.n_he_cm3 + ne),
            photon_cm3: [0.05, 0.005, 0.001].map(|p| self.gas.n_h_cm3 * p),
            escaped_erg_cm3: 0.0,
        }
    }

    fn validate_state(&self, state: &HHeState) -> Result<f64, ForwardError> {
        self.gas.validate_state(state)?;
        if self.gas.n_h_cm3 <= 0.0 || self.gas.n_he_cm3 <= 0.0 {
            return Err(ForwardError::InvalidInput("FT03_NUCLEAR_DENSITY_DOMAIN"));
        }
        let t = self.gas.temperature(state)?;
        ft03_coefficients(t)?;
        Ok(t)
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Ft03Rhs {
    pub derivative: [f64; 7],
    pub photo_per_cm3_s: [[f64; 3]; 3],
    pub collision_per_cm3_s: [f64; 3],
    pub recombination_per_cm3_s: [f64; 3],
    pub dr_per_cm3_s: [f64; 2],
    pub escaped_energy_rate: f64,
}

// Exact zero factors describe absent channels. A zero from nonzero factors
// instead means this binary64 event/energy ledger cannot represent the product.
fn checked_product(factors: &[f64]) -> Result<f64, ForwardError> {
    if factors.iter().any(|x| !x.is_finite()) {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    if factors.contains(&0.0) {
        return Ok(0.0);
    }
    let product = factors.iter().product::<f64>();
    if !product.is_finite() {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    if product == 0.0 {
        return Err(ForwardError::InvalidInput("FT03_PRODUCT_UNDERFLOW"));
    }
    Ok(product)
}

pub fn ft03_rhs(model: &Ft03Model, state: &HHeState) -> Result<Ft03Rhs, ForwardError> {
    let t = model.validate_state(state)?;
    let c = ft03_coefficients(t)?;
    let g = &model.gas;
    let [h, he1, he2] = state.fractions;
    let lower = [
        checked_product(&[g.n_h_cm3, 1.0 - h])?,
        checked_product(&[g.n_he_cm3, 1.0 - (he1 + he2)])?,
        checked_product(&[g.n_he_cm3, he1])?,
    ];
    let upper = [
        checked_product(&[g.n_h_cm3, h])?,
        checked_product(&[g.n_he_cm3, he1])?,
        checked_product(&[g.n_he_cm3, he2])?,
    ];
    let ne = g.electron_density(state)?;
    let mut photo = [[0.0; 3]; 3];
    let mut ci = [0.0; 3];
    let mut rr = [0.0; 3];
    let mut photon_dot = [0.0; 3];
    let mut j = [0.0; 3];
    let mut du = 0.0;
    let mut escape = 0.0;
    for a in 0..3 {
        ci[a] = checked_product(&[lower[a], ne, c.beta_ci_cm3_s[a]])?;
        rr[a] = checked_product(&[upper[a], ne, c.alpha_rr_cm3_s[a]])?;
        j[a] = ci[a] - rr[a];
        let chi = g.threshold_ev[a] * g.ev_erg;
        let kinetic_rate = checked_product(&[upper[a], ne, c.rr_kinetic_erg_cm3_s[a]])?;
        du -= checked_product(&[ci[a], chi])? + kinetic_rate;
        escape += checked_product(&[rr[a], chi])? + kinetic_rate;
        for (k, photon_dot_k) in photon_dot.iter_mut().enumerate() {
            photo[a][k] =
                checked_product(&[g.c_cm_s, lower[a], g.sigma_cm2[a][k], state.photon_cm3[k]])?;
            j[a] += photo[a][k];
            *photon_dot_k -= photo[a][k];
            du += checked_product(&[
                photo[a][k],
                g.photon_energy_ev[k] - g.threshold_ev[a],
                g.ev_erg,
            ])?;
        }
    }
    let dr = [
        checked_product(&[upper[1], ne, c.alpha_dr_cm3_s[0]])?,
        checked_product(&[upper[1], ne, c.alpha_dr_cm3_s[1]])?,
    ];
    for (k, event) in dr.iter().enumerate() {
        j[1] -= event;
        du -= checked_product(&[*event, c.dr_energy_erg[k]])?;
        escape += checked_product(&[*event, g.threshold_ev[1] * g.ev_erg + c.dr_energy_erg[k]])?;
    }
    let d = [
        j[0] / g.n_h_cm3,
        (j[1] - j[2]) / g.n_he_cm3,
        j[2] / g.n_he_cm3,
        du,
        photon_dot[0],
        photon_dot[1],
        photon_dot[2],
    ];
    if d.iter().any(|x| !x.is_finite())
        || !escape.is_finite()
        || photo.iter().flatten().any(|x| !x.is_finite() || *x < 0.0)
        || ci
            .iter()
            .chain(rr.iter())
            .chain(dr.iter())
            .any(|x| !x.is_finite() || *x < 0.0)
    {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    Ok(Ft03Rhs {
        derivative: d,
        photo_per_cm3_s: photo,
        collision_per_cm3_s: ci,
        recombination_per_cm3_s: rr,
        dr_per_cm3_s: dr,
        escaped_energy_rate: escape,
    })
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Ft03Events {
    pub photo_per_cm3: [[f64; 3]; 3],
    pub collision_per_cm3: [f64; 3],
    pub recombination_per_cm3: [f64; 3],
    pub dr_per_cm3: [f64; 2],
}

impl Ft03Events {
    pub(crate) fn plus(self, other: Self) -> Self {
        let mut sum = self;
        for a in 0..3 {
            for k in 0..3 {
                sum.photo_per_cm3[a][k] += other.photo_per_cm3[a][k];
            }
            sum.collision_per_cm3[a] += other.collision_per_cm3[a];
            sum.recombination_per_cm3[a] += other.recombination_per_cm3[a];
        }
        for k in 0..2 {
            sum.dr_per_cm3[k] += other.dr_per_cm3[k];
        }
        sum
    }

    fn finite(&self) -> bool {
        self.photo_per_cm3
            .iter()
            .flatten()
            .all(|x| x.is_finite() && *x >= 0.0)
            && self
                .collision_per_cm3
                .iter()
                .all(|x| x.is_finite() && *x >= 0.0)
            && self
                .recombination_per_cm3
                .iter()
                .all(|x| x.is_finite() && *x >= 0.0)
            && self.dr_per_cm3.iter().all(|x| x.is_finite() && *x >= 0.0)
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Ft03Step {
    pub state: HHeState,
    pub events: Ft03Events,
    pub iterations: usize,
    pub residual_norm: f64,
    pub local_error: f64,
}

/// Final endpoint backward Euler residual; one source site for all seven
/// coordinates, escaped energy, and integrated event counts.
fn be_endpoint_residual(
    model: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    dt: f64,
) -> Result<(f64, Ft03Events), ForwardError> {
    let rhs = ft03_rhs(model, new)?;
    let x0 = old.coordinates();
    let x1 = new.coordinates();
    let scale = [
        1.0,
        1.0,
        1.0,
        old.u_erg_cm3.max(1e-30),
        old.photon_cm3[0].max(1e-30),
        old.photon_cm3[1].max(1e-30),
        old.photon_cm3[2].max(1e-30),
    ];
    let mut norm: f64 = 0.0;
    for k in 0..7 {
        norm = norm.max(((x1[k] - x0[k] - dt * rhs.derivative[k]) / scale[k]).abs());
    }
    norm = norm.max(
        ((new.escaped_erg_cm3 - old.escaped_erg_cm3 - dt * rhs.escaped_energy_rate)
            / model.gas.total_energy(old)?.max(1e-30))
        .abs(),
    );
    let mut events = Ft03Events::default();
    for a in 0..3 {
        events.collision_per_cm3[a] = dt * rhs.collision_per_cm3_s[a];
        events.recombination_per_cm3[a] = dt * rhs.recombination_per_cm3_s[a];
        for k in 0..3 {
            events.photo_per_cm3[a][k] = dt * rhs.photo_per_cm3_s[a][k];
        }
    }
    for k in 0..2 {
        events.dr_per_cm3[k] = dt * rhs.dr_per_cm3_s[k];
    }
    if !norm.is_finite() || !events.finite() {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    Ok((norm, events))
}

fn check_invariants(
    model: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    events: &Ft03Events,
    tolerance: f64,
) -> Result<(), ForwardError> {
    let g = &model.gas;
    let energy0 = g.total_energy(old)?;
    let energy1 = g.total_energy(new)?;
    let mut norm = ((energy1 - energy0) / energy0.max(1e-30)).abs();
    let mut j = [0.0; 3];
    for (a, value) in j.iter_mut().enumerate() {
        *value = events.photo_per_cm3[a].iter().sum::<f64>() + events.collision_per_cm3[a]
            - events.recombination_per_cm3[a];
    }
    j[1] -= events.dr_per_cm3.iter().sum::<f64>();
    norm = norm.max(((g.n_h_cm3 * (new.fractions[0] - old.fractions[0]) - j[0]) / g.n_h_cm3).abs());
    norm = norm.max(
        ((g.n_he_cm3 * (new.fractions[1] - old.fractions[1]) - j[1] + j[2]) / g.n_he_cm3).abs(),
    );
    norm =
        norm.max(((g.n_he_cm3 * (new.fractions[2] - old.fractions[2]) - j[2]) / g.n_he_cm3).abs());
    for k in 0..3 {
        let absorbed = (0..3).map(|a| events.photo_per_cm3[a][k]).sum::<f64>();
        norm = norm.max(
            ((old.photon_cm3[k] - new.photon_cm3[k] - absorbed) / old.photon_cm3[k].max(1e-30))
                .abs(),
        );
    }
    if !norm.is_finite() || norm > tolerance.max(1e-13) * 8.0 {
        return Err(ForwardError::InvalidInput("FT03_INVARIANT_RESIDUAL"));
    }
    Ok(())
}

pub fn ft03_implicit_step(
    model: &Ft03Model,
    old: &HHeState,
    dt: f64,
    control: StepControl,
) -> Result<Ft03Step, ForwardError> {
    model.validate_state(old)?;
    if !dt.is_finite()
        || dt < 0.0
        || control.max_iterations == 0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(ForwardError::InvalidInput("FT03_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok(Ft03Step {
            state: *old,
            events: Ft03Events::default(),
            iterations: 0,
            residual_norm: 0.0,
            local_error: 0.0,
        });
    }
    let g = &model.gas;
    let mut guess = *old;
    for iteration in 1..=control.max_iterations {
        let ne = g.electron_density(&guess)?;
        let c = ft03_coefficients(model.validate_state(&guess)?)?;
        let [h, he1, he2] = guess.fractions;
        let lower = [
            g.n_h_cm3 * (1.0 - h),
            g.n_he_cm3 * (1.0 - (he1 + he2)),
            g.n_he_cm3 * he1,
        ];
        let mut next = guess;
        for k in 0..3 {
            let opacity = (0..3).map(|a| lower[a] * g.sigma_cm2[a][k]).sum::<f64>();
            next.photon_cm3[k] = old.photon_cm3[k] / (1.0 + dt * g.c_cm_s * opacity);
        }
        let ion = std::array::from_fn::<_, 3, _>(|a| {
            (0..3)
                .map(|k| g.c_cm_s * g.sigma_cm2[a][k] * next.photon_cm3[k])
                .sum::<f64>()
                + ne * c.beta_ci_cm3_s[a]
        });
        let rr = std::array::from_fn::<_, 3, _>(|a| ne * c.alpha_rr_cm3_s[a]);
        let dr = ne * c.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let he0_old = 1.0 - (old.fractions[1] + old.fractions[2]);
        let a = dt * ion[1];
        let b = dt * (rr[1] + dr);
        let c2 = dt * ion[2];
        let d = dt * rr[2];
        // All production terms are nonnegative at a helium boundary.
        let he1_next =
            (old.fractions[1] + he0_old * (a / (1.0 + a)) + old.fractions[2] * (d / (1.0 + d)))
                / (1.0 + b / (1.0 + a) + c2 / (1.0 + d));
        next.fractions[1] = he1_next;
        next.fractions[2] = (old.fractions[2] + c2 * he1_next) / (1.0 + d);
        // Use the candidate's fractions and photons with the current thermal
        // guess; the final RHS and residual are reevaluated at the actual T.
        let rates = ft03_rhs(model, &next)?;
        next.u_erg_cm3 = old.u_erg_cm3 + dt * rates.derivative[3];
        next.escaped_erg_cm3 = old.escaped_erg_cm3 + dt * rates.escaped_energy_rate;
        model.validate_state(&next)?;
        let (norm, events) = be_endpoint_residual(model, old, &next, dt)?;
        if norm < control.residual_tolerance {
            check_invariants(model, old, &next, &events, control.residual_tolerance)?;
            return Ok(Ft03Step {
                state: next,
                events,
                iterations: iteration,
                residual_norm: norm,
                local_error: 0.0,
            });
        }
        guess = next;
    }
    Err(ForwardError::InvalidInput("FT03_NONCONVERGENCE"))
}

pub fn ft03_try_step(
    model: &Ft03Model,
    state: &mut HHeState,
    dt: f64,
    control: StepControl,
) -> Result<Ft03Step, ForwardError> {
    let step = ft03_implicit_step(model, state, dt, control)?;
    *state = step.state;
    Ok(step)
}

pub fn ft03_adaptive_step(
    model: &Ft03Model,
    old: &HHeState,
    dt: f64,
    control: StepControl,
) -> Result<Ft03Step, ForwardError> {
    if dt == 0.0 {
        return ft03_implicit_step(model, old, dt, control);
    }
    let full = ft03_implicit_step(model, old, dt, control)?;
    let half1 = ft03_implicit_step(model, old, dt / 2.0, control)?;
    let half2 = ft03_implicit_step(model, &half1.state, dt / 2.0, control)?;
    let tf = model.gas.temperature(&full.state)?;
    let th = model.gas.temperature(&half2.state)?;
    let mut error = (tf.ln() - th.ln()).abs();
    for a in 0..3 {
        error = error.max((full.state.fractions[a] - half2.state.fractions[a]).abs());
    }
    if !error.is_finite() || error >= 2e-4 {
        return Err(ForwardError::InvalidInput("FT03_LOCAL_ERROR"));
    }
    let events = half1.events.plus(half2.events);
    if !events.finite() {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    Ok(Ft03Step {
        state: half2.state,
        events,
        iterations: full.iterations + half1.iterations + half2.iterations,
        residual_norm: half1.residual_norm.max(half2.residual_norm),
        local_error: error,
    })
}
