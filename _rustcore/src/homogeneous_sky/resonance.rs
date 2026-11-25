//! R118-C2: source-normalized, localized material-frame resonance diffusion.
//! Scalar, angle-averaged dilute FP (Rybicki 2006, RD-adopted Voigt D).
//! Isolated frozen bath/ground-state density; NOT atomic feedback or
//! polarized angle-frequency redistribution. Ordinary Hz and SI seconds.
use std::f64::consts::PI;
pub const C: f64 = 299792458.;
pub const H_PLANCK: f64 = 6.62607015e-34;
pub const KB: f64 = 1.380649e-23;
pub const R_E: f64 = 2.8179403262e-15;
pub const AMU: f64 = 1.66053906892e-27;
#[derive(Clone, Copy, Debug)]
pub struct AtomicLine {
    pub name: &'static str,
    pub wavelength_m: f64,
    pub a21_s: f64,
    pub mass_kg: f64,
    pub f_lu: f64,
}
impl AtomicLine {
    /// REC event_weight.py::Scalar2PPoleModel, thermal_deposition.py.
    /// A and f independently adopted, not silently rescaled.
    pub fn hydrogen() -> Self {
        Self {
            name: "HI_Lya_unresolved",
            wavelength_m: 1215.6701e-10,
            a21_s: 6.265e8,
            mass_kg: 1.00782503223 * AMU,
            f_lu: 0.4161967179799824,
        }
    }
    /// NIST persistent He I lines, 1s^2 singlet -> 1s2p singlet,
    /// J=0->1. Derive f from A with g_u/g_l=3.
    pub fn helium() -> Self {
        let wavelength_m = 584.33436e-10;
        let a21_s = 1.7989e9;
        let nu = C / wavelength_m;
        Self {
            name: "HeI_584_singlet",
            wavelength_m,
            a21_s,
            mass_kg: 4.00260325413 * AMU,
            f_lu: 3. * C * a21_s / (8. * PI * PI * R_E * nu * nu),
        }
    }
    pub fn nu0(self) -> f64 {
        C / self.wavelength_m
    }
    pub fn oscillator_strength(self) -> f64 {
        self.f_lu
    }
    pub fn calibrate(self, m: Material) -> Result<Calibration, String> {
        Material::new(m.temperature_k, m.n_ground_m3, m.hubble_s, m.p_scatter)?;
        if ![self.wavelength_m, self.a21_s, self.mass_kg, self.f_lu]
            .iter()
            .all(|v| v.is_finite() && *v > 0.)
        {
            return Err("invalid atomic line constants".into());
        }
        let b = (2. * KB * m.temperature_k / self.mass_kg).sqrt() / C;
        let nu0 = self.nu0();
        let width = nu0 * b;
        let damping = self.a21_s / (4. * PI * width);
        let sigma = PI * R_E * C * self.f_lu;
        let rate_scale = C * m.n_ground_m3 * m.p_scatter * sigma / width;
        let peak = rate_scale * voigt_h(damping, 0.)? / PI.sqrt();
        let sobolev_rate = m.n_ground_m3 * C * sigma / (m.hubble_s * nu0);
        if ![b, width, damping, sigma, peak, sobolev_rate]
            .iter()
            .all(|v| v.is_finite())
        {
            return Err("nonfinite resonance calibration".into());
        }
        Ok(Calibration {
            nu0_hz: nu0,
            doppler_fraction: b,
            doppler_width_hz: width,
            damping,
            sigma_integral_m2_hz: sigma,
            rate_scale_s: rate_scale,
            peak_scattering_s: peak,
            sobolev_optical_depth: sobolev_rate,
            recoil_per_scattering_doppler: H_PLANCK * nu0 / (self.mass_kg * C * C * b),
            epsilon_doppler: H_PLANCK * width / (KB * m.temperature_k),
        })
    }
}
#[derive(Clone, Copy, Debug)]
pub struct Material {
    pub temperature_k: f64,
    pub n_ground_m3: f64,
    pub hubble_s: f64,
    pub p_scatter: f64,
}
impl Material {
    pub fn new(t: f64, n: f64, h: f64, p: f64) -> Result<Self, String> {
        if ![t, n, h, p].iter().all(|v| v.is_finite())
            || !(1. ..=1e7).contains(&t)
            || n < 0.
            || h <= 0.
            || !(0. ..=1.).contains(&p)
        {
            return Err("invalid prescribed material state".into());
        }
        Ok(Self {
            temperature_k: t,
            n_ground_m3: n,
            hubble_s: h,
            p_scatter: p,
        })
    }
}
/// The reference carries total neutral species abundance, treated as
/// ground-state abundance in this bounded resonance-only approximation.
/// No excited-level population or branching fraction is inferred here.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Species {
    HI,
    HeI,
}
pub fn from_reference(
    history: &rec_microphysics::species_thermal::ReferenceHistory,
    eta: f64,
    species: Species,
    p_scatter: f64,
) -> Result<(AtomicLine, Material), String> {
    let node = history
        .at(eta)
        .map_err(|e| format!("REC source state: {e:?}"))?;
    let fhe = history.f_he();
    let (line, fraction) = match species {
        Species::HI => (AtomicLine::hydrogen(), node.state.x_hi),
        Species::HeI => (AtomicLine::helium(), node.state.x_hei(fhe)),
    };
    Ok((
        line,
        Material::new(
            node.state.tm(fhe),
            node.n_h_m3 * fraction,
            node.h_s,
            p_scatter,
        )?,
    ))
}
#[derive(Clone, Copy, Debug)]
pub struct Calibration {
    pub nu0_hz: f64,
    pub doppler_fraction: f64,
    pub doppler_width_hz: f64,
    pub damping: f64,
    pub sigma_integral_m2_hz: f64,
    pub rate_scale_s: f64,
    pub peak_scattering_s: f64,
    pub sobolev_optical_depth: f64,
    pub recoil_per_scattering_doppler: f64,
    pub epsilon_doppler: f64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DiffusionProfile {
    Voigt,
    DipoleMoment,
}
impl Calibration {
    pub fn diffusion_x_model(self, x: f64, profile: DiffusionProfile) -> Result<f64, String> {
        let h = match profile {
            DiffusionProfile::Voigt => voigt_h(self.damping, x)?,
            DiffusionProfile::DipoleMoment => voigt_dipole_moment(self.damping, x)?,
        };
        Ok(0.5 * self.rate_scale_s * h / PI.sqrt())
    }
    /// Multiply local phase-volume masses by this factor to obtain
    /// proper isotropic photon number density (two polarization states).
    pub fn phase_density_m3(self) -> f64 {
        8. * PI * self.nu0_hz.powi(2) * self.doppler_width_hz / C.powi(3)
    }
    pub fn scattering_rate(self, x: f64) -> Result<f64, String> {
        Ok(self.rate_scale_s * voigt_h(self.damping, x)? / PI.sqrt())
    }
    /// nu-space diffusion coefficient / Delta_nu_D^2, in s^-1.
    pub fn diffusion_x(self, x: f64) -> Result<f64, String> {
        Ok(self.scattering_rate(x)? * 0.5)
    }
    pub fn diffusion_log(self, x: f64) -> Result<f64, String> {
        let ratio = 1. + self.doppler_fraction * x;
        if ratio <= 0. {
            return Err("nonpositive photon frequency".into());
        }
        Ok(self.diffusion_x(x)? * (self.doppler_fraction / ratio).powi(2))
    }
}
// Positive quadrature of H(a,x)=a/pi int exp(-t^2)/((x-t)^2+a^2) dt.
// Split at dyadic distances from Lorentz pole; base Gaussian grid resolves
// smooth wings. No wing fit or negative polynomial interpolation.
const GX: [f64; 8] = [
    0.09501250983763744,
    0.2816035507792589,
    0.4580167776572274,
    0.6178762444026438,
    0.755404408355003,
    0.8656312023878318,
    0.9445750230732326,
    0.9894009349916499,
];
const GW: [f64; 8] = [
    0.1894506104550685,
    0.1826034150449236,
    0.16915651939500254,
    0.14959598881657673,
    0.12462897125553387,
    0.09515851168249279,
    0.06225352393864789,
    0.027152459411754095,
];
pub fn voigt_h(a: f64, x: f64) -> Result<f64, String> {
    voigt_moment(a, x, false)
}
/// RD dipole second-moment coefficient H+(7/20)H''. Integrating by parts
/// twice gives a strictly positive integrand factor 3/10+7t^2/5.
pub fn voigt_dipole_moment(a: f64, x: f64) -> Result<f64, String> {
    voigt_moment(a, x, true)
}
fn voigt_moment(a: f64, x: f64, dipole: bool) -> Result<f64, String> {
    if !a.is_finite() || !(1e-10..=10.).contains(&a) || !x.is_finite() || x.abs() > 1e6 {
        return Err("Voigt evaluation outside bounded domain".into());
    }
    let x = x.abs();
    let mut edges = (-24..=24).map(|i| i as f64 * 0.5).collect::<Vec<_>>();
    if x < 12. {
        edges.push(x);
        let mut d = a;
        while d < 32. {
            for y in [x - d, x + d] {
                if y > -12. && y < 12. {
                    edges.push(y);
                }
            }
            d *= 2.;
        }
    }
    edges.sort_by(f64::total_cmp);
    edges.dedup();
    let mut q = 0.;
    for u in edges.windows(2) {
        let m = 0.5 * (u[0] + u[1]);
        let h = 0.5 * (u[1] - u[0]);
        for i in 0..8 {
            for sign in [-1., 1.] {
                let t = m + sign * h * GX[i];
                let f = if dipole { 0.3 + 1.4 * t * t } else { 1. };
                q += h * GW[i] * f * (-t * t).exp() * a / ((x - t).powi(2) + a * a);
            }
        }
    }
    Ok(q / PI)
}
fn bernoulli(x: f64) -> f64 {
    if x == 0. {
        1.
    } else {
        x / x.exp_m1()
    }
}
#[derive(Clone, Debug)]
pub struct Patch {
    pub calibration: Calibration,
    pub material: Material,
    pub x: Vec<f64>,
    pub volume: Vec<f64>,
    pub up: Vec<f64>,
    pub down: Vec<f64>,
}
#[derive(Clone, Debug)]
pub struct BoseStep {
    pub step: Step,
    pub iterations: usize,
    pub nonlinear_scaled_residual: f64,
}
#[derive(Clone, Debug)]
pub struct Step {
    pub mass: Vec<f64>,
    pub integrated_flux: Vec<f64>,
    pub number_defect: f64,
    pub continuity_l1: f64,
    pub energy_change_j: f64,
    pub flux_energy_j: f64,
}
#[derive(Clone, Debug)]
pub struct DriftStep {
    pub mass: Vec<f64>,
    pub escaped_mass: f64,
    pub escaped_energy_j: f64,
    pub work_j: f64,
    pub number_defect: f64,
    pub energy_defect: f64,
    pub numerical_second_detuning_moment: f64,
}
impl Patch {
    pub fn full_energy_j(&self, mass: &[f64]) -> Result<f64, String> {
        if mass.len() != self.x.len() || mass.iter().any(|v| !v.is_finite() || *v < 0.) {
            return Err("invalid local number mass".into());
        }
        Ok(H_PLANCK
            * self.calibration.nu0_hz
            * mass
                .iter()
                .zip(&self.x)
                .map(|(m, x)| m * (1. + self.calibration.doppler_fraction * x))
                .sum::<f64>())
    }
    /// Conditional frequency translation only; this is NOT angular
    /// Liouville or volume dilution. Use exact exp(delta zeta) energy
    /// shift and barycentric remap in linear detuning. Zero exterior.
    pub fn shift_log(&self, mass: &[f64], dz: f64) -> Result<DriftStep, String> {
        let e0 = self.full_energy_j(mass)?;
        if !dz.is_finite() || dz.abs() > 1. {
            return Err("invalid local log-frequency shift".into());
        }
        let b = self.calibration.doppler_fraction;
        let mut y = vec![0.; mass.len()];
        let (mut escaped, mut ee, mut spread) = (0., 0., 0.);
        let d = dz.exp_m1();
        for (m, x) in mass.iter().zip(&self.x) {
            if *m == 0. {
                continue;
            }
            let z = x + d * (1. / b + x);
            if z < self.x[0] || z > self.x[self.x.len() - 1] {
                escaped += m;
                ee += H_PLANCK * self.calibration.nu0_hz * (1. + b * z) * m;
                continue;
            }
            let i = self.x.partition_point(|x| *x <= z).saturating_sub(1);
            if i == self.x.len() - 1 {
                y[i] += m;
                continue;
            }
            let l = self.x[i];
            let r = self.x[i + 1];
            let w = (z - l) / (r - l);
            if !(0. ..=1.).contains(&w) {
                return Err("invalid local remap weights".into());
            }
            y[i] += (1. - w) * m;
            y[i + 1] += w * m;
            spread += m * (z - l) * (r - z);
        }
        let n0 = mass.iter().sum::<f64>();
        let n1 = y.iter().sum::<f64>();
        let e1 = self.full_energy_j(&y)?;
        let work = e0 * d;
        Ok(DriftStep {
            mass: y,
            escaped_mass: escaped,
            escaped_energy_j: ee,
            work_j: work,
            number_defect: (n1 + escaped - n0).abs() / n0.max(f64::MIN_POSITIVE),
            energy_defect: (e1 + ee - e0 - work).abs() / e0.max(f64::MIN_POSITIVE),
            numerical_second_detuning_moment: spread,
        })
    }
    pub fn new(line: AtomicLine, m: Material, extent: f64, n: usize) -> Result<Self, String> {
        Self::with_profile(line, m, extent, n, false, DiffusionProfile::Voigt)
    }
    pub fn stretched(line: AtomicLine, m: Material, extent: f64, n: usize) -> Result<Self, String> {
        Self::with_profile(line, m, extent, n, true, DiffusionProfile::Voigt)
    }
    pub fn with_profile(
        line: AtomicLine,
        m: Material,
        extent: f64,
        n: usize,
        stretched: bool,
        profile: DiffusionProfile,
    ) -> Result<Self, String> {
        if !extent.is_finite()
            || extent <= 0.
            || extent > 1e4
            || !(8..=8192).contains(&n)
            || n % 2 != 0
        {
            return Err("invalid local resonance mesh".into());
        }
        let cal = line.calibrate(m)?;
        if 1. - cal.doppler_fraction * extent <= 0. {
            return Err("nonpositive lower frequency".into());
        }
        let x: Vec<_> = (0..=n)
            .map(|i| {
                let u = 2. * i as f64 / n as f64 - 1.;
                if stretched {
                    (u * extent.asinh()).sinh()
                } else {
                    u * extent
                }
            })
            .collect();
        let mut volume = vec![0.; n + 1];
        let mut up = vec![0.; n];
        let mut down = vec![0.; n];
        let b = cal.doppler_fraction;
        for (i, p) in x.windows(2).enumerate() {
            let dx = p[1] - p[0];
            let v0 = 1. + b * p[0];
            let v1 = 1. + b * p[1];
            // Exact integrals of linear hat times quadratic phase density.
            // int_0^1 (1-t)(v0+(v1-v0)t)^2 dt
            volume[i] += dx * (3. * v0 * v0 + 2. * v0 * v1 + v1 * v1) / 12.;
            volume[i + 1] += dx * (v0 * v0 + 2. * v0 * v1 + 3. * v1 * v1) / 12.;
        }
        for (i, p) in x.windows(2).enumerate() {
            let dx = p[1] - p[0];
            let mid = 0.5 * (p[0] + p[1]);
            let conductance = cal.diffusion_x_model(mid, profile)? * (1. + b * mid).powi(2) / dx;
            let delta = cal.epsilon_doppler * dx;
            up[i] = conductance * bernoulli(delta) / volume[i];
            down[i] = conductance * bernoulli(-delta) / volume[i + 1];
        }
        if volume.iter().any(|v| !v.is_finite() || *v <= 0.)
            || up.iter().chain(&down).any(|v| !v.is_finite() || *v < 0.)
        {
            return Err("nonfinite local FP matrix".into());
        }
        Ok(Self {
            calibration: cal,
            material: m,
            x,
            volume,
            up,
            down,
        })
    }
    pub fn wien(&self, center_occupation: f64) -> Result<Vec<f64>, String> {
        if !center_occupation.is_finite() || center_occupation < 0. {
            return Err("invalid Wien amplitude".into());
        }
        let y: Vec<_> = self
            .x
            .iter()
            .zip(&self.volume)
            .map(|(x, v)| v * center_occupation * (-self.calibration.epsilon_doppler * x).exp())
            .collect();
        if y.iter().any(|v| !v.is_finite()) {
            return Err("Wien amplitude overflow".into());
        }
        Ok(y)
    }
    pub fn bose(&self, chemical_potential_k_t: f64) -> Result<Vec<f64>, String> {
        let eps0 = H_PLANCK * self.calibration.nu0_hz / (KB * self.material.temperature_k);
        if !chemical_potential_k_t.is_finite()
            || eps0 + self.calibration.epsilon_doppler * self.x[0] <= chemical_potential_k_t
        {
            return Err("Bose chemical potential reaches lowest mode".into());
        }
        let v: Vec<_> = self
            .x
            .iter()
            .zip(&self.volume)
            .map(|(x, v)| {
                v / (eps0 + self.calibration.epsilon_doppler * x - chemical_potential_k_t).exp_m1()
            })
            .collect();
        if v.iter().any(|v| !v.is_finite() || *v < 0.) {
            return Err("invalid Bose equilibrium".into());
        }
        Ok(v)
    }
    pub fn be_step(&self, mass: &[f64], dt_s: f64) -> Result<Vec<f64>, String> {
        Ok(self.be_audit(mass, dt_s)?.mass)
    }
    /// Positive conservative tridiagonal implicit solve. Eliminate using
    /// p_i = a_i+t_i, t_i=1+b_(i-1)*t_(i-1)/p_(i-1), avoiding subtraction
    /// of two large rates. Integrated flux from eliminated row:
    /// F_i = rhs_i-t_i*y_i, not a_i*y_i-b_i*y_(i+1).
    pub fn be_audit(&self, mass: &[f64], dt_s: f64) -> Result<Step, String> {
        self.linear_step(mass, dt_s, &self.up, &self.down)
    }
    /// Scalar nonlinear stimulated FP using lagged positive occupation
    /// factors and the full conservative implicit chain. Reject an
    /// unconverged nonlinear solve. This is not a polarized Bose operator.
    pub fn bose_step(&self, mass: &[f64], dt_s: f64) -> Result<BoseStep, String> {
        let n = self.x.len();
        if mass.len() != n
            || mass.iter().any(|x| !x.is_finite() || *x < 0.)
            || !dt_s.is_finite()
            || dt_s < 0.
        {
            return Err("invalid Bose FP state".into());
        }
        let total = mass.iter().sum::<f64>().max(f64::MIN_POSITIVE);
        let mut current = mass.to_vec();
        for k in 1..=100 {
            let a: Vec<_> = self
                .up
                .iter()
                .enumerate()
                .map(|(i, a)| a * (1. + current[i + 1] / self.volume[i + 1]))
                .collect();
            let b: Vec<_> = self
                .down
                .iter()
                .enumerate()
                .map(|(i, b)| b * (1. + current[i] / self.volume[i]))
                .collect();
            let y = self.linear_step(mass, dt_s, &a, &b)?;
            let change = y
                .mass
                .iter()
                .zip(&current)
                .map(|(u, v)| (u - v).abs())
                .sum::<f64>()
                / total;
            if change < 64. * f64::EPSILON {
                // Direct nonlinear edge flux check, scaled by local
                // forward/backward terms to remain meaningful in stiff cells.
                let mut max: f64 = 0.;
                for i in 0..n - 1 {
                    let l =
                        dt_s * self.up[i] * y.mass[i] * (1. + y.mass[i + 1] / self.volume[i + 1]);
                    let r = dt_s * self.down[i] * y.mass[i + 1] * (1. + y.mass[i] / self.volume[i]);
                    let residual = (l - r - y.integrated_flux[i]).abs() / (l + r + total);
                    if !residual.is_finite() {
                        return Err("nonfinite Bose residual".into());
                    }
                    max = max.max(residual);
                }
                if max <= 1e-11 {
                    return Ok(BoseStep {
                        step: y,
                        iterations: k,
                        nonlinear_scaled_residual: max,
                    });
                }
            }
            current = y.mass;
        }
        Err("scalar Bose FP fixed point did not converge".into())
    }
    fn linear_step(
        &self,
        mass: &[f64],
        dt_s: f64,
        up: &[f64],
        down: &[f64],
    ) -> Result<Step, String> {
        let n = self.x.len();
        if mass.len() != n
            || !dt_s.is_finite()
            || dt_s < 0.
            || mass.iter().any(|v| !v.is_finite() || *v < 0.)
        {
            return Err("invalid FP step".into());
        }
        let a: Vec<_> = up.iter().map(|v| dt_s * v).collect();
        let b: Vec<_> = down.iter().map(|v| dt_s * v).collect();
        if a.iter().chain(&b).any(|v| !v.is_finite() || *v > 1e250) {
            return Err("FP rate overflow".into());
        }
        let mut t = vec![1.; n];
        let mut p = vec![0.; n];
        let mut rhs = mass.to_vec();
        p[0] = 1. + a[0];
        for i in 1..n {
            t[i] = 1. + b[i - 1] * (t[i - 1] / p[i - 1]);
            rhs[i] += (a[i - 1] / p[i - 1]) * rhs[i - 1];
            p[i] = t[i] + if i < n - 1 { a[i] } else { 0. };
        }
        let mut y = vec![0.; n];
        y[n - 1] = rhs[n - 1] / p[n - 1];
        for i in (0..n - 1).rev() {
            y[i] = (rhs[i] + b[i] * y[i + 1]) / p[i];
        }
        let flux: Vec<_> = (0..n - 1).map(|i| rhs[i] - t[i] * y[i]).collect();
        let mut err = 0.;
        for i in 0..n {
            let l = if i == 0 { 0. } else { flux[i - 1] };
            let r = if i == n - 1 { 0. } else { flux[i] };
            err += (y[i] - mass[i] + r - l).abs();
        }
        let total = mass.iter().sum::<f64>();
        let delta = self.energy_change_j(mass, &y)?;
        let en = H_PLANCK
            * self.calibration.doppler_width_hz
            * flux
                .iter()
                .zip(self.x.windows(2))
                .map(|(f, v)| f * (v[1] - v[0]))
                .sum::<f64>();
        if y.iter().any(|v| !v.is_finite() || *v < 0.) || !en.is_finite() || !err.is_finite() {
            return Err("invalid implicit FP result".into());
        }
        Ok(Step {
            number_defect: (y.iter().sum::<f64>() - total).abs() / total.max(f64::MIN_POSITIVE),
            continuity_l1: err / total.max(f64::MIN_POSITIVE),
            mass: y,
            integrated_flux: flux,
            energy_change_j: delta,
            flux_energy_j: en,
        })
    }
    /// At fixed number compute energy exchange using detuning only.
    /// Units J times dimensionless local mass normalization; no claim of
    /// physical volume heating until the missing phase-space scale is applied.
    pub fn energy_change_j(&self, a: &[f64], b: &[f64]) -> Result<f64, String> {
        if a.len() != self.x.len() || b.len() != a.len() {
            return Err("invalid energy arrays".into());
        }
        Ok(H_PLANCK
            * self.calibration.doppler_width_hz
            * a.iter()
                .zip(b)
                .zip(&self.x)
                .map(|((u, v), x)| (v - u) * x)
                .sum::<f64>())
    }
}
/// Scalar two-node BE for Bose-stimulated transitions, independent of
/// the dilute full-chain solver. Masses include their phase volumes.
/// Positive bracket, no clipping. Detailed balance gives BE equilibrium.
pub fn bose_pair_be(
    l: f64,
    r: f64,
    vl: f64,
    vr: f64,
    a: f64,
    b: f64,
    dt: f64,
) -> Result<(f64, f64), String> {
    if ![l, r, vl, vr, a, b, dt].iter().all(|v| v.is_finite())
        || l < 0.
        || r < 0.
        || vl <= 0.
        || vr <= 0.
        || a < 0.
        || b < 0.
        || dt < 0.
    {
        return Err("invalid Bose pair".into());
    }
    let total = l + r;
    if total == 0. || dt == 0. || a == 0. && b == 0. {
        return Ok((l, r));
    }
    // Scale implicit residual to avoid stiff dt multiplication overflow.
    let scale = 1. / dt.max(1.);
    let h = dt * scale;
    let mut lo = 0.;
    let mut hi = total;
    for _ in 0..96 {
        let x = 0.5 * (lo + hi);
        let y = total - x;
        let f = h * (a * y * (1. + x / vr) - b * x * (1. + y / vl)) - scale * (x - r);
        if !f.is_finite() {
            return Err("nonfinite Bose pair flux".into());
        }
        if f > 0. {
            lo = x;
        } else {
            hi = x;
        }
        if hi - lo <= 2. * f64::EPSILON * total {
            break;
        }
    }
    let x = 0.5 * (lo + hi);
    Ok((total - x, x))
}
