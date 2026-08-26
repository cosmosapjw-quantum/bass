use super::events::{
    builtin_registry, certify_carrier_subsegment, compile_carrier_polynomial, domain_margin,
    initial_domain_classification, isolate_exact_roots, isolate_rearm_points, stored_event_epsilon,
    CarrierCertificateInput, DomainMargin, EventDirection, EventExpression, EventFailure,
    InitialDomainClassification, RootIsolation, CLOSED_AST_OPS, REGISTRY_SHA256,
};

fn coefficient_bits(coefficients: &[f64]) -> Vec<u64> {
    coefficients.iter().map(|value| value.to_bits()).collect()
}

fn root_summary(result: RootIsolation) -> Vec<(u64, usize, EventDirection)> {
    match result {
        RootIsolation::Roots(roots) => roots
            .into_iter()
            .map(|root| (root.theta_bits, root.multiplicity, root.direction))
            .collect(),
        RootIsolation::ContinuumZero => panic!("expected isolated roots"),
    }
}

#[test]
fn rf02c_closed_callback_free_builtin_event_registry() {
    assert_eq!(
        CLOSED_AST_OPS,
        [
            "state",
            "parameter",
            "const_f64_bits",
            "add",
            "sub",
            "mul",
            "neg"
        ]
    );
    assert_eq!(REGISTRY_SHA256.len(), 64);
    assert_eq!(builtin_registry("class_a").unwrap().len(), 1);
    assert_eq!(builtin_registry("class_b").unwrap().len(), 4);
    assert_eq!(builtin_registry("exceptional").unwrap().len(), 1);
    assert_eq!(builtin_registry("type_ix_d").unwrap().len(), 6);
    let future = builtin_registry("type_ix_d_future").unwrap();
    assert_eq!(future.len(), 7);
    assert_eq!(future.last().unwrap().id, "type_ix_recollapse");
    assert_eq!(
        future
            .iter()
            .map(|event| event.declaration_order)
            .collect::<Vec<_>>(),
        (0..future.len()).collect::<Vec<_>>()
    );
    assert!(future.last().unwrap().one_shot_after_transition);
    assert!(future[..future.len() - 1]
        .iter()
        .all(|event| !event.one_shot_after_transition));
    assert_eq!(
        builtin_registry("caller_defined"),
        Err(EventFailure::UnsupportedExpression)
    );
}

#[test]
fn rf02c_ast_compiles_to_degree_at_most_six_in_frozen_order() {
    let theta = [[0.0, 1.0, 0.0, 0.0]];
    let square = EventExpression::Mul(
        Box::new(EventExpression::State(0)),
        Box::new(EventExpression::State(0)),
    );
    let compiled = compile_carrier_polynomial(&square, &theta, 0.0).unwrap();
    assert_eq!(compiled, coefficient_bits(&[0.0, 0.0, 1.0]));

    let unsupported_state = EventExpression::State(1);
    assert_eq!(
        compile_carrier_polynomial(&unsupported_state, &theta, 0.0),
        Err(EventFailure::UnsupportedExpression)
    );
}

#[test]
fn rf02c_exact_isolation_enumerates_two_crossings() {
    // (theta-1/4)(theta-3/4) = theta^2-theta+3/16.
    let result = isolate_exact_roots(
        &coefficient_bits(&[3.0 / 16.0, -1.0, 1.0]),
        EventDirection::Any,
        false,
    )
    .unwrap();
    assert_eq!(
        root_summary(result),
        vec![
            (0.25f64.to_bits(), 1, EventDirection::Decreasing),
            (0.75f64.to_bits(), 1, EventDirection::Increasing),
        ]
    );
}

#[test]
fn rf02c_exact_isolation_keeps_tangential_double_root() {
    // (theta-1/2)^2.
    let result = isolate_exact_roots(
        &coefficient_bits(&[0.25, -1.0, 1.0]),
        EventDirection::Any,
        false,
    )
    .unwrap();
    assert_eq!(
        root_summary(result),
        vec![(0.5f64.to_bits(), 2, EventDirection::Any)]
    );
    // Isolation is detector evidence and therefore retains the tangency even
    // when a later direction filter will make it ineligible.
    assert_eq!(
        root_summary(
            isolate_exact_roots(
                &coefficient_bits(&[0.25, -1.0, 1.0]),
                EventDirection::Decreasing,
                false,
            )
            .unwrap()
        ),
        vec![(0.5f64.to_bits(), 2, EventDirection::Any)]
    );
}

#[test]
fn rf02c_exact_isolation_preserves_mixed_multiplicity() {
    // (theta-1/4)^2(theta-3/4)^3, ascending coefficients.
    let result = isolate_exact_roots(
        &coefficient_bits(&[
            -27.0 / 1024.0,
            81.0 / 256.0,
            -45.0 / 32.0,
            23.0 / 8.0,
            -11.0 / 4.0,
            1.0,
        ]),
        EventDirection::Any,
        false,
    )
    .unwrap();
    assert_eq!(
        root_summary(result),
        vec![
            (0.25f64.to_bits(), 2, EventDirection::Any),
            (0.75f64.to_bits(), 3, EventDirection::Increasing),
        ]
    );
}

#[test]
fn rf02c_exact_isolation_owns_initial_and_final_endpoint_roots() {
    // theta(theta-1)^2.
    let result = isolate_exact_roots(
        &coefficient_bits(&[0.0, 1.0, -2.0, 1.0]),
        EventDirection::Any,
        false,
    )
    .unwrap();
    assert_eq!(
        root_summary(result),
        vec![
            (0.0f64.to_bits(), 1, EventDirection::Increasing),
            (1.0f64.to_bits(), 2, EventDirection::Decreasing),
        ]
    );
}

#[test]
fn rf02c_identically_zero_polynomial_is_continuum_zero() {
    assert_eq!(
        isolate_exact_roots(&coefficient_bits(&[0.0, 0.0]), EventDirection::Any, false,).unwrap(),
        RootIsolation::ContinuumZero
    );
}

#[test]
fn rf02c_backward_integration_maps_theta_to_actual_tau_order() {
    let result = isolate_exact_roots(
        &coefficient_bits(&[3.0 / 16.0, -1.0, 1.0]),
        EventDirection::Any,
        true,
    )
    .unwrap();
    let roots = root_summary(result);
    assert_eq!(
        roots,
        vec![
            (0.25f64.to_bits(), 1, EventDirection::Decreasing),
            (0.75f64.to_bits(), 1, EventDirection::Increasing),
        ]
    );
    let actual_taus: Vec<u64> = roots
        .iter()
        .map(|(theta_bits, _, _)| (1.0 - f64::from_bits(*theta_bits)).to_bits())
        .collect();
    assert_eq!(actual_taus, vec![0.75f64.to_bits(), 0.25f64.to_bits()]);
}

#[test]
fn rf02c_carrier_rejects_nonadvancing_accepted_step() {
    let y0 = [0.0];
    let y1 = [0.0];
    let f0 = [0.0];
    let f1 = [0.0];
    let endpoint_states: &[&[f64]] = &[&y0, &y1];
    let endpoint_rhs: &[&[f64]] = &[&f0, &f1];
    let input = CarrierCertificateInput {
        tau0: 1.0,
        tau1: 1.0,
        endpoint_states,
        endpoint_rhs,
        midpoint_state: &y0,
        midpoint_event_values: &y0,
        depth: 0,
    };
    assert_eq!(
        certify_carrier_subsegment(input),
        Err(EventFailure::NonadvancingAcceptedStep)
    );
}

#[test]
fn rf02c_carrier_nonfinite_and_depth_exhaustion_are_typed() {
    let finite = [0.0];
    let nonfinite = [f64::NAN];
    let endpoint_states: &[&[f64]] = &[&finite, &finite];
    let endpoint_rhs: &[&[f64]] = &[&finite, &finite];
    let nonfinite_input = CarrierCertificateInput {
        tau0: 0.0,
        tau1: 1.0,
        endpoint_states,
        endpoint_rhs,
        midpoint_state: &nonfinite,
        midpoint_event_values: &finite,
        depth: 0,
    };
    assert_eq!(
        certify_carrier_subsegment(nonfinite_input),
        Err(EventFailure::CarrierNonfinite)
    );
    let exhausted_input = CarrierCertificateInput {
        tau0: 0.0,
        tau1: 1.0,
        endpoint_states,
        endpoint_rhs,
        midpoint_state: &finite,
        midpoint_event_values: &[1.0],
        depth: 24,
    };
    assert_eq!(
        certify_carrier_subsegment(exhausted_input),
        Err(EventFailure::CarrierCertificateFailure)
    );
}

#[test]
fn rf02c_raw_event_surface_is_distinct_from_certificate_margin() {
    let first = domain_margin(0.0, 2.0, 1e-8, 1e-10).unwrap();
    let second = domain_margin(0.0, 2.0, 1e-10, 1e-12).unwrap();
    assert_eq!(first.raw.to_bits(), second.raw.to_bits());
    assert_eq!(first.raw.to_bits(), 0.0f64.to_bits());
    assert_ne!(first.certificate.to_bits(), second.certificate.to_bits());
    assert_eq!(
        first,
        DomainMargin {
            raw: 0.0,
            certificate: 1e-10 + 1e-8 * 2.0,
        }
    );
}

#[test]
fn rf02c_initial_domain_uses_frozen_boundary_neighborhood() {
    assert_eq!(
        initial_domain_classification(-2e-10, 1e-10).unwrap(),
        InitialDomainClassification::Violation
    );
    assert_eq!(
        initial_domain_classification(-1e-10, 1e-10).unwrap(),
        InitialDomainClassification::BoundaryNeighborhood
    );
    assert_eq!(
        initial_domain_classification(2e-10, 1e-10).unwrap(),
        InitialDomainClassification::Interior
    );
}

#[test]
fn rf02c_epsilon_is_stored_once_and_direction_rearm_is_exact() {
    // p(theta) = -theta(theta-1/3)(theta-2/3).
    let coefficients = coefficient_bits(&[0.0, -2.0 / 9.0, 1.0, -1.0]);
    let epsilon_bits = stored_event_epsilon(&coefficients, 0.0, 1.0 / 1000.0).unwrap();
    assert_eq!(epsilon_bits, (1.0f64 / 1000.0).to_bits());
    let rearm = isolate_rearm_points(
        &coefficients,
        epsilon_bits,
        EventDirection::Decreasing,
        false,
    )
    .unwrap();
    assert!(!rearm.is_empty());
    assert!(rearm.windows(2).all(|pair| pair[0] < pair[1]));
}

#[test]
fn rf02c_leave_zero_band_can_rearm_and_refire_within_one_step() {
    let coefficients = coefficient_bits(&[0.0, -2.0 / 9.0, 1.0, -1.0]);
    let epsilon_bits = (1.0f64 / 1000.0).to_bits();
    let rearm =
        isolate_rearm_points(&coefficients, epsilon_bits, EventDirection::Any, false).unwrap();
    let roots = isolate_exact_roots(&coefficients, EventDirection::Any, false).unwrap();
    assert!(rearm.len() >= 2);
    assert_eq!(root_summary(roots).len(), 3);
    assert!(rearm[0] < (1.0f64 / 3.0).to_bits());
}
