//! Source-exact RF-03 force and analytic fixed-context state JVP.

use super::eos::GammaLawModel;
use super::state::{cross, dot, mat_vec, MatterContext, MatterDirection, MatterError, MatterState};

const SOURCE_GUARD_EPS: f64 = 1.0e-12;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MatterForce {
    pub omega: f64,
    pub v: [f64; 3],
}

impl MatterForce {
    #[inline]
    pub fn as_array(self) -> [f64; 4] {
        [self.omega, self.v[0], self.v[1], self.v[2]]
    }
}

#[inline]
fn source_safe(value: f64) -> (f64, bool) {
    if value.abs() < SOURCE_GUARD_EPS {
        (
            if value >= 0.0 {
                SOURCE_GUARD_EPS
            } else {
                -SOURCE_GUARD_EPS
            },
            true,
        )
    } else {
        (value, false)
    }
}

#[derive(Clone, Copy)]
struct Scalars {
    v2: f64,
    adv: f64,
    gp: f64,
    gp_clamped: bool,
    gm: f64,
    gm_clamped: bool,
    b: f64,
    k: f64,
    u: f64,
    t: f64,
}

fn scalars(model: GammaLawModel, state: MatterState, context: MatterContext) -> Scalars {
    let gamma = model.gamma();
    let v2 = dot(state.v, state.v);
    let adv = dot(context.a, state.v);
    let sigma_v = mat_vec(context.sigma, state.v);
    let sv2 = dot(state.v, sigma_v);
    let (gp, gp_clamped) = source_safe(1.0 + (gamma - 1.0) * v2);
    let (gm, gm_clamped) = source_safe(1.0 - (gamma - 1.0) * v2);
    let c = 2.0 * context.q * (gamma - 1.0) - (2.0 - gamma);
    let b = 2.0 * context.q - (3.0 * gamma - 2.0) + 2.0 * gamma * adv + c * v2 - gamma * sv2;
    let k = (3.0 * gamma - 4.0) - 2.0 * (gamma - 1.0) * adv;
    let u = k * (1.0 - v2) + (2.0 - gamma) * sv2;
    let t = u / gm;
    Scalars {
        v2,
        adv,
        gp,
        gp_clamped,
        gm,
        gm_clamped,
        b,
        k,
        u,
        t,
    }
}

pub fn force(
    model: GammaLawModel,
    state: MatterState,
    context: MatterContext,
) -> Result<MatterForce, MatterError> {
    state.validate()?;
    let values = scalars(model, state, context);
    let sigma_v = mat_vec(context.sigma, state.v);
    let rotation = cross(context.r, state.v);
    let n_v = mat_vec(context.n, state.v);
    let connection = cross(state.v, n_v);
    let p = [
        context.a[0] * values.v2 - values.adv * state.v[0] + connection[0],
        context.a[1] * values.v2 - values.adv * state.v[1] + connection[1],
        context.a[2] * values.v2 - values.adv * state.v[2] + connection[2],
    ];
    let result = MatterForce {
        omega: state.omega * values.b / values.gp,
        v: [
            values.t * state.v[0] - sigma_v[0] + rotation[0] - p[0],
            values.t * state.v[1] - sigma_v[1] + rotation[1] - p[1],
            values.t * state.v[2] - sigma_v[2] + rotation[2] - p[2],
        ],
    };
    if !result.omega.is_finite() || result.v.iter().any(|value| !value.is_finite()) {
        return Err(MatterError::Domain(
            "force became nonfinite inside the certified domain".to_string(),
        ));
    }
    Ok(result)
}

pub fn force_jvp(
    model: GammaLawModel,
    state: MatterState,
    direction: MatterDirection,
    context: MatterContext,
) -> Result<(MatterForce, MatterForce), MatterError> {
    let primal = force(model, state, context)?;
    let values = scalars(model, state, context);
    let gamma = model.gamma();
    let sigma_v = mat_vec(context.sigma, state.v);
    let sigma_w = mat_vec(context.sigma, direction.v);
    let ds = 2.0 * dot(state.v, direction.v);
    let da = dot(context.a, direction.v);
    let dsv2 = dot(direction.v, sigma_v) + dot(state.v, sigma_w);
    let c = 2.0 * context.q * (gamma - 1.0) - (2.0 - gamma);
    let db = 2.0 * gamma * da + c * ds - gamma * dsv2;
    let dgp = if values.gp_clamped {
        0.0
    } else {
        (gamma - 1.0) * ds
    };
    let domega = direction.omega * values.b / values.gp
        + state.omega * (db / values.gp - values.b * dgp / (values.gp * values.gp));

    let dk = -2.0 * (gamma - 1.0) * da;
    let du = dk * (1.0 - values.v2) - values.k * ds + (2.0 - gamma) * dsv2;
    let dgm = if values.gm_clamped {
        0.0
    } else {
        -(gamma - 1.0) * ds
    };
    let dt = du / values.gm - values.u * dgm / (values.gm * values.gm);

    let n_v = mat_vec(context.n, state.v);
    let n_w = mat_vec(context.n, direction.v);
    let dconnection_left = cross(direction.v, n_v);
    let dconnection_right = cross(state.v, n_w);
    let dp = [
        context.a[0] * ds - da * state.v[0] - values.adv * direction.v[0]
            + dconnection_left[0]
            + dconnection_right[0],
        context.a[1] * ds - da * state.v[1] - values.adv * direction.v[1]
            + dconnection_left[1]
            + dconnection_right[1],
        context.a[2] * ds - da * state.v[2] - values.adv * direction.v[2]
            + dconnection_left[2]
            + dconnection_right[2],
    ];
    let rotation_w = cross(context.r, direction.v);
    let tangent = MatterForce {
        omega: domega,
        v: [
            dt * state.v[0] + values.t * direction.v[0] - sigma_w[0] + rotation_w[0] - dp[0],
            dt * state.v[1] + values.t * direction.v[1] - sigma_w[1] + rotation_w[1] - dp[1],
            dt * state.v[2] + values.t * direction.v[2] - sigma_w[2] + rotation_w[2] - dp[2],
        ],
    };
    if !tangent.omega.is_finite() || tangent.v.iter().any(|value| !value.is_finite()) {
        return Err(MatterError::Domain(
            "analytic JVP became nonfinite inside the certified domain".to_string(),
        ));
    }
    Ok((primal, tangent))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::matter::EXPLICIT_GAMMA_LAW_MODEL_ID;

    fn fixture() -> (GammaLawModel, MatterState, MatterContext) {
        let model = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 1.31).unwrap();
        let state = MatterState::new(0.37, [0.13, -0.08, 0.04]).unwrap();
        let context = MatterContext::new(
            [
                [0.07, -0.02, 0.01],
                [0.04, -0.04, 0.03],
                [0.01, -0.05, -0.03],
            ],
            [[0.2, 0.03, -0.01], [-0.02, -0.1, 0.04], [0.06, 0.01, 0.05]],
            [0.04, -0.03, 0.02],
            [-0.02, 0.01, 0.03],
            0.41,
        )
        .unwrap();
        (model, state, context)
    }

    #[test]
    fn rf03_zero_tilt_limit_has_no_velocity_force() {
        let model = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 4.0 / 3.0).unwrap();
        let state = MatterState::new(0.25, [0.0; 3]).unwrap();
        let context =
            MatterContext::new([[0.0; 3]; 3], [[0.0; 3]; 3], [0.0; 3], [0.0; 3], 0.37).unwrap();
        let observed = force(model, state, context).unwrap();
        assert_eq!(observed.v, [0.0; 3]);
        let expected = state.omega * (2.0 * context.q - (3.0 * model.gamma() - 2.0));
        assert!((observed.omega - expected).abs() <= 2.0e-16);
    }

    #[test]
    fn rf03_analytic_jvp_matches_diagnostic_central_difference() {
        let (model, state, context) = fixture();
        let direction = MatterDirection::new(0.07, [0.03, -0.02, 0.04]).unwrap();
        let (_, analytic) = force_jvp(model, state, direction, context).unwrap();
        let h = 1.0e-6;
        let plus = MatterState::new(
            state.omega + h * direction.omega,
            [
                state.v[0] + h * direction.v[0],
                state.v[1] + h * direction.v[1],
                state.v[2] + h * direction.v[2],
            ],
        )
        .unwrap();
        let minus = MatterState::new(
            state.omega - h * direction.omega,
            [
                state.v[0] - h * direction.v[0],
                state.v[1] - h * direction.v[1],
                state.v[2] - h * direction.v[2],
            ],
        )
        .unwrap();
        let fp = force(model, plus, context).unwrap().as_array();
        let fm = force(model, minus, context).unwrap().as_array();
        let expected = std::array::from_fn::<_, 4, _>(|index| (fp[index] - fm[index]) / (2.0 * h));
        for (observed, expected) in analytic.as_array().into_iter().zip(expected) {
            assert!((observed - expected).abs() <= 3.0e-10);
        }
    }

    #[test]
    fn rf03_source_denominator_guard_is_finite_and_explicit() {
        let model = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 1.0e-14).unwrap();
        let state = MatterState::new(0.2, [1.0 - 5.0e-14, 0.0, 0.0]).unwrap();
        let context =
            MatterContext::new([[0.0; 3]; 3], [[0.0; 3]; 3], [0.0; 3], [0.0; 3], 0.1).unwrap();
        let observed = force(model, state, context).unwrap();
        assert!(observed.as_array().into_iter().all(f64::is_finite));
    }
}
