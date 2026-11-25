//! Universal Lie-generated spin-harmonic (PSTF) hierarchy of bolometric radiation.
//!
//! One set of equations for every Bianchi algebra (Dossier II ii:spectral_hierarchy
//! integrated over E^(k-1) dE with carrier weight k; k = 4 is the energy carrier):
//!
//!   d_eta a^h_lm = sum [ k R~_LM G^h - U_LM K_grad^h - Z_LM K_J^h + i h omega_LM G^h ] a^h_l'm'
//!                  - k a^h_lm,
//!
//! where (R~, U, Z, omega)_LM, L <= 2, are the type constants of `geom::lie` for the
//! Hubble-normalized Lie data (Sigma, N, A, Omega), and G, K_grad, K_J = -i kj are the
//! Gaunt kernels of `kinetic::wigner`. Spins: h = 0 (I) and h = +-2 (Q +- iU) in the
//! (e_theta, e_phi) dyad of the photon propagation direction; V is not carried.
//! Each row couples |l - l'| <= 2, m' = m - M. The isotropic term -k a is integrated
//! exactly; the rest by classical RK4 on substeps with linearly interpolated Lie
//! data (the same background interpolation as `lie_history::advance_ray`).
//! The truncated (Galerkin) system sets a_l'm' = 0 for l' > lmax.
use crate::geom::lie::{photon_potentials, LieData, PhotonPotentials, POTENTIAL_MODES};
use crate::kinetic::lie_history::RayNode;
use crate::kinetic::spin_sht::{index, modes, C64};
use crate::kinetic::wigner::{gaunt, LogFactorial};

/// Lie data of a history node (Hubble units).
pub fn lie_data(node: &RayNode) -> LieData {
    LieData {
        shear: node.shear,
        n: node.n,
        a: node.a,
        rotation: node.rotation,
    }
}

#[derive(Clone, Copy, Debug)]
struct Entry {
    target: u32,
    source: u32,
    lm: u8,
    g: f64,
    kgrad: f64,
    kj: f64,
}

/// Spin of each slot of a state vector.
pub const SPINS: [i64; 3] = [0, 2, -2];

/// Precomputed kernel table for one lmax.
#[derive(Clone, Debug)]
pub struct LieHierarchy {
    pub lmax: usize,
    pub polarized: bool,
    /// Carrier weight k of the integrated spectrum (4 = bolometric energy).
    pub carrier: f64,
    entries: Vec<Vec<Entry>>,
}

impl LieHierarchy {
    pub fn new(lmax: usize, polarized: bool, carrier: f64) -> Result<Self, String> {
        if !(2..=2048).contains(&lmax) || !carrier.is_finite() {
            return Err("Lie hierarchy needs 2 <= lmax <= 2048 and a finite carrier weight".into());
        }
        let lf = LogFactorial::new(2 * lmax + 16);
        let spins: &[i64] = if polarized { &SPINS } else { &SPINS[..1] };
        let mut entries = Vec::with_capacity(spins.len());
        for &h in spins {
            let mut list = Vec::new();
            let lmin = h.unsigned_abs() as i64;
            for l in lmin..=lmax as i64 {
                for m in -l..=l {
                    for big_l in 0..=2i64 {
                        for big_m in -big_l..=big_l {
                            let lo = lmin.max(l - big_l);
                            let hi = (lmax as i64).min(l + big_l);
                            for lp in lo..=hi {
                                let mp = m - big_m;
                                if mp.abs() > lp {
                                    continue;
                                }
                                let k = gaunt(&lf, h, l, m, big_l, big_m, lp);
                                if k.g == 0.0 && k.kgrad == 0.0 && k.kj == 0.0 {
                                    continue;
                                }
                                list.push(Entry {
                                    target: index(l as usize, m) as u32,
                                    source: index(lp as usize, mp) as u32,
                                    lm: (big_l * big_l + big_l + big_m) as u8,
                                    g: k.g,
                                    kgrad: k.kgrad,
                                    kj: k.kj,
                                });
                            }
                        }
                    }
                }
            }
            entries.push(list);
        }
        Ok(Self {
            lmax,
            polarized,
            carrier,
            entries,
        })
    }

    /// Number of spin slots (1 unpolarized, 3 polarized).
    pub fn slots(&self) -> usize {
        self.entries.len()
    }

    /// Number of stored kernel entries.
    pub fn entry_count(&self) -> usize {
        self.entries.iter().map(Vec::len).sum()
    }

    /// Anisotropic generator (without the exact isotropic -k a term).
    pub fn rhs(&self, pot: &PhotonPotentials, state: &[Vec<C64>], out: &mut [Vec<C64>]) {
        let i = C64::new(0.0, 1.0);
        for (slot, list) in self.entries.iter().enumerate() {
            let h = SPINS[slot] as f64;
            let cg: [C64; POTENTIAL_MODES] =
                std::array::from_fn(|k| pot.r[k] * self.carrier + i * h * pot.omega[k]);
            let cgrad: [C64; POTENTIAL_MODES] = std::array::from_fn(|k| -pot.u[k]);
            let cj: [C64; POTENTIAL_MODES] = std::array::from_fn(|k| i * pot.z[k]);
            let src = &state[slot];
            let dst = &mut out[slot];
            dst.iter_mut().for_each(|v| *v = C64::new(0.0, 0.0));
            for e in list {
                let lm = e.lm as usize;
                let coef = cg[lm] * e.g + cgrad[lm] * e.kgrad + cj[lm] * e.kj;
                dst[e.target as usize] += coef * src[e.source as usize];
            }
        }
    }

    /// Generator including the isotropic term -k a (for tests and diagnostics).
    pub fn full_rhs(&self, pot: &PhotonPotentials, state: &[Vec<C64>], out: &mut [Vec<C64>]) {
        self.rhs(pot, state, out);
        for (o, s) in out.iter_mut().zip(state) {
            for (x, y) in o.iter_mut().zip(s) {
                *x -= y * self.carrier;
            }
        }
    }

    /// Multiplication by R~=-Sigma:ee in the signed-spin basis.
    fn redshift_add(
        &self,
        pot: &PhotonPotentials,
        src: &[Vec<C64>],
        dst: &mut [Vec<C64>],
        factor: f64,
    ) {
        for (slot, list) in self.entries.iter().enumerate() {
            for e in list {
                dst[slot][e.target as usize] +=
                    factor * pot.r[e.lm as usize] * e.g * src[slot][e.source as usize];
            }
        }
    }

    /// Raw moments of xi=log(T/T_emit)+eta. Differentiate the centered
    /// Mellin generator at carrier zero: A0 M_k + k R~ M_(k-1).
    /// No angular synthesis or finite differences in carrier weight.
    pub fn stream_log_triplet(
        &self,
        states: &mut [Vec<Vec<C64>>; 3],
        left: &LieData,
        right: &LieData,
        dt: f64,
    ) -> Result<(), String> {
        if self.carrier != 0.
            || !dt.is_finite()
            || states
                .iter()
                .any(|s| s.len() != self.slots() || s.iter().any(|v| v.len() != modes(self.lmax)))
        {
            return Err("invalid log-moment hierarchy shape or carrier".into());
        }
        let norm = |d: &LieData| {
            d.shear
                .iter()
                .flatten()
                .chain(d.n.iter().flatten())
                .chain(&d.a)
                .chain(&d.rotation)
                .map(|v| v * v)
                .sum::<f64>()
                .sqrt()
        };
        let bound = dt.abs() * (self.lmax as f64 + 6.) * 2. * norm(left).max(norm(right));
        if !bound.is_finite() || bound > 1e7 {
            return Err("unresolved log-moment streaming interval".into());
        }
        let count = (bound / 0.5).ceil().max(1.) as usize;
        let h = dt / count as f64;
        let pl = photon_potentials(left);
        let pr = photon_potentials(right);
        let zero = || std::array::from_fn::<_, 3, _>(|_| self.zero_state());
        let mut k1 = zero();
        let mut k2 = zero();
        let mut k3 = zero();
        let mut k4 = zero();
        let mut tmp = zero();
        let rhs = |p: &PhotonPotentials, x: &[Vec<Vec<C64>>; 3], out: &mut [Vec<Vec<C64>>; 3]| {
            for i in 0..3 {
                self.rhs(p, &x[i], &mut out[i]);
                if i > 0 {
                    self.redshift_add(p, &x[i - 1], &mut out[i], i as f64);
                }
            }
        };
        let axpy = |out: &mut [Vec<Vec<C64>>; 3],
                    x: &[Vec<Vec<C64>>; 3],
                    k: &[Vec<Vec<C64>>; 3],
                    a: f64| {
            for i in 0..3 {
                for j in 0..self.slots() {
                    for m in 0..modes(self.lmax) {
                        out[i][j][m] = x[i][j][m] + a * k[i][j][m];
                    }
                }
            }
        };
        for i in 0..count {
            let p0 = pl.lerp(&pr, i as f64 / count as f64);
            let pm = pl.lerp(&pr, (i as f64 + 0.5) / count as f64);
            let p1 = pl.lerp(&pr, (i + 1) as f64 / count as f64);
            rhs(&p0, states, &mut k1);
            axpy(&mut tmp, states, &k1, h * 0.5);
            rhs(&pm, &tmp, &mut k2);
            axpy(&mut tmp, states, &k2, h * 0.5);
            rhs(&pm, &tmp, &mut k3);
            axpy(&mut tmp, states, &k3, h);
            rhs(&p1, &tmp, &mut k4);
            for j in 0..3 {
                for s in 0..self.slots() {
                    for m in 0..modes(self.lmax) {
                        states[j][s][m] +=
                            (k1[j][s][m] + 2. * (k2[j][s][m] + k3[j][s][m]) + k4[j][s][m])
                                * (h / 6.);
                    }
                }
            }
        }
        if states
            .iter()
            .flatten()
            .flatten()
            .any(|v| !v.re.is_finite() || !v.im.is_finite())
        {
            return Err("nonfinite log-moment coefficients".into());
        }
        Ok(())
    }

    pub fn zero_state(&self) -> Vec<Vec<C64>> {
        vec![vec![C64::new(0.0, 0.0); modes(self.lmax)]; self.slots()]
    }

    /// Free streaming across [0, dt] with Lie data interpolated linearly from `left`
    /// to `right`. The isotropic factor exp(-k dt) is exact; RK4 substeps are chosen
    /// from a bound of the generator norm.
    pub fn stream(
        &self,
        state: &mut [Vec<C64>],
        left: &LieData,
        right: &LieData,
        dt: f64,
    ) -> Result<(), String> {
        self.stream_impl(state, left, right, dt, false)
    }

    /// Stream exp(k eta) B_k without the common FLRW redshift factor.
    pub fn stream_centered(
        &self,
        state: &mut [Vec<C64>],
        left: &LieData,
        right: &LieData,
        dt: f64,
    ) -> Result<(), String> {
        self.stream_impl(state, left, right, dt, true)
    }
    fn stream_impl(
        &self,
        state: &mut [Vec<C64>],
        left: &LieData,
        right: &LieData,
        dt: f64,
        centered: bool,
    ) -> Result<(), String> {
        if !dt.is_finite() {
            return Err("non-finite streaming interval".into());
        }
        if state.len() != self.slots() || state.iter().any(|s| s.len() != modes(self.lmax)) {
            return Err("state shape does not match the hierarchy".into());
        }
        let norm = |d: &LieData| {
            let f = |t: &[[f64; 3]; 3]| t.iter().flatten().map(|x| x * x).sum::<f64>().sqrt();
            let v = |t: &[f64; 3]| t.iter().map(|x| x * x).sum::<f64>().sqrt();
            f(&d.shear) + f(&d.n) + v(&d.a) + v(&d.rotation)
        };
        let bound =
            dt.abs() * (self.lmax as f64 + 2.0 + self.carrier) * norm(left).max(norm(right));
        if !bound.is_finite() || bound > 1e7 {
            return Err("streaming interval requires subdivision of its history".into());
        }
        let count = (bound / 0.5).ceil().max(1.0) as usize;
        let h = dt / count as f64;
        let pl = photon_potentials(left);
        let pr = photon_potentials(right);
        let mut k1 = self.zero_state();
        let mut k2 = self.zero_state();
        let mut k3 = self.zero_state();
        let mut k4 = self.zero_state();
        let mut tmp = self.zero_state();
        let axpy = |out: &mut [Vec<C64>], y: &[Vec<C64>], k: &[Vec<C64>], s: f64| {
            for ((o, a), b) in out.iter_mut().zip(y).zip(k) {
                for ((o, a), b) in o.iter_mut().zip(a).zip(b) {
                    *o = a + b * s;
                }
            }
        };
        for step in 0..count {
            let f0 = step as f64 / count as f64;
            let fm = (step as f64 + 0.5) / count as f64;
            let f1 = (step + 1) as f64 / count as f64;
            let p0 = pl.lerp(&pr, f0);
            let pm = pl.lerp(&pr, fm);
            let p1 = pl.lerp(&pr, f1);
            self.rhs(&p0, state, &mut k1);
            axpy(&mut tmp, state, &k1, 0.5 * h);
            self.rhs(&pm, &tmp, &mut k2);
            axpy(&mut tmp, state, &k2, 0.5 * h);
            self.rhs(&pm, &tmp, &mut k3);
            axpy(&mut tmp, state, &k3, h);
            self.rhs(&p1, &tmp, &mut k4);
            for slot in 0..state.len() {
                for j in 0..state[slot].len() {
                    state[slot][j] +=
                        (k1[slot][j] + (k2[slot][j] + k3[slot][j]) * 2.0 + k4[slot][j]) * (h / 6.0);
                }
            }
        }
        if !centered {
            let decay = (-self.carrier * dt).exp();
            for s in state.iter_mut() {
                for v in s.iter_mut() {
                    *v *= decay;
                }
            }
        }
        if state
            .iter()
            .flatten()
            .any(|v| !v.re.is_finite() || !v.im.is_finite())
        {
            return Err("non-finite harmonic coefficient after streaming".into());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geom::lie::canonical_algebra;
    use crate::kinetic::lie_history::advance_ray;
    use crate::kinetic::spin_sht::{evaluate_at, random_real_coefficients, SpinSht};
    use nalgebra::{Matrix3, Rotation3, Vector3};

    fn node(d: &LieData, eta: f64) -> RayNode {
        RayNode {
            eta,
            shear: d.shear,
            n: d.n,
            a: d.a,
            rotation: d.rotation,
            ..Default::default()
        }
    }

    fn dyad(e: Vector3<f64>) -> (Vector3<f64>, Vector3<f64>) {
        let z = e.z.clamp(-1.0, 1.0);
        let theta = z.acos();
        let phi = if e.x == 0.0 && e.y == 0.0 {
            0.0
        } else {
            e.y.atan2(e.x)
        };
        (
            Vector3::new(
                theta.cos() * phi.cos(),
                theta.cos() * phi.sin(),
                -theta.sin(),
            ),
            Vector3::new(-phi.sin(), phi.cos(), 0.0),
        )
    }

    fn coherency(e: Vector3<f64>, i: f64, q: f64, u: f64) -> Matrix3<f64> {
        let (t, p) = dyad(e);
        0.5 * (i * (t * t.transpose() + p * p.transpose())
            + q * (t * t.transpose() - p * p.transpose())
            + u * (t * p.transpose() + p * t.transpose()))
    }

    fn stokes(e: Vector3<f64>, f: &Matrix3<f64>) -> [f64; 3] {
        let (t, p) = dyad(e);
        [
            f.trace(),
            t.dot(&(f * t)) - p.dot(&(f * p)),
            2.0 * t.dot(&(f * p)),
        ]
    }

    /// Exact transported field at time `t` from the R109 characteristic map.
    fn transported(
        state: &[Vec<C64>; 3],
        lmax: usize,
        d: &LieData,
        t: f64,
        e: Vector3<f64>,
    ) -> [f64; 3] {
        let step = advance_ray(&node(d, t), &node(d, 0.0), e.into()).unwrap();
        let e0 = Vector3::from(step.e);
        let i0 = evaluate_at(0, &state[0], lmax, e0.into()).re;
        let p = evaluate_at(2, &state[1], lmax, e0.into());
        let f0 = coherency(e0, i0, p.re, p.im);
        let r = Matrix3::from_fn(|a, b| step.rotation[a][b]);
        let f = r.transpose() * f0 * r * (-4.0 * step.log_energy).exp();
        stokes(e, &f)
    }

    fn generator_error(d: &LieData, seed: u64) -> f64 {
        let lmax = 9;
        let band = 6;
        let [a0, ap, am] = random_real_coefficients(lmax, band, seed);
        let state = [a0, ap, am];
        let hier = LieHierarchy::new(lmax, true, 4.0).unwrap();
        let mut out = hier.zero_state();
        hier.full_rhs(&photon_potentials(d), &state, &mut out);
        let sht = SpinSht::new(lmax, 26, 52).unwrap();
        let delta = 2e-4;
        let mut di = vec![0.0; sht.len()];
        let mut dq = vec![0.0; sht.len()];
        let mut du = vec![0.0; sht.len()];
        for k in 0..sht.len() {
            let e = Vector3::new(
                sht.grid.ehat[3 * k],
                sht.grid.ehat[3 * k + 1],
                sht.grid.ehat[3 * k + 2],
            );
            let plus = transported(&state, lmax, d, delta, e);
            let minus = transported(&state, lmax, d, -delta, e);
            di[k] = (plus[0] - minus[0]) / (2.0 * delta);
            dq[k] = (plus[1] - minus[1]) / (2.0 * delta);
            du[k] = (plus[2] - minus[2]) / (2.0 * delta);
        }
        let fd = sht.from_stokes(&di, &dq, &du);
        let mut num = 0.0;
        let mut den = 0.0;
        for slot in 0..3 {
            for (x, y) in fd[slot].iter().zip(&out[slot]) {
                num += (x - y).norm_sqr();
                den += y.norm_sqr();
            }
        }
        (num / den).sqrt()
    }

    #[test]
    fn hierarchy_matches_exact_characteristic_generator_for_class_a_and_b() {
        let rot = Rotation3::from_euler_angles(0.3, -0.7, 1.1);
        let cases = [
            (
                "IX",
                0.4,
                [
                    [0.15, 0.04, -0.02],
                    [0.04, -0.1, 0.05],
                    [-0.02, 0.05, -0.05],
                ],
                [0.0, 0.0, 0.0],
            ),
            (
                "VIII",
                0.35,
                [[0.05, -0.08, 0.0], [-0.08, 0.02, 0.06], [0.0, 0.06, -0.07]],
                [0.02, -0.04, 0.03],
            ),
            (
                "VIIh:0.6",
                0.3,
                [[0.0, 0.07, 0.03], [0.07, 0.11, -0.02], [0.03, -0.02, -0.11]],
                [0.0, 0.05, 0.0],
            ),
            (
                "VIstar",
                0.25,
                [[0.09, 0.0, 0.05], [0.0, -0.03, 0.02], [0.05, 0.02, -0.06]],
                [-0.03, 0.0, 0.02],
            ),
            ("V", 0.5, [[0.0; 3]; 3], [0.0; 3]),
        ];
        for (k, (family, scale, shear, rotation)) in cases.into_iter().enumerate() {
            let (n, a) = canonical_algebra(family, scale, rot.matrix()).unwrap();
            let d = LieData {
                shear,
                n,
                a,
                rotation,
            };
            d.validate().unwrap();
            let err = generator_error(&d, 100 + k as u64);
            eprintln!("V3 {family}: relative generator error {err:e}");
            assert!(err < 1e-6, "{family}: relative generator error {err:e}");
        }
    }

    #[test]
    fn closed_form_limits_rotation_curvature_phase_and_type_v_mixing() {
        let lmax = 6;
        let hier = LieHierarchy::new(lmax, true, 4.0).unwrap();
        let [a0, ap, am] = random_real_coefficients(lmax, lmax, 3);
        let state = [a0, ap, am];
        let mut out = hier.zero_state();
        // Rigid rotation: d a / d eta = -i m Omega_z a.
        let omega_z = 0.37;
        let d = LieData {
            rotation: [0.0, 0.0, omega_z],
            ..Default::default()
        };
        hier.rhs(&photon_potentials(&d), &state, &mut out);
        for slot in 0..3 {
            for l in 0..=lmax {
                for m in -(l as i64)..=(l as i64) {
                    let k = index(l, m);
                    let want = state[slot][k] * C64::new(0.0, -(m as f64) * omega_z);
                    assert!((out[slot][k] - want).norm() < 1e-13);
                }
            }
        }
        // Isotropic curvature N = n_c I: d a^h = -i h n_c a^h / 2.
        let nc = 0.29;
        let d = LieData {
            n: [[nc, 0.0, 0.0], [0.0, nc, 0.0], [0.0, 0.0, nc]],
            ..Default::default()
        };
        hier.rhs(&photon_potentials(&d), &state, &mut out);
        for slot in 0..3 {
            let h = SPINS[slot] as f64;
            for (x, y) in out[slot].iter().zip(&state[slot]) {
                assert!((x - y * C64::new(0.0, -h * nc / 2.0)).norm() < 1e-13);
            }
        }
        // Type V, a = A z: same-mode advection -+A/3 at (l, m) = (2, 1) for h = +-2.
        let big_a = 0.41;
        let d = LieData {
            a: [0.0, 0.0, big_a],
            ..Default::default()
        };
        let mut unit = hier.zero_state();
        unit[1][index(2, 1)] = C64::new(1.0, 0.0);
        unit[2][index(2, 1)] = C64::new(1.0, 0.0);
        hier.rhs(&photon_potentials(&d), &unit, &mut out);
        assert!((out[1][index(2, 1)] - C64::new(-big_a / 3.0, 0.0)).norm() < 1e-14);
        assert!((out[2][index(2, 1)] - C64::new(big_a / 3.0, 0.0)).norm() < 1e-14);
    }

    #[test]
    fn streaming_preserves_reality_and_conserves_number_in_class_a() {
        // Class A: J_3 = 1 (Dossier II ii:moment_distortion) for the number carrier k = 3.
        let lmax = 12;
        let hier = LieHierarchy::new(lmax, true, 3.0).unwrap();
        let rot = Rotation3::from_euler_angles(0.2, 0.5, -0.4);
        let (n, a) = canonical_algebra("VIII", 0.4, rot.matrix()).unwrap();
        let left = LieData {
            shear: [[0.06, 0.02, 0.0], [0.02, -0.03, 0.01], [0.0, 0.01, -0.03]],
            n,
            a,
            rotation: [0.0; 3],
        };
        let mut right = left;
        right.shear[0][0] += 0.02;
        right.shear[1][1] -= 0.02;
        let mut state = hier.zero_state();
        state[0][0] = C64::new((4.0 * std::f64::consts::PI).sqrt(), 0.0);
        hier.stream(&mut state, &left, &right, 0.3).unwrap();
        // Monopole of the k = 3 carrier after removing exp(-3 eta): J_3 = 1 up to truncation.
        let j3 = state[0][0].re / (4.0 * std::f64::consts::PI).sqrt() / (-0.9f64).exp();
        assert!((j3 - 1.0).abs() < 1e-9, "{j3}");
        for l in 0..=lmax {
            for m in 0..=(l as i64) {
                let sign = if m % 2 == 0 { 1.0 } else { -1.0 };
                assert!(
                    (state[0][index(l, -m)] - state[0][index(l, m)].conj() * sign).norm() < 1e-14
                );
                assert!(
                    (state[2][index(l, -m)] - state[1][index(l, m)].conj() * sign).norm() < 1e-14
                );
            }
        }
    }
}
