//! Export native spin-harmonic shear generator and independent quadrature basis.
use bianchi_rustcore::{
    geom::lie::photon_potentials,
    kinetic::{
        lie_hierarchy::{lie_data, LieHierarchy},
        lie_history::RayNode,
        memory_mixture::stf_matrix,
        spin_sht::{modes, SpinSht, C64},
    },
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let l: usize = args[0].parse()?;
    let h = LieHierarchy::new(l, true, 4.)?;
    let m = modes(l);
    if args[1] == "gen" {
        println!("axis,row,col,re,im");
        for k in 0..5 {
            let s = stf_matrix(std::array::from_fn(|j| if j == k { 1. } else { 0. }));
            let p = photon_potentials(&lie_data(&RayNode {
                shear: std::array::from_fn(|i| std::array::from_fn(|j| s[(i, j)])),
                ..Default::default()
            }));
            for j in 0..3 * m {
                let mut y = h.zero_state();
                y[j / m][j % m] = C64::new(1., 0.);
                let mut o = h.zero_state();
                h.rhs(&p, &y, &mut o);
                for (i, v) in o.iter().flatten().enumerate() {
                    if v.norm() > 1e-15 {
                        println!("{k},{i},{j},{:.17e},{:.17e}", v.re, v.im);
                    }
                }
            }
        }
    } else {
        let t = SpinSht::new(l, 32, 64)?;
        println!("ray,mu,phi,w,mode,re,im");
        for j in 0..m {
            let mut a = vec![C64::new(0., 0.); m];
            a[j] = C64::new(1., 0.);
            let v = t.synthesize(2, &a);
            for (i, z) in v.iter().enumerate() {
                println!(
                    "{i},{:.17e},{:.17e},{:.17e},{j},{:.17e},{:.17e}",
                    t.grid.ct[i / 64],
                    t.grid.phi[i % 64],
                    t.grid.w[i],
                    z.re,
                    z.im
                );
            }
        }
    }
    Ok(())
}
