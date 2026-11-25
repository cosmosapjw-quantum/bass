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
    let m = ThomsonOwner::new(0., 32, 12, 24, l, 12, 24)?;
    let mut s = m.initial(1. / 21., [amp * angle.cos(), amp * angle.sin(), 0., 0., 0.])?;
    let end = (21_f64 / 5.).ln();
    let du = end / n as f64;
    println!("u,a,h,S0,S1,S2,S3,S4,monopole,E2,B3,B3re_m2,B3im_m2,B5,gauss");
    for i in 0..=n {
        let y = &s.sky.coefficients;
        let e = |ll: usize, mm: i64| -(y[1][index(ll, mm)] + y[2][index(ll, mm)]) * 0.5;
        let b =
            |ll: usize, mm: i64| C64::new(0., 0.5) * (y[1][index(ll, mm)] - y[2][index(ll, mm)]);
        let norm = |ll: usize, electric: bool| {
            (-(ll as i64)..=ll as i64)
                .map(|m| {
                    if electric {
                        e(ll, m).norm_sqr()
                    } else {
                        b(ll, m).norm_sqr()
                    }
                })
                .sum::<f64>()
                .sqrt()
                / y[0][0].re
        };
        let g = &s.geometry;
        let b32 = b(3, 2) / y[0][0].re;
        println!("{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",i as f64*du,g.a,g.h,g.s[0],g.s[1],g.s[2],g.s[3],g.s[4],y[0][0].re,norm(2,true),norm(3,false),b32.re,b32.im,if l>=5{norm(5,false)}else{0.},m.constraint(&s)?);
        if i < n {
            let t = i as f64 * du;
            let (y, _) = m.step(&s, du, interp(&x, t, 1), interp(&x, t + du / 2., 1))?;
            s = y;
        }
    }
    Ok(())
}
