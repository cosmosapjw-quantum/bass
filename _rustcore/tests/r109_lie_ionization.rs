use bianchi_rustcore::homogeneous_sky::{
    ionization::Ionization,
    material::Material,
    solve::{solve_with_inputs, Settings},
};
use bianchi_rustcore::kinetic::lie_history::{initial_lie_node, required_flux, LieInitial};
use std::path::Path;

fn options() -> Settings<'static> {
    Settings {
        family: "FLRW",
        shear: 0.,
        duration: 0.1,
        steps: 8,
        nmu: 8,
        nphi: 16,
        active: true,
        recoil: false,
        dust_fraction: 0.2,
        dust_beta: [0.; 3],
    }
}

#[test]
fn custom_lie_slice_satisfies_signed_codazzi_with_the_solved_coflow() {
    let ic = LieInitial {
        shear: [
            [0.12, 0.08, -0.03],
            [0.08, -0.07, 0.06],
            [-0.03, 0.06, -0.05],
        ],
        n: [[0., 0., 0.], [0., 0.3, 0.07], [0., 0.07, -0.2]],
        a: [0.15, 0., 0.],
    };
    let mut cfg = options();
    let mat = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let output = solve_with_inputs(&cfg, &mat, Some(&ic), None).unwrap();
    assert_eq!(output.initial_dust_mode, "codazzi_coflow");
    let req = required_flux(&initial_lie_node(&ic).unwrap());
    for (i, target) in req.iter().enumerate() {
        assert!(output.history[0].node.codazzi_residual[i].abs() < 1e-14);
        assert!((output.history[0].host_beta[i] - target / cfg.dust_fraction).abs() < 1e-14);
    }
    cfg.dust_fraction = 0.001;
    assert!(solve_with_inputs(&cfg, &mat, Some(&ic), None).is_err());
}

#[test]
fn dynamic_opacity_uses_the_evolving_rest_density_and_hubble_endpoint_each_half() {
    let mut cfg = options();
    cfg.recoil = true;
    let src = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/r109_constant_xe.tsv");
    let sigma_c = 299_792_458.0 * 6.652_458_705_1e-29;
    let ion = Ionization::load(&src, 0.2 / sigma_c, 1.).unwrap();
    let m = Material::constant(cfg.duration, 0., [0.; 3]).unwrap();
    let sol = solve_with_inputs(&cfg, &m, None, Some(&ion)).unwrap();
    let mut expected = 0.;
    for pair in sol.history.windows(2) {
        let (a, b) = (&pair[0].node, &pair[1].node);
        let rate = |eta: f64, h: f64| 0.2 * (-3. * eta).exp() / h;
        expected +=
            (b.eta - a.eta) * (rate(a.eta, a.hubble_ratio) + rate(b.eta, b.hubble_ratio)) / 2.;
        assert!((pair[1].proper_depth - expected).abs() < 3e-14);
    }
    assert!((expected - 0.2 * cfg.duration).abs() > 5e-4);
    cfg.recoil = false;
    assert!(solve_with_inputs(&cfg, &m, None, Some(&ion)).is_err());
}
