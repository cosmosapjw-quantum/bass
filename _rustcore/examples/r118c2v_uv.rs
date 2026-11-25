use bianchi_rustcore::kinetic::{
    owned_thomson::ThomsonOwner,
    uv_feedback::{Gas, UvModel},
};
use std::fs;
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
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let data = fs::read_to_string(&p[0])?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    let nh0: f64 = p[1].parse()?;
    let n: usize = p[2].parse()?;
    let nq: usize = p[3].parse()?;
    let strength: f64 = p[4].parse()?;
    let feedback = p[5] == "on";
    let m = ThomsonOwner::new(0.03, 32, 8, 16, 4, 8, 16)?;
    let uv = UvModel::new(1. / 21., nh0, 8, 16, nq, strength)?;
    let mut s = m.initial(1. / 21., [0.03 / 3., 0., 0., 0., 0.03 / 4.])?;
    let mut us = uv.empty();
    let end = (21_f64 / 5.).ln();
    let du = end / n as f64;
    let gas = |u: f64| Gas {
        ne_m3: interp(&data, u, 1),
        absorbers_m3: std::array::from_fn(|k| interp(&data, u, k + 2)),
    };
    println!("u,a,h,S0,S1,S2,S3,S4,F00,F01,F02,F10,F11,F12,F20,F21,F22,gauss,UV,Pxx,Pyy,Pzz,Pxy,Pxz,Pyz,reservoir,work,emitted,absorbed,births,absorbed_n,ledger");
    for i in 0..=n {
        let g = &s.geometry;
        let (u, q) = uv.moments(&us, g)?;
        print!("{:.17e},{:.17e},{:.17e}", i as f64 * du, g.a, g.h);
        for x in g.s {
            print!(",{x:.17e}")
        }
        for j in 0..3 {
            for k in 0..3 {
                print!(",{:.17e}", g.f[(j, k)]);
            }
        }
        println!(",{:.17e},{u:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",m.constraint_uv(&s,&uv,&us,feedback)?,q[(0,0)],q[(1,1)],q[(2,2)],q[(0,1)],q[(0,2)],q[(1,2)],us.reservoir,us.work,us.emitted,us.absorbed,us.births,us.absorbed_n,u+us.reservoir+us.work);
        if i < n {
            let u = i as f64 * du;
            let (y, v, _) = m.step_uv(
                &s,
                &uv,
                &us,
                du,
                gas(u),
                gas(u + du / 4.),
                gas(u + du / 2.),
                feedback,
            )?;
            s = y;
            us = v;
        }
    }
    Ok(())
}
