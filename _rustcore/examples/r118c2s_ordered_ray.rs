use bianchi_rustcore::kinetic::lie_history::{advance_ray, RayNode};
use nalgebra::{Matrix3, Vector3};
fn rows(m: Matrix3<f64>) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Matrix3<f64> = Matrix3::from_diagonal(&Vector3::new(1., -1., 0.));
    let b: Matrix3<f64> = Matrix3::new(0., 1., 0., 1., 0., 1., 0., 1., 0.);
    let n0 = Vector3::new(0.3, 0.4, 0.5).normalize();
    let f0 = Vector3::new(0., 0., 1.).cross(&n0).normalize();
    println!("eps,nstep,case,nx,ny,nz,fx,fy,fz,lnE,area,F00,F01,F02,F10,F11,F12,F20,F21,F22");
    for eps in [0.04, 0.02, 0.01, 0.005] {
        for steps in [64, 128, 256] {
            for (name, pulses) in [
                ("AB", vec![a, b]),
                ("BA", vec![b, a]),
                ("loop", vec![a, b, -a, -b]),
                ("reverse", vec![b, a, -b, -a]),
            ] {
                let mut coframe = Matrix3::identity();
                let mut n = n0;
                let mut f = f0;
                let mut le = 0.;
                let mut area = 0.;
                let h = 1. / steps as f64;
                let mut u = 0.;
                for s in pulses {
                    let s = eps * s;
                    let e = (s * h).exp();
                    for _ in 0..steps {
                        let l = RayNode {
                            eta: u,
                            shear: rows(s),
                            ..Default::default()
                        };
                        let r = RayNode {
                            eta: u + h,
                            ..l.clone()
                        };
                        let ray = advance_ray(&l, &r, n.into())?;
                        n = Vector3::from(ray.e);
                        f = Matrix3::from_fn(|i, j| ray.rotation[i][j]) * f;
                        le += ray.log_energy;
                        area += ray.log_area;
                        coframe = e * coframe;
                        u += h;
                    }
                }
                print!("{eps},{steps},{name}");
                for x in n.iter().chain(f.iter()) {
                    print!(",{x:.17e}");
                }
                print!(",{le:.17e},{area:.17e}");
                for i in 0..3 {
                    for j in 0..3 {
                        print!(",{:.17e}", coframe[(i, j)]);
                    }
                }
                println!();
            }
        }
    }
    Ok(())
}
