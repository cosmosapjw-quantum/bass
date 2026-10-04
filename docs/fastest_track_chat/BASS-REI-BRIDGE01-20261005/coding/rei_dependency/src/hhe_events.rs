//! Synthetic static H/He event model. All rates use proper number densities.
use crate::ForwardError;

#[derive(Clone, Copy, Debug)]
pub struct HHeModel {
    pub n_h_cm3: f64,
    pub n_he_cm3: f64,
    pub c_cm_s: f64,
    pub kb_erg_k: f64,
    pub ev_erg: f64,
    pub threshold_ev: [f64; 3],
    pub photon_energy_ev: [f64; 3],
    pub sigma_cm2: [[f64; 3]; 3],
    pub alpha_cm3_s: [f64; 3],
    pub beta_cm3_s: [f64; 3],
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct HHeState {
    pub fractions: [f64; 3],
    pub u_erg_cm3: f64,
    pub photon_cm3: [f64; 3],
    pub escaped_erg_cm3: f64,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct HHeEvents {
    pub photo_per_cm3: [[f64; 3]; 3],
    pub collision_per_cm3: [f64; 3],
    pub recombination_per_cm3: [f64; 3],
}

impl HHeEvents {
    pub(crate) fn plus(self, other: Self) -> Self {
        let mut out = self;
        for a in 0..3 {
            for g in 0..3 {
                out.photo_per_cm3[a][g] += other.photo_per_cm3[a][g];
            }
            out.collision_per_cm3[a] += other.collision_per_cm3[a];
            out.recombination_per_cm3[a] += other.recombination_per_cm3[a];
        }
        out
    }
}

#[derive(Clone, Copy, Debug)]
pub struct HHeRhs {
    pub derivative: [f64; 7],
    pub photo_per_cm3_s: [[f64; 3]; 3],
    pub collision_per_cm3_s: [f64; 3],
    pub recombination_per_cm3_s: [f64; 3],
    pub escaped_energy_rate: f64,
}

fn valid_nonnegative(x: f64) -> bool {
    x.is_finite() && x >= 0.0
}

impl HHeModel {
    pub fn controlled_fixture() -> Self {
        Self {
            n_h_cm3: 1e-4,
            n_he_cm3: 8.3e-6,
            c_cm_s: 29_979_245_800.0,
            kb_erg_k: 1.380_649e-16,
            ev_erg: 1.602_176_634e-12,
            threshold_ev: [13.598_434_599_702, 24.587_389_011, 54.417_76],
            photon_energy_ev: [13.7, 24.7, 54.5],
            sigma_cm2: [
                [6e-18, 1e-18, 1e-19],
                [0.0, 7e-18, 1e-18],
                [0.0, 0.0, 1.5e-18],
            ],
            alpha_cm3_s: [2e-13, 1e-12, 3e-13],
            beta_cm3_s: [1e-16, 1e-17, 1e-18],
        }
    }

    pub(crate) fn validate(&self) -> Result<(), ForwardError> {
        if !valid_nonnegative(self.n_h_cm3)
            || !valid_nonnegative(self.n_he_cm3)
            || !(self.n_h_cm3 + self.n_he_cm3).is_finite()
            || self.n_h_cm3 + self.n_he_cm3 <= 0.0
            || !self.c_cm_s.is_finite()
            || self.c_cm_s <= 0.0
            || !self.kb_erg_k.is_finite()
            || self.kb_erg_k <= 0.0
            || !self.ev_erg.is_finite()
            || self.ev_erg <= 0.0
        {
            return Err(ForwardError::InvalidInput("HHE_MODEL_DOMAIN"));
        }
        for a in 0..3 {
            if !valid_nonnegative(self.threshold_ev[a])
                || !valid_nonnegative(self.alpha_cm3_s[a])
                || !valid_nonnegative(self.beta_cm3_s[a])
            {
                return Err(ForwardError::InvalidInput("HHE_MODEL_DOMAIN"));
            }
            for g in 0..3 {
                let sigma = self.sigma_cm2[a][g];
                if !valid_nonnegative(sigma)
                    || (sigma > 0.0 && self.photon_energy_ev[g] < self.threshold_ev[a])
                {
                    return Err(ForwardError::InvalidInput("HHE_SUBTHRESHOLD_EDGE"));
                }
            }
        }
        if self.photon_energy_ev.iter().any(|&x| !valid_nonnegative(x)) {
            return Err(ForwardError::InvalidInput("HHE_MODEL_DOMAIN"));
        }
        Ok(())
    }

    pub(crate) fn validate_state(&self, s: &HHeState) -> Result<(), ForwardError> {
        self.validate()?;
        let [h, he1, he2] = s.fractions;
        if !valid_nonnegative(h)
            || h > 1.0
            || !valid_nonnegative(he1)
            || !valid_nonnegative(he2)
            || he1 + he2 > 1.0
            || !valid_nonnegative(s.u_erg_cm3)
            || !valid_nonnegative(s.escaped_erg_cm3)
            || s.photon_cm3.iter().any(|&x| !valid_nonnegative(x))
        {
            return Err(ForwardError::InvalidInput("HHE_STATE_DOMAIN"));
        }
        Ok(())
    }

    pub fn electron_density(&self, s: &HHeState) -> Result<f64, ForwardError> {
        self.validate_state(s)?;
        let ne =
            self.n_h_cm3 * s.fractions[0] + self.n_he_cm3 * (s.fractions[1] + 2.0 * s.fractions[2]);
        if !ne.is_finite() {
            return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
        }
        Ok(ne)
    }

    pub fn temperature(&self, s: &HHeState) -> Result<f64, ForwardError> {
        let ne = self.electron_density(s)?;
        let particles = self.n_h_cm3 + self.n_he_cm3 + ne;
        let numerator = 2.0 * s.u_erg_cm3;
        let denominator = 3.0 * self.kb_erg_k * particles;
        if !particles.is_finite()
            || !numerator.is_finite()
            || !denominator.is_finite()
            || denominator <= 0.0
        {
            return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
        }
        let t = numerator / denominator;
        if !t.is_finite() || (s.u_erg_cm3 > 0.0 && t == 0.0) {
            return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
        }
        Ok(t)
    }

    pub fn total_energy(&self, s: &HHeState) -> Result<f64, ForwardError> {
        self.validate_state(s)?;
        let [h, he1, he2] = s.fractions;
        let binding = self.ev_erg
            * (self.n_h_cm3 * h * self.threshold_ev[0]
                + self.n_he_cm3
                    * (he1 * self.threshold_ev[1]
                        + he2 * (self.threshold_ev[1] + self.threshold_ev[2])));
        let photons = self.ev_erg
            * (0..3)
                .map(|g| self.photon_energy_ev[g] * s.photon_cm3[g])
                .sum::<f64>();
        let total = s.u_erg_cm3 + binding + photons + s.escaped_erg_cm3;
        if !total.is_finite() {
            return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
        }
        Ok(total)
    }
}

impl HHeState {
    pub fn controlled_fixture(model: &HHeModel) -> Self {
        let fractions = [0.01, 0.019, 0.001];
        let ne =
            model.n_h_cm3 * fractions[0] + model.n_he_cm3 * (fractions[1] + 2.0 * fractions[2]);
        Self {
            fractions,
            u_erg_cm3: 1.5 * model.kb_erg_k * 1e4 * (model.n_h_cm3 + model.n_he_cm3 + ne),
            photon_cm3: [2e-5, 2e-6, 2e-7],
            escaped_erg_cm3: 0.0,
        }
    }

    pub fn coordinates(&self) -> [f64; 7] {
        [
            self.fractions[0],
            self.fractions[1],
            self.fractions[2],
            self.u_erg_cm3,
            self.photon_cm3[0],
            self.photon_cm3[1],
            self.photon_cm3[2],
        ]
    }
}

pub fn hhe_rhs(model: &HHeModel, state: &HHeState) -> Result<HHeRhs, ForwardError> {
    model.validate_state(state)?;
    let [h, he1, he2] = state.fractions;
    let lower = [
        model.n_h_cm3 * (1.0 - h),
        model.n_he_cm3 * (1.0 - (he1 + he2)),
        model.n_he_cm3 * he1,
    ];
    let upper = [
        model.n_h_cm3 * h,
        model.n_he_cm3 * he1,
        model.n_he_cm3 * he2,
    ];
    let ne = model.electron_density(state)?;
    let temperature = model.temperature(state)?;
    let mut photo = [[0.0; 3]; 3];
    let mut collision = [0.0; 3];
    let mut recombination = [0.0; 3];
    let mut j = [0.0; 3];
    let mut du = 0.0;
    let mut escape = 0.0;
    let mut photon_dot = [0.0; 3];
    for a in 0..3 {
        collision[a] = lower[a] * ne * model.beta_cm3_s[a];
        recombination[a] = upper[a] * ne * model.alpha_cm3_s[a];
        j[a] = collision[a] - recombination[a];
        du -= collision[a] * model.threshold_ev[a] * model.ev_erg
            + recombination[a] * 1.5 * model.kb_erg_k * temperature;
        escape += recombination[a]
            * (model.threshold_ev[a] * model.ev_erg + 1.5 * model.kb_erg_k * temperature);
        for g in 0..3 {
            photo[a][g] = model.c_cm_s * lower[a] * model.sigma_cm2[a][g] * state.photon_cm3[g];
            j[a] += photo[a][g];
            photon_dot[g] -= photo[a][g];
            du += photo[a][g] * (model.photon_energy_ev[g] - model.threshold_ev[a]) * model.ev_erg;
        }
    }
    // Per-capita equations remain meaningful if one nuclear density is zero.
    let per_capita = |a: usize| {
        let lower_fraction = [1.0 - h, 1.0 - (he1 + he2), he1][a];
        let upper_fraction = [h, he1, he2][a];
        let photo_rate: f64 = (0..3)
            .map(|g| model.c_cm_s * model.sigma_cm2[a][g] * state.photon_cm3[g])
            .sum();
        lower_fraction * (photo_rate + ne * model.beta_cm3_s[a])
            - upper_fraction * ne * model.alpha_cm3_s[a]
    };
    let d = [
        per_capita(0),
        per_capita(1) - per_capita(2),
        per_capita(2),
        du,
        photon_dot[0],
        photon_dot[1],
        photon_dot[2],
    ];
    if d.iter().any(|x| !x.is_finite())
        || !escape.is_finite()
        || photo.iter().flatten().any(|x| !x.is_finite())
        || collision
            .iter()
            .chain(recombination.iter())
            .any(|x| !x.is_finite())
    {
        return Err(ForwardError::InvalidInput("HHE_OVERFLOW"));
    }
    Ok(HHeRhs {
        derivative: d,
        photo_per_cm3_s: photo,
        collision_per_cm3_s: collision,
        recombination_per_cm3_s: recombination,
        escaped_energy_rate: escape,
    })
}
