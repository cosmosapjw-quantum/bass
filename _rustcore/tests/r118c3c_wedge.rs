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

#[test]
fn full_wedge_projector() {
    let v: Vec<_> = (0..10)
        .map(|i| harmonics(&std::array::from_fn(|j| if i == j { 1. } else { 0. }), 4.).unwrap())
        .collect();
    let scale = 256. / 189.;
    let g: [[f64; 10]; 10] = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            v[i].iter()
                .zip(v[j])
                .map(|(a, b)| (a.conj() * b).re)
                .sum::<f64>()
                / scale
        })
    });
    let tr = (0..10).map(|i| g[i][i]).sum::<f64>();
    assert!((tr - 3.5).abs() < 1e-13);
    for i in 0..10 {
        for j in 0..10 {
            let z = (0..10).map(|k| g[i][k] * g[k][j]).sum::<f64>();
            assert!((2. * z - g[i][j]).abs() < 1e-13);
        }
    }
}
