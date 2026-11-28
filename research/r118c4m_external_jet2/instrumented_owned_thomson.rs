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

impl ThomsonOwner {
    pub fn c4l_weights2(&self,specs:&[(f64,f64,[f64;5],[f64;5])],nr:usize,nt:usize,np:usize)->Result<Vec<f64>,String>{self.model.c4l_weights2(specs,nr,nt,np)}
    pub fn c4l_matter2(&self,t:&ThomsonState,d1:&C4KTangent,d2:&C4KTangent,w1:&[f64],w2:&[f64])->Result<Matter,String>{
        use crate::kinetic::spin_sht::index;
        let mut m=self.model.c4l_matter2(t.geometry.a,&t.geometry.f,&d1.f,&d2.f,w1,w2)?;
        let a=&d2.sky[0];let p=std::f64::consts::PI;let energy=(4.*p).sqrt()*a[0].re;
        let zz=(16.*p/45.).sqrt()*a[index(2,0)].re;let c=(8.*p/15.).sqrt();let xy=c*a[index(2,2)].re;
        let off=-c*a[index(2,2)].im;let xz=-c*a[index(2,1)].re;let yz=c*a[index(2,1)].im;
        let pressure=Matrix3::new(energy/3.-zz/2.+xy,off,xz,off,energy/3.-zz/2.-xy,yz,xz,yz,energy/3.+zz);
        let scale=OG/t.initial_a.powi(4)/(4.*p);m.rho+=scale*energy;m.photon_rho=scale*energy;m.pressure+=scale*pressure;Ok(m)
    }
    pub fn c4l_initial2(&self,t:&ThomsonState,d1:&C4KTangent,w1:&[f64],w2:&[f64])->Result<C4KTangent,String>{
        let mut d2=C4KTangent{h:0.,s:Matrix3::zeros(),f:Matrix3::zeros(),sky:t.sky.coefficients.iter().map(|v|vec![crate::kinetic::spin_sht::C64::new(0.,0.);v.len()]).collect()};
        let m=self.matter(t)?;let m1=self.c4k_matter_d(t,d1,w1)?;let m2=self.c4l_matter2(t,d1,&d2,w1,w2)?;
        let s=stf_matrix(t.geometry.s);let den=1.-s.norm_squared()/6.;
        let a=s.dot(&d1.s)/(3.*den);let b=(d1.s.norm_squared()+2.*s.dot(&d2.s))/(6.*den);
        let r1=m1.rho/(m.rho+OL)+a;let r2=m2.rho/(m.rho+OL)+a*m1.rho/(m.rho+OL)+a*a+b;
        d2.h=t.geometry.h*(0.5*r2-0.125*r1*r1);Ok(d2)
    }
    pub fn c4l_constraint2(&self,t:&ThomsonState,d1:&C4KTangent,d2:&C4KTangent,w1:&[f64],w2:&[f64])->Result<f64,String>{
        let m=self.matter(t)?;let m1=self.c4k_matter_d(t,d1,w1)?;let m2=self.c4l_matter2(t,d1,d2,w1,w2)?;let h=t.geometry.h;let x=d1.h/h;let y=d2.h/h;
        Ok(-(d1.s.norm_squared()+2.*stf_matrix(t.geometry.s).dot(&d2.s))/6.-(m2.rho-2.*x*m1.rho+(3.*x*x-2.*y)*(m.rho+OL))/h.powi(2))
    }
    fn c4l_geom2(old:&ThomsonState,o1:&C4KTangent,o2:&C4KTangent,at:&ThomsonState,d1:&C4KTangent,d2:&C4KTangent,m:&Matter,m1:&Matter,m2:&Matter,dt:f64,hnew:f64)->(f64,Matrix3<f64>){
        let s=stf_matrix(at.geometry.s);let h=at.geometry.h;let x=d1.h/h;let y=d2.h/h;let r=3.*x*x-2.*y;
        let a=m.rho+m.pressure.trace()-2.*OL;let b=m1.rho+m1.pressure.trace();let c=m2.rho+m2.pressure.trace();
        let q=s.norm_squared()/3.+a/(2.*h*h);
        let q1=2.*s.dot(&d1.s)/3.+(b-2.*x*a)/(2.*h*h);
        let q2=(d1.s.norm_squared()+2.*s.dot(&d2.s))/3.+(c-2.*x*b+r*a)/(2.*h*h);
        let p=(m2.pressure-2.*x*m1.pressure+r*m.pressure)/h.powi(2);
        let ds=(q-2.)*d2.s+q1*d1.s+q2*s+3.*(p-Matrix3::identity()*p.trace()/3.);
        let dh=hnew*(o2.h/old.geometry.h-dt*q2+0.5*(dt*q1).powi(2)-dt*q1*o1.h/old.geometry.h);
        (dh,o2.s+dt*ds)
    }
    fn c4l_f2(s:&Matrix3<f64>,s1:&Matrix3<f64>,s2:&Matrix3<f64>,f:&Matrix3<f64>,f1:&Matrix3<f64>,f2:&Matrix3<f64>,dt:f64)->Matrix3<f64>{
        let x=s*dt;let x1=s1*dt;let x2=s2*dt;let mut a=Matrix3::<f64>::identity();let mut b=Matrix3::<f64>::zeros();let mut c=b;let mut e1=b;let mut e2=b;
        for k in 1..=18{let z=k as f64;c=(c*x+b*x1+a*x2)/z;b=(b*x+a*x1)/z;a=a*x/z;e1+=b;e2+=c;}
        x.exp()*f2+e1*f1+e2*f
    }
    fn c4l_stream2(h:&crate::kinetic::lie_hierarchy::LieHierarchy,y:&C4KV,y1:&C4KV,y2:&C4KV,s:&Matrix3<f64>,s1:&Matrix3<f64>,s2:&Matrix3<f64>,dt:f64)->C4KV{
        use crate::geom::lie::{LieData,photon_potentials};
        let pot=|s:Matrix3<f64>|photon_potentials(&LieData{shear:rows(s),..Default::default()});
        let p=pot(*s);let p1=pot(*s1);let p2=pot(*s2);
        assert!(dt.abs()*(h.lmax as f64+2.+h.carrier)*s.norm()<0.49);
        let ax=|a:&C4KV,b:&C4KV,c:f64|->C4KV{a.iter().zip(b).map(|(v,w)|v.iter().zip(w).map(|(x,z)|*x+c*z).collect()).collect()};
        let base=[y.clone(),y1.clone(),y2.clone()];
        let rhs=|a:&[C4KV;3]|-> [C4KV;3]{
            let mut f=h.zero_state();let mut g=h.zero_state();let mut r=h.zero_state();let mut z=h.zero_state();let mut v=h.zero_state();
            h.rhs(&p,&a[0],&mut f);h.rhs(&p,&a[1],&mut g);h.rhs(&p1,&a[0],&mut z);g=ax(&g,&z,1.);
            h.rhs(&p,&a[2],&mut r);h.rhs(&p1,&a[1],&mut z);h.rhs(&p2,&a[0],&mut v);r=ax(&ax(&r,&z,1.),&v,1.);
            [f,g,r]
        };
        let stage=|k:&[C4KV;3],v:f64|std::array::from_fn(|j|ax(&base[j],&k[j],v));
        let k1=rhs(&base);let k2=rhs(&stage(&k1,dt/2.));let k3=rhs(&stage(&k2,dt/2.));let k4=rhs(&stage(&k3,dt));
        let decay=(-h.carrier*dt).exp();
        y2.iter().zip(&k1[2]).zip(&k2[2]).zip(&k3[2]).zip(&k4[2]).map(|((((a,b),c),d),e)|a.iter().zip(b).zip(c).zip(d).zip(e).map(|((((x,k1),k2),k3),k4)|(*x+(*k1+(*k2+*k3)*2.+*k4)*(dt/6.))*decay).collect()).collect()
    }
    fn c4l_radiation(old:&HarmonicSky,y1:&C4KV,y2:&C4KV,at:&RayNode,s1:&Matrix3<f64>,s2:&Matrix3<f64>,du:f64,depth:[f64;3],h:&crate::kinetic::lie_hierarchy::LieHierarchy)->Result<(HarmonicSky,C4KV,C4KV),String>{
        use crate::kinetic::spin_sht::index;
        let sig=Matrix3::from_fn(|i,j|at.shear[i][j]);
        let mut s=old.clone();let mut d=old.clone();let mut b=old.clone();
        d.coefficients=Self::c4k_stream_d(h,&old.coefficients,y1,&sig,s1,du/2.);
        b.coefficients=Self::c4l_stream2(h,&old.coefficients,y1,y2,&sig,s1,s2,du/2.);
        let a=RayNode{eta:0.,..at.clone()};let v=RayNode{eta:du/2.,..a.clone()};
        s.stream(&a,&v)?;Self::c3w_parity(&mut s);Self::c3w_parity(&mut d);Self::c3w_parity(&mut b);
        let [x,x1,x2]=depth;
        let z=(-x).exp();let t=(-0.3*x).exp()*(-(-0.7*x).exp_m1())/0.7;let dz=-z*x1;let dt=(z-0.3*t)*x1;
        let z2=z*(0.5*x1*x1-x2);let t2=(z-0.3*t)*x2+0.5*(-z-0.3*(z-0.3*t))*x1*x1;
        let c=(8_f64/3.).sqrt();
        for l in 1..=s.lmax(){for m in -(l as i64)..=l as i64{let k=index(l,m);
            if l==2{
                let i=s.coefficients[0][k];let e=-(s.coefficients[1][k]+s.coefficients[2][k])*0.5;
                let di=d.coefficients[0][k];let de=-(d.coefficients[1][k]+d.coefficients[2][k])*0.5;
                let bi=b.coefficients[0][k];let be=-(b.coefficients[1][k]+b.coefficients[2][k])*0.5;
                let ni=z*i+t*(0.1*i+0.4/c*e);let ne=z*e+t*(0.15*c*i+0.6*e);
                let ndi=z*di+t*(0.1*di+0.4/c*de)+dz*i+dt*(0.1*i+0.4/c*e);
                let nde=z*de+t*(0.15*c*di+0.6*de)+dz*e+dt*(0.15*c*i+0.6*e);
                let nbi=z*bi+t*(0.1*bi+0.4/c*be)+dz*di+dt*(0.1*di+0.4/c*de)+z2*i+t2*(0.1*i+0.4/c*e);
                let nbe=z*be+t*(0.15*c*bi+0.6*be)+dz*de+dt*(0.15*c*di+0.6*de)+z2*e+t2*(0.15*c*i+0.6*e);
                s.coefficients[0][k]=ni;s.coefficients[1][k]=-ne;s.coefficients[2][k]=-ne;
                d.coefficients[0][k]=ndi;d.coefficients[1][k]=-nde;d.coefficients[2][k]=-nde;
                b.coefficients[0][k]=nbi;b.coefficients[1][k]=-nbe;b.coefficients[2][k]=-nbe;
            }else{for j in 0..s.coefficients.len(){b.coefficients[j][k]=z*b.coefficients[j][k]+dz*d.coefficients[j][k]+z2*s.coefficients[j][k];d.coefficients[j][k]=z*d.coefficients[j][k]+dz*s.coefficients[j][k];s.coefficients[j][k]*=z;}}
        }}
        b.coefficients=Self::c4l_stream2(h,&s.coefficients,&d.coefficients,&b.coefficients,&sig,s1,s2,du/2.);
        d.coefficients=Self::c4k_stream_d(h,&s.coefficients,&d.coefficients,&sig,s1,du/2.);
        let c=RayNode{eta:du,..a.clone()};s.stream(&v,&c)?;Self::c3w_parity(&mut s);Self::c3w_parity(&mut d);Self::c3w_parity(&mut b);s.moments()?;
        Ok((s,d.coefficients,b.coefficients))
    }
    pub fn c4l_step(&self,t:&ThomsonState,d:&C4KTangent,b:&C4KTangent,w1:&[f64],w2:&[f64],h:&crate::kinetic::lie_hierarchy::LieHierarchy,du:f64,ne0:f64,nem:f64)->Result<(ThomsonState,C4KTangent,C4KTangent),String>{
        let s=&t.geometry;let m=self.matter(t)?;let dm=self.c4k_matter_d(t,d,w1)?;let bm=self.c4l_matter2(t,d,b,w1,w2)?;let n=Self::node(s,&m);
        let mid=advance_mixture(&n,&n,du/2.,m.rho/s.h.powi(2),rows(m.pressure/m.rho),[0.;3])?;
        let sm=stf_components(Matrix3::from_fn(|i,j|mid.shear[i][j]));let dep=|x:f64,h:f64,d:f64,b:f64|[x,-x*d/h,x*((d/h).powi(2)-b/h)];
        let depth=dep(C_SIG*(ne0+nem)/2./(H0*s.h)*du/2.,s.h,d.h,b.h);
        let (sk,dsk,bsk)=Self::c4l_radiation(&t.sky,&d.sky,&b.sky,&n,&d.s,&b.s,du/2.,depth,h)?;
        let half=ThomsonState{geometry:OwnedState{a:s.a*(du/2.).exp(),h:mid.hubble_ratio,s:sm,f:(stf_matrix(s.s)*(du/2.)).exp()*s.f},sky:sk,initial_a:t.initial_a};
        let(dh,ds)=Self::c4k_geom_d(t,d,t,d,&m,&dm,du/2.,mid.hubble_ratio);
        let(bh,bs)=Self::c4l_geom2(t,d,b,t,d,b,&m,&dm,&bm,du/2.,mid.hubble_ratio);
        let hd=C4KTangent{h:dh,s:ds,f:Self::c4k_f_d(&stf_matrix(s.s),&d.s,&s.f,&d.f,du/2.),sky:dsk};
        let hb=C4KTangent{h:bh,s:bs,f:Self::c4l_f2(&stf_matrix(s.s),&d.s,&b.s,&s.f,&d.f,&b.f,du/2.),sky:bsk};
        let hm=self.matter(&half)?;let dhm=self.c4k_matter_d(&half,&hd,w1)?;let bhm=self.c4l_matter2(&half,&hd,&hb,w1,w2)?;let at=Self::node(&half.geometry,&hm);
        let out=advance_mixture(&n,&at,du,hm.rho/half.geometry.h.powi(2),rows(hm.pressure/hm.rho),[0.;3])?;
        let depth=dep(C_SIG*nem/(H0*half.geometry.h)*du,half.geometry.h,hd.h,hb.h);
        let(sky,dsky,bsky)=Self::c4l_radiation(&t.sky,&d.sky,&b.sky,&at,&hd.s,&hb.s,du,depth,h)?;
        let next=ThomsonState{geometry:OwnedState{a:s.a*du.exp(),h:out.hubble_ratio,s:stf_components(Matrix3::from_fn(|i,j|out.shear[i][j])),f:(stf_matrix(sm)*du).exp()*s.f},sky,initial_a:t.initial_a};
        let(dh,ds)=Self::c4k_geom_d(t,d,&half,&hd,&hm,&dhm,du,out.hubble_ratio);
        let(bh,bs)=Self::c4l_geom2(t,d,b,&half,&hd,&hb,&hm,&dhm,&bhm,du,out.hubble_ratio);
        let nd=C4KTangent{h:dh,s:stf_matrix(stf_components(ds)),f:Self::c4k_f_d(&stf_matrix(sm),&hd.s,&s.f,&d.f,du),sky:dsky};
        let nb=C4KTangent{h:bh,s:stf_matrix(stf_components(bs)),f:Self::c4l_f2(&stf_matrix(sm),&hd.s,&hb.s,&s.f,&d.f,&b.f,du),sky:bsky};
        self.matter(&next)?;Ok((next,nd,nb))
    }
}

// C4M: independently conserved massive canonical beam pairs and prescribed opacity family.
pub struct C4MExternal{pub clock:Vec<Vec<f64>>,pub scale:f64,pub a0:f64,pub weight:f64,pub mass:f64}
impl C4MExternal{
    fn ne(&self,a:f64)->f64{
        let u=(a/self.a0).ln();let x=&self.clock;let i=x.partition_point(|r|r[0]<=u);
        self.scale*if i==0{x[0][1]}else if i==x.len(){x[i-1][1]}else{let (p,q)=(&x[i-1],&x[i]);p[1]+(q[1]-p[1])*(u-p[0])/(q[0]-p[0])}
    }
    fn moments(&self,g:&OwnedState,d:Option<(&Matrix3<f64>,&Matrix3<f64>)>)->Result<[Matter;3],String>{
        use nalgebra::Vector3;
        let f=g.f.try_inverse().ok_or("beam inverse")?.transpose();
        let z=Matrix3::zeros();let (f1,f2)=d.unwrap_or((&z,&z));let g1=-(f*f1.transpose());let g2=-(f*f2.transpose());
        let mut r=[0.;3];let mut p=[Matrix3::zeros();3];let w=self.weight*self.scale/3./g.a.powi(4);
        for i in 0..3{
            let mut q=Vector3::zeros();q[i]=1.;
            let v=f*q;let v1=g1*v;let v2=g2*v+g1*v1;
            let e=v.norm().hypot(g.a*self.mass);let e1=v.dot(&v1)/e;let e2=(v1.norm_squared()+2.*v.dot(&v2)-e1*e1)/(2.*e);
            let vv=v*v.transpose();let q1=v1*v.transpose()+v*v1.transpose();let q2=v2*v.transpose()+v*v2.transpose()+v1*v1.transpose();
            let r1=-e1/e.powi(2);let r2=e1*e1/e.powi(3)-e2/e.powi(2);
            r[0]+=w*e;r[1]+=w*(e+e1);r[2]+=w*(e1+e2);
            p[0]+=w*vv/e;p[1]+=w*(q1/e+vv*(1./e+r1));p[2]+=w*(q2/e+q1*(1./e+r1)+vv*(r1+r2));
        }
        Ok(std::array::from_fn(|i|Matter{rho:r[i],pressure:p[i],photon_rho:0.}))
    }
    pub fn continuity(&self,g:&OwnedState)->Result<f64,String>{
        let ep:f64=1e-5;let s=stf_matrix(g.s);let mut a=g.clone();let mut b=g.clone();
        a.a*=ep.exp();b.a*=(-ep).exp();a.f=(s*ep).exp()*g.f;b.f=(s*(-ep)).exp()*g.f;
        let p=self.moments(&a,None)?[0].rho;let q=self.moments(&b,None)?[0].rho;let m=self.moments(g,None)?;
        Ok(((p-q)/(2.*ep)+3.*m[0].rho+m[0].pressure.trace()+s.dot(&m[0].pressure)).abs()/m[0].rho)
    }
}
impl ExternalMatter for C4MExternal{
    type State=();
    fn contribution(&mut self,_:&(),g:&OwnedState)->Result<ExternalContribution,String>{
        let m=self.moments(g,None)?;
        Ok(ExternalContribution{rho:m[0].rho,pressure:rows(m[0].pressure),photon_rho:0.,ne_m3:self.ne(g.a)})
    }
    fn advance(&mut self,_:&(),_:&OwnedState,_:&OwnedState,_:&OwnedState)->Result<(),String>{Ok(())}
}
impl ThomsonOwner{
    pub fn c4m_matter(&self,t:&ThomsonState,d:&C4KTangent,b:&C4KTangent,w1:&[f64],w2:&[f64],ext:&C4MExternal)->Result<[Matter;3],String>{
        let mut m=[self.matter(t)?,self.c4k_matter_d(t,d,w1)?,self.c4l_matter2(t,d,b,w1,w2)?];
        let ex=ext.moments(&t.geometry,Some((&d.f,&b.f)))?;
        for i in 0..3{m[i].rho+=ex[i].rho;m[i].pressure+=ex[i].pressure;}
        Ok(m)
    }
    pub fn c4m_init(&self,t:&mut ThomsonState,d:&mut C4KTangent,b:&mut C4KTangent,w1:&[f64],w2:&[f64],ext:&C4MExternal)->Result<(),String>{
        let m=self.c4m_matter(t,d,b,w1,w2,ext)?;let s=stf_matrix(t.geometry.s);
        let den=1.-s.norm_squared()/6.;let a=s.dot(&d.s)/(3.*den);let bb=(d.s.norm_squared()+2.*s.dot(&b.s))/(6.*den);
        let r1=m[1].rho/(m[0].rho+OL)+a;let r2=m[2].rho/(m[0].rho+OL)+a*m[1].rho/(m[0].rho+OL)+a*a+bb;
        t.geometry.h=((m[0].rho+OL)/den).sqrt();d.h=t.geometry.h*0.5*r1;b.h=t.geometry.h*(0.5*r2-0.125*r1*r1);Ok(())
    }
    pub fn c4m_constraint(&self,t:&ThomsonState,d:&C4KTangent,b:&C4KTangent,w1:&[f64],w2:&[f64],ext:&C4MExternal)->Result<[f64;3],String>{
        let m=self.c4m_matter(t,d,b,w1,w2,ext)?;let s=stf_matrix(t.geometry.s);let h=t.geometry.h;let x=d.h/h;let y=b.h/h;
        Ok([1.-s.norm_squared()/6.-(m[0].rho+OL)/h.powi(2),-s.dot(&d.s)/3.-(m[1].rho-2.*x*(m[0].rho+OL))/h.powi(2),-(d.s.norm_squared()+2.*s.dot(&b.s))/6.-(m[2].rho-2.*x*m[1].rho+(3.*x*x-2.*y)*(m[0].rho+OL))/h.powi(2)])
    }
    pub fn c4m_step(&self,t:&ThomsonState,d:&C4KTangent,b:&C4KTangent,w1:&[f64],w2:&[f64],h:&crate::kinetic::lie_hierarchy::LieHierarchy,du:f64,ext:&C4MExternal)->Result<(ThomsonState,C4KTangent,C4KTangent),String>{
        let s=&t.geometry;let [m,dm,bm]=self.c4m_matter(t,d,b,w1,w2,ext)?;let n=Self::node(s,&m);
        let mid=advance_mixture(&n,&n,du/2.,m.rho/s.h.powi(2),rows(m.pressure/m.rho),[0.;3])?;
        let sm=stf_components(Matrix3::from_fn(|i,j|mid.shear[i][j]));
        let dep=|x:f64,h:f64,d:f64,b:f64|[x,x*(1.-d/h),x*((d/h).powi(2)-b/h-d/h)];
        let depth=dep(C_SIG*ext.ne(s.a)/(H0*s.h)*du/2.,s.h,d.h,b.h);
        let (sk,dsk,bsk)=Self::c4l_radiation(&t.sky,&d.sky,&b.sky,&n,&d.s,&b.s,du/2.,depth,h)?;
        let half=ThomsonState{geometry:OwnedState{a:s.a*(du/2.).exp(),h:mid.hubble_ratio,s:sm,f:(stf_matrix(s.s)*(du/2.)).exp()*s.f},sky:sk,initial_a:t.initial_a};
        let(dh,ds)=Self::c4k_geom_d(t,d,t,d,&m,&dm,du/2.,mid.hubble_ratio);
        let(bh,bs)=Self::c4l_geom2(t,d,b,t,d,b,&m,&dm,&bm,du/2.,mid.hubble_ratio);
        let hd=C4KTangent{h:dh,s:ds,f:Self::c4k_f_d(&stf_matrix(s.s),&d.s,&s.f,&d.f,du/2.),sky:dsk};
        let hb=C4KTangent{h:bh,s:bs,f:Self::c4l_f2(&stf_matrix(s.s),&d.s,&b.s,&s.f,&d.f,&b.f,du/2.),sky:bsk};
        let [hm,dhm,bhm]=self.c4m_matter(&half,&hd,&hb,w1,w2,ext)?;let at=Self::node(&half.geometry,&hm);
        let out=advance_mixture(&n,&at,du,hm.rho/half.geometry.h.powi(2),rows(hm.pressure/hm.rho),[0.;3])?;
        let depth=dep(C_SIG*ext.ne(half.geometry.a)/(H0*half.geometry.h)*du,half.geometry.h,hd.h,hb.h);
        let(sky,dsky,bsky)=Self::c4l_radiation(&t.sky,&d.sky,&b.sky,&at,&hd.s,&hb.s,du,depth,h)?;
        let next=ThomsonState{geometry:OwnedState{a:s.a*du.exp(),h:out.hubble_ratio,s:stf_components(Matrix3::from_fn(|i,j|out.shear[i][j])),f:(stf_matrix(sm)*du).exp()*s.f},sky,initial_a:t.initial_a};
        let(dh,ds)=Self::c4k_geom_d(t,d,&half,&hd,&hm,&dhm,du,out.hubble_ratio);
        let(bh,bs)=Self::c4l_geom2(t,d,b,&half,&hd,&hb,&hm,&dhm,&bhm,du,out.hubble_ratio);
        let nd=C4KTangent{h:dh,s:stf_matrix(stf_components(ds)),f:Self::c4k_f_d(&stf_matrix(sm),&hd.s,&s.f,&d.f,du),sky:dsky};
        let nb=C4KTangent{h:bh,s:stf_matrix(stf_components(bs)),f:Self::c4l_f2(&stf_matrix(sm),&hd.s,&hb.s,&s.f,&d.f,&b.f,du),sky:bsky};
        self.matter(&next)?;Ok((next,nd,nb))
    }
}
