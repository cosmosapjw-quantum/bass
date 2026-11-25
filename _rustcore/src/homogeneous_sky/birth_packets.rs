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
    pub max_support_error: f64,
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
        for (i, &d) in self.directions.iter().enumerate() {
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
        for a in &mut new_weights {
            *a /= w;
        }
        let mut work = Vec::with_capacity(self.packets.len());
        let mut escaped = Vec::new();
        let mut kept = Vec::with_capacity(self.packets.len());
        let mut max_support_error = 0_f64;
        for &p in &self.packets {
            let e = p.energy_ev * ratios[p.ray];
            // Expanding LRS: energy is monotone and crossing occurs exactly
            // at the Verner HI fit cutoff. Binding thresholds stay in REI.
            let stop = if e < HI_EDGE_EV { HI_EDGE_EV } else { e };
            work.push(p.per_h * (p.energy_ev - stop));
            if e < HI_EDGE_EV {
                escaped.push(p.per_h)
            } else {
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
            max_support_error,
        })
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
