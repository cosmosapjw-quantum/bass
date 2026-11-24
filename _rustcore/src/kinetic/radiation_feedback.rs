//! Active, massless radiation geometry in the e-fold clock eta=ln(a/a_initial).
//! RayNode stores Sigma=sigma/H and N,A in Hubble units. This step consumes
//! physical normal-frame moments of the propagated radiation; a tracer with
//! independently prescribed opacity or electron velocity supplies no compensating
//! material force. A conserved total matter model must account for that force.

use crate::geom::group::BianchiGroup;
use crate::kinetic::lie_history::RayNode;
use nalgebra::{Matrix3, Vector3};

type Tensor = [[f64; 3]; 3];

fn matrix(m: Tensor) -> Matrix3<f64> {
    Matrix3::from_fn(|i, j| m[i][j])
}

fn tensor(m: Matrix3<f64>) -> Tensor {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}

fn group(node: &RayNode) -> BianchiGroup {
    let n = &node.n;
    BianchiGroup::new(
        [n[0][0], n[1][1], n[2][2], n[0][1], n[0][2], n[1][2]],
        node.a,
    )
}

fn validate_geometry(node: &RayNode) -> Result<(), String> {
    if !node.hubble_ratio.is_finite()
        || node.hubble_ratio <= 0.0
        || !node.eta.is_finite()
        || !node.a.iter().chain(&node.rotation).all(|x| x.is_finite())
    {
        return Err("invalid clock, Hubble ratio or frame vector".into());
    }
    for (name, x) in [("Sigma", matrix(node.shear)), ("N", matrix(node.n))] {
        if !x.iter().all(|v| v.is_finite()) || (x - x.transpose()).amax() > 1e-10 * (1.0 + x.amax())
        {
            return Err(format!("{name} must be a finite symmetric tensor"));
        }
    }
    let sigma = matrix(node.shear);
    if sigma.trace().abs() > 1e-10 * (1.0 + sigma.amax()) {
        return Err("Hubble-normalized shear must be trace-free".into());
    }
    Ok(())
}

/// Update the residuals for the specified *same-time* density and flux/E.
/// Residuals retain their signs, with public Codazzi defined as +(div Sigma + q/H²)
/// in units 8 pi G/c^4=1. No projection is performed.
pub fn refresh(node: &mut RayNode, omega: f64, flux_fraction: [f64; 3]) -> Result<(), String> {
    refresh_mixture(node, omega, flux_fraction)?;
    node.omega_radiation = omega;
    Ok(())
}

/// Measure Einstein constraints with total matter energy and momentum.
/// The photon-only abundance in node.omega_radiation is preserved.
pub fn refresh_mixture(
    node: &mut RayNode,
    omega: f64,
    flux_fraction: [f64; 3],
) -> Result<(), String> {
    validate_geometry(node)?;
    let flux = Vector3::from(flux_fraction);
    if !omega.is_finite()
        || omega < 0.0
        || !flux.iter().all(|v| v.is_finite())
        || flux.norm() > 1.0 + 1e-10
    {
        return Err("radiation density or normalized energy flux is unphysical".into());
    }
    let s = matrix(node.shear);
    let g = group(node);
    let (curvature, _) = g.curvature();
    let ns = g.n_mat() * s;
    let axial = Vector3::new(
        ns[(1, 2)] - ns[(2, 1)],
        ns[(2, 0)] - ns[(0, 2)],
        ns[(0, 1)] - ns[(1, 0)],
    );
    let div_sigma = -(3.0 * (s * g.a_vec()) + axial);
    let codazzi = div_sigma + (3.0 * omega) * flux;
    if !node.omega_lambda.is_finite() || node.omega_lambda < 0.0 {
        return Err("Omega_Lambda must be finite and nonnegative".into());
    }
    let gauss = s.norm_squared() / 6.0 + curvature + omega + node.omega_lambda - 1.0;
    let jacobi = g.jacobi_residual();
    if !gauss.is_finite() || !codazzi.iter().chain(&jacobi).all(|x| x.is_finite()) {
        return Err("non-finite Einstein constraint diagnostic".into());
    }
    node.gauss_residual = gauss;
    node.jacobi_residual = jacobi;
    node.codazzi_residual = codazzi.into();
    Ok(())
}

/// Advance the geometry from 'old' using the RHS at 'at', which can be 'old'
/// for a predictor or the independently computed midpoint for the full step.
/// pressure_fraction = P_ij/E, flux_fraction = q_i/E on *propagation* directions.
/// Returned diagnostics initially use the provided stage moments. Call refresh
/// with endpoint energy and flux after propagating the screen to the endpoint.
pub fn advance_geometry(
    old: &RayNode,
    at: &RayNode,
    dt: f64,
    omega: f64,
    pressure_fraction: Tensor,
    flux_fraction: [f64; 3],
) -> Result<RayNode, String> {
    let p = matrix(pressure_fraction);
    if (p.trace() - 1.0).abs() > 1e-10 {
        return Err("massless radiation pressure must have unit trace for P/E".into());
    }
    let mut out = advance_mixture(old, at, dt, omega, pressure_fraction, flux_fraction)?;
    out.omega_radiation = omega;
    Ok(out)
}

/// Both formulations agree on the Hamiltonian constraint surface. The reduced
/// equation substitutes Gauss Omega only in the deceleration. The density and
/// anisotropic stress sourcing the other terms remain the measured matter ones.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExpansionEquation {
    Raychaudhuri,
    GaussReduced,
}
impl ExpansionEquation {
    pub fn name(self) -> &'static str {
        match self {
            Self::Raychaudhuri => "raychaudhuri",
            Self::GaussReduced => "gauss-reduced",
        }
    }
}

/// Update of the structure constants across one step.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum LieUpdate {
    /// R109 increment N += dt N', A += dt A'. Jacobi, rank and h = A^2/(n2 n3)
    /// are then preserved only to the local truncation error.
    #[default]
    Additive,
    /// Congruence N -> P N Pᵀ, A -> det(P) P^{-T} A with P = exp[dt(Sigma + W + q I/2)]
    /// (Dossier I (1.26) in Hubble-normalized form). Jacobi, rank, inertia and the
    /// class-B invariant h are preserved to roundoff for any step size.
    Congruence,
}

impl LieUpdate {
    pub fn name(self) -> &'static str {
        match self {
            Self::Additive => "additive",
            Self::Congruence => "congruence",
        }
    }
    pub fn parse(s: &str) -> Result<Self, String> {
        match s {
            "additive" => Ok(Self::Additive),
            "congruence" => Ok(Self::Congruence),
            _ => Err(format!("unknown Lie update {s} (additive or congruence)")),
        }
    }
}

/// Advance a mixture of massless radiation and kinetic massive matter using
/// total Omega, P/E and q/E at the same stage. The photon-only omega field is
/// inherited from 'old' until the caller supplies the actual endpoint photon density.
pub fn advance_mixture(
    old: &RayNode,
    at: &RayNode,
    dt: f64,
    omega: f64,
    pressure_fraction: Tensor,
    flux_fraction: [f64; 3],
) -> Result<RayNode, String> {
    advance_mixture_with_equation(
        old,
        at,
        dt,
        omega,
        pressure_fraction,
        flux_fraction,
        ExpansionEquation::Raychaudhuri,
    )
}

pub fn advance_mixture_with_equation(
    old: &RayNode,
    at: &RayNode,
    dt: f64,
    omega: f64,
    pressure_fraction: Tensor,
    flux_fraction: [f64; 3],
    expansion: ExpansionEquation,
) -> Result<RayNode, String> {
    advance_mixture_with_options(
        old,
        at,
        dt,
        omega,
        pressure_fraction,
        flux_fraction,
        expansion,
        LieUpdate::Additive,
    )
}

#[allow(clippy::too_many_arguments)]
pub fn advance_mixture_with_options(
    old: &RayNode,
    at: &RayNode,
    dt: f64,
    omega: f64,
    pressure_fraction: Tensor,
    flux_fraction: [f64; 3],
    expansion: ExpansionEquation,
    lie: LieUpdate,
) -> Result<RayNode, String> {
    if old.hubble_ratio <= 0. || at.hubble_ratio <= 0. {
        return Err("Hubble-normalized expansion ends at zero H or recollapse; use a regular turnaround chart".into());
    }
    validate_geometry(old)?;
    validate_geometry(at)?;
    if !dt.is_finite() {
        return Err("non-finite e-fold increment".into());
    }
    let p = matrix(pressure_fraction);
    let f = Vector3::from(flux_fraction);
    if !p.iter().chain(f.iter()).all(|v| v.is_finite())
        || !omega.is_finite()
        || omega < 0.0
        || (p - p.transpose()).amax() > 1e-10
        || p.trace() < -1e-10
        || p.trace() > 1.0 + 1e-10
    {
        return Err(
            "P/E must be finite, symmetric, with trace in [0,1]; omega must be nonnegative".into(),
        );
    }
    // For a positive angular intensity E[eeᵀ]-E[e]E[e]ᵀ is a covariance.
    if (p - f * f.transpose()).symmetric_eigen().eigenvalues.min() < -1e-10 {
        return Err("kinetic moments violate P/E - (q/E)(q/E)^T >= 0".into());
    }
    let s = matrix(at.shear);
    let n = matrix(at.n);
    let a = Vector3::from(at.a);
    let [rx, ry, rz] = at.rotation;
    let w = Matrix3::new(0., -rz, ry, rz, 0., -rx, -ry, rx, 0.);
    let (curvature, curvature_stf) = group(at).curvature();
    // Lambda enters only the Raychaudhuri/Gauss scalars (Dossier I (1.14), (1.23)).
    let omega_lambda = at.omega_lambda;
    let omega_q = match expansion {
        ExpansionEquation::Raychaudhuri => omega,
        ExpansionEquation::GaussReduced => {
            let density = 1. - s.norm_squared() / 6. - curvature - omega_lambda;
            if !density.is_finite() || density <= 0. {
                return Err("Gauss-reduced active expansion requires positive geometric Omega on the expanding Hubble-normalized branch".into());
            }
            density
        }
    };
    let q = s.norm_squared() / 3.0 + 0.5 * omega_q * (1.0 + p.trace()) - omega_lambda;
    let pi = 3.0 * omega * (p - Matrix3::identity() * (p.trace() / 3.0));
    let ds = (q - 2.0) * s - curvature_stf + pi + w * s - s * w;
    let dn = q * n + s * n + n * s + w * n - n * w;
    let da = q * a - s * a + w * a;

    let mut out = old.clone();
    out.eta = old.eta + dt;
    out.shear = tensor(matrix(old.shear) + dt * ds);
    match lie {
        LieUpdate::Additive => {
            out.n = tensor(matrix(old.n) + dt * dn);
            out.a = (Vector3::from(old.a) + dt * da).into();
        }
        LieUpdate::Congruence => {
            let g = s + w + Matrix3::identity() * (0.5 * q);
            let p = (g * dt).exp();
            let inverse = p
                .try_inverse()
                .ok_or("singular structure-constant congruence")?;
            let n_new = p * matrix(old.n) * p.transpose();
            out.n = tensor((n_new + n_new.transpose()) * 0.5);
            out.a = (p.determinant() * (inverse.transpose() * Vector3::from(old.a))).into();
        }
    }
    out.hubble_ratio = old.hubble_ratio * (-dt * (1.0 + q)).exp();
    // Exact for constant Lambda: Omega_Lambda h^2 is conserved.
    out.omega_lambda = old.omega_lambda * (old.hubble_ratio / out.hubble_ratio).powi(2);
    refresh_mixture(&mut out, omega, flux_fraction)?;
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kinetic::{qevolve::QState, radial::Tail, sphere::SphereGrid};

    fn isotropic_pressure() -> Tensor {
        tensor(Matrix3::identity() / 3.0)
    }

    fn flrw() -> RayNode {
        RayNode {
            hubble_ratio: 1.0,
            omega_radiation: 1.0,
            ..Default::default()
        }
    }

    #[test]
    fn reduced_equation_changes_only_the_gauss_off_shell_deceleration() {
        let mut at = flrw();
        at.shear = [[0.1, 0., 0.], [0., -0.07, 0.], [0., 0., -0.03]];
        at.n = [[0.2, 0., 0.], [0., -0.1, 0.], [0., 0., 0.03]];
        let omega = 0.63;
        let pressure = [[0.24, 0.03, 0.], [0.03, 0.19, 0.], [0., 0., 0.12]];
        let dt = 0.01;
        refresh_mixture(&mut at, omega, [0.; 3]).unwrap();
        let stage =
            |eq| advance_mixture_with_equation(&at, &at, dt, omega, pressure, [0.; 3], eq).unwrap();
        let measured = stage(ExpansionEquation::Raychaudhuri);
        let reduced = stage(ExpansionEquation::GaussReduced);
        let delta_q = (measured.hubble_ratio / reduced.hubble_ratio).ln() / dt;
        assert!(
            (delta_q + 0.5 * (1. + matrix(pressure).trace()) * at.gauss_residual).abs() < 3e-14
        );
        assert!(
            (matrix(reduced.shear) - matrix(measured.shear) - dt * delta_q * matrix(at.shear))
                .norm()
                < 3e-16
        );
        // Same measured endpoint Omega must retain a visible residual.
        assert!(reduced.gauss_residual.abs() > 0.1);
        at.shear = [[2., 0., 0.], [0., -2., 0.], [0., 0., 0.]];
        assert!(advance_mixture_with_equation(
            &at,
            &at,
            dt,
            omega,
            pressure,
            [0.; 3],
            ExpansionEquation::GaussReduced
        )
        .is_err());
        at.hubble_ratio = 0.;
        assert!(advance_mixture_with_equation(
            &at,
            &at,
            dt,
            omega,
            pressure,
            [0.; 3],
            ExpansionEquation::GaussReduced
        )
        .unwrap_err()
        .contains("recollapse"));
    }

    #[test]
    fn public_codazzi_is_div_sigma_plus_normal_flux_with_positive_kappa() {
        let mut node = flrw();
        let flux = [0.2, -0.1, 0.03];
        refresh_mixture(&mut node, 0.7, flux).unwrap();
        for (residual, f) in node.codazzi_residual.iter().zip(flux) {
            assert!((residual - 3. * 0.7 * f).abs() < 1e-15);
        }
        node.shear = [[0.2, 0., 0.], [0., -0.15, 0.], [0., 0., -0.05]];
        node.a = [0.3, 0., 0.];
        refresh_mixture(&mut node, 0.7, [0.; 3]).unwrap();
        assert!((node.codazzi_residual[0] + 0.18).abs() < 1e-15);
    }

    #[test]
    fn radiation_flrw_density_and_hubble_are_exact() {
        let mut n = flrw();
        for _ in 0..37 {
            let mut next =
                advance_geometry(&n, &n, 0.007, 1., isotropic_pressure(), [0.; 3]).unwrap();
            let rho_ratio = (-4. * next.eta).exp();
            let omega = rho_ratio / next.hubble_ratio.powi(2);
            refresh(&mut next, omega, [0.; 3]).unwrap();
            assert!(next.gauss_residual.abs() < 2e-14);
            n = next;
        }
        assert!((n.hubble_ratio - (-2. * n.eta).exp()).abs() < 3e-15);
        assert_eq!(n.shear, [[0.; 3]; 3]);
    }

    #[test]
    fn dust_and_mixed_flrw_use_total_pressure_without_overwriting_photon_density() {
        let mut dust = flrw();
        dust.omega_radiation = 0.;
        let dust = advance_mixture(&dust, &dust, 0.1, 1., [[0.; 3]; 3], [0.; 3]).unwrap();
        assert!((dust.hubble_ratio.powi(2) - (-3.0_f64 * 0.1).exp()).abs() < 3e-16);
        assert_eq!(dust.omega_radiation, 0.);
        let mut mixture = flrw();
        mixture.omega_radiation = 0.25;
        let p = tensor(Matrix3::identity() * (0.25 / 3.0));
        // This is the exact stage RHS q=0.5*(1+0.25); the fractions evolve afterward.
        let out = advance_mixture(&mixture, &mixture, 0.01, 1., p, [0.; 3]).unwrap();
        assert!((out.hubble_ratio.ln() / 0.01 + 1.625).abs() < 1e-14);
        assert_eq!(out.omega_radiation, 0.25);
        assert_eq!(out.gauss_residual, 0.);
        assert!(advance_geometry(&dust, &dust, 0.1, 1., p, [0.; 3]).is_err());
    }

    #[test]
    fn anisotropic_pressure_and_frame_sign_are_observable() {
        let mut base = flrw();
        base.shear = [[0.1, 0., 0.], [0., -0.1, 0.], [0., 0., 0.]];
        base.rotation = [0., 0., 0.5];
        let p = [[0.5, 0.05, 0.], [0.05, 0.3, 0.], [0., 0., 0.2]];
        let dt = 0.001;
        let n = advance_geometry(&base, &base, dt, 0.8, p, [0.; 3]).unwrap();
        let shear_xy_rate = 3.0 * 0.8 * 0.05 + 0.5 * (0.1 - (-0.1));
        assert!((n.shear[0][1] / dt - shear_xy_rate).abs() < 1e-14);
        assert!(
            advance_geometry(&base, &base, dt, 1., isotropic_pressure(), [1., 0., 0.]).is_err()
        );
        // Positive x flux exactly cancels the negative spatial divergence of Sigma.
        base.a = [0.2, 0., 0.];
        refresh(&mut base, 0.5, [0.04, 0., 0.]).unwrap();
        assert!(base.codazzi_residual.iter().all(|x| x.abs() < 5e-17));
    }

    fn native_node(state: &QState, eta: f64) -> RayNode {
        let unpack = |x: [f64; 6]| [[x[0], x[3], x[4]], [x[3], x[1], x[5]], [x[4], x[5], x[2]]];
        RayNode {
            eta,
            shear: unpack(state.s6),
            n: unpack(state.n6),
            a: state.a3,
            hubble_ratio: state.ln_h.exp(),
            ..Default::default()
        }
    }

    fn native_comparison(nsteps: usize) -> f64 {
        let sphere = SphereGrid::new(8, 16);
        let mut ref_state = QState {
            s6: [0.07, -0.05, -0.02, 0.005, 0., 0.],
            n6: [0.13, -0.11, 0., 0., 0., 0.],
            a3: [0.; 3],
            ln_h: 0.,
            m: [1., 0., 0., 0., 1., 0., 0., 0., 1.],
            lg: vec![-1.4; sphere.len()],
            rot: [0.; 3],
            residual: false,
            jac_min: 1.,
            n_p: 0,
            rad: None,
            tail: Tail::Wien,
            k_rad: 4,
            v_b: None,
        };
        let mut active = native_node(&ref_state, 0.);
        let moments = |st: &QState| {
            let (omega, pi, _) = st.sources(&sphere);
            let p = [
                [pi[0], pi[3], pi[4]],
                [pi[3], pi[1], pi[5]],
                [pi[4], pi[5], pi[2]],
            ];
            (
                omega,
                tensor(matrix(p) / (3. * omega) + Matrix3::identity() / 3.),
            )
        };
        // Native QState supplies an independent Fermi-frame scalar geometry and
        // time-varying pressures. This test does not exercise the polarized step.
        let dt = 0.2 / nsteps as f64;
        for _ in 0..nsteps {
            let (om, p) = moments(&ref_state);
            let pred = advance_geometry(&active, &active, dt / 2., om, p, [0.; 3]).unwrap();
            ref_state.rk4_step(&sphere, dt / 2.);
            let (om, p) = moments(&ref_state);
            active = advance_geometry(&active, &pred, dt, om, p, [0.; 3]).unwrap();
            ref_state.rk4_step(&sphere, dt / 2.);
        }
        let reference = native_node(&ref_state, 0.2);
        (matrix(active.shear) - matrix(reference.shear)).norm()
            + (matrix(active.n) - matrix(reference.n)).norm()
            + (active.hubble_ratio - reference.hubble_ratio).abs()
    }

    #[test]
    fn fermi_midpoint_converges_to_native_scalar_geometry() {
        let coarse = native_comparison(4);
        let fine = native_comparison(8);
        assert!(
            fine < coarse / 3.2 && fine < 2e-4,
            "errors {coarse:e}, {fine:e}"
        );
    }
}
