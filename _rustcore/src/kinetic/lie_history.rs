//! Finite homogeneous radiation-sourced backgrounds and polarized normal-ray transport.
//! Time is eta = ln(a/a_initial), and Sigma, N, A and R are Hubble-normalized.
//! The QState background carries scalar, collisionless, bolometric radiation. Its
//! quadrature supplies anisotropic stress to Einstein's equations. Polarized rays
//! propagated afterwards are tracers on that solution.
use nalgebra::{Matrix3, Rotation3, UnitQuaternion, Vector3};

use crate::geom::group::BianchiGroup;
use crate::kinetic::collide_exact::Kernel;
use crate::kinetic::comoving::{ln_phys_weights, moments_log, phys_dirs, Frame};
use crate::kinetic::qevolve::{Config, QState};
use crate::kinetic::radial::Tail;
use crate::kinetic::radiation_feedback::refresh_mixture;
use crate::kinetic::sphere::SphereGrid;
use crate::runtime::typeii_photon_host::typeii_physical_guard::ScreenInputPolicy;
use crate::runtime::typeii_photon_host::typeii_polarized_liouville::{
    transport_characteristic, HomogeneousRayBackground,
};

#[derive(Clone, Debug)]
pub struct RayNode {
    pub eta: f64,
    pub shear: [[f64; 3]; 3],
    pub n: [[f64; 3]; 3],
    pub a: [f64; 3],
    pub rotation: [f64; 3],
    pub hubble_ratio: f64,
    pub omega_radiation: f64,
    pub gauss_residual: f64,
    /// Signed Hubble-normalized (D_b sigma^b_a + kappa q_a)/H^2.
    pub codazzi_residual: [f64; 3],
    pub jacobi_residual: [f64; 3],
}

impl Default for RayNode {
    fn default() -> Self {
        Self {
            eta: 0.,
            shear: [[0.; 3]; 3],
            n: [[0.; 3]; 3],
            a: [0.; 3],
            rotation: [0.; 3],
            hubble_ratio: 1.,
            omega_radiation: 1.,
            gauss_residual: 0.,
            codazzi_residual: [0.; 3],
            jacobi_residual: [0.; 3],
        }
    }
}

#[derive(Clone, Debug)]
pub struct RayStep {
    pub e: [f64; 3],
    /// Maps initial to final tetrad components, including the screen twist.
    pub rotation: [[f64; 3]; 3],
    pub log_energy: f64,
    /// ln(dOmega_final/dOmega_initial) for photon propagation directions.
    pub log_area: f64,
}

fn sym(v: [f64; 6]) -> [[f64; 3]; 3] {
    [[v[0], v[3], v[4]], [v[3], v[1], v[5]], [v[4], v[5], v[2]]]
}
fn matrix(rows: [[f64; 3]; 3]) -> Matrix3<f64> {
    Matrix3::from_fn(|i, j| rows[i][j])
}
fn rows(m: Matrix3<f64>) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}

// Original BASS bianchi/algebra.py::CANONICAL; h = a_1^2/(n_2 n_3).
fn canonical(family: &str) -> Result<([f64; 3], f64), String> {
    match family {
        "I" | "FLRW" => Ok(([0., 0., 0.], 0.)),
        "II" => Ok(([1., 0., 0.], 0.)),
        "III" => Ok(([0., 1., -1.], 1.)),
        "IV" => Ok(([0., 0., 1.], 1.)),
        "V" => Ok(([0., 0., 0.], 1.)),
        "VI0" => Ok(([0., 1., -1.], 0.)),
        "VIstar" => Ok(([0., 3., -3.], 1.)),
        "VII0" => Ok(([0., 1., 1.], 0.)),
        "VIII" => Ok(([-1., 1., 1.], 0.)),
        "IX" => Ok(([1., 1., 1.], 0.)),
        _ => {
            let (name, arg) = family.split_once(':').unwrap_or((family, ""));
            let sign = match name {
                "VIh" => -1.,
                "VIIh" => 1.,
                _ => return Err(format!("unknown Bianchi family {family}")),
            };
            let h = if !family.contains(':') {
                0.25 * sign
            } else {
                arg.parse::<f64>()
                    .map_err(|_| format!("invalid h in {family}"))?
            };
            if !h.is_finite() || sign * h <= 0. {
                return Err(format!("invalid h in {family}"));
            }
            Ok(([0., 1., sign], h.abs().sqrt()))
        }
    }
}

/// User-supplied right-handed orthonormal Fermi-frame Lie data in Hubble units.
/// Sigma is trace-free and symmetric, N symmetric, and Jacobi requires N A = 0.
#[derive(Clone, Debug, Default)]
pub struct LieInitial {
    pub shear: [[f64; 3]; 3],
    pub n: [[f64; 3]; 3],
    pub a: [f64; 3],
}

fn packed(m: [[f64; 3]; 3]) -> [f64; 6] {
    [m[0][0], m[1][1], m[2][2], m[0][1], m[0][2], m[1][2]]
}

fn gauss_energy(node: &RayNode) -> f64 {
    let (curvature, _) = BianchiGroup::new(packed(node.n), node.a).curvature();
    1. - matrix(node.shear).norm_squared() / 6. - curvature
}

/// Construct an initial geometric node with total Omega fixed by Gauss.
/// Before matter is assigned the omega_radiation slot holds this total;
/// At zero supplied material flux the signed Codazzi residual equals −kappa*q_required/H².
pub fn initial_lie_node(initial: &LieInitial) -> Result<RayNode, String> {
    let mut node = RayNode {
        shear: initial.shear,
        n: initial.n,
        a: initial.a,
        ..Default::default()
    };
    for (m, trace_free) in [(matrix(node.shear), true), (matrix(node.n), false)] {
        if !m.iter().all(|v| v.is_finite())
            || (m - m.transpose()).norm() > 1e-12 * (1. + m.norm())
            || (trace_free && m.trace().abs() > 1e-12 * (1. + m.norm()))
        {
            return Err("Lie tensors must be finite and symmetric and Sigma traceless".into());
        }
    }
    if !node.a.iter().all(|v| v.is_finite()) {
        return Err("Lie A must be finite".into());
    }
    let n = matrix(node.n);
    let a = Vector3::from(node.a);
    if (n * a).norm() > 1e-12 * n.norm() * a.norm() {
        return Err("initial Lie algebra violates Jacobi N A = 0".into());
    }
    let omega = gauss_energy(&node);
    if !omega.is_finite() || omega <= 0. {
        return Err("initial Gauss surface has nonpositive total density".into());
    }
    node.omega_radiation = omega;
    refresh_mixture(&mut node, omega, [0.; 3])?;
    if Vector3::from(node.codazzi_residual).norm() > 3. * omega * (1. + 1e-12) {
        return Err("initial Codazzi requires a superluminal total normal energy flux".into());
    }
    Ok(node)
}

/// q_required / E_total = (3 Sigma A + epsilon:N Sigma)/(3 Omega_total).
/// Input is an admissible geometric node. This reconstructs total Omega from
/// its geometry and deliberately does not use the photon-only density slot.
/// Returns NaNs for a node outside the finite, positive Gauss domain.
pub fn required_flux(node: &RayNode) -> [f64; 3] {
    let omega = gauss_energy(node);
    let mut zero_flux = node.clone();
    if !omega.is_finite() || omega <= 0. || refresh_mixture(&mut zero_flux, omega, [0.; 3]).is_err()
    {
        return [f64::NAN; 3];
    }
    zero_flux.codazzi_residual.map(|v| -v / (3. * omega))
}

fn snapshot(eta: f64, state: &QState, grid: &SphereGrid) -> Result<RayNode, String> {
    let frame = Frame { m: state.m };
    let (e, mu) = phys_dirs(&frame, &grid.ehat);
    let weights = ln_phys_weights(&frame, &grid.w, &mu);
    let (log_rho, flux, _) = moments_log(&weights, &state.lg, &e);
    let omega = (log_rho - 3f64.ln() - 2. * state.ln_h).exp();
    if !omega.is_finite() || omega <= 0. {
        return Err(format!(
            "nonfinite or degenerate radiation background at eta={eta}"
        ));
    }
    let mut node = RayNode {
        eta,
        shear: sym(state.s6),
        n: sym(state.n6),
        a: state.a3,
        rotation: state.rot,
        hubble_ratio: state.ln_h.exp(),
        omega_radiation: omega,
        ..Default::default()
    };
    refresh_mixture(&mut node, omega, flux)?;
    Ok(node)
}

/// Finite, Gauss-initialized radiation-only Bianchi evolution. Initial normal
/// shear is diag(s,-s/2,-s/2) in class A and diag(0,s,-s) in class B, with
/// canonical structure constants multiplied by 0.3 and an initially isotropic
/// radiation sky. Setting s=0 gives the flat FLRW solution for family I.
/// VIh:<h> and VIIh:<h> select the continuously varying dimensionless group h.
pub fn radiation_history(
    family: &str,
    shear_amplitude: f64,
    duration: f64,
    steps: usize,
    n_mu: usize,
    n_phi: usize,
) -> Result<Vec<RayNode>, String> {
    if family == "FLRW" && shear_amplitude != 0. {
        return Err("flat FLRW requires zero shear".into());
    }
    let (diag, a1) = canonical(family)?;
    let s = shear_amplitude;
    let s6 = if a1 == 0. {
        [s, -0.5 * s, -0.5 * s, 0., 0., 0.]
    } else {
        [0., s, -s, 0., 0., 0.]
    };
    let n6 = [0.3 * diag[0], 0.3 * diag[1], 0.3 * diag[2], 0., 0., 0.];
    let a3 = [0.3 * a1, 0., 0.];
    radiation_history_from_lie(
        &LieInitial {
            shear: sym(s6),
            n: sym(n6),
            a: a3,
        },
        duration,
        steps,
        n_mu,
        n_phi,
    )
}

/// Evolve this Lie geometry with initially isotropic radiation as the sole material
/// source. A nonzero required initial flux needs a different matter distribution.
pub fn radiation_history_from_lie(
    initial: &LieInitial,
    duration: f64,
    steps: usize,
    n_mu: usize,
    n_phi: usize,
) -> Result<Vec<RayNode>, String> {
    if !duration.is_finite()
        || duration == 0.
        || steps == 0
        || n_mu < 4
        || n_phi < 4
        || !n_phi.is_multiple_of(2)
        || n_mu.checked_mul(n_phi).is_none()
    {
        return Err(
            "finite nonzero time span, at least one step, n_mu >= 4 and even n_phi >= 4 required"
                .into(),
        );
    }
    let initial = initial_lie_node(initial)?;
    let omega = initial.omega_radiation;
    if Vector3::from(initial.codazzi_residual).norm() > 3. * omega * 1e-12 {
        return Err("isotropic radiation cannot supply the initial Codazzi-required flux".into());
    }
    let s6 = packed(initial.shear);
    let n6 = packed(initial.n);
    let a3 = initial.a;
    let grid = SphereGrid::new(n_mu, n_phi);
    let intensity = 3. * omega / grid.w.iter().sum::<f64>();
    let mut state = QState {
        s6,
        n6,
        a3,
        ln_h: 0.,
        m: [1., 0., 0., 0., 1., 0., 0., 0., 1.],
        lg: vec![intensity.ln(); grid.len()],
        rot: [0.; 3],
        residual: true,
        jac_min: 1.,
        n_p: 0,
        rad: None,
        tail: Tail::Wien,
        k_rad: 4,
        v_b: None,
    };
    let cfg = Config {
        v_b: None,
        dtau: duration / (steps as f64),
        nsteps: steps,
        nu: 0.,
        kernel: Kernel::Thomson,
        k_theta: 4,
        k_phi: 4,
        sub: 2,
        keep_every: 0,
        nu_sched: vec![],
        h_anchor: 0.,
    };
    let mut output = vec![snapshot(0., &state, &grid)?];
    for step in 0..steps {
        state.strang_step_at(&grid, &cfg, step);
        output.push(snapshot(
            duration * ((step + 1) as f64 / steps as f64),
            &state,
            &grid,
        )?);
    }
    Ok(output)
}

fn background(node: &RayNode) -> HomogeneousRayBackground {
    HomogeneousRayBackground {
        expansion: 1.,
        shear: node.shear,
        structure_n: node.n,
        class_b_a: node.a,
        triad_rotation: node.rotation,
    }
}

fn midpoint(left: &RayNode, right: &RayNode, f: f64) -> HomogeneousRayBackground {
    let blend = |a: f64, b: f64| a + (b - a) * f;
    let mat = |a: [[f64; 3]; 3], b: [[f64; 3]; 3]| {
        std::array::from_fn(|i| std::array::from_fn(|j| blend(a[i][j], b[i][j])))
    };
    let vec = |a: [f64; 3], b: [f64; 3]| std::array::from_fn(|i| blend(a[i], b[i]));
    HomogeneousRayBackground {
        expansion: 1.,
        shear: mat(left.shear, right.shear),
        structure_n: mat(left.n, right.n),
        class_b_a: vec(left.a, right.a),
        triad_rotation: vec(left.rotation, right.rotation),
    }
}

fn rotation_bound(node: &RayNode) -> f64 {
    let b = background(node);
    let n = matrix(b.structure_n);
    matrix(b.shear).norm()
        + n.norm()
        + 0.5 * n.trace().abs()
        + Vector3::from(b.class_b_a).norm()
        + Vector3::from(b.triad_rotation).norm()
}

/// Propagate e, its polarization frame, log energy, and angular area under the
/// same original BASS midpoint Lie rotation. The sphere divergence of e' is
/// 3 e.Sigma.e + 2 A.e; rotation and N give divergence-free vector fields.
pub fn advance_ray(left: &RayNode, right: &RayNode, e: [f64; 3]) -> Result<RayStep, String> {
    let dt = right.eta - left.eta;
    let mut dir = Vector3::from(e);
    if !dt.is_finite() || !dir.norm_squared().is_finite() || (dir.norm_squared() - 1.).abs() > 1e-9
    {
        return Err("finite interval and unit normal-frame photon direction required".into());
    }
    for node in [left, right] {
        if !node
            .shear
            .iter()
            .flatten()
            .chain(node.n.iter().flatten())
            .chain(&node.a)
            .chain(&node.rotation)
            .all(|x| x.is_finite())
            || (matrix(node.shear) - matrix(node.shear).transpose()).norm() > 1e-10
            || matrix(node.shear).trace().abs() > 1e-10
            || (matrix(node.n) - matrix(node.n).transpose()).norm() > 1e-10
        {
            return Err("invalid symmetric N or symmetric trace-free Sigma".into());
        }
    }
    // Keep the principal square root of each midpoint SO(3) step single-valued.
    // Short rotations also keep the inherited implicit midpoint iteration contractive.
    let bound = dt.abs() * rotation_bound(left).max(rotation_bound(right));
    if !bound.is_finite() || bound > 20000. {
        return Err("ray interval requires subdivision of its history".into());
    }
    let count = (bound / 0.2).ceil().max(1.) as usize;
    let h = dt / count as f64;
    let mut rotation = Matrix3::identity();
    let mut log_energy = 0.;
    let mut log_area = 0.;
    for k in 0..count {
        let b = midpoint(left, right, (k as f64 + 0.5) / count as f64);
        let out = transport_characteristic(
            dir.into(),
            &b,
            &b,
            h,
            1,
            &[0.; 9],
            ScreenInputPolicy::Reject { tolerance: 1e-12 },
        )
        .map_err(|e| format!("{e:?}"))?;
        let r = matrix(out.spatial_transport);
        let half =
            UnitQuaternion::from_rotation_matrix(&Rotation3::from_matrix_unchecked(r)).powf(0.5);
        let mid = half * dir;
        // Evaluate the small anisotropic divergence directly, even when
        // |Sigma| is below the relative precision of the isotropic redshift.
        log_area += h
            * (3. * mid.dot(&(matrix(b.shear) * mid)) + 2. * Vector3::from(b.class_b_a).dot(&mid));
        rotation = r * rotation;
        dir = Vector3::from(out.direction);
        log_energy += out.log_energy_shift;
    }
    Ok(RayStep {
        e: dir.into(),
        rotation: rows(rotation),
        log_energy,
        log_area,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn marched(node: &RayNode, direction: [f64; 3], duration: f64, steps: usize) -> RayStep {
        let mut out = RayStep {
            e: direction,
            log_area: 0.,
            log_energy: 0.,
            rotation: rows(Matrix3::identity()),
        };
        for i in 0..steps {
            let mut left = node.clone();
            left.eta = duration * i as f64 / steps as f64;
            let mut right = node.clone();
            right.eta = duration * (i + 1) as f64 / steps as f64;
            let step = advance_ray(&left, &right, out.e).unwrap();
            out.e = step.e;
            out.log_area += step.log_area;
            out.log_energy += step.log_energy;
            out.rotation = rows(matrix(step.rotation) * matrix(out.rotation));
        }
        out
    }

    fn minus_divergence(initial: &LieInitial) -> Vector3<f64> {
        // Orthonormal-frame covariant divergence of the mixed shear tensor.
        // The independent path uses all 27 spatial Koszul coefficients.
        let c = BianchiGroup::new(packed(initial.n), initial.a).structure_constants();
        let conn = |up: usize, i: usize, j: usize| 0.5 * (c[up][i][j] - c[i][j][up] + c[j][up][i]);
        Vector3::from_fn(|a, _| {
            let mut value = 0.;
            for b in 0..3 {
                for d in 0..3 {
                    value +=
                        conn(d, b, a) * initial.shear[b][d] - conn(b, b, d) * initial.shear[d][a];
                }
            }
            value
        })
    }

    #[test]
    fn codazzi_required_flux_has_koszul_sign_in_both_lie_classes() {
        let shear = sym([0.12, -0.07, -0.05, 0.08, -0.03, 0.06]);
        let class_a = LieInitial {
            shear,
            n: sym([0.4, 0.1, -0.2, 0., 0., 0.]),
            a: [0.; 3],
        };
        let class_b = LieInitial {
            shear,
            n: sym([0., 0.3, -0.2, 0., 0., 0.07]),
            a: [0.15, 0., 0.],
        };
        for input in [class_a, class_b] {
            let mut node = initial_lie_node(&input).unwrap();
            let total = node.omega_radiation;
            let required = required_flux(&node);
            assert!(Vector3::from(required).norm() > 1e-3);
            assert!(
                (Vector3::from(required) * 3. * total - minus_divergence(&input)).norm() < 1e-14
            );
            assert!(radiation_history_from_lie(&input, 0.05, 4, 8, 16).is_err());
            node.omega_radiation = total * 0.65;
            assert_eq!(required_flux(&node), required);
            refresh_mixture(&mut node, total, required).unwrap();
            assert!(
                node.gauss_residual.abs() < 2e-15
                    && Vector3::from(node.codazzi_residual).norm() < 2e-15
            );
        }
    }

    #[test]
    fn generic_rotated_initial_data_preserve_constraints_and_reject_forbidden_inputs() {
        let r = Rotation3::from_euler_angles(0.24, -0.3, 0.47);
        let n = r.matrix()
            * Matrix3::from_diagonal(&Vector3::new(0., 0.3, -0.2))
            * r.matrix().transpose();
        let shear = r.matrix()
            * Matrix3::from_diagonal(&Vector3::new(0., 0.1, -0.1))
            * r.matrix().transpose();
        let a = r * Vector3::new(0.16, 0., 0.);
        let ic = LieInitial {
            shear: rows(shear),
            n: rows(n),
            a: a.into(),
        };
        let h = radiation_history_from_lie(&ic, 0.05, 4, 8, 16).unwrap();
        assert!(h[0].n[0][1].abs() > 0.01 && Vector3::from(required_flux(&h[0])).norm() < 1e-14);
        assert!(Vector3::from(h.last().unwrap().jacobi_residual).norm() < 1e-12);
        let mut bad = ic.clone();
        bad.a = [1., 0., 0.];
        assert!(initial_lie_node(&bad).unwrap_err().contains("Jacobi"));
        let mut bad = ic.clone();
        bad.n[0][1] += 0.02;
        assert!(initial_lie_node(&bad).is_err());
        let mut bad = ic.clone();
        bad.shear[1][1] += 0.02;
        assert!(initial_lie_node(&bad).is_err());
        let bad = LieInitial {
            shear: sym([2., -1., -1., 0., 0., 0.]),
            ..Default::default()
        };
        assert!(initial_lie_node(&bad).unwrap_err().contains("nonpositive"));
        let bad = LieInitial {
            shear: sym([0., 0., 0., 1.6, 0., 0.]),
            n: sym([0., 0., 0., 0., 0., 0.]),
            a: [0.3, 0., 0.],
        };
        assert!(initial_lie_node(&bad).unwrap_err().contains("superluminal"));
    }

    #[test]
    fn exact_bianchi_i_redshift_and_area_converge() {
        let node = RayNode {
            shear: sym([0.4, -0.3, -0.1, 0., 0., 0.]),
            ..Default::default()
        };
        let e = Vector3::new(0.4, 0.7, -0.3).normalize();
        let duration = 0.7;
        let p = Vector3::from_fn(|i, _| e[i] * (-duration * node.shear[i][i]).exp());
        let err = |n| {
            let v = marched(&node, e.into(), duration, n);
            (Vector3::from(v.e) - p.normalize())
                .norm()
                .max((v.log_energy + duration - p.norm().ln()).abs())
                .max((v.log_area + 3. * p.norm().ln()).abs())
        };
        assert!(err(32) < err(16) / 3.8 && err(32) < 1e-5);
    }

    #[test]
    fn class_b_solid_angle_matches_differential_and_forward_backward() {
        let n = RayNode {
            shear: sym([0., 0.13, -0.13, 0., 0., -0.1]),
            n: sym([0., 0.3, -0.3, 0., 0., 0.12]),
            a: [0.11, 0., 0.],
            rotation: [0.05, -0.01, 0.02],
            ..Default::default()
        };
        let e = Vector3::new(0.4, 0.5, 0.6).normalize();
        let t1 = e.cross(&Vector3::z()).normalize();
        let t2 = e.cross(&t1);
        let v = marched(&n, e.into(), 0.31, 24);
        let deriv = |t: Vector3<f64>| {
            let delta = 1e-5;
            let f = |x: Vector3<f64>| Vector3::from(marched(&n, x.normalize().into(), 0.31, 24).e);
            (f(e + delta * t) - f(e - delta * t)) / (2. * delta)
        };
        let j = Vector3::from(v.e).dot(&deriv(t1).cross(&deriv(t2)));
        assert!(
            (v.log_area - j.ln()).abs() < 8e-7,
            "{}, {}",
            v.log_area,
            j.ln()
        );
        let back = marched(&n, v.e, -0.31, 24);
        assert!((Vector3::from(back.e) - e).norm() < 2e-13);
        assert!((matrix(back.rotation) * matrix(v.rotation) - Matrix3::identity()).norm() < 3e-13);
        assert!((back.log_energy + v.log_energy).abs() < 2e-13);
        assert!((back.log_area + v.log_area).abs() < 2e-13);
    }

    #[test]
    fn original_all_family_histories_and_varying_h() {
        for family in [
            "I", "II", "III", "IV", "V", "VI0", "VIh", "VIstar", "VII0", "VIIh", "VIII", "IX",
            "VIh:-0.5", "VIIh:0.7",
        ] {
            let h = radiation_history(family, 0.06, 0.04, 4, 8, 16).unwrap();
            assert_eq!(h.len(), 5);
            let first = &h[0];
            let last = h.last().unwrap();
            assert!(
                first.gauss_residual.abs() < 2e-14
                    && Vector3::from(first.codazzi_residual).norm() < 2e-14
            );
            assert!(last.hubble_ratio < first.hubble_ratio && last.omega_radiation > 0.);
            assert!((matrix(last.shear) - matrix(first.shear)).norm() > 1e-4);
            assert!(Vector3::from(last.jacobi_residual).norm() < 1e-12);
            assert!(
                last.gauss_residual.abs() < 5e-4
                    && Vector3::from(last.codazzi_residual).norm() < 5e-4
            );
            if let Some((_, value)) = family.split_once(':') {
                let asked = value.parse::<f64>().unwrap();
                let expected = first.a[0].powi(2) / (first.n[1][1] * first.n[2][2]);
                assert!((expected - asked).abs() < 1e-14);
            }
        }
        assert!(radiation_history("VIh:0.5", 0.1, 0.1, 2, 8, 16).is_err());
        assert!(radiation_history("VIIh:-0.5", 0.1, 0.1, 2, 8, 16).is_err());
    }

    #[test]
    fn flat_radiation_and_spin_transport_have_independent_exact_controls() {
        let h = radiation_history("FLRW", 0., 0.1, 10, 8, 16).unwrap();
        let end = h.last().unwrap();
        assert!((end.hubble_ratio - (-0.2_f64).exp()).abs() < 1e-11);
        assert!(matrix(end.shear).norm() < 1e-11);
        let n = RayNode {
            rotation: [0., 0., 0.9],
            ..Default::default()
        };
        let v = marched(&n, [0., 0., 1.], 0.3, 4);
        assert_eq!(v.e, [0., 0., 1.]);
        assert!((v.rotation[1][0] - (0.27_f64).sin()).abs() < 1e-14);
        assert!(v.log_area.abs() < 2e-14 && (v.log_energy + 0.3).abs() < 1e-14);
    }
}
