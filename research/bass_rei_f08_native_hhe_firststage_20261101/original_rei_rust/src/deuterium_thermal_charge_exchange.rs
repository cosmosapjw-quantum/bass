//! Opt-in isolated fixed-proper-volume H/D thermal CX. No driver activation.
//! One extent owns densities and binding/thermal energy. The local estimator
//! is heuristic; provider-boundary approach is neither an exact event time nor
//! a certified lower bound. Core units: cm^-3, eV cm^-3, K, seconds.
use crate::deuterium_charge_exchange::{DhEnergyDefect, DhState, Savin2002};

pub const EV_J: f64 = 1.602176634e-19;
pub const KB_EV_K: f64 = 1.380649e-23 / EV_J;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ThermalCxState {
    pub h0: f64,
    pub hp: f64,
    pub d0: f64,
    pub dp: f64,
    pub thermal_ev_cm3: f64,
}
impl ThermalCxState {
    pub fn densities(self) -> [f64; 4] { [self.h0,self.hp,self.d0,self.dp] }
}
#[derive(Clone, Copy, Debug)]
pub struct ThermalCxDefect<'a> { pub delta_chi_ev: f64, pub source: &'a str }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ThermalCxError {
    InvalidInput(&'static str), StageOutside, WorkLimit(&'static str),
    FieldFailure(&'static str),
}
pub struct ThermalCxProvider<'a> {
    pub source: &'a str,
    pub minimum_k: f64,
    pub maximum_k: f64,
    pub rates: &'a dyn Fn(f64) -> Result<(f64,f64), ThermalCxError>,
}
pub fn savin_rates_cm3(t: f64) -> Result<(f64,f64), ThermalCxError> {
    let r=Savin2002::rates(t).map_err(|_|ThermalCxError::FieldFailure("SAVIN_PROVIDER"))?;
    Ok((r.forward_m3_s*1e6,r.reverse_m3_s*1e6))
}
pub fn savin_provider() -> ThermalCxProvider<'static> {
    ThermalCxProvider {source:Savin2002::SOURCE,minimum_k:Savin2002::MINIMUM_K,
        maximum_k:Savin2002::MAXIMUM_K,rates:&savin_rates_cm3}
}
#[derive(Clone, Copy, Debug)]
pub struct ThermalCxControls {
    pub rtol: f64,
    pub atol_normalized: f64,
    pub event_atol_normalized: f64,
    pub max_attempts: usize,
    pub max_rhs_calls: usize,
    pub max_consecutive_rejections: usize,
    pub trace_rows_max: usize,
}
impl Default for ThermalCxControls {
    fn default() -> Self {
        Self {rtol:1e-7,atol_normalized:1e-11,event_atol_normalized:1e-12,
            max_attempts:20000,max_rhs_calls:200000,max_consecutive_rejections:80,
            trace_rows_max:512}
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ThermalCxStatus {
    Complete, CompleteEquilibrium, CompleteEmpty, DomainBoundaryApproach,
    WorkLimit, StepUnderflow, ArithmeticFailure, InvalidInput,
}
impl ThermalCxStatus {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Complete=>"COMPLETE",Self::CompleteEquilibrium=>"COMPLETE_EQUILIBRIUM",
            Self::CompleteEmpty=>"COMPLETE_EMPTY",Self::DomainBoundaryApproach=>"DOMAIN_BOUNDARY_APPROACH",
            Self::WorkLimit=>"WORK_LIMIT",Self::StepUnderflow=>"STEP_UNDERFLOW",
            Self::ArithmeticFailure=>"ARITHMETIC_FAILURE",Self::InvalidInput=>"INVALID_INPUT",
        }
    }
    pub fn complete(self) -> bool {
        matches!(self,Self::Complete|Self::CompleteEquilibrium|Self::CompleteEmpty)
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct ThermalCxCounts {
    pub accepted_steps: usize, pub rejected_steps: usize,
    pub attempts: usize, pub rhs_calls: usize,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ThermalCxBoundary {
    pub extent_cm3: f64, pub temperature_k: f64, pub interval_side: &'static str,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ThermalCxTraceRow {
    pub time_s: f64, pub extent_cm3: f64, pub thermal_ev_cm3: f64,
    pub temperature_k: Option<f64>,
}
#[derive(Clone, Debug)]
pub struct ThermalCxResult {
    pub status: ThermalCxStatus,
    pub full_interval_complete: bool,
    pub t_reached_s: f64,
    pub t_requested_s: Option<f64>,
    pub state: Option<ThermalCxState>,
    pub extent_cm3: Option<f64>,
    pub normalized_extent: Option<f64>,
    pub temperature_k: Option<f64>,
    pub chemical_delta_ev_cm3: Option<f64>,
    pub thermal_delta_ev_cm3: Option<f64>,
    pub electron_delta_cm3: f64,
    pub temperature_amplitude_ceiling_k: Option<f64>,
    pub physical_interval: Option<[f64;2]>,
    pub admissible_interval: Option<[f64;2]>,
    pub provider_boundary_if_approached: Option<ThermalCxBoundary>,
    pub distance_to_boundary_cm3: Option<f64>,
    pub event_atol_normalized: f64,
    pub maximum_accepted_local_error_ratio: f64,
    pub counts: ThermalCxCounts,
    pub trace: Vec<ThermalCxTraceRow>,
    pub reason: Option<String>,
    pub rate_source: String,
    pub defect_source: String,
}
fn invalid(time: f64, reason: &str) -> ThermalCxResult {
    ThermalCxResult {status:ThermalCxStatus::InvalidInput,full_interval_complete:false,
        t_reached_s:0.0,t_requested_s:time.is_finite().then_some(time),state:None,
        extent_cm3:None,normalized_extent:None,temperature_k:None,
        chemical_delta_ev_cm3:None,thermal_delta_ev_cm3:None,electron_delta_cm3:0.0,
        temperature_amplitude_ceiling_k:None,physical_interval:None,admissible_interval:None,
        provider_boundary_if_approached:None,distance_to_boundary_cm3:None,
        event_atol_normalized:0.0,maximum_accepted_local_error_ratio:0.0,
        counts:ThermalCxCounts::default(),trace:Vec::new(),reason:Some(reason.into()),
        rate_source:String::new(),defect_source:String::new()}
}
fn finite(values: &[f64]) -> bool { values.iter().all(|x|x.is_finite()) }

/// Validated algebraic reduction. Rejected candidates never replace `initial`.
pub struct ThermalCxSystem<'a> {
    initial: ThermalCxState,
    defect: ThermalCxDefect<'a>,
    provider: &'a ThermalCxProvider<'a>,
    scale: f64,
    capacity: f64,
    physical: [f64;2],
    admissible: [f64;2],
    interval: [f64;2],
    boundaries: [Option<ThermalCxBoundary>;2],
    ceiling: Option<f64>,
}
impl<'a> ThermalCxSystem<'a> {
    pub fn new(initial: ThermalCxState, defect: ThermalCxDefect<'a>,
        provider: &'a ThermalCxProvider<'a>) -> Result<Self,ThermalCxError> {
        let densities=initial.densities();
        if !finite(&densities) || !initial.thermal_ev_cm3.is_finite()
            || densities.iter().any(|x|*x<0.0) || initial.thermal_ev_cm3<0.0 {
            return Err(ThermalCxError::InvalidInput("DENSITY_OR_THERMAL"));
        }
        if !defect.delta_chi_ev.is_finite() || defect.source.is_empty()
            || provider.source.is_empty() || !finite(&[provider.minimum_k,provider.maximum_k])
            || provider.minimum_k<=0.0 || provider.minimum_k>provider.maximum_k {
            return Err(ThermalCxError::InvalidInput("DEFECT_OR_PROVIDER_METADATA"));
        }
        let [a,b,c,d]=densities;
        let scale=a.max(b).max(c).max(d);
        let nth=a+b+c+d+b+d;
        if !nth.is_finite() { return Err(ThermalCxError::InvalidInput("PARTICLE_INVENTORY")); }
        let capacity=1.5*KB_EV_K*nth;
        let physical=[-a.min(d),b.min(c)];
        let mut system=Self {initial,defect,provider,scale,capacity,physical,
            admissible:physical,interval:[0.0,0.0],boundaries:[None,None],ceiling:None};
        if scale==0.0 {
            if initial.thermal_ev_cm3!=0.0 { return Err(ThermalCxError::InvalidInput("EMPTY_WITH_THERMAL")); }
            return Ok(system);
        }
        let t0=initial.thermal_ev_cm3/capacity;
        if !t0.is_finite() || t0<provider.minimum_k || t0>provider.maximum_k {
            return Err(ThermalCxError::InvalidInput("INITIAL_TEMPERATURE_DOMAIN"));
        }
        let delta=defect.delta_chi_ev;
        let ceiling=delta.abs()*(c+d)/capacity;
        if !ceiling.is_finite() { return Err(ThermalCxError::InvalidInput("AMPLITUDE_CEILING")); }
        system.ceiling=Some(ceiling);
        if delta!=0.0 {
            let ends=[(initial.thermal_ev_cm3-capacity*provider.minimum_k)/delta,
                (initial.thermal_ev_cm3-capacity*provider.maximum_k)/delta];
            if !finite(&ends) { return Err(ThermalCxError::InvalidInput("THERMAL_INTERVAL")); }
            let thermal=[ends[0].min(ends[1]),ends[0].max(ends[1])];
            system.admissible=[physical[0].max(thermal[0]),physical[1].min(thermal[1])];
            for side in 0..2 {
                let x=system.admissible[side];
                if x==thermal[side] {
                    system.boundaries[side]=Some(ThermalCxBoundary {extent_cm3:x,
                        temperature_k:if delta*x==delta*ends[0] {provider.minimum_k} else {provider.maximum_k},
                        interval_side:if side==0 {"lower"} else {"upper"}});
                }
            }
        }
        if system.admissible[0]>0.0 || system.admissible[1]<0.0 {
            return Err(ThermalCxError::InvalidInput("INITIAL_EXTENT_DOMAIN"));
        }
        system.interval=system.admissible.map(|x|x/scale);
        if !finite(&system.interval) { return Err(ThermalCxError::InvalidInput("NORMALIZED_INTERVAL")); }
        Ok(system)
    }
    pub fn reconstruct(&self,z:f64) -> (ThermalCxState,f64,Option<f64>,f64) {
        let s=self.initial;
        let xi=self.scale*z;
        let chemical=self.defect.delta_chi_ev*xi;
        let state=ThermalCxState {h0:s.h0+xi,hp:s.hp-xi,d0:s.d0-xi,dp:s.dp+xi,
            thermal_ev_cm3:s.thermal_ev_cm3-chemical};
        let temperature=if self.scale==0.0 {None} else {Some(state.thermal_ev_cm3/self.capacity)};
        (state,xi,temperature,chemical)
    }
    pub fn check_stage(&self,z:f64) -> Result<(),ThermalCxError> {
        if !z.is_finite() {return Err(ThermalCxError::FieldFailure("NONFINITE_STAGE"));}
        if z<self.interval[0] || z>self.interval[1] {return Err(ThermalCxError::StageOutside);}
        let (s,xi,t,chemical)=self.reconstruct(z);
        let t=t.ok_or(ThermalCxError::FieldFailure("EMPTY_FIELD"))?;
        if !finite(&s.densities()) || !finite(&[xi,s.thermal_ev_cm3,t,chemical]) {
            return Err(ThermalCxError::FieldFailure("NONFINITE_RECONSTRUCTION"));
        }
        if s.densities().iter().any(|x|*x<0.0) || s.thermal_ev_cm3<0.0
            || t<self.provider.minimum_k || t>self.provider.maximum_k {
            return Err(ThermalCxError::StageOutside);
        }
        Ok(())
    }
    pub fn field(&self,z:f64) -> Result<f64,ThermalCxError> {
        self.check_stage(z)?;
        let (s,_,t,_)=self.reconstruct(z);
        let (kf,kr)=(self.provider.rates)(t.unwrap())
            .map_err(|_|ThermalCxError::FieldFailure("PROVIDER_EVALUATION"))?;
        if !finite(&[kf,kr]) || kf<0.0 || kr<0.0 {
            return Err(ThermalCxError::FieldFailure("NONFINITE_OR_NEGATIVE_RATE"));
        }
        let g=(kf*s.d0*s.hp-kr*s.dp*s.h0)/self.scale;
        if !g.is_finite() {return Err(ThermalCxError::FieldFailure("NONFINITE_FIELD"));}
        Ok(g)
    }
}

/// Both Euler states are checked before the convex endpoint; no extrapolation.
pub fn heun_step<F>(system:&ThermalCxSystem<'_>,z:f64,h:f64,rhs:&mut F)
    -> Result<f64,ThermalCxError>
where F:FnMut(f64)->Result<f64,ThermalCxError> {
    let e=z+h*rhs(z)?;
    system.check_stage(e)?;
    let v=e+h*rhs(e)?;
    system.check_stage(v)?;
    let endpoint=(z+v)/2.0;
    system.check_stage(endpoint)?;
    Ok(endpoint)
}
fn charged_rhs(system:&ThermalCxSystem<'_>,z:f64,counts:&mut ThermalCxCounts,
    controls:ThermalCxControls) -> Result<f64,ThermalCxError> {
    if counts.rhs_calls>=controls.max_rhs_calls {
        return Err(ThermalCxError::WorkLimit("RHS_CALL_CAP"));
    }
    counts.rhs_calls+=1;
    system.field(z)
}
struct Progress {
    t:f64,z:f64,maximum_ratio:f64,trace:Vec<ThermalCxTraceRow>,
    boundary:Option<ThermalCxBoundary>,counts:ThermalCxCounts,
}
enum TrialOutcome { Equilibrium, Boundary, Candidate(f64,f64,f64) }
impl Progress {
    fn trace(&mut self,system:&ThermalCxSystem<'_>,maximum:usize) {
        if self.trace.len()<maximum.min(512) {
            let (s,xi,t,_)=system.reconstruct(self.z);
            self.trace.push(ThermalCxTraceRow {time_s:self.t,extent_cm3:xi,
                thermal_ev_cm3:s.thermal_ev_cm3,temperature_k:t});
        }
    }
    fn result(self,system:&ThermalCxSystem<'_>,requested:f64,controls:ThermalCxControls,
        status:ThermalCxStatus,reason:Option<String>) -> ThermalCxResult {
        let (state,xi,temperature,chemical)=system.reconstruct(self.z);
        ThermalCxResult {status,full_interval_complete:status.complete(),t_reached_s:self.t,
            t_requested_s:Some(requested),state:Some(state),extent_cm3:Some(xi),
            normalized_extent:Some(self.z),temperature_k:temperature,
            chemical_delta_ev_cm3:Some(chemical),thermal_delta_ev_cm3:Some(-chemical),
            electron_delta_cm3:0.0,temperature_amplitude_ceiling_k:system.ceiling,
            physical_interval:Some(system.physical),admissible_interval:Some(system.admissible),
            provider_boundary_if_approached:self.boundary,
            distance_to_boundary_cm3:self.boundary.map(|b|(b.extent_cm3-xi).abs()),
            event_atol_normalized:controls.event_atol_normalized,
            maximum_accepted_local_error_ratio:self.maximum_ratio,counts:self.counts,
            trace:self.trace,reason,rate_source:system.provider.source.into(),
            defect_source:system.defect.source.into()}
    }
}
pub fn integrate(initial:ThermalCxState,defect:ThermalCxDefect<'_>,
    provider:&ThermalCxProvider<'_>,requested:f64,controls:ThermalCxControls) -> ThermalCxResult {
    if !requested.is_finite() || requested<0.0 {return invalid(requested,"REQUESTED_TIME");}
    if !finite(&[controls.rtol,controls.atol_normalized,controls.event_atol_normalized])
        || controls.rtol<0.0 || controls.atol_normalized<=0.0 || controls.event_atol_normalized<=0.0
        || controls.max_attempts==0 || controls.max_rhs_calls==0 || controls.max_consecutive_rejections==0 {
        return invalid(requested,"CONTROLS");
    }
    let system=match ThermalCxSystem::new(initial,defect,provider) {
        Ok(s)=>s,Err(e)=>return invalid(requested,&format!("{e:?}")),
    };
    let mut p=Progress {t:0.0,z:0.0,maximum_ratio:0.0,trace:Vec::new(),boundary:None,
        counts:ThermalCxCounts::default()};
    if system.scale==0.0 {
        p.t=requested;return p.result(&system,requested,controls,ThermalCxStatus::CompleteEmpty,None);
    }
    if requested==0.0 {return p.result(&system,requested,controls,ThermalCxStatus::Complete,None);}
    p.trace(&system,controls.trace_rows_max);
    let mut h=requested/16.0;
    let mut consecutive=0;
    while p.t<requested {
        if p.counts.attempts>=controls.max_attempts || consecutive>=controls.max_consecutive_rejections {
            return p.result(&system,requested,controls,ThermalCxStatus::WorkLimit,Some("ATTEMPT_OR_REJECTION_CAP".into()));
        }
        let trial=(|| -> Result<TrialOutcome,ThermalCxError> {
            let g=charged_rhs(&system,p.z,&mut p.counts,controls)?;
            if g==0.0 {return Ok(TrialOutcome::Equilibrium);}
            let side=if g>0.0 {1} else {0};
            let distance=(system.interval[side]-p.z).abs();
            if system.boundaries[side].is_some() && distance<=controls.event_atol_normalized {
                p.boundary=system.boundaries[side];
                return Ok(TrialOutcome::Boundary);
            }
            h=h.min(requested-p.t).min(0.8*distance/g.abs());
            if !h.is_finite() || h<=0.0 || p.t+h==p.t {
                return Err(ThermalCxError::WorkLimit("STEP_UNDERFLOW"));
            }
            p.counts.attempts+=1;
            let mut rhs=|z|charged_rhs(&system,z,&mut p.counts,controls);
            let coarse=heun_step(&system,p.z,h,&mut rhs)?;
            let half=heun_step(&system,p.z,h/2.0,&mut rhs)?;
            let fine=heun_step(&system,half,h/2.0,&mut rhs)?;
            let error=(fine-coarse).abs()/3.0;
            let tolerance=controls.atol_normalized+controls.rtol*p.z.abs().max(fine.abs());
            if !finite(&[fine,error,tolerance,error/tolerance]) {
                return Err(ThermalCxError::FieldFailure("LOCAL_ERROR_ARITHMETIC"));
            }
            Ok(TrialOutcome::Candidate(fine,error,tolerance))
        })();
        match trial {
            Ok(TrialOutcome::Equilibrium)=>{
                p.t=requested;return p.result(&system,requested,controls,ThermalCxStatus::CompleteEquilibrium,None);
            }
            Ok(TrialOutcome::Boundary)=>{
                return p.result(&system,requested,controls,ThermalCxStatus::DomainBoundaryApproach,None);
            }
            Ok(TrialOutcome::Candidate(fine,error,tolerance))=>{
                let factor=if error==0.0 {2.0} else {(0.9*(tolerance/error).powf(1.0/3.0)).clamp(0.2,2.0)};
                if error<=tolerance {
                    p.z=fine;p.t+=h;p.counts.accepted_steps+=1;consecutive=0;
                    p.maximum_ratio=p.maximum_ratio.max(error/tolerance);
                    p.trace(&system,controls.trace_rows_max);h*=factor;
                } else {
                    p.counts.rejected_steps+=1;consecutive+=1;h*=factor.min(0.8);
                }
            }
            Err(ThermalCxError::StageOutside)=>{
                p.counts.rejected_steps+=1;consecutive+=1;h*=0.5;
            }
            Err(ThermalCxError::WorkLimit("STEP_UNDERFLOW"))=>{
                return p.result(&system,requested,controls,ThermalCxStatus::StepUnderflow,None);
            }
            Err(e)=>{
                let status=if matches!(e,ThermalCxError::WorkLimit(_)) {ThermalCxStatus::WorkLimit}
                    else {ThermalCxStatus::ArithmeticFailure};
                return p.result(&system,requested,controls,status,Some(format!("{e:?}")));
            }
        }
    }
    p.result(&system,requested,controls,ThermalCxStatus::Complete,None)
}

#[derive(Clone, Debug)]
pub struct ThermalCxSiResult {
    pub core: ThermalCxResult,
    pub state_si: Option<DhState>,
    pub extent_m3: Option<f64>,
    pub integrated_chemical_delta_j_m3: Option<f64>,
    pub integrated_thermal_delta_j_m3: Option<f64>,
}
/// Native value adapter; input and output are proper SI, rates remain explicit.
pub fn integrate_si(initial:DhState,defect:DhEnergyDefect,provider:&ThermalCxProvider<'_>,
    requested:f64,controls:ThermalCxControls) -> ThermalCxSiResult {
    let native_values=[initial.h0_m3,initial.hp_m3,initial.d0_m3,initial.dp_m3,
        initial.thermal_j_m3,defect.delta_chi_j];
    let converted=[initial.h0_m3/1e6,initial.hp_m3/1e6,initial.d0_m3/1e6,
        initial.dp_m3/1e6,initial.thermal_j_m3/(1e6*EV_J),defect.delta_chi_j/EV_J];
    let conversion_preserves_nonzero=|a:f64,b:f64| b.is_finite()&&(a==0.0||b!=0.0);
    let mut core=if initial.totals().is_err() {
        invalid(requested,"SI_STATE_OR_INVENTORY")
    } else if !native_values.into_iter().zip(converted)
        .all(|(a,b)|conversion_preserves_nonzero(a,b)) {
        invalid(requested,"SI_INPUT_CONVERSION_NONFINITE_OR_NONZERO_LOSS")
    } else {
        integrate(ThermalCxState {h0:converted[0],hp:converted[1],d0:converted[2],
            dp:converted[3],thermal_ev_cm3:converted[4]},
            ThermalCxDefect {delta_chi_ev:converted[5],source:defect.source},
            provider,requested,controls)
    };
    let state_si=core.state.map(|s|DhState {h0_m3:s.h0*1e6,hp_m3:s.hp*1e6,
        d0_m3:s.d0*1e6,dp_m3:s.dp*1e6,thermal_j_m3:s.thermal_ev_cm3*(1e6*EV_J)});
    let extent_m3=core.extent_cm3.map(|x|x*1e6);
    let chemical=core.chemical_delta_ev_cm3.map(|x|x*(1e6*EV_J));
    let thermal=core.thermal_delta_ev_cm3.map(|x|x*(1e6*EV_J));
    let output_state_valid=match (core.state,state_si) {
        (Some(a),Some(b))=>[a.h0,a.hp,a.d0,a.dp,a.thermal_ev_cm3].into_iter()
            .zip([b.h0_m3,b.hp_m3,b.d0_m3,b.dp_m3,b.thermal_j_m3])
            .all(|(a,b)|conversion_preserves_nonzero(a,b)),
        _=>true,
    };
    let output_scalars_valid=[(core.extent_cm3,extent_m3),
        (core.chemical_delta_ev_cm3,chemical),(core.thermal_delta_ev_cm3,thermal)]
        .into_iter().all(|(a,b)|match (a,b) {
            (Some(a),Some(b))=>conversion_preserves_nonzero(a,b),_=>true,
        });
    if !output_state_valid || !output_scalars_valid {
        // Retain the accepted core state/time, but export no corrupted SI state
        // or ledger and never claim full interval completion at this interface.
        core.status=ThermalCxStatus::ArithmeticFailure;
        core.full_interval_complete=false;
        core.reason=Some("SI_OUTPUT_CONVERSION_NONFINITE_OR_NONZERO_LOSS".into());
        return ThermalCxSiResult {core,state_si:None,extent_m3:None,
            integrated_chemical_delta_j_m3:None,integrated_thermal_delta_j_m3:None};
    }
    ThermalCxSiResult {extent_m3,
        integrated_chemical_delta_j_m3:chemical,
        integrated_thermal_delta_j_m3:thermal,
        core,state_si}
}
