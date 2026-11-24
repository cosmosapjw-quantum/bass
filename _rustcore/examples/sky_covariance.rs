//! Actual finite-law population moments from BASS observer modes; stdout is TSV.
//!
//! cargo run --release --example sky_covariance -- \
//!   --member 1 a/modes.tsv --member 2 b/modes.tsv --pair 2 1 3 -2
//!
//! Use --all to stream every ordered mode pair (the output is O(L^4)).
//! With --pair only the selected coefficients are retained from each input.
//! An alternative --haar a/modes.tsv averages a single deterministic sky over
//! uniform SO(3) rotations exactly. The law is explicit in both modes.
use bianchi_rustcore::kinetic::sky_spectrum::{outer, Mode};
use std::{
    collections::{BTreeMap, BTreeSet},
    env,
    fs::File,
    io::{self, BufRead, BufReader, BufWriter, Write},
    path::{Path, PathBuf},
};

type Key = (usize, i32);
type Pair = (Key, Key);
type Sky = BTreeMap<Key, Mode>;
type Product = [[[f64; 2]; 3]; 3];
const FIELDS: [&str; 3] = ["T", "E", "B"];
const HEADER: [&str; 8] = ["ell", "m", "T_re", "T_im", "E_re", "E_im", "B_re", "B_im"];

#[derive(Default)]
struct Args {
    members: Vec<(f64, PathBuf)>,
    haar: Option<PathBuf>,
    pairs: BTreeSet<Pair>,
    all: bool,
}

fn key(l: &str, m: &str) -> Result<Key, String> {
    let l = l.parse::<usize>().map_err(|_| "invalid ell")?;
    let m = m.parse::<i32>().map_err(|_| "invalid m")?;
    if l > i32::MAX as usize || m.unsigned_abs() as usize > l {
        return Err("invalid (ell,m)".into());
    }
    Ok((l, m))
}

fn parse(tokens: impl IntoIterator<Item = String>) -> Result<Args, String> {
    let mut args = Args::default();
    let mut it = tokens.into_iter();
    while let Some(arg) = it.next() {
        let mut next = || {
            it.next()
                .ok_or_else(|| format!("missing argument for {arg}"))
        };
        match arg.as_str() {
            "--member" => {
                let w = next()?.parse::<f64>().map_err(|_| "invalid weight")?;
                if !w.is_finite() || w <= 0.0 {
                    return Err("weights must be finite and strictly positive".into());
                }
                args.members.push((w, next()?.into()));
            }
            "--haar" => {
                if args.haar.replace(next()?.into()).is_some() {
                    return Err("supply one Haar sky".into());
                }
            }
            "--pair" => {
                let left = key(&next()?, &next()?)?;
                let right = key(&next()?, &next()?)?;
                args.pairs.insert((left, right));
            }
            "--all" => args.all = true,
            _ => return Err(format!("unrecognized option {arg}")),
        }
    }
    if args.haar.is_some() == !args.members.is_empty() {
        return Err("select --haar SKY or one or more --member WEIGHT SKY".into());
    }
    if args.all == !args.pairs.is_empty() {
        return Err("select --all or --pair L M L2 M2 (repeatable)".into());
    }
    Ok(args)
}

fn read_sky(path: &Path, keep: impl Fn(Key) -> bool) -> Result<Sky, String> {
    let io_err = |e: io::Error| format!("{}: {e}", path.display());
    let mut lines = BufReader::new(File::open(path).map_err(io_err)?).lines();
    let header = lines.next().ok_or("empty mode table")?.map_err(io_err)?;
    let names: Vec<_> = header.split_whitespace().collect();
    if !names.starts_with(&HEADER) {
        return Err(format!("{}: incompatible T/E/B header", path.display()));
    }
    let mut sky = Sky::new();
    for (n, line) in lines.enumerate() {
        let line = line.map_err(io_err)?;
        if line.trim().is_empty() {
            continue;
        }
        let f: Vec<_> = line.split_whitespace().collect();
        if f.len() != names.len() {
            return Err(format!("{} line {}: column count", path.display(), n + 2));
        }
        let (ell, m) = key(f[0], f[1])?;
        if !keep((ell, m)) {
            continue;
        }
        let mut a = Mode {
            ell,
            m,
            alm: [[0.; 2]; 3],
        };
        for (v, s) in a.alm.iter_mut().flatten().zip(&f[2..8]) {
            *v = s
                .parse::<f64>()
                .map_err(|_| "non-numeric harmonic coefficient")?;
            if !v.is_finite() {
                return Err("nonfinite harmonic coefficient".into());
            }
        }
        if sky.insert((ell, m), a).is_some() {
            return Err(format!("duplicate retained ({ell},{m})"));
        }
    }
    if sky.is_empty() {
        return Err(format!("no selected coefficients in {}", path.display()));
    }
    Ok(sky)
}

fn zero((ell, m): Key) -> Mode {
    Mode {
        ell,
        m,
        alm: [[0.; 2]; 3],
    }
}

struct Moment {
    left: Mode,
    right: Mode,
    raw: Product,
    covariance: Product,
    weight: f64,
}

impl Moment {
    fn new((a, b): Pair) -> Self {
        Self {
            left: zero(a),
            right: zero(b),
            raw: [[[0.; 2]; 3]; 3],
            covariance: [[[0.; 2]; 3]; 3],
            weight: 0.,
        }
    }
    fn update(&mut self, a: &Mode, b: &Mode, w: f64) {
        let sum = self.weight + w;
        let old = self.weight / sum;
        let new = w / sum;
        let mut da = *a;
        let mut db = *b;
        for j in 0..3 {
            for u in 0..2 {
                da.alm[j][u] -= self.left.alm[j][u];
                db.alm[j][u] -= self.right.alm[j][u];
                self.left.alm[j][u] += new * da.alm[j][u];
                self.right.alm[j][u] += new * db.alm[j][u];
            }
        }
        let delta = outer(&da, &db);
        let product = outer(a, b);
        // Weighted Welford population co-moment; raw accumulates independently.
        for i in 0..3 {
            for j in 0..3 {
                for t in 0..2 {
                    self.covariance[i][j][t] =
                        old * self.covariance[i][j][t] + old * new * delta[i][j][t];
                    self.raw[i][j][t] = old * self.raw[i][j][t] + new * product[i][j][t];
                }
            }
        }
        self.weight = sum;
    }
}

fn haar(pair: Pair, sky: &Sky, cached: &mut BTreeMap<usize, Product>) -> Result<Moment, String> {
    let (a, b) = pair;
    let mut result = Moment::new(pair);
    result.weight = 1.;
    if a.0 == 0 {
        result.left = sky[&a];
    }
    if b.0 == 0 {
        result.right = sky[&b];
    }
    if a == b {
        let d = if let Some(d) = cached.get(&a.0) {
            *d
        } else {
            let mut d = [[[0.; 2]; 3]; 3];
            // Schur orthogonality of normalized Haar measure. Proper rotations
            // do not average over parity, so cross TB/EB may survive.
            for m in -(a.0 as i32)..=(a.0 as i32) {
                let row = sky
                    .get(&(a.0, m))
                    .ok_or("Haar average needs a complete multiplet")?;
                let v = outer(row, row);
                for (sum, x) in d
                    .iter_mut()
                    .flatten()
                    .flatten()
                    .zip(v.iter().flatten().flatten())
                {
                    *sum += x / (2 * a.0 + 1) as f64;
                }
            }
            cached.insert(a.0, d);
            d
        };
        result.raw = d;
        if a.0 > 0 {
            result.covariance = d;
        }
    }
    Ok(result)
}

fn emit(w: &mut impl Write, m: &Moment) -> Result<(), String> {
    let means = outer(&m.left, &m.right);
    for (i, x) in FIELDS.iter().enumerate() {
        for (j, y) in FIELDS.iter().enumerate() {
            let fields = [
                m.left.alm[i],
                m.right.alm[j],
                m.covariance[i][j],
                m.raw[i][j],
                means[i][j],
                std::array::from_fn(|k| m.raw[i][j][k] - m.covariance[i][j][k] - means[i][j][k]),
            ];
            if !fields.iter().flatten().all(|v| v.is_finite()) {
                return Err("nonfinite second moment".into());
            }
            write!(
                w,
                "{}\t{}\t{}\t{}\t{x}\t{y}",
                m.left.ell, m.left.m, m.right.ell, m.right.m
            )
            .map_err(|e| e.to_string())?;
            for v in fields.into_iter().flatten() {
                write!(w, "\t{v:.17e}").map_err(|e| e.to_string())?;
            }
            writeln!(w).map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

fn run(args: Args, w: &mut impl Write) -> Result<(), String> {
    let keys: BTreeSet<_> = args.pairs.iter().flat_map(|(a, b)| [*a, *b]).collect();
    let ells: BTreeSet<_> = keys.iter().map(|k| k.0).collect();
    let is_haar = args.haar.is_some();
    let keep = |k: Key| args.all || keys.contains(&k) || (is_haar && ells.contains(&k.0));
    let inputs: Vec<_> = match args.haar {
        Some(p) => vec![(1., p)],
        None => args.members,
    };
    let max_weight = inputs.iter().map(|p| p.0).fold(0., f64::max);
    let mut skies = Vec::new();
    for (w, path) in inputs {
        let weight = w / max_weight;
        if weight == 0.0 {
            return Err("weight ratio underflows f64".into());
        }
        skies.push((weight, read_sky(&path, keep)?));
    }
    let first = &skies[0].1;
    if args.all {
        let max_l = first.last_key_value().unwrap().0 .0;
        if (max_l + 1).checked_pow(2) != Some(first.len()) {
            return Err("--all needs complete signed m across 0..lmax".into());
        }
        if skies.iter().any(|(_, s)| s.keys().ne(first.keys())) {
            return Err("inconsistent ranges across mode tables".into());
        }
    } else if keys
        .iter()
        .any(|k| skies.iter().any(|(_, s)| !s.contains_key(k)))
    {
        return Err("specified mode absent from an input".into());
    }
    writeln!(w,"ell\tm\tell_prime\tm_prime\tX\tY\tmean_X_re\tmean_X_im\tmean_Y_re\tmean_Y_im\tcov_re\tcov_im\traw_re\traw_im\tmean_outer_re\tmean_outer_im\tclosure_re\tclosure_im").map_err(|e|e.to_string())?;
    let mut cache = BTreeMap::new();
    let mut process = |pair: Pair| -> Result<(), String> {
        let result = if is_haar {
            haar(pair, first, &mut cache)?
        } else {
            let mut result = Moment::new(pair);
            for (weight, sky) in &skies {
                result.update(&sky[&pair.0], &sky[&pair.1], *weight);
            }
            result
        };
        emit(w, &result)
    };
    if args.all {
        for &a in first.keys() {
            for &b in first.keys() {
                process((a, b))?;
            }
        }
    } else {
        for p in args.pairs {
            process(p)?;
        }
    }
    w.flush().map_err(|e| e.to_string())
}

fn main() -> Result<(), String> {
    let args = parse(env::args().skip(1))?;
    run(args, &mut BufWriter::new(io::stdout().lock()))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn row(key: Key, z: [f64; 2]) -> Mode {
        let mut a = zero(key);
        a.alm[0] = z;
        a.alm[1] = [-z[1], z[0]];
        a
    }
    fn close(a: [f64; 2], b: [f64; 2]) {
        for (x, y) in a.into_iter().zip(b) {
            assert!((x - y).abs() < 1e-13, "{x} {y}");
        }
    }
    #[test]
    fn unequal_weights_complex_population_and_centered_closure() {
        let p = ((2, 1), (3, -2));
        let mut r = Moment::new(p);
        let a = [row(p.0, [1., 2.]), row(p.0, [3., -1.])];
        let b = [row(p.1, [2., -1.]), row(p.1, [-1., 4.])];
        r.update(&a[0], &b[0], 1.);
        r.update(&a[1], &b[1], 3.);
        // Two-atom covariance is p(1-p)(a2-a1) conj(b2-b1).
        close(r.left.alm[0], [2.5, -0.25]);
        close(r.right.alm[0], [-0.25, 2.75]);
        close(r.covariance[0][0], [-21. * 3. / 16., -3. / 16.]);
        close(r.raw[0][0], [-5.25, -7.0]);
        let means = outer(&r.left, &r.right);
        for i in 0..3 {
            for j in 0..3 {
                close(
                    r.raw[i][j],
                    std::array::from_fn(|k| r.covariance[i][j][k] + means[i][j][k]),
                );
            }
        }
    }

    #[test]
    fn proper_rotation_average_schur_selection_monopole_and_cross() {
        let mut s = Sky::new();
        s.insert((0, 0), row((0, 0), [2., 0.]));
        for m in -1i32..=1 {
            let mut a = zero((1, m));
            a.alm[0] = [if m < 0 { -1. } else { 1. }, 0.];
            a.alm[2] = a.alm[0].map(|v| 2. * v);
            s.insert((1, m), a);
        }
        let mut cache = BTreeMap::new();
        let h = haar(((0, 0), (0, 0)), &s, &mut cache).unwrap();
        close(h.raw[0][0], [4., 0.]);
        close(h.covariance[0][0], [0., 0.]);
        let h = haar(((1, 0), (1, 0)), &s, &mut cache).unwrap();
        close(h.covariance[0][2], [2., 0.]);
        let h = haar(((1, 0), (1, 1)), &s, &mut cache).unwrap();
        close(h.raw[0][2], [0., 0.]);
        let h = haar(((0, 0), (1, 1)), &s, &mut cache).unwrap();
        close(h.raw[0][2], [0., 0.]);
    }

    #[test]
    fn invalid_laws_and_indices_fail() {
        let parse_str = |s: &str| parse(s.split_whitespace().map(str::to_string));
        assert!(parse_str("--member 0 a --all").is_err());
        assert!(parse_str("--member NaN a --all").is_err());
        assert!(parse_str("--member 1 a --haar b --all").is_err());
        assert!(parse_str("--member 1 a --pair 2 -3 1 0").is_err());
        assert!(parse_str("--member 1 a --all --pair 2 0 1 0").is_err());
        assert!(parse_str("--member 1 a --member 3 b --pair 2 -1 3 2").is_ok());
    }
}
