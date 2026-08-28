//! RF-03 explicit gamma-law tilted perfect-fluid production core.

mod eos;
mod force;
mod integrate;
mod state;

pub use eos::{GammaLawModel, EXPLICIT_GAMMA_LAW_MODEL_ID};
pub use force::{force, force_jvp};
pub use integrate::{integrate_context_history, integrate_fixed_context, IntegrationResult};
pub use state::{MatterContext, MatterDirection, MatterError, MatterState};
