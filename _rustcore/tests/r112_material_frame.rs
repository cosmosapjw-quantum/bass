use bianchi_rustcore::homogeneous_sky::{
    initial_sky,
    rec_bridge::{material_directional_sky, material_expansion_factor},
};
use bianchi_rustcore::kinetic::lie_history::{advance_ray, RayNode};
#[test]
fn finite_tilt_rate_matches_independent_ray_difference() {
    let n = RayNode {
        shear: [[0.1, 0.02, 0.], [0.02, -0.04, 0.], [0., 0., -0.06]],
        n: [[0., 0., 0.], [0., 0.3, 0.], [0., 0., -0.2]],
        a: [0.1, 0., 0.],
        rotation: [0.02, 0.01, -0.03],
        ..Default::default()
    };
    let e = [0.6, 0., 0.8];
    let b = [0.13, 0.07, -0.03];
    let db = [-0.04, 0.02, 0.01];
    let dot = |a: [f64; 3], b: [f64; 3]| a.iter().zip(b).map(|(x, y)| x * y).sum::<f64>();
    let d = |b: [f64; 3], e: [f64; 3]| (1. - dot(b, e)) / (1. - dot(b, b)).sqrt();
    let h = 1e-5;
    let log_e = |h: f64| {
        let end = RayNode {
            eta: h,
            ..n.clone()
        };
        let r = advance_ray(&n, &end, e).unwrap();
        let bt = std::array::from_fn(|i| b[i] + h * db[i]);
        r.log_energy + d(bt, r.e).ln()
    };
    let expected = -(log_e(h) - log_e(-h)) / (2. * h * d(b, e));
    let f = material_expansion_factor(&n, e, b, db).unwrap();
    assert!((f - expected).abs() < 2e-9, "{f} {expected}");
    let f0 = material_expansion_factor(&n, e, [0.; 3], [0.; 3]).unwrap();
    assert!((f0 - (1. + 0.1 * 0.36 - 0.06 * 0.64)).abs() < 1e-14);
}
#[test]
fn rest_quadrature_temperature_and_contracting_direction() {
    let rays = initial_sky(18, 36).unwrap();
    let rest =
        material_directional_sky(&rays, &RayNode::default(), [0.; 3], [0.; 3], 3000.).unwrap();
    assert!(rest.temperature_k.iter().all(|x| (x - 3000.).abs() < 1e-10));
    assert!(rest
        .expansion_factor
        .iter()
        .all(|x| (*x - 1.).abs() < 1e-14));
    let boost = material_directional_sky(&rays, &RayNode::default(), [0.2, 0., 0.], [0.; 3], 3000.)
        .unwrap();
    assert!((boost.weights.iter().sum::<f64>() - 4. * std::f64::consts::PI).abs() < 1e-11);
    assert!(
        material_directional_sky(&rays, &RayNode::default(), [0.; 3], [2., 0., 0.], 3000.).is_err()
    );
}

#[test]
fn calls_pinned_rec_from_native_sky() {
    use rec_microphysics::hydrogen_peebles::RetainedState;
    let rays = initial_sky(8, 16).unwrap();
    let sky =
        material_directional_sky(&rays, &RayNode::default(), [0.; 3], [0.; 3], 3000.).unwrap();
    let state = RetainedState { xp: 0.5, x2: 0.01 };
    let a = sky.rec_source(1e8, 1e-13, state, 3000.).unwrap();
    let b = sky.rec_source(1e8, 1e-13, state, 2000.).unwrap();
    assert!(b.alpha_b_m3_s > a.alpha_b_m3_s);
    assert_eq!(a.beta_p_s, b.beta_p_s);
    assert_eq!(a.r_alpha_s, b.r_alpha_s);
}
