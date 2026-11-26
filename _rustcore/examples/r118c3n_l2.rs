//! Check exact l2 transport coefficients in native LieHierarchy convention.
use bianchi_rustcore::{
    geom::lie::photon_potentials,
    kinetic::{
        lie_hierarchy::{lie_data, LieHierarchy},
        lie_history::RayNode,
        spin_sht::{index, C64},
    },
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let h = LieHierarchy::new(6, true, 4.)?;
    let s = 1. / 6_f64.sqrt();
    let pot = photon_potentials(&lie_data(&RayNode {
        shear: [[-s, 0., 0.], [0., -s, 0.], [0., 0., 2. * s]],
        ..Default::default()
    }));
    let k = index(2, 0);
    let mut y = h.zero_state();
    let mut o = h.zero_state();
    y[0][k] = C64::new(1., 0.);
    h.rhs(&pot, &y, &mut o);
    let i = o[0][k].re / s;
    y = h.zero_state();
    y[1][k] = C64::new(1., 0.);
    y[2][k] = C64::new(1., 0.);
    h.rhs(&pot, &y, &mut o);
    let p = (o[1][k] + o[2][k]).re / (2. * s);
    assert!(
        (i + 10. / 7.).abs() < 1e-13 && (p - 10. / 7.).abs() < 1e-13,
        "{i} {p}"
    );
    println!("I2={i:.17e} P2={p:.17e}");
    Ok(())
}
