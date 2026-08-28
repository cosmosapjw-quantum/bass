//! The single RF-03 production EOS selected by an exact caller-supplied ID.

use super::state::MatterError;

pub const EXPLICIT_GAMMA_LAW_MODEL_ID: &str = "explicit_gamma_law_tilted_perfect_fluid_v1";

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct GammaLawModel {
    gamma: f64,
}

impl GammaLawModel {
    pub fn select(model_id: &str, gamma: f64) -> Result<Self, MatterError> {
        if model_id != EXPLICIT_GAMMA_LAW_MODEL_ID {
            return Err(MatterError::Model(format!(
                "unsupported RF-03 model_id {model_id:?}; expected {EXPLICIT_GAMMA_LAW_MODEL_ID:?}"
            )));
        }
        if !gamma.is_finite() || gamma <= 0.0 || gamma > 2.0 {
            return Err(MatterError::Domain(
                "gamma must be finite and satisfy 0 < gamma <= 2".to_string(),
            ));
        }
        Ok(Self { gamma })
    }

    #[inline]
    pub fn gamma(self) -> f64 {
        self.gamma
    }

    #[inline]
    pub fn pressure(self, rest_density: f64) -> Result<f64, MatterError> {
        if !rest_density.is_finite() || rest_density < 0.0 {
            return Err(MatterError::Domain(
                "rest density must be finite and nonnegative".to_string(),
            ));
        }
        Ok((self.gamma - 1.0) * rest_density)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rf03_eos_requires_exact_model_id_and_gamma_domain() {
        let selected = GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 4.0 / 3.0)
            .expect("authorized model");
        assert!((selected.pressure(3.0).expect("valid density") - 1.0).abs() <= 3.0e-16);
        assert!(matches!(
            GammaLawModel::select("constant_w", 4.0 / 3.0),
            Err(MatterError::Model(_))
        ));
        assert!(matches!(
            GammaLawModel::select(EXPLICIT_GAMMA_LAW_MODEL_ID, 0.0),
            Err(MatterError::Domain(_))
        ));
    }
}
