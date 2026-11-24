//! Line-of-sight replay of a recorded homogeneous-sky solution.
//!
//! The forward Lagrangian solve emits, for every accepted e-fold step, its two
//! geometry nodes and the collision events of both half steps. Given those
//! global sources, a single ray evolves independently of all others (each
//! collision touches the global field only through a 3x3 rest-frame tensor).
//! Replaying that discrete map from the backward-traced initial direction of any
//! observed sky direction therefore evaluates the same scheme at that direction;
//! replaying a forward ray reproduces it with the same floating-point operations.
//! The observed angular resolution is thus independent of the Lagrangian mesh,
//! which only controls the accuracy of the recorded sources.

use super::{
    boost, geometric_one, replay_collision, sky_sample, transformed, CollisionEvent, Photon, M, V,
};
use crate::kinetic::lie_history::{advance_ray, RayNode};
use crate::kinetic::sky_spectrum::{analyze_rings, Mode, SkySample};
use crate::kinetic::sphere::SphereGrid;
use rayon::prelude::*;

/// One accepted forward step: `first` acts at `left`, then free transport
/// `left -> right`, then `second` at `right`.
#[derive(Clone, Debug)]
pub struct StepRecord {
    pub left: RayNode,
    pub right: RayNode,
    pub first: Vec<CollisionEvent>,
    pub second: Vec<CollisionEvent>,
}

/// Normal-frame propagation direction at the first node that reaches
/// `direction` at the last node under the recorded characteristic maps.
pub fn trace_back(records: &[StepRecord], direction: [f64; 3]) -> Result<[f64; 3], String> {
    let mut e = direction;
    for r in records.iter().rev() {
        e = advance_ray(&r.right, &r.left, e)?.e;
    }
    Ok(e)
}

/// Apply the recorded discrete scheme to one bundle.
pub fn replay(records: &[StepRecord], photon: Photon) -> Result<Photon, String> {
    let mut p = photon;
    for r in records {
        for event in &r.first {
            replay_collision(&mut p, event)?;
        }
        geometric_one(&mut p, &r.left, &r.right)?;
        for event in &r.second {
            replay_collision(&mut p, event)?;
        }
    }
    Ok(p)
}

/// Observer-frame coherency arriving from outward sky direction `outward`.
#[derive(Clone, Debug)]
pub struct Arrival {
    pub outward: [f64; 3],
    pub screen: [[f64; 3]; 3],
    /// |replayed observer-frame propagation direction + outward|.
    pub landing_error: f64,
}

/// Trace the observed direction back to the first node, replay the recorded
/// scheme from a unit isotropic unpolarized coherency, and boost to the observer.
pub fn arrival(
    records: &[StepRecord],
    observer_beta: [f64; 3],
    outward: [f64; 3],
) -> Result<Arrival, String> {
    let n = V::from(outward);
    if !n.norm_squared().is_finite() || (n.norm_squared() - 1.0).abs() > 1e-9 {
        return Err("outward sky direction must be a unit vector".into());
    }
    let b = V::from(observer_beta);
    let seen_propagation = -n;
    let (normal, _, _) = boost(seen_propagation, -b)?;
    let start = trace_back(records, normal.into())?;
    let end = replay(records, Photon::isotropic(start, 1.0)?)?;
    let seen = transformed(&end, b)?;
    Ok(Arrival {
        outward,
        screen: seen.screen(),
        landing_error: (seen.direction - seen_propagation).norm(),
    })
}

/// Line-of-sight sky on a Gauss-Legendre x uniform-phi grid of outward
/// observer-frame directions (`SphereGrid` order: ring-major, phi_0 = 0).
pub struct LosSky {
    pub grid: SphereGrid,
    pub samples: Vec<SkySample>,
    pub max_landing_error: f64,
    pub min_intensity: f64,
    pub min_screen_eigenvalue: f64,
}

pub fn los_sky(
    records: &[StepRecord],
    observer_beta: [f64; 3],
    n_theta: usize,
    n_phi: usize,
) -> Result<LosSky, String> {
    if n_theta < 2 || n_phi < 3 {
        return Err("line-of-sight grid needs at least 2 rings and 3 azimuths".into());
    }
    let grid = SphereGrid::new(n_theta, n_phi);
    let arrivals: Vec<Arrival> = grid
        .ehat
        .par_chunks_exact(3)
        .map(|e| arrival(records, observer_beta, [e[0], e[1], e[2]]))
        .collect::<Result<_, _>>()?;
    let screens: Vec<M> = arrivals
        .iter()
        .map(|a| M::from_fn(|i, j| a.screen[i][j]))
        .collect();
    let area: f64 = grid.w.iter().sum();
    let mut tsum = 0.0;
    let mut isum = 0.0;
    let mut min_i = f64::INFINITY;
    let mut min_eig = f64::INFINITY;
    for (s, w) in screens.iter().zip(&grid.w) {
        let i = s.trace();
        if !i.is_finite() || i <= 0.0 {
            return Err("nonpositive or nonfinite replayed intensity".into());
        }
        let discr = (2.0 * s.norm_squared() - i * i).max(0.0).sqrt();
        min_eig = min_eig.min(0.5 * (i - discr));
        min_i = min_i.min(i);
        tsum += w * i.sqrt().sqrt();
        isum += w * i;
    }
    let tbar = tsum / area;
    let ibar = isum / area;
    let samples = grid
        .ehat
        .chunks_exact(3)
        .zip(&screens)
        .zip(&grid.w)
        .map(|((e, s), w)| sky_sample(V::new(e[0], e[1], e[2]), s, *w, tbar, ibar))
        .collect();
    Ok(LosSky {
        max_landing_error: arrivals
            .iter()
            .map(|a| a.landing_error)
            .fold(0.0, f64::max),
        min_intensity: min_i,
        min_screen_eigenvalue: min_eig,
        grid,
        samples,
    })
}

impl LosSky {
    /// All signed modes to `lmax` with the conventions of `sky_spectrum::analyze`.
    pub fn modes(&self, lmax: usize) -> Result<Vec<Mode>, String> {
        // Exactly the per-sample SphereGrid weights, constant on each ring.
        let ring_weight: Vec<f64> = (0..self.grid.n_theta)
            .map(|it| self.grid.w[it * self.grid.n_phi])
            .collect();
        let field = |f: fn(&SkySample) -> f64| self.samples.iter().map(f).collect::<Vec<_>>();
        analyze_rings(
            &self.grid.ct,
            &ring_weight,
            self.grid.n_phi,
            &field(|s| s.t),
            &field(|s| s.q),
            &field(|s| s.u),
            lmax,
        )
    }
}
