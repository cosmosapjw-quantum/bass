//! Deterministic fixed-context RK4 for the RF-03 production matter state.

use super::eos::GammaLawModel;
use super::force::{force, MatterForce};
use super::state::{MatterContext, MatterError, MatterState};

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum IntegrationTerminal {
    Complete,
    DomainViolation { step: usize, detail: String },
}

impl IntegrationTerminal {
    pub fn code(&self) -> &'static str {
        match self {
            Self::Complete => "COMPLETE",
            Self::DomainViolation { .. } => "RF03_DOMAIN_TERMINATION",
        }
    }

    pub fn detail(&self) -> Option<&str> {
        match self {
            Self::Complete => None,
            Self::DomainViolation { detail, .. } => Some(detail),
        }
    }

    pub fn terminal_index(&self, completed_steps: usize) -> usize {
        match self {
            Self::Complete => completed_steps,
            Self::DomainViolation { step, .. } => *step,
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct IntegrationResult {
    pub times: Vec<f64>,
    pub states: Vec<[f64; 4]>,
    pub terminal: IntegrationTerminal,
}

#[inline]
fn shifted(state: MatterState, force: MatterForce, scale: f64) -> Result<MatterState, MatterError> {
    MatterState::new(
        state.omega + scale * force.omega,
        [
            state.v[0] + scale * force.v[0],
            state.v[1] + scale * force.v[1],
            state.v[2] + scale * force.v[2],
        ],
    )
}

fn rk4_step(
    model: GammaLawModel,
    state: MatterState,
    context: MatterContext,
    dt: f64,
) -> Result<MatterState, MatterError> {
    let k1 = force(model, state, context)?;
    let k2 = force(model, shifted(state, k1, 0.5 * dt)?, context)?;
    let k3 = force(model, shifted(state, k2, 0.5 * dt)?, context)?;
    let k4 = force(model, shifted(state, k3, dt)?, context)?;
    MatterState::new(
        state.omega + dt * (k1.omega + 2.0 * k2.omega + 2.0 * k3.omega + k4.omega) / 6.0,
        [
            state.v[0] + dt * (k1.v[0] + 2.0 * k2.v[0] + 2.0 * k3.v[0] + k4.v[0]) / 6.0,
            state.v[1] + dt * (k1.v[1] + 2.0 * k2.v[1] + 2.0 * k3.v[1] + k4.v[1]) / 6.0,
            state.v[2] + dt * (k1.v[2] + 2.0 * k2.v[2] + 2.0 * k3.v[2] + k4.v[2]) / 6.0,
        ],
    )
}

fn rk4_step_between_contexts(
    model: GammaLawModel,
    state: MatterState,
    left: MatterContext,
    right: MatterContext,
    dt: f64,
) -> Result<MatterState, MatterError> {
    let midpoint = left.interpolate(right, 0.5);
    let k1 = force(model, state, left)?;
    let k2 = force(model, shifted(state, k1, 0.5 * dt)?, midpoint)?;
    let k3 = force(model, shifted(state, k2, 0.5 * dt)?, midpoint)?;
    let k4 = force(model, shifted(state, k3, dt)?, right)?;
    MatterState::new(
        state.omega + dt * (k1.omega + 2.0 * k2.omega + 2.0 * k3.omega + k4.omega) / 6.0,
        [
            state.v[0] + dt * (k1.v[0] + 2.0 * k2.v[0] + 2.0 * k3.v[0] + k4.v[0]) / 6.0,
            state.v[1] + dt * (k1.v[1] + 2.0 * k2.v[1] + 2.0 * k3.v[1] + k4.v[1]) / 6.0,
            state.v[2] + dt * (k1.v[2] + 2.0 * k2.v[2] + 2.0 * k3.v[2] + k4.v[2]) / 6.0,
        ],
    )
}

pub fn integrate_fixed_context(
    model: GammaLawModel,
    initial: MatterState,
    context: MatterContext,
    t_end: f64,
    nsteps: usize,
) -> Result<IntegrationResult, MatterError> {
    if !t_end.is_finite() {
        return Err(MatterError::Input("t_end must be finite".to_string()));
    }
    if nsteps == 0 {
        return Err(MatterError::Input(
            "nsteps must be at least one".to_string(),
        ));
    }
    initial.validate()?;
    let dt = t_end / nsteps as f64;
    let mut times = Vec::with_capacity(nsteps + 1);
    let mut states = Vec::with_capacity(nsteps + 1);
    let mut current = initial;
    times.push(0.0);
    states.push(current.as_array());
    for step in 0..nsteps {
        match rk4_step(model, current, context, dt) {
            Ok(next) => {
                current = next;
                times.push((step + 1) as f64 * dt);
                states.push(current.as_array());
            }
            Err(MatterError::Domain(detail)) => {
                return Ok(IntegrationResult {
                    times,
                    states,
                    terminal: IntegrationTerminal::DomainViolation { step, detail },
                });
            }
            Err(other) => return Err(other),
        }
    }
    Ok(IntegrationResult {
        times,
        states,
        terminal: IntegrationTerminal::Complete,
    })
}

pub fn integrate_context_history(
    model: GammaLawModel,
    initial: MatterState,
    times: &[f64],
    contexts: &[MatterContext],
) -> Result<IntegrationResult, MatterError> {
    if times.len() < 2 || contexts.len() != times.len() {
        return Err(MatterError::Input(
            "context integration requires matching histories with at least two samples".to_string(),
        ));
    }
    if times.iter().any(|time| !time.is_finite()) {
        return Err(MatterError::Input(
            "every context-history time must be finite".to_string(),
        ));
    }
    let first_dt = times[1] - times[0];
    if first_dt == 0.0 {
        return Err(MatterError::Input(
            "context-history times must be strictly monotone".to_string(),
        ));
    }
    let direction = first_dt.signum();
    if times.windows(2).any(|window| {
        let dt = window[1] - window[0];
        dt == 0.0 || dt.signum() != direction
    }) {
        return Err(MatterError::Input(
            "context-history times must be strictly monotone in one direction".to_string(),
        ));
    }
    initial.validate()?;
    let mut states = Vec::with_capacity(times.len());
    let mut retained_times = Vec::with_capacity(times.len());
    let mut current = initial;
    retained_times.push(times[0]);
    states.push(current.as_array());
    for step in 0..times.len() - 1 {
        let dt = times[step + 1] - times[step];
        match rk4_step_between_contexts(model, current, contexts[step], contexts[step + 1], dt) {
            Ok(next) => {
                current = next;
                retained_times.push(times[step + 1]);
                states.push(current.as_array());
            }
            Err(MatterError::Domain(detail)) => {
                return Ok(IntegrationResult {
                    times: retained_times,
                    states,
                    terminal: IntegrationTerminal::DomainViolation { step, detail },
                });
            }
            Err(other) => return Err(other),
        }
    }
    Ok(IntegrationResult {
        times: retained_times,
        states,
        terminal: IntegrationTerminal::Complete,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::matter::EXPLICIT_GAMMA_LAW_MODEL_ID;

    #[test]
    fn rf03_fixed_context_rk4_is_repeatable_and_cools() {
        let model = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 4.0 / 3.0).unwrap();
        let initial = MatterState::new(0.5, [0.0; 3]).unwrap();
        let context =
            MatterContext::new([[0.0; 3]; 3], [[0.0; 3]; 3], [0.0; 3], [0.0; 3], 0.5).unwrap();
        let first = integrate_fixed_context(model, initial, context, 1.0, 128).unwrap();
        let second = integrate_fixed_context(model, initial, context, 1.0, 128).unwrap();
        assert_eq!(first, second);
        assert_eq!(first.terminal, IntegrationTerminal::Complete);
        assert!(first.states.last().unwrap()[0] < initial.omega);
    }

    #[test]
    fn rf03_integrator_returns_typed_physical_boundary_terminal() {
        let model = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 2.0).unwrap();
        let initial = MatterState::new(0.2, [0.9, 0.0, 0.0]).unwrap();
        let context =
            MatterContext::new([[0.0; 3]; 3], [[0.0; 3]; 3], [0.0; 3], [0.0; 3], 0.0).unwrap();
        let result = integrate_fixed_context(model, initial, context, 1.0, 20).unwrap();
        assert!(matches!(
            result.terminal,
            IntegrationTerminal::DomainViolation { .. }
        ));
        assert!(result
            .states
            .iter()
            .flatten()
            .all(|value| value.is_finite()));
    }

    #[test]
    fn rf03_context_history_is_deterministic_and_uses_endpoint_contexts() {
        let model = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 4.0 / 3.0).unwrap();
        let initial = MatterState::new(0.5, [0.0; 3]).unwrap();
        let left =
            MatterContext::new([[0.0; 3]; 3], [[0.0; 3]; 3], [0.0; 3], [0.0; 3], 0.4).unwrap();
        let right =
            MatterContext::new([[0.0; 3]; 3], [[0.0; 3]; 3], [0.0; 3], [0.0; 3], 0.5).unwrap();
        let first = integrate_context_history(model, initial, &[0.0, 0.2], &[left, right]).unwrap();
        let second =
            integrate_context_history(model, initial, &[0.0, 0.2], &[left, right]).unwrap();
        assert_eq!(first, second);
        assert_eq!(first.terminal, IntegrationTerminal::Complete);
        assert!(first.states[1][0] < initial.omega);
    }
}
