//! Closed RF-02C event algebra and exact root substrate.

use super::exact::{
    f64_bits_to_rational, isolate_unit_roots, ExactArithmeticError, ExactPolynomial,
    RepresentedExactRoot,
};
use num_rational::BigRational;
use num_traits::{Signed, Zero};

const BACKGROUND_RTOL: f64 = 1.0e-10;
const BACKGROUND_ATOL: f64 = 1.0e-12;
pub(crate) const EVENT_RTOL: f64 = 1.0e-10;
pub(crate) const EVENT_ATOL: f64 = 1.0e-12;
pub(crate) const CARRIER_DEFECT_BUDGET: f64 = 0.25;
pub(crate) const CARRIER_MAX_DEPTH: usize = 24;
const MAX_EVENT_DEGREE: usize = 6;

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) enum EventExpression {
    State(usize),
    ParameterKappa,
    ConstF64Bits(u64),
    Add(Box<EventExpression>, Box<EventExpression>),
    Sub(Box<EventExpression>, Box<EventExpression>),
    Mul(Box<EventExpression>, Box<EventExpression>),
    Neg(Box<EventExpression>),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum EventDirection {
    Decreasing,
    Any,
    Increasing,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct EventDefinition {
    pub id: &'static str,
    pub margin_id: &'static str,
    pub expression: EventExpression,
    pub direction: EventDirection,
    pub priority: u32,
    pub declaration_order: usize,
    pub segment_terminal: bool,
    pub trajectory_terminal: bool,
    pub transition_id: Option<&'static str>,
    pub one_shot_after_transition: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum EventFailure {
    UnsupportedExpression,
    CarrierNonfinite,
    CarrierCertificateFailure,
    NonadvancingAcceptedStep,
    RootRepresentationFailure,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct IsolatedRoot {
    pub theta_bits: u64,
    pub multiplicity: usize,
    pub direction: EventDirection,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) enum RootIsolation {
    Roots(Vec<IsolatedRoot>),
    ContinuumZero,
}

#[derive(Clone, Copy, Debug)]
pub(crate) struct CarrierCertificateInput<'a> {
    pub tau0: f64,
    pub tau1: f64,
    pub endpoint_states: &'a [&'a [f64]],
    pub endpoint_rhs: &'a [&'a [f64]],
    pub midpoint_state: &'a [f64],
    pub midpoint_event_values: &'a [f64],
    pub depth: usize,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) struct DomainMargin {
    pub raw: f64,
    pub certificate: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum InitialDomainClassification {
    Interior,
    BoundaryNeighborhood,
    Violation,
}

pub(crate) const REGISTRY_SHA256: &str =
    "8b3d342328b4549c797fca1c106181657f832a07fafed29eb498450465b43918";

pub(crate) const CLOSED_AST_OPS: [&str; 7] = [
    "state",
    "parameter",
    "const_f64_bits",
    "add",
    "sub",
    "mul",
    "neg",
];

fn state(index: usize) -> EventExpression {
    EventExpression::State(index)
}

fn constant(bits: u64) -> EventExpression {
    EventExpression::ConstF64Bits(bits)
}

fn add(lhs: EventExpression, rhs: EventExpression) -> EventExpression {
    EventExpression::Add(Box::new(lhs), Box::new(rhs))
}

fn sub(lhs: EventExpression, rhs: EventExpression) -> EventExpression {
    EventExpression::Sub(Box::new(lhs), Box::new(rhs))
}

fn mul(lhs: EventExpression, rhs: EventExpression) -> EventExpression {
    EventExpression::Mul(Box::new(lhs), Box::new(rhs))
}

fn square(index: usize) -> EventExpression {
    mul(state(index), state(index))
}

fn event(
    id: &'static str,
    margin_id: &'static str,
    expression: EventExpression,
    priority: u32,
) -> EventDefinition {
    EventDefinition {
        id,
        margin_id,
        expression,
        direction: EventDirection::Decreasing,
        priority,
        declaration_order: 0,
        segment_terminal: true,
        trajectory_terminal: true,
        transition_id: None,
        one_shot_after_transition: false,
    }
}

fn class_a_registry() -> Vec<EventDefinition> {
    let shear = add(square(0), square(1));
    let diagonal_curvature = add(add(square(2), square(3)), square(4));
    let mixed_curvature = add(
        add(mul(state(2), state(3)), mul(state(3), state(4))),
        mul(state(4), state(2)),
    );
    let curvature = mul(
        constant(0x3fb5_5555_5555_5555),
        sub(
            diagonal_curvature,
            mul(constant(0x4000_0000_0000_0000), mixed_curvature),
        ),
    );
    vec![event(
        "domain.class_a.omega",
        "Omega",
        sub(constant(0x3ff0_0000_0000_0000), add(shear, curvature)),
        0,
    )]
}

fn class_b_n_tilde() -> EventExpression {
    mul(
        constant(0x3fd5_5555_5555_5555),
        sub(square(4), mul(EventExpression::ParameterKappa, state(3))),
    )
}

fn class_b_registry() -> Vec<EventDefinition> {
    let omega_rhs = add(add(add(square(0), state(1)), class_b_n_tilde()), state(3));
    vec![
        event("domain.class_b.sigma_tilde", "Sigma_tilde", state(1), 0),
        event("domain.class_b.n_tilde", "N_tilde", class_b_n_tilde(), 1),
        event("domain.class_b.a_tilde", "A_tilde", state(3), 2),
        event(
            "domain.class_b.omega",
            "Omega",
            sub(constant(0x3ff0_0000_0000_0000), omega_rhs),
            3,
        ),
    ]
}

fn exceptional_registry() -> Vec<EventDefinition> {
    let rhs = add(
        add(
            add(add(add(square(0), square(1)), square(2)), square(3)),
            square(4),
        ),
        mul(constant(0x4010_0000_0000_0000), square(5)),
    );
    vec![event(
        "domain.exceptional.omega",
        "Omega",
        sub(constant(0x3ff0_0000_0000_0000), rhs),
        0,
    )]
}

fn type_ix_registry(include_recollapse: bool) -> Vec<EventDefinition> {
    let shear = mul(
        constant(0x3fc5_5555_5555_5555),
        add(add(square(1), square(2)), square(3)),
    );
    let curvature = mul(
        constant(0x3fb5_5555_5555_5555),
        add(add(square(4), square(5)), square(6)),
    );
    let mut registry = vec![
        event(
            "domain.type_ix.omega",
            "Omega",
            sub(constant(0x3ff0_0000_0000_0000), add(shear, curvature)),
            0,
        ),
        event(
            "domain.type_ix.h_upper",
            "1-H_bar",
            sub(constant(0x3ff0_0000_0000_0000), state(0)),
            1,
        ),
        event(
            "domain.type_ix.h_lower",
            "1+H_bar",
            add(constant(0x3ff0_0000_0000_0000), state(0)),
            2,
        ),
        event("domain.type_ix.n1n2", "N1*N2", mul(state(4), state(5)), 3),
        event("domain.type_ix.n2n3", "N2*N3", mul(state(5), state(6)), 4),
        event("domain.type_ix.n3n1", "N3*N1", mul(state(6), state(4)), 5),
    ];
    if include_recollapse {
        registry.push(EventDefinition {
            id: "type_ix_recollapse",
            margin_id: "H_bar",
            expression: state(0),
            direction: EventDirection::Decreasing,
            priority: 20,
            declaration_order: 0,
            segment_terminal: true,
            trajectory_terminal: false,
            transition_id: Some("type_ix_expanding_to_contracting"),
            one_shot_after_transition: true,
        });
    }
    registry
}

pub(crate) fn builtin_registry(chart: &str) -> Result<Vec<EventDefinition>, EventFailure> {
    let mut registry = match chart {
        "class_a" => class_a_registry(),
        "class_b" => class_b_registry(),
        "exceptional" => exceptional_registry(),
        "type_ix_d" => type_ix_registry(false),
        "type_ix_d_future" => type_ix_registry(true),
        _ => return Err(EventFailure::UnsupportedExpression),
    };
    for (declaration_order, event) in registry.iter_mut().enumerate() {
        event.declaration_order = declaration_order;
    }
    Ok(registry)
}

/// Evaluate a closed event AST in the contract's fixed binary64 order.
pub(crate) fn evaluate_expression(
    expression: &EventExpression,
    state: &[f64],
    kappa: f64,
) -> Result<f64, EventFailure> {
    let value = match expression {
        EventExpression::State(index) => *state
            .get(*index)
            .ok_or(EventFailure::UnsupportedExpression)?,
        EventExpression::ParameterKappa => kappa,
        EventExpression::ConstF64Bits(bits) => f64::from_bits(*bits),
        EventExpression::Add(lhs, rhs) => {
            let left = evaluate_expression(lhs, state, kappa)?;
            let right = evaluate_expression(rhs, state, kappa)?;
            left + right
        }
        EventExpression::Sub(lhs, rhs) => {
            let left = evaluate_expression(lhs, state, kappa)?;
            let right = evaluate_expression(rhs, state, kappa)?;
            left - right
        }
        EventExpression::Mul(lhs, rhs) => {
            let left = evaluate_expression(lhs, state, kappa)?;
            let right = evaluate_expression(rhs, state, kappa)?;
            left * right
        }
        EventExpression::Neg(inner) => -evaluate_expression(inner, state, kappa)?,
    };
    if value.is_finite() {
        Ok(value)
    } else {
        Err(EventFailure::CarrierNonfinite)
    }
}

fn trim_f64_polynomial(mut coefficients: Vec<f64>) -> Vec<f64> {
    while coefficients.len() > 1 && coefficients.last().is_some_and(|value| *value == 0.0) {
        coefficients.pop();
    }
    coefficients
}

fn ensure_finite_polynomial(coefficients: Vec<f64>) -> Result<Vec<f64>, EventFailure> {
    if coefficients
        .iter()
        .all(|coefficient| coefficient.is_finite())
    {
        Ok(trim_f64_polynomial(coefficients))
    } else {
        Err(EventFailure::CarrierNonfinite)
    }
}

fn compile_expression(
    expression: &EventExpression,
    state_carriers: &[[f64; 4]],
    kappa: f64,
) -> Result<Vec<f64>, EventFailure> {
    let result = match expression {
        EventExpression::State(index) => state_carriers
            .get(*index)
            .map(|carrier| carrier.to_vec())
            .ok_or(EventFailure::UnsupportedExpression)?,
        EventExpression::ParameterKappa => {
            if !kappa.is_finite() {
                return Err(EventFailure::CarrierNonfinite);
            }
            vec![kappa]
        }
        EventExpression::ConstF64Bits(bits) => {
            let value = f64::from_bits(*bits);
            if !value.is_finite() {
                return Err(EventFailure::CarrierNonfinite);
            }
            vec![value]
        }
        EventExpression::Add(lhs, rhs) | EventExpression::Sub(lhs, rhs) => {
            // Contract order: fully evaluate lhs before rhs, without reassociation.
            let left = compile_expression(lhs, state_carriers, kappa)?;
            let right = compile_expression(rhs, state_carriers, kappa)?;
            let mut coefficients = vec![0.0; left.len().max(right.len())];
            let subtraction = matches!(expression, EventExpression::Sub(_, _));
            for (index, coefficient) in coefficients.iter_mut().enumerate() {
                let left_value = left.get(index).copied().unwrap_or(0.0);
                let right_value = right.get(index).copied().unwrap_or(0.0);
                *coefficient = if subtraction {
                    left_value - right_value
                } else {
                    left_value + right_value
                };
            }
            coefficients
        }
        EventExpression::Mul(lhs, rhs) => {
            let left = compile_expression(lhs, state_carriers, kappa)?;
            let right = compile_expression(rhs, state_carriers, kappa)?;
            let degree = left.len().saturating_sub(1) + right.len().saturating_sub(1);
            if degree > MAX_EVENT_DEGREE {
                return Err(EventFailure::UnsupportedExpression);
            }
            let mut coefficients = vec![0.0; degree + 1];
            for (left_degree, left_value) in left.iter().copied().enumerate() {
                for (right_degree, right_value) in right.iter().copied().enumerate() {
                    let product = left_value * right_value;
                    coefficients[left_degree + right_degree] =
                        coefficients[left_degree + right_degree] + product;
                }
            }
            coefficients
        }
        EventExpression::Neg(inner) => {
            let compiled = compile_expression(inner, state_carriers, kappa)?;
            compiled.into_iter().map(|value| -value).collect()
        }
    };
    ensure_finite_polynomial(result)
}

/// Compile a closed event AST after substituting ascending cubic carrier
/// coefficients for each state component. Returned coefficients are f64 bit
/// patterns in ascending order; exact dyadic conversion belongs to isolation.
pub(crate) fn compile_carrier_polynomial(
    expression: &EventExpression,
    state_carriers: &[[f64; 4]],
    kappa: f64,
) -> Result<Vec<u64>, EventFailure> {
    let coefficients = compile_expression(expression, state_carriers, kappa)?;
    if coefficients.len().saturating_sub(1) > MAX_EVENT_DEGREE {
        return Err(EventFailure::UnsupportedExpression);
    }
    Ok(coefficients
        .into_iter()
        .map(f64::to_bits)
        .collect::<Vec<_>>())
}

fn map_exact_error(error: ExactArithmeticError) -> EventFailure {
    match error {
        ExactArithmeticError::NonfiniteCoefficient => EventFailure::CarrierNonfinite,
        ExactArithmeticError::ZeroDivisor
        | ExactArithmeticError::InexactDivision
        | ExactArithmeticError::RootIsolationFailure
        | ExactArithmeticError::RootRepresentationFailure => {
            EventFailure::RootRepresentationFailure
        }
    }
}

fn intrinsic_direction(root: &RepresentedExactRoot) -> EventDirection {
    if root.theta_bits == 0.0f64.to_bits() {
        if root.right_sign < 0 {
            EventDirection::Decreasing
        } else if root.right_sign > 0 {
            EventDirection::Increasing
        } else {
            EventDirection::Any
        }
    } else if root.theta_bits == 1.0f64.to_bits() {
        if root.left_sign > 0 {
            EventDirection::Decreasing
        } else if root.left_sign < 0 {
            EventDirection::Increasing
        } else {
            EventDirection::Any
        }
    } else if root.left_sign > 0 && root.right_sign < 0 {
        EventDirection::Decreasing
    } else if root.left_sign < 0 && root.right_sign > 0 {
        EventDirection::Increasing
    } else {
        EventDirection::Any
    }
}

pub(crate) fn direction_is_eligible(intrinsic: EventDirection, requested: EventDirection) -> bool {
    requested == EventDirection::Any || intrinsic == requested
}

fn f64_polynomial_value(coefficient_bits: &[u64], theta: f64) -> Result<f64, EventFailure> {
    let mut value = 0.0;
    for bits in coefficient_bits.iter().rev() {
        let coefficient = f64::from_bits(*bits);
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

fn verify_represented_root(
    polynomial: &ExactPolynomial,
    coefficient_bits: &[u64],
    root: &RepresentedExactRoot,
) -> Result<(), EventFailure> {
    let epsilon_bits = stored_event_epsilon(coefficient_bits, EVENT_RTOL, EVENT_ATOL)?;
    let epsilon = f64::from_bits(epsilon_bits);
    let exact_epsilon = f64_bits_to_rational(epsilon_bits).map_err(map_exact_error)?;
    let exact_theta = f64_bits_to_rational(root.theta_bits).map_err(map_exact_error)?;
    if polynomial.evaluate(&exact_theta).abs() > exact_epsilon {
        return Err(EventFailure::RootRepresentationFailure);
    }
    let binary_residual = f64_polynomial_value(coefficient_bits, f64::from_bits(root.theta_bits))?;
    if binary_residual.abs() > epsilon {
        return Err(EventFailure::RootRepresentationFailure);
    }
    Ok(())
}

/// Isolate all roots of an ascending-coefficient f64 polynomial on [0,1].
/// Every coefficient bit pattern is treated as an exact dyadic. Theta always
/// increases in the actual integration direction, including a backward step.
pub(crate) fn isolate_exact_roots(
    coefficient_bits: &[u64],
    _direction: EventDirection,
    _backward: bool,
) -> Result<RootIsolation, EventFailure> {
    let polynomial = ExactPolynomial::from_f64_bits(coefficient_bits).map_err(map_exact_error)?;
    if polynomial
        .degree()
        .is_some_and(|degree| degree > MAX_EVENT_DEGREE)
    {
        return Err(EventFailure::UnsupportedExpression);
    }
    if polynomial.is_zero() {
        return Ok(RootIsolation::ContinuumZero);
    }
    let exact_roots = isolate_unit_roots(&polynomial).map_err(map_exact_error)?;
    let mut roots = Vec::new();
    for root in exact_roots {
        verify_represented_root(&polynomial, coefficient_bits, &root)?;
        roots.push(IsolatedRoot {
            theta_bits: root.theta_bits,
            multiplicity: root.multiplicity,
            direction: intrinsic_direction(&root),
        });
    }
    Ok(RootIsolation::Roots(roots))
}

pub(crate) fn certify_carrier_subsegment(
    input: CarrierCertificateInput<'_>,
) -> Result<(), EventFailure> {
    if !(input.tau0.is_finite() && input.tau1.is_finite()) {
        return Err(EventFailure::CarrierNonfinite);
    }
    if input.tau0 == input.tau1 {
        return Err(EventFailure::NonadvancingAcceptedStep);
    }
    if input.endpoint_states.len() != 2 || input.endpoint_rhs.len() != 2 {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    let dimension = input.endpoint_states[0].len();
    if dimension == 0
        || input.endpoint_states[1].len() != dimension
        || input.endpoint_rhs[0].len() != dimension
        || input.endpoint_rhs[1].len() != dimension
        || input.midpoint_state.len() != dimension
    {
        return Err(EventFailure::CarrierCertificateFailure);
    }
    let all_finite = input
        .endpoint_states
        .iter()
        .chain(input.endpoint_rhs.iter())
        .flat_map(|values| values.iter())
        .chain(input.midpoint_state.iter())
        .chain(input.midpoint_event_values.iter())
        .all(|value| value.is_finite());
    if !all_finite {
        return Err(EventFailure::CarrierNonfinite);
    }

    let step = input.tau1 - input.tau0;
    if !step.is_finite() {
        return Err(EventFailure::CarrierNonfinite);
    }
    let mut state_defect = 0.0f64;
    for index in 0..dimension {
        // Frozen Hermite term order at theta=1/2.
        let hermite_midpoint = 0.5 * input.endpoint_states[0][index]
            + 0.125 * step * input.endpoint_rhs[0][index]
            + 0.5 * input.endpoint_states[1][index]
            - 0.125 * step * input.endpoint_rhs[1][index];
        let scale = BACKGROUND_ATOL
            + BACKGROUND_RTOL
                * 1.0f64
                    .max(input.midpoint_state[index].abs())
                    .max(hermite_midpoint.abs());
        let defect = (input.midpoint_state[index] - hermite_midpoint).abs() / scale;
        if !defect.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
        state_defect = state_defect.max(defect);
    }
    let event_defect = input
        .midpoint_event_values
        .iter()
        .fold(0.0f64, |maximum, value| maximum.max(value.abs()));
    if state_defect <= CARRIER_DEFECT_BUDGET && event_defect <= CARRIER_DEFECT_BUDGET {
        return Ok(());
    }
    if input.depth >= CARRIER_MAX_DEPTH {
        Err(EventFailure::CarrierCertificateFailure)
    } else {
        // The owner must bisect; returning success would expose an uncertified
        // accepted step. The same typed failure is used if no owner is present.
        Err(EventFailure::CarrierCertificateFailure)
    }
}

pub(crate) fn domain_margin(
    raw: f64,
    state_infinity_norm: f64,
    rtol: f64,
    atol: f64,
) -> Result<DomainMargin, EventFailure> {
    if !(raw.is_finite() && state_infinity_norm.is_finite() && rtol.is_finite() && atol.is_finite())
        || state_infinity_norm < 0.0
        || rtol < 0.0
        || atol < 0.0
    {
        return Err(EventFailure::CarrierNonfinite);
    }
    let slack = atol + rtol * 1.0f64.max(state_infinity_norm);
    let certificate = raw + slack;
    if !(slack.is_finite() && certificate.is_finite()) {
        return Err(EventFailure::CarrierNonfinite);
    }
    Ok(DomainMargin { raw, certificate })
}

pub(crate) fn initial_domain_classification(
    raw: f64,
    epsilon_initial: f64,
) -> Result<InitialDomainClassification, EventFailure> {
    if !(raw.is_finite() && epsilon_initial.is_finite()) || epsilon_initial < 0.0 {
        return Err(EventFailure::CarrierNonfinite);
    }
    if raw < -epsilon_initial {
        Ok(InitialDomainClassification::Violation)
    } else if raw.abs() <= epsilon_initial {
        Ok(InitialDomainClassification::BoundaryNeighborhood)
    } else {
        Ok(InitialDomainClassification::Interior)
    }
}

pub(crate) fn stored_event_epsilon(
    coefficient_bits: &[u64],
    event_rtol: f64,
    event_atol: f64,
) -> Result<u64, EventFailure> {
    if !(event_rtol.is_finite() && event_atol.is_finite()) || event_rtol < 0.0 || event_atol < 0.0 {
        return Err(EventFailure::CarrierNonfinite);
    }
    let mut coefficient_sum = 0.0f64;
    for bits in coefficient_bits {
        let coefficient = f64::from_bits(*bits);
        if !coefficient.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
        coefficient_sum = coefficient_sum + coefficient.abs();
        if !coefficient_sum.is_finite() {
            return Err(EventFailure::CarrierNonfinite);
        }
    }
    let epsilon = event_atol + event_rtol * 1.0f64.max(coefficient_sum);
    if !epsilon.is_finite() {
        return Err(EventFailure::CarrierNonfinite);
    }
    Ok(epsilon.to_bits())
}

fn threshold_roots(
    polynomial: &ExactPolynomial,
    epsilon: &BigRational,
    positive_threshold: bool,
) -> Result<Vec<u64>, EventFailure> {
    // p-epsilon=0 isolates +epsilon; p+epsilon=0 isolates -epsilon.
    let threshold = ExactPolynomial::constant(epsilon.clone());
    let shifted = if positive_threshold {
        polynomial.sub(&threshold)
    } else {
        polynomial.add(&threshold)
    };
    isolate_unit_roots(&shifted)
        .map_err(map_exact_error)
        .map(|roots| roots.into_iter().map(|root| root.theta_bits).collect())
}

pub(crate) fn isolate_rearm_points(
    coefficient_bits: &[u64],
    stored_epsilon_bits: u64,
    direction: EventDirection,
    _backward: bool,
) -> Result<Vec<u64>, EventFailure> {
    let polynomial = ExactPolynomial::from_f64_bits(coefficient_bits).map_err(map_exact_error)?;
    if polynomial.is_zero() {
        return Ok(Vec::new());
    }
    if polynomial
        .degree()
        .is_some_and(|degree| degree > MAX_EVENT_DEGREE)
    {
        return Err(EventFailure::UnsupportedExpression);
    }
    let epsilon = f64_bits_to_rational(stored_epsilon_bits).map_err(map_exact_error)?;
    if epsilon.is_negative() || epsilon.is_zero() && f64::from_bits(stored_epsilon_bits) != 0.0 {
        return Err(EventFailure::CarrierNonfinite);
    }
    let mut roots = match direction {
        EventDirection::Decreasing => threshold_roots(&polynomial, &epsilon, true)?,
        EventDirection::Increasing => threshold_roots(&polynomial, &epsilon, false)?,
        EventDirection::Any => {
            let mut roots = threshold_roots(&polynomial, &epsilon, true)?;
            roots.extend(threshold_roots(&polynomial, &epsilon, false)?);
            roots
        }
    };
    roots.sort_unstable();
    roots.dedup();
    Ok(roots)
}
