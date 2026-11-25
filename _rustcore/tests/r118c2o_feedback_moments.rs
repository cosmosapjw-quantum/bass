use bianchi_rustcore::{
    homogeneous_sky::{field::HarmonicSky, moments},
    kinetic::{lie_history::RayNode, radiation_feedback::advance_mixture, spin_sht::SpinSht},
};
fn pressure(a: f64, b: f64) -> [[f64; 3]; 3] {
    let sht = SpinSht::new(4, 12, 24).unwrap();
    let mu: Vec<f64> = sht.grid.ehat.chunks_exact(3).map(|v| v[2]).collect();
    let iv: Vec<f64> = mu.iter().map(|m| 1. + a * (3. * m * m - 1.) / 2.).collect();
    let qv: Vec<f64> = mu.iter().map(|m| b * (1. - m * m)).collect();
    let mut h = HarmonicSky::isotropic(4, 12, 24, true).unwrap();
    h.coefficients = sht.from_stokes(&iv, &qv, &vec![0.; mu.len()]).into();
    let r = moments(&h.photons().unwrap()).unwrap();
    assert!(r.flux.iter().all(|x| x.abs() < 1e-13));
    assert!((r.pressure[2][2] - 1. / 3. - 2. * a / 15.).abs() < 2e-13);
    r.pressure
}
#[test]
fn native_mixture_shear_source_has_positive_quadrupole_coefficient() {
    let mut worst: f64 = 0.;
    for (og, on, om) in [
        (0.003, 0.002, 0.994),
        (0.001, 0.0007, 0.95),
        (0.2, 0.1, 0.6),
    ] {
        let omega = og + on + om;
        let ol = 1. - omega;
        for (a, b, n) in [(0.02, 0.03, -0.04), (-0.02, 0.01, -0.04), (0., 0.05, 0.03)] {
            let pg = pressure(a, b);
            let pn = pressure(n, 0.);
            let p = std::array::from_fn(|i| {
                std::array::from_fn(|j| (og * pg[i][j] + on * pn[i][j]) / omega)
            });
            for s in [-1e-5, 0., 1e-5] {
                let mut at = RayNode::default();
                at.omega_lambda = ol;
                at.shear = [[-s / 2., 0., 0.], [0., -s / 2., 0.], [0., 0., s]];
                let dt = 1e-3;
                let r = advance_mixture(&at, &at, dt, omega, p, [0.; 3]).unwrap();
                // Native geometry retains the exact O(S^2) deceleration term;
                // subtract its O(S^3) contribution before testing the linear source.
                let d = -(3. * om + 4. * (og + on)) / 2.;
                let want = -(3. + d) * s + 0.4 * (og * a + on * n) + 0.5 * s * s * s;
                let got = (r.shear[2][2] - s) / dt;
                worst = worst.max((got - want).abs());
                assert!((got - want).abs() < 2e-13);
            }
        }
    }
    eprintln!("27 native mixture feedback cases, max derivative residual {worst:e}");
}
