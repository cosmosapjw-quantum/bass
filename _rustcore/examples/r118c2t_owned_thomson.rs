use bianchi_rustcore::kinetic::{owned_thomson::ThomsonOwner, spin_sht::index};
use std::fs;
fn interp(x: &[(f64, f64)], u: f64) -> f64 {
    let i = x.partition_point(|r| r.0 <= u);
    if i == 0 {
        return x[0].1;
    }
    if i >= x.len() {
        return x[x.len() - 1].1;
    }
    let (a, y) = x[i - 1];
    let (b, z) = x[i];
    y + (z - y) * (u - a) / (b - a)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let eps: f64 = p[0].parse()?;
    let n: usize = p[1].parse()?;
    let l: usize = p[2].parse()?;
    let scatter = p[3] == "scatter";
    let input = fs::read_to_string(&p[4])?;
    let data: Vec<(f64, f64)> = input
        .lines()
        .skip(1)
        .map(|x| {
            let mut it = x.split(',');
            (
                it.next().unwrap().parse().unwrap(),
                it.next().unwrap().parse().unwrap(),
            )
        })
        .collect();
    let m = ThomsonOwner::new(eps, 32, 8, 16, l, l + 3, 2 * l + 6)?;
    let mut s = m.initial(1. / 21., [eps / 3., 0., 0., 0., eps / 4.])?;
    let du = (21_f64 / 5.).ln() / n as f64;
    let mut collision: f64 = 0.;
    println!("u,a,h,S0,S1,S2,S3,S4,F00,F01,F02,F10,F11,F12,F20,F21,F22,gauss,det,rho,photon,E2,B3,Eodd,Beven,min_screen,collision");
    for i in 0..=n {
        let u = i as f64 * du;
        let g = &s.geometry;
        let mat = m.matter(&s)?;
        let sm = s.sky.moments()?;
        let (mut e2, mut b3, mut eo, mut be) = (0., 0., 0., 0.);
        for ll in 2..=l {
            for mm in -(ll as i64)..=ll as i64 {
                let k = index(ll, mm);
                let ap = s.sky.coefficients[1][k];
                let am = s.sky.coefficients[2][k];
                let e = (ap + am) * 0.5;
                let b = (ap - am) * 0.5;
                if ll == 2 {
                    e2 += e.norm_sqr()
                }
                if ll == 3 {
                    b3 += b.norm_sqr()
                }
                if ll % 2 == 1 {
                    eo += e.norm_sqr()
                } else {
                    be += b.norm_sqr()
                }
            }
        }
        let norm = sm.energy / (4. * std::f64::consts::PI);
        print!("{u:.17e},{:.17e},{:.17e}", g.a, g.h);
        for v in g.s {
            print!(",{v:.17e}")
        }
        for j in 0..3 {
            for k in 0..3 {
                print!(",{:.17e}", g.f[(j, k)])
            }
        }
        println!(",{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{collision:.17e}",m.constraint(&s)?,g.f.determinant(),mat.rho,mat.photon_rho,e2.sqrt()/norm,b3.sqrt()/norm,eo.sqrt()/norm,be.sqrt()/norm,sm.minimum_screen_eigenvalue);
        if i < n {
            let ne = if scatter { interp(&data, u) } else { 0. };
            let nem = if scatter {
                interp(&data, u + du / 2.)
            } else {
                0.
            };
            let (t, c) = m.step(&s, du, ne, nem)?;
            s = t;
            collision = collision.max(c);
        }
    }
    Ok(())
}
