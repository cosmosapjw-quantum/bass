//! Direct B3 source from a shear quadrupole and an electric quadrupole.
//! Goldberg convention, a^+-2=-(E+-iB); u=ln(a/a_i).
use super::spin_sht::C64;
pub fn b3_source(s: &[C64; 5], e: &[C64; 5], carrier: f64) -> [C64; 7] {
    // G^+_{3m,2M,2m'} in m=-3..3, M=-2..2, m'=m-M.
    // Exact table from independent 3j evaluation, not native Wigner routine.
    let a = 5. / (4. * (7. * std::f64::consts::PI).sqrt());
    let b = (15. / (7. * std::f64::consts::PI)).sqrt() / 4.;
    let c = (5. / (14. * std::f64::consts::PI)).sqrt() / 2.;
    let d = (5. / (7. * std::f64::consts::PI)).sqrt() / 4.;
    let g = [
        [-a, a, 0., 0., 0.],
        [-a, 0., a, 0., 0.],
        [-b, -c, c, b, 0.],
        [-d, -2. * d, 0., 2. * d, d],
        [0., -b, -c, c, b],
        [0., 0., -a, 0., a],
        [0., 0., 0., -a, a],
    ];
    std::array::from_fn(|m| {
        let mut v = C64::new(0., 0.);
        for j in 0..5 {
            let n = m as isize - 3 - (j as isize - 2) + 2;
            if (0..5).contains(&n) {
                v += s[j] * e[n as usize] * g[m][j];
            }
        }
        C64::new(0., carrier) * v
    })
}
