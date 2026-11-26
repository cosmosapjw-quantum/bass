//! Causal quadratic B3 map for a general real STF wedge.
use super::{
    b3_coupling::b3_source,
    memory_mixture::stf_matrix,
    spin_sht::{SpinSht, C64},
};
use crate::geom::lie::quadratic_coefficients;
use nalgebra::Vector3;
pub const PAIRS: [(usize, usize); 10] = [
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (1, 2),
    (1, 3),
    (1, 4),
    (2, 3),
    (2, 4),
    (3, 4),
];
/// Magnetic spin-harmonic vector normalized by the initial I monopole.
pub fn harmonics(w: &[f64; 10], carrier: f64) -> Result<[C64; 7], String> {
    if w.iter().any(|x| !x.is_finite()) || !carrier.is_finite() {
        return Err("wedge domain".into());
    }
    let sht = SpinSht::new(4, 10, 20)?;
    let mut s = [[C64::new(0., 0.); 5]; 5];
    let mut e = s;
    for j in 0..5 {
        let t = stf_matrix(std::array::from_fn(|k| if j == k { 1. } else { 0. }));
        let sc =
            quadratic_coefficients(&std::array::from_fn(|i| std::array::from_fn(|k| t[(i, k)])));
        s[j] = std::array::from_fn(|k| sc[k + 4]);
        let mut q = vec![];
        let mut u = vec![];
        for v in sht.grid.ehat.chunks_exact(3) {
            let n = Vector3::from_column_slice(v);
            let h = n.x.hypot(n.y);
            let p = Vector3::new(-n.y / h, n.x / h, 0.);
            let z = p.cross(&n);
            q.push(2. / 3. * (z.dot(&(t * z)) - p.dot(&(t * p))));
            u.push(4. / 3. * z.dot(&(t * p)));
        }
        let c = sht.from_stokes(&vec![0.; sht.len()], &q, &u);
        e[j] = std::array::from_fn(|k| -(c[1][k + 4] + c[2][k + 4]) * 0.5);
    }
    let mut out = [C64::new(0., 0.); 7];
    for (&x, &(i, j)) in w.iter().zip(PAIRS.iter()) {
        let v = b3_source(&s[i], &e[j], carrier);
        for k in 0..7 {
            out[k] += v[k] * x / (4. * std::f64::consts::PI).sqrt();
        }
    }
    Ok(out)
}
