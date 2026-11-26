use bianchi_rustcore::kinetic::quadratic_wedge::{harmonics, PAIRS};
#[test]
fn spin3_wedge_map_and_reversal() {
    let mut w = [0.; 10];
    w[0] = 1.;
    let b = harmonics(&w, 4.).unwrap();
    let norm = b.iter().map(|x| x.norm_sqr()).sum::<f64>();
    assert!((norm - 128. / 189.).abs() < 1e-13);
    let c = harmonics(&w.map(|x| -x), 4.).unwrap();
    assert!(b.iter().zip(c).all(|(x, y)| (*x + y).norm() < 1e-15));
    assert_eq!(PAIRS[0], (0, 1));
    // Kernel of spin-3 projection: e02 + .5 e34.
    let mut w = [0.; 10];
    w[1] = 1.;
    w[9] = 0.5;
    assert!(harmonics(&w, 4.).unwrap().iter().all(|x| x.norm() < 1e-14));
}
