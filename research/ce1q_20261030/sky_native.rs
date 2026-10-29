//! CE1-Q: observer-tetrad energy-integrated sky harmonics from the immutable
//! six-cell collisionless massless Bianchi-I source and CE1-P metric histories.
//! BASS's actual covariant Frame::apply/det/phys_dirs and real_ylm_l are linked.
//! This binary64 physical observable is NOT an MPFR interval/blackbody/TQU claim.
//! Input: N_POSITIVE_OCTANT_RAYS N_TIMES LMAX (0<=LMAX<=4)
//!        MASS_BITS QX_BITS QY_BITS QZ_BITS for each positive ray
//!        U_BITS ELL1_BITS ELL2_BITS ELL3_BITS for each time
//! All _BITS are decimal unsigned u64 bit patterns preserving IEEE binary64.
//! Source mass includes *all eight* Cartesian reflections. Observable sky is
//! s=-n_photon, where n_photon=(M qhat)/|M qhat|.
#[path = "../../_rustcore/src/kinetic/comoving.rs"]
mod bass_comoving;
use bass_comoving::{phys_dirs, real_ylm_l, Frame};
use std::f64::consts::PI;
use std::io::{self, Read};

#[derive(Clone, Copy)]
struct Ray {
    mass: f64,
    n: [f64; 3],
}

fn positive_finite(x: f64, what: &str) -> Result<f64, String> {
    if x.is_finite() && x > 0.0 {
        Ok(x)
    } else {
        Err(format!("invalid positive {what}"))
    }
}
fn decode_f64(it: &mut std::str::SplitAsciiWhitespace<'_>) -> Result<f64, String> {
    let word = it.next().ok_or("missing float bit word")?;
    let bits = word.parse::<u64>().map_err(|_| "invalid float bit word")?;
    let x = f64::from_bits(bits);
    if x.is_finite() {
        Ok(x)
    } else {
        Err("nonfinite float".into())
    }
}
fn decode_usize(it: &mut std::str::SplitAsciiWhitespace<'_>) -> Result<usize, String> {
    it.next()
        .ok_or("missing count")?
        .parse::<usize>()
        .map_err(|_| "invalid count".into())
}

// Condon-Shortley associated Legendre polynomial P_l^m(z), m>=0.
fn assoc_legendre(l: usize, m: usize, z: f64) -> f64 {
    assert!(m <= l);
    let mut pmm = 1.0;
    for k in 1..=m {
        pmm *= -((2 * k - 1) as f64) * (1.0 - z * z).max(0.0).sqrt();
    }
    if l == m {
        return pmm;
    }
    let mut prev = pmm;
    let mut current = (2 * m + 1) as f64 * z * prev;
    if l == m + 1 {
        return current;
    }
    for n in (m + 2)..=l {
        let next = ((2 * n - 1) as f64 * z * current - (n + m - 1) as f64 * prev) / (n - m) as f64;
        prev = current;
        current = next;
    }
    current
}
fn ylm_conjugate(l: usize, m: usize, s: [f64; 3]) -> (f64, f64) {
    let norm_ratio = ((l - m + 1)..=(l + m)).fold(1.0, |a, i| a / (i as f64));
    let normalization = (((2 * l + 1) as f64) / (4.0 * PI) * norm_ratio).sqrt();
    let p = assoc_legendre(l, m, s[2]);
    let phase = (m as f64) * s[1].atan2(s[0]);
    (
        normalization * p * phase.cos(),
        -normalization * p * phase.sin(),
    )
}
fn offset(l: usize, m: usize) -> usize {
    l * (l + 1) / 2 + m
}
fn sky_row(
    ell: [f64; 3],
    rays: &[Ray],
    lmax: usize,
) -> Result<(f64, [f64; 3], Vec<(f64, f64)>, f64), String> {
    let mut m = [0.0; 9];
    for k in 0..3 {
        m[4 * k] = positive_finite((-ell[k]).exp(), "scale")?;
    }
    let frame = Frame { m };
    let det = positive_finite(frame.det(), "frame determinant")?;
    let ncomplex = (lmax + 1) * (lmax + 2) / 2;
    let mut harmonics = vec![(0.0, 0.0); ncomplex];
    let mut p = [0.0; 3];
    let mut energy = 0.0;
    let mut real2 = [0.0; 5];
    // Eight signed octants. Stored-positive-source mass already includes all 8.
    for ray in rays {
        let pq = frame.apply(&ray.n);
        let norm = (pq[0] * pq[0] + pq[1] * pq[1] + pq[2] * pq[2]).sqrt();
        let norm = positive_finite(norm, "observer momentum")?;
        // Actual BASS comoving-frame direction implementation, not a clone.
        let (nback, muback) = phys_dirs(&frame, &ray.n);
        if (muback[0] - norm).abs() > 3e-14
            || (0..3).any(|k| (nback[k] - pq[k] / norm).abs() > 3e-14)
        {
            return Err("BASS native direction map mismatch".into());
        }
        let weight = positive_finite(det * ray.mass * norm / 8.0, "physical ray energy")?;
        for sx in [-1.0, 1.0] {
            for sy in [-1.0, 1.0] {
                for sz in [-1.0, 1.0] {
                    // Observation sky direction opposite photon propagation.
                    let sky = [-sx * pq[0] / norm, -sy * pq[1] / norm, -sz * pq[2] / norm];
                    energy += weight;
                    for k in 0..3 {
                        p[k] += weight * sky[k] * sky[k];
                    }
                    if lmax >= 2 {
                        let b2 = real_ylm_l(2, &sky);
                        for k in 0..5 {
                            real2[k] += weight * b2[k];
                        }
                    }
                    for l in 0..=lmax {
                        for j in 0..=l {
                            let (yr, yi) = ylm_conjugate(l, j, sky);
                            let a = &mut harmonics[offset(l, j)];
                            a.0 += weight * yr;
                            a.1 += weight * yi;
                        }
                    }
                }
            }
        }
    }
    let mut native_diff = 0.0f64;
    if lmax >= 2 {
        // BASS exact real basis [xy, yz, 3z²-1, xz, x²-y²] must
        // match standard complex Y_lm quadrupole (Condon-Shortley).
        native_diff = native_diff.max((real2[2] - harmonics[offset(2, 0)].0).abs());
        native_diff =
            native_diff.max((real2[4] - (2.0f64).sqrt() * harmonics[offset(2, 2)].0).abs());
        native_diff =
            native_diff.max((real2[3] + (2.0f64).sqrt() * harmonics[offset(2, 1)].0).abs());
        native_diff =
            native_diff.max((real2[1] - (2.0f64).sqrt() * harmonics[offset(2, 1)].1).abs());
        native_diff =
            native_diff.max((real2[0] + (2.0f64).sqrt() * harmonics[offset(2, 2)].1).abs());
    }
    Ok((energy, p, harmonics, native_diff))
}
fn run(s: &str) -> Result<String, String> {
    let mut it = s.split_ascii_whitespace();
    let n = decode_usize(&mut it)?;
    let nt = decode_usize(&mut it)?;
    let lmax = decode_usize(&mut it)?;
    if n == 0 || n > 100_000 || nt == 0 || nt > 500 || lmax > 4 {
        return Err("invalid ray/time/lmax cardinality".into());
    }
    let mut rays = Vec::with_capacity(n);
    let mut masses = 0.0;
    for _ in 0..n {
        let mass = positive_finite(decode_f64(&mut it)?, "mass")?;
        let mut q = [0.0; 3];
        for v in q.iter_mut() {
            *v = decode_f64(&mut it)?;
        }
        if q.iter().any(|v| *v < 0.0) {
            return Err("expected positive octant ray".into());
        }
        let norm2 = q.iter().map(|v| v * v).sum::<f64>();
        if (norm2 - 1.0).abs() > 1e-11 {
            return Err("nonunit positive octant ray".into());
        }
        masses += mass;
        rays.push(Ray { mass, n: q });
    }
    if (masses - 0.9).abs() > 5e-12 {
        return Err(format!("source mass mismatch {masses}"));
    }
    let mut times = Vec::with_capacity(nt);
    for _ in 0..nt {
        let u = decode_f64(&mut it)?;
        let mut ell = [0.0; 3];
        for v in ell.iter_mut() {
            *v = decode_f64(&mut it)?;
        }
        if !(0.0..=0.08).contains(&u) {
            return Err("outside frozen proper-time domain".into());
        }
        if ell.iter().any(|x| *x < 0.0) {
            return Err("not all expanding".into());
        }
        times.push((u, ell));
    }
    if it.next().is_some() {
        return Err("unexpected trailing input".into());
    }
    let mut out = String::new();
    out.push_str("u,E,P1,P2,P3,native_real_basis_gap");
    for l in 0..=lmax {
        for m in -(l as i32)..=(l as i32) {
            out.push_str(&format!(",a_{l}_{m}_re,a_{l}_{m}_im"));
        }
    }
    out.push('\n');
    for (u, ell) in times {
        let (e, p, a, ngap) = sky_row(ell, &rays, lmax)?;
        out.push_str(&format!(
            "{u:.17e},{e:.17e},{:.17e},{:.17e},{:.17e},{ngap:.17e}",
            p[0], p[1], p[2]
        ));
        for l in 0..=lmax {
            for m in -(l as i32)..=(l as i32) {
                let (rr, ii) = a[offset(l, m.unsigned_abs() as usize)];
                let (rr, ii) = if m < 0 {
                    let sign = if -m % 2 == 0 { 1.0 } else { -1.0 };
                    (sign * rr, -sign * ii)
                } else {
                    (rr, ii)
                };
                out.push_str(&format!(",{rr:.17e},{ii:.17e}"));
            }
        }
        out.push('\n');
    }
    Ok(out)
}
fn main() {
    if std::env::args().nth(1).as_deref() == Some("--selftest") {
        let rays = [Ray {
            mass: 0.9,
            n: [1.0, 0.0, 0.0],
        }];
        let (e, p, a, d) = sky_row([0.0; 3], &rays, 4).expect("selftest");
        assert!((e - 0.9).abs() < 5e-15);
        assert!((p[0] - 0.9).abs() < 5e-15 && p[1].abs() < 5e-15 && p[2].abs() < 5e-15);
        assert!((a[0].0 * (4.0 * PI).sqrt() - e).abs() < 5e-15);
        assert!(d < 5e-14); // BASS real-harmonic conventions cross-check.
        assert!((ylm_conjugate(0, 0, [0.0, 0.0, 1.0]).0 - (4.0 * PI).sqrt().recip()).abs() < 1e-15);
        assert!((assoc_legendre(2, 0, 0.0) + 0.5).abs() < 1e-15);
        println!("BASS_CE1Q_NATIVE_RUST_SELFTEST_PASS");
        return;
    }
    let mut inp = String::new();
    if let Err(e) = io::stdin().read_to_string(&mut inp) {
        eprintln!("BASS_CE1Q_REJECT: {e}");
        std::process::exit(2);
    }
    match run(&inp) {
        Ok(csv) => print!("{csv}"),
        Err(e) => {
            eprintln!("BASS_CE1Q_REJECT: {e}");
            std::process::exit(2);
        }
    }
}
