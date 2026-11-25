use bianchi_rustcore::kinetic::{
    lie_history::{advance_ray, RayNode},
    memory_mixture::stf_matrix,
    sphere::SphereGrid,
};
use nalgebra::{Matrix3, Vector3};
use std::fs;
fn rows(m: Matrix3<f64>) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let data = fs::read_to_string(&p[0])?;
    let hist = data
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    let grid = SphereGrid::new(4, 8);
    let mut out=String::from("case,id,u,n0x,n0y,n0z,c000,c001,c002,c010,c011,c012,c020,c021,c022,c100,c101,c102,c110,c111,c112,c120,c121,c122\n");
    println!("case,id,u,energy_scale,nx,ny,nz,jacobian");
    let c0 = Matrix3::identity() * hist[0][1];
    for (i, n0) in grid.ehat.chunks_exact(3).enumerate() {
        let mut n = Vector3::from_column_slice(n0);
        let (mut le, mut la) = (0., 0.);
        for k in 1..hist.len() {
            let make = |x: &[f64]| RayNode {
                eta: x[0],
                shear: rows(stf_matrix(std::array::from_fn(|k| x[3 + k]))),
                ..Default::default()
            };
            let x = make(&hist[k - 1]);
            let y = make(&hist[k]);
            let r = advance_ray(&x, &y, n.into())?;
            n = Vector3::from(r.e);
            le += r.log_energy;
            la += r.log_area;
            if k == hist.len() - 1 || k == hist.len() / 2 {
                let u = hist[k][0];
                let c1 = Matrix3::from_fn(|i, j| hist[k][8 + 3 * i + j]) * hist[k][1];
                out.push_str(&format!("{},{i},{u:.17e}", p[1]));
                for x in n0 {
                    out.push_str(&format!(",{x:.17e}"))
                }
                for c in [c0, c1] {
                    for i in 0..3 {
                        for j in 0..3 {
                            out.push_str(&format!(",{:.17e}", c[(i, j)]));
                        }
                    }
                }
                out.push('\n');
                println!(
                    "{},{i},{u:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                    p[1],
                    le.exp(),
                    n[0],
                    n[1],
                    n[2],
                    la.exp()
                );
            }
        }
    }
    fs::write(&p[2], out)?;
    Ok(())
}
