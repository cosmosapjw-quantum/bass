//! RF-04 internal contract and hostile-mutation tests.

use super::rf04_typeii::{
    parse_carrier, parse_quadrature_route, rf04_deterministic_batch_probe,
    scalar_contract_diagnostics, Carrier, QuadratureRoute, CERTIFICATE_SCOPE,
};

fn grid() -> ([[f64; 3]; 6], [f64; 6]) {
    (
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ],
        [4.0 * std::f64::consts::PI / 6.0; 6],
    )
}

#[test]
fn rf04_rate_dual_and_projector_contracts_hold() {
    let (directions, weights) = grid();
    let diagnostics = scalar_contract_diagnostics(&directions, &weights, 0.1, 1).unwrap();
    assert!(diagnostics.right_kernel_residual < 2e-13);
    assert!(diagnostics.left_invariant_residual < 3e-13);
    assert!(diagnostics.projector_idempotence_residual < 3e-13);
    assert!(diagnostics.connection_commutator_residual < 3e-13);
}

#[test]
fn rf04_route_capabilities_are_distinct_and_fail_closed() {
    assert_eq!(parse_carrier("scalar_intensity_v1").unwrap(), Carrier::ScalarIntensity);
    assert_eq!(parse_carrier("polarized_rank9_v1").unwrap(), Carrier::PolarizedRank9);
    assert!(parse_carrier("stokes4_silent_projection").is_err());
    assert_eq!(
        parse_quadrature_route("fixed_grid_raw_v1").unwrap(),
        QuadratureRoute::FixedGridRaw
    );
    assert_eq!(
        parse_quadrature_route("fixed_grid_ap_corrected_v1").unwrap(),
        QuadratureRoute::FixedGridApCorrected
    );
    assert_ne!(
        parse_quadrature_route("paired_rest_to_normal_reference_v1").unwrap(),
        parse_quadrature_route("fixed_grid_ap_corrected_v1").unwrap()
    );
    assert!(parse_quadrature_route("fixed_grid_claimed_ap_without_correction").is_err());
}

#[test]
fn rf04_nonnormal_certificate_never_claims_global_forward_error() {
    assert_eq!(CERTIFICATE_SCOPE, "PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR");
    assert!(!CERTIFICATE_SCOPE.starts_with("GLOBAL_FORWARD_ERROR"));
}

#[test]
fn rf04_scalar_and_independent_parallel_batches_are_bit_identical() {
    let serial = rf04_deterministic_batch_probe(1).unwrap();
    let parallel = rf04_deterministic_batch_probe(4).unwrap();
    assert_eq!(serial, parallel);
}
