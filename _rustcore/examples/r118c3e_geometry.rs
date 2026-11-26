//! Conditional REC electron history, full native BASS state carried to REI.
use bianchi_rustcore::kinetic::owned_thomson::ThomsonOwner;
use std::{fs, io::Write};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let r = fs::read_to_string(&p[0])?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    let n: usize = p[1].parse()?;
    let amp: f64 = p[2].parse()?;
    let m = ThomsonOwner::new(0., 32, 8, 16, 4, 8, 16)?;
    let mut s = m.initial(r[0][2], [amp, 0., 0., 0., amp / 4.])?;
    let end = (1. / 21. / r[0][2]).ln();
    let ne = |u: f64| {
        let j = r.partition_point(|x| x[0] <= u);
        if j == 0 {
            return r[0][1];
        }
        if j == r.len() {
            return r[j - 1][1];
        }
        let (a, b) = (&r[j - 1], &r[j]);
        a[1] + (b[1] - a[1]) * (u - a[0]) / (b[0] - a[0])
    };
    let mut f = std::io::BufWriter::new(fs::File::create(&p[3])?);
    writeln!(
        f,
        "u,a,h,S0,S1,S2,S3,S4,ne,gauss,sky_energy,E2,B3,F00,F01,F02,F10,F11,F12,F20,F21,F22"
    )?;
    for i in 0..=n {
        let u = i as f64 * end / n as f64;
        let g = &s.geometry;
        let e = s.sky.moments()?.energy;
        let c = &s.sky.coefficients;
        let norm = |l: usize, mag: bool| {
            (l * l..(l + 1) * (l + 1))
                .map(|j| {
                    if mag {
                        (c[1][j] - c[2][j]).norm_sqr() * 0.25
                    } else {
                        (c[1][j] + c[2][j]).norm_sqr() * 0.25
                    }
                })
                .sum::<f64>()
                .sqrt()
                / c[0][0].re
        };
        write!(f, "{u:.17e},{:.17e},{:.17e}", g.a, g.h)?;
        for x in g.s {
            write!(f, ",{x:.17e}")?
        }
        write!(
            f,
            ",{:.17e},{:.17e},{e:.17e},{:.17e},{:.17e}",
            ne(u),
            m.constraint(&s)?,
            norm(2, false),
            norm(3, true)
        )?;
        for i in 0..3 {
            for j in 0..3 {
                write!(f, ",{:.17e}", g.f[(i, j)])?;
            }
        }
        writeln!(f)?;
        if i == n {
            break;
        }
        let du = if i == n - 1 {
            (1. / 21. / g.a).ln()
        } else {
            end / n as f64
        };
        let (mut q, _) = m.step(&s, du, ne(u), ne(u + du / 2.))?;
        if i == n - 1 {
            if (q.geometry.a - 1. / 21.).abs() > 1e-15 {
                return Err("boundary endpoint".into());
            }
            q.geometry.a = 1. / 21.;
        }
        s = q;
    }
    f.flush()?;
    fs::write(&p[4], m.state_text(&s)?)?;
    Ok(())
}
