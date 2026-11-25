//! R118-C2C: positive reciprocal source-event graph and conditional
//! frequency transport. Each graph edge is an integrated conductance,
//! not a signed harmonic moment. No negative-kernel clipping.
use std::{
    fs::File,
    io::{BufReader, Read},
    path::Path,
};
const H: f64 = 6.62607015e-34;
#[derive(Clone, Debug)]
pub struct Mode {
    pub g: f64,
    pub pi: f64,
    pub p: f64,
}
#[derive(Clone, Debug)]
pub struct Block {
    pub i: usize,
    pub j: usize,
    pub w: Vec<f64>,
}
#[derive(Clone, Debug)]
pub struct Graph {
    pub modes: Vec<Mode>,
    pub directions: Vec<[f64; 3]>,
    pub weights: Vec<f64>,
    pub blocks: Vec<Block>,
}
#[derive(Clone, Debug)]
pub struct Action {
    pub rate: Vec<f64>,
    pub number_defect: f64,
    pub free_derivative: f64,
    pub q: [f64; 4],
    pub event_q: [f64; 4],
    pub force_defect: f64,
}
#[derive(Clone, Debug)]
pub struct Step {
    pub mass: Vec<f64>,
    pub number_defect: f64,
    pub q: [f64; 4],
    pub event_q: [f64; 4],
    pub force_defect: f64,
    pub free_change: f64,
}
fn valid_pos(x: f64) -> bool {
    x.is_finite() && x > 0.
}
fn valid_mass(x: f64) -> bool {
    x.is_finite() && x >= 0.
}
fn sum(x: &[f64]) -> f64 {
    let mut s = 0.;
    let mut c = 0.;
    for v in x {
        let y = v - c;
        let t = s + y;
        c = (t - s) - y;
        s = t;
    }
    s
}
/// Exact autonomous two-node Bose exchange. Represent the fraction
/// r=M_i/(M_i+M_j) as the projectivization of a positive 2x2 linear
/// flow with diagonals a*(1+u), b*(1+v), offdiagonals a,b.
/// Shift the larger eigenvalue before exponentiation. No clipping.
pub fn pair_exact(
    x: f64,
    y: f64,
    vi: f64,
    vj: f64,
    zi: f64,
    zj: f64,
    w: f64,
    dt: f64,
) -> Result<(f64, f64), String> {
    if ![x, y, w, dt].iter().all(|v| valid_mass(*v))
        || ![vi, vj, zi, zj].iter().all(|v| valid_pos(*v))
    {
        return Err("invalid positive pair".into());
    }
    pair_inner(x, y, vi, vj, zi, zj, w, dt)
}
fn pair_inner(
    x: f64,
    y: f64,
    vi: f64,
    vj: f64,
    zi: f64,
    zj: f64,
    w: f64,
    dt: f64,
) -> Result<(f64, f64), String> {
    if w == 0. || dt == 0. || x == 0. && y == 0. {
        return Ok((x, y));
    }
    let m = x + y;
    let r = x / m;
    let s = y / m;
    let u = m / vi;
    let v = m / vj;
    let aa = w / (vj * zj);
    let bb = w / (vi * zi);
    let scale = aa.max(bb);
    if scale == 0. {
        return Ok((x, y));
    }
    let a = aa / scale;
    let b = bb / scale;
    let f = a * s * (1. + x / vi) - b * r * (1. + y / vj);
    if f == 0. {
        return Ok((x, y));
    }
    let d = a * (1. + u) - b * (1. + v);
    let lam = d.hypot(2. * a.sqrt() * b.sqrt());
    if !valid_pos(lam) {
        return Err("invalid Bose pair eigenvalue".into());
    }
    let alpha = -(-lam * (dt * scale)).exp_m1();
    let e = (-lam * (dt * scale)).exp();
    // Stable small diagonal component of Perron spectral projector.
    let (p00, p11) = if d >= 0. {
        let k = 2. * a * b / (lam * (lam + d));
        (1. - k, k)
    } else {
        let k = 2. * a * b / (lam * (lam - d));
        (k, 1. - k)
    };
    let xx = e * r + alpha * (p00 * r + a / lam * s);
    let yy = e * s + alpha * (b / lam * r + p11 * s);
    let den = xx + yy;
    if !valid_pos(den) || !valid_mass(xx) || !valid_mass(yy) {
        return Err("invalid projective Bose pair map".into());
    }
    // Cancellation-free increment for weak edges. Use positive
    // projective outputs if one side is nearly exhausted.
    let delta = m * (alpha * (f / lam) / den);
    let (nx, ny) = if x + delta >= 0.
        && y - delta >= 0.
        && delta.abs() <= 0.9 * x.max(y)
        && x + delta > 1e-12 * m
        && y - delta > 1e-12 * m
    {
        (x + delta, y - delta)
    } else {
        (m * (xx / den), m * (yy / den))
    };
    if !valid_mass(nx) || !valid_mass(ny) {
        return Err("nonpositive Bose pair result".into());
    }
    Ok((nx, ny))
}
impl Graph {
    pub fn new(
        modes: Vec<Mode>,
        directions: Vec<[f64; 3]>,
        weights: Vec<f64>,
        blocks: Vec<Block>,
    ) -> Result<Self, String> {
        let n = modes.len();
        let a = weights.len();
        if n == 0
            || n > 128
            || a == 0
            || a > 1024
            || directions.len() != a
            || !weights.iter().all(|x| valid_pos(*x))
            || (sum(&weights) - 1.).abs() > 1e-12
            || modes
                .iter()
                .any(|m| !valid_pos(m.g) || !valid_pos(m.pi) || !valid_pos(m.p))
            || directions.iter().any(|v| {
                !v.iter().all(|x| x.is_finite())
                    || (v.iter().map(|x| x * x).sum::<f64>() - 1.).abs() > 1e-12
            })
        {
            return Err("invalid event graph measure".into());
        }
        let mut seen = vec![false; n * n];
        for b in &blocks {
            if b.i >= n
                || b.j >= n
                || b.i > b.j
                || b.w.len() != a * a
                || seen[b.i * n + b.j]
                || b.w.iter().any(|x| !valid_mass(*x))
            {
                return Err("invalid event graph block".into());
            }
            seen[b.i * n + b.j] = true;
            for k in 0..a {
                if b.i == b.j && b.w[k * a + k] != 0. {
                    return Err("same-node event diagonal".into());
                }
                for l in 0..a {
                    if b.w[k * a + l] != b.w[l * a + k] {
                        return Err("nonreciprocal event block".into());
                    }
                }
            }
        }
        Ok(Self {
            modes,
            directions,
            weights,
            blocks,
        })
    }
    pub fn load(path: &Path) -> Result<Self, String> {
        let mut f = BufReader::new(File::open(path).map_err(|e| e.to_string())?);
        fn bytes<const N: usize>(f: &mut impl Read) -> Result<[u8; N], String> {
            let mut a = [0; N];
            f.read_exact(&mut a).map_err(|e| e.to_string())?;
            Ok(a)
        }
        fn u(f: &mut impl Read) -> Result<usize, String> {
            Ok(u32::from_le_bytes(bytes::<4>(f)?) as usize)
        }
        fn v(f: &mut impl Read) -> Result<f64, String> {
            Ok(f64::from_le_bytes(bytes::<8>(f)?))
        }
        if &bytes::<8>(&mut f)? != b"RECPOS01" {
            return Err("invalid event graph schema".into());
        }
        let n = u(&mut f)?;
        let a = u(&mut f)?;
        let b = u(&mut f)?;
        if n == 0 || n > 128 || a == 0 || a > 1024 || b > n * (n + 1) / 2 || b * a * a > 160_000_000
        {
            return Err("event graph allocation exceeds cap".into());
        }
        let mut dirs = Vec::with_capacity(a);
        let mut weights = Vec::with_capacity(a);
        for _ in 0..a {
            dirs.push([v(&mut f)?, v(&mut f)?, v(&mut f)?]);
            weights.push(v(&mut f)?);
        }
        let mut modes = vec![];
        for _ in 0..n {
            modes.push(Mode {
                g: v(&mut f)?,
                pi: v(&mut f)?,
                p: v(&mut f)?,
            });
        }
        let mut blocks = Vec::with_capacity(b);
        for _ in 0..b {
            let i = u(&mut f)?;
            let j = u(&mut f)?;
            let mut w = Vec::with_capacity(a * a);
            let mut raw = vec![0u8; a * a * 8];
            f.read_exact(&mut raw).map_err(|e| e.to_string())?;
            for chunk in raw.chunks_exact(8) {
                w.push(f64::from_le_bytes(chunk.try_into().unwrap()));
            }
            blocks.push(Block { i, j, w });
        }
        if f.read(&mut [0u8; 1]).map_err(|e| e.to_string())? != 0 {
            return Err("trailing event graph bytes".into());
        }
        Self::new(modes, dirs, weights, blocks)
    }
    pub fn angles(&self) -> usize {
        self.weights.len()
    }
    pub fn size(&self) -> usize {
        self.modes.len() * self.angles()
    }
    fn volume(&self, clock: &[f64]) -> Result<(Vec<f64>, Vec<f64>), String> {
        let a = self.angles();
        if clock.len() != a || clock.iter().any(|x| !valid_pos(*x)) {
            return Err("invalid normal/material clock".into());
        }
        let mut v = Vec::with_capacity(self.size());
        let mut z = Vec::with_capacity(self.size());
        for m in &self.modes {
            for k in 0..a {
                v.push(m.g * self.weights[k] / clock[k]);
                z.push(m.pi / m.g);
            }
        }
        Ok((v, z))
    }
    pub fn to_mass(&self, f: &[f64], clock: &[f64]) -> Result<Vec<f64>, String> {
        if f.len() != self.size() || f.iter().any(|x| !valid_mass(*x)) {
            return Err("invalid occupation".into());
        }
        let (v, _) = self.volume(clock)?;
        Ok(v.iter().zip(f).map(|(v, f)| v * f).collect())
    }
    pub fn to_occupation(&self, m: &[f64], clock: &[f64]) -> Result<Vec<f64>, String> {
        if m.len() != self.size() || m.iter().any(|x| !valid_mass(*x)) {
            return Err("invalid mass".into());
        }
        let (v, _) = self.volume(clock)?;
        Ok(m.iter().zip(v).map(|(m, v)| m / v).collect())
    }
    /// Direct material tetrad momentum on the normal hypersurface when
    /// clock=D. Photon four-momentum in the frozen atom frame per photon.
    fn momentum(&self, k: usize) -> [f64; 4] {
        let a = self.angles();
        let p = self.modes[k / a].p;
        let e = self.directions[k % a];
        [p, p * e[0], p * e[1], p * e[2]]
    }
    fn free(&self, m: &[f64], v: &[f64], z: &[f64]) -> f64 {
        let mut t = 0.;
        for k in 0..m.len() {
            let f = m[k] / v[k];
            if f > 0. {
                t += m[k] * (f.ln() - z[k].ln()) - (v[k] + m[k]) * f.ln_1p();
            }
        }
        t
    }
    fn for_edges(
        &self,
        reverse: bool,
        mut fun: impl FnMut(usize, usize, f64) -> Result<(), String>,
    ) -> Result<(), String> {
        let a = self.angles();
        for k in 0..self.blocks.len() {
            let b = &self.blocks[if reverse {
                self.blocks.len() - 1 - k
            } else {
                k
            }];
            for u in 0..a {
                let i = if reverse { a - 1 - u } else { u };
                for v in 0..a {
                    let j = if reverse { a - 1 - v } else { v };
                    if b.i == b.j && i >= j {
                        continue;
                    }
                    let w = b.w[i * a + j];
                    if w != 0. {
                        fun(b.i * a + i, b.j * a + j, w)?;
                    }
                }
            }
        }
        Ok(())
    }
    pub fn action(&self, m: &[f64], clock: &[f64]) -> Result<Action, String> {
        let f = self.to_occupation(m, clock)?;
        let (_, z) = self.volume(clock)?;
        let phi: Vec<_> = f.iter().zip(&z).map(|(x, z)| x / (z * (1. + x))).collect();
        let mut rate = vec![0.; m.len()];
        let mut q = [0.; 4];
        let mut gross = 0.;
        let mut ent = 0.;
        let mut scale = 0.;
        self.for_edges(false, |i, j, w| {
            let t = w * (1. + f[i]) * (1. + f[j]) * (phi[j] - phi[i]);
            rate[i] += t;
            rate[j] -= t;
            gross += t.abs() * 2.;
            let p = self.momentum(i);
            let r = self.momentum(j);
            for k in 0..4 {
                q[k] += t * (p[k] - r[k]);
            }
            scale += t.abs() * (p[0] + r[0]);
            if t != 0. {
                ent += if phi[i] == 0. || phi[j] == 0. {
                    f64::NEG_INFINITY
                } else {
                    t * (phi[i].ln() - phi[j].ln())
                };
            }
            Ok(())
        })?;
        let mut direct = [0.; 4];
        for (i, t) in rate.iter().enumerate() {
            let p = self.momentum(i);
            for k in 0..4 {
                direct[k] += p[k] * t;
            }
        }
        let defect = direct
            .iter()
            .zip(q)
            .map(|(a, b)| (a - b).abs())
            .fold(0., f64::max)
            / scale.max(f64::MIN_POSITIVE);
        Ok(Action {
            number_defect: sum(&rate).abs() / gross.max(f64::MIN_POSITIVE),
            rate,
            free_derivative: ent,
            q: direct,
            event_q: q,
            force_defect: defect,
        })
    }
    /// Symmetric exact edge splitting: forward/reverse half sweeps.
    /// Second order for fixed finite graph; NOT a stiff-uniform method.
    pub fn step(&self, m: &[f64], clock: &[f64], dt: f64) -> Result<Step, String> {
        if !valid_mass(dt) || m.len() != self.size() || m.iter().any(|x| !valid_mass(*x)) {
            return Err("invalid event step".into());
        }
        let (v, z) = self.volume(clock)?;
        let mut y = m.to_vec();
        let mut q = [0.; 4];
        let mut scale = 0.;
        let before = self.free(m, &v, &z);
        for reverse in [false, true] {
            self.for_edges(reverse, |i, j, w| {
                let x = y[i];
                let t = y[j];
                let (a, b) = pair_inner(x, t, v[i], v[j], z[i], z[j], w, dt * 0.5)?;
                y[i] = a;
                y[j] = b;
                let di = a - x;
                let dj = b - t;
                let p = self.momentum(i);
                let r = self.momentum(j);
                // Signed event transfer from one endpoint; number defect
                // of the two computed endpoints is not silently corrected.
                let flux = (di - dj) * 0.5;
                for k in 0..4 {
                    q[k] += flux * (p[k] - r[k]);
                }
                scale += flux.abs() * (p[0] + r[0]);
                Ok(())
            })?;
        }
        let mut direct = [0.; 4];
        for i in 0..y.len() {
            let p = self.momentum(i);
            for k in 0..4 {
                direct[k] += (y[i] - m[i]) * p[k];
            }
        }
        let defect = direct
            .iter()
            .zip(q)
            .map(|(a, b)| (a - b).abs())
            .fold(0., f64::max)
            / scale
                .max(sum(m) * self.modes[0].p * f64::EPSILON)
                .max(f64::MIN_POSITIVE);
        Ok(Step {
            number_defect: (sum(&y) - sum(m)).abs() / sum(m).max(f64::MIN_POSITIVE),
            free_change: self.free(&y, &v, &z) - before,
            mass: y,
            q: direct,
            event_q: q,
            force_defect: defect,
        })
    }
}
#[derive(Clone, Debug)]
pub struct Transport {
    pub edges: Vec<f64>,
    pub nu0: f64,
    pub dnu: f64,
    red: f64,
    blue: f64,
}
#[derive(Clone, Debug)]
pub struct Drift {
    pub mass: Vec<f64>,
    pub escaped_mass: f64,
    pub escaped_energy: f64,
    pub work: f64,
    pub projection: f64,
    pub projection_core: f64,
    pub projection_exterior: f64,
    pub core_number_defect: f64,
    pub exterior_number_defect: f64,
    pub number_defect: f64,
    pub energy_defect: f64,
    pub red_in: f64,
    pub red_out: f64,
    pub blue_in: f64,
    pub blue_out: f64,
    pub red_face_energy: f64,
    pub blue_face_energy: f64,
    pub atom_energy: f64,
}
impl Transport {
    pub fn new(edges: Vec<f64>, nu0: f64, dnu: f64, red: f64, blue: f64) -> Result<Self, String> {
        if edges.len() < 4
            || edges.len() > 8193
            || !valid_pos(nu0)
            || !valid_pos(dnu)
            || edges.iter().any(|x| !x.is_finite() || nu0 + dnu * x <= 0.)
            || edges.windows(2).any(|x| x[0] >= x[1])
            || !edges.contains(&red)
            || !edges.contains(&blue)
            || red >= blue
            || red == edges[0]
            || blue == *edges.last().unwrap()
        {
            return Err("invalid frequency transport mesh".into());
        }
        Ok(Self {
            edges,
            nu0,
            dnu,
            red,
            blue,
        })
    }
    fn integrals(&self, l: f64, r: f64) -> (f64, f64) {
        if r <= l {
            return (0., 0.);
        }
        let b = self.dnu / self.nu0;
        let a = 1. + b * l;
        let z = 1. + b * r;
        let dx = r - l;
        (
            dx * (a * a + a * z + z * z) / 3.,
            dx * (a * a * a + a * a * z + a * z * z + z * z * z) / 4.,
        )
    }
    pub fn energy(&self, m: &[f64]) -> f64 {
        self.edges
            .windows(2)
            .zip(m)
            .map(|(x, m)| {
                let (v, e) = self.integrals(x[0], x[1]);
                m * H * self.nu0 * e / v
            })
            .sum()
    }
    /// Conditional advection in frequency only, fixed angular weights.
    /// Positive exact overlap of constant occupation in each donor cell.
    /// Full exterior reservoirs evolve; outermost boundary has zero inflow.
    /// Physical crossing packet carries face energy. Projection error is
    /// separate from geometric work and never assigned to atoms.
    pub fn shift(&self, m: &[f64], dz: f64) -> Result<Drift, String> {
        if m.len() + 1 != self.edges.len()
            || m.iter().any(|x| !valid_mass(*x))
            || !dz.is_finite()
            || dz.abs() > 0.1
        {
            return Err("invalid frequency shift".into());
        }
        let b = self.dnu / self.nu0;
        let a = dz.exp();
        let back = (-dz).exp_m1();
        let inv = |x: f64| x + back * (1. / b + x);
        let pre: Vec<_> = self.edges.iter().map(|x| inv(*x)).collect();
        let mut y = vec![0.; m.len()];
        let mut raw_cell_e = vec![0.; m.len()];
        let (mut esc, mut ee, mut eraw) = (0., 0., 0.);
        let (mut red_in, mut red_out, mut blue_in, mut blue_out) = (0., 0., 0., 0.);
        let e0 = self.energy(m);
        for (i, cell) in self.edges.windows(2).enumerate() {
            let l = cell[0];
            let r = cell[1];
            let (v, _) = self.integrals(l, r);
            if m[i] == 0. {
                continue;
            }
            let f = m[i] / v;
            let portion = |u: f64, v: f64| -> (f64, f64) {
                let (n, e) = self.integrals(l.max(u), r.min(v));
                (f * n, f * e * H * self.nu0 * a)
            };
            let (q, e) = portion(f64::NEG_INFINITY, pre[0]);
            esc += q;
            ee += e;
            let (q, e) = portion(*pre.last().unwrap(), f64::INFINITY);
            esc += q;
            ee += e;
            for j in 0..y.len() {
                let (q, e) = portion(pre[j], pre[j + 1]);
                y[j] += q;
                raw_cell_e[j] += e;
                eraw += e;
            }
            for (face, red) in [(self.red, true), (self.blue, false)] {
                let p = inv(face);
                if dz < 0. {
                    let (n, _) = portion(face, p);
                    if red {
                        red_out += n
                    } else {
                        blue_in += n
                    }
                } else if dz > 0. {
                    let (n, _) = portion(p, face);
                    if red {
                        red_in += n
                    } else {
                        blue_out += n
                    }
                }
            }
        }
        let work = e0 * dz.exp_m1();
        let red = self.edges.iter().position(|v| *v == self.red).unwrap();
        let blue = self.edges.iter().position(|v| *v == self.blue).unwrap();
        let mut projection_core = 0.;
        let mut projection_exterior = 0.;
        for j in 0..y.len() {
            let (v, e) = self.integrals(self.edges[j], self.edges[j + 1]);
            let defect = y[j] * H * self.nu0 * e / v - raw_cell_e[j];
            if (red..blue).contains(&j) {
                projection_core += defect;
            } else {
                projection_exterior += defect;
            }
        }
        let projection = projection_core + projection_exterior;
        let net = red_in + blue_in - red_out - blue_out;
        let core_change = sum(&y[red..blue]) - sum(&m[red..blue]);
        let ext_change = sum(&y[..red]) + sum(&y[blue..]) - sum(&m[..red]) - sum(&m[blue..]);
        let core_number_defect = (core_change - net).abs() / sum(m).max(f64::MIN_POSITIVE);
        let exterior_number_defect = (ext_change + net + esc).abs() / sum(m).max(f64::MIN_POSITIVE);
        let number_defect = (sum(&y) + esc - sum(m)).abs() / sum(m).max(f64::MIN_POSITIVE);
        let energy_defect = (eraw + ee - e0 - work).abs() / e0.max(f64::MIN_POSITIVE);
        if y.iter().any(|x| !valid_mass(*x))
            || ![number_defect, energy_defect, projection]
                .iter()
                .all(|x| x.is_finite())
        {
            return Err("nonfinite remap ledger".into());
        }
        Ok(Drift {
            mass: y,
            escaped_mass: esc,
            escaped_energy: ee,
            work,
            projection,
            projection_core,
            projection_exterior,
            core_number_defect,
            exterior_number_defect,
            number_defect,
            energy_defect,
            red_in,
            red_out,
            blue_in,
            blue_out,
            red_face_energy: H * (self.nu0 + self.dnu * self.red) * (red_in - red_out),
            blue_face_energy: H * (self.nu0 + self.dnu * self.blue) * (blue_in - blue_out),
            atom_energy: 0.,
        })
    }
}
