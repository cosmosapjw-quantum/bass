//! Opt-in, source-bound BASS point table. The CSV is an immutable producer input.
//! Cubic Hermite interpolation uses the producer's local tangent columns.
use crate::axbi_background::{BackgroundIncrement, BackgroundPoint};
use crate::interval_math::Interval;
use crate::ForwardError;
use std::{
    fs,
    io::Write,
    path::Path,
    process::{Command, Stdio},
};

fn bad(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}

pub fn sha256_bytes(bytes: &[u8]) -> Result<String, ForwardError> {
    let mut child = Command::new("sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .map_err(|_| bad("BASS_SHA_TOOL"))?;
    child
        .stdin
        .take()
        .ok_or(bad("BASS_SHA_STDIN"))?
        .write_all(bytes)
        .map_err(|_| bad("BASS_SHA_STDIN"))?;
    let output = child.wait_with_output().map_err(|_| bad("BASS_SHA_TOOL"))?;
    if !output.status.success() {
        return Err(bad("BASS_SHA_TOOL"));
    }
    let digest = String::from_utf8(output.stdout).map_err(|_| bad("BASS_SHA_TOOL"))?;
    Ok(digest[..64].to_owned())
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BassSourceIdentity {
    pub producer_commit: String,
    pub source_csv_sha256: String,
    pub source_manifest_sha256: String,
    pub case: String,
    pub grid_points: usize,
}
#[derive(Clone, Copy, Debug)]
struct Row {
    x: f64,
    a: f64,
    t: f64,
    b: f64,
    h: f64,
    s: f64,
    hf: f64,
    dhdx: f64,
}

#[derive(Clone, Debug)]
pub struct BassBackground {
    pub identity: BassSourceIdentity,
    rows: Vec<Row>,
    pub max_hamiltonian_normalized: f64,
    pub max_raychaudhuri_normalized: f64,
    pub max_producer_clock_relative: f64,
}
/// Typed result of the sufficient all-segment certificate. Failure is not a
/// physical nonmonotonicity claim: uncertain enclosures fail closed.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BassMonotonicityStatus {
    Established,
    MonotonicityNotEstablished,
}
impl BassMonotonicityStatus {
    pub fn code(self) -> &'static str {
        match self {
            Self::Established => "MONOTONICITY_ESTABLISHED",
            Self::MonotonicityNotEstablished => "MONOTONICITY_NOT_ESTABLISHED",
        }
    }
}
#[derive(Clone, Debug)]
pub struct BassDerivativeEnclosure {
    /// x0,x1,b0,b1,s0,H0,s1,H1; retained even for invalid input.
    pub inputs: [f64; 8],
    pub controls: [Option<Interval>; 3],
    pub status: BassMonotonicityStatus,
}
/// Enclose the three quadratic Bernstein controls of the existing Hermite b'.
/// No sampling, fitting, tolerance, or interpolation coefficient is changed.
pub fn enclose_hermite_derivative(inputs: [f64; 8]) -> BassDerivativeEnclosure {
    let mut out = BassDerivativeEnclosure {
        inputs,
        controls: [None; 3],
        status: BassMonotonicityStatus::MonotonicityNotEstablished,
    };
    let [x0, x1, b0, b1, s0, h0, s1, h1] = inputs;
    let compute = || -> crate::interval_math::Result<[Interval; 3]> {
        let point = Interval::point;
        if !inputs.iter().all(|v| v.is_finite()) || x1 <= x0 || h0 <= 0.0 || h1 <= 0.0 {
            return Err(crate::interval_math::IntervalError);
        }
        let dx = point(x1)?.sub(&point(x0)?)?;
        let d0 = point(s0)?.div(&point(h0)?)?;
        let d1 = point(s1)?.div(&point(h1)?)?;
        let middle = point(3.0)?
            .mul(&point(b1)?.sub(&point(b0)?)?)?
            .div(&dx)?
            .sub(&d0)?
            .sub(&d1)?;
        Ok([d0, middle, d1])
    };
    if let Ok(controls) = compute() {
        out.controls = controls.map(Some);
        if controls.iter().all(|v| v.lo > -0.5 && v.hi < 1.0) {
            out.status = BassMonotonicityStatus::Established;
        }
    }
    out
}
#[derive(Clone, Debug)]
pub struct BassMonotonicityReport {
    pub identity: BassSourceIdentity,
    pub status: BassMonotonicityStatus,
    pub reason: &'static str,
    /// One enclosure per consecutive table pair; all raw inputs retained.
    pub segments: Vec<BassDerivativeEnclosure>,
}

fn integrate_clock(l: Row, r: Row, to_x: f64) -> f64 {
    if to_x == l.x {
        return 0.0;
    }
    let width = to_x - l.x;
    let span = r.x - l.x;
    let h_at = |x: f64| {
        let u = (x - l.x) / span;
        let y0 = l.h.ln();
        let y1 = r.h.ln();
        let d0 = l.dhdx / l.h;
        let d1 = r.dhdx / r.h;
        ((2.0 * u * u * u - 3.0 * u * u + 1.0) * y0
            + (u * u * u - 2.0 * u * u + u) * span * d0
            + (-2.0 * u * u * u + 3.0 * u * u) * y1
            + (u * u * u - u * u) * span * d1)
            .exp()
    };
    const GL8: [(f64, f64); 4] = [
        (0.1834346424956498, 0.3626837833783620),
        (0.5255324099163290, 0.3137066458778873),
        (0.7966664774136267, 0.2223810344533745),
        (0.9602898564975363, 0.1012285362903763),
    ];
    let half = width / 2.0;
    let mid = l.x + half;
    GL8.iter()
        .map(|&(node, weight)| {
            weight * half * (1.0 / h_at(mid - half * node) + 1.0 / h_at(mid + half * node))
        })
        .sum()
}
impl BassBackground {
    pub fn from_files(
        csv: &Path,
        manifest: &Path,
        identity: BassSourceIdentity,
    ) -> Result<Self, ForwardError> {
        for digest in [
            &identity.source_csv_sha256,
            &identity.source_manifest_sha256,
        ] {
            if digest.len() != 64 || !digest.bytes().all(|b| b.is_ascii_hexdigit()) {
                return Err(bad("BASS_SOURCE_HASH_FORMAT"));
            }
        }
        if identity.producer_commit.len() != 40
            || identity.case.is_empty()
            || identity.case.contains('\n')
            || identity.case.contains('\r')
            || identity.case.contains('|')
        {
            return Err(bad("BASS_SOURCE_IDENTITY"));
        }
        let csv_bytes = fs::read(csv).map_err(|_| bad("BASS_SOURCE_CSV_IO"))?;
        let manifest_bytes = fs::read(manifest).map_err(|_| bad("BASS_SOURCE_MANIFEST_IO"))?;
        if sha256_bytes(&csv_bytes)? != identity.source_csv_sha256 {
            return Err(bad("BASS_SOURCE_CSV_SHA256"));
        }
        if sha256_bytes(&manifest_bytes)? != identity.source_manifest_sha256 {
            return Err(bad("BASS_SOURCE_MANIFEST_SHA256"));
        }
        let manifest_text =
            std::str::from_utf8(&manifest_bytes).map_err(|_| bad("BASS_SOURCE_MANIFEST_UTF8"))?;
        if !manifest_text.contains("bass.rei.proposed_background_point_tangent.v1")
            || !manifest_text.contains(&format!(
                "\"csv_sha256\": \"{}\"",
                identity.source_csv_sha256
            ))
        {
            return Err(bad("BASS_SOURCE_MANIFEST_CONTRACT"));
        }
        let data = std::str::from_utf8(&csv_bytes).map_err(|_| bad("BASS_SOURCE_CSV_UTF8"))?;
        let mut lines = data.lines();
        let header = lines.next().ok_or(bad("BASS_SOURCE_HEADER"))?;
        let columns = header.split(',').collect::<Vec<_>>();
        let column = |name: &str| {
            columns
                .iter()
                .position(|c| *c == name)
                .ok_or(bad("BASS_SOURCE_HEADER"))
        };
        let names = [
            "case",
            "x",
            "a",
            "proper_elapsed_s",
            "b",
            "H_mean_per_s",
            "s_per_s",
            "H_cold_FLRW_reference_per_s",
            "dH_dln_a_per_s",
            "signed_s_over_H",
            "Sigma",
        ];
        let ix = names
            .iter()
            .map(|n| column(n))
            .collect::<Result<Vec<_>, _>>()?;
        let rhoi = column("massive_rho_norm")?;
        let pi = column("massive_pbar_norm")?;
        let mut rows: Vec<Row> = Vec::new();
        let mut max_hamiltonian_normalized = 0.0_f64;
        let mut max_raychaudhuri_normalized = 0.0_f64;
        let fm = if identity.case == "COLD_FLRW" {
            0.0
        } else {
            0.1
        };
        for line in lines {
            let parts = line.split(',').collect::<Vec<_>>();
            if parts.len() != columns.len() {
                return Err(bad("BASS_SOURCE_CSV_SHAPE"));
            }
            if parts[ix[0]] != identity.case {
                continue;
            }
            let num = |j: usize| -> Result<f64, ForwardError> {
                let v = parts[ix[j]]
                    .parse::<f64>()
                    .map_err(|_| bad("BASS_SOURCE_CSV_NUMBER"))?;
                if !v.is_finite() {
                    return Err(bad("BASS_SOURCE_CSV_NUMBER"));
                }
                Ok(v)
            };
            let row = Row {
                x: num(1)?,
                a: num(2)?,
                t: num(3)?,
                b: num(4)?,
                h: num(5)?,
                s: num(6)?,
                hf: num(7)?,
                dhdx: num(8)?,
            };
            let rho = parts[rhoi]
                .parse::<f64>()
                .map_err(|_| bad("BASS_SOURCE_CSV_NUMBER"))?;
            let pressure = parts[pi]
                .parse::<f64>()
                .map_err(|_| bad("BASS_SOURCE_CSV_NUMBER"))?;
            if !rho.is_finite()
                || !pressure.is_finite()
                || rho < 0.0
                || pressure < 0.0
                || pressure > rho / 3.0 + 1e-19
            {
                return Err(bad("BASS_KINETIC_PRESSURE"));
            }
            let signed = num(9)?;
            let sigma = num(10)?;
            if row.h <= 0.0
                || row.a <= 0.0
                || (signed - row.s / row.h).abs() > 2e-12
                || (sigma - 3.0_f64.sqrt() * signed.abs()).abs() > 2e-12
            {
                return Err(bad("BASS_SIGNED_SHEAR"));
            }
            let h0 = 2.1842852410855026e-18_f64;
            let om = 0.315_f64;
            let orad = 0.000092_f64;
            let ol = 0.6849080000000001_f64;
            let expected_h2 =
                h0 * h0 * (om * (1.0 - fm) / row.a.powi(3) + orad / row.a.powi(4) + ol + rho)
                    + row.s * row.s;
            let observed_h2 = row.h * row.h;
            let he = (observed_h2 - expected_h2).abs() / observed_h2.abs().max(expected_h2.abs());
            max_hamiltonian_normalized = max_hamiltonian_normalized.max(he);
            if he > 3e-12 {
                return Err(bad("BASS_HAMILTONIAN"));
            }
            let hp = (h0
                * h0
                * (-3.0 * om * (1.0 - fm) / row.a.powi(3)
                    - 4.0 * orad / row.a.powi(4)
                    - 3.0 * (rho + pressure))
                - 6.0 * row.s * row.s)
                / (2.0 * row.h);
            let re = (row.dhdx - hp).abs() / hp.abs().max(1e-300);
            max_raychaudhuri_normalized = max_raychaudhuri_normalized.max(re);
            if (row.dhdx - hp).abs() > 1e-26 + 3e-12 * hp.abs() {
                return Err(bad("BASS_RAYCHAUDHURI"));
            }
            if let Some(prev) = rows.last().copied() {
                if !(row.x > prev.x && row.a > prev.a && row.t > prev.t) {
                    return Err(bad("BASS_PROPER_TIME_MONOTONIC"));
                }
                if ((row.a / prev.a).ln() - (row.x - prev.x)).abs() > 2e-12 {
                    return Err(bad("BASS_SCALE_HISTORY"));
                }
            }
            rows.push(row);
        }
        if rows.len() != identity.grid_points || rows.len() < 2 {
            return Err(bad("BASS_GRID_POINTS_OR_CASE"));
        }
        let first = rows[0];
        if first.x.abs() > 1e-14 || first.t.abs() > 1e-8 || (first.a - 1.0 / 21.0).abs() > 1e-14 {
            return Err(bad("BASS_TIME_ORIGIN"));
        }
        let mut max_producer_clock_relative = 0.0_f64;
        let mut proper_time = 0.0;
        for i in 1..rows.len() {
            proper_time += integrate_clock(rows[i - 1], rows[i], rows[i].x);
            max_producer_clock_relative = max_producer_clock_relative
                .max((rows[i].t - proper_time).abs() / rows[i].t.abs().max(1.0));
            rows[i].t = proper_time;
        }
        Ok(Self {
            identity,
            rows,
            max_hamiltonian_normalized,
            max_raychaudhuri_normalized,
            max_producer_clock_relative,
        })
    }
    fn interpolate(&self, x: f64) -> Result<BackgroundPoint, ForwardError> {
        if !x.is_finite() {
            return Err(bad("BASS_POINT_DOMAIN"));
        }
        let rows = &self.rows;
        if x < rows[0].x - 1e-14 || x > rows[rows.len() - 1].x + 1e-14 {
            return Err(bad("BASS_POINT_DOMAIN"));
        }
        let k = rows.partition_point(|r| r.x < x).clamp(1, rows.len() - 1);
        let (l, r) = (rows[k - 1], rows[k]);
        if x == l.x {
            return Ok(Self::point(l));
        }
        if x == r.x {
            return Ok(Self::point(r));
        }
        let dx = r.x - l.x;
        let u = (x - l.x) / dx;
        let hermite = |y0: f64, y1: f64, d0: f64, d1: f64| {
            (2.0 * u * u * u - 3.0 * u * u + 1.0) * y0
                + (u * u * u - 2.0 * u * u + u) * dx * d0
                + (-2.0 * u * u * u + 3.0 * u * u) * y1
                + (u * u * u - u * u) * dx * d1
        };
        let h = hermite(l.h.ln(), r.h.ln(), l.dhdx / l.h, r.dhdx / r.h).exp();
        let b = hermite(l.b, r.b, l.s / l.h, r.s / r.h);
        let deriv = |y0: f64, y1: f64, d0: f64, d1: f64| {
            ((6.0 * u * u - 6.0 * u) * y0
                + (3.0 * u * u - 4.0 * u + 1.0) * dx * d0
                + (-6.0 * u * u + 6.0 * u) * y1
                + (3.0 * u * u - 2.0 * u) * dx * d1)
                / dx
        };
        let s = h * deriv(l.b, r.b, l.s / l.h, r.s / r.h);
        let t = l.t + integrate_clock(l, r, x);
        if h <= 0.0 || !t.is_finite() || !b.is_finite() || !s.is_finite() {
            return Err(bad("BASS_INTERPOLATION"));
        }
        Ok(BackgroundPoint {
            a: rows[0].a * x.exp(),
            b,
            time_s: t,
            h_flrw_per_s: l.hf + (r.hf - l.hf) * u,
            h_per_s: h,
            s_per_s: s,
            sigma: s / h,
        })
    }
    fn point(r: Row) -> BackgroundPoint {
        BackgroundPoint {
            a: r.a,
            b: r.b,
            time_s: r.t,
            h_flrw_per_s: r.hf,
            h_per_s: r.h,
            s_per_s: r.s,
            sigma: r.s / r.h,
        }
    }
    pub fn point_at_scale(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {
        if !a.is_finite() || a < self.rows[0].a || a > self.rows.last().unwrap().a {
            return Err(bad("BASS_POINT_DOMAIN"));
        }
        let x = (a / self.rows[0].a).ln();
        self.interpolate(x)
    }
    pub fn point_at_time(&self, t: f64) -> Result<BackgroundPoint, ForwardError> {
        if !t.is_finite() || t < 0.0 || t > self.rows.last().unwrap().t {
            return Err(bad("BASS_TIME_DOMAIN"));
        }
        if t == 0.0 {
            return Ok(Self::point(self.rows[0]));
        }
        if t == self.rows.last().unwrap().t {
            return Ok(Self::point(*self.rows.last().unwrap()));
        }
        let mut lo = self.rows[0].x;
        let mut hi = self.rows.last().unwrap().x;
        for _ in 0..70 {
            let mid = (lo + hi) / 2.0;
            if self.interpolate(mid)?.time_s < t {
                lo = mid
            } else {
                hi = mid
            }
        }
        self.interpolate((lo + hi) / 2.0)
    }
    pub fn interval_increment(
        &self,
        a0: f64,
        a1: f64,
    ) -> Result<BackgroundIncrement, ForwardError> {
        if a1 < a0 {
            return Err(bad("BASS_INTERVAL_DOMAIN"));
        }
        let p0 = self.point_at_scale(a0)?;
        let p1 = self.point_at_scale(a1)?;
        let proper = p1.time_s - p0.time_s;
        let delta_b = p1.b - p0.b;
        if proper < 0.0 {
            return Err(bad("BASS_INTERVAL_CLOCK"));
        }
        let x0 = (a0 / self.rows[0].a).ln();
        let x1 = (a1 / self.rows[0].a).ln();
        const GL4: [(f64, f64); 2] = [
            (0.3399810435848563, 0.6521451548625461),
            (0.8611363115940526, 0.3478548451374538),
        ];
        let (mut t4, mut b4) = (0.0, 0.0);
        for pair in self.rows.windows(2) {
            let start = x0.max(pair[0].x);
            let end = x1.min(pair[1].x);
            if end <= start {
                continue;
            }
            let half = (end - start) / 2.0;
            let mid = (start + end) / 2.0;
            for &(node, weight) in &GL4 {
                for sign in [-1.0, 1.0] {
                    let p = self.interpolate(mid + sign * half * node)?;
                    t4 += weight * half / p.h_per_s;
                    b4 += weight * half * p.sigma;
                }
            }
        }
        Ok(BackgroundIncrement {
            proper_time_s: proper,
            delta_b,
            gl4_time_difference_s: t4 - proper,
            gl4_b_difference: b4 - delta_b,
        })
    }
    /// The source008 passive extension is deliberately limited to these exact
    /// selected model/table/case identities. Other BASS use retains mode=false.
    pub fn passive_monotonicity(&self) -> BassMonotonicityReport {
        let selected = self.identity.producer_commit == "3c39bbbf46b6663e7c40277e194fd0ef48118472"
            && self.identity.source_csv_sha256
                == "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133"
            && self.identity.source_manifest_sha256
                == "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed"
            && self.identity.grid_points == 121
            && self.rows.len() == 121
            && matches!(self.identity.case.as_str(), "COLD_FLRW" | "SIGNED_MINUS");
        let segments = self
            .rows
            .windows(2)
            .map(|pair| {
                let (l, r) = (pair[0], pair[1]);
                enclose_hermite_derivative([l.x, r.x, l.b, r.b, l.s, l.h, r.s, r.h])
            })
            .collect::<Vec<_>>();
        let established = selected
            && segments
                .iter()
                .all(|s| s.status == BassMonotonicityStatus::Established);
        BassMonotonicityReport {
            identity: self.identity.clone(),
            status: if established {
                BassMonotonicityStatus::Established
            } else {
                BassMonotonicityStatus::MonotonicityNotEstablished
            },
            reason: if !selected {
                "NONSELECTED_SOURCE_IDENTITY"
            } else if !established {
                "CONTROL_ENCLOSURE_NOT_STRICTLY_INSIDE_MINUS_HALF_TO_ONE"
            } else {
                "ALL_SEGMENTS_STRICT_BERNSTEIN_ENCLOSURE"
            },
            segments,
        }
    }
    pub fn grid_points(&self) -> usize {
        self.rows.len()
    }
}
