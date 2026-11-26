use bianchi_rustcore::kinetic::{
    memory_mixture::stf_matrix,
    owned_thomson::ThomsonOwner,
    spin_sht::{index, SpinSht, C64},
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
    let m = ThomsonOwner::new(0., 32, 12, 24, l, 20, 40)?;
    let mut s = m.initial(1. / 21., [amp * angle.cos(), amp * angle.sin(), 0., 0., 0.])?;
    let end = (21_f64 / 5.).ln();
    let du = end / n as f64;
    for i in 0..n {
        let t = i as f64 * du;
        let (y, _) = m.step(&s, du, interp(&x, t, 1), interp(&x, t + du / 2., 1))?;
        s = y;
    }
    let t = stf_matrix([angle.cos(), angle.sin(), 0., 0., 0.]);
    let eig = [t[(0, 0)], t[(1, 1)], t[(2, 2)]];
    let delta = (eig[1] - eig[0]) * (eig[2] - eig[0]) * (eig[2] - eig[1]);
    let sht = SpinSht::new(14, 24, 48)?;
    let y = &s.sky.coefficients;
    println!("ell,m,re,im,template_re,template_im");
    for ll in [3, 5, 7, 9, 11] {
        let k = (ll - 3) / 2;
        // SHT projection of D Q^k onto exactly ll removes all traces.
        let f: Vec<f64> = sht
            .grid
            .ehat
            .chunks_exact(3)
            .map(|v| {
                let q = eig.iter().zip(v).map(|(t, x)| t * x * x).sum::<f64>();
                delta * v[0] * v[1] * v[2] * q.powi(k as i32)
            })
            .collect();
        let z = vec![0.; f.len()];
        let c = sht.from_stokes(&f, &z, &z);
        for m in -(ll as i64)..=ll as i64 {
            let k = index(ll, m);
            let b = C64::new(0., 0.5) * (y[1][k] - y[2][k]) / y[0][0].re;
            let v = c[0][k];
            println!(
                "{ll},{m},{:.17e},{:.17e},{:.17e},{:.17e}",
                b.re, b.im, v.re, v.im
            );
        }
    }
    Ok(())
}
