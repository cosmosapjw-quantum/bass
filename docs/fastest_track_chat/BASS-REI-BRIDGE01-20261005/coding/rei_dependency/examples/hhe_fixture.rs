//! Controlled synthetic H/He fixture, with transactional adaptive trial steps.
use rei_microphysics::{adaptive_hhe_step, HHeEvents, HHeModel, HHeState, StepControl};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let requested_dt: f64 = match std::env::args().nth(1) {
        Some(text) => text.parse()?,
        None => 1e9,
    };
    if !requested_dt.is_finite() || requested_dt <= 0.0 {
        return Err("dt must be positive and finite".into());
    }
    let model = HHeModel::controlled_fixture();
    let initial = HHeState::controlled_fixture(&model);
    let initial_energy = model.total_energy(&initial)?;
    let mut state = initial;
    let mut t = 0.0;
    let mut trial_dt = requested_dt;
    let mut accepted_steps = 0usize;
    let mut rejected_steps = 0usize;
    let mut rejected_candidate_writes = 0usize;
    let mut max_local_error: f64 = 0.0;
    let mut events = HHeEvents::default();
    const END: f64 = 1e12;
    const MIN_DT: f64 = 1e3;
    while t < END {
        let h = trial_dt.min(END - t);
        let before_trial = state;
        match adaptive_hhe_step(&model, &state, h, StepControl::default()) {
            Ok(step) => {
                state = step.state;
                accepted_steps += 1;
                max_local_error = max_local_error.max(step.local_error);
                for a in 0..3 {
                    for g in 0..3 {
                        events.photo_per_cm3[a][g] += step.events.photo_per_cm3[a][g];
                    }
                    events.collision_per_cm3[a] += step.events.collision_per_cm3[a];
                    events.recombination_per_cm3[a] += step.events.recombination_per_cm3[a];
                }
                t += h;
            }
            Err(error) => {
                rejected_steps += 1;
                if state != before_trial {
                    rejected_candidate_writes += 1;
                }
                trial_dt *= 0.5;
                if trial_dt < MIN_DT {
                    return Err(format!("minimum trial dt reached: {error}").into());
                }
            }
        }
    }
    let mut event_residual: f64 = 0.0;
    let mut j = [0.0; 3];
    for (a, value) in j.iter_mut().enumerate() {
        *value = events.photo_per_cm3[a].iter().sum::<f64>() + events.collision_per_cm3[a]
            - events.recombination_per_cm3[a];
    }
    event_residual = event_residual.max(
        (model.n_h_cm3 * (state.fractions[0] - initial.fractions[0]) - j[0]).abs() / model.n_h_cm3,
    );
    for (fraction, expected) in [(1, j[1] - j[2]), (2, j[2])] {
        event_residual = event_residual.max(
            (model.n_he_cm3 * (state.fractions[fraction] - initial.fractions[fraction]) - expected)
                .abs()
                / model.n_he_cm3,
        );
    }
    for g in 0..3 {
        let absorbed: f64 = (0..3).map(|a| events.photo_per_cm3[a][g]).sum();
        event_residual = event_residual.max(
            (initial.photon_cm3[g] - state.photon_cm3[g] - absorbed).abs() / initial.photon_cm3[g],
        );
    }
    let temperature = model.temperature(&state)?;
    let energy_residual = (model.total_energy(&state)? - initial_energy) / initial_energy;
    println!(
        "{{\"fixture_id\":\"REI_SYNTHETIC_HHE_3GROUP_STATIC_V1\",\"dt_s\":{requested_dt},\
         \"t_end_s\":{END},\"coordinates\":[\"x_HII\",\"x_HeII\",\"x_HeIII\",\
         \"u_th_proper_erg_cm3\",\"N0_proper_cm3\",\"N1_proper_cm3\",\"N2_proper_cm3\"],\
         \"source_site\":\"backward_euler_endpoint\",\"scientific_admission\":\"HOLD\",\
         \"accepted_steps\":{accepted_steps},\"rejected_steps\":{rejected_steps},\
         \"rejected_candidate_writes\":{rejected_candidate_writes},\"max_local_error\":{max_local_error},\
         \"observables\":[{},{},{},{}],\"photons_cm3\":[{},{},{}],\
         \"relative_energy_residual\":{energy_residual},\"scaled_event_residual\":{event_residual}}}",
        state.fractions[0], state.fractions[1], state.fractions[2], temperature.ln(),
        state.photon_cm3[0], state.photon_cm3[1], state.photon_cm3[2]
    );
    Ok(())
}
