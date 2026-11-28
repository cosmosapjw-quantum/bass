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
    /// Research-only configurable collisionless memory species; original constructor unchanged.
    pub fn with_species(
        specs: &[(f64, f64, [f64; 5])],
        nr: usize,
        nt: usize,
        np: usize,
        l: usize,
        st: usize,
        sp: usize,
    ) -> Result<Self, String> {
        let model = OwnedModel::with_species(specs, nr, nt, np)?;
        HarmonicSky::isotropic(l, st, sp, true)?;
        let mut owner_identity = format!("SPECIES_V1 {nr} {nt} {np} {l} {st} {sp} {}", specs.len());
        for &(m, w, j) in specs {
            for v in [m, w].into_iter().chain(j) {
                owner_identity.push_str(&format!(" {:016x}", v.to_bits()));
            }
        }
        Ok(Self {
            model,
            l,
            nt: st,
            np: sp,
            owner_identity,
        })
    }
    pub fn with_radial_species(
        specs: &[(f64, f64, [f64; 5], [f64; 5])],
        nr: usize,
        nt: usize,
        np: usize,
        l: usize,
        st: usize,
        sp: usize,
    ) -> Result<Self, String> {
        let model = OwnedModel::with_radial_species(specs, nr, nt, np)?;
        HarmonicSky::isotropic(l, st, sp, true)?;
        let mut owner_identity = format!("RADIAL_SPECIES_V1 {nr} {nt} {np} {l} {st} {sp} {}", specs.len());
        for &(m, w, j, k) in specs {
            for v in [m, w].into_iter().chain(j).chain(k) {
                owner_identity.push_str(&format!(" {:016x}", v.to_bits()));
            }
        }
        Ok(Self {
            model,
            l,
            nt: st,
            np: sp,
            owner_identity,
        })
    }
    pub fn c4j_matter_probe(&self,t:&ThomsonState,g:&Matrix3<f64>)->Result<(),String>{
        let a=t.geometry.a;let f=&t.geometry.f;let base=self.model.matter_without_photons(a,f)?;
        let jet=self.model.c4j_matter_jet(a,f,g)?;
        for eps in [0.01,0.003,0.001]{
            let p=self.model.matter_without_photons(a,&((g*eps).exp()*f))?;
            let m=self.model.matter_without_photons(a,&((g*(-eps)).exp()*f))?;
            let r1=(p.rho-m.rho)/(2.*eps);let r2=(p.rho+m.rho-2.*base.rho)/(2.*eps*eps);
            let p1=(p.pressure-m.pressure)/(2.*eps);let p2=(p.pressure+m.pressure-2.*base.pressure)/(2.*eps*eps);
            let scale=base.rho;let ps=base.pressure.norm();
            eprintln!("C4J_MAT,{a:.17e},{eps:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",jet[0].0/scale,jet[1].0/scale,(r1-jet[0].0).abs()/scale,(r2-jet[1].0).abs()/scale,jet[0].1.norm()/ps,jet[1].1.norm()/ps,(p1-jet[0].1).norm()/ps,(p2-jet[1].1).norm()/ps);
        }
        Ok(())
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

    // Research-only homogeneous Bianchi-I rest-electron closure.
    // Preserve inversion parity exactly; no O(1) pixel collision round trip.
    fn c3w_parity(s: &mut HarmonicSky) {
        use crate::kinetic::spin_sht::{index,C64};
        for l in 0..=s.lmax() {
            for m in -(l as i64)..=l as i64 {
                let k=index(l,m);
                if l%2==1 {s.coefficients[0][k]=C64::new(0.,0.);}
                if l<2 {s.coefficients[1][k]=C64::new(0.,0.);s.coefficients[2][k]=C64::new(0.,0.);}
                else if l%2==0 {
                    let e=(s.coefficients[1][k]+s.coefficients[2][k])*0.5;
                    s.coefficients[1][k]=e;s.coefficients[2][k]=e;
                } else {
                    let b=(s.coefficients[1][k]-s.coefficients[2][k])*0.5;
                    s.coefficients[1][k]=b;s.coefficients[2][k]=-b;
                }
            }
        }
    }
    fn radiation(old:&HarmonicSky,at:&RayNode,du:f64,depth:f64)->Result<(HarmonicSky,f64),String> {
        use crate::kinetic::spin_sht::index;
        if !depth.is_finite()||depth<0.{return Err("C3W depth".into())}
        let mut s=old.clone();
        let a=RayNode{eta:0.,..at.clone()};
        let b=RayNode{eta:du/2.,..a.clone()};
        s.stream(&a,&b)?;Self::c3w_parity(&mut s);
        let e0=s.coefficients[0][0];let d=(8_f64/3.).sqrt();
        let z=(-depth).exp();let t=(-0.3*depth).exp()*(-(-0.7*depth).exp_m1())/0.7;
        for l in 1..=s.lmax() {
            for m in -(l as i64)..=l as i64 {
                let k=index(l,m);
                if l==2{
                    let i=s.coefficients[0][k];let e=-(s.coefficients[1][k]+s.coefficients[2][k])*0.5;
                    let ni=z*i+t*(0.1*i+0.4/d*e);
                    let ne=z*e+t*(0.15*d*i+0.6*e);
                    s.coefficients[0][k]=ni;s.coefficients[1][k]=-ne;s.coefficients[2][k]=-ne;
                } else {for slot in &mut s.coefficients{slot[k]*=z;}}
            }
        }
        assert_eq!(s.coefficients[0][0],e0);
        let c=RayNode{eta:du,..a.clone()};s.stream(&b,&c)?;
        Self::c3w_parity(&mut s);s.moments()?;Ok((s,0.))
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

#[derive(Clone)]
pub struct C4KTangent{pub h:f64,pub s:Matrix3<f64>,pub f:Matrix3<f64>,pub sky:Vec<Vec<crate::kinetic::spin_sht::C64>>}
type C4KV=Vec<Vec<crate::kinetic::spin_sht::C64>>;
impl ThomsonOwner{
    pub fn c4k_weights(&self,specs:&[(f64,f64,[f64;5],[f64;5])],nr:usize,nt:usize,np:usize)->Result<Vec<f64>,String>{self.model.c4k_weights(specs,nr,nt,np)}
    pub fn c4k_matter_d(&self,t:&ThomsonState,d:&C4KTangent,dw:&[f64])->Result<Matter,String>{
        use crate::kinetic::spin_sht::index;
        let mut m=self.model.c4k_matter_d(t.geometry.a,&t.geometry.f,&d.f,dw)?;
        let a=&d.sky[0];let p=std::f64::consts::PI;let energy=(4.*p).sqrt()*a[0].re;
        let zz=(16.*p/45.).sqrt()*a[index(2,0)].re;let c=(8.*p/15.).sqrt();let xy=c*a[index(2,2)].re;
        let off=-c*a[index(2,2)].im;let xz=-c*a[index(2,1)].re;let yz=c*a[index(2,1)].im;
        let pressure=Matrix3::new(energy/3.-zz/2.+xy,off,xz,off,energy/3.-zz/2.-xy,yz,xz,yz,energy/3.+zz);
        let scale=OG/t.initial_a.powi(4)/(4.*p);m.rho+=scale*energy;m.photon_rho=scale*energy;m.pressure+=scale*pressure;Ok(m)
    }
    pub fn c4k_initial_d(&self,t:&ThomsonState,dw:&[f64])->Result<C4KTangent,String>{
        let mut d=C4KTangent{h:0.,s:stf_matrix(t.geometry.s),f:Matrix3::zeros(),sky:t.sky.coefficients.iter().map(|v|vec![crate::kinetic::spin_sht::C64::new(0.,0.);v.len()]).collect()};
        let m=self.matter(t)?;let dm=self.c4k_matter_d(t,&d,dw)?;let s=stf_matrix(t.geometry.s);let den=1.-s.norm_squared()/6.;
        d.h=t.geometry.h*0.5*(dm.rho/(m.rho+OL)+s.dot(&d.s)/(3.*den));Ok(d)
    }
    pub fn c4k_constraint_d(&self,t:&ThomsonState,d:&C4KTangent,dw:&[f64])->Result<f64,String>{
        let m=self.matter(t)?;let dm=self.c4k_matter_d(t,d,dw)?;let h=t.geometry.h;
        Ok(-stf_matrix(t.geometry.s).dot(&d.s)/3.-dm.rho/h.powi(2)+2.*(m.rho+OL)*d.h/h.powi(3))
    }
    pub fn c4k_weight_only(&self,t:&ThomsonState,dw:&[f64])->Result<Matter,String>{self.model.c4k_matter_d(t.geometry.a,&t.geometry.f,&Matrix3::zeros(),dw)}
    pub fn c4k_fixed_matter(&self,a:f64,f:&Matrix3<f64>)->Result<Matter,String>{self.model.matter_without_photons(a,f)}
    fn c4k_geom_d(old:&ThomsonState,dold:&C4KTangent,at:&ThomsonState,dat:&C4KTangent,m:&Matter,dm:&Matter,dt:f64,hnew:f64)->(f64,Matrix3<f64>){
        let s=stf_matrix(at.geometry.s);let h=at.geometry.h;let a=m.rho+m.pressure.trace()-2.*OL;
        let q=s.norm_squared()/3.+a/(2.*h*h);
        let dq=2.*s.dot(&dat.s)/3.+(dm.rho+dm.pressure.trace())/(2.*h*h)-a*dat.h/h.powi(3);
        let p=dm.pressure/h.powi(2)-2.*m.pressure*dat.h/h.powi(3);
        let ds=(q-2.)*dat.s+dq*s+3.*(p-Matrix3::identity()*p.trace()/3.);
        (hnew*(dold.h/old.geometry.h-dt*dq),dold.s+dt*ds)
    }
    fn c4k_f_d(s:&Matrix3<f64>,ds:&Matrix3<f64>,f:&Matrix3<f64>,df:&Matrix3<f64>,dt:f64)->Matrix3<f64>{
        let x=s*dt;let dx=ds*dt;let mut a=Matrix3::<f64>::identity();let mut da=Matrix3::<f64>::zeros();let mut de=Matrix3::<f64>::zeros();
        for k in 1..=18{da=(da*x+a*dx)/(k as f64);a=a*x/(k as f64);de+=da;}
        x.exp()*df+de*f
    }
    fn c4k_stream_d(h:&crate::kinetic::lie_hierarchy::LieHierarchy,y:&C4KV,dy:&C4KV,s:&Matrix3<f64>,ds:&Matrix3<f64>,dt:f64)->C4KV{
        use crate::geom::lie::{LieData,photon_potentials};
        let p=photon_potentials(&LieData{shear:rows(*s),..Default::default()});let dp=photon_potentials(&LieData{shear:rows(*ds),..Default::default()});
        assert!(dt.abs()*(h.lmax as f64+2.+h.carrier)*s.norm()<0.49);
        let ax=|a:&C4KV,b:&C4KV,c:f64|->C4KV{a.iter().zip(b).map(|(v,w)|v.iter().zip(w).map(|(x,z)|*x+c*z).collect()).collect()};
        let rhs=|a:&C4KV,b:&C4KV|->(C4KV,C4KV){let mut f=h.zero_state();let mut g=h.zero_state();let mut z=h.zero_state();h.rhs(&p,a,&mut f);h.rhs(&p,b,&mut g);h.rhs(&dp,a,&mut z);(f,ax(&g,&z,1.))};
        let (k1,d1)=rhs(y,dy);let (k2,d2)=rhs(&ax(y,&k1,dt/2.),&ax(dy,&d1,dt/2.));let(k3,d3)=rhs(&ax(y,&k2,dt/2.),&ax(dy,&d2,dt/2.));let(_,d4)=rhs(&ax(y,&k3,dt),&ax(dy,&d3,dt));
        let decay=(-h.carrier*dt).exp();dy.iter().zip(&d1).zip(&d2).zip(&d3).zip(&d4).map(|((((a,b),c),d),e)|a.iter().zip(b).zip(c).zip(d).zip(e).map(|((((x,k1),k2),k3),k4)|(*x+(*k1+(*k2+*k3)*2.+*k4)*(dt/6.))*decay).collect()).collect()
    }
    fn c4k_radiation(old:&HarmonicSky,dy:&C4KV,at:&RayNode,ds:&Matrix3<f64>,du:f64,depth:f64,ddepth:f64,h:&crate::kinetic::lie_hierarchy::LieHierarchy)->Result<(HarmonicSky,C4KV),String>{
        use crate::kinetic::spin_sht::index;
        let mut s=old.clone();let mut d=old.clone();let sig=Matrix3::from_fn(|i,j|at.shear[i][j]);
        d.coefficients=Self::c4k_stream_d(h,&old.coefficients,dy,&sig,ds,du/2.);
        let a=RayNode{eta:0.,..at.clone()};let b=RayNode{eta:du/2.,..a.clone()};
        s.stream(&a,&b)?;Self::c3w_parity(&mut s);Self::c3w_parity(&mut d);
        let z=(-depth).exp();let t=(-0.3*depth).exp()*(-(-0.7*depth).exp_m1())/0.7;let dz=-z*ddepth;let dt=(z-0.3*t)*ddepth;let c=(8_f64/3.).sqrt();
        for l in 1..=s.lmax(){for m in -(l as i64)..=l as i64{let k=index(l,m);
            if l==2{
                let i=s.coefficients[0][k];let e=-(s.coefficients[1][k]+s.coefficients[2][k])*0.5;
                let di=d.coefficients[0][k];let de=-(d.coefficients[1][k]+d.coefficients[2][k])*0.5;
                let ni=z*i+t*(0.1*i+0.4/c*e);let ne=z*e+t*(0.15*c*i+0.6*e);
                let ndi=z*di+t*(0.1*di+0.4/c*de)+dz*i+dt*(0.1*i+0.4/c*e);
                let nde=z*de+t*(0.15*c*di+0.6*de)+dz*e+dt*(0.15*c*i+0.6*e);
                s.coefficients[0][k]=ni;s.coefficients[1][k]=-ne;s.coefficients[2][k]=-ne;
                d.coefficients[0][k]=ndi;d.coefficients[1][k]=-nde;d.coefficients[2][k]=-nde;
            }else{for j in 0..s.coefficients.len(){d.coefficients[j][k]=z*d.coefficients[j][k]+dz*s.coefficients[j][k];s.coefficients[j][k]*=z;}}
        }}
        d.coefficients=Self::c4k_stream_d(h,&s.coefficients,&d.coefficients,&sig,ds,du/2.);
        let c=RayNode{eta:du,..a.clone()};s.stream(&b,&c)?;Self::c3w_parity(&mut s);Self::c3w_parity(&mut d);s.moments()?;
        Ok((s,d.coefficients))
    }
    pub fn c4k_step(&self,t:&ThomsonState,d:&C4KTangent,dw:&[f64],h:&crate::kinetic::lie_hierarchy::LieHierarchy,du:f64,ne0:f64,nem:f64)->Result<(ThomsonState,C4KTangent),String>{
        let s=&t.geometry;let m=self.matter(t)?;let dm=self.c4k_matter_d(t,d,dw)?;let n=Self::node(s,&m);
        let mid=advance_mixture(&n,&n,du/2.,m.rho/s.h.powi(2),rows(m.pressure/m.rho),[0.;3])?;
        let sm=stf_components(Matrix3::from_fn(|i,j|mid.shear[i][j]));
        let depth=C_SIG*(ne0+nem)/2./(H0*s.h)*du/2.;
        let (sk,dsk)=Self::c4k_radiation(&t.sky,&d.sky,&n,&d.s,du/2.,depth,-depth*d.h/s.h,h)?;
        let half=ThomsonState{geometry:OwnedState{a:s.a*(du/2.).exp(),h:mid.hubble_ratio,s:sm,f:(stf_matrix(s.s)*(du/2.)).exp()*s.f},sky:sk,initial_a:t.initial_a};
        let(dh,ds)=Self::c4k_geom_d(t,d,t,d,&m,&dm,du/2.,mid.hubble_ratio);
        let hd=C4KTangent{h:dh,s:ds,f:Self::c4k_f_d(&stf_matrix(s.s),&d.s,&s.f,&d.f,du/2.),sky:dsk};
        let hm=self.matter(&half)?;let dhm=self.c4k_matter_d(&half,&hd,dw)?;let at=Self::node(&half.geometry,&hm);
        let out=advance_mixture(&n,&at,du,hm.rho/half.geometry.h.powi(2),rows(hm.pressure/hm.rho),[0.;3])?;
        let depth=C_SIG*nem/(H0*half.geometry.h)*du;
        let(sky,dsky)=Self::c4k_radiation(&t.sky,&d.sky,&at,&hd.s,du,depth,-depth*hd.h/half.geometry.h,h)?;
        let next=ThomsonState{geometry:OwnedState{a:s.a*du.exp(),h:out.hubble_ratio,s:stf_components(Matrix3::from_fn(|i,j|out.shear[i][j])),f:(stf_matrix(sm)*du).exp()*s.f},sky,initial_a:t.initial_a};
        let(dh,ds)=Self::c4k_geom_d(t,d,&half,&hd,&hm,&dhm,du,out.hubble_ratio);
        let nd=C4KTangent{h:dh,s:stf_matrix(stf_components(ds)),f:Self::c4k_f_d(&stf_matrix(sm),&hd.s,&s.f,&d.f,du),sky:dsky};
        self.matter(&next)?;Ok((next,nd))
    }
}
