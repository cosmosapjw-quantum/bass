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
    let amp: f64 = p[1].parse()?;
    let angle: f64 = p[2].parse()?;
    let n: usize = p[3].parse()?;
    let l: usize = p[4].parse()?;
    let m = ThomsonOwner::new(
        if p[5] == "multi" { amp } else { 0. },
        32,
        12,
        24,
        l,
        12,
        24,
    )?;
    let mut s = m.initial(
        1. / 21.,
        [
            amp * angle.cos() / 3.,
            amp * angle.sin() / 3.,
            0.,
            0.,
            amp / 4.,
        ],
    )?;
    let end = (21_f64 / 5.).ln();
    let du = end / n as f64;
    eprintln!("u,a,h,S0,S1,S2,S3,S4");
    for i in 0..n {
        eprintln!(
            "{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            i as f64 * du,
            s.geometry.a,
            s.geometry.h,
            s.geometry.s[0],
            s.geometry.s[1],
            s.geometry.s[2],
            s.geometry.s[3],
            s.geometry.s[4]
        );
        let t = i as f64 * du;
        let (y, _) = m.step(&s, du, interp(&x, t, 1), interp(&x, t + du / 2., 1))?;
        s = y;
    }
    eprintln!(
        "{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
        end,
        s.geometry.a,
        s.geometry.h,
        s.geometry.s[0],
        s.geometry.s[1],
        s.geometry.s[2],
        s.geometry.s[3],
        s.geometry.s[4]
    );
    let y = &s.sky.coefficients;
    println!("ell,m,re,im");
    for ll in [3, 5, 7] {
        for m in -(ll as i64)..=ll as i64 {
            let k = index(ll, m);
            let b = C64::new(0., 0.5) * (y[1][k] - y[2][k]) / y[0][0].re;
            println!("{ll},{m},{:.17e},{:.17e}", b.re, b.im);
        }
    }
    eprintln!("gauss={:.17e}", m.constraint(&s)?);
    Ok(())
}
