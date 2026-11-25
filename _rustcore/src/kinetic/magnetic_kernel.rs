//! Cartesian counterpart of the direct B3 quadrupole source.
use nalgebra::{Matrix3, Vector3};
pub type Rank3 = [[[f64; 3]; 3]; 3];
pub fn magnetic_rank3(s: Matrix3<f64>, e: Matrix3<f64>) -> Rank3 {
    let raw = |i: usize, j: usize, k: usize| {
        let a = (i + 1) % 3;
        let b = (i + 2) % 3;
        s[(j, a)] * e[(k, b)] - s[(j, b)] * e[(k, a)]
    };
    let t: Rank3 = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            std::array::from_fn(|k| {
                (raw(i, j, k)
                    + raw(i, k, j)
                    + raw(j, i, k)
                    + raw(j, k, i)
                    + raw(k, i, j)
                    + raw(k, j, i))
                    / 6.
            })
        })
    });
    let v = Vector3::from_fn(|i, _| (0..3).map(|j| t[i][j][j]).sum::<f64>());
    std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            std::array::from_fn(|k| {
                t[i][j][k]
                    - ((if i == j { v[k] } else { 0. })
                        + (if i == k { v[j] } else { 0. })
                        + (if j == k { v[i] } else { 0. }))
                        / 5.
            })
        })
    })
}
pub fn norm2(m: &Rank3) -> f64 {
    m.iter().flatten().flatten().map(|x| x * x).sum()
}
