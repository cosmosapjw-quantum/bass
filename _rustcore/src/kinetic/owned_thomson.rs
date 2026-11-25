//! Opt-in coupled nonlinear rest-electron Thomson and collisionless matter.
use super::{
    lie_history::RayNode,
    memory_mixture::{stf_components, stf_matrix},
    owned_vlasov::{Matter, OwnedModel, OwnedState},
    radiation_feedback::advance_mixture,
};
use crate::homogeneous_sky::{field::HarmonicSky, scatter_with, CollisionScheme};
use nalgebra::Matrix3;
const OG: f64 = 5.4437488671046486e-5;
const OL: f64 = 0.684908;
const H0: f64 = 2.1842852410855023e-18;
const C_SIG: f64 = 299792458. * 6.6524587051e-29;
#[derive(Clone)]
pub struct ThomsonState {
    pub geometry: OwnedState,
    pub sky: HarmonicSky,
    initial_a: f64,
}
pub struct ThomsonOwner {
    model: OwnedModel,
    l: usize,
    nt: usize,
    np: usize,
    owner_identity: String,
}
fn rows(m: Matrix3<f64>) -> [[f64; 3]; 3] {
    std::array::from_fn(|i| std::array::from_fn(|j| m[(i, j)]))
}
impl ThomsonOwner {
    pub fn new(
        eps: f64,
        nr: usize,
        nt: usize,
        np: usize,
        l: usize,
        st: usize,
        sp: usize,
    ) -> Result<Self, String> {
        let model = OwnedModel::new(eps, nr, nt, np)?;
        HarmonicSky::isotropic(l, st, sp, true)?;
        Ok(Self {
            model,
            l,
            nt: st,
            np: sp,
            owner_identity: format!("{:016x} {nr} {nt} {np} {l} {st} {sp}", eps.to_bits()),
        })
    }
    pub fn initial(&self, a: f64, s: [f64; 5]) -> Result<ThomsonState, String> {
        let mut t = ThomsonState {
            geometry: self.model.initial(a, s)?,
            sky: HarmonicSky::isotropic(self.l, self.nt, self.np, true)?,
            initial_a: a,
        };
        let m = self.matter(&t)?;
        t.geometry.h = ((m.rho + OL) / (1. - s.iter().map(|v| v * v).sum::<f64>() / 6.)).sqrt();
        Ok(t)
    }
    pub fn matter(&self, t: &ThomsonState) -> Result<Matter, String> {
        let mut m = self
            .model
            .matter_without_photons(t.geometry.a, &t.geometry.f)?;
        let p = t.sky.moments()?;
        let rho = OG / t.initial_a.powi(4) * p.energy / (4. * std::f64::consts::PI);
        if p.flux.iter().any(|x| x.abs() > 1e-10) {
            return Err("nonzero Codazzi photon flux".into());
        }
        m.rho += rho;
        m.photon_rho = rho;
        m.pressure += rho * Matrix3::from_fn(|i, j| p.pressure[i][j]);
        Ok(m)
    }
    pub fn constraint(&self, t: &ThomsonState) -> Result<f64, String> {
        let s = &t.geometry;
        let m = self.matter(t)?;
        Ok(1. - s.s.iter().map(|v| v * v).sum::<f64>() / 6. - (m.rho + OL) / s.h.powi(2))
    }
    fn node(s: &OwnedState, m: &Matter) -> RayNode {
        RayNode {
            shear: rows(stf_matrix(s.s)),
            hubble_ratio: s.h,
            omega_lambda: OL / s.h.powi(2),
            omega_radiation: m.photon_rho / s.h.powi(2),
            ..Default::default()
        }
    }
    fn radiation(
        old: &HarmonicSky,
        at: &RayNode,
        du: f64,
        depth: f64,
    ) -> Result<(HarmonicSky, f64), String> {
        let mut s = old.clone();
        let a = RayNode {
            eta: 0.,
            ..at.clone()
        };
        let b = RayNode {
            eta: du / 2.,
            ..a.clone()
        };
        s.stream(&a, &b)?;
        let mut rays = s.photons()?;
        let before = rays.clone();
        let e = s.moments()?.energy;
        scatter_with(&mut rays, depth, [0.; 3], CollisionScheme::Sdirk2)?;
        s.absorb_delta(&before, &rays)?;
        let err = (s.moments()?.energy / e - 1.).abs();
        if err > 5e-12 {
            return Err("elastic collision energy defect".into());
        }
        let c = RayNode {
            eta: du,
            ..a.clone()
        };
        s.stream(&b, &c)?;
        s.moments()?;
        Ok((s, err))
    }
    pub fn step(
        &self,
        t: &ThomsonState,
        du: f64,
        ne0: f64,
        nem: f64,
    ) -> Result<(ThomsonState, f64), String> {
        if !du.is_finite()
            || du <= 0.
            || du > 0.1
            || ![ne0, nem].iter().all(|x| x.is_finite() && *x >= 0.)
        {
            return Err("Thomson step domain".into());
        }
        let s = &t.geometry;
        let m = self.matter(t)?;
        let n = Self::node(s, &m);
        let mid = advance_mixture(
            &n,
            &n,
            du / 2.,
            m.rho / s.h.powi(2),
            rows(m.pressure / m.rho),
            [0.; 3],
        )?;
        let sm = stf_components(Matrix3::from_fn(|i, j| mid.shear[i][j]));
        let (sk, err0) = Self::radiation(
            &t.sky,
            &n,
            du / 2.,
            C_SIG * (ne0 + nem) / 2. / (H0 * s.h) * du / 2.,
        )?;
        let half = ThomsonState {
            geometry: OwnedState {
                a: s.a * (du / 2.).exp(),
                h: mid.hubble_ratio,
                s: sm,
                f: (stf_matrix(s.s) * (du / 2.)).exp() * s.f,
            },
            sky: sk,
            initial_a: t.initial_a,
        };
        let hm = self.matter(&half)?;
        let at = Self::node(&half.geometry, &hm);
        let out = advance_mixture(
            &n,
            &at,
            du,
            hm.rho / half.geometry.h.powi(2),
            rows(hm.pressure / hm.rho),
            [0.; 3],
        )?;
        let (sky, err) =
            Self::radiation(&t.sky, &at, du, C_SIG * nem / (H0 * half.geometry.h) * du)?;
        let next = ThomsonState {
            geometry: OwnedState {
                a: s.a * du.exp(),
                h: out.hubble_ratio,
                s: stf_components(Matrix3::from_fn(|i, j| out.shear[i][j])),
                f: (stf_matrix(sm) * du).exp() * s.f,
            },
            sky,
            initial_a: t.initial_a,
        };
        self.matter(&next)?;
        Ok((next, err.max(err0)))
    }
}

impl ThomsonOwner {
    /// Research-only UV exchange: actual H/S/F drives canonical UV rays.
    /// Gas inputs are prescribed; UV emission draws from a pressureless
    /// reservoir inside cold matter and absorption returns to it.
    pub fn step_uv(
        &self,
        t: &ThomsonState,
        uv: &super::uv_feedback::UvModel,
        us: &super::uv_feedback::UvState,
        du: f64,
        g0: super::uv_feedback::Gas,
        gq: super::uv_feedback::Gas,
        gm: super::uv_feedback::Gas,
        feedback: bool,
    ) -> Result<(ThomsonState, super::uv_feedback::UvState, f64), String> {
        if !du.is_finite() || du <= 0. || du > 0.1 {
            return Err("UV step domain".into());
        }
        let s = &t.geometry;
        let mut m = self.matter(t)?;
        if feedback {
            uv.add_matter(us, s, &mut m)?;
        }
        let n = Self::node(s, &m);
        let stage = |d: f64| {
            advance_mixture(
                &n,
                &n,
                d,
                m.rho / s.h.powi(2),
                rows(m.pressure / m.rho),
                [0.; 3],
            )
        };
        let geom = |d: f64, stage: RayNode| OwnedState {
            a: s.a * d.exp(),
            h: stage.hubble_ratio,
            s: stf_components(Matrix3::from_fn(|i, j| stage.shear[i][j])),
            f: (stf_matrix(s.s) * d).exp() * s.f,
        };
        let q = geom(du / 4., stage(du / 4.)?);
        let mg = geom(du / 2., stage(du / 2.)?);
        let (sk, er0) = Self::radiation(
            &t.sky,
            &n,
            du / 2.,
            C_SIG * (g0.ne_m3 + gm.ne_m3) / 2. / (H0 * s.h) * du / 2.,
        )?;
        let half = ThomsonState {
            geometry: mg,
            sky: sk,
            initial_a: t.initial_a,
        };
        let mut uh = us.clone();
        uv.advance(&mut uh, s, &q, &half.geometry, du / 2. / (H0 * q.h), gq)?;
        let mut hm = self.matter(&half)?;
        if feedback {
            uv.add_matter(&uh, &half.geometry, &mut hm)?;
        }
        let at = Self::node(&half.geometry, &hm);
        let out = advance_mixture(
            &n,
            &at,
            du,
            hm.rho / half.geometry.h.powi(2),
            rows(hm.pressure / hm.rho),
            [0.; 3],
        )?;
        let (sky, er) = Self::radiation(
            &t.sky,
            &at,
            du,
            C_SIG * gm.ne_m3 / (H0 * half.geometry.h) * du,
        )?;
        let next = ThomsonState {
            geometry: OwnedState {
                a: s.a * du.exp(),
                h: out.hubble_ratio,
                s: stf_components(Matrix3::from_fn(|i, j| out.shear[i][j])),
                f: (stf_matrix(half.geometry.s) * du).exp() * s.f,
            },
            sky,
            initial_a: t.initial_a,
        };
        let mut uu = us.clone();
        uv.advance(
            &mut uu,
            s,
            &half.geometry,
            &next.geometry,
            du / (H0 * half.geometry.h),
            gm,
        )?;
        Ok((next, uu, er.max(er0)))
    }
    pub fn constraint_uv(
        &self,
        t: &ThomsonState,
        uv: &super::uv_feedback::UvModel,
        us: &super::uv_feedback::UvState,
        feedback: bool,
    ) -> Result<f64, String> {
        let mut m = self.matter(t)?;
        let s = &t.geometry;
        if feedback {
            uv.add_matter(us, s, &mut m)?;
        }
        Ok(1. - s.s.iter().map(|v| v * v).sum::<f64>() / 6. - (m.rho + OL) / s.h.powi(2))
    }
}

/// External material/radiation correction in present critical energy units.
/// Negative rho is permitted only as a correction to an existing reservoir.
#[derive(Clone, Copy, Debug)]
pub struct ExternalContribution {
    pub rho: f64,
    pub pressure: [[f64; 3]; 3],
    pub photon_rho: f64,
    pub ne_m3: f64,
}
pub trait ExternalMatter {
    type State: Clone;
    fn contribution(
        &mut self,
        s: &Self::State,
        g: &OwnedState,
    ) -> Result<ExternalContribution, String>;
    fn advance(
        &mut self,
        s: &Self::State,
        old: &OwnedState,
        mid: &OwnedState,
        end: &OwnedState,
    ) -> Result<Self::State, String>;
}
impl ThomsonOwner {
    fn external_matter<X: ExternalMatter>(
        &self,
        t: &ThomsonState,
        s: &X::State,
        x: &mut X,
    ) -> Result<(Matter, f64), String> {
        let mut m = self.matter(t)?;
        let v = x.contribution(s, &t.geometry)?;
        if ![v.rho, v.photon_rho, v.ne_m3]
            .iter()
            .chain(v.pressure.iter().flatten())
            .all(|x| x.is_finite())
            || v.ne_m3 < 0.
        {
            return Err("external matter domain".into());
        }
        let p = Matrix3::from_fn(|i, j| v.pressure[i][j]);
        if (p - p.transpose()).norm() > 1e-12 * p.norm().max(1e-30) {
            return Err("external pressure symmetry".into());
        }
        m.rho += v.rho;
        m.pressure += p;
        m.photon_rho += v.photon_rho;
        if m.rho <= 0. || m.photon_rho <= 0. {
            return Err("external total density domain".into());
        }
        Ok((m, v.ne_m3))
    }
    /// Midpoint-predicted geometry plus stage-owned external matter. State is
    /// returned by value; the caller retains old state if either trial fails.
    pub fn step_external<X: ExternalMatter>(
        &self,
        t: &ThomsonState,
        xs: &X::State,
        x: &mut X,
        du: f64,
    ) -> Result<(ThomsonState, X::State, f64), String> {
        if !du.is_finite() || du <= 0. || du > 0.1 {
            return Err("external step domain".into());
        }
        let s = &t.geometry;
        let (m, ne) = self.external_matter(t, xs, x)?;
        let n = Self::node(s, &m);
        let stage = |d: f64| {
            advance_mixture(
                &n,
                &n,
                d,
                m.rho / s.h.powi(2),
                rows(m.pressure / m.rho),
                [0.; 3],
            )
        };
        let geom = |d: f64, y: RayNode| OwnedState {
            a: s.a * d.exp(),
            h: y.hubble_ratio,
            s: stf_components(Matrix3::from_fn(|i, j| y.shear[i][j])),
            f: (stf_matrix(s.s) * d).exp() * s.f,
        };
        let q = geom(du / 4., stage(du / 4.)?);
        let mg = geom(du / 2., stage(du / 2.)?);
        let (sk, e0) = Self::radiation(&t.sky, &n, du / 2., C_SIG * ne / (H0 * s.h) * du / 2.)?;
        let half = ThomsonState {
            geometry: mg,
            sky: sk,
            initial_a: t.initial_a,
        };
        let xm = x.advance(xs, s, &q, &half.geometry)?;
        let (hm, nem) = self.external_matter(&half, &xm, x)?;
        let at = Self::node(&half.geometry, &hm);
        let out = advance_mixture(
            &n,
            &at,
            du,
            hm.rho / half.geometry.h.powi(2),
            rows(hm.pressure / hm.rho),
            [0.; 3],
        )?;
        let (sky, e1) =
            Self::radiation(&t.sky, &at, du, C_SIG * nem / (H0 * half.geometry.h) * du)?;
        let next = ThomsonState {
            geometry: OwnedState {
                a: s.a * du.exp(),
                h: out.hubble_ratio,
                s: stf_components(Matrix3::from_fn(|i, j| out.shear[i][j])),
                f: (stf_matrix(half.geometry.s) * du).exp() * s.f,
            },
            sky,
            initial_a: t.initial_a,
        };
        let xn = x.advance(xs, s, &half.geometry, &next.geometry)?;
        self.external_matter(&next, &xn, x)?;
        Ok((next, xn, e0.max(e1)))
    }
    pub fn constraint_external<X: ExternalMatter>(
        &self,
        t: &ThomsonState,
        s: &X::State,
        x: &mut X,
    ) -> Result<f64, String> {
        let (m, _) = self.external_matter(t, s, x)?;
        let g = &t.geometry;
        Ok(1. - g.s.iter().map(|v| v * v).sum::<f64>() / 6. - (m.rho + OL) / g.h.powi(2))
    }
}

impl ThomsonOwner {
    /// Exact, finite accepted state in the native bolometric hierarchy convention.
    /// A separate joint manifest binds source/executable identities.
    pub fn state_text(&self, t: &ThomsonState) -> Result<String, String> {
        let g = &t.geometry;
        if !g.a.is_finite()
            || !g.h.is_finite()
            || g.a < t.initial_a
            || g.h <= 0.
            || t.initial_a <= 0.
            || !t.initial_a.is_finite()
            || !g.s.iter().chain(g.f.iter()).all(|x| x.is_finite())
            || (g.f.determinant() - 1.).abs() > 1e-7
            || t.sky.lmax() != self.l
            || t.sky.grid_size() != (self.nt, self.np)
            || !t.sky.polarized()
            || t.sky.coefficients.len() != 3
            || t.sky.coefficients.iter().any(|v| {
                v.len() != (self.l + 1).pow(2)
                    || v.iter().any(|x| !x.re.is_finite() || !x.im.is_finite())
            })
        {
            return Err("Thomson checkpoint domain".into());
        }
        self.matter(t)?;
        let v = [g.a, g.h, t.initial_a]
            .into_iter()
            .chain(g.s)
            .chain((0..3).flat_map(|i| (0..3).map(move |j| g.f[(i, j)])))
            .chain(
                t.sky
                    .coefficients
                    .iter()
                    .flatten()
                    .flat_map(|x| [x.re, x.im]),
            );
        Ok(format!(
            "BASS_THOMSON_STATE_V1\n{}\n{}\n",
            self.owner_identity,
            v.map(|x| format!("{:016x}", x.to_bits()))
                .collect::<Vec<_>>()
                .join(" ")
        ))
    }
    pub fn restore_state_text(&self, text: &str) -> Result<ThomsonState, String> {
        let l = text.lines().collect::<Vec<_>>();
        if l.len() != 3 || l[0] != "BASS_THOMSON_STATE_V1" || l[1] != self.owner_identity {
            return Err("Thomson checkpoint identity".into());
        }
        let v = l[2]
            .split_whitespace()
            .map(|s| {
                u64::from_str_radix(s, 16)
                    .map(f64::from_bits)
                    .map_err(|_| "Thomson checkpoint format".to_string())
            })
            .collect::<Result<Vec<_>, _>>()?;
        if v.len() != 17 + 6 * (self.l + 1).pow(2) || v.iter().any(|x| !x.is_finite()) {
            return Err("Thomson checkpoint shape".into());
        }
        let mut sky = HarmonicSky::isotropic(self.l, self.nt, self.np, true)?;
        for (x, p) in sky
            .coefficients
            .iter_mut()
            .flatten()
            .zip(v[17..].chunks_exact(2))
        {
            *x = super::spin_sht::C64::new(p[0], p[1]);
        }
        let t = ThomsonState {
            geometry: OwnedState {
                a: v[0],
                h: v[1],
                s: v[3..8].try_into().unwrap(),
                f: Matrix3::from_row_slice(&v[8..17]),
            },
            sky,
            initial_a: v[2],
        };
        self.state_text(&t)?;
        Ok(t)
    }
}
