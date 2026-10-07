//! Positive backward Euler solve for the controlled H/He system.
use crate::{hhe_rhs, thermal::endpoint_thermal, ForwardError, HHeEvents, HHeModel, HHeState};

#[derive(Clone, Copy, Debug)]
pub struct StepControl {
    pub max_iterations: usize,
    pub residual_tolerance: f64,
}

impl Default for StepControl {
    fn default() -> Self {
        Self {
            max_iterations: 80,
            residual_tolerance: 1e-14,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct HHeStep {
    pub state: HHeState,
    pub events: HHeEvents,
    pub iterations: usize,
    pub residual_norm: f64,
    pub local_error: f64,
}

/// Seven coordinate backward Euler residual evaluated at the final endpoint.
/// Fractions use unit scales, thermal energy uses old u, and each photon
/// coordinate uses its old group density, with 1e-30 floors for zero inputs.
fn be_endpoint_residual(
    model: &HHeModel,
    old: &HHeState,
    new: &HHeState,
    dt: f64,
) -> Result<(f64, HHeEvents), ForwardError> {
    let rhs = hhe_rhs(model, new)?;
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
    for i in 0..7 {
        norm = norm.max(((x1[i] - x0[i] - dt * rhs.derivative[i]) / scale[i]).abs());
    }
    let escape_scale = model.total_energy(old)?.max(1e-30);
    norm = norm.max(
        ((new.escaped_erg_cm3 - old.escaped_erg_cm3 - dt * rhs.escaped_energy_rate) / escape_scale)
            .abs(),
    );
    let mut events = HHeEvents::default();
    for a in 0..3 {
        events.collision_per_cm3[a] = dt * rhs.collision_per_cm3_s[a];
        events.recombination_per_cm3[a] = dt * rhs.recombination_per_cm3_s[a];
        for g in 0..3 {
            events.photo_per_cm3[a][g] = dt * rhs.photo_per_cm3_s[a][g];
        }
    }
    if !norm.is_finite()
        || events
            .photo_per_cm3
            .iter()
            .flatten()
            .any(|x| !x.is_finite())
        || events
            .collision_per_cm3
            .iter()
            .chain(events.recombination_per_cm3.iter())
            .any(|x| !x.is_finite())
    {
        return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
    }
    Ok((norm, events))
}

fn check_invariants(
    model: &HHeModel,
    old: &HHeState,
    new: &HHeState,
    events: &HHeEvents,
    tolerance: f64,
) -> Result<(), ForwardError> {
    let energy0 = model.total_energy(old)?;
    let energy1 = model.total_energy(new)?;
    let mut norm = ((energy1 - energy0) / energy0.max(1e-30)).abs();
    let mut j = [0.0; 3];
    for (a, value) in j.iter_mut().enumerate() {
        *value = events.photo_per_cm3[a].iter().sum::<f64>() + events.collision_per_cm3[a]
            - events.recombination_per_cm3[a];
    }
    let counts = [
        (
            model.n_h_cm3 * (new.fractions[0] - old.fractions[0]) - j[0],
            model.n_h_cm3,
        ),
        (
            model.n_he_cm3 * (new.fractions[1] - old.fractions[1]) - j[1] + j[2],
            model.n_he_cm3,
        ),
        (
            model.n_he_cm3 * (new.fractions[2] - old.fractions[2]) - j[2],
            model.n_he_cm3,
        ),
    ];
    for (difference, scale) in counts {
        norm = norm.max((difference / scale.max(1e-30)).abs());
    }
    for g in 0..3 {
        let absorbed: f64 = (0..3).map(|a| events.photo_per_cm3[a][g]).sum();
        norm = norm.max(
            ((old.photon_cm3[g] - new.photon_cm3[g] - absorbed) / old.photon_cm3[g].max(1e-30))
                .abs(),
        );
    }
    if !norm.is_finite() || norm > tolerance.max(1e-13) * 8.0 {
        return Err(ForwardError::InvalidInput("HHE_INVARIANT_RESIDUAL"));
    }
    Ok(())
}

pub fn implicit_hhe_step(
    model: &HHeModel,
    old: &HHeState,
    dt: f64,
    control: StepControl,
) -> Result<HHeStep, ForwardError> {
    model.validate_state(old)?;
    if !dt.is_finite()
        || dt < 0.0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(ForwardError::InvalidInput("HHE_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok(HHeStep {
            state: *old,
            events: HHeEvents::default(),
            iterations: 0,
            residual_norm: 0.0,
            local_error: 0.0,
        });
    }
    if control.max_iterations == 0 {
        return Err(ForwardError::InvalidInput("HHE_STEP_CONTROL"));
    }
    let mut guess = *old;
    for iteration in 1..=control.max_iterations {
        let ne = model.electron_density(&guess)?;
        let [h, he1, he2] = guess.fractions;
        let lower = [
            model.n_h_cm3 * (1.0 - h),
            model.n_he_cm3 * (1.0 - (he1 + he2)),
            model.n_he_cm3 * he1,
        ];
        let mut next = guess;
        for g in 0..3 {
            let opacity: f64 = (0..3).map(|a| lower[a] * model.sigma_cm2[a][g]).sum();
            next.photon_cm3[g] = old.photon_cm3[g] / (1.0 + dt * model.c_cm_s * opacity);
        }
        let photo_rate = std::array::from_fn::<_, 3, _>(|a| {
            (0..3)
                .map(|g| model.c_cm_s * model.sigma_cm2[a][g] * next.photon_cm3[g])
                .sum::<f64>()
        });
        let ion = std::array::from_fn::<_, 3, _>(|a| photo_rate[a] + ne * model.beta_cm3_s[a]);
        let rr = std::array::from_fn::<_, 3, _>(|a| ne * model.alpha_cm3_s[a]);
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let p0old = 1.0 - (old.fractions[1] + old.fractions[2]);
        let p2old = old.fractions[2];
        let a = dt * ion[1];
        let b = dt * rr[1];
        let c = dt * ion[2];
        let d = dt * rr[2];
        // Nonnegative production terms avoid cancellation at a zero HeII boundary.
        let p1 = (old.fractions[1] + p0old * (a / (1.0 + a)) + p2old * (d / (1.0 + d)))
            / (1.0 + b / (1.0 + a) + c / (1.0 + d));
        let p2 = (p2old + c * p1) / (1.0 + d);
        next.fractions[1] = p1;
        next.fractions[2] = p2;
        // Rates are independent of temperature in this synthetic fixture.
        // The temporary u merely permits evaluating the endpoint event rates.
        let rates = hhe_rhs(model, &next)?;
        let (u, escaped) = endpoint_thermal(model, old, &next, &rates, dt)?;
        next.u_erg_cm3 = u;
        next.escaped_erg_cm3 = escaped;
        model.validate_state(&next)?;
        let (norm, events) = be_endpoint_residual(model, old, &next, dt)?;
        if norm < control.residual_tolerance {
            check_invariants(model, old, &next, &events, control.residual_tolerance)?;
            return Ok(HHeStep {
                state: next,
                events,
                iterations: iteration,
                residual_norm: norm,
                local_error: 0.0,
            });
        }
        guess = next;
    }
    Err(ForwardError::InvalidInput("HHE_NONCONVERGENCE"))
}

pub fn try_hhe_step(
    model: &HHeModel,
    state: &mut HHeState,
    dt: f64,
    control: StepControl,
) -> Result<HHeStep, ForwardError> {
    let result = implicit_hhe_step(model, state, dt, control)?;
    *state = result.state;
    Ok(result)
}

pub fn adaptive_hhe_step(
    model: &HHeModel,
    old: &HHeState,
    dt: f64,
    control: StepControl,
) -> Result<HHeStep, ForwardError> {
    if dt == 0.0 {
        return implicit_hhe_step(model, old, dt, control);
    }
    let full = implicit_hhe_step(model, old, dt, control)?;
    let half1 = implicit_hhe_step(model, old, 0.5 * dt, control)?;
    let half2 = implicit_hhe_step(model, &half1.state, 0.5 * dt, control)?;
    let t_full = model.temperature(&full.state)?;
    let t_half = model.temperature(&half2.state)?;
    if t_full <= 0.0 || t_half <= 0.0 {
        return Err(ForwardError::InvalidInput("HHE_TEMPERATURE_DOMAIN"));
    }
    let mut error = (t_full.ln() - t_half.ln()).abs();
    for a in 0..3 {
        error = error.max((full.state.fractions[a] - half2.state.fractions[a]).abs());
    }
    if !error.is_finite() || error >= 2e-4 {
        return Err(ForwardError::InvalidInput("HHE_LOCAL_ERROR"));
    }
    let events = half1.events.plus(half2.events);
    if events
        .photo_per_cm3
        .iter()
        .flatten()
        .any(|x| !x.is_finite())
        || events
            .collision_per_cm3
            .iter()
            .chain(events.recombination_per_cm3.iter())
            .any(|x| !x.is_finite())
    {
        return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
    }
    Ok(HHeStep {
        state: half2.state,
        events,
        iterations: full.iterations + half1.iterations + half2.iterations,
        residual_norm: half1.residual_norm.max(half2.residual_norm),
        local_error: error,
    })
}
