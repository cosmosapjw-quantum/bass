//! C3 optional constant-H directional Bianchi-I reference: threshold-aware
//! finite-time frozen-gas absorption. No production AXBI Driver/chemistry coupling.
//! Each packet retains its exact covariant spatial momentum during free flight.
use crate::axbi_q_reference::CovariantPhoton;
use crate::{Absorber, AtomicProvider, ForwardError, GeometrySnapshot, HHeModel};

fn bad() -> ForwardError {
    ForwardError::InvalidInput("AXBI_Q_EVENT_DOMAIN")
}
fn valid(x: f64) -> bool {
    x.is_finite() && x >= 0.0
}

#[derive(Clone, Debug)]
pub struct EvolvingPacket {
    pub final_packet: CovariantPhoton,
    pub final_energy_ev: f64,
    pub absorbed_per_h: [f64; 3],
    pub binding_ev_per_h: f64,
    pub heat_ev_per_h: f64,
    pub redshift_work_ev_per_h: f64,
    pub threshold_crossings: usize,
}

/// Forward evolution on an EXACT constant directional Hubble-rate background.
/// Optical depth is approximated by midpoint quadrature within intervals that
/// are split at exact-fit threshold crossings; photon survival is exponential.
/// Gas proper absorber densities are held constant and independent of chemistry.
pub fn advance_frozen_expanding(
    packet: &CovariantPhoton,
    g0: &GeometrySnapshot,
    h_per_s: [f64; 3],
    neutrals_cm3: [f64; 3],
    duration_s: f64,
    slices: usize,
) -> Result<EvolvingPacket, ForwardError> {
    g0.volume_factor()?;
    if !(1..=4096).contains(&slices)
        || !valid(duration_s)
        || !h_per_s.iter().all(|x| valid(*x))
        || !neutrals_cm3.iter().all(|x| valid(*x))
        || !valid(packet.photons_per_h)
    {
        return Err(bad());
    }
    let p0: [f64; 3] = std::array::from_fn(|i| packet.k_ev[i] / g0.scale_factors[i]);
    if !p0.iter().all(|x| x.is_finite()) {
        return Err(bad());
    }
    let p_xy = p0[0].hypot(p0[1]);
    // FLRW one exponential; axisymmetry two. No physical approximation.
    let energy = |t: f64| -> Result<f64, ForwardError> {
        let e = if h_per_s[0] == h_per_s[1] && h_per_s[1] == h_per_s[2] {
            p_xy.hypot(p0[2]) * (-h_per_s[0] * t).exp()
        } else if h_per_s[0] == h_per_s[1] {
            (p_xy * (-h_per_s[0] * t).exp()).hypot(p0[2] * (-h_per_s[2] * t).exp())
        } else {
            let p: [f64; 3] = std::array::from_fn(|i| p0[i] * (-h_per_s[i] * t).exp());
            p[0].hypot(p[1]).hypot(p[2])
        };
        if !(e.is_finite() && e > 0.0 && e <= 50_000.0) {
            return Err(bad());
        }
        Ok(e)
    };
    let initial = energy(0.)?;
    let end = energy(duration_s)?;
    let mut checkpoints = vec![0.0];
    if duration_s > 0.0 {
        for edge in [13.60, 24.59, 54.42] {
            if initial > edge && end < edge {
                let (mut lo, mut hi) = (0.0, duration_s);
                for _ in 0..64 {
                    let mid = lo + 0.5 * (hi - lo);
                    if energy(mid)? > edge {
                        lo = mid;
                    } else {
                        hi = mid;
                    }
                }
                let t = lo + 0.5 * (hi - lo);
                if t > 0.0 && t < duration_s {
                    checkpoints.push(t);
                }
            }
        }
        checkpoints.push(duration_s);
    }
    checkpoints.sort_by(|a, b| a.total_cmp(b));
    checkpoints.dedup_by(|a, b| a.to_bits() == b.to_bits());
    let threshold_crossings = checkpoints.len().saturating_sub(2);
    let atomic = AtomicProvider::reference();
    let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
    let binding = HHeModel::controlled_fixture().threshold_ev;
    let c = HHeModel::controlled_fixture().c_cm_s;
    let mut n = packet.photons_per_h;
    let mut absorbed = [0.0; 3];
    let mut heat = 0.0;
    let mut bound = 0.0;
    let mut work = 0.0;
    if duration_s > 0.0 {
        for pair in checkpoints.windows(2) {
            let (a, b) = (pair[0], pair[1]);
            if b <= a {
                continue;
            }
            let nstep = ((slices as f64) * ((b - a) / duration_s)).ceil() as usize;
            let nstep = nstep.max(1);
            for i in 0..nstep {
                let left = a + (b - a) * i as f64 / nstep as f64;
                let right = a + (b - a) * (i + 1) as f64 / nstep as f64;
                let mid = left + 0.5 * (right - left);
                let el = energy(left)?;
                let em = energy(mid)?;
                let er = energy(right)?;
                work += n * (el - em);
                let mut rates = [0.0; 3];
                for k in 0..3 {
                    rates[k] = if neutrals_cm3[k] == 0.0 || em < [13.60, 24.59, 54.42][k] {
                        0.0
                    } else {
                        c * neutrals_cm3[k] * atomic.cross_section(species[k], em)?
                    };
                    if !valid(rates[k]) {
                        return Err(bad());
                    }
                }
                let total: f64 = rates.iter().sum();
                if !valid(total) {
                    return Err(bad());
                }
                if total > 0.0 {
                    let lost = n * -(-total * (right - left)).exp_m1();
                    if !valid(lost) {
                        return Err(bad());
                    }
                    for k in 0..3 {
                        let taken = lost * rates[k] / total;
                        absorbed[k] += taken;
                        bound += taken * binding[k];
                        heat += taken * (em - binding[k]);
                    }
                    n -= lost;
                }
                work += n * (em - er);
            }
        }
    }
    if !valid(n) || !valid(heat) || !valid(bound) || !valid(work) {
        return Err(bad());
    }
    Ok(EvolvingPacket {
        final_packet: CovariantPhoton {
            k_ev: packet.k_ev,
            photons_per_h: n,
        },
        final_energy_ev: end,
        absorbed_per_h: absorbed,
        binding_ev_per_h: bound,
        heat_ev_per_h: heat,
        redshift_work_ev_per_h: work,
        threshold_crossings,
    })
}

/// Parallelism is scoped, capped at 4 worker threads and only used for
/// independent packets at >=512 packets/worker. Output order is unchanged.
/// No mutation of shared gas state and no nested Rayon global worker pool.
pub fn advance_batch(
    packets: &[CovariantPhoton],
    g: &GeometrySnapshot,
    h: [f64; 3],
    n: [f64; 3],
    dt: f64,
    slices: usize,
    threads: usize,
) -> Result<Vec<EvolvingPacket>, ForwardError> {
    if !(1..=4).contains(&threads) {
        return Err(bad());
    }
    if packets.is_empty() {
        return Ok(Vec::new());
    }
    if threads == 1 || packets.len() < threads * 512 {
        return packets
            .iter()
            .map(|p| advance_frozen_expanding(p, g, h, n, dt, slices))
            .collect();
    }
    let size = packets.len().div_ceil(threads);
    std::thread::scope(|scope| {
        let mut handles = Vec::new();
        for chunk in packets.chunks(size) {
            handles.push(
                scope.spawn(move || -> Result<Vec<EvolvingPacket>, ForwardError> {
                    chunk
                        .iter()
                        .map(|p| advance_frozen_expanding(p, g, h, n, dt, slices))
                        .collect()
                }),
            );
        }
        let mut all = Vec::with_capacity(packets.len());
        for handle in handles {
            let group = handle.join().map_err(|_| bad())??;
            all.extend(group);
        }
        Ok(all)
    })
}

/// Contiguous structure-of-arrays form for repeated energy readout at a common
/// Bianchi-I geometry. This is SIMD-friendly, but SIMD machine instructions
/// or a speedup must be verified on the actual build; no such claim is implicit.
#[derive(Clone, Debug)]
pub struct EnergySoA {
    kx: Vec<f64>,
    ky: Vec<f64>,
    kz: Vec<f64>,
}
impl EnergySoA {
    pub fn from_packets(packets: &[CovariantPhoton]) -> Result<Self, ForwardError> {
        let mut x = Vec::with_capacity(packets.len());
        let mut y = Vec::with_capacity(packets.len());
        let mut z = Vec::with_capacity(packets.len());
        for p in packets {
            if !p.k_ev.iter().all(|v| v.is_finite()) || !valid(p.photons_per_h) {
                return Err(bad());
            }
            x.push(p.k_ev[0]);
            y.push(p.k_ev[1]);
            z.push(p.k_ev[2]);
        }
        Ok(Self {
            kx: x,
            ky: y,
            kz: z,
        })
    }
    pub fn len(&self) -> usize {
        self.kx.len()
    }
    pub fn is_empty(&self) -> bool {
        self.kx.is_empty()
    }
    pub fn allocated_bytes(&self) -> usize {
        (self.kx.capacity() + self.ky.capacity() + self.kz.capacity()) * std::mem::size_of::<f64>()
    }
    /// Uses a single geometry check and three precomputed inverse scale
    /// factors for the entire batch. This path is valid for physically capped
    /// packet energies <=50keV; the original scalar hypot path remains the
    /// robust reference for arbitrary representable values.
    pub fn energies_at(&self, g: &GeometrySnapshot) -> Result<Vec<f64>, ForwardError> {
        g.volume_factor()?;
        let inv: [f64; 3] = std::array::from_fn(|i| 1.0 / g.scale_factors[i]);
        let mut output = Vec::with_capacity(self.len());
        for i in 0..self.len() {
            let x = self.kx[i] * inv[0];
            let y = self.ky[i] * inv[1];
            let z = self.kz[i] * inv[2];
            let e = (x * x + y * y + z * z).sqrt();
            if !(e > 0.0 && e.is_finite() && e <= 50_000.0) {
                return Err(bad());
            }
            output.push(e);
        }
        Ok(output)
    }
}
