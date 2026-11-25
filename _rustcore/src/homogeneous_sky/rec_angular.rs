//! R118-C2B: native scalar operator for the pinned REC COM-KHW harmonic
//! conductances, not a polarized scattering matrix or a recalibrated kernel.
//! Angles use dOmega/(4*pi); f is occupation; g,pi in m^-3, pair in
//! m^-3 s^-1, same-cell eigenvalues in s^-1, p in kg m s^-1.
//! Retain finite harmonic release and signed moments without clipping.
use super::{boost, rec_bridge::material_expansion_factor, RayNode, V};
use nalgebra::{linalg::LU, DMatrix, DVector, Dyn};
const H_PLANCK: f64 = 6.62607015e-34;
const C: f64 = 299792458.;
#[derive(Clone, Debug)]
pub struct State {
    pub label: String,
    pub lo: f64,
    pub hi: f64,
    pub g: f64,
    pub pi: f64,
    pub p: f64,
}
#[derive(Clone, Debug)]
pub struct Network {
    pub states: Vec<State>,
    pub ell: usize,
    pair: Vec<f64>,
    same: Vec<f64>,
}
impl Network {
    pub fn new(
        states: Vec<State>,
        ell: usize,
        pair: Vec<f64>,
        same: Vec<f64>,
    ) -> Result<Self, String> {
        let n = states.len();
        if n < 2
            || n > 128
            || ell > 32
            || pair.len() != (ell + 1) * n * n
            || same.len() != (ell + 1) * n
            || states.iter().any(|s| {
                s.label.is_empty()
                    || ![s.lo, s.hi, s.g, s.pi, s.p].iter().all(|x| x.is_finite())
                    || s.lo >= s.hi
                    || s.g <= 0.
                    || s.pi <= 0.
                    || s.p <= 0.
            })
            || pair.iter().chain(&same).any(|x| !x.is_finite())
        {
            return Err("invalid REC source network".into());
        }
        let scale = pair
            .iter()
            .map(|v| v.abs())
            .fold(0., f64::max)
            .max(f64::MIN_POSITIVE);
        for i in 0..n {
            if same[i] != 0. || states[..i].iter().any(|s| s.label == states[i].label) {
                return Err("REC same-cell monopole or label mismatch".into());
            }
            for j in 0..n {
                if pair[i * n + j] < 0. {
                    return Err("negative REC pair monopole".into());
                }
                for l in 0..=ell {
                    if (pair[(l * n + i) * n + j] - pair[(l * n + j) * n + i]).abs() > 1e-12 * scale
                    {
                        return Err("asymmetric REC conductances".into());
                    }
                }
            }
        }
        Ok(Self {
            states,
            ell,
            pair,
            same,
        })
    }
    fn n(&self) -> usize {
        self.states.len()
    }
    fn z(&self, i: usize) -> f64 {
        self.states[i].pi / self.states[i].g
    }
    fn get(&self, l: usize, i: usize, j: usize, scope: Scope) -> f64 {
        let n = self.n();
        if i == j || self.pair[i * n + j] <= 0. {
            return 0.;
        }
        let a = self.states[i].label.starts_with('I');
        let b = self.states[j].label.starts_with('I');
        if scope == Scope::CoreExterior && a == b {
            return 0.;
        }
        self.pair[(l * n + i) * n + j]
    }
    fn same(&self, l: usize, i: usize, scope: Scope) -> f64 {
        if scope == Scope::Full {
            self.same[l * self.n() + i]
        } else {
            0.
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Scope {
    Full,
    CoreExterior,
}
#[derive(Clone, Debug)]
pub struct Grid {
    pub directions: Vec<[f64; 3]>,
    pub weights: Vec<f64>,
    pub ell: usize,
    pub gram_defect: f64,
    syn: DMatrix<f64>,
    ana: DMatrix<f64>,
    lm: Vec<usize>,
}
impl Grid {
    /// Independent real spherical harmonics, orthonormal under normalized
    /// sphere measure. Only harmonic-exact positive quadratures admitted.
    pub fn new(directions: Vec<[f64; 3]>, weights: Vec<f64>, ell: usize) -> Result<Self, String> {
        let na = directions.len();
        let nm = (ell + 1) * (ell + 1);
        if ell > 24
            || na < nm
            || na > 4096
            || weights.len() != na
            || weights.iter().any(|w| !w.is_finite() || *w <= 0.)
            || (weights.iter().sum::<f64>() - 1.).abs() > 1e-12
            || directions.iter().any(|e| {
                !e.iter().all(|x| x.is_finite())
                    || (e.iter().map(|x| x * x).sum::<f64>() - 1.).abs() > 1e-12
            })
        {
            return Err("invalid positive REC angular grid".into());
        }
        let mut syn = DMatrix::zeros(na, nm);
        let mut lm = vec![0; nm];
        for l in 0..=ell {
            for k in l * l..(l + 1) * (l + 1) {
                lm[k] = l;
            }
        }
        for (i, e) in directions.iter().enumerate() {
            let mu = e[2].clamp(-1., 1.);
            let phi = e[1].atan2(e[0]);
            let sin = (e[0] * e[0] + e[1] * e[1]).sqrt();
            let mut pmm = 1.;
            for m in 0..=ell {
                if m > 0 {
                    pmm *= -((2 * m - 1) as f64) * sin;
                }
                let (mut pm2, mut pm1) = (0., pmm);
                for l in m..=ell {
                    let p = if l == m {
                        pmm
                    } else if l == m + 1 {
                        (2 * m + 1) as f64 * mu * pmm
                    } else {
                        ((2 * l - 1) as f64 * mu * pm1 - (l + m - 1) as f64 * pm2) / (l - m) as f64
                    };
                    let norm = ((2 * l + 1) as f64
                        / (l - m + 1..=l + m).fold(1., |a, k| a * k as f64))
                    .sqrt()
                        * p;
                    if m == 0 {
                        syn[(i, l * l + l)] = norm;
                    } else {
                        let c = 2_f64.sqrt() * norm;
                        syn[(i, l * l + l + m)] = c * (m as f64 * phi).cos();
                        syn[(i, l * l + l - m)] = c * (m as f64 * phi).sin();
                    }
                    pm2 = pm1;
                    pm1 = p;
                }
            }
        }
        let ana = DMatrix::from_fn(nm, na, |k, i| syn[(i, k)] * weights[i]);
        let gram = &ana * &syn - DMatrix::<f64>::identity(nm, nm);
        let defect = gram.amax();
        if !defect.is_finite() || defect > 1e-10 {
            return Err(format!("REC grid not harmonic exact: {defect:e}"));
        }
        Ok(Self {
            directions,
            weights,
            ell,
            gram_defect: defect,
            syn,
            ana,
            lm,
        })
    }
    pub fn n(&self) -> usize {
        self.weights.len()
    }
    pub fn modes(&self) -> usize {
        self.lm.len()
    }
}
pub struct Bridge {
    pub network: Network,
    pub grid: Grid,
}
#[derive(Clone, Debug)]
pub struct Action {
    pub occupation: DMatrix<f64>,
    pub number: DMatrix<f64>,
    pub number_residual: f64,
    pub entropy_rate: f64,
    pub q_gamma: [f64; 4],
    pub q_atom: [f64; 4],
    pub number_l1: f64,
    pub weighted_force_scale: f64,
}
#[derive(Clone, Debug)]
pub struct FrameMap {
    pub directions_normal: Vec<[f64; 3]>,
    pub doppler: Vec<f64>,
    pub weights_normal: Vec<f64>,
    pub log_frequency_drift: Vec<f64>,
    pub beta: [f64; 3],
    pub hubble_s: f64,
    pub roundtrip: f64,
}
pub fn frame_map(
    grid: &Grid,
    node: &RayNode,
    beta: [f64; 3],
    beta_prime: [f64; 3],
    hubble_s: f64,
) -> Result<FrameMap, String> {
    if !hubble_s.is_finite() || hubble_s <= 0. {
        return Err("invalid normal H".into());
    }
    let b = V::from(beta);
    let mut m = FrameMap {
        directions_normal: vec![],
        doppler: vec![],
        weights_normal: vec![],
        log_frequency_drift: vec![],
        beta,
        hubble_s,
        roundtrip: 0.,
    };
    for (i, e) in grid.directions.iter().enumerate() {
        let (n, _, dinv) = boost(V::from(*e), -b)?;
        let (h, _, d) = boost(n, b)?;
        m.roundtrip = m
            .roundtrip
            .max((h - V::from(*e)).norm())
            .max((d * dinv - 1.).abs());
        let normal: [f64; 3] = n.into();
        let drift = -d * material_expansion_factor(node, normal, beta, beta_prime)?;
        m.directions_normal.push(normal);
        m.doppler.push(d);
        m.weights_normal.push(grid.weights[i] * d * d);
        m.log_frequency_drift.push(drift);
    }
    Ok(m)
}
pub fn boost_force_to_normal(q: [f64; 4], beta: [f64; 3]) -> Result<[f64; 4], String> {
    let b = V::from(beta);
    let b2 = b.norm_squared();
    if !(0. ..1.).contains(&b2) || q.iter().any(|v| !v.is_finite()) {
        return Err("invalid four-force boost".into());
    }
    let g = 1. / (1. - b2).sqrt();
    let v = V::new(q[1], q[2], q[3]);
    let dot = b.dot(&v);
    let r = v + (g * g / (1. + g) * dot + g * q[0]) * b;
    Ok([g * (q[0] + dot), r[0], r[1], r[2]])
}
#[derive(Clone, Debug)]
pub struct NormalLedger {
    pub number_per_eta: f64,
    pub q_gamma_per_eta: [f64; 4],
    pub q_atom_per_eta: [f64; 4],
    pub force_relative_defect: f64,
    pub occupation_per_eta: DMatrix<f64>,
}
#[derive(Clone, Debug)]
pub struct Implicit {
    pub occupation: DMatrix<f64>,
    pub residual: f64,
    pub iterations: usize,
    pub krylov: usize,
    pub number_defect: f64,
    pub free_energy_change: f64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Side {
    Red,
    Blue,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Direction {
    IntoCom,
    OutOfCom,
}
#[derive(Clone, Debug)]
pub struct Packet {
    pub side: Side,
    pub direction: Direction,
    pub frequency_hz: f64,
    pub number_per_h: f64,
    pub energy_j_per_h: f64,
}
#[derive(Clone, Debug)]
pub struct PacketLedger {
    pub native_number_per_h: f64,
    pub com_number_per_h: f64,
    pub native_energy_j_per_h: f64,
    pub com_energy_j_per_h: f64,
    pub centroid_proxy_j_per_h: f64,
    pub unresolved_j_per_h: f64,
    pub atom_energy_j_per_h: f64,
}
impl Bridge {
    pub fn new(network: Network, grid: Grid) -> Result<Self, String> {
        if grid.ell > network.ell {
            return Err("angular release exceeds source moments".into());
        }
        Ok(Self { network, grid })
    }
    fn shape(&self, f: &DMatrix<f64>) -> bool {
        f.shape() == (self.grid.n(), self.network.n())
    }
    fn check(&self, f: &DMatrix<f64>) -> Result<(), String> {
        if !self.shape(f) || f.iter().any(|x| !x.is_finite() || *x <= 0.) {
            return Err("invalid positive REC occupation".into());
        }
        Ok(())
    }
    pub fn equilibrium(&self, activity: f64) -> Result<DMatrix<f64>, String> {
        let f = DMatrix::from_fn(self.grid.n(), self.network.n(), |_, i| {
            let x = activity * self.network.z(i);
            x / (1. - x)
        });
        if activity <= 0.
            || !activity.is_finite()
            || (0..self.network.n()).any(|i| activity * self.network.z(i) >= 1.)
        {
            return Err("invalid REC equilibrium activity".into());
        }
        self.check(&f)?;
        Ok(f)
    }
    fn avg(&self, f: &DMatrix<f64>) -> f64 {
        let mut q = 0.;
        for i in 0..f.ncols() {
            for a in 0..f.nrows() {
                q += self.grid.weights[a] * f[(a, i)];
            }
        }
        q
    }
    // Summed frequency-pair convolutions, rather than an O(nfreq^2)
    // array of angular fields. Addition theorem diagonalizes each ell.
    fn convolve(&self, f: &DMatrix<f64>, scope: Scope, same: bool) -> DMatrix<f64> {
        let c = &self.grid.ana * f;
        let n = self.network.n();
        let mut g = DMatrix::zeros(c.nrows(), n);
        for k in 0..c.nrows() {
            let l = self.grid.lm[k];
            for i in 0..n {
                let v = if same {
                    self.network.same(l, i, scope) * c[(k, i)]
                } else {
                    (0..n)
                        .map(|j| self.network.get(l, i, j, scope) * c[(k, j)])
                        .sum()
                };
                g[(k, i)] = v;
            }
        }
        &self.grid.syn * g
    }
    fn activities(&self, f: &DMatrix<f64>) -> (DMatrix<f64>, DMatrix<f64>, DMatrix<f64>, f64) {
        let n = self.network.n();
        let one = f.map(|v| 1. + v);
        let phi = DMatrix::from_fn(f.nrows(), n, |a, i| {
            f[(a, i)] / self.network.z(i) / one[(a, i)]
        });
        let reference = self.avg(&phi) / n as f64;
        let shifted = phi.map(|v| v - reference);
        let delta = one.component_mul(&shifted);
        (one, shifted, delta, reference)
    }
    fn number_action(&self, f: &DMatrix<f64>, scope: Scope) -> DMatrix<f64> {
        let (one, q, delta, _) = self.activities(f);
        let residual = self.convolve(&delta, scope, false)
            - q.component_mul(&self.convolve(&one, scope, false));
        let mut result = one.component_mul(&residual);
        let same = self.convolve(f, scope, true);
        for i in 0..result.ncols() {
            for a in 0..result.nrows() {
                result[(a, i)] += self.network.states[i].g * same[(a, i)];
            }
        }
        result
    }
    fn to_occupation(&self, number: &DMatrix<f64>) -> DMatrix<f64> {
        DMatrix::from_fn(number.nrows(), number.ncols(), |a, i| {
            number[(a, i)] / self.network.states[i].g
        })
    }
    pub fn occupation_action(
        &self,
        f: &DMatrix<f64>,
        scope: Scope,
    ) -> Result<DMatrix<f64>, String> {
        self.check(f)?;
        let a = self.to_occupation(&self.number_action(f, scope));
        if a.iter().any(|x| !x.is_finite()) {
            return Err("nonfinite REC action".into());
        }
        Ok(a)
    }
    pub fn action(&self, f: &DMatrix<f64>, scope: Scope) -> Result<Action, String> {
        self.check(f)?;
        let number = self.number_action(f, scope);
        let occupation = self.to_occupation(&number);
        let (mut n, mut ent, mut l1, mut fs) = (0., 0., 0., 0.);
        let mut q = [0.; 4];
        for i in 0..f.ncols() {
            let s = &self.network.states[i];
            let logz = self.network.z(i).ln();
            for a in 0..f.nrows() {
                let v = number[(a, i)] * self.grid.weights[a];
                n += v;
                l1 += v.abs();
                ent += v * (f[(a, i)].ln() - f[(a, i)].ln_1p() - logz);
                let pv = v * s.p;
                q[0] += pv;
                fs += pv.abs();
                for k in 0..3 {
                    q[k + 1] += pv * self.grid.directions[a][k];
                }
            }
        }
        if ![n, ent, l1, fs].iter().chain(&q).all(|v| v.is_finite())
            || number.iter().any(|x| !x.is_finite())
        {
            return Err("nonfinite REC diagnostics".into());
        }
        Ok(Action {
            occupation,
            number,
            number_residual: n,
            entropy_rate: ent,
            q_gamma: q,
            q_atom: q.map(|x| -x),
            number_l1: l1,
            weighted_force_scale: fs,
        })
    }
    pub fn jvp(
        &self,
        f: &DMatrix<f64>,
        v: &DMatrix<f64>,
        scope: Scope,
    ) -> Result<DMatrix<f64>, String> {
        self.check(f)?;
        if !self.shape(v) || v.iter().any(|x| !x.is_finite()) {
            return Err("invalid REC JVP direction".into());
        }
        let (one, q, delta, reference) = self.activities(f);
        let n = self.network.n();
        let du = DMatrix::from_fn(f.nrows(), n, |a, i| {
            v[(a, i)] / self.network.z(i) / one[(a, i)].powi(2)
        });
        let dr = self.avg(&du) / n as f64;
        let dq = du.map(|x| x - dr);
        let dd = DMatrix::from_fn(f.nrows(), n, |a, i| {
            v[(a, i)] / self.network.z(i) - reference * v[(a, i)] - dr * one[(a, i)]
        });
        let ko = self.convolve(&one, scope, false);
        let residual = self.convolve(&delta, scope, false) - q.component_mul(&ko);
        let dres = self.convolve(&dd, scope, false)
            - dq.component_mul(&ko)
            - q.component_mul(&self.convolve(v, scope, false));
        let result = self.to_occupation(&(v.component_mul(&residual) + one.component_mul(&dres)))
            + self.convolve(v, scope, true);
        if result.iter().any(|x| !x.is_finite()) {
            return Err("nonfinite REC JVP".into());
        }
        Ok(result)
    }
    pub fn normal_ledger(&self, a: &Action, m: &FrameMap) -> Result<NormalLedger, String> {
        if m.doppler.len() != self.grid.n() || !self.shape(&a.number) {
            return Err("frame/action mismatch".into());
        }
        let h = m.hubble_s;
        let mut q = [0.; 4];
        let mut n = 0.;
        let mut scale = 0.;
        // Direct normal quadrature: w_n=D^2 w_b, g_n=g_b/D^3,
        // d f/d eta=D C_b/H. Photon p_n=p_b/D.
        let rate = DMatrix::from_fn(a.number.nrows(), a.number.ncols(), |k, i| {
            a.occupation[(k, i)] * m.doppler[k] / h
        });
        for i in 0..a.number.ncols() {
            let s = &self.network.states[i];
            for k in 0..a.number.nrows() {
                let d = m.doppler[k];
                let dn = rate[(k, i)] * s.g / d.powi(3) * m.weights_normal[k];
                n += dn;
                let p = dn * s.p / d;
                q[0] += p;
                scale += p.abs();
                for j in 0..3 {
                    q[j + 1] += p * m.directions_normal[k][j];
                }
            }
        }
        let expected = boost_force_to_normal(a.q_gamma, m.beta)?.map(|x| x / h);
        let err = q
            .iter()
            .zip(expected)
            .map(|(a, b)| (a - b).abs())
            .fold(0., f64::max)
            / scale.max(f64::MIN_POSITIVE);
        Ok(NormalLedger {
            number_per_eta: n,
            q_gamma_per_eta: q,
            q_atom_per_eta: q.map(|x| -x),
            force_relative_defect: err,
            occupation_per_eta: rate,
        })
    }
    pub fn photon_number(&self, f: &DMatrix<f64>, clock: &[f64]) -> Result<f64, String> {
        if !self.shape(f)
            || clock.len() != f.nrows()
            || clock.iter().any(|x| !x.is_finite() || *x <= 0.)
        {
            return Err("invalid clock weighted number".into());
        }
        Ok((0..f.ncols())
            .map(|i| {
                (0..f.nrows())
                    .map(|a| self.network.states[i].g * self.grid.weights[a] * f[(a, i)] / clock[a])
                    .sum::<f64>()
            })
            .sum())
    }
    pub fn free_energy(&self, f: &DMatrix<f64>, clock: &[f64]) -> f64 {
        let mut s = 0.;
        for i in 0..f.ncols() {
            let z = self.network.z(i).ln();
            for a in 0..f.nrows() {
                let x = f[(a, i)];
                s += self.network.states[i].g * self.grid.weights[a] / clock[a]
                    * (x * (x.ln() - z) - (1. + x) * x.ln_1p());
            }
        }
        s
    }
    pub fn packet(&self, p: &Packet, n_h: f64) -> Result<(DMatrix<f64>, PacketLedger), String> {
        if ![p.frequency_hz, p.number_per_h, p.energy_j_per_h, n_h]
            .iter()
            .all(|x| x.is_finite() && *x > 0.)
            || (p.energy_j_per_h / (H_PLANCK * p.frequency_hz * p.number_per_h) - 1.).abs() > 1e-12
        {
            return Err("invalid positive REC interface packet".into());
        }
        let (label, face) = if p.side == Side::Red {
            ("FR00", -21.25)
        } else {
            ("FB02", 21.25)
        };
        let i = self
            .network
            .states
            .iter()
            .position(|s| s.label == label)
            .ok_or("missing source far cell")?;
        let s = &self.network.states[i];
        if (if p.side == Side::Red { s.lo } else { s.hi }) != face {
            return Err("source face mismatch".into());
        }
        let sign = if p.direction == Direction::IntoCom {
            1.
        } else {
            -1.
        };
        let number = sign * p.number_per_h;
        let energy = sign * p.energy_j_per_h;
        let proxy = number * s.p * C;
        let mut increment = DMatrix::zeros(self.grid.n(), self.network.n());
        increment.column_mut(i).fill(n_h * number / s.g);
        Ok((
            increment,
            PacketLedger {
                native_number_per_h: -number,
                com_number_per_h: number,
                native_energy_j_per_h: -energy,
                com_energy_j_per_h: energy,
                centroid_proxy_j_per_h: proxy,
                unresolved_j_per_h: energy - proxy,
                atom_energy_j_per_h: 0.,
            },
        ))
    }
}

// A frequency block per ell is the exact Jacobian at the angular mean.
// For nonisotropic states or direction-dependent clocks this is only a
// preconditioner; the residual and all Krylov products use the actual JVP.
struct Preconditioner<'a> {
    bridge: &'a Bridge,
    blocks: Vec<LU<f64, Dyn, Dyn>>,
    diagonal: Vec<f64>,
}
impl<'a> Preconditioner<'a> {
    fn new(bridge: &'a Bridge, f: &DMatrix<f64>, dt: f64, clock: &[f64]) -> Result<Self, String> {
        let n = bridge.network.n();
        let g = &bridge.grid;
        let mean = (0..n)
            .map(|i| (0..g.n()).map(|k| g.weights[k] * f[(k, i)]).sum::<f64>())
            .collect::<Vec<_>>();
        let time = dt
            * clock
                .iter()
                .zip(&g.weights)
                .map(|(d, w)| d * w)
                .sum::<f64>();
        let net = &bridge.network;
        let diag = (0..n)
            .map(|i| {
                let z = net.z(i);
                (0..n)
                    .map(|j| {
                        net.get(0, i, j, Scope::Full) * (mean[j] / net.z(j) - (1. + mean[j]) / z)
                    })
                    .sum::<f64>()
                    / net.states[i].g
            })
            .collect::<Vec<_>>();
        let mut blocks = Vec::new();
        for l in 0..=g.ell {
            let a = DMatrix::from_fn(n, n, |i, j| {
                let c = if i == j {
                    diag[i] + net.same(l, i, Scope::Full)
                } else {
                    net.get(l, i, j, Scope::Full) * ((1. + mean[i]) / net.z(j) - mean[i] / net.z(i))
                        / net.states[i].g
                };
                if i == j {
                    1. - time * c
                } else {
                    -time * c
                }
            });
            blocks.push(a.lu());
        }
        let diagonal = diag.iter().map(|v| 1. - time * v).collect::<Vec<_>>();
        if diagonal.iter().any(|x| !x.is_finite() || x.abs() < 1e-15) {
            return Err("invalid REC preconditioner diagonal".into());
        }
        Ok(Self {
            bridge,
            blocks,
            diagonal,
        })
    }
    fn apply(&self, f: &DMatrix<f64>) -> Result<DMatrix<f64>, String> {
        let g = &self.bridge.grid;
        let c = &g.ana * f;
        let mut rest = f - &g.syn * &c;
        for i in 0..rest.ncols() {
            rest.column_mut(i).scale_mut(1. / self.diagonal[i]);
        }
        let mut solved = c.clone();
        for k in 0..c.nrows() {
            let rhs = DVector::from_iterator(c.ncols(), (0..c.ncols()).map(|i| c[(k, i)]));
            let y = self.blocks[g.lm[k]]
                .solve(&rhs)
                .ok_or("singular REC harmonic preconditioner")?;
            for i in 0..c.ncols() {
                solved[(k, i)] = y[i];
            }
        }
        Ok(rest + &g.syn * solved)
    }
}
// Restarted, left-preconditioned GMRES with reorthogonalization. Dense
// Krylov vectors, no materialization of the angular-frequency Jacobian.
fn gmres<F>(b: &DMatrix<f64>, op: F) -> Result<(DMatrix<f64>, usize), String>
where
    F: Fn(&DMatrix<f64>) -> Result<DMatrix<f64>, String>,
{
    let target = 2e-9 * b.norm();
    let mut x = DMatrix::zeros(b.nrows(), b.ncols());
    let mut count = 0;
    if b.norm() == 0. {
        return Ok((x, count));
    }
    let restart = 24;
    for _ in 0..8 {
        let r = b - op(&x)?;
        let beta = r.norm();
        if beta <= target {
            return Ok((x, count));
        }
        let mut basis = vec![r / beta];
        let mut h = DMatrix::<f64>::zeros(restart + 1, restart);
        let mut cs = vec![0.; restart];
        let mut sn = vec![0.; restart];
        let mut rhs = vec![0.; restart + 1];
        rhs[0] = beta;
        let mut used = 0;
        for j in 0..restart {
            let mut v = op(&basis[j])?;
            count += 1;
            for _ in 0..2 {
                for i in 0..=j {
                    let a = v.dot(&basis[i]);
                    h[(i, j)] += a;
                    v -= a * &basis[i];
                }
            }
            let next = v.norm();
            h[(j + 1, j)] = next;
            for i in 0..j {
                let a = h[(i, j)];
                let b = h[(i + 1, j)];
                h[(i, j)] = cs[i] * a + sn[i] * b;
                h[(i + 1, j)] = -sn[i] * a + cs[i] * b;
            }
            let a = h[(j, j)];
            let d = a.hypot(h[(j + 1, j)]);
            if !d.is_finite() || d == 0. {
                return Err("GMRES breakdown".into());
            }
            cs[j] = a / d;
            sn[j] = h[(j + 1, j)] / d;
            h[(j, j)] = d;
            h[(j + 1, j)] = 0.;
            rhs[j + 1] = -sn[j] * rhs[j];
            rhs[j] *= cs[j];
            used = j + 1;
            if rhs[j + 1].abs() <= target || next <= 1e-15 * d {
                break;
            }
            basis.push(v / next);
        }
        let mut y = vec![0.; used];
        for i in (0..used).rev() {
            y[i] = (rhs[i] - (i + 1..used).map(|j| h[(i, j)] * y[j]).sum::<f64>()) / h[(i, i)];
        }
        for i in 0..used {
            x += y[i] * &basis[i];
        }
    }
    let r = b - op(&x)?;
    if r.norm() > target {
        return Err(format!("REC GMRES not converged: {}", r.norm() / b.norm()));
    }
    Ok((x, count))
}
impl Bridge {
    /// Frozen material-frame or normal-clock BE. clock=D for a step
    /// measured in normal proper time, clock=1 for a material clock.
    /// Prescribed integrated packet increment is in the same occupation
    /// representation. In this bounded bridge packets require clock=1.
    /// Positive line search, no clipping or renormalization.
    pub fn implicit(
        &self,
        old: &DMatrix<f64>,
        dt: f64,
        clock: &[f64],
        increment: &DMatrix<f64>,
    ) -> Result<Implicit, String> {
        self.check(old)?;
        if !dt.is_finite()
            || dt < 0.
            || clock.len() != old.nrows()
            || clock.iter().any(|v| !v.is_finite() || *v <= 0.)
            || !self.shape(increment)
            || increment.iter().any(|v| !v.is_finite())
            || increment.amax() != 0. && clock.iter().any(|v| *v != 1.)
        {
            return Err("invalid REC implicit step or clock/packet combination".into());
        }
        let scale = old.amax().max(increment.amax()).max(f64::MIN_POSITIVE);
        let time_mul = |a: DMatrix<f64>| {
            DMatrix::from_fn(a.nrows(), a.ncols(), |k, i| dt * clock[k] * a[(k, i)])
        };
        let residual = |f: &DMatrix<f64>| -> Result<DMatrix<f64>, String> {
            Ok(f - old - increment - time_mul(self.occupation_action(f, Scope::Full)?))
        };
        let mut f = old.clone();
        let mut krylov = 0;
        let n0 = self.photon_number(old, clock)?;
        let expected = n0 + self.photon_number(increment, clock)?;
        let free0 = self.free_energy(old, clock);
        for k in 0..=16 {
            let r = residual(&f)?;
            let norm = r.amax() / scale;
            let number_defect =
                (self.photon_number(&f, clock)? - expected).abs() / n0.max(f64::MIN_POSITIVE);
            // Require both net BE residual and the independently computed
            // number ledger. No backward-error-only acceptance.
            if norm <= 2e-10 && number_defect <= 2e-10 {
                return Ok(Implicit {
                    free_energy_change: self.free_energy(&f, clock) - free0,
                    occupation: f,
                    residual: norm,
                    iterations: k,
                    krylov,
                    number_defect,
                });
            }
            if k == 16 {
                break;
            }
            let p = Preconditioner::new(self, &f, dt, clock)?;
            let b = p.apply(&(-r))?;
            let (delta, it) = gmres(&b, |v| {
                p.apply(&(v - time_mul(self.jvp(&f, v, Scope::Full)?)))
            })?;
            krylov += it;
            let mut alpha = 1.;
            let mut next = None;
            for _ in 0..24 {
                let trial = &f + alpha * &delta;
                if trial.iter().all(|v| v.is_finite() && *v > 0.) {
                    let nn = residual(&trial)?.amax() / scale;
                    if nn < norm * (1. - 1e-4 * alpha) {
                        next = Some(trial);
                        break;
                    }
                }
                alpha *= 0.5;
            }
            f = next.ok_or_else(|| format!("REC Newton line search failed, residual {norm:e}"))?;
        }
        Err(format!(
            "REC Newton not converged: {:e}",
            residual(&f)?.amax() / scale
        ))
    }
}

#[derive(Clone, Debug)]
pub struct PlanckSample {
    pub occupation: DMatrix<f64>,
    pub temperature_h: Vec<f64>,
    pub source_measure_defect: f64,
    pub source_momentum_defect: f64,
    pub cell_energy_projection_defect: f64,
}
/// Exact collisionless Planck characteristic: f is invariant. Integrate
/// over the source-owned frequency cells, using their *absorption* center
/// (including the source recoil shift), not a bolometric fit to mixed spectra.
/// A finite cell stores only number; its energy moment is a centroid proxy.
pub fn sample_collisionless_planck(
    net: &Network,
    frame: &FrameMap,
    records: &[super::replay::StepRecord],
    t_emit: f64,
    nu_abs: f64,
    dnu: f64,
) -> Result<PlanckSample, String> {
    if records.is_empty()
        || ![t_emit, nu_abs, dnu]
            .iter()
            .all(|v| v.is_finite() && *v > 0.)
        || records
            .iter()
            .any(|r| r.first.iter().chain(&r.second).any(|ev| ev.depth != 0.))
    {
        return Err(
            "Planck sampler requires collisionless accepted history and physical source anchors"
                .into(),
        );
    }
    for (i, r) in records.iter().enumerate() {
        if r.right.eta <= r.left.eta || (i > 0 && records[i - 1].right.eta != r.left.eta) {
            return Err("invalid characteristic history".into());
        }
    }
    let mut temp = Vec::new();
    for (n, d) in frame.directions_normal.iter().zip(&frame.doppler) {
        let mut dir = *n;
        let mut back = 0.;
        for r in records.iter().rev() {
            let q = super::advance_ray(&r.right, &r.left, dir)?;
            dir = q.e;
            back += q.log_energy;
        }
        temp.push(t_emit * d * (-back).exp());
    }
    let (mut dm, mut dp, mut de): (f64, f64, f64) = (0., 0., 0.);
    let mut f = DMatrix::zeros(temp.len(), net.n());
    const GX: [f64; 4] = [
        0.1834346424956498,
        0.5255324099163290,
        0.7966664774136267,
        0.9602898564975363,
    ];
    const GW: [f64; 4] = [
        0.3626837833783620,
        0.3137066458778873,
        0.2223810344533745,
        0.1012285362903763,
    ];
    let b = dnu / nu_abs;
    let kb = 1.380649e-23;
    let phase = 8. * std::f64::consts::PI * nu_abs * nu_abs * dnu / C.powi(3);
    for (i, s) in net.states.iter().enumerate() {
        let m = (s.lo + s.hi) * 0.5;
        let w = (s.hi - s.lo) * 0.5;
        if 1. + b * s.lo <= 0. {
            return Err("source cell has nonpositive frequency".into());
        }
        let (mut v, mut e) = (0., 0.);
        for k in 0..4 {
            for sign in [-1., 1.] {
                let u = 1. + b * (m + sign * w * GX[k]);
                let ww = w * GW[k] * u * u;
                v += ww;
                e += ww * u;
            }
        }
        dm = dm.max((phase * v / s.g - 1.).abs());
        dp = dp.max((H_PLANCK * nu_abs / C * e / v / s.p - 1.).abs());
        for (a, t) in temp.iter().enumerate() {
            let mut number = 0.;
            let mut energy = 0.;
            for k in 0..4 {
                for sign in [-1., 1.] {
                    let u = 1. + b * (m + sign * w * GX[k]);
                    let occ = 1. / (H_PLANCK * nu_abs * u / (kb * t)).exp_m1();
                    let mass = w * GW[k] * u * u * occ;
                    number += mass;
                    energy += mass * u;
                }
            }
            f[(a, i)] = number / v;
            if energy > 0. {
                de = de.max((number * e / v / energy - 1.).abs());
            }
        }
    }
    if f.iter().any(|v| !v.is_finite() || *v <= 0.) {
        return Err("invalid Planck occupation".into());
    }
    Ok(PlanckSample {
        occupation: f,
        temperature_h: temp,
        source_measure_defect: dm,
        source_momentum_defect: dp,
        cell_energy_projection_defect: de,
    })
}
