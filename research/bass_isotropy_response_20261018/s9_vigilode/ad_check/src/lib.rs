//! Independent scalar-forward AD oracle for S9 frozen-bank primal callbacks.
//!
//! The dual program below evaluates the primal kernels directly. It does not
//! call BASS/VigilODE analytic derivatives, an ODE solver, or the KL projector.
//! Birth coordinates, source-frame directions, and weights are constants here.
//! This derivative is deliberately distinct from the S8 full-history tangent.
use num_dual::{Dual64, DualNum};

/// Fixed before executing any test; this is a callback comparison criterion,
/// not a relaxation of the 3e-15 angular moment/normalization gate.
pub const CALLBACK_SCALED_GATE: f64 = 5e-13;

#[derive(Clone, Debug, PartialEq)]
pub struct Cohort {
    pub u: f64,
    pub b_birth: f64,
    pub energy_birth: f64,
    pub mu: Vec<f64>,
    pub alpha: Vec<f64>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct FrozenBank {
    pub cohorts: Vec<Cohort>,
    /// donor0 * exp(-decay_lambda * exposure), fixed on this open interval.
    pub donor_amplitude: f64,
    pub cosmological_constant: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct Oracle {
    pub rhs: [f64; 3],
    pub jvp: [f64; 3],
    pub partial_t: [f64; 3],
    /// J v + partial_t * time_seed, for the time-augmented formulation.
    pub total_direction: [f64; 3],
}

#[derive(Clone, Copy, Debug)]
pub struct Analytic {
    pub rhs: [f64; 3],
    pub jacobian: [[f64; 3]; 3],
    pub partial_t: [f64; 3],
    pub energy: f64,
    pub pi: f64,
    pub pi_b: f64,
    pub donor: f64,
}

fn finite_nonnegative(value: f64) -> bool {
    value.is_finite() && value >= 0.0
}

impl FrozenBank {
    pub fn validate(&self, x: f64, state: [f64; 3]) -> Result<(), &'static str> {
        if !x.is_finite() || state.iter().any(|v| !v.is_finite()) || state[0] <= 0.0 {
            return Err("AD_STATE_DOMAIN");
        }
        if !finite_nonnegative(self.donor_amplitude)
            || !finite_nonnegative(self.cosmological_constant)
        {
            return Err("AD_BACKGROUND_DOMAIN");
        }
        for cohort in &self.cohorts {
            if !cohort.u.is_finite() || cohort.u > x || !cohort.b_birth.is_finite()
                || !finite_nonnegative(cohort.energy_birth) || cohort.mu.is_empty()
                || cohort.mu.len() != cohort.alpha.len()
            {
                return Err("AD_COHORT_DOMAIN");
            }
            if cohort.mu.iter().any(|v| !v.is_finite() || v.abs() > 1.0)
                || cohort.alpha.iter().any(|v| !v.is_finite() || *v <= 0.0)
            {
                return Err("AD_ANGULAR_DOMAIN");
            }
            let n = cohort.mu.len();
            for i in 0..n {
                if cohort.mu[i] != -cohort.mu[n - 1 - i]
                    || cohort.alpha[i] != cohort.alpha[n - 1 - i]
                {
                    return Err("AD_REFLECTION_DOMAIN");
                }
            }
        }
        Ok(())
    }

    fn dual_moments(&self, x: Dual64, b: Dual64) -> (Dual64, Dual64, Dual64) {
        let mut energy = Dual64::from_re(0.0);
        let mut pi = Dual64::from_re(0.0);
        for cohort in &self.cohorts {
            let d = b - cohort.b_birth;
            let dilution = ((x - cohort.u) * -4.0).exp() * cohort.energy_birth;
            for (&mu, &alpha) in cohort.mu.iter().zip(&cohort.alpha) {
                let a = (d * 2.0).exp() * (1.0 - mu * mu);
                let bb = (d * -4.0).exp() * (mu * mu);
                let r = (a + bb).sqrt();
                let pressure_kernel = (bb - a * 0.5) / r;
                energy += dilution * alpha * r;
                pi += dilution * alpha * pressure_kernel;
            }
        }
        let donor = (x * -3.0).exp() * self.donor_amplitude;
        (energy, pi, donor)
    }

    fn dual_rhs(&self, x: Dual64, state: [Dual64; 3]) -> [Dual64; 3] {
        let [h, b, shear] = state;
        let (energy, pi, donor) = self.dual_moments(x, b);
        [
            (-h * h - shear * shear * 2.0 - donor * 0.5 - energy
                + self.cosmological_constant) / h,
            shear / h,
            shear * -3.0 + pi / h,
        ]
    }

    /// Directional derivative with all stored cohort data held constant.
    pub fn directional_ad(
        &self,
        x: f64,
        state: [f64; 3],
        time_seed: f64,
        direction: [f64; 3],
    ) -> Result<[f64; 3], &'static str> {
        self.validate(x, state)?;
        if !time_seed.is_finite() || direction.iter().any(|v| !v.is_finite()) {
            return Err("AD_DIRECTION_DOMAIN");
        }
        let dual_state = std::array::from_fn(|i| Dual64::new(state[i], direction[i]));
        let result = self.dual_rhs(Dual64::new(x, time_seed), dual_state);
        if result.iter().any(|v| !v.re.is_finite() || !v.eps.is_finite()) {
            return Err("AD_EVALUATION_NONFINITE");
        }
        Ok(result.map(|v| v.eps))
    }

    pub fn oracle(
        &self,
        x: f64,
        state: [f64; 3],
        time_seed: f64,
        direction: [f64; 3],
    ) -> Result<Oracle, &'static str> {
        self.validate(x, state)?;
        let rhs = self.dual_rhs(Dual64::from_re(x), state.map(Dual64::from_re))
            .map(|v| v.re);
        let jvp = self.directional_ad(x, state, 0.0, direction)?;
        let partial_t = self.directional_ad(x, state, 1.0, [0.0; 3])?;
        let total_direction = self.directional_ad(x, state, time_seed, direction)?;
        Ok(Oracle { rhs, jvp, partial_t, total_direction })
    }

    /// Independent closed formulas used by unit checks. The adapter can instead
    /// pass its actual callback output to scaled_error against `oracle()`.
    pub fn analytic(&self, x: f64, state: [f64; 3]) -> Result<Analytic, &'static str> {
        self.validate(x, state)?;
        let [h, b, shear] = state;
        let (mut energy, mut pi, mut pi_b) = (0.0, 0.0, 0.0);
        for cohort in &self.cohorts {
            let d = b - cohort.b_birth;
            let dilution = (-4.0 * (x - cohort.u)).exp() * cohort.energy_birth;
            for (&mu, &alpha) in cohort.mu.iter().zip(&cohort.alpha) {
                let aa = (2.0 * d).exp() * (1.0 - mu * mu);
                let bb = (-4.0 * d).exp() * mu * mu;
                let r = (aa + bb).sqrt();
                let numerator = bb - 0.5 * aa;
                energy += dilution * alpha * r;
                pi += dilution * alpha * numerator / r;
                pi_b += dilution * alpha
                    * ((-4.0 * bb - aa) / r + 2.0 * numerator * numerator / r.powi(3));
            }
        }
        let donor = self.donor_amplitude * (-3.0 * x).exp();
        let rhs = [
            (-h * h - 2.0 * shear * shear - donor / 2.0 - energy
                + self.cosmological_constant) / h,
            shear / h,
            -3.0 * shear + pi / h,
        ];
        let jacobian = [
            [-2.0 - rhs[0] / h, 2.0 * pi / h, -4.0 * shear / h],
            [-shear / (h * h), 0.0, 1.0 / h],
            [-pi / (h * h), pi_b / h, -3.0],
        ];
        let partial_t = [(1.5 * donor + 4.0 * energy) / h, 0.0, -4.0 * pi / h];
        Ok(Analytic { rhs, jacobian, partial_t, energy, pi, pi_b, donor })
    }
}

pub fn matvec(matrix: [[f64; 3]; 3], direction: [f64; 3]) -> [f64; 3] {
    matrix.map(|row| row.iter().zip(direction).map(|(a, b)| a * b).sum())
}

pub fn scaled_error(actual: [f64; 3], reference: [f64; 3]) -> f64 {
    actual.iter().zip(reference).fold(0.0_f64, |worst, (a, r)| {
        if !a.is_finite() || !r.is_finite() { f64::INFINITY }
        else { worst.max((a - r).abs() / (1.0 + r.abs())) }
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    const STATES: [[f64; 3]; 4] = [
        [0.42, -0.5, -0.08], [0.9, 0.0, 0.0],
        [1.4, 0.34, 0.09], [2.1, 0.9, -0.13],
    ];
    const TIMES: [f64; 3] = [0.45, 0.9, 1.2];
    const DIRECTIONS: [[f64; 3]; 5] = [
        [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0],
        [0.31, -0.73, 1.2], [-2.0, 0.09, -0.4],
    ];

    fn p24(u: f64, b_birth: f64, energy_birth: f64) -> Cohort {
        let half = 0.5_f64.sqrt();
        Cohort { u, b_birth, energy_birth,
            mu: vec![-1.0, -half, 0.0, half, 1.0],
            alpha: vec![1.0/30.0, 4.0/15.0, 2.0/5.0, 4.0/15.0, 1.0/30.0] }
    }

    fn banks() -> Vec<FrozenBank> {
        let dust = FrozenBank { cohorts: vec![], donor_amplitude: 0.7,
            cosmological_constant: 0.1 };
        let mut old = p24(0.0, -0.2, 0.2);
        for (alpha, mu) in old.alpha.iter_mut().zip(&old.mu) {
            *alpha *= 1.0 + 0.4 * (3.0 * mu * mu - 1.0) / 2.0;
        }
        let stock = FrozenBank { cohorts: vec![old.clone()],
            donor_amplitude: 0.7 * (-0.12_f64).exp(), cosmological_constant: 0.1 };
        let cohorts = FrozenBank { cohorts: vec![old, p24(0.15, 0.13, 0.012),
            p24(0.3, -0.31, 0.02)], donor_amplitude: 0.7 * (-0.3_f64).exp(),
            cosmological_constant: 0.1 };
        vec![dust, stock, cohorts]
    }

    fn accept(actual: [f64; 3], reference: [f64; 3], worst: &mut f64) {
        let error = scaled_error(actual, reference);
        *worst = worst.max(error);
        assert!(error <= CALLBACK_SCALED_GATE,
            "scaled error {error:e}, actual={actual:?}, reference={reference:?}");
    }

    #[test]
    fn analytic_jvp_matches_directional_ad_on_frozen_banks() {
        let (mut vectors, mut worst) = (0, 0.0_f64);
        for bank in banks() { for x in TIMES { for state in STATES {
            let formula = bank.analytic(x, state).unwrap();
            for direction in DIRECTIONS {
                let ad = bank.directional_ad(x, state, 0.0, direction).unwrap();
                accept(matvec(formula.jacobian, direction), ad, &mut worst);
                vectors += 1;
            }
        } } }
        println!("AD_JVP vectors={vectors} components={} max_scaled_error={worst:e}", 3*vectors);
    }

    #[test]
    fn explicit_time_derivative_matches_ad_without_finite_difference() {
        let (mut vectors, mut worst) = (0, 0.0_f64);
        for bank in banks() { for x in TIMES { for state in STATES {
            let formula = bank.analytic(x, state).unwrap();
            let ad = bank.directional_ad(x, state, 1.0, [0.0; 3]).unwrap();
            accept(formula.partial_t, ad, &mut worst); vectors += 1;
        } } }
        println!("AD_FT vectors={vectors} components={} max_scaled_error={worst:e}", 3*vectors);
    }

    #[test]
    fn time_augmented_jvp_is_jvp_plus_partial_t() {
        let (mut vectors, mut worst) = (0, 0.0_f64);
        for bank in banks() { for x in TIMES { for state in STATES {
            let formula = bank.analytic(x, state).unwrap();
            for time_seed in [-1.3, 0.0, 0.71] {
                let direction = DIRECTIONS[3];
                let jvp = matvec(formula.jacobian, direction);
                let expected = std::array::from_fn(|i| jvp[i] + time_seed * formula.partial_t[i]);
                let ad = bank.directional_ad(x, state, time_seed, direction).unwrap();
                accept(expected, ad, &mut worst); vectors += 1;
            }
        } } }
        println!("AD_AUGMENTED vectors={vectors} components={} max_scaled_error={worst:e}", 3*vectors);
    }

    #[test]
    fn direct_primal_program_matches_closed_primal() {
        let mut worst = 0.0_f64;
        for bank in banks() { for x in TIMES { for state in STATES {
            let actual = bank.oracle(x, state, 0.0, [0.0; 3]).unwrap().rhs;
            accept(actual, bank.analytic(x, state).unwrap().rhs, &mut worst);
        } } }
        println!("AD_PRIMAL vectors=36 components=108 max_scaled_error={worst:e}");
    }

    fn birth_jump_case(norm_scale: f64, eta: f64, worst: &mut f64) {
        let before = banks().remove(2);
        let x: f64 = 0.61;
        for state in STATES {
            let mut after = before.clone();
            let donor = before.donor_amplitude * (-3.0 * x).exp();
            let w = donor * -(-0.7_f64 * 0.05).exp_m1();
            after.donor_amplitude -= w * (3.0 * x).exp();
            let mut birth = p24(x, state[1], w);
            for (alpha, mu) in birth.alpha.iter_mut().zip(&birth.mu) {
                *alpha *= norm_scale * (1.0 + eta * (3.0 * mu * mu - 1.0) / 2.0);
            }
            let mut s = 0.0;
            let mut m2 = 0.0;
            let mut m4 = 0.0;
            for (&mu, &alpha) in birth.mu.iter().zip(&birth.alpha) {
                let z = mu * mu;
                s += alpha;
                m2 += alpha * (3.0 * z - 1.0) / 2.0;
                m4 += alpha * (35.0 * z * z - 30.0 * z + 3.0) / 8.0;
            }
            let kd = -8.0*s/5.0 - 10.0*m2/7.0 + 36.0*m4/35.0;
            after.cohorts.push(birth);
            let f0 = before.oracle(x, state, 1.0, [0.0; 3]).unwrap();
            let f1 = after.oracle(x, state, 1.0, [0.0; 3]).unwrap();
            let h = state[0];
            accept(std::array::from_fn(|i| f1.rhs[i] - f0.rhs[i]),
                [w*(0.5-s)/h, 0.0, w*m2/h], worst);
            accept(std::array::from_fn(|i| f1.partial_t[i] - f0.partial_t[i]),
                [w*(4.0*s-1.5)/h, 0.0, -4.0*w*m2/h], worst);
            let jump = [
                [w*(s-0.5)/(h*h), 2.0*w*m2/h, 0.0],
                [0.0; 3], [-w*m2/(h*h), w*kd/h, 0.0],
            ];
            for direction in DIRECTIONS {
                let j0 = before.directional_ad(x, state, 0.0, direction).unwrap();
                let j1 = after.directional_ad(x, state, 0.0, direction).unwrap();
                accept(std::array::from_fn(|i| j1[i]-j0[i]), matvec(jump, direction), worst);
            }
            let e0 = before.analytic(x, state).unwrap();
            let e1 = after.analytic(x, state).unwrap();
            let c0 = h*h - state[2]*state[2] - e0.donor - e0.energy - before.cosmological_constant;
            let c1 = h*h - state[2]*state[2] - e1.donor - e1.energy - after.cosmological_constant;
            accept([c1-c0, 0.0, 0.0], [w*(1.0-s), 0.0, 0.0], worst);
            assert_eq!(&after.cohorts[..before.cohorts.len()], &before.cohorts);
        }
    }

    #[test]
    fn normalized_p24_birth_changes_rhs_ft_and_jacobian() {
        let mut worst = 0.0_f64;
        birth_jump_case(1.0, 0.0, &mut worst);
        println!("AD_P24_BIRTH events=4 max_scaled_error={worst:e}");
    }

    #[test]
    fn imperfect_birth_moments_and_normalization_remain_observable() {
        let mut worst = 0.0_f64;
        // Deliberate failing-source controls are not accepted by a projector.
        birth_jump_case(1.0, 0.2, &mut worst);
        birth_jump_case(1.02, -0.1, &mut worst);
        println!("AD_DEFECTIVE_BIRTH events=8 max_scaled_error={worst:e}");
    }

    #[test]
    fn omitted_partial_t_negative_control_is_rejected() {
        let mut smallest_mismatch = f64::INFINITY;
        for bank in banks() {
            let expected = bank.directional_ad(0.61, STATES[2], 1.0, [0.0; 3]).unwrap();
            let mismatch = scaled_error([0.0; 3], expected);
            assert!(mismatch > CALLBACK_SCALED_GATE);
            smallest_mismatch = smallest_mismatch.min(mismatch);
        }
        println!("EXPECTED_NEGATIVE_CONTROL_REJECTED cases=3 min_scaled_mismatch={smallest_mismatch:e}");
    }

    #[test]
    fn hamiltonian_transport_identity_matches_ad_off_constraint() {
        let mut worst = 0.0_f64;
        for bank in banks() { for x in TIMES { for state in STATES {
            let formula = bank.analytic(x, state).unwrap();
            let dual_state: [Dual64; 3] = std::array::from_fn(|i| Dual64::new(state[i], formula.rhs[i]));
            let (energy, _, donor) = bank.dual_moments(Dual64::new(x, 1.0), dual_state[1]);
            let c = dual_state[0]*dual_state[0] - dual_state[2]*dual_state[2]
                - energy - donor - bank.cosmological_constant;
            accept([c.eps, 0.0, 0.0], [-2.0*c.re, 0.0, 0.0], &mut worst);
        } } }
        println!("AD_CONSTRAINT points=36 max_scaled_error={worst:e}");
    }

    #[test]
    fn validation_and_bank_immutability_preserve_positive_reflection_data() {
        let bank = banks().remove(2);
        let original = bank.clone();
        for direction in DIRECTIONS {
            bank.oracle(0.9, STATES[2], 0.3, direction).unwrap();
        }
        assert_eq!(bank, original);
        assert_eq!(bank.oracle(0.9, [0.0, 0.2, 0.01], 0.0, [0.0; 3]).unwrap_err(), "AD_STATE_DOMAIN");
        let mut negative = bank.clone(); negative.cohorts[0].alpha[0] = -0.1;
        assert_eq!(negative.validate(0.9, STATES[2]).unwrap_err(), "AD_ANGULAR_DOMAIN");
        let mut odd = bank.clone(); odd.cohorts[0].alpha[0] *= 1.01;
        assert_eq!(odd.validate(0.9, STATES[2]).unwrap_err(), "AD_REFLECTION_DOMAIN");
        let mut bad_mu = bank.clone(); bad_mu.cohorts[0].mu[0] = -1.1;
        assert_eq!(bad_mu.validate(0.9, STATES[2]).unwrap_err(), "AD_ANGULAR_DOMAIN");
        assert_eq!(bank.validate(0.1, STATES[2]).unwrap_err(), "AD_COHORT_DOMAIN");
        println!("AD_DOMAIN_AND_IMMUTABILITY expected_rejections=5 frozen_checks=5");
    }
}
