//! Radiation representations of the homogeneous sky.
//!
//! * `Field::Rays`: the R109 Lagrangian bundle (exact characteristics, evolving
//!   solid-angle weights).
//! * `Field::Harmonic`: the R113 Eulerian spin-harmonic (PSTF) hierarchy generated
//!   from the Lie data (`kinetic::lie_hierarchy`), sampled on a fixed
//!   Gauss-Legendre x uniform-phi grid of propagation directions whenever a
//!   collision, a moment or an observation needs the coherency field. The grid
//!   photons carry the field values and the fixed quadrature weights, so every
//!   collision kernel, recoil step, moment and observation routine of the ray route
//!   applies unchanged; after a collision the grid field is projected back to
//!   l <= lmax (exact for rest electrons, Galerkin for moving electrons; l = 0, 1
//!   are the same quadrature sums as the energy and momentum of the ray route).
//!
//! Both representations start from the unit isotropic unpolarized sky
//! (bolometric intensity 1 in every direction).
use super::{moments, Photon, RadiationMoments, M, V};
use crate::kinetic::lie_hierarchy::{lie_data, LieHierarchy};
use crate::kinetic::lie_history::RayNode;
use crate::kinetic::spin_sht::{SpinSht, C64};
use std::sync::Arc;

/// Representation selected for photons (and neutrinos) of one solve.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Route {
    /// Lagrangian rays on the `nmu x nphi` initial grid (R109 default).
    Rays,
    /// Spin-harmonic hierarchy to `lmax` on an `n_theta x n_phi` collision grid.
    Harmonic {
        lmax: usize,
        n_theta: usize,
        n_phi: usize,
    },
}

impl Route {
    pub fn name(&self) -> String {
        match self {
            Route::Rays => "rays".into(),
            Route::Harmonic {
                lmax,
                n_theta,
                n_phi,
            } => format!("harmonic_lmax{lmax}_grid{n_theta}x{n_phi}"),
        }
    }
    /// Default collision grid of a harmonic route: exact for the rest-electron step.
    pub fn harmonic(lmax: usize) -> Self {
        Route::Harmonic {
            lmax,
            n_theta: lmax + 3,
            n_phi: 2 * lmax + 6,
        }
    }
}

fn dyad(e: &V) -> (V, V) {
    let z = e.z.clamp(-1.0, 1.0);
    let theta = z.acos();
    let phi = if e.x == 0.0 && e.y == 0.0 {
        0.0
    } else {
        e.y.atan2(e.x)
    };
    (
        V::new(
            theta.cos() * phi.cos(),
            theta.cos() * phi.sin(),
            -theta.sin(),
        ),
        V::new(-phi.sin(), phi.cos(), 0.0),
    )
}

/// Spin-harmonic coefficients of the bolometric coherency of propagation directions.
#[derive(Clone)]
pub struct HarmonicSky {
    hierarchy: Arc<LieHierarchy>,
    transform: Arc<SpinSht>,
    /// Slots (a^0, a^+2, a^-2) or (a^0) for an unpolarized species.
    pub coefficients: Vec<Vec<C64>>,
}

impl HarmonicSky {
    /// Unit isotropic unpolarized sky.
    pub fn isotropic(
        lmax: usize,
        n_theta: usize,
        n_phi: usize,
        polarized: bool,
    ) -> Result<Self, String> {
        if n_theta < lmax + 1 || n_phi < 2 * lmax + 1 {
            return Err("harmonic collision grid is below the band limit of its lmax".into());
        }
        let hierarchy = Arc::new(LieHierarchy::new(lmax, polarized, 4.0)?);
        let transform = Arc::new(SpinSht::new(lmax, n_theta, n_phi)?);
        let mut coefficients = hierarchy.zero_state();
        coefficients[0][0] = C64::new((4.0 * std::f64::consts::PI).sqrt(), 0.0);
        Ok(Self {
            hierarchy,
            transform,
            coefficients,
        })
    }

    pub fn lmax(&self) -> usize {
        self.hierarchy.lmax
    }
    pub fn polarized(&self) -> bool {
        self.hierarchy.polarized
    }
    pub fn grid_size(&self) -> (usize, usize) {
        (self.transform.grid.n_theta, self.transform.grid.n_phi)
    }

    /// Free streaming between two history nodes.
    pub fn stream(&mut self, left: &RayNode, right: &RayNode) -> Result<(), String> {
        self.hierarchy.stream(
            &mut self.coefficients,
            &lie_data(left),
            &lie_data(right),
            right.eta - left.eta,
        )
    }

    /// Grid photons with the field values and fixed quadrature weights.
    pub fn photons(&self) -> Result<Vec<Photon>, String> {
        let polar = if self.polarized() {
            Some((&self.coefficients[1][..], &self.coefficients[2][..]))
        } else {
            None
        };
        let (i, q, u) = self.transform.to_stokes(&self.coefficients[0], polar);
        let grid = &self.transform.grid;
        let mut out = Vec::with_capacity(grid.len());
        for k in 0..grid.len() {
            let e = V::new(grid.ehat[3 * k], grid.ehat[3 * k + 1], grid.ehat[3 * k + 2]);
            let (t, p) = dyad(&e);
            let screen: M = (t * t.transpose() + p * p.transpose()) * (0.5 * i[k])
                + (t * t.transpose() - p * p.transpose()) * (0.5 * q[k])
                + (t * p.transpose() + p * t.transpose()) * (0.5 * u[k]);
            if !screen.iter().all(|x| x.is_finite()) {
                return Err("non-finite synthesized harmonic sky".into());
            }
            out.push(Photon {
                direction: e,
                weight: grid.w[k],
                screen,
            });
        }
        Ok(out)
    }

    /// Project grid photons (same directions as [`Self::photons`]) back to l <= lmax.
    pub fn absorb(&mut self, photons: &[Photon]) -> Result<(), String> {
        let grid = &self.transform.grid;
        if photons.len() != grid.len() {
            return Err("grid photon count does not match the harmonic grid".into());
        }
        let mut i = Vec::with_capacity(photons.len());
        let mut q = Vec::with_capacity(photons.len());
        let mut u = Vec::with_capacity(photons.len());
        for (k, ph) in photons.iter().enumerate() {
            let e = V::new(grid.ehat[3 * k], grid.ehat[3 * k + 1], grid.ehat[3 * k + 2]);
            if (ph.direction - e).norm() > 1e-12 {
                return Err("grid photon moved off its harmonic grid direction".into());
            }
            let (t, p) = dyad(&e);
            i.push(ph.screen.trace());
            q.push(t.dot(&(ph.screen * t)) - p.dot(&(ph.screen * p)));
            u.push(2.0 * t.dot(&(ph.screen * p)));
        }
        let [a0, ap, am] = self.transform.from_stokes(&i, &q, &u);
        self.coefficients[0] = a0;
        if self.polarized() {
            self.coefficients[1] = ap;
            self.coefficients[2] = am;
        }
        Ok(())
    }
}

/// One radiation species in either representation.
#[derive(Clone)]
pub enum Field {
    Rays(Vec<Photon>),
    Harmonic(HarmonicSky),
}

impl Field {
    /// Unit isotropic sky; rays use the `nmu x nphi` grid of `initial_sky`.
    pub fn isotropic(
        route: &Route,
        nmu: usize,
        nphi: usize,
        polarized: bool,
    ) -> Result<Self, String> {
        match route {
            Route::Rays => Ok(Field::Rays(super::initial_sky(nmu, nphi)?)),
            Route::Harmonic {
                lmax,
                n_theta,
                n_phi,
            } => Ok(Field::Harmonic(HarmonicSky::isotropic(
                *lmax, *n_theta, *n_phi, polarized,
            )?)),
        }
    }

    pub fn moments(&self) -> Result<RadiationMoments, String> {
        match self {
            Field::Rays(sky) => moments(sky),
            Field::Harmonic(h) => moments(&h.photons()?),
        }
    }

    /// Free characteristic transport across [left.eta, right.eta].
    pub fn geometric(&mut self, left: &RayNode, right: &RayNode) -> Result<(), String> {
        match self {
            Field::Rays(sky) => super::geometric(sky, left, right),
            Field::Harmonic(h) => h.stream(left, right),
        }
    }

    /// Photons that represent the field (rays, or grid samples of the harmonic sky).
    pub fn photons(&self) -> Result<Vec<Photon>, String> {
        match self {
            Field::Rays(sky) => Ok(sky.clone()),
            Field::Harmonic(h) => h.photons(),
        }
    }
}
