use bianchi_rustcore::kinetic::{
    owned_thomson::ThomsonOwner,
    spin_sht::{index, C64},
};
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
    let x = std::fs::read_to_string(&p[0])?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    if p.len() != 4 {
        return Err("usage: clock controls steps lmax".into());
    }
    let a: Vec<f64> = std::fs::read_to_string(&p[1])?
        .split_whitespace()
        .map(str::parse::<f64>)
        .collect::<Result<_, _>>()?;
    if a.len() != 23 || !a.iter().all(|x| x.is_finite()) {
        return Err("expected three masses and four finite STF vectors".into());
    }
    let n: usize = p[2].parse()?;
    let l: usize = p[3].parse()?;
    if n == 0 || l < 7 {
        return Err("grid domain".into());
    }
    let vec = |k: usize| -> [f64; 5] { a[3 + 5 * k..3 + 5 * k + 5].try_into().unwrap() };
    let specs = [
        (a[0], 1. / 3., vec(1)),
        (a[1], 1. / 3., vec(2)),
        (a[2], 1. / 3., vec(3)),
    ];
    let m = ThomsonOwner::with_species(&specs, 32, 12, 24, l, 12, 24)?;
    let a0 = 1_f64 / 1601.;
    let cut = (1. / 21. / a0).ln();
    let end = (1. / 5. / a0).ln();
    let mut s = m.initial(a0, vec(0))?;
    let mut min_screen = 1.;
    println!("epoch,ell,m,Ire,Iim,Ere,Eim,Bre,Bim");
    eprintln!("u,a,h,S0,S1,S2,S3,S4,gauss");
    let mut t = 0.;
    let nlate = n / 8;
    for (part, nn, left, right) in [(0, n, 0., cut), (1, nlate, cut, end)] {
        for i in 0..=nn {
            if part == 0 || i > 0 {
                eprintln!(
                    "{t:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                    s.geometry.a,
                    s.geometry.h,
                    s.geometry.s[0],
                    s.geometry.s[1],
                    s.geometry.s[2],
                    s.geometry.s[3],
                    s.geometry.s[4],
                    m.constraint(&s)?
                );
            }
            if i == nn {
                {
                    for p in s.sky.photons()? {
                        let z = p.screen();
                        let e = nalgebra::Matrix3::from_fn(|i, j| z[i][j])
                            .symmetric_eigen()
                            .eigenvalues;
                        if e.min() < -1e-10 {
                            return Err("negative screen".into());
                        }
                        let mut a = e.as_slice().to_vec();
                        a.sort_by(f64::total_cmp);
                        min_screen = f64::min(min_screen, a[1]);
                    }
                    let y = &s.sky.coefficients;
                    let norm = y[0][0].re;
                    for ll in [2, 3, 5, 7] {
                        for mm in -(ll as i64)..=ll as i64 {
                            let k = index(ll, mm);
                            let ii = y[0][k] / norm;
                            let e = -(y[1][k] + y[2][k]) * 0.5 / norm;
                            let b = C64::new(0., 0.5) * (y[1][k] - y[2][k]) / norm;
                            println!(
                                "{part},{ll},{mm},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                                ii.re, ii.im, e.re, e.im, b.re, b.im
                            );
                        }
                    }
                    break;
                }
            }
            // advance from current t to next scheduled knot; in second segment i=0 skipped above,
            // so handle actual loop separately below.
            let target = left + (right - left) * (i + 1) as f64 / nn as f64;
            let du = target - t;
            let (q, _) = m.step(&s, du, interp(&x, t, 1), interp(&x, t + du / 2., 1))?;
            s = q;
            t = target;
        }
    }
    eprintln!("min_screen={min_screen:.17e}");
    Ok(())
}
