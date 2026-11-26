use bianchi_rustcore::kinetic::quadratic_wedge::{harmonics, PAIRS};
fn data(p: &str) -> Result<Vec<Vec<f64>>, Box<dyn std::error::Error>> {
    Ok(std::fs::read_to_string(p)?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?)
}
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
    let geom = data(&p[0])?;
    let ne = data(&p[1])?;
    let n: usize = p[2].parse()?;
    let eps: f64 = p[3].parse()?;
    let end = geom.last().unwrap()[0];
    let du = end / n as f64;
    let rhs = |u: f64, y: &[f64; 20]| {
        let s: [f64; 5] = std::array::from_fn(|j| interp(&geom, u, 3 + j) / eps);
        let k = 299792458. * 6.6524587051e-29 / 2.1842852410855023e-18 * interp(&ne, u, 1)
            / interp(&geom, u, 2);
        let mut f = [0.; 20];
        for j in 0..5 {
            f[j] = -4. * s[j] - k * (0.9 * y[j] + 0.4 * y[j + 5]);
            f[j + 5] = -k * (0.15 * y[j] + 0.4 * y[j + 5]);
        }
        for (l, (i, j)) in PAIRS.into_iter().enumerate() {
            f[l + 10] = s[i] * y[j + 5] - s[j] * y[i + 5] - k * y[l + 10];
        }
        f
    };
    let mut y = [0.; 20];
    for i in 0..n {
        let t = i as f64 * du;
        let a = rhs(t, &y);
        let b = rhs(t + du / 2., &std::array::from_fn(|k| y[k] + du * a[k] / 2.));
        let c = rhs(t + du / 2., &std::array::from_fn(|k| y[k] + du * b[k] / 2.));
        let d = rhs(t + du, &std::array::from_fn(|k| y[k] + du * c[k]));
        for k in 0..20 {
            y[k] += du * (a[k] + 2. * b[k] + 2. * c[k] + d[k]) / 6.;
        }
    }
    let w: [f64; 10] = y[10..].try_into().unwrap();
    let b = harmonics(&w, 4.)?;
    println!("m,re,im");
    for (i, z) in b.iter().enumerate() {
        println!("{},{:.17e},{:.17e}", i as i32 - 3, z.re, z.im);
    }
    Ok(())
}
