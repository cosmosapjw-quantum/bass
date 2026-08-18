//! AUTO-GENERATED low-rank moving-equilibrium action.
//! Formula authority SHA-256: 3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361

#[derive(Clone, Debug)]
pub struct ProjectorFactors {
    pub r: Vec<f64>,
    pub a: Vec<f64>,
    pub rv: Vec<f64>,
    pub av: Vec<f64>,
    pub denominator: f64,
    pub denominator_v: f64,
}

fn validate(directions: &[[f64; 3]], weights: &[f64], y: &[f64], axis: usize) {
    assert_eq!(directions.len(), weights.len());
    assert_eq!(directions.len(), y.len());
    assert!(axis < 3);
}

pub fn projector_factors(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    axis: usize,
) -> ProjectorFactors {
    assert_eq!(directions.len(), weights.len());
    assert!(axis < 3);
    assert!(v.abs() < 1.0);
    let gamma = 1.0 / (1.0 - v * v).sqrt();
    let mut r = Vec::with_capacity(directions.len());
    let mut a = Vec::with_capacity(directions.len());
    let mut rv = Vec::with_capacity(directions.len());
    let mut av = Vec::with_capacity(directions.len());
    for (e, &w) in directions.iter().zip(weights) {
        let mu = e[axis];
        let q = 1.0 - v * mu;
        let d = gamma * q;
        let ri = d.powi(-4);
        let ai = w * q / (4.0 * std::f64::consts::PI);
        let rvi = 4.0 * ri * (mu / q - gamma * gamma * v);
        let avi = -w * mu / (4.0 * std::f64::consts::PI);
        r.push(ri);
        a.push(ai);
        rv.push(rvi);
        av.push(avi);
    }
    let denominator: f64 = a.iter().zip(&r).map(|(x, y)| x * y).sum();
    let denominator_v: f64 = av.iter().zip(&r).map(|(x, y)| x * y).sum::<f64>()
        + a.iter().zip(&rv).map(|(x, y)| x * y).sum::<f64>();
    ProjectorFactors {
        r,
        a,
        rv,
        av,
        denominator,
        denominator_v,
    }
}

pub fn projector_apply(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    axis: usize,
    y: &[f64],
) -> Vec<f64> {
    validate(directions, weights, y, axis);
    let f = projector_factors(directions, weights, v, axis);
    let s: f64 = f.a.iter().zip(y).map(|(x, z)| x * z).sum();
    f.r.iter().map(|ri| ri * s / f.denominator).collect()
}

pub fn projector_dv_apply(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    axis: usize,
    y: &[f64],
) -> Vec<f64> {
    validate(directions, weights, y, axis);
    let f = projector_factors(directions, weights, v, axis);
    let s: f64 = f.a.iter().zip(y).map(|(x, z)| x * z).sum();
    let sv: f64 = f.av.iter().zip(y).map(|(x, z)| x * z).sum();
    f.r.iter()
        .zip(&f.rv)
        .map(|(ri, rvi)| {
            rvi * s / f.denominator + ri * sv / f.denominator
                - ri * s * f.denominator_v / (f.denominator * f.denominator)
        })
        .collect()
}

pub fn kato_apply(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    vdot: f64,
    axis: usize,
    y: &[f64],
) -> Vec<f64> {
    // K y = [Pdot,P]y = vdot * (Pv(P y) - P(Pv y)).
    let py = projector_apply(directions, weights, v, axis, y);
    let pv_py = projector_dv_apply(directions, weights, v, axis, &py);
    let pv_y = projector_dv_apply(directions, weights, v, axis, y);
    let p_pv_y = projector_apply(directions, weights, v, axis, &pv_y);
    pv_py
        .iter()
        .zip(p_pv_y)
        .map(|(x, z)| vdot * (x - z))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    fn grid() -> ([[f64; 3]; 6], [f64; 6]) {
        (
            [
                [1., 0., 0.],
                [-1., 0., 0.],
                [0., 1., 0.],
                [0., -1., 0.],
                [0., 0., 1.],
                [0., 0., -1.],
            ],
            [4.0 * std::f64::consts::PI / 6.0; 6],
        )
    }
    fn max_abs(v: &[f64]) -> f64 {
        v.iter().map(|x| x.abs()).fold(0.0, f64::max)
    }

    #[test]
    fn projector_is_idempotent() {
        let (e, w) = grid();
        let y = [0.2, -0.1, 0.4, 0.7, -0.3, 0.9];
        let p = projector_apply(&e, &w, 0.05, 1, &y);
        let pp = projector_apply(&e, &w, 0.05, 1, &p);
        let d: Vec<_> = pp.iter().zip(p).map(|(x, z)| x - z).collect();
        assert!(max_abs(&d) < 2e-14);
    }

    #[test]
    fn kato_commutator_identity_holds_as_action() {
        let (e, w) = grid();
        let y = [0.2, -0.1, 0.4, 0.7, -0.3, 0.9];
        let v = 0.05;
        let vd = 0.03;
        let py = projector_apply(&e, &w, v, 1, &y);
        let kpy = kato_apply(&e, &w, v, vd, 1, &py);
        let ky = kato_apply(&e, &w, v, vd, 1, &y);
        let pky = projector_apply(&e, &w, v, 1, &ky);
        let pd: Vec<_> = projector_dv_apply(&e, &w, v, 1, &y)
            .into_iter()
            .map(|x| vd * x)
            .collect();
        let diff: Vec<_> = kpy
            .iter()
            .zip(pky)
            .zip(pd)
            .map(|((a, b), c)| a - b - c)
            .collect();
        assert!(max_abs(&diff) < 3e-13);
    }
}
