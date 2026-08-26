//! RF-02C Type-IX index-1 DAE primitives.

use crate::ode::charts::{self, Chart};

use super::history::FailureCode;

pub(crate) const TYPE_IX_DAE_MASS_DIAGONAL: [f64; 7] = [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0];

pub(crate) fn apply_mass(input: &[f64; 7]) -> [f64; 7] {
    [input[0], input[1], input[2], 0.0, input[4], input[5], 0.0]
}

pub(crate) fn regularity_gate(state: &[f64; 7], rtol: f64, atol: f64) -> Result<(), FailureCode> {
    if !rtol.is_finite()
        || !atol.is_finite()
        || rtol < 0.0
        || atol < 0.0
        || !state.iter().all(|value| value.is_finite())
    {
        return Err(FailureCode::InvalidInput);
    }
    let norm_inf = state.iter().map(|value| value.abs()).fold(0.0f64, f64::max);
    let threshold = atol + rtol * norm_inf.max(1.0);
    if !threshold.is_finite() {
        return Err(FailureCode::InvalidInput);
    }
    if (state[4] + state[5]).abs() <= threshold {
        return Err(FailureCode::TypeIxDaeSingularChart);
    }
    Ok(())
}

fn check_chart(chart: &Chart) -> Result<(), FailureCode> {
    if matches!(chart, Chart::TypeIXD { .. }) {
        Ok(())
    } else {
        Err(FailureCode::InvalidInput)
    }
}

pub(crate) fn dae_rhs(
    chart: &Chart,
    state: &[f64; 7],
    rtol: f64,
    atol: f64,
) -> Result<[f64; 7], FailureCode> {
    check_chart(chart)?;
    regularity_gate(state, rtol, atol)?;

    let mut out = [0.0; 7];
    charts::rhs(chart, state, &mut out);
    let mut constraints = [0.0; 2];
    charts::constraint_values(chart, state, &mut constraints)
        .map_err(|_| FailureCode::InvalidInput)?;
    out[3] = constraints[1];
    out[6] = constraints[0];
    Ok(out)
}

pub(crate) fn dae_jvp(
    chart: &Chart,
    state: &[f64; 7],
    direction: &[f64; 7],
    rtol: f64,
    atol: f64,
) -> Result<[f64; 7], FailureCode> {
    check_chart(chart)?;
    regularity_gate(state, rtol, atol)?;
    if !direction.iter().all(|value| value.is_finite()) {
        return Err(FailureCode::InvalidInput);
    }

    let mut out = [0.0; 7];
    charts::exact_jvp(chart, state, direction, &mut out).map_err(|_| FailureCode::InvalidInput)?;
    out[3] = direction[1] + direction[2] + direction[3];
    out[6] = 2.0 * state[0] * direction[0]
        + ((state[5] + state[6]) * direction[4]
            + (state[4] + state[6]) * direction[5]
            + (state[4] + state[5]) * direction[6])
            / 6.0;
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ode::charts;

    const RTOL: f64 = 1.0e-10;
    const ATOL: f64 = 1.0e-12;

    fn chart(future: bool) -> Chart {
        Chart::TypeIXD { gamma: 1.0, future }
    }

    // Catches a misplaced algebraic row or a nonzero mass entry for S3/N3.
    #[test]
    fn rf02c_type_ix_dae_mass_apply_has_frozen_diagonal() {
        let input = [1.0, -2.0, 3.0, -4.0, 5.0, -6.0, 7.0];
        assert_eq!(apply_mass(&input), [1.0, -2.0, 3.0, 0.0, 5.0, -6.0, 0.0]);
        assert_eq!(
            TYPE_IX_DAE_MASS_DIAGONAL,
            [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0]
        );
    }

    // Catches using all seven ODE rows instead of replacing rows 3 and 6 by constraints.
    #[test]
    fn rf02c_type_ix_dae_rhs_replaces_exact_algebraic_rows() {
        let chart = chart(false);
        let state = [0.25, 0.1, -0.2, 0.3, 1.0, 2.0, 0.5];
        let mut full = [0.0; 7];
        charts::rhs(&chart, &state, &mut full);

        let dae = dae_rhs(&chart, &state, RTOL, ATOL).unwrap();
        for row in [0, 1, 2, 4, 5] {
            assert_eq!(
                dae[row].to_bits(),
                full[row].to_bits(),
                "differential row {row}"
            );
        }
        assert_eq!(dae[3].to_bits(), (state[1] + state[2] + state[3]).to_bits());
        assert!((dae[6] - (-17.0f64 / 48.0)).abs() <= 64.0 * f64::EPSILON);
    }

    // Catches finite-differencing the algebraic rows or taking them from the full ODE JVP.
    #[test]
    fn rf02c_type_ix_dae_jvp_uses_analytic_constraint_rows() {
        let chart = chart(true);
        let state = [0.25, 0.1, -0.2, 0.3, 1.0, 2.0, 0.5];
        let direction = [0.05, -0.1, 0.2, -0.3, 0.4, -0.5, 0.6];
        let mut full = [0.0; 7];
        charts::exact_jvp(&chart, &state, &direction, &mut full).unwrap();

        let dae = dae_jvp(&chart, &state, &direction, RTOL, ATOL).unwrap();
        for row in [0, 1, 2, 4, 5] {
            assert_eq!(
                dae[row].to_bits(),
                full[row].to_bits(),
                "differential row {row}"
            );
        }
        assert!((dae[3] - (-0.2f64)).abs() <= 64.0 * f64::EPSILON);
        let expected_definition_jvp = 2.0 * state[0] * direction[0]
            + ((state[5] + state[6]) * direction[4]
                + (state[4] + state[6]) * direction[5]
                + (state[4] + state[5]) * direction[6])
                / 6.0;
        assert!((dae[6] - expected_definition_jvp).abs() <= 64.0 * f64::EPSILON);
    }

    // Catches a non-strict comparison or a gate scaled by anything except caller tolerances.
    #[test]
    fn rf02c_type_ix_dae_regularity_gate_is_strict_at_caller_scale() {
        let at_threshold = [0.0, 0.0, 0.0, 0.0, 0.75, -0.65, 0.0];
        assert_eq!(
            regularity_gate(&at_threshold, 0.1, 0.0),
            Err(FailureCode::TypeIxDaeSingularChart)
        );

        let above_threshold = [0.0, 0.0, 0.0, 0.0, 0.75, -0.649, 0.0];
        assert_eq!(regularity_gate(&above_threshold, 0.1, 0.0), Ok(()));
    }

    fn unit_interval(seed: &mut u64) -> f64 {
        *seed = seed
            .wrapping_mul(6_364_136_223_846_793_005)
            .wrapping_add(1_442_695_040_888_963_407);
        ((*seed >> 11) as f64) * (1.0 / ((1u64 << 53) as f64))
    }

    fn symmetric(seed: &mut u64, radius: f64) -> f64 {
        radius * (2.0 * unit_interval(seed) - 1.0)
    }

    // Catches a constraint derivative inconsistent with the tangent space even when rows map correctly.
    #[test]
    fn rf02c_type_ix_dae_tangent_equivalence_random_on_manifold() {
        let mut seed = 0x52f0_2cda_e202_6082u64;
        for case in 0..128 {
            let h = symmetric(&mut seed, 0.7);
            let n1 = 0.75 + 0.5 * unit_interval(&mut seed);
            let n2 = 0.75 + 0.5 * unit_interval(&mut seed);
            let n3 = (6.0 * (1.0 - h * h) - n1 * n2) / (n1 + n2);
            let s1 = symmetric(&mut seed, 0.25);
            let s2 = symmetric(&mut seed, 0.25);
            let state = [h, s1, s2, -s1 - s2, n1, n2, n3];

            let dh = symmetric(&mut seed, 0.1);
            let dn1 = symmetric(&mut seed, 0.1);
            let dn2 = symmetric(&mut seed, 0.1);
            let dn3 = (-12.0 * h * dh - (n2 + n3) * dn1 - (n1 + n3) * dn2) / (n1 + n2);
            let ds1 = symmetric(&mut seed, 0.1);
            let ds2 = symmetric(&mut seed, 0.1);
            let direction = [dh, ds1, ds2, -ds1 - ds2, dn1, dn2, dn3];
            let chart = chart(case % 2 != 0);

            let dae_rhs = dae_rhs(&chart, &state, RTOL, ATOL).unwrap();
            assert!(dae_rhs[3].abs() <= 64.0 * f64::EPSILON, "trace case {case}");
            assert!(
                dae_rhs[6].abs() <= 64.0 * f64::EPSILON,
                "definition case {case}"
            );

            let mut full_rhs = [0.0; 7];
            charts::rhs(&chart, &state, &mut full_rhs);
            assert!(
                (full_rhs[3] + full_rhs[1] + full_rhs[2]).abs() <= 64.0 * f64::EPSILON,
                "redundant S3 row case {case}: full={full_rhs:?}"
            );
            let restored_n3 = -(2.0 * state[0] * full_rhs[0]
                + ((state[5] + state[6]) * full_rhs[4] + (state[4] + state[6]) * full_rhs[5])
                    / 6.0)
                / ((state[4] + state[5]) / 6.0);
            assert!(
                (full_rhs[6] - restored_n3).abs() <= 64.0 * f64::EPSILON,
                "redundant N3 row case {case}: full={} restored={restored_n3}",
                full_rhs[6]
            );

            let mut full_jvp = [0.0; 7];
            charts::exact_jvp(&chart, &state, &direction, &mut full_jvp).unwrap();
            let expected_tangent = apply_mass(&full_jvp);
            let dae_jvp = dae_jvp(&chart, &state, &direction, RTOL, ATOL).unwrap();
            for row in 0..7 {
                assert!(
                    (dae_jvp[row] - expected_tangent[row]).abs() <= 64.0 * f64::EPSILON,
                    "case {case}, row {row}: dae={} expected={}",
                    dae_jvp[row],
                    expected_tangent[row]
                );
            }
        }
    }
}
