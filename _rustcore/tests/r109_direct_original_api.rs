use rec_microphysics::thomson_history::{integrate, RaySample};
use rei_microphysics::thomson::{thomson_history, DensityConstraint, MaterialKnot};

#[test]
fn native_rei_material_to_native_rec_ray_slab() {
    let normal_t_s = [0.0, 1.5e15, 4.0e15];
    let beta = [0.3, -0.1, 0.2];
    let direction = [0.6, 0.0, 0.8];
    let knots = normal_t_s.map(|t| MaterialKnot {
        normal_t_s: t,
        a: 1.0,
        b: 0.0,
        n_reference_m3: 2e3,
        electrons_per_reference: 0.85,
        beta,
    });
    let rei = thomson_history(&knots, DensityConstraint::FixedNormalInventory, direction).unwrap();
    let native: Vec<_> = rei
        .iter()
        .map(|s| {
            RaySample::new(
                s.material.normal_t_s,
                s.n_reference_rest_m3,
                s.material.electrons_per_reference,
                s.material.beta,
                s.direction,
            )
            .unwrap()
        })
        .collect();
    let bins = integrate(&native).unwrap();
    let oracle = rec_microphysics::thomson_history::C_SIGMA_T_M3_S
        * 2e3
        * 0.85
        * (1.0 - 0.3 * 0.6 - 0.2 * 0.8)
        * 4e15;
    assert!((bins[0].tau_far / oracle - 1.0).abs() < 2e-15);
    assert!((rei[0].tau_to_receiver / oracle - 1.0).abs() < 2e-15);
    assert!((bins[0].visibility_mass / rei[0].next_cell_mass - 1.0).abs() < 2e-15);
    println!(
        "tau_REC {:.17e} tau_REI {:.17e} tau_invariant {:.17e}",
        bins[0].tau_far, rei[0].tau_to_receiver, oracle
    );
}
