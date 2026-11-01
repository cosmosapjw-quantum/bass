//! Positive packet measure and conservative angular/energy deposition.
use crate::{CharacteristicRay, ForwardError, GeometrySnapshot};

fn invalid(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}

fn nonnegative(x: f64, tag: &'static str) -> Result<f64, ForwardError> {
    if x.is_finite() && x >= 0.0 {
        Ok(x)
    } else {
        Err(invalid(tag))
    }
}

#[derive(Clone, Copy, Default)]
struct MeasureSum {
    sum: f64,
    correction: f64,
}
impl MeasureSum {
    fn add(&mut self, value: f64) -> Result<(), ForwardError> {
        nonnegative(value, "PhotonMeasure")?;
        let next = nonnegative(self.sum + value, "PhotonMeasureOverflow")?;
        let error = if self.sum >= value {
            (self.sum - next) + value
        } else {
            (value - next) + self.sum
        };
        self.correction += error;
        if !self.correction.is_finite() {
            return Err(invalid("PhotonMeasureOverflow"));
        }
        self.sum = next;
        Ok(())
    }
    fn value(self) -> Result<f64, ForwardError> {
        nonnegative(self.sum + self.correction, "PhotonMeasureOverflow")
    }
}
fn total(values: impl Iterator<Item = f64>) -> Result<f64, ForwardError> {
    let mut sum = MeasureSum::default();
    for value in values {
        sum.add(value)?;
    }
    sum.value()
}

#[derive(Clone, Debug, PartialEq)]
pub struct PhotonPacket {
    pub ray: CharacteristicRay,
    pub comoving_count_cm3: f64,
}

impl PhotonPacket {
    pub fn new(ray: CharacteristicRay, comoving_count_cm3: f64) -> Result<Self, ForwardError> {
        let ray = CharacteristicRay::new(ray.energy_ev, ray.direction, ray.occupation)?;
        nonnegative(comoving_count_cm3, "PhotonCount")?;
        Ok(Self {
            ray,
            comoving_count_cm3,
        })
    }

    fn deposited_energy(&self) -> Result<f64, ForwardError> {
        Self::new(self.ray, self.comoving_count_cm3)?;
        let energy = nonnegative(
            self.ray.energy_ev * self.comoving_count_cm3,
            "PhotonEnergyMeasure",
        )?;
        if energy == 0.0 && self.comoving_count_cm3 != 0.0 {
            return Err(invalid("PhotonEnergyUnderflow"));
        }
        Ok(energy)
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct RadiationState {
    pub geometry: GeometrySnapshot,
    pub packets: Vec<PhotonPacket>,
}

impl RadiationState {
    pub fn new(
        geometry: GeometrySnapshot,
        packets: Vec<PhotonPacket>,
    ) -> Result<Self, ForwardError> {
        geometry.volume_factor()?;
        let packets: Vec<_> = packets
            .into_iter()
            .map(|packet| PhotonPacket::new(packet.ray, packet.comoving_count_cm3))
            .collect::<Result<_, _>>()?;
        for packet in &packets {
            packet.deposited_energy()?;
        }
        let state = Self { geometry, packets };
        state.comoving_photon_count()?;
        state.comoving_energy_ev_cm3()?;
        Ok(state)
    }

    pub fn transport(&self, to: GeometrySnapshot) -> Result<Self, ForwardError> {
        self.validate()?;
        to.volume_factor()?;
        let mut packets = Vec::with_capacity(self.packets.len());
        for packet in &self.packets {
            packets.push(PhotonPacket::new(
                packet.ray.pullback(&self.geometry, &to)?,
                packet.comoving_count_cm3,
            )?);
        }
        Self::new(to, packets)
    }

    fn validate(&self) -> Result<(), ForwardError> {
        self.geometry.volume_factor()?;
        for packet in &self.packets {
            PhotonPacket::new(packet.ray, packet.comoving_count_cm3)?;
        }
        Ok(())
    }

    pub fn comoving_photon_count(&self) -> Result<f64, ForwardError> {
        self.validate()?;
        total(self.packets.iter().map(|packet| packet.comoving_count_cm3))
    }

    pub fn proper_photon_density_cm3(&self) -> Result<f64, ForwardError> {
        let count = self.comoving_photon_count()?;
        let density = nonnegative(
            count / self.geometry.volume_factor()?,
            "PhotonProperDensity",
        )?;
        if density == 0.0 && count != 0.0 {
            return Err(invalid("PhotonDensityUnderflow"));
        }
        Ok(density)
    }

    pub fn comoving_energy_ev_cm3(&self) -> Result<f64, ForwardError> {
        self.validate()?;
        let mut sum = MeasureSum::default();
        for packet in &self.packets {
            sum.add(packet.deposited_energy()?)?;
        }
        sum.value()
    }

    pub fn remap(&self, grid: &PhotonGrid) -> Result<PhotonBins, ForwardError> {
        self.validate()?;
        grid.validate()?;
        let shape = grid.bin_count()?;
        let size = shape
            .checked_add(2)
            .ok_or_else(|| invalid("PhotonGridShapeOverflow"))?;
        let mut counts = Vec::new();
        counts
            .try_reserve_exact(size)
            .map_err(|_| invalid("PhotonGridAllocation"))?;
        counts.resize(size, MeasureSum::default());
        let mut energies = Vec::new();
        energies
            .try_reserve_exact(size)
            .map_err(|_| invalid("PhotonGridAllocation"))?;
        energies.resize(size, MeasureSum::default());
        let nmu = grid.mu_edges.len() - 1;
        for packet in &self.packets {
            let packet = PhotonPacket::new(packet.ray, packet.comoving_count_cm3)?;
            let energy = packet.deposited_energy()?;
            let count = packet.comoving_count_cm3;
            let ray_energy = packet.ray.energy_ev;
            let index = if ray_energy < grid.energy_edges_ev[0] {
                shape
            } else if ray_energy > *grid.energy_edges_ev.last().expect("validated edges") {
                shape + 1
            } else {
                let ebin = grid
                    .energy_edges_ev
                    .partition_point(|edge| *edge <= ray_energy)
                    .saturating_sub(1)
                    .min(grid.energy_edges_ev.len() - 2);
                let mu = packet.ray.direction[2];
                let mubin = grid
                    .mu_edges
                    .partition_point(|edge| *edge <= mu)
                    .saturating_sub(1)
                    .min(nmu - 1);
                let mut phi = packet.ray.direction[1].atan2(packet.ray.direction[0]);
                if phi < 0.0 {
                    phi += std::f64::consts::TAU;
                }
                let pbin = ((phi / std::f64::consts::TAU) * grid.phi_bins as f64) as usize;
                let pbin = pbin.min(grid.phi_bins - 1);
                (ebin * nmu + mubin) * grid.phi_bins + pbin
            };
            counts[index].add(count)?;
            energies[index].add(energy)?;
        }
        let bins = PhotonBins {
            counts_cm3: counts[..shape]
                .iter()
                .map(|sum| sum.value())
                .collect::<Result<_, _>>()?,
            energy_ev_cm3: energies[..shape]
                .iter()
                .map(|sum| sum.value())
                .collect::<Result<_, _>>()?,
            below_count_cm3: counts[shape].value()?,
            above_count_cm3: counts[shape + 1].value()?,
            below_energy_ev_cm3: energies[shape].value()?,
            above_energy_ev_cm3: energies[shape + 1].value()?,
        };
        bins.total_count()?;
        bins.total_energy_ev_cm3()?;
        Ok(bins)
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct PhotonGrid {
    pub energy_edges_ev: Vec<f64>,
    pub mu_edges: Vec<f64>,
    pub phi_bins: usize,
}

impl PhotonGrid {
    pub fn new(
        energy_edges_ev: Vec<f64>,
        mu_edges: Vec<f64>,
        phi_bins: usize,
    ) -> Result<Self, ForwardError> {
        let grid = Self {
            energy_edges_ev,
            mu_edges,
            phi_bins,
        };
        grid.validate()?;
        Ok(grid)
    }

    fn validate(&self) -> Result<(), ForwardError> {
        if self.energy_edges_ev.len() < 2 || self.mu_edges.len() < 2 || self.phi_bins == 0 {
            return Err(invalid("PhotonGridShape"));
        }
        for edges in [&self.energy_edges_ev, &self.mu_edges] {
            if edges.iter().any(|x| !x.is_finite())
                || edges.windows(2).any(|pair| pair[0] >= pair[1])
            {
                return Err(invalid("PhotonGridEdges"));
            }
        }
        if self.energy_edges_ev[0] <= 0.0
            || self.mu_edges[0] != -1.0
            || *self.mu_edges.last().expect("checked length") != 1.0
        {
            return Err(invalid("PhotonGridDomain"));
        }
        self.bin_count()?;
        Ok(())
    }

    fn bin_count(&self) -> Result<usize, ForwardError> {
        (self.energy_edges_ev.len() - 1)
            .checked_mul(self.mu_edges.len() - 1)
            .and_then(|n| n.checked_mul(self.phi_bins))
            .filter(|n| *n <= isize::MAX as usize)
            .ok_or_else(|| invalid("PhotonGridShapeOverflow"))
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct PhotonBins {
    pub counts_cm3: Vec<f64>,
    pub energy_ev_cm3: Vec<f64>,
    pub below_count_cm3: f64,
    pub above_count_cm3: f64,
    pub below_energy_ev_cm3: f64,
    pub above_energy_ev_cm3: f64,
}

impl PhotonBins {
    pub fn total_count(&self) -> Result<f64, ForwardError> {
        total(
            self.counts_cm3
                .iter()
                .chain([&self.below_count_cm3, &self.above_count_cm3])
                .copied(),
        )
    }

    pub fn total_energy_ev_cm3(&self) -> Result<f64, ForwardError> {
        total(
            self.energy_ev_cm3
                .iter()
                .chain([&self.below_energy_ev_cm3, &self.above_energy_ev_cm3])
                .copied(),
        )
    }
}
