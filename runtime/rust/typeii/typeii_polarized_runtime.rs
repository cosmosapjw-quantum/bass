use super::typeii_polarized::{collision_generator_apply_polarized, kato_apply_polarized};
use super::typeii_runtime::{expm_action, KrylovOptions, RuntimeError};

pub fn frozen_collision_step(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    axis: usize,
    optical_depth: f64,
    y: &[f64],
    options: KrylovOptions,
) -> Result<Vec<f64>, RuntimeError> {
    let c = |x: &[f64]| collision_generator_apply_polarized(directions, weights, v, axis, x);
    expm_action(&c, y, optical_depth, options)
}

pub fn frozen_kato_step(
    directions: &[[f64; 3]],
    weights: &[f64],
    v: f64,
    vdot: f64,
    axis: usize,
    h: f64,
    y: &[f64],
    options: KrylovOptions,
) -> Result<Vec<f64>, RuntimeError> {
    let k = |x: &[f64]| kato_apply_polarized(directions, weights, v, vdot, axis, x);
    expm_action(&k, y, h, options)
}
