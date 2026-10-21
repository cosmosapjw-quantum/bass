//! S9 research client: independent Raychaudhuri + signed shear + frozen cohorts.
//!
//! Metric (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b).
//! The three evolved variables are [h,b,y], y=s/H*. Existing cohorts are immutable.
//! Every birth constructs a new bank and starts a new upstream driver/workspace.
use std::sync::Arc;
use std::time::Instant;
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use rodas5p_core::{CoreError, CoreResult, LinearMethod, LinearSolverConfig};
use rodas5p_integrators::{
    AdaptiveStepConfig, MaxStepPolicy, OdeProblem, OutputSchedule, SmallProblem,
    integrate_rodas5p_fast_small_observed,
    integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace,
};

#[allow(dead_code)]
#[path = "../../balance_p24.rs"]
mod balance_p24;

pub const ALGORITHM: &str = "BASS_S9_VIGILODE_FROZEN_COHORT_RESTART_V1";
pub const VIGILODE_SOURCE: &str = "a21d573980f66fe02891bd216153443b5352f921";
pub const SPECTRAL_OWNER: &str = "0e25846433170d0f420c4cda44a0bedbf02cd177";
pub const PROJECT_TOL: f64 = 1e-15;

fn sum(values: impl Iterator<Item = f64>) -> f64 {
    let (mut s, mut c) = (0.0_f64, 0.0_f64);
    for x in values {
        let t = s + x;
        c += if s.abs() >= x.abs() { (s - t) + x } else { (x - t) + s };
        s = t;
    }
    s + c
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Cohort {
    pub u: f64,
    pub b_birth: f64,
    pub energy_birth: f64,
    pub mu: Vec<f64>,
    pub alpha: Vec<f64>,
    pub role: String,
}

impl Cohort {
    pub fn validate(&self) -> Result<(), String> {
        if self.mu.is_empty() || self.mu.len() != self.alpha.len()
            || !self.u.is_finite() || !self.b_birth.is_finite()
            || !(self.energy_birth > 0.0 && self.energy_birth.is_finite())
            || self.mu.iter().any(|m| !m.is_finite() || m.abs() > 1.0)
            || self.alpha.iter().any(|a| !a.is_finite() || *a <= 0.0)
        { return Err("COHORT_POSITIVE_DOMAIN".into()); }
        if self.mu.iter().zip(self.mu.iter().rev()).any(|(a,b)| *a != -*b)
            || self.alpha.iter().zip(self.alpha.iter().rev()).any(|(a,b)| a != b)
        { return Err("COHORT_REFLECTION_EXACT_FAILURE".into()); }
        if (sum(self.alpha.iter().copied()) - 1.0).abs() > 3e-15 {
            return Err("COHORT_NORMALIZATION_FAILURE".into());
        }
        Ok(())
    }
    pub fn digest(&self) -> String {
        let mut h = Sha256::new();
        for x in [self.u, self.b_birth, self.energy_birth].iter().chain(&self.mu).chain(&self.alpha) {
            h.update(x.to_le_bytes());
        }
        h.update(self.role.as_bytes());
        hex::encode(h.finalize())
    }
    /// (E, Pi, dPi/db) at fixed immutable birth data.
    pub fn moments(&self, x: f64, b: f64) -> [f64; 3] {
        let d = b - self.b_birth;
        let (perp, para) = ((2.0*d).exp(), (-4.0*d).exp());
        let factor = self.energy_birth * (-4.0*(x-self.u)).exp();
        let mut terms = Vec::with_capacity(self.mu.len());
        for (&m, &w) in self.mu.iter().zip(&self.alpha) {
            let z = m*m;
            let (a, c) = (perp*(1.0-z), para*z);
            let r = (a+c).sqrt();
            let n = c - a/2.0;
            let dd = (-4.0*c-a)/r + 2.0*n*n/(r*r*r);
            terms.push([w*r, w*n/r, w*dd]);
        }
        std::array::from_fn(|i| factor*sum(terms.iter().map(|t| t[i])))
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FrozenBank {
    pub cohorts: Vec<Cohort>,
    pub donor0: f64,
    pub decay_lambda: f64,
    pub exposure: f64,
    pub cosmological_constant: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Evaluation {
    pub rhs: [f64; 3],
    pub jacobian: [[f64; 3]; 3],
    pub partial_t: [f64; 3],
    pub energy: f64,
    pub pi: f64,
    pub pi_b: f64,
    pub donor: f64,
}

impl FrozenBank {
    pub fn eval(&self, x: f64, state: [f64; 3]) -> Result<Evaluation, String> {
        let [h,b,y] = state;
        if !x.is_finite() || state.iter().any(|v| !v.is_finite()) || h <= 0.0 {
            return Err("BACKGROUND_POSITIVE_FINITE_DOMAIN".into());
        }
        let terms: Vec<_> = self.cohorts.iter().map(|c| c.moments(x,b)).collect();
        let e = sum(terms.iter().map(|m| m[0]));
        let p = sum(terms.iter().map(|m| m[1]));
        let pb = sum(terms.iter().map(|m| m[2]));
        let ed = self.donor0 * (-3.0*x-self.decay_lambda*self.exposure).exp();
        let fh = (-h*h-2.0*y*y-0.5*ed-e+self.cosmological_constant)/h;
        let rhs = [fh, y/h, -3.0*y+p/h];
        // E_b=-2 Pi; donor is analytic within a segment, not an evolved state.
        let jacobian = [
            [-2.0-fh/h, 2.0*p/h, -4.0*y/h],
            [-y/(h*h), 0.0, 1.0/h],
            [-p/(h*h), pb/h, -3.0],
        ];
        let partial_t = [(1.5*ed+4.0*e)/h, 0.0, -4.0*p/h];
        if rhs.iter().chain(jacobian.iter().flatten()).chain(&partial_t)
            .chain([e,p,pb,ed].iter()).any(|v| !v.is_finite()) {
            return Err("KERNEL_NONFINITE".into());
        }
        Ok(Evaluation {rhs, jacobian, partial_t, energy:e, pi:p, pi_b:pb, donor:ed})
    }
    pub fn jvp(&self, x: f64, state: [f64;3], direction: [f64;3]) -> Result<[f64;3],String> {
        if direction.iter().any(|v| !v.is_finite()) { return Err("JVP_DIRECTION_DOMAIN".into()); }
        let j = self.eval(x,state)?.jacobian;
        Ok(std::array::from_fn(|i| sum((0..3).map(|k| j[i][k]*direction[k]))))
    }
    pub fn digests(&self) -> Vec<String> { self.cohorts.iter().map(Cohort::digest).collect() }
}

fn core_error(e: String) -> CoreError { CoreError::InvalidInput(e) }
fn state3(v: &[f64]) -> CoreResult<[f64;3]> {
    v.try_into().map_err(|_| CoreError::Dimension("BASS state must have dimension three".into()))
}

/// A fresh OdeProblem owns a fresh immutable Arc for each segment.
pub fn ode_problem(bank: Arc<FrozenBank>) -> CoreResult<OdeProblem> {
    let (br,bj,bt) = (bank.clone(), bank.clone(), bank);
    OdeProblem::new("BASS S9 independent Raychaudhuri frozen bank",3,
        Arc::new(move |x,z,out| {
            out.copy_from_slice(&br.eval(x,state3(z)?).map_err(core_error)?.rhs); Ok(())
        }), None, None,
        Some(Arc::new(move |x,z,v,out| {
            out.copy_from_slice(&bj.jvp(x,state3(z)?,state3(v)?).map_err(core_error)?); Ok(())
        })),
        Some(Arc::new(move |x,z,out| {
            out.copy_from_slice(&bt.eval(x,state3(z)?).map_err(core_error)?.partial_t); Ok(())
        })), false, None, None)
}

/// The actual SmallProblem API is autonomous. Its fourth state is x, with x'=1.
/// The fourth Jacobian column is analytic partial_t; no clock from an oracle.
pub struct ClockProblem(pub Arc<FrozenBank>);
impl SmallProblem<4> for ClockProblem {
    fn rhs(&self, z: &[f64;4], out: &mut [f64;4]) {
        match self.0.eval(z[3], [z[0],z[1],z[2]]) {
            Ok(e) => { out[..3].copy_from_slice(&e.rhs); out[3]=1.0; },
            Err(_) => out.fill(f64::NAN),
        }
    }
    fn jacobian(&self, z: &[f64;4], out: &mut [[f64;4];4]) {
        *out = [[0.0;4];4];
        match self.0.eval(z[3], [z[0],z[1],z[2]]) {
            Ok(e) => for i in 0..3 { out[i][..3].copy_from_slice(&e.jacobian[i]); out[i][3]=e.partial_t[i]; },
            Err(_) => *out = [[f64::NAN;4];4],
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MomentCertificate {
    pub criterion: String,
    pub gate_rational: String,
    pub pass: bool,
    pub sum_alpha_exact: String,
    pub m2_exact: String,
    pub m4_exact: String,
    pub m2: f64,
    pub m4: f64,
}

/// Exact dyadic-input polynomial admission using BigRational. The unnormalized
/// sum(alpha_i P_l(mu_i)) is compared with exactly 3/10^15; no f64 proxy.
pub fn exact_moment_certificate(mu: &[f64], alpha: &[f64]) -> Result<MomentCertificate,String> {
    if mu.is_empty() || mu.len()!=alpha.len() { return Err("EXACT_MOMENT_INPUT".into()); }
    let (mut norm, mut m2, mut m4) = (BigRational::zero(),BigRational::zero(),BigRational::zero());
    let integer = |n: i64| BigRational::from_integer(BigInt::from(n));
    for (&m,&w) in mu.iter().zip(alpha) {
        if !m.is_finite() || m.abs()>1.0 || !w.is_finite() || w<=0.0 { return Err("EXACT_MOMENT_INPUT".into()); }
        let fm = BigRational::from_float(m).ok_or("EXACT_MOMENT_NONFINITE")?;
        let fw = BigRational::from_float(w).ok_or("EXACT_MOMENT_NONFINITE")?;
        let z = &fm*&fm;
        m2 += &fw*(integer(3)*&z-integer(1))/integer(2);
        m4 += &fw*(integer(35)*&z*&z-integer(30)*&z+integer(3))/integer(8);
        norm += fw;
    }
    let gate = BigRational::new(BigInt::from(3),BigInt::from(1_000_000_000_000_000_i64));
    let passed = m2.abs()<=gate && m4.abs()<=gate && (&norm-BigRational::one()).abs()<=gate;
    Ok(MomentCertificate {criterion:"Exact unnormalized binary64-input polynomial sums; normalization separate; no continuum certificate".into(),
        gate_rational:gate.to_string(), pass:passed, sum_alpha_exact:norm.to_string(),
        m2_exact:m2.to_string(),m4_exact:m4.to_string(),m2:m2.to_f64().unwrap(),m4:m4.to_f64().unwrap()})
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CoordinateGrid { pub mu0: Vec<f64>, pub prior0: Vec<f64> }

pub fn birth_support(b: f64, grid: &CoordinateGrid) -> Result<(Vec<f64>,Vec<f64>),String> {
    if grid.mu0.len()!=grid.prior0.len() || grid.mu0.len()<4 || grid.mu0.len()>512
        || grid.mu0.len()%2!=0 || !b.is_finite() || b.abs()>2.0 {
        return Err("BIRTH_COORDINATE_INPUT".into());
    }
    let mut mu=Vec::new(); let mut q=Vec::new();
    for (&m,&w) in grid.mu0.iter().zip(&grid.prior0) {
        if !m.is_finite() || m.abs()>1.0 || !w.is_finite() || w<=0.0 { return Err("BIRTH_COORDINATE_INPUT".into()); }
        let r=((2.0*b).exp()*(1.0-m*m)+(-4.0*b).exp()*m*m).sqrt();
        mu.push(m*(-2.0*b).exp()/r); q.push(w/(r*r*r));
    }
    let total=sum(q.iter().copied());
    for w in &mut q { *w/=total; }
    if mu.iter().chain(&q).any(|v| !v.is_finite()) { return Err("BIRTH_SUPPORT_NONFINITE".into()); }
    Ok((mu,q))
}

fn projected_birth(u:f64,b:f64,energy:f64,grid:&CoordinateGrid) -> Result<(Cohort,MomentCertificate,Value),String> {
    let (mu,q)=birth_support(b,grid)?;
    let p=balance_p24::project(&mu,&q,PROJECT_TOL).map_err(str::to_string)?;
    let cohort=Cohort {u,b_birth:b,energy_birth:energy,mu,alpha:p.weights,role:"new_isotropic_P24".into()};
    cohort.validate()?;
    let cert=exact_moment_certificate(&cohort.mu,&cohort.alpha)?;
    Ok((cohort,cert,json!({"owner_algorithm":balance_p24::ID,"project_tol":PROJECT_TOL,
        "multipliers":p.multipliers,"f64_residuals":p.residuals,"evaluations":p.iterations})))
}

pub fn admitted_birth(u:f64,b:f64,energy:f64,grid:&CoordinateGrid) -> Result<(Cohort,MomentCertificate,Value),String> {
    let candidate=projected_birth(u,b,energy,grid)?;
    if !candidate.1.pass { return Err("EXACT_BIRTH_MOMENT_GATE_FAILURE".into()); }
    Ok(candidate)
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Config {
    pub k:usize, pub n:usize, pub b0:f64, pub y0:f64, pub donor0:f64,
    pub old_isotropic:f64, pub old_anisotropic:f64, pub cosmological_constant:f64,
    pub decay_lambda:f64, pub birth_end:f64, pub x_end:f64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SolverConfig {
    pub arm:String, pub rtol:f64, pub atol:f64, pub initial_step:f64, pub max_step:f64,
    pub max_attempts:usize, pub linear_rtol:f64, pub linear_atol:f64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Input {
    pub schema:String, pub config:Config, pub coordinate_grid:CoordinateGrid,
    pub initial_cohorts:Vec<Cohort>, pub expected_old_digests:Vec<String>,
    pub output_times:Vec<f64>, pub solver:SolverConfig, pub provenance:Value,
}

fn validate_input(input:&Input) -> Result<(),String> {
    let c=&input.config;
    if c.k>2048 || c.n!=input.coordinate_grid.mu0.len() || c.n<4 || c.n>512 || c.n%2!=0
        || !(0.0<c.birth_end && c.birth_end<=c.x_end && c.x_end<=8.0)
        || [c.b0,c.y0,c.donor0,c.old_isotropic,c.old_anisotropic,c.cosmological_constant,c.decay_lambda].iter().any(|v| !v.is_finite())
        || [c.donor0,c.old_isotropic,c.old_anisotropic,c.cosmological_constant,c.decay_lambda].iter().any(|v| *v<0.0)
        || (c.k==0 && c.donor0*c.decay_lambda!=0.0)
    { return Err("CONFIG_DOMAIN".into()); }
    if input.solver.arm!="mf_into_ls" && input.solver.arm!="small_clock4" { return Err("SOLVER_ARM_DOMAIN".into()); }
    if input.output_times.first()!=Some(&0.0) || input.output_times.last()!=Some(&c.x_end)
        || input.output_times.iter().any(|x| !x.is_finite())
        || input.output_times.windows(2).any(|p| p[1]<=p[0]) { return Err("OUTPUT_TIME_DOMAIN".into()); }
    let mut iso=0.0; let mut aniso=0.0;
    for cohort in &input.initial_cohorts {
        cohort.validate()?;
        if cohort.u!=0.0 || cohort.b_birth!=c.b0 { return Err("INITIAL_STOCK_FRAME".into()); }
        match cohort.role.as_str() {
            "old_isotropic" => iso+=cohort.energy_birth,
            "old_physical_anisotropic" => aniso+=cohort.energy_birth,
            _ => return Err("INITIAL_STOCK_ROLE".into()),
        }
    }
    if iso!=c.old_isotropic || aniso!=c.old_anisotropic { return Err("INITIAL_STOCK_ENERGY".into()); }
    if input.initial_cohorts.iter().map(Cohort::digest).collect::<Vec<_>>()!=input.expected_old_digests {
        return Err("OLD_STOCK_DIGEST_MISMATCH".into());
    }
    Ok(())
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Observation {
    pub x:f64, pub state:[f64;3], pub e_donor:f64, pub e_radiation:f64, pub pi:f64,
    pub sigma:f64, pub c:f64, pub c_relative:f64, pub clock_error:f64,
}
fn observe(bank:&FrozenBank,x:f64,state:[f64;3],clock_error:f64) -> Result<Observation,String> {
    let e=bank.eval(x,state)?; let [h,_,y]=state;
    let c=h*h-y*y-e.donor-e.energy-bank.cosmological_constant;
    let scale=h*h+y*y+e.donor+e.energy+bank.cosmological_constant;
    Ok(Observation {x,state,e_donor:e.donor,e_radiation:e.energy,pi:e.pi,
        sigma:3.0_f64.sqrt()*y.abs()/h,c,c_relative:c.abs()/scale,clock_error})
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RunReceipt {
    pub schema:String, pub algorithm:String, pub vigilode_source:String, pub spectral_owner:String,
    pub input:Input, pub status:String, pub failure:Option<Value>,
    pub observations:Vec<Observation>, pub events:Vec<Value>, pub segments:Vec<Value>,
    pub final_cohorts:Vec<Cohort>, pub old_stock_digests:Vec<String>,
    pub pending_birth:Option<Value>, pub elapsed_seconds:f64,
}

pub fn failure_kind(error:&str) -> &'static str {
    if error.starts_with("INFEASIBLE") {"support_feasibility"}
    else if error.starts_with("FEASIBILITY_UNRESOLVED") {"support_feasibility_unresolved"}
    else if error.contains("PRECISION") {"angular_numeric_precision"}
    else if error.contains("MOMENT_GATE") {"exact_moment_admission"}
    else if error.contains("COHORT") || error.contains("STOCK") {"stock_contract"}
    else if error.starts_with("SOLVER") {"solver_failure"}
    else {"input_or_numeric_failure"}
}

pub fn run(input:Input) -> RunReceipt {
    let start=Instant::now();
    let mut receipt=RunReceipt {schema:"BASS_S9_VIGILODE_RUN_V1".into(),algorithm:ALGORITHM.into(),
        vigilode_source:VIGILODE_SOURCE.into(),spectral_owner:SPECTRAL_OWNER.into(),input:input.clone(),
        status:"incomplete".into(),failure:None,observations:vec![],events:vec![],segments:vec![],
        final_cohorts:input.initial_cohorts.clone(),old_stock_digests:input.expected_old_digests.clone(),
        pending_birth:None,elapsed_seconds:0.0};
    let result=run_inner(&input,&mut receipt);
    match result { Ok(())=>receipt.status="completed".into(), Err(e)=>{
        receipt.status="failed".into(); receipt.failure=Some(json!({"kind":failure_kind(&e),"error":e,
            "completed_segments":receipt.segments.len(),"admitted_births":receipt.events.len()}));
    }}
    receipt.elapsed_seconds=start.elapsed().as_secs_f64(); receipt
}

fn run_inner(input:&Input,receipt:&mut RunReceipt) -> Result<(),String> {
    validate_input(input)?;
    let c=&input.config; let sc=&input.solver;
    let adaptive=AdaptiveStepConfig {rtol:sc.rtol,atol:sc.atol,initial_step:sc.initial_step,
        max_step:sc.max_step,max_attempts:sc.max_attempts,max_step_policy:MaxStepPolicy::StrictRepresentedCap,
        ..Default::default()};
    adaptive.validate().map_err(|e| e.to_string())?;
    let linear=LinearSolverConfig {method:LinearMethod::Gmres,rtol:sc.linear_rtol,atol:sc.linear_atol,
        restart:8,maxiter:40,..Default::default()};
    linear.validate()?;
    let mut bank=FrozenBank {cohorts:input.initial_cohorts.clone(),donor0:c.donor0,decay_lambda:c.decay_lambda,
        exposure:0.0,cosmological_constant:c.cosmological_constant};
    let h0=(c.y0*c.y0+c.donor0+c.old_isotropic+c.old_anisotropic+c.cosmological_constant).sqrt();
    let mut state=[h0,c.b0,c.y0];
    let du=if c.k==0 {0.0} else {c.birth_end/c.k as f64};
    let births:Vec<_>=if c.donor0*c.decay_lambda==0.0 {vec![]} else {(0..c.k).map(|k| (k as f64+0.5)*c.birth_end/c.k as f64).collect()};
    let mut endpoints=births.clone(); endpoints.push(c.x_end);
    let mut begin=0.0;
    receipt.observations.push(observe(&bank,0.0,state,0.0)?);
    for (segment_index,end) in endpoints.into_iter().enumerate() {
        let before_digests=bank.digests();
        let mut times=vec![begin];
        times.extend(input.output_times.iter().copied().filter(|x| *x>begin && *x<end));
        times.push(end);
        let schedule=OutputSchedule::new(times.clone()).map_err(|e|e.to_string())?;
        let shared=Arc::new(bank.clone());
        let (observed,meta)=if sc.arm=="mf_into_ls" {
            let problem=ode_problem(shared).map_err(|e|e.to_string())?;
            let r=integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace(&problem,(begin,end),&state,&linear,&adaptive,&schedule)
                .map_err(|e|format!("SOLVER_UPSTREAM_ERROR: {e}"))?;
            let meta=json!({"driver":r.driver,"attempts":r.attempts,"accepted":r.accepted_steps,"rejected":r.rejected_steps,
                "state_reuses":r.state_reuses,"krylov_workspace":r.krylov_workspace});
            (r.observed,meta)
        } else {
            let problem=ClockProblem(shared);
            let r=integrate_rodas5p_fast_small_observed(&problem,(begin,end),&[state[0],state[1],state[2],begin],&adaptive,&schedule)
                .map_err(|e|format!("SOLVER_UPSTREAM_ERROR: {e}"))?;
            let meta=json!({"driver":r.driver,"attempts":r.attempts,"accepted":r.accepted_steps,"rejected":r.rejected_steps,
                "jacobian_reuses":r.jacobian_reuses,"clock_augmentation":true});
            (r.observed,meta)
        };
        receipt.segments.push(json!({"index":segment_index,"begin":begin,"end":end,
            "fresh_driver":true,"fresh_immutable_bank":true,"cohort_count":bank.cohorts.len(),
            "exposure":bank.exposure,"output_times":times,"success":observed.success,"message":observed.message,
            "counters":observed.counters,"internal_steps":observed.internal_steps,
            "output_clipped_steps":observed.output_clipped_steps,"solver":meta}));
        if observed.t.len()!=observed.y.len() {return Err("SOLVER_OUTPUT_SHAPE".into());}
        for (&x,z) in observed.t.iter().zip(&observed.y).skip(1) {
            if z.len()!=if sc.arm=="mf_into_ls" {3} else {4} {return Err("SOLVER_STATE_SHAPE".into());}
            let values=[z[0],z[1],z[2]];
            let clock=if z.len()==4 {z[3]-x} else {0.0};
            receipt.observations.push(observe(&bank,x,values,clock)?);
        }
        if !observed.success {return Err(format!("SOLVER_RETURNED_FAILURE: {}",observed.message));}
        if observed.t!=times || observed.t.last()!=Some(&end) {return Err("SOLVER_EXACT_OUTPUT_SCHEDULE".into());}
        let last=observed.y.last().ok_or("SOLVER_EMPTY_OUTPUT")?;
        state=[last[0],last[1],last[2]];
        if bank.digests()!=before_digests {return Err("STOCK_MUTATED_DURING_SEGMENT".into());}
        begin=end;
        if segment_index==births.len() {break;}
        let before=bank.eval(end,state)?;
        let energy=before.donor*(-(-c.decay_lambda*du).exp_m1());
        if !energy.is_finite() || energy<=0.0 {return Err("BIRTH_POSITIVE_TRANSFER".into());}
        let (mu,prior)=birth_support(state[1],&input.coordinate_grid)?;
        receipt.pending_birth=Some(json!({"u":end,"state":state,"energy_birth":energy,"mu":mu,"prior":prior}));
        let (cohort,cert,projection)=projected_birth(end,state[1],energy,&input.coordinate_grid)?;
        receipt.pending_birth=Some(json!({"u":end,"state":state,"energy_birth":energy,
            "candidate_cohort":cohort,"exact_moment_certificate":cert,"projection":projection,"admitted":false}));
        if !cert.pass {return Err("EXACT_BIRTH_MOMENT_GATE_FAILURE".into());}
        let digest=cohort.digest();
        bank.cohorts.push(cohort);
        bank.exposure=(segment_index+1) as f64*du;
        if bank.digests()[..before_digests.len()]!=before_digests {return Err("STOCK_MUTATED_AT_BIRTH".into());}
        let after=bank.eval(end,state)?;
        let jump=after.donor+after.energy-before.donor-before.energy;
        receipt.events.push(json!({"u":end,"state":state,"b_birth":state[1],"energy_birth":energy,
            "donor_before":before.donor,"donor_after":after.donor,"radiation_before":before.energy,
            "radiation_after":after.energy,"pi_before":before.pi,"pi_after":after.pi,
            "energy_jump":jump,"energy_jump_relative":jump.abs()/(before.donor+before.energy),
            "rhs_before":before.rhs,"rhs_after":after.rhs,"partial_t_before":before.partial_t,
            "partial_t_after":after.partial_t,"jacobian_before":before.jacobian,"jacobian_after":after.jacobian,
            "state_jump":[0.0,0.0,0.0],"exact_moment_certificate":cert,"projection":projection,
            "birth_rule_sha256":digest,"previous_cohort_digests_unchanged":true}));
        // The output convention at a birth is the right-hand bank, as in S8.
        let clock=receipt.observations.last().map(|o|o.clock_error).unwrap_or(0.0);
        *receipt.observations.last_mut().ok_or("SOLVER_MISSING_BIRTH_OUTPUT")?=observe(&bank,end,state,clock)?;
        receipt.final_cohorts=bank.cohorts.clone();
        receipt.pending_birth=None;
    }
    if bank.digests()[..input.expected_old_digests.len()]!=input.expected_old_digests {return Err("OLD_STOCK_FINAL_DIGEST".into());}
    receipt.final_cohorts=bank.cohorts;
    Ok(())
}

#[derive(Clone, Debug, Deserialize)]
pub struct CallbackQuery {pub x:f64,pub state:[f64;3],pub direction:[f64;3]}
#[derive(Clone, Debug, Deserialize)]
pub struct CallbackInput {pub bank:FrozenBank,pub queries:Vec<CallbackQuery>}
pub fn callbacks(input:CallbackInput) -> Result<Value,String> {
    for c in &input.bank.cohorts {c.validate()?;}
    let mut rows=vec![];
    for q in input.queries {
        let ev=input.bank.eval(q.x,q.state)?;
        rows.push(json!({"x":q.x,"state":q.state,"direction":q.direction,"evaluation":ev,
            "jvp":input.bank.jvp(q.x,q.state,q.direction)?}));
    }
    Ok(json!({"algorithm":ALGORITHM,"bank":input.bank,"rows":rows}))
}
