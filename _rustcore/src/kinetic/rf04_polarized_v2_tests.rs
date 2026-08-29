use super::rf04_polarized_v2::{
    validate_fixed_eulerian_history_shape, validate_remap_plan_v1, RemapPlanV1, SCHEMA_ID,
};
use super::rf04_typeii::{require_supported, Carrier, QuadratureRoute};

const GRID_SHA256: &str = "1111111111111111111111111111111111111111111111111111111111111111";
const PLAN_SHA256: &str = "2222222222222222222222222222222222222222222222222222222222222222";

fn directions() -> Vec<[f64; 3]> {
    vec![[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
}

fn valid_plan() -> RemapPlanV1 {
    RemapPlanV1 {
        schema_id: SCHEMA_ID.to_string(),
        target_offsets: vec![0, 1, 2, 3],
        source_indices: vec![0, 1, 2],
        weights: vec![1.0, 1.0, 1.0],
        direction_grid_sha256: GRID_SHA256.to_string(),
        builder_id: "rf04-red-identity-plan".to_string(),
        builder_version: "1".to_string(),
        plan_sha256: PLAN_SHA256.to_string(),
        minimum_transport_dot: f64::from_bits(1.0_f64.to_bits() - 1),
    }
}

fn assert_plan_error(plan: &RemapPlanV1, expected_code: &str) {
    let error = validate_remap_plan_v1(plan, &directions(), GRID_SHA256)
        .expect_err("mutated remap plan must fail closed");
    assert_eq!(error.code(), expected_code);
}

#[test]
fn rf04_polarized_v2_valid_content_addressed_plan_is_admitted() {
    let result = validate_remap_plan_v1(&valid_plan(), &directions(), GRID_SHA256);
    assert!(result.is_ok(), "valid v2 plan was rejected: {result:?}");
}

#[test]
fn rf04_polarized_v2_empty_row_is_rejected() {
    let mut plan = valid_plan();
    plan.target_offsets = vec![0, 1, 1, 2];
    plan.source_indices = vec![0, 2];
    plan.weights = vec![1.0, 1.0];
    assert_plan_error(&plan, "RF04_EMPTY_REMAP_ROW");
}

#[test]
fn rf04_polarized_v2_negative_and_nonfinite_weights_are_rejected() {
    for (mutant, code) in [
        (-0.25, "RF04_NEGATIVE_REMAP_WEIGHT"),
        (f64::NAN, "RF04_NONFINITE_REMAP_WEIGHT"),
    ] {
        let mut plan = valid_plan();
        plan.weights[0] = mutant;
        assert_plan_error(&plan, code);
    }
}

#[test]
fn rf04_polarized_v2_partition_mutation_is_rejected() {
    let mut plan = valid_plan();
    plan.weights[0] = 0.75;
    assert_plan_error(&plan, "RF04_REMAP_PARTITION_MISMATCH");
}

#[test]
fn rf04_polarized_v2_stale_grid_and_plan_hashes_are_rejected() {
    let mut stale_grid = valid_plan();
    stale_grid.direction_grid_sha256 = "3".repeat(64);
    assert_plan_error(&stale_grid, "RF04_DIRECTION_GRID_IDENTITY_MISMATCH");

    let mut stale_plan = valid_plan();
    stale_plan.plan_sha256 = "4".repeat(64);
    assert_plan_error(&stale_plan, "RF04_REMAP_PLAN_IDENTITY_MISMATCH");
}

#[test]
fn rf04_polarized_v2_free_support_constants_are_rejected() {
    for free_constant in [0.75, 0.80] {
        let mut plan = valid_plan();
        plan.minimum_transport_dot = free_constant;
        assert_plan_error(&plan, "RF04_REMAP_SUPPORT_BOUND_MISMATCH");
    }
}

#[test]
fn rf04_polarized_v2_fixed_eulerian_history_shape_is_admitted() {
    let history = vec![vec![0.0; 27], vec![0.0; 27], vec![0.0; 27]];
    let result = validate_fixed_eulerian_history_shape(&history, 2, 3);
    assert!(
        result.is_ok(),
        "valid fixed-grid history was rejected: {result:?}"
    );
}

#[test]
fn rf04_polarized_v2_history_grid_mutation_is_rejected() {
    let history = vec![vec![0.0; 27], vec![0.0; 18], vec![0.0; 27]];
    let error = validate_fixed_eulerian_history_shape(&history, 2, 3)
        .expect_err("history row on a different grid must fail closed");
    assert_eq!(error.code(), "RF04_HISTORY_GRID_MISMATCH");
}

#[test]
fn rf04_polarized_v2_v1_polarized_dispatch_remains_fail_closed() {
    let error = require_supported(Carrier::PolarizedRank9, QuadratureRoute::FixedGridRaw)
        .expect_err("polarized-on-v1 must remain unsupported");
    assert_eq!(error.code(), "RF04_UNSUPPORTED_CAPABILITY");
}
