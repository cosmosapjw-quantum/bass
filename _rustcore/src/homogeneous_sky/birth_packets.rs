//! Recovery of the F08 source-born characteristic representation, using the
//! current BASS Lie characteristic rather than a duplicated fixed-energy remap.
//! Counts are per H nucleus on a homogeneous non-tilted expanding LRS I slice.
//! No angular migration to a new grid, no count multiplication by solid angle.
//! Angular weights change for NEW locally isotropic births only.
use crate::kinetic::lie_history::{advance_ray, RayNode};
pub const HI_EDGE_EV: f64 = 13.60;
#[derive(Clone, Copy, Debug)]
pub struct Packet {
    pub ray: usize,
    pub energy_ev: f64,
    pub per_h: f64,
    pub birth_eta: f64,
    pub birth_energy_ev: f64,
}
#[derive(Clone, Debug, Default)]
pub struct TransportLedger {
    pub boundary_n: f64,
    pub boundary_u: f64,
    pub redshift_work: f64,
    pub boundary_pz: f64,
    pub redshift_pz: f64,
    pub crossing_energy_error: f64,
    pub max_support_error: f64,
}
#[derive(Clone, Debug, Default)]
pub struct CompressionLedger {
    pub before: usize,
    pub after: usize,
    pub max_number_relative: f64,
    pub max_energy_relative: f64,
    pub max_log_span: f64,
    pub max_rate_relative: f64,
    pub rate_splits: usize,
}
/// Frozen material absorption signature. The positive observables are
/// endpoint and BE-survivor weighted cross sections and excess energies,
/// plus the survivor number and energy. Units cancel in relative checks.
#[derive(Clone, Copy, Debug)]
pub struct RateGuard {
    pub absorber_cm3: [f64; 3],
    pub dt_s: f64,
}
impl RateGuard {
    fn validate(self) -> Result<(), String> {
        if !self.dt_s.is_finite()
            || self.dt_s <= 0.
            || self.absorber_cm3.iter().any(|v| !v.is_finite() || *v < 0.)
        {
            return Err("invalid compression rate guard".into());
        }
        Ok(())
    }
    fn features(self, e: f64) -> Result<[f64; 14], String> {
        use rei_microphysics::{Absorber, AtomicProvider, HHeModel};
        let p = AtomicProvider::reference();
        let c = HHeModel::controlled_fixture();
        let mut sigma = [0.; 3];
        for (j, a) in [Absorber::HI, Absorber::HeI, Absorber::HeII]
            .into_iter()
            .enumerate()
        {
            sigma[j] = p.cross_section(a, e).map_err(|v| v.to_string())?;
        }
        let x = self.dt_s * c.c_cm_s * sum((0..3).map(|j| self.absorber_cm3[j] * sigma[j]));
        if !x.is_finite() || x < 0. {
            return Err("invalid compression optical depth".into());
        }
        let survival = 1. / (1. + x);
        let mut v = [0.; 14];
        v[12] = survival;
        v[13] = survival * e;
        for j in 0..3 {
            let heat = if sigma[j] == 0. {
                0.
            } else {
                if e < c.threshold_ev[j] {
                    return Err("compression threshold ownership".into());
                }
                sigma[j] * (e - c.threshold_ev[j])
            };
            v[4 * j] = sigma[j];
            v[4 * j + 1] = heat;
            v[4 * j + 2] = sigma[j] * survival;
            v[4 * j + 3] = heat * survival;
        }
        Ok(v)
    }
}
fn rate_error(a: [f64; 14], b: [f64; 14]) -> f64 {
    (0..14)
        .map(|j| {
            if a[j] == 0. {
                if b[j] == 0. {
                    0.
                } else {
                    f64::INFINITY
                }
            } else {
                (b[j] - a[j]).abs() / a[j]
            }
        })
        .fold(0., f64::max)
}
fn rate_moments(p: &[Packet], g: RateGuard) -> Result<[f64; 14], String> {
    let mut out = [0.; 14];
    for a in p {
        if !a.per_h.is_finite()
            || a.per_h < 0.
            || !a.energy_ev.is_finite()
            || a.energy_ev < HI_EDGE_EV
        {
            return Err("invalid rate moment stock".into());
        }
        for (q, v) in out.iter_mut().zip(g.features(a.energy_ev)?) {
            *q += a.per_h * v;
        }
    }
    if out.iter().any(|v| !v.is_finite() || *v < 0.) {
        return Err("invalid rate moment".into());
    }
    Ok(out)
}
pub fn rate_moment_error(before: &[Packet], after: &[Packet], g: RateGuard) -> Result<f64, String> {
    g.validate()?;
    Ok(rate_error(
        rate_moments(before, g)?,
        rate_moments(after, g)?,
    ))
}
/// Axisymmetric ring-averaged normal-frame UV stress (SI energy density).
/// This is a tracer inventory, not an Einstein-source admission.
#[derive(Clone, Copy, Debug)]
pub struct LrsStress {
    pub rho_j_m3: f64,
    pub flux_z_j_m3: f64,
    pub p_parallel_j_m3: f64,
    pub p_perp_j_m3: f64,
    pub delta_j_m3: f64,
}
#[derive(Clone, Debug)]
pub struct BirthPackets {
    pub directions: Vec<[f64; 3]>,
    pub weights: Vec<f64>,
    pub packets: Vec<Packet>,
}
fn valid_node(p: &RayNode) -> bool {
    // The current packet inventory does not include class-B spatial
    // divergence or generic non-axial source. Fail closed even for vacuum.
    p.eta.is_finite()
        && p.n.iter().flatten().all(|&x| x == 0.)
        && p.a == [0.; 3]
        && p.rotation == [0.; 3]
        && p.shear.iter().flatten().all(|v| v.is_finite())
        && (p.shear[0][0] - p.shear[1][1]).abs() < 2e-11
        && (p.shear[0][0] + p.shear[1][1] + p.shear[2][2]).abs() < 2e-11
        && (0..3)
            .all(|i| p.shear[i][i] > -1. && (0..3).all(|j| i == j || p.shear[i][j].abs() < 2e-11))
}
impl BirthPackets {
    pub fn new(directions: Vec<[f64; 3]>, weights: Vec<f64>) -> Result<Self, String> {
        if directions.is_empty()
            || directions.len() != weights.len()
            || directions.iter().any(|v| {
                !v.iter().all(|x| x.is_finite())
                    || (v.iter().map(|x| x * x).sum::<f64>() - 1.).abs() > 2e-12
            })
            || weights.iter().any(|w| !w.is_finite() || *w <= 0.)
            || (weights.iter().sum::<f64>() - 1.).abs() > 2e-12
        {
            return Err("invalid birth angular quadrature".into());
        }
        Ok(Self {
            directions,
            weights,
            packets: vec![],
        })
    }
    pub fn inventory(&self) -> (f64, f64) {
        // Neumaier summation preserves tiny packet contributions.
        (
            sum(self.packets.iter().map(|p| p.per_h)),
            sum(self.packets.iter().map(|p| p.per_h * p.energy_ev)),
        )
    }
    /// PR171/PR173 proper volume conversion, exactly once per H nucleus.
    pub fn lrs_stress(&self, nh_m3: f64) -> Result<LrsStress, String> {
        if !nh_m3.is_finite()
            || nh_m3 <= 0.
            || self.packets.iter().any(|p| {
                p.ray >= self.directions.len()
                    || !p.per_h.is_finite()
                    || p.per_h < 0.
                    || !p.energy_ev.is_finite()
                    || p.energy_ev <= 0.
            })
        {
            return Err("invalid UV stress input".into());
        }
        let scale = nh_m3 * 1.602176634e-19;
        let u = sum(self.packets.iter().map(|p| p.per_h * p.energy_ev));
        let q = sum(self
            .packets
            .iter()
            .map(|p| p.per_h * p.energy_ev * self.directions[p.ray][2]));
        let z = sum(self
            .packets
            .iter()
            .map(|p| p.per_h * p.energy_ev * self.directions[p.ray][2].powi(2)));
        let pp = sum(self
            .packets
            .iter()
            .map(|p| p.per_h * p.energy_ev * (1. - self.directions[p.ray][2].powi(2)) * 0.5));
        Ok(LrsStress {
            rho_j_m3: u * scale,
            flux_z_j_m3: q * scale,
            p_parallel_j_m3: z * scale,
            p_perp_j_m3: pp * scale,
            delta_j_m3: (z - pp) * scale,
        })
    }
    pub fn transport(
        &mut self,
        left: &RayNode,
        right: &RayNode,
    ) -> Result<TransportLedger, String> {
        if !valid_node(left) || !valid_node(right) || right.eta <= left.eta {
            return Err(
                "source packet transport requires expanding non-tilted LRS Bianchi I".into(),
            );
        }
        if self.packets.iter().any(|p| {
            p.ray >= self.directions.len()
                || !p.energy_ev.is_finite()
                || p.energy_ev < HI_EDGE_EV
                || !p.per_h.is_finite()
                || p.per_h < 0.
                || !p.birth_energy_ev.is_finite()
                || p.birth_energy_ev < HI_EDGE_EV
                || !p.birth_eta.is_finite()
                || p.birth_eta > left.eta
        }) {
            return Err("invalid packet state".into());
        }
        let mut new_dirs = Vec::with_capacity(self.directions.len());
        let mut ratios = Vec::with_capacity(self.directions.len());
        let mut new_weights = Vec::with_capacity(self.directions.len());
        let flrw = left
            .shear
            .iter()
            .flatten()
            .chain(right.shear.iter().flatten())
            .all(|&x| x == 0.);
        for (i, &d) in self.directions.iter().enumerate() {
            // Exactly isotropic geometry has a common Killing redshift.
            // Do not introduce ray-dependent roundoff into subsequent
            // discontinuous compression-bin/threshold decisions.
            if flrw {
                new_dirs.push(d);
                ratios.push((left.eta - right.eta).exp());
                new_weights.push(self.weights[i]);
                continue;
            }
            let ray = advance_ray(left, right, d)?;
            let r = ray.log_energy.exp();
            if !(0. < r && r <= 1.) {
                return Err("non-redshifting ray in expanding source lane".into());
            }
            new_dirs.push(ray.e);
            ratios.push(r);
            new_weights.push(self.weights[i] * ray.log_area.exp());
        }
        let w = sum(new_weights.iter().copied());
        if !w.is_finite() || w <= 0. {
            return Err("invalid angular birth measure".into());
        }
        if !flrw {
            for a in &mut new_weights {
                *a /= w;
            }
        }
        let mut work = Vec::with_capacity(self.packets.len());
        let mut momentum_work = Vec::with_capacity(self.packets.len());
        let mut boundary_pz = Vec::new();
        let mut crossing_energy_error = 0_f64;
        let mut escaped = Vec::new();
        let mut kept = Vec::with_capacity(self.packets.len());
        let mut max_support_error = 0_f64;
        for &p in &self.packets {
            let e = p.energy_ev * ratios[p.ray];
            // Expanding LRS: energy is monotone and crossing occurs exactly
            // at the Verner HI fit cutoff. Binding thresholds stay in REI.
            let stop = if e < HI_EDGE_EV { HI_EDGE_EV } else { e };
            work.push(p.per_h * (p.energy_ev - stop));
            let old_pz = p.per_h * p.energy_ev * self.directions[p.ray][2];
            if e < HI_EDGE_EV {
                escaped.push(p.per_h);
                let mu = if flrw || p.energy_ev == HI_EDGE_EV {
                    self.directions[p.ray][2]
                } else {
                    // Exact Killing components for diagonal LRS I with
                    // linearly interpolated accepted shear. The BASS full-step
                    // ray still owns the survivor map. Crossing uses the exact
                    // local LRS geodesic, not a guessed endpoint direction.
                    let dir = self.directions[p.ray];
                    let h = right.eta - left.eta;
                    let at = |t: f64| {
                        let q: [f64; 3] = std::array::from_fn(|i| {
                            let integ = h
                                * (t * left.shear[i][i]
                                    + 0.5 * t * t * (right.shear[i][i] - left.shear[i][i]));
                            dir[i] * (-h * t - integ).exp()
                        });
                        let r = q.iter().map(|v| v * v).sum::<f64>().sqrt();
                        (p.energy_ev * r, q[2] / r)
                    };
                    let (mut lo, mut hi) = (0., 1.);
                    if at(hi).0 > HI_EDGE_EV {
                        return Err("LRS crossing inconsistent with accepted ray map".into());
                    }
                    for _ in 0..52 {
                        let t = (lo + hi) * 0.5;
                        if at(t).0 > HI_EDGE_EV {
                            lo = t
                        } else {
                            hi = t
                        }
                    }
                    let (en, mu) = at((lo + hi) * 0.5);
                    crossing_energy_error =
                        crossing_energy_error.max((en - HI_EDGE_EV).abs() / HI_EDGE_EV);
                    mu
                };
                let q = p.per_h * HI_EDGE_EV * mu;
                boundary_pz.push(q);
                momentum_work.push(old_pz - q);
            } else {
                momentum_work.push(old_pz - p.per_h * e * new_dirs[p.ray][2]);
                max_support_error = max_support_error.max((e / p.birth_energy_ev - 1.).max(0.));
                kept.push(Packet { energy_ev: e, ..p });
            }
        }
        let bn = sum(escaped.into_iter());
        self.packets = kept;
        self.directions = new_dirs;
        self.weights = new_weights;
        Ok(TransportLedger {
            boundary_n: bn,
            boundary_u: bn * HI_EDGE_EV,
            redshift_work: sum(work.into_iter()),
            boundary_pz: sum(boundary_pz.into_iter()),
            redshift_pz: sum(momentum_work.into_iter()),
            crossing_energy_error,
            max_support_error,
        })
    }
    /// Positive endpoint quadrature on existing physical support. Same ray
    /// and actual Verner threshold region, bounded log-energy span.
    /// Representative birth labels remain exact; their weights are no longer
    /// the uncompressed birth-cohort weights. No invented energy or direction.
    pub fn compress(&mut self, width: f64) -> Result<CompressionLedger, String> {
        self.compress_impl(width, None)
    }
    pub fn compress_rate_checked(
        &mut self,
        width: f64,
        guard: RateGuard,
        tol: f64,
    ) -> Result<CompressionLedger, String> {
        guard.validate()?;
        if !tol.is_finite() || !(1e-10..=0.01).contains(&tol) {
            return Err("compression rate tolerance domain".into());
        }
        self.compress_impl(width, Some((guard, tol)))
    }
    fn compress_impl(
        &mut self,
        width: f64,
        guard: Option<(RateGuard, f64)>,
    ) -> Result<CompressionLedger, String> {
        if !width.is_finite()
            || !(1e-5..=0.25).contains(&width)
            || self.packets.iter().any(|p| {
                p.ray >= self.directions.len()
                    || !p.energy_ev.is_finite()
                    || p.energy_ev < HI_EDGE_EV
                    || !p.per_h.is_finite()
                    || p.per_h < 0.
                    || !p.birth_eta.is_finite()
                    || !p.birth_energy_ev.is_finite()
                    || p.energy_ev > p.birth_energy_ev * (1. + 2e-13)
            })
        {
            return Err("invalid endpoint compression domain".into());
        }
        let mut groups = std::collections::BTreeMap::<(usize, usize, i64), Vec<Packet>>::new();
        let edges = [HI_EDGE_EV, 24.59, 54.42];
        for &p in &self.packets {
            if p.per_h == 0. {
                continue;
            }
            let region = edges.partition_point(|e| *e <= p.energy_ev) - 1;
            let bin = ((p.energy_ev / edges[region]).ln() / width).floor() as i64;
            groups.entry((p.ray, region, bin)).or_default().push(p);
        }
        let mut r = CompressionLedger {
            before: self.packets.len(),
            ..Default::default()
        };
        let mut out = Vec::new();
        // Depth-first per-group splitting, with deterministic order. The
        // original unguarded path still follows the original group order.
        let mut todo: Vec<_> = groups.into_values().rev().collect();
        while let Some(mut g) = todo.pop() {
            if g.len() <= 2 {
                out.extend(g);
                continue;
            }
            let lo = *g
                .iter()
                .min_by(|a, b| a.energy_ev.total_cmp(&b.energy_ev))
                .unwrap();
            let hi = *g
                .iter()
                .max_by(|a, b| a.energy_ev.total_cmp(&b.energy_ev))
                .unwrap();
            let n = sum(g.iter().map(|p| p.per_h));
            let u = sum(g.iter().map(|p| p.per_h * p.energy_ev));
            if !n.is_finite() || !u.is_finite() || n <= 0. || u <= 0. {
                return Err("nonfinite compression stock".into());
            }
            let span = hi.energy_ev - lo.energy_ev;
            let (a, b) = if span == 0. {
                (n, 0.)
            } else {
                (
                    sum(g
                        .iter()
                        .map(|p| p.per_h * ((hi.energy_ev - p.energy_ev) / span))),
                    sum(g
                        .iter()
                        .map(|p| p.per_h * ((p.energy_ev - lo.energy_ev) / span))),
                )
            };
            if !a.is_finite() || !b.is_finite() || a < 0. || b < 0. {
                return Err("invalid endpoint weights".into());
            }
            let nd = ((a + b) - n).abs() / n;
            let ud = (a * lo.energy_ev + b * hi.energy_ev - u).abs() / u;
            if nd > 3e-14 || ud > 3e-14 {
                return Err("endpoint compression moment defect".into());
            }
            if let Some((ctx, tol)) = guard {
                let q = [Packet { per_h: a, ..lo }, Packet { per_h: b, ..hi }];
                let err = rate_moment_error(&g, &q, ctx)?;
                if err > tol {
                    g.sort_by(|a, b| a.energy_ev.total_cmp(&b.energy_ev));
                    let right = g.split_off(g.len() / 2);
                    todo.push(right);
                    todo.push(g);
                    r.rate_splits += 1;
                    continue;
                }
                r.max_rate_relative = r.max_rate_relative.max(err);
            }
            r.max_number_relative = r.max_number_relative.max(nd);
            r.max_energy_relative = r.max_energy_relative.max(ud);
            r.max_log_span = r.max_log_span.max((hi.energy_ev / lo.energy_ev).ln());
            if a > 0. {
                out.push(Packet { per_h: a, ..lo });
            }
            if b > 0. {
                out.push(Packet { per_h: b, ..hi });
            }
        }
        r.after = out.len();
        self.packets = out;
        Ok(r)
    }
    /// Positive cell-integrated number/energy source at the actual birth time.
    pub fn inject(
        &mut self,
        eta: f64,
        rate_per_h_s: f64,
        dt: f64,
        cells: &[(f64, f64)],
    ) -> Result<(f64, f64), String> {
        if !eta.is_finite()
            || !rate_per_h_s.is_finite()
            || rate_per_h_s < 0.
            || !dt.is_finite()
            || dt <= 0.
            || cells.is_empty()
            || cells
                .iter()
                .any(|&(e, w)| !e.is_finite() || e < HI_EDGE_EV || !w.is_finite() || w <= 0.)
            || (sum(cells.iter().map(|x| x.1)) - 1.).abs() > 2e-12
            || self.packets.len() + cells.len() * self.weights.len() > 2_000_000
        {
            return Err("invalid or oversized source birth".into());
        }
        let n = rate_per_h_s * dt;
        if !n.is_finite() {
            return Err("source birth overflow".into());
        }
        if n == 0. {
            return Ok((0., 0.));
        }
        for (ray, w) in self.weights.iter().enumerate() {
            for &(e, f) in cells {
                self.packets.push(Packet {
                    ray,
                    energy_ev: e,
                    per_h: n * w * f,
                    birth_eta: eta,
                    birth_energy_ev: e,
                });
            }
        }
        Ok((n, n * sum(cells.iter().map(|(e, w)| e * w))))
    }
}
pub fn sum(it: impl Iterator<Item = f64>) -> f64 {
    let (mut s, mut c) = (0_f64, 0_f64);
    for x in it {
        let t = s + x;
        c += if s.abs() >= x.abs() {
            (s - t) + x
        } else {
            (x - t) + s
        };
        s = t;
    }
    s + c
}
