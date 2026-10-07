//! Finite controlled FT03 endpoint experiment; scientific admission remains HOLD.
use rei_microphysics::{ft03_adaptive_step, Ft03Events, Ft03Model, StepControl, FT03_MODEL_ID};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let requested_dt: f64 = match std::env::args().nth(1) {
        Some(text) => text.parse()?,
        None => 1e11,
    };
    if !requested_dt.is_finite() || requested_dt <= 0.0 {
        return Err("dt must be positive and finite".into());
    }
    let model = Ft03Model::controlled()?;
    let initial = model.initial_state();
    let initial_energy = model.gas.total_energy(&initial)?;
    let mut state = initial;
    let mut t = 0.0;
    let mut trial_dt = requested_dt;
    let mut accepted_steps = 0usize;
    let mut rejected_steps = 0usize;
    let mut rejected_candidate_writes = 0usize;
    let mut max_local_error: f64 = 0.0;
    let mut events = Ft03Events::default();
    let mut temperature_min = model.gas.temperature(&state)?;
    let mut temperature_max = temperature_min;
    const END: f64 = 1e14;
    const MIN_DT: f64 = 1e3;
    while t < END {
        let h = trial_dt.min(END - t);
        let before_trial = state;
        match ft03_adaptive_step(&model, &state, h, StepControl::default()) {
            Ok(step) => {
                state = step.state;
                accepted_steps += 1;
                max_local_error = max_local_error.max(step.local_error);
                for a in 0..3 {
                    for k in 0..3 {
                        events.photo_per_cm3[a][k] += step.events.photo_per_cm3[a][k];
                    }
                    events.collision_per_cm3[a] += step.events.collision_per_cm3[a];
                    events.recombination_per_cm3[a] += step.events.recombination_per_cm3[a];
                }
                for k in 0..2 {
                    events.dr_per_cm3[k] += step.events.dr_per_cm3[k];
                }
                let temperature = model.gas.temperature(&state)?;
                temperature_min = temperature_min.min(temperature);
                temperature_max = temperature_max.max(temperature);
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
    let g = &model.gas;
    let mut j = [0.0; 3];
    for (a, value) in j.iter_mut().enumerate() {
        *value = events.photo_per_cm3[a].iter().sum::<f64>() + events.collision_per_cm3[a]
            - events.recombination_per_cm3[a];
    }
    j[1] -= events.dr_per_cm3.iter().sum::<f64>();
    let mut event_residual: f64 = 0.0;
    event_residual = event_residual
        .max((g.n_h_cm3 * (state.fractions[0] - initial.fractions[0]) - j[0]).abs() / g.n_h_cm3);
    event_residual = event_residual.max(
        (g.n_he_cm3 * (state.fractions[1] - initial.fractions[1]) - j[1] + j[2]).abs() / g.n_he_cm3,
    );
    event_residual = event_residual
        .max((g.n_he_cm3 * (state.fractions[2] - initial.fractions[2]) - j[2]).abs() / g.n_he_cm3);
    for k in 0..3 {
        let absorbed = (0..3).map(|a| events.photo_per_cm3[a][k]).sum::<f64>();
        event_residual = event_residual.max(
            (initial.photon_cm3[k] - state.photon_cm3[k] - absorbed).abs() / initial.photon_cm3[k],
        );
    }
    let temperature = g.temperature(&state)?;
    let energy_residual = (g.total_energy(&state)? - initial_energy) / initial_energy;
    println!(
        "{{\"model_id\":\"{FT03_MODEL_ID}\",\"dt_s\":{requested_dt},\
         \"t_end_s\":{END},\"source_site\":\"backward_euler_endpoint\",\
         \"scientific_admission\":\"HOLD\",\"F04_certificate_completed\":false,\
         \"accepted_steps\":{accepted_steps},\"rejected_steps\":{rejected_steps},\
         \"rejected_candidate_writes\":{rejected_candidate_writes},\
         \"max_local_error\":{max_local_error},\"temperature_min_K\":{temperature_min},\
         \"temperature_max_K\":{temperature_max},\
         \"observables\":[{},{},{},{}],\"photons_cm3\":[{},{},{}],\
         \"relative_energy_residual\":{energy_residual},\"scaled_event_residual\":{event_residual}}}",
        state.fractions[0],
        state.fractions[1],
        state.fractions[2],
        temperature.ln(),
        state.photon_cm3[0],
        state.photon_cm3[1],
        state.photon_cm3[2]
    );
    Ok(())
}
