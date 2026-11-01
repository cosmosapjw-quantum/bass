//! Source-backed, elemental ground-parent lithium CI/RR/DR coefficients.
//!
//! Voronov (1997) and Badnell RR/DR parameter rows are retained verbatim in
//! the research unit. This module supplies number kinetics only. It supplies
//! no isotope-resolved rates, photo donor, thermal closure, or abundances.
//! Isotope-native identities remain distinct from an explicitly selected
//! elemental electronic equality approximation; Li8/Li9 decay is unresolved.

use crate::rate_table::LogRateGrid;
use crate::ForwardError;

pub const MODEL_ID: &str = "ELEMENTAL_LI_GROUND_CI_RR_DR_V1";
/// Literal used by the official Voronov cfit.f implementation, eV/K.
pub const VORONOV_KB_EV_K: f64 = 8.617385e-5;
pub const COMMON_MIN_K: f64 = 5.0 / VORONOV_KB_EV_K;
pub const COMMON_MAX_K: f64 = 1e7;
const RR_ROWS: &str = include_str!("../../../research/flrw_rate_table_acceleration_20261016/data/badnell_lithium_rr_rows.txt");
const DR_ROWS: &str = include_str!("../../../research/flrw_rate_table_acceleration_20261016/data/badnell_lithium_dr_rows.txt");
const CI_ROWS: &str = include_str!("../../../research/flrw_rate_table_acceleration_20261016/data/voronov_lithium_ci_rows.txt");

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum IsotopeRatePolicy {
    /// These elemental tables provide no isotope-resolved coefficient source.
    IsotopeResolved,
    /// Explicit approximation: the same electronic coefficients for 6Li/7Li.
    ElementalElectronicEquality,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LithiumIsotope { Li6, Li7, Li8, Li9 }
impl LithiumIsotope {
    pub fn mass_number(self)->u16 { match self { Self::Li6=>6,Self::Li7=>7,Self::Li8=>8,Self::Li9=>9 } }
    pub fn nuclear_charge(self)->u16 { 3 }
    pub fn scope(self)->LithiumIsotopeScope { match self {Self::Li6|Self::Li7=>LithiumIsotopeScope::StableCollisionalProbe,Self::Li8|Self::Li9=>LithiumIsotopeScope::PendingNuclearDecayDaughterClosure} }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LithiumIsotopeScope { StableCollisionalProbe, PendingNuclearDecayDaughterClosure }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LithiumIonIdentity { pub isotope:LithiumIsotope, pub charge:u8 }
impl LithiumIonIdentity {
    pub fn new(isotope:LithiumIsotope,charge:u8)->Result<Self,LithiumError> {if charge>3 {Err(LithiumError::InvalidCharge)} else {Ok(Self{isotope,charge})}}
    pub fn nuclear_charge(self)->u16 {self.isotope.nuclear_charge()}
    pub fn mass_number(self)->u16 {self.isotope.mass_number()}
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LithiumError {
    MissingSource,
    PendingNuclearDecayDaughterClosure,
    InvalidCharge,
    InvalidInput,
    TemperatureDomain,
    SourceData,
    Arithmetic,
    Table,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LithiumProcess { CollisionalIonization, RadiativeRecombination, DielectronicRecombination }
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct LithiumChannelRecord {
    pub initial_charge: usize,
    pub final_charge: usize,
    pub process: LithiumProcess,
    pub minimum_k: f64,
    pub maximum_k: f64,
    pub structural_zero: bool,
    pub source: &'static str,
    pub units: &'static str,
    pub domain_description: &'static str,
}
#[derive(Clone, Debug)]
struct RrFit { a: f64, b: f64, t0: f64, t1: f64, c: f64, t2: f64 }
#[derive(Clone, Debug)]
struct DrFit { c: Vec<f64>, e: Vec<f64> }
#[derive(Clone, Debug)]
struct CiFit { energy: f64, p: f64, a: f64, x: f64, k: f64, minimum_ev: f64, maximum_kev: f64 }
#[derive(Clone, Debug)]
pub struct LithiumProvider {
    rr: [Option<RrFit>; 4],
    dr: [Option<DrFit>; 4],
    ci: [Option<CiFit>; 4],
}
fn numbers(line: &str) -> Vec<f64> {
    line.split_whitespace().filter_map(|x| x.parse::<f64>().ok()).collect()
}
fn valid_rate(value: f64) -> Result<f64, LithiumError> {
    if value.is_finite() && value >= 0.0 { Ok(value) } else { Err(LithiumError::Arithmetic) }
}
fn nonnegative(value: f64) -> Result<f64, LithiumError> {
    if value.is_finite() && value >= 0.0 { Ok(value) } else { Err(LithiumError::InvalidInput) }
}
fn checked_product(a: f64, b: f64, c: f64) -> Result<f64, LithiumError> {
    nonnegative(a)?; nonnegative(b)?; nonnegative(c)?;
    if a == 0.0 || b == 0.0 || c == 0.0 { return Ok(0.0); }
    let v = a * b * c;
    if v.is_finite() && v > 0.0 { Ok(v) } else { Err(LithiumError::Arithmetic) }
}
impl LithiumProvider {
    /// Parse the preserved primary parameter rows once; no coefficient is fit here.
    pub fn from_primary_rows() -> Result<Self, LithiumError> {
        let mut provider = Self { rr: std::array::from_fn(|_| None), dr: std::array::from_fn(|_| None), ci: std::array::from_fn(|_| None) };
        for line in RR_ROWS.lines() {
            let v = numbers(line);
            if !(v.len() == 8 || v.len() == 10) || v[0] != 3.0 || v[2] != 1.0 { return Err(LithiumError::SourceData); }
            let n = v[1] as usize;
            if n > 2 || v[1] != n as f64 { return Err(LithiumError::SourceData); }
            let q = 3 - n;
            if provider.rr[q].is_some() { return Err(LithiumError::SourceData); }
            provider.rr[q] = Some(RrFit { a:v[4], b:v[5], t0:v[6], t1:v[7], c:if v.len()==10 {v[8]} else {0.0}, t2:if v.len()==10 {v[9]} else {0.0} });
        }
        let rows: Vec<Vec<f64>> = DR_ROWS.lines().map(numbers).collect();
        if rows.len() != 4 { return Err(LithiumError::SourceData); }
        for i in 0..2 {
            let (c,e) = (&rows[i], &rows[i+2]);
            if c.len() < 5 || c.len()!=e.len() || c[..4]!=e[..4] || c[0]!=3.0 || c[2]!=1.0 { return Err(LithiumError::SourceData); }
            let n=c[1] as usize;
            if !(1..=2).contains(&n) || c[1]!=n as f64 { return Err(LithiumError::SourceData); }
            let q=3-n;
            if provider.dr[q].is_some() { return Err(LithiumError::SourceData); }
            // Individual DR amplitudes are signed source parameters, not rates.
            provider.dr[q]=Some(DrFit { c:c[4..].to_vec(), e:e[4..].to_vec() });
        }
        for line in CI_ROWS.lines() {
            let v=numbers(line);
            if v.len()!=9 || v[0]!=3.0 { return Err(LithiumError::SourceData); }
            let n=v[1] as usize;
            if !(1..=3).contains(&n) || v[1]!=n as f64 { return Err(LithiumError::SourceData); }
            let q=3-n;
            if provider.ci[q].is_some() { return Err(LithiumError::SourceData); }
            provider.ci[q]=Some(CiFit { energy:v[2], p:v[3], a:v[4], x:v[5], k:v[6], minimum_ev:v[7], maximum_kev:v[8] });
        }
        if provider.rr[1..].iter().any(Option::is_none) || provider.dr[1..3].iter().any(Option::is_none) || provider.ci[..3].iter().any(Option::is_none) { return Err(LithiumError::SourceData); }
        Ok(provider)
    }
    pub fn record(&self, process: LithiumProcess, q: usize) -> Result<LithiumChannelRecord, LithiumError> {
        use LithiumProcess::*;
        if q>3 { return Err(LithiumError::InvalidCharge); }
        let structural_zero = matches!((process,q),(CollisionalIonization,3)|(RadiativeRecombination,0)|(DielectronicRecombination,0|3));
        let (minimum_k,maximum_k,source,domain_description)=if structural_zero {
            (0.0,f64::INFINITY,"adjacent-chain structural boundary / bare-ion DR absence","structural absence for all finite T>0")
        } else if process==CollisionalIonization {
            let p=self.ci[q].as_ref().ok_or(LithiumError::SourceData)?;
            (p.minimum_ev/VORONOV_KB_EV_K,1000.0*p.maximum_kev/VORONOV_KB_EV_K,"Voronov 1997 official cfit.dat/cfit.f","per-row source Tmin(eV)..Tmax(keV)")
        } else {
            (10.0*(q*q) as f64,1e7*(q*q) as f64,if process==RadiativeRecombination {"Badnell RR 20230511 ground M=1"} else {"Badnell DR 20230512 ground M=1"},"conservative standard ADAS tabulation range; not universal fit-accuracy bound")
        };
        Ok(LithiumChannelRecord { initial_charge:q, final_charge:if process==CollisionalIonization { (q+1).min(3) } else { q.saturating_sub(1) }, process, minimum_k, maximum_k, structural_zero, source, units:"cm^3 s^-1", domain_description })
    }
    /// Each channel retains its own source domain, including cold-valid RR.
    pub fn coefficient_cm3_s(&self, process: LithiumProcess, q: usize, t: f64) -> Result<f64, LithiumError> {
        if !t.is_finite() || t<=0.0 { return Err(LithiumError::InvalidInput); }
        let record=self.record(process,q)?;
        if record.structural_zero { return Ok(0.0); }
        if t<record.minimum_k || t>record.maximum_k { return Err(LithiumError::TemperatureDomain); }
        use LithiumProcess::*;
        let rate=match process {
            CollisionalIonization => { let p=self.ci[q].as_ref().ok_or(LithiumError::SourceData)?; let u=p.energy/(VORONOV_KB_EV_K*t); p.a*(1.0+p.p*u.sqrt())/(p.x+u)*u.powf(p.k)*(-u).exp() },
            RadiativeRecombination => { let p=self.rr[q].as_ref().ok_or(LithiumError::SourceData)?; let b=p.b+p.c*(-p.t2/t).exp(); let x=(t/p.t0).sqrt(); let y=(t/p.t1).sqrt(); p.a/(x*(1.0+x).powf(1.0-b)*(1.0+y).powf(1.0+b)) },
            DielectronicRecombination => { let p=self.dr[q].as_ref().ok_or(LithiumError::SourceData)?; p.c.iter().zip(&p.e).map(|(c,e)|c*(-e/t).exp()).sum::<f64>()/t.powf(1.5) },
        };
        valid_rate(rate)
    }
    /// Complete bundle uses the intersection, without broadening any source.
    pub fn rates(&self,t:f64)->Result<LithiumRates,LithiumError> {
        if !t.is_finite() || !(COMMON_MIN_K..=COMMON_MAX_K).contains(&t) { return Err(LithiumError::TemperatureDomain); }
        let mut flat=[0.0;12];
        for (i,p) in [LithiumProcess::CollisionalIonization,LithiumProcess::RadiativeRecombination,LithiumProcess::DielectronicRecombination].iter().enumerate() {
            for q in 0..4 { flat[4*i+q]=self.coefficient_cm3_s(*p,q,t)?; }
        }
        Ok(LithiumRates::from_flat(t,flat))
    }
}
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct LithiumRates {
    pub temperature_k:f64,
    pub ci_cm3_s:[f64;4],
    pub rr_cm3_s:[f64;4],
    pub dr_cm3_s:[f64;4],
}
impl LithiumRates {
    fn from_flat(t:f64,v:[f64;12])->Self { Self {temperature_k:t,ci_cm3_s:std::array::from_fn(|q|v[q]),rr_cm3_s:std::array::from_fn(|q|v[q+4]),dr_cm3_s:std::array::from_fn(|q|v[q+8])} }
    fn flat(self)->[f64;12] { std::array::from_fn(|i|if i<4 {self.ci_cm3_s[i]} else if i<8 {self.rr_cm3_s[i-4]} else {self.dr_cm3_s[i-8]}) }
}
/// Same immutable, shared-log-temperature mechanism as the H/He provider.
pub struct LithiumRateTable { provider:LithiumProvider, grid:LogRateGrid<12> }
impl LithiumRateTable {
    pub fn build(provider:LithiumProvider,nodes:usize)->Result<Self,LithiumError> {
        let grid=LogRateGrid::build(COMMON_MIN_K,COMMON_MAX_K,nodes,|t|provider.rates(t).map(LithiumRates::flat).map_err(|_|ForwardError::InvalidInput("LITHIUM_RATE_DOMAIN")),|_,_|false,|i,_,_|matches!(i,3|4|8|11)).map_err(|_|LithiumError::Table)?;
        Ok(Self {provider,grid})
    }
    pub fn rates(&self,t:f64)->Result<LithiumRates,LithiumError> {
        if !t.is_finite() || !(COMMON_MIN_K..=COMMON_MAX_K).contains(&t) { return Err(LithiumError::TemperatureDomain); }
        let v=self.grid.evaluate(t,|t|self.provider.rates(t).map(LithiumRates::flat).map_err(|_|ForwardError::InvalidInput("LITHIUM_RATE_DOMAIN"))).map_err(|_|LithiumError::Table)?;
        Ok(LithiumRates::from_flat(t,v))
    }
    pub fn batch(&self,temperatures:&[f64])->Result<Vec<LithiumRates>,LithiumError> { temperatures.iter().map(|&t|self.rates(t)).collect() }
}
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct LithiumNumberRhs {
    pub species_m3_s:[f64;4],
    /// Supply this contribution once to the caller's global electron equation.
    pub electron_m3_s:f64,
    pub ionization_events_m3_s:[f64;4],
    pub recombination_events_m3_s:[f64;4],
}
/// Proper densities, prescribed free-electron density, and one rate bundle.
/// CI/RR/DR events own only number changes here; energy closure is absent.
pub fn lithium_number_rhs(rates:&LithiumRates,density_m3:[f64;4],electron_density_m3:f64)->Result<LithiumNumberRhs,LithiumError> {
    nonnegative(electron_density_m3)?;
    let mut ci=[0.0;4]; let mut re=[0.0;4];
    for q in 0..4 {
        nonnegative(density_m3[q])?;
        ci[q]=checked_product(electron_density_m3,density_m3[q],rates.ci_cm3_s[q]*1e-6)?;
        re[q]=checked_product(electron_density_m3,density_m3[q],(rates.rr_cm3_s[q]+rates.dr_cm3_s[q])*1e-6)?;
    }
    if ci[3]!=0.0 || re[0]!=0.0 {return Err(LithiumError::InvalidInput);}
    let mut species=[0.0;4]; let mut electrons=0.0;
    for q in 0..3 {
        let net=ci[q]-re[q+1];
        species[q]-=net; species[q+1]+=net; electrons+=net;
    }
    if !electrons.is_finite() || species.iter().any(|x|!x.is_finite()) {return Err(LithiumError::Arithmetic);}
    Ok(LithiumNumberRhs {species_m3_s:species,electron_m3_s:electrons,ionization_events_m3_s:ci,recombination_events_m3_s:re})
}

fn qualify_isotope(isotope:LithiumIsotope,policy:IsotopeRatePolicy)->Result<(),LithiumError> {
    if matches!(isotope,LithiumIsotope::Li8|LithiumIsotope::Li9) {return Err(LithiumError::PendingNuclearDecayDaughterClosure);}
    match policy {IsotopeRatePolicy::IsotopeResolved=>Err(LithiumError::MissingSource),IsotopeRatePolicy::ElementalElectronicEquality=>Ok(())}
}
/// Native (Z=3,A,q) identity; coefficients are explicitly elemental approximation.
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct LithiumIsotopeRates {
    pub isotope:LithiumIsotope,
    pub policy:IsotopeRatePolicy,
    pub electronic:LithiumRates,
    pub isotope_resolved:bool,
}
impl LithiumProvider {
    /// Mandatory policy: there is no implicit elemental-to-isotope mapping.
    pub fn isotope_rates(&self,isotope:LithiumIsotope,policy:IsotopeRatePolicy,t:f64)->Result<LithiumIsotopeRates,LithiumError> {
        qualify_isotope(isotope,policy)?;
        Ok(LithiumIsotopeRates {isotope,policy,electronic:self.rates(t)?,isotope_resolved:false})
    }
    pub fn isotope_coefficient_cm3_s(&self,isotope:LithiumIsotope,policy:IsotopeRatePolicy,process:LithiumProcess,q:usize,t:f64)->Result<f64,LithiumError> {
        qualify_isotope(isotope,policy)?;
        self.coefficient_cm3_s(process,q,t)
    }
}
impl LithiumRateTable {
    /// Both stable isotopes reuse one electronic table under the named policy.
    pub fn isotope_rates(&self,isotope:LithiumIsotope,policy:IsotopeRatePolicy,t:f64)->Result<LithiumIsotopeRates,LithiumError> {
        qualify_isotope(isotope,policy)?;
        Ok(LithiumIsotopeRates {isotope,policy,electronic:self.rates(t)?,isotope_resolved:false})
    }
}
/// Caller-supplied proper number densities: [6Li(q=0..3),7Li(q=0..3)].
/// No isotope abundance, ionic fraction or electron density is defaulted.
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct LithiumIsotopeNumberState { density_m3:[[f64;4];2] }
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct LithiumNumberMoments {
    pub isotope_nuclei_m3:[f64;2],
    pub baryon_number_m3:f64,
    pub nuclear_charge_number_m3:f64,
    pub ionic_charge_number_m3:f64,
}
impl LithiumIsotopeNumberState {
    pub fn new(li6_m3:[f64;4],li7_m3:[f64;4])->Result<Self,LithiumError> {
        for value in li6_m3.into_iter().chain(li7_m3) {nonnegative(value)?;}
        let state=Self {density_m3:[li6_m3,li7_m3]};
        state.moments()?;
        Ok(state)
    }
    pub fn densities_m3(self)->[[f64;4];2] {self.density_m3}
    pub fn density_m3(self,identity:LithiumIonIdentity)->Result<f64,LithiumError> {
        if identity.charge>3 {return Err(LithiumError::InvalidCharge);}
        let i=match identity.isotope {LithiumIsotope::Li6=>0,LithiumIsotope::Li7=>1,_=>return Err(LithiumError::PendingNuclearDecayDaughterClosure)};
        Ok(self.density_m3[i][identity.charge as usize])
    }
    pub fn moments(self)->Result<LithiumNumberMoments,LithiumError> {
        let isotope_nuclei_m3=[self.density_m3[0].iter().sum::<f64>(),self.density_m3[1].iter().sum::<f64>()];
        let baryon_number_m3=6.0*isotope_nuclei_m3[0]+7.0*isotope_nuclei_m3[1];
        let nuclear_charge_number_m3=3.0*(isotope_nuclei_m3[0]+isotope_nuclei_m3[1]);
        let ionic_charge_number_m3=self.density_m3.iter().map(|row|row.iter().enumerate().map(|(q,n)|q as f64*n).sum::<f64>()).sum::<f64>();
        if [isotope_nuclei_m3[0],isotope_nuclei_m3[1],baryon_number_m3,nuclear_charge_number_m3,ionic_charge_number_m3].iter().any(|v|!v.is_finite()) {return Err(LithiumError::Arithmetic);}
        Ok(LithiumNumberMoments {isotope_nuclei_m3,baryon_number_m3,nuclear_charge_number_m3,ionic_charge_number_m3})
    }
}
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct LithiumIsotopeNumberRhs {
    /// Registry order: 6Li q0..3, then 7Li q0..3.
    pub species_m3_s:[[f64;4];2],
    /// One combined electron source to be added once by the caller.
    pub electron_m3_s:f64,
    pub isotope_channels:[LithiumNumberRhs;2],
    pub policy:IsotopeRatePolicy,
    pub isotope_resolved_coefficients:bool,
}
/// Number-only network: isotope nuclei and A-weighted baryon number conserve.
/// A single external electron density is shared; no nuclear decay/energy model.
pub fn lithium_isotope_number_rhs(rates:&LithiumRates,state:&LithiumIsotopeNumberState,electron_density_m3:f64,policy:IsotopeRatePolicy)->Result<LithiumIsotopeNumberRhs,LithiumError> {
    qualify_isotope(LithiumIsotope::Li6,policy)?;
    qualify_isotope(LithiumIsotope::Li7,policy)?;
    let li6=lithium_number_rhs(rates,state.density_m3[0],electron_density_m3)?;
    let li7=lithium_number_rhs(rates,state.density_m3[1],electron_density_m3)?;
    let electrons=li6.electron_m3_s+li7.electron_m3_s;
    if !electrons.is_finite() {return Err(LithiumError::Arithmetic);}
    Ok(LithiumIsotopeNumberRhs {species_m3_s:[li6.species_m3_s,li7.species_m3_s],electron_m3_s:electrons,isotope_channels:[li6,li7],policy,isotope_resolved_coefficients:false})
}
