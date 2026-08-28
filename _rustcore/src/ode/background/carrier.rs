//! Certified dyadic cubic-Hermite carriers for RF-02C background events.
//!
//! The dense solver supplies only state samples.  Event expressions remain the
//! closed built-in AST from [`super::events`]; they are never callbacks.

use crate::ode::charts::{self, Chart};

use super::events::{
    compile_carrier_polynomial, evaluate_expression, DomainMargin, EventDefinition, EventFailure,
    CARRIER_DEFECT_BUDGET, CARRIER_MAX_DEPTH, EVENT_ATOL, EVENT_RTOL,
};

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct CertifiedEventPolynomial {
    /// Frozen declaration order in the chart's complete built-in registry.
    pub declaration_index: usize,
    pub id: &'static str,
    pub margin_id: &'static str,
    /// Ascending polynomial coefficient bit patterns.
    pub coefficient_bits: Vec<u64>,
    /// Raw AST values at the solver-dense start, midpoint, and end states.
    pub raw_values: [f64; 3],
    /// Corresponding caller-tolerance domain certificates.
    pub certificate_values: [f64; 3],
}

#[derive(Clone, Debug, PartialEq)]
pub(crate) struct CertifiedSubsegment {
    pub tau0: f64,
    pub tau1: f64,
    pub depth: usize,
    /// Ascending cubic coefficients for every frozen state component.
    pub state_coefficients: Vec<[f64; 4]>,
    pub event_polynomials: Vec<CertifiedEventPolynomial>,
    endpoint_states: [Vec<f64>; 2],
    endpoint_rhs: [Vec<f64>; 2],
}

impl CertifiedSubsegment {
    /// Evaluate the frozen displayed Hermite formula once, in its displayed
    /// term order.  This is the state evaluator used for a selected root.
    pub(crate) fn evaluate_state(&self, theta: f64) -> Result<Vec<f64>, EventFailure> {
        if !theta.is_finite() || !(0.0..=1.0).contains(&theta) {
            return Err(EventFailure::CarrierNonfinite);
        }
        let h = self.tau1 - self.tau0;
        if !h.is_finite() || h == 0.0 {
            return Err(if h == 0.0 {
                EventFailure::NonadvancingAcceptedStep
            } else {
                EventFailure::CarrierNonfinite
            });
        }
        evaluate_hermite_state(
            &self.endpoint_states[0],
            &self.endpoint_states[1],
            &self.endpoint_rhs[0],
            &self.endpoint_rhs[1],
            h,
            theta,
        )
    }
}

fn ensure_finite(values: &[f64]) -> Result<(), EventFailure> {
    if values.iter().all(|value| value.is_finite()) {
        Ok(())
    } else {
        Err(EventFailure::CarrierNonfinite)
    }
}

fn state_infinity_norm(state: &[f64]) -> Result<f64, EventFailure> {
    ensure_finite(state)?;
    Ok(state
        .iter()
        .fold(0.0f64, |maximum, value| maximum.max(value.abs())))
}

fn certificate_margin(
    raw: f64,
    state: &[f64],
    rtol: f64,
    atol: f64,
) -> Result<DomainMargin, EventFailure> {
    let norm = state_infinity_norm(state)?;
    let slack = atol + rtol * 1.0f64.max(norm);
    let certificate = raw + slack;
    if raw.is_finite() && slack.is_finite() && certificate.is_finite() {
        Ok(DomainMargin { raw, certificate })
    } else {
        Err(EventFailure::CarrierNonfinite)
    }
}

fn evaluate_polynomial(coefficient_bits: &[u64], theta: f64) -> Result<f64, EventFailure> {
    let mut value = 0.0f64;
    for coefficient_bits in coefficient_bits.iter().rev() {
        let coefficient = f64::from_bits(*coefficient_bits);
        if !coefficient.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
        value = value * theta + coefficient;
        if !value.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
    }
    Ok(value)
}

fn rhs(chart: &Chart, state: &[f64]) -> Result<Vec<f64>, EventFailure> {
    if state.len() != chart.nstates() {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    ensure_finite(state)?;
    let mut derivative = vec![f64::NAN; state.len()];
    charts::rhs(chart, state, &mut derivative);
    ensure_finite(&derivative)?;
    Ok(derivative)
}

/// Build ascending coefficients without reassociating the frozen formula.
fn hermite_coefficients(
    y0: &[f64],
    y1: &[f64],
    f0: &[f64],
    f1: &[f64],
    h: f64,
) -> Result<Vec<[f64; 4]>, EventFailure> {
    if y0.len() != y1.len() || y0.len() != f0.len() || y0.len() != f1.len() || y0.is_empty() {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    let mut coefficients = Vec::with_capacity(y0.len());
    for index in 0..y0.len() {
        let h_f0 = h * f0[index];
        let h_f1 = h * f1[index];
        let c0 = y0[index];
        let c1 = h_f0;
        let c2 = ((-3.0 * y0[index] - 2.0 * h_f0) + 3.0 * y1[index]) - h_f1;
        let c3 = ((2.0 * y0[index] + h_f0) - 2.0 * y1[index]) + h_f1;
        let component = [c0, c1, c2, c3];
        ensure_finite(&component)?;
        coefficients.push(component);
    }
    Ok(coefficients)
}

fn evaluate_hermite_state(
    y0: &[f64],
    y1: &[f64],
    f0: &[f64],
    f1: &[f64],
    h: f64,
    theta: f64,
) -> Result<Vec<f64>, EventFailure> {
    if y0.len() != y1.len() || y0.len() != f0.len() || y0.len() != f1.len() || y0.is_empty() {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    let theta2 = theta * theta;
    let theta3 = theta2 * theta;
    let basis_y0 = (2.0 * theta3 - 3.0 * theta2) + 1.0;
    let basis_f0 = (theta3 - 2.0 * theta2) + theta;
    let basis_y1 = -2.0 * theta3 + 3.0 * theta2;
    let basis_f1 = theta3 - theta2;
    let mut state = Vec::with_capacity(y0.len());
    for index in 0..y0.len() {
        // Frozen displayed order: y0, h*f0, y1, h*f1.
        let value = ((basis_y0 * y0[index] + basis_f0 * h * f0[index]) + basis_y1 * y1[index])
            + basis_f1 * h * f1[index];
        if !value.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
        state.push(value);
    }
    Ok(state)
}

fn event_carriers(
    armed_events: &[EventDefinition],
    state_coefficients: &[[f64; 4]],
    dense_states: [&[f64]; 3],
    kappa: f64,
    rtol: f64,
    atol: f64,
) -> Result<(Vec<CertifiedEventPolynomial>, f64), EventFailure> {
    let mut carriers = Vec::with_capacity(armed_events.len());
    let mut maximum_defect = 0.0f64;
    for event in armed_events {
        let coefficient_bits =
            compile_carrier_polynomial(&event.expression, state_coefficients, kappa)?;
        let polynomial_midpoint = evaluate_polynomial(&coefficient_bits, 0.5)?;
        let raw_values = [
            evaluate_expression(&event.expression, dense_states[0], kappa)?,
            evaluate_expression(&event.expression, dense_states[1], kappa)?,
            evaluate_expression(&event.expression, dense_states[2], kappa)?,
        ];
        let event_scale = EVENT_ATOL
            + EVENT_RTOL
                * 1.0f64
                    .max(raw_values[1].abs())
                    .max(polynomial_midpoint.abs());
        let defect = (raw_values[1] - polynomial_midpoint).abs() / event_scale;
        if !(event_scale.is_finite() && event_scale > 0.0 && defect.is_finite()) {
            return Err(EventFailure::CarrierNonfinite);
        }
        maximum_defect = maximum_defect.max(defect);
        let start = certificate_margin(raw_values[0], dense_states[0], rtol, atol)?;
        let midpoint = certificate_margin(raw_values[1], dense_states[1], rtol, atol)?;
        let end = certificate_margin(raw_values[2], dense_states[2], rtol, atol)?;
        carriers.push(CertifiedEventPolynomial {
            declaration_index: event.declaration_order,
            id: event.id,
            margin_id: event.margin_id,
            coefficient_bits,
            raw_values,
            certificate_values: [start.certificate, midpoint.certificate, end.certificate],
        });
    }
    Ok((carriers, maximum_defect))
}

#[allow(clippy::too_many_arguments)]
fn certify_interval<F>(
    chart: &Chart,
    kappa: f64,
    tau0: f64,
    y0: Vec<f64>,
    tau1: f64,
    y1: Vec<f64>,
    rtol: f64,
    atol: f64,
    armed_events: &[EventDefinition],
    depth: usize,
    interpolate: &mut F,
    output: &mut Vec<CertifiedSubsegment>,
) -> Result<(), EventFailure>
where
    F: FnMut(f64) -> Result<Vec<f64>, EventFailure>,
{
    if !(tau0.is_finite() && tau1.is_finite()) {
        return Err(EventFailure::CarrierNonfinite);
    }
    if tau0 == tau1 {
        return Err(EventFailure::NonadvancingAcceptedStep);
    }
    if y0.len() != chart.nstates() || y1.len() != chart.nstates() {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    ensure_finite(&y0)?;
    ensure_finite(&y1)?;

    let midpoint_tau = tau0.midpoint(tau1);
    if !midpoint_tau.is_finite() {
        return Err(EventFailure::CarrierNonfinite);
    }
    let midpoint_state = interpolate(midpoint_tau)?;
    if midpoint_state.len() != chart.nstates() {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    ensure_finite(&midpoint_state)?;

    let f0 = rhs(chart, &y0)?;
    let f1 = rhs(chart, &y1)?;
    let h = tau1 - tau0;
    if !h.is_finite() {
        return Err(EventFailure::CarrierNonfinite);
    }
    let state_coefficients = hermite_coefficients(&y0, &y1, &f0, &f1, h)?;
    let hermite_midpoint = evaluate_hermite_state(&y0, &y1, &f0, &f1, h, 0.5)?;

    let mut maximum_state_defect = 0.0f64;
    for (actual, carrier) in midpoint_state.iter().zip(&hermite_midpoint) {
        let scale = atol + rtol * 1.0f64.max(actual.abs()).max(carrier.abs());
        let defect = (actual - carrier).abs() / scale;
        if !(scale.is_finite() && scale > 0.0 && defect.is_finite()) {
            return Err(EventFailure::CarrierNonfinite);
        }
        maximum_state_defect = maximum_state_defect.max(defect);
    }

    let (event_polynomials, maximum_event_defect) = event_carriers(
        armed_events,
        &state_coefficients,
        [&y0, &midpoint_state, &y1],
        kappa,
        rtol,
        atol,
    )?;

    if maximum_state_defect <= CARRIER_DEFECT_BUDGET
        && maximum_event_defect <= CARRIER_DEFECT_BUDGET
    {
        output.push(CertifiedSubsegment {
            tau0,
            tau1,
            depth,
            state_coefficients,
            event_polynomials,
            endpoint_states: [y0, y1],
            endpoint_rhs: [f0, f1],
        });
        return Ok(());
    }

    if depth >= CARRIER_MAX_DEPTH || midpoint_tau == tau0 || midpoint_tau == tau1 {
        return Err(EventFailure::CarrierCertificateFailure);
    }

    // Left then right is the frozen increasing-theta ownership order.  It is
    // also the actual integration order for a backward accepted step because
    // theta still increases from tau0 to tau1.
    certify_interval(
        chart,
        kappa,
        tau0,
        y0,
        midpoint_tau,
        midpoint_state.clone(),
        rtol,
        atol,
        armed_events,
        depth + 1,
        interpolate,
        output,
    )?;
    certify_interval(
        chart,
        kappa,
        midpoint_tau,
        midpoint_state,
        tau1,
        y1,
        rtol,
        atol,
        armed_events,
        depth + 1,
        interpolate,
        output,
    )
}

/// Certify one accepted solver step as ordered dyadic Hermite subsegments.
///
/// `interpolate` is the native solver's dense-state accessor.  It cannot
/// supply event logic; every event polynomial is compiled from `armed_events`.
#[allow(clippy::too_many_arguments)]
pub(crate) fn certify_step<F>(
    chart: &Chart,
    kappa: f64,
    tau0: f64,
    y0: &[f64],
    tau1: f64,
    y1: &[f64],
    rtol: f64,
    atol: f64,
    armed_events: &[EventDefinition],
    mut interpolate: F,
) -> Result<Vec<CertifiedSubsegment>, EventFailure>
where
    F: FnMut(f64) -> Result<Vec<f64>, EventFailure>,
{
    if !(kappa.is_finite() && rtol.is_finite() && atol.is_finite()) || rtol < 0.0 || atol < 0.0 {
        return Err(EventFailure::CarrierNonfinite);
    }
    if let Chart::ClassB {
        kappa: chart_kappa, ..
    } = chart
    {
        if chart_kappa.to_bits() != kappa.to_bits() {
            return Err(EventFailure::CarrierCertificateFailure);
        }
    }
    if y0.len() != chart.nstates() || y1.len() != chart.nstates() {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    ensure_finite(y0)?;
    ensure_finite(y1)?;

    // V2 makes the solver-dense representation authoritative at every
    // carrier endpoint, including the two outer accepted-step endpoints.
    // Some BDF implementations retain a corrected `state().y` whose final
    // bits differ from `interpolate(tau1)`; mixing those representations
    // creates a non-vanishing right-end defect under dyadic subdivision.
    let dense_y0 = interpolate(tau0)?;
    let dense_y1 = interpolate(tau1)?;
    let mut output = Vec::new();
    certify_interval(
        chart,
        kappa,
        tau0,
        dense_y0,
        tau1,
        dense_y1,
        rtol,
        atol,
        armed_events,
        0,
        &mut interpolate,
        &mut output,
    )?;
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ode::background::events::{
        builtin_registry, compile_carrier_polynomial, isolate_exact_roots, EventDirection,
        EventExpression, RootIsolation,
    };

    fn class_a() -> Chart {
        Chart::ClassA { gamma: 1.0 }
    }

    fn isotropic_type_ix_tau(h_bar: f64) -> f64 {
        -(((1.0 + h_bar) / (1.0 - h_bar)).ln() + 2.0 * h_bar.atan())
    }

    fn isotropic_type_ix_state(h_bar: f64) -> Vec<f64> {
        let curvature = (2.0 * (1.0 - h_bar * h_bar)).sqrt();
        vec![h_bar, 0.0, 0.0, 0.0, curvature, curvature, curvature]
    }

    fn isolated_isotropic_root(chart: &Chart, h_left: f64, h_right: f64) -> (f64, f64) {
        let tau0 = isotropic_type_ix_tau(h_left);
        let tau1 = isotropic_type_ix_tau(h_right);
        let state0 = isotropic_type_ix_state(h_left);
        let state1 = isotropic_type_ix_state(h_right);
        let mut rhs0 = vec![0.0; 7];
        let mut rhs1 = vec![0.0; 7];
        charts::rhs(chart, &state0, &mut rhs0);
        charts::rhs(chart, &state1, &mut rhs1);
        let coefficients =
            hermite_coefficients(&state0, &state1, &rhs0, &rhs1, tau1 - tau0).unwrap();
        let event =
            compile_carrier_polynomial(&EventExpression::State(0), &coefficients, 0.0).unwrap();
        let roots = match isolate_exact_roots(&event, EventDirection::Decreasing, false).unwrap() {
            RootIsolation::Roots(roots) => roots,
            RootIsolation::ContinuumZero => panic!("Type-IX H carrier is not identically zero"),
        };
        assert_eq!(roots.len(), 1);
        let theta = f64::from_bits(roots[0].theta_bits);
        let root_state =
            evaluate_hermite_state(&state0, &state1, &rhs0, &rhs1, tau1 - tau0, theta).unwrap();
        let mut constraints = [0.0; 2];
        charts::constraint_values(chart, &root_state, &mut constraints).unwrap();
        let norm = root_state
            .iter()
            .fold(0.0f64, |maximum, value| maximum.max(value.abs()));
        let scale = 1.0e-12 + 1.0e-10 * norm.max(1.0);
        let normalized = constraints
            .iter()
            .fold(0.0f64, |maximum, value| maximum.max(value.abs() / scale));
        let tau = (tau1 - tau0).mul_add(theta, tau0);
        (tau, normalized)
    }

    #[test]
    fn rf02c_carrier_accepts_exact_dense_equilibrium_and_exposes_margins() {
        let chart = class_a();
        let state = vec![0.0; chart.nstates()];
        let events = builtin_registry("class_a").unwrap();
        let future_events = builtin_registry("type_ix_d_future").unwrap();
        assert_eq!(
            future_events
                .iter()
                .map(|event| event.declaration_order)
                .collect::<Vec<_>>(),
            (0..future_events.len()).collect::<Vec<_>>()
        );
        assert!(future_events.last().unwrap().one_shot_after_transition);
        let segments = certify_step(
            &chart,
            0.0,
            0.0,
            &state,
            1.0,
            &state,
            1.0e-10,
            1.0e-12,
            &events,
            |_| Ok(state.clone()),
        )
        .unwrap();
        assert_eq!(segments.len(), 1);
        assert_eq!(segments[0].depth, 0);
        assert_eq!(segments[0].state_coefficients, vec![[0.0; 4]; 5]);
        let event = &segments[0].event_polynomials[0];
        assert_eq!(event.coefficient_bits, vec![1.0f64.to_bits()]);
        assert_eq!(event.raw_values, [1.0; 3]);
        assert_eq!(event.certificate_values, [1.0 + 1.01e-10; 3]);
        assert_eq!(segments[0].evaluate_state(0.5).unwrap(), state);
    }

    #[test]
    fn rf02c_carrier_subdivides_until_both_child_certificates_pass() {
        let chart = class_a();
        let zero = vec![0.0; chart.nstates()];
        let mut middle = zero.clone();
        middle[0] = 0.1;
        let events = builtin_registry("class_a").unwrap();

        let mut middle_rhs = vec![0.0; chart.nstates()];
        charts::rhs(&chart, &middle, &mut middle_rhs);
        let left_quarter =
            evaluate_hermite_state(&zero, &middle, &zero, &middle_rhs, 0.5, 0.5).unwrap();
        let right_quarter =
            evaluate_hermite_state(&middle, &zero, &middle_rhs, &zero, 0.5, 0.5).unwrap();
        let segments = certify_step(
            &chart,
            0.0,
            0.0,
            &zero,
            1.0,
            &zero,
            0.0,
            1.0e-2,
            &events,
            |tau| {
                if tau.to_bits() == 0.0f64.to_bits() || tau.to_bits() == 1.0f64.to_bits() {
                    Ok(zero.clone())
                } else if tau.to_bits() == 0.5f64.to_bits() {
                    Ok(middle.clone())
                } else if tau.to_bits() == 0.25f64.to_bits() {
                    Ok(left_quarter.clone())
                } else if tau.to_bits() == 0.75f64.to_bits() {
                    Ok(right_quarter.clone())
                } else {
                    Err(EventFailure::CarrierCertificateFailure)
                }
            },
        )
        .unwrap();
        assert_eq!(segments.len(), 2);
        assert_eq!(
            segments
                .iter()
                .map(|segment| segment.depth)
                .collect::<Vec<_>>(),
            vec![1, 1]
        );
        assert_eq!(segments[0].tau0.to_bits(), 0.0f64.to_bits());
        assert_eq!(segments[0].tau1.to_bits(), 0.5f64.to_bits());
        assert_eq!(segments[1].tau0.to_bits(), 0.5f64.to_bits());
        assert_eq!(segments[1].tau1.to_bits(), 1.0f64.to_bits());
    }

    #[test]
    fn rf02c_carrier_outer_endpoints_use_one_dense_representation() {
        let chart = class_a();
        let dense = vec![0.0; chart.nstates()];
        let mut corrected_solver_endpoint = dense.clone();
        corrected_solver_endpoint[0] = 1.2e-10;
        let events = builtin_registry("class_a").unwrap();
        let segments = certify_step(
            &chart,
            0.0,
            0.0,
            &dense,
            1.0,
            &corrected_solver_endpoint,
            1.0e-10,
            1.0e-12,
            &events,
            |_| Ok(dense.clone()),
        )
        .unwrap();
        assert_eq!(segments.len(), 1);
        assert_eq!(segments[0].state_coefficients, vec![[0.0; 4]; 5]);
        assert_eq!(segments[0].evaluate_state(1.0).unwrap(), dense);
    }

    #[test]
    fn rf02c_carrier_depth_exhaustion_and_dense_nonfinite_are_typed() {
        let chart = class_a();
        let zero = vec![0.0; chart.nstates()];
        let events = builtin_registry("class_a").unwrap();
        let mut output = Vec::new();
        let exhausted = certify_interval(
            &chart,
            0.0,
            0.0,
            zero.clone(),
            1.0,
            zero.clone(),
            0.0,
            1.0e-12,
            &events,
            CARRIER_MAX_DEPTH,
            &mut |_| {
                let mut inconsistent = zero.clone();
                inconsistent[0] = 1.0;
                Ok(inconsistent)
            },
            &mut output,
        );
        assert_eq!(exhausted, Err(EventFailure::CarrierCertificateFailure));
        assert!(output.is_empty());

        let nonfinite = certify_step(
            &chart,
            0.0,
            0.0,
            &zero,
            1.0,
            &zero,
            1.0e-10,
            1.0e-12,
            &events,
            |_| {
                let mut state = zero.clone();
                state[0] = f64::NAN;
                Ok(state)
            },
        );
        assert_eq!(nonfinite, Err(EventFailure::CarrierNonfinite));
    }

    #[test]
    fn rf02c_type_ix_coarse_root_fails_equality_and_one_local_replay_passes() {
        let chart = Chart::TypeIXD {
            gamma: 1.0,
            future: true,
        };
        let h_left = 0.006;
        let h_right = -0.004;
        let tau_left = isotropic_type_ix_tau(h_left);
        let tau_right = isotropic_type_ix_tau(h_right);
        let tau_mid = tau_left.midpoint(tau_right);
        let mut h_mid = 0.5 * (h_left + h_right);
        for _ in 0..16 {
            let residual = isotropic_type_ix_tau(h_mid) - tau_mid;
            let derivative = -4.0 / (1.0 - h_mid.powi(4));
            h_mid -= residual / derivative;
        }

        let (coarse_tau, coarse_residual) = isolated_isotropic_root(&chart, h_left, h_right);
        let (replayed_tau, replayed_residual) = isolated_isotropic_root(&chart, h_mid, h_right);
        let root_budget = 8.0 * (EVENT_ATOL + EVENT_RTOL);

        assert!(coarse_residual > 1.0, "coarse residual={coarse_residual:e}");
        assert!(
            replayed_residual <= 1.0,
            "replayed residual={replayed_residual:e}"
        );
        assert!((coarse_tau - 0.0).abs() <= root_budget);
        assert!((replayed_tau - 0.0).abs() <= root_budget);
        assert!((tau_right - tau_mid).abs() <= 0.5 * (tau_right - tau_left).abs());
    }
}
