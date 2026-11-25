use bianchi_rustcore::{
    geom::lie::quadratic_coefficients,
    homogeneous_sky::{field::HarmonicSky, scatter_with, CollisionScheme},
    kinetic::{
        b3_coupling::b3_source,
        lie_history::RayNode,
        memory_mixture::stf_matrix,
        spin_sht::{index, SpinSht, C64},
    },
};
use nalgebra::Vector3;
use std::fs;
const H0: f64 = 2.1842852410855023e-18;
const CS: f64 = 299792458. * 6.6524587051e-29;
fn interp(x: &[Vec<f64>], u: f64, k: usize) -> f64 {
    let i = x.partition_point(|r| r[0] <= u);
    if i == 0 {
        return x[0][k];
    }
    if i >= x.len() {
        return x[x.len() - 1][k];
    }
    let a = &x[i - 1];
    let b = &x[i];
    a[k] + (b[k] - a[k]) * (u - a[0]) / (b[0] - a[0])
}
fn data(p: &str) -> Result<Vec<Vec<f64>>, Box<dyn std::error::Error>> {
    Ok(fs::read_to_string(p)?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    let geom = data(&a[0])?;
    let ne = data(&a[1])?;
    let label = &a[2];
    let sht = SpinSht::new(4, 10, 20)?;
    let zero = vec![0.; sht.len()];
    let mut emap = [[C64::new(0., 0.); 5]; 5];
    for j in 0..5 {
        let b = stf_matrix(std::array::from_fn(|k| if k == j { 1. } else { 0. }));
        let mut q = vec![];
        let mut u = vec![];
        for v in sht.grid.ehat.chunks_exact(3) {
            let n = Vector3::from_column_slice(v);
            let h = n.x.hypot(n.y);
            let p = Vector3::new(-n.y / h, n.x / h, 0.);
            let t = p.cross(&n);
            q.push(2. / 3. * (t.dot(&(b * t)) - p.dot(&(b * p))));
            u.push(4. / 3. * t.dot(&(b * p)));
        }
        let c = sht.from_stokes(&zero, &q, &u);
        for m in 0..5 {
            emap[j][m] = -(c[1][4 + m] + c[2][4 + m]) * 0.5;
        }
    }
    println!("history,scale,n,analytic_B3,native_B3,relative_vector_error,analytic_E2,native_E2,forbidden");
    let end = geom.last().unwrap()[0];
    for scale in [1., 0.5, 0.25, 0.125] {
        for n in [512, 1024] {
            let step = end / n as f64;
            let mut y = [0.; 24];
            let mut sky = HarmonicSky::isotropic(6, 12, 24, true)?;
            let rhs = |u: f64, v: [f64; 24]| -> [f64; 24] {
                let s = std::array::from_fn(|k| scale * interp(&geom, u, 3 + k));
                let k = CS * interp(&ne, u, 1) / (H0 * interp(&geom, u, 2));
                let mut d = [0.; 24];
                for j in 0..5 {
                    d[j] = -4. * s[j] - k * (0.9 * v[j] + 0.4 * v[j + 5]);
                    d[j + 5] = -k * (0.15 * v[j] + 0.4 * v[j + 5]);
                }
                let sm = stf_matrix(s);
                let sq = quadratic_coefficients(&std::array::from_fn(|i| {
                    std::array::from_fn(|j| sm[(i, j)])
                }));
                let e = std::array::from_fn(|m| (0..5).map(|i| emap[i][m] * v[i + 5]).sum());
                let bs = b3_source(&std::array::from_fn(|m| sq[m + 4]), &e, 4.);
                for m in 0..7 {
                    d[10 + 2 * m] = bs[m].re - k * v[10 + 2 * m];
                    d[11 + 2 * m] = bs[m].im - k * v[11 + 2 * m];
                }
                d
            };
            for i in 0..n {
                let u = i as f64 * step;
                let k1 = rhs(u, y);
                let k2 = rhs(
                    u + step / 2.,
                    std::array::from_fn(|j| y[j] + step * k1[j] / 2.),
                );
                let k3 = rhs(
                    u + step / 2.,
                    std::array::from_fn(|j| y[j] + step * k2[j] / 2.),
                );
                let k4 = rhs(u + step, std::array::from_fn(|j| y[j] + step * k3[j]));
                y = std::array::from_fn(|j| {
                    y[j] + step * (k1[j] + 2. * k2[j] + 2. * k3[j] + k4[j]) / 6.
                });
                let node = |u: f64| {
                    let s = stf_matrix(std::array::from_fn(|j| scale * interp(&geom, u, 3 + j)));
                    RayNode {
                        eta: u,
                        shear: std::array::from_fn(|i| std::array::from_fn(|j| s[(i, j)])),
                        ..Default::default()
                    }
                };
                let x = node(u);
                let m = node(u + step / 2.);
                let z = node(u + step);
                sky.stream(&x, &m)?;
                let mut ph = sky.photons()?;
                let before = ph.clone();
                scatter_with(
                    &mut ph,
                    CS * interp(&ne, u + step / 2., 1) / (H0 * interp(&geom, u + step / 2., 2))
                        * step,
                    [0.; 3],
                    CollisionScheme::Sdirk2,
                )?;
                sky.absorb_delta(&before, &ph)?;
                sky.stream(&m, &z)?;
            }
            let norm = sky.moments()?.energy / (4. * std::f64::consts::PI);
            let b: [C64; 7] = std::array::from_fn(|m| {
                C64::new(0., 0.5) * (sky.coefficients[1][9 + m] - sky.coefficients[2][9 + m]) / norm
            });
            let want: [C64; 7] = std::array::from_fn(|m| C64::new(y[10 + 2 * m], y[11 + 2 * m]));
            let mag = |x: &[C64]| x.iter().map(|v| v.norm_sqr()).sum::<f64>().sqrt();
            let error = mag(&std::array::from_fn::<_, 7, _>(|m| b[m] - want[m])) / mag(&want);
            let e: [C64; 5] = std::array::from_fn(|m| (0..5).map(|i| emap[i][m] * y[i + 5]).sum());
            let ee: [C64; 5] = std::array::from_fn(|m| {
                -(sky.coefficients[1][4 + m] + sky.coefficients[2][4 + m]) * 0.5 / norm
            });
            let mut forbidden = 0_f64;
            for l in 2..=6 {
                for m in -(l as i64)..=l as i64 {
                    let i = index(l, m);
                    let ap = sky.coefficients[1][i];
                    let am = sky.coefficients[2][i];
                    forbidden = forbidden.max(
                        if l % 2 == 0 {
                            (ap - am).norm()
                        } else {
                            (ap + am).norm()
                        } / (2. * norm),
                    );
                }
            }
            println!(
                "{label},{scale},{n},{:.17e},{:.17e},{error:.17e},{:.17e},{:.17e},{forbidden:.17e}",
                mag(&want),
                mag(&b),
                mag(&e),
                mag(&ee)
            );
        }
    }
    Ok(())
}
