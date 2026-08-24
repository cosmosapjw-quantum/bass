//! AUTO-GENERATED matrix-free scalar finite-tilt Thomson generator action.
//! Formula authority SHA-256: 3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361

fn aberrate(e: [f64; 3], v: f64, axis: usize) -> ([f64; 3], f64) {
    assert!(axis < 3);
    assert!(v.abs() < 1.0);
    if v.abs() < 1e-15 {
        return (e, 1.0);
    }
    let gamma = 1.0 / (1.0 - v * v).sqrt();
    let mu = e[axis];
    let ve = v * mu;
    let d = gamma * (1.0 - ve);
    let coeff = (gamma - 1.0) * ve / (v * v) - gamma;
    let mut ep = e;
    ep[axis] += coeff * v;
    for x in &mut ep {
        *x /= d;
    }
    (ep, d)
}

pub fn collision_generator_apply(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    axis: usize,
    y: &[f64],
) -> Vec<f64> {
    // Moment-factorized rest-frame Thomson gain: I0 + e^a e^b M_ab.
    assert_eq!(directions.len(), weights.len());
    assert_eq!(directions.len(), y.len());
    let n = directions.len();
    let mut ep = Vec::with_capacity(n);
    let mut d = Vec::with_capacity(n);
    let mut gp = Vec::with_capacity(n);
    let mut wr = Vec::with_capacity(n);
    for i in 0..n {
        let (ei, di) = aberrate(directions[i], v, axis);
        ep.push(ei);
        d.push(di);
        gp.push(di.powi(4) * y[i]);
        wr.push(weights[i] / di.powi(2));
    }
    let mut i0 = 0.0;
    let mut moment = [[0.0_f64; 3]; 3];
    for i in 0..n {
        let wg = wr[i] * gp[i];
        i0 += wg;
        for a in 0..3 {
            for b in 0..3 {
                moment[a][b] += wg * ep[i][a] * ep[i][b];
            }
        }
    }
    let gamma = 1.0 / (1.0 - v * v).sqrt();
    let pref = 3.0 / (16.0 * std::f64::consts::PI);
    let mut out = vec![0.0; n];
    for i in 0..n {
        let mut quad = 0.0;
        for a in 0..3 {
            for b in 0..3 {
                quad += ep[i][a] * moment[a][b] * ep[i][b];
            }
        }
        let gain = pref * (i0 + quad);
        let qout = 1.0 - v * directions[i][axis];
        out[i] = qout * d[i].powi(-4) * (gain - gp[i]);
        debug_assert!((d[i] - gamma * qout).abs() < 1e-12);
    }
    out
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
    #[test]
    fn finite_tilt_action_matches_independent_dense_python_receipt() {
        let (e, w) = grid();
        let y = [1.0, 0.7, 1.2, 0.9, 0.6, 1.4];
        let got = collision_generator_apply(&e, &w, 0.1, 1, &y);
        let expected = [
            -0.077556362500000239,
            0.22097348749999984,
            0.25408950617283943,
            -0.25930785123966976,
            0.3561345749999999,
            -0.4399450250000001,
        ];
        let err = got
            .iter()
            .zip(expected)
            .map(|(a, b)| (a - b).abs())
            .fold(0.0, f64::max);
        assert!(err < 3e-13, "err={err} got={got:?}");
    }
    #[test]
    fn rest_isotropic_state_is_null() {
        let (e, w) = grid();
        let y = [1.0; 6];
        let got = collision_generator_apply(&e, &w, 0.0, 1, &y);
        assert!(got.iter().map(|x| x.abs()).fold(0.0, f64::max) < 3e-15);
    }
}
