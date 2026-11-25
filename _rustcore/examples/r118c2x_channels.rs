use bianchi_rustcore::{
    geom::lie::photon_potentials,
    kinetic::{
        lie_hierarchy::{lie_data, LieHierarchy},
        lie_history::RayNode,
        memory_mixture::stf_matrix,
        spin_sht::{index, C64},
    },
};
use std::fs;
type Sky = Vec<Vec<C64>>;
const H0: f64 = 2.1842852410855023e-18;
const CS: f64 = 299792458. * 6.6524587051e-29;
fn interp(x: &[Vec<f64>], u: f64, k: usize) -> f64 {
    let i = x.partition_point(|r| r[0] <= u);
    if i == 0 {
        return x[0][k];
    }
    if i >= x.len() {
        return x.last().unwrap()[k];
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
fn collision(h: &LieHierarchy, y: &Sky, k: f64, out: &mut Sky) {
    let d = (8_f64 / 3.).sqrt();
    for l in 1..=h.lmax {
        for m in -(l as i64)..=l as i64 {
            let i = index(l, m);
            if l == 2 {
                let it = y[0][i];
                let e = -(y[1][i] + y[2][i]) * 0.5;
                let b = C64::new(0., 0.5) * (y[1][i] - y[2][i]);
                let di = k * (-0.9 * it + 0.4 / d * e);
                let de = k * (0.15 * d * it - 0.4 * e);
                let db = -k * b;
                out[0][i] += di;
                out[1][i] += -de - C64::new(0., 1.) * db;
                out[2][i] += -de + C64::new(0., 1.) * db;
            } else {
                for s in 0..3 {
                    out[s][i] -= k * y[s][i];
                }
            }
        }
    }
}
fn add(a: &[Sky], b: &[Sky], w: f64) -> Vec<Sky> {
    a.iter()
        .zip(b)
        .map(|(x, y)| {
            x.iter()
                .zip(y)
                .map(|(x, y)| x.iter().zip(y).map(|(x, y)| *x + w * *y).collect())
                .collect()
        })
        .collect()
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let geom = data(&p[0])?;
    let ne = data(&p[1])?;
    let amp: f64 = p[2].parse()?;
    let n: usize = p[3].parse()?;
    let h = LieHierarchy::new(6, true, 4.)?;
    let end = geom.last().unwrap()[0];
    // y0, y1, y2-stream, y2-geometry, B3 stream-E2, stream-E4,
    // geometry, other channels; the last four store just B3 spin slots.
    let mut y = vec![h.zero_state(); 8];
    y[0][0][0] = C64::new((4. * std::f64::consts::PI).sqrt(), 0.);
    let pot = |s: [f64; 5]| {
        let s = stf_matrix(s);
        let node = RayNode {
            shear: std::array::from_fn(|i| std::array::from_fn(|j| s[(i, j)])),
            ..Default::default()
        };
        photon_potentials(&lie_data(&node))
    };
    let rhs = |u: f64, y: &[Sky]| -> Vec<Sky> {
        let p1 = pot([interp(&geom, u, 3) / amp, 0., 0., 0., 0.]);
        let p2 = pot([0., interp(&geom, u, 4) / amp.powi(2), 0., 0., 0.]);
        let k = CS * interp(&ne, u, 1) / (H0 * interp(&geom, u, 2));
        let mut o = vec![h.zero_state(); 8];
        h.rhs(&p1, &y[0], &mut o[1]);
        collision(&h, &y[1], k, &mut o[1]);
        h.rhs(&p1, &y[1], &mut o[2]);
        collision(&h, &y[2], k, &mut o[2]);
        h.rhs(&p2, &y[0], &mut o[3]);
        collision(&h, &y[3], k, &mut o[3]);
        let mut extract = |target: usize, src: &Sky, pot: &_| {
            let mut r = h.zero_state();
            h.rhs(pot, src, &mut r);
            for m in -3..=3 {
                let i = index(3, m);
                for slot in 1..3 {
                    o[target][slot][i] += r[slot][i];
                }
            }
        };
        for (target, ell) in [(4, 2), (5, 4)] {
            let mut src = h.zero_state();
            for m in -(ell as i64)..=ell as i64 {
                let i = index(ell, m);
                for slot in 1..3 {
                    src[slot][i] = y[2][slot][i];
                }
            }
            extract(target, &src, &p1);
        }
        extract(6, &y[3], &p1);
        extract(6, &y[1], &p2);
        let mut rest = y[2].clone();
        for ell in [2, 4] {
            for m in -(ell as i64)..=ell as i64 {
                let i = index(ell, m);
                for slot in 1..3 {
                    rest[slot][i] = C64::new(0., 0.);
                }
            }
        }
        extract(7, &rest, &p1);
        for i in 4..8 {
            collision(&h, &y[i], k, &mut o[i]);
        }
        o
    };
    let dt = end / n as f64;
    for i in 0..n {
        let u = i as f64 * dt;
        let k1 = rhs(u, &y);
        let k2 = rhs(u + dt / 2., &add(&y, &k1, dt / 2.));
        let k3 = rhs(u + dt / 2., &add(&y, &k2, dt / 2.));
        let k4 = rhs(u + dt, &add(&y, &k3, dt));
        y = add(
            &add(&add(&add(&y, &k1, dt / 6.), &k2, dt / 3.), &k3, dt / 3.),
            &k4,
            dt / 6.,
        );
    }
    println!("channel,m,re,im");
    for (j, name) in [(4, "E2"), (5, "E4"), (6, "geometry"), (7, "other")] {
        for m in -3..=3 {
            let i = index(3, m);
            let b = C64::new(0., 0.5) * (y[j][1][i] - y[j][2][i]) / y[0][0][0].re;
            println!("{name},{m},{:.17e},{:.17e}", b.re, b.im);
        }
    }
    Ok(())
}
