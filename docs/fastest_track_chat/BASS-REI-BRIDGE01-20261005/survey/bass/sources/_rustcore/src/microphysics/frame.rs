//! Material Lorentz frame at a Bianchi normal observer.
//! This is distinct from kinetic::comoving::Frame, which maps a momentum grid.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum FrameError {
    InvalidVelocity,
    InvalidDirection,
    InvalidEnergy,
    NonFiniteSource,
    ModeDirectionMismatch,
    PairEnergyMismatch {
        material_sum_ev: f64,
        transition_ev: f64,
    },
}

#[derive(Clone, Copy, Debug)]
pub struct MaterialFrame {
    beta_normal: [f64; 3],
    gamma: f64,
}

impl MaterialFrame {
    pub fn new(beta_normal: [f64; 3]) -> Result<Self, FrameError> {
        if beta_normal.iter().any(|v| !v.is_finite()) {
            return Err(FrameError::InvalidVelocity);
        }
        let beta2: f64 = beta_normal.iter().map(|v| v * v).sum();
        if !beta2.is_finite() || beta2 >= 1.0 {
            return Err(FrameError::InvalidVelocity);
        }
        Ok(Self {
            beta_normal,
            gamma: 1.0 / (1.0 - beta2).sqrt(),
        })
    }

    pub fn gamma(self) -> f64 {
        self.gamma
    }

    /// The ray clock converts a material-frame occupation collision derivative
    /// to normal time. It is direction dependent.
    pub fn doppler(self, e_normal: [f64; 3]) -> Result<f64, FrameError> {
        if e_normal.iter().any(|v| !v.is_finite()) {
            return Err(FrameError::InvalidDirection);
        }
        let norm2: f64 = e_normal.iter().map(|v| v * v).sum();
        if (norm2 - 1.0).abs() > 1.0e-12 {
            return Err(FrameError::InvalidDirection);
        }
        let dot: f64 = self
            .beta_normal
            .iter()
            .zip(e_normal)
            .map(|(b, e)| b * e)
            .sum();
        let doppler = self.gamma * (1.0 - dot);
        if !doppler.is_finite() || doppler <= 0.0 {
            return Err(FrameError::InvalidDirection);
        }
        Ok(doppler)
    }

    pub fn material_energy_ev(self, normal_ev: f64, e_normal: [f64; 3]) -> Result<f64, FrameError> {
        if !normal_ev.is_finite() || normal_ev <= 0.0 {
            return Err(FrameError::InvalidEnergy);
        }
        let energy = self.doppler(e_normal)? * normal_ev;
        if !energy.is_finite() || energy <= 0.0 {
            return Err(FrameError::InvalidEnergy);
        }
        Ok(energy)
    }

    pub fn photon_normal_time_source(
        self,
        material_source: f64,
        e_normal: [f64; 3],
    ) -> Result<f64, FrameError> {
        if !material_source.is_finite() {
            return Err(FrameError::NonFiniteSource);
        }
        let source = self.doppler(e_normal)? * material_source;
        if !source.is_finite() {
            return Err(FrameError::NonFiniteSource);
        }
        Ok(source)
    }

    /// Material proper-density evolution uses dtau_m/dt_n = 1/gamma_m,
    /// independent of photon direction.
    pub fn atomic_normal_time_source(self, material_source: f64) -> Result<f64, FrameError> {
        if !material_source.is_finite() {
            return Err(FrameError::NonFiniteSource);
        }
        let source = material_source / self.gamma;
        if !source.is_finite() {
            return Err(FrameError::NonFiniteSource);
        }
        Ok(source)
    }

    pub fn pair_material_fraction(
        self,
        normal_ev: [f64; 2],
        directions_normal: [[f64; 3]; 2],
        transition_ev: f64,
    ) -> Result<f64, FrameError> {
        if !transition_ev.is_finite() || transition_ev <= 0.0 {
            return Err(FrameError::InvalidEnergy);
        }
        let e1 = self.material_energy_ev(normal_ev[0], directions_normal[0])?;
        let e2 = self.material_energy_ev(normal_ev[1], directions_normal[1])?;
        let sum = e1 + e2;
        if !sum.is_finite() {
            return Err(FrameError::InvalidEnergy);
        }
        if (sum - transition_ev).abs() > 1.0e-12 * transition_ev {
            return Err(FrameError::PairEnergyMismatch {
                material_sum_ev: sum,
                transition_ev,
            });
        }
        Ok(e1 / transition_ev)
    }
}
