//! Opt-in KL projection of a new isotropic source onto P2=P4=0.
//!
//! std-only; the support, source-frame directions and spectral owner stay fixed.
//! This is a birth quadrature operation. Do not reweight surviving photons.
//! Geometry is checked before optimization. Float-ambiguous geometry is reported
//! unresolved, including compatible rank1 supports; it is not called infeasible.
//! Build CLI: rustc --edition=2021 -O balance_p24.rs -o balance_p24_probe
//! Tests:     rustc --edition=2021 --test balance_p24.rs -o balance_p24_tests
use std::fs::{self, OpenOptions};
use std::io::Write;

pub const ID: &str = "BASS_LRS_SOURCE_KL_P24_V1";
pub const DEFAULT_TOL: f64 = 3e-15;
const PARITY_TOL: f64 = 5e-14;
const GEOMETRY_GUARD: f64 = 64.0 * f64::EPSILON;

#[derive(Debug)]
pub struct Projection {
    pub weights: Vec<f64>,
    pub multipliers: [f64; 2],
    pub residuals: [f64; 2],
    /// Number of evaluated nested distributions, including bracket searches.
    pub iterations: usize,
}

fn sum(xs: impl Iterator<Item = f64>) -> f64 {
    let (mut s, mut correction) = (0.0_f64, 0.0_f64);
    for x in xs {
        let next = s + x;
        correction += if s.abs() >= x.abs() {
            (s - next) + x
        } else {
            (x - next) + s
        };
        s = next;
    }
    s + correction
}

fn geometry(mu: &[f64]) -> Result<(), &'static str> {
    let mut z: Vec<f64> = mu.iter().map(|m| m * m).collect();
    z.sort_by(f64::total_cmp);
    z.dedup_by(|a, b| *a == *b);
    let (t, v) = (1.0 / 3.0, 1.0 / 5.0);
    if z.len() == 1 {
        return Err("INFEASIBLE_P24_RANK0");
    }
    let first = z[0];
    let last = z[z.len() - 1];
    if t - first < -GEOMETRY_GUARD || last - t < -GEOMETRY_GUARD {
        return Err("INFEASIBLE_P24_MEAN");
    }
    let upper = (first + last) * t - first * last;
    if z.len() == 2 {
        if (upper - v).abs() > GEOMETRY_GUARD {
            return Err("INFEASIBLE_P24_RANK1");
        }
        // Exact rank1 feasibility is affine compatibility, proved separately.
        // A near-zero f64 defect does not certify that exact equality holds.
        // There is no silent rank2 solve or enlarged constraint tolerance here.
        return Err("FEASIBILITY_UNRESOLVED_RANK1");
    }
    let lower = z.windows(2)
        .map(|pair| (pair[0] + pair[1]) * t - pair[0] * pair[1])
        .fold(f64::NEG_INFINITY, f64::max);
    let lower_gap = v - lower;
    let upper_gap = upper - v;
    if lower_gap < -GEOMETRY_GUARD {
        return Err("INFEASIBLE_P24_LOWER");
    }
    if upper_gap < -GEOMETRY_GUARD {
        return Err("INFEASIBLE_P24_UPPER");
    }
    if lower_gap <= GEOMETRY_GUARD || upper_gap <= GEOMETRY_GUARD
        || t - first <= GEOMETRY_GUARD || last - t <= GEOMETRY_GUARD
    {
        return Err("FEASIBILITY_UNRESOLVED_NEAR_BOUNDARY");
    }
    Ok(())
}

struct Evaluated {
    weights: Vec<f64>,
    residuals: [f64; 2],
    lambda2: f64,
}

fn evaluated(
    logq: &[f64], p2: &[f64], p4: &[f64], lambda2: f64, lambda4: f64,
    count: &mut usize,
) -> Result<Evaluated, &'static str> {
    *count += 1;
    let logs: Vec<f64> = logq.iter().zip(p2).zip(p4)
        .map(|((q, a), b)| q + lambda2 * a + lambda4 * b).collect();
    let top = logs.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    if !top.is_finite() {
        return Err("NUMERIC_EXPONENTIAL_DOMAIN");
    }
    let mut weights: Vec<f64> = logs.iter().map(|x| (x - top).exp()).collect();
    let total = sum(weights.iter().copied());
    if !total.is_finite() || total <= 0.0 {
        return Err("NUMERIC_NORMALIZATION_DOMAIN");
    }
    for w in &mut weights {
        *w /= total;
    }
    let residuals = [
        sum(weights.iter().zip(p2).map(|(a, p)| a * p)),
        sum(weights.iter().zip(p4).map(|(a, p)| a * p)),
    ];
    if residuals.iter().any(|m| !m.is_finite()) {
        return Err("NUMERIC_MOMENT_DOMAIN");
    }
    // Zero tail weights may occur at bracket probes only. finish() rejects them
    // in every accepted output, independently of moment residuals.
    Ok(Evaluated { weights, residuals, lambda2 })
}

fn solve_p2(
    logq: &[f64], p2: &[f64], p4: &[f64], lambda4: f64, inner_tol: f64,
    count: &mut usize,
) -> Result<Evaluated, &'static str> {
    let initial = evaluated(logq, p2, p4, 0.0, lambda4, count)?;
    if initial.residuals[0].abs() <= inner_tol {
        return Ok(initial);
    }
    let (mut lo, mut hi) = (-1.0_f64, 1.0_f64);
    let mut lower = None;
    let mut upper = None;
    for _ in 0..60 {
        let e = evaluated(logq, p2, p4, lo, lambda4, count)?;
        if e.residuals[0] <= 0.0 {
            lower = Some(e);
            break;
        }
        lo *= 2.0;
    }
    for _ in 0..60 {
        let e = evaluated(logq, p2, p4, hi, lambda4, count)?;
        if e.residuals[0] >= 0.0 {
            upper = Some(e);
            break;
        }
        hi *= 2.0;
    }
    let lower = lower.ok_or("INNER_P2_LOWER_BRACKET")?;
    let upper = upper.ok_or("INNER_P2_UPPER_BRACKET")?;
    if lower.residuals[0].abs() <= inner_tol {
        return Ok(lower);
    }
    if upper.residuals[0].abs() <= inner_tol {
        return Ok(upper);
    }
    for _ in 0..200 {
        let lambda2 = lo + (hi - lo) / 2.0;
        if lambda2 == lo || lambda2 == hi {
            return Err("INNER_P2_PRECISION_LIMIT");
        }
        let e = evaluated(logq, p2, p4, lambda2, lambda4, count)?;
        if e.residuals[0].abs() <= inner_tol {
            return Ok(e);
        }
        if e.residuals[0] < 0.0 {
            lo = lambda2;
        } else {
            hi = lambda2;
        }
    }
    Err("INNER_P2_NOT_CONVERGED")
}

fn finish(
    e: Evaluated, lambda4: f64, tol: f64, count: usize,
) -> Result<Projection, &'static str> {
    if e.weights.iter().any(|w| !w.is_finite() || *w <= 0.0) {
        return Err("NUMERIC_POSITIVE_SUPPORT_LOSS");
    }
    if e.residuals.iter().any(|m| m.abs() > tol) {
        return Err("MOMENT_TOLERANCE");
    }
    if (sum(e.weights.iter().copied()) - 1.0).abs() > tol {
        return Err("NORMALIZATION_TOLERANCE");
    }
    let n = e.weights.len();
    if (0..n).any(|i| (e.weights[i] - e.weights[n - 1 - i]).abs() > PARITY_TOL) {
        return Err("NUMERIC_REFLECTION_LOSS");
    }
    Ok(Projection {
        weights: e.weights,
        multipliers: [e.lambda2, lambda4],
        residuals: e.residuals,
        iterations: count,
    })
}

pub fn project(mu: &[f64], prior: &[f64], tol: f64) -> Result<Projection, &'static str> {
    let n = mu.len();
    if n < 2 || n > 4096 || prior.len() != n {
        return Err("ANGULAR_INPUT_DOMAIN");
    }
    if !tol.is_finite() || !(1e-16..=DEFAULT_TOL).contains(&tol) {
        return Err("ANGULAR_TOLERANCE_DOMAIN");
    }
    for i in 0..n {
        if !mu[i].is_finite() || mu[i].abs() > 1.0
            || !prior[i].is_finite() || prior[i] <= 0.0
            || (i > 0 && mu[i] <= mu[i - 1])
        {
            return Err("ANGULAR_INPUT_DOMAIN");
        }
    }
    let scale = prior.iter().copied().fold(0.0_f64, f64::max);
    let mut q: Vec<f64> = prior.iter().map(|value| value / scale).collect();
    let total = sum(q.iter().copied());
    for w in &mut q {
        *w /= total;
        if *w <= 0.0 || !w.is_finite() {
            return Err("NUMERIC_POSITIVE_SUPPORT_LOSS");
        }
    }
    for i in 0..n {
        if (mu[i] + mu[n - 1 - i]).abs() > PARITY_TOL
            || (q[i] - q[n - 1 - i]).abs() > PARITY_TOL
        {
            return Err("REFLECTION_SOURCE_REQUIRED");
        }
    }
    geometry(mu)?;
    let p2: Vec<f64> = mu.iter().map(|m| (3.0 * m * m - 1.0) / 2.0).collect();
    let p4: Vec<f64> = mu.iter().map(|m| {
        let z = m * m;
        (35.0 * z * z - 30.0 * z + 3.0) / 8.0
    }).collect();
    let before = [sum(q.iter().zip(&p2).map(|(a, p)| a * p)),
                  sum(q.iter().zip(&p4).map(|(a, p)| a * p))];
    if before.iter().all(|m| m.abs() <= tol) {
        return finish(Evaluated { weights: q, residuals: before, lambda2: 0.0 }, 0.0, tol, 0);
    }
    let logq: Vec<f64> = q.iter().map(|q| q.ln()).collect();
    let inner_tol = tol / 8.0;
    let mut count = 0;
    let initial = solve_p2(&logq, &p2, &p4, 0.0, inner_tol, &mut count)?;
    if initial.residuals[1].abs() <= tol {
        return finish(initial, 0.0, tol, count);
    }
    let (mut lo, mut hi) = (-1.0_f64, 1.0_f64);
    let mut lower = None;
    let mut upper = None;
    for _ in 0..60 {
        let e = solve_p2(&logq, &p2, &p4, lo, inner_tol, &mut count)?;
        if e.residuals[1] <= 0.0 {
            lower = Some(e);
            break;
        }
        lo *= 2.0;
    }
    for _ in 0..60 {
        let e = solve_p2(&logq, &p2, &p4, hi, inner_tol, &mut count)?;
        if e.residuals[1] >= 0.0 {
            upper = Some(e);
            break;
        }
        hi *= 2.0;
    }
    let lower = lower.ok_or("OUTER_P4_LOWER_BRACKET")?;
    let upper = upper.ok_or("OUTER_P4_UPPER_BRACKET")?;
    if lower.residuals[1].abs() <= tol {
        return finish(lower, lo, tol, count);
    }
    if upper.residuals[1].abs() <= tol {
        return finish(upper, hi, tol, count);
    }
    for _ in 0..200 {
        let lambda4 = lo + (hi - lo) / 2.0;
        if lambda4 == lo || lambda4 == hi {
            return Err("OUTER_P4_PRECISION_LIMIT");
        }
        let e = solve_p2(&logq, &p2, &p4, lambda4, inner_tol, &mut count)?;
        if e.residuals[1].abs() <= tol {
            return finish(e, lambda4, tol, count);
        }
        if e.residuals[1] < 0.0 {
            lo = lambda4;
        } else {
            hi = lambda4;
        }
    }
    Err("OUTER_P4_NOT_CONVERGED")
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        return Err("USAGE balance_p24_probe INPUT OUTPUT".into());
    }
    if fs::metadata(&args[1]).map_err(|e| e.to_string())?.len() > 2_000_000 {
        return Err("INPUT_SIZE".into());
    }
    let data = fs::read_to_string(&args[1]).map_err(|e| e.to_string())?;
    let mut it = data.split_whitespace();
    if it.next() != Some(ID) {
        return Err("INPUT_SCHEMA".into());
    }
    let n: usize = it.next().ok_or("CASE_COUNT")?.parse().map_err(|_| "CASE_COUNT")?;
    if n == 0 || n > 512 {
        return Err("CASE_COUNT".into());
    }
    let mut lines = Vec::new();
    let mut ids = std::collections::HashSet::new();
    for _ in 0..n {
        let id = it.next().ok_or("CASE_ID")?;
        if id.contains(',') || !ids.insert(id) {
            return Err("CASE_ID".into());
        }
        let m: usize = it.next().ok_or("RAY_COUNT")?.parse().map_err(|_| "RAY_COUNT")?;
        if m < 2 || m > 4096 {
            return Err("RAY_COUNT".into());
        }
        let (mut mu, mut q) = (Vec::with_capacity(m), Vec::with_capacity(m));
        for _ in 0..m {
            mu.push(it.next().ok_or("TRUNCATED")?.parse::<f64>().map_err(|_| "NUMBER")?);
            q.push(it.next().ok_or("TRUNCATED")?.parse::<f64>().map_err(|_| "NUMBER")?);
        }
        let r = project(&mu, &q, DEFAULT_TOL).map_err(str::to_string)?;
        let weights = r.weights.iter().map(|w| format!("{:.17e}", w)).collect::<Vec<_>>().join(",");
        lines.push(format!("{},{},{:.17e},{:.17e},{:.17e},{:.17e},{},{}",
                           id, m, r.multipliers[0], r.multipliers[1],
                           r.residuals[0], r.residuals[1], r.iterations, weights));
    }
    if it.next().is_some() {
        return Err("TRAILING_INPUT".into());
    }
    // All cases must pass before an output is created; create_new forbids overwrite.
    let mut output = OpenOptions::new().write(true).create_new(true).open(&args[2])
        .map_err(|e| e.to_string())?;
    writeln!(output, "{} {}", ID, n).map_err(|e| e.to_string())?;
    for row in lines {
        writeln!(output, "{}", row).map_err(|e| e.to_string())?;
    }
    writeln!(output, "END {}", n).map_err(|e| e.to_string())?;
    println!("BALANCE_P24_PASS cases={}", n);
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("BALANCE_P24_ERROR {}", error);
        std::process::exit(3);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn five() -> (Vec<f64>, Vec<f64>) {
        let half = 0.5_f64.sqrt();
        (vec![-1.0, -half, 0.0, half, 1.0], vec![0.08, 0.19, 0.46, 0.19, 0.08])
    }

    fn paired_z(z: &[f64]) -> Vec<f64> {
        let mut mu = Vec::new();
        for zz in z.iter().rev() {
            if *zz > 0.0 { mu.push(-zz.sqrt()); }
        }
        for zz in z {
            mu.push(zz.sqrt());
        }
        mu
    }

    #[test]
    fn analytic_three_group_unique_weights() {
        let (mu, q) = five();
        let r = project(&mu, &q, DEFAULT_TOL).unwrap();
        let expected = [1.0/30.0, 4.0/15.0, 2.0/5.0, 4.0/15.0, 1.0/30.0];
        for (actual, target) in r.weights.iter().zip(expected) {
            assert!((actual-target).abs() < 8e-15);
        }
        assert!(r.residuals.iter().all(|m| m.abs() <= DEFAULT_TOL));
        assert!(r.weights.iter().all(|w| *w > 0.0));
        assert_eq!(r.weights[0], r.weights[4]);
        assert_eq!(r.weights[1], r.weights[3]);
    }

    #[test]
    fn manufactured_exponential_family_kl_solution() {
        let mu = paired_z(&[0.0, 0.25, 0.5, 1.0]);
        let expected = [4.0/75.0, 11.0/75.0, 4.0/25.0, 7.0/25.0,
                        4.0/25.0, 11.0/75.0, 4.0/75.0];
        let q: Vec<f64> = mu.iter().zip(expected).map(|(m, a)| {
            let z=m*m;
            a * (-0.7*(3.0*z-1.0)/2.0 + 0.4*(35.0*z*z-30.0*z+3.0)/8.0).exp()
        }).collect();
        let r = project(&mu, &q, DEFAULT_TOL).unwrap();
        assert!(r.weights.iter().zip(expected).all(|(a,b)| (a-b).abs()<1e-14));
        assert!((r.multipliers[0]-0.7).abs()<2e-13);
        assert!((r.multipliers[1]+0.4).abs()<2e-13);
    }

    #[test]
    fn idempotence_without_changing_weights() {
        let (mu, q) = five();
        let r = project(&mu, &q, DEFAULT_TOL).unwrap();
        let second = project(&mu, &r.weights, DEFAULT_TOL).unwrap();
        assert_eq!(second.iterations, 0);
        assert!(second.weights.iter().zip(&r.weights).all(|(a,b)| (a-b).abs()<5e-16));
    }

    #[test]
    fn positive_prior_scale_invariance() {
        let (mu, q) = five();
        let r = project(&mu, &q, DEFAULT_TOL).unwrap();
        for scale in [1e-300, 1e300] {
            let changed: Vec<f64> = q.iter().map(|w| w*scale).collect();
            let other=project(&mu, &changed, DEFAULT_TOL).unwrap();
            assert!(r.weights.iter().zip(other.weights).all(|(a,b)| (a-b).abs()<1e-14));
        }
    }

    #[test]
    fn clear_lower_hull_failure() {
        let mu = paired_z(&[0.0, 0.7, 1.0]);
        assert_eq!(project(&mu, &vec![1.0;mu.len()], DEFAULT_TOL).unwrap_err(), "INFEASIBLE_P24_LOWER");
    }

    #[test]
    fn clear_upper_hull_failure() {
        let mu = paired_z(&[0.0, 0.25, 0.5]);
        assert_eq!(project(&mu, &vec![1.0;mu.len()], DEFAULT_TOL).unwrap_err(), "INFEASIBLE_P24_UPPER");
    }

    #[test]
    fn clear_mean_failure() {
        let mu = paired_z(&[0.6, 0.7, 0.9]);
        assert_eq!(project(&mu, &vec![1.0;mu.len()], DEFAULT_TOL).unwrap_err(), "INFEASIBLE_P24_MEAN");
    }

    #[test]
    fn rank0_cannot_match_positive_variance() {
        let mu = paired_z(&[1.0/3.0]);
        assert_eq!(project(&mu, &[0.5,0.5], DEFAULT_TOL).unwrap_err(), "INFEASIBLE_P24_RANK0");
    }

    #[test]
    fn rank1_p2_balanced_but_p4_incompatible() {
        let mu = paired_z(&[1.0/6.0, 0.5]);
        assert_eq!(project(&mu, &[0.25;4], DEFAULT_TOL).unwrap_err(), "INFEASIBLE_P24_RANK1");
    }

    #[test]
    fn mathematically_feasible_rank1_is_unresolved_not_infeasible() {
        let mu = paired_z(&[0.0, 0.6]);
        let q = [5.0/18.0,4.0/9.0,5.0/18.0];
        assert_eq!(project(&mu, &q, DEFAULT_TOL).unwrap_err(), "FEASIBILITY_UNRESOLVED_RANK1");
    }

    #[test]
    fn boundary_or_float_ambiguity_is_unresolved() {
        for z in [&[0.0,0.6,1.0][..], &[0.0,0.3,0.6][..], &[0.0,0.6-1e-14,1.0][..]] {
            let mu=paired_z(z);
            assert_eq!(project(&mu,&vec![1.0;mu.len()],DEFAULT_TOL).unwrap_err(),
                       "FEASIBILITY_UNRESOLVED_NEAR_BOUNDARY");
        }
    }

    #[test]
    fn refuses_tolerance_relaxation() {
        let (mu,q)=five();
        for tol in [0.0,1e-17,3.01e-15,1e-10,f64::NAN] {
            assert_eq!(project(&mu,&q,tol).unwrap_err(),"ANGULAR_TOLERANCE_DOMAIN");
        }
    }

    #[test]
    fn validates_input_domain() {
        let (mu,q)=five();
        let mut wrong=mu.clone();wrong[2]=f64::NAN;
        assert_eq!(project(&wrong,&q,DEFAULT_TOL).unwrap_err(),"ANGULAR_INPUT_DOMAIN");
        let mut unsorted=mu.clone();unsorted.swap(0,1);
        assert_eq!(project(&unsorted,&q,DEFAULT_TOL).unwrap_err(),"ANGULAR_INPUT_DOMAIN");
        let mut bad=q.clone();bad[1]=0.0;
        assert_eq!(project(&mu,&bad,DEFAULT_TOL).unwrap_err(),"ANGULAR_INPUT_DOMAIN");
        let mut bad=q.clone();bad[2]=f64::INFINITY;
        assert_eq!(project(&mu,&bad,DEFAULT_TOL).unwrap_err(),"ANGULAR_INPUT_DOMAIN");
    }

    #[test]
    fn rejects_odd_source_and_asymmetric_rays() {
        let (mu,mut q)=five();q[0]*=2.0;
        assert_eq!(project(&mu,&q,DEFAULT_TOL).unwrap_err(),"REFLECTION_SOURCE_REQUIRED");
        let (mut mu,q)=five();mu[0]=-0.99;
        assert_eq!(project(&mu,&q,DEFAULT_TOL).unwrap_err(),"REFLECTION_SOURCE_REQUIRED");
    }

    #[test]
    fn reports_normalization_underflow_as_numeric() {
        let (mu,_)=five();
        let q=[1e-308,1e-308,1e308,1e-308,1e-308];
        assert_eq!(project(&mu,&q,DEFAULT_TOL).unwrap_err(),"NUMERIC_POSITIVE_SUPPORT_LOSS");
    }

    #[test]
    fn native_gl8_birth_plus_minus_point_three() {
        let positive = [0.1834346424956498_f64,0.5255324099163290,0.7966664774136267,0.9602898564975363];
        let weights = [0.3626837833783620_f64,0.3137066458778873,0.2223810344533745,0.1012285362903763];
        for b in [-0.3_f64,0.3] {
            let mut mu=Vec::new();let mut q=Vec::new();
            for i in (0..4).rev() {
                let m=-positive[i];
                let r=((2.0*b).exp()*(1.0-m*m)+(-4.0*b).exp()*m*m).sqrt();
                mu.push(m*(-2.0*b).exp()/r);q.push(weights[i]/r.powi(3));
            }
            for i in 0..4 {
                let m=positive[i];
                let r=((2.0*b).exp()*(1.0-m*m)+(-4.0*b).exp()*m*m).sqrt();
                mu.push(m*(-2.0*b).exp()/r);q.push(weights[i]/r.powi(3));
            }
            let r=project(&mu,&q,DEFAULT_TOL).unwrap();
            assert!(r.residuals.iter().all(|m|m.abs()<=DEFAULT_TOL));
            assert!(r.weights.iter().all(|w|*w>0.0));
        }
    }
}
