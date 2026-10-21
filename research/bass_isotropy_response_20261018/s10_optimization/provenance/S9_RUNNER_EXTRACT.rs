//! Minimal original S9 runner excerpt; see provenance/ for byte identity/diff.
//! Only solver callback construction changes. P24, exact admission, events,
//! observations, original driver counters and failure receipts are preserved.
use crate::Mode;
use bass_s9_vigilode::{ALGORITHM,VIGILODE_SOURCE,SPECTRAL_OWNER,PROJECT_TOL,
    Cohort,MomentCertificate,CoordinateGrid,FrozenBank,Input,Observation,RunReceipt,
    birth_support,exact_moment_certificate,failure_kind};
use rodas5p_core::{LinearMethod,LinearSolverConfig};
use rodas5p_integrators::{AdaptiveStepConfig,MaxStepPolicy,OutputSchedule,
    integrate_rodas5p_fast_small_observed,
    integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace};
use serde_json::{Value,json};
use std::{sync::Arc,time::Instant};
#[allow(dead_code)]
#[path = "../../balance_p24.rs"]
mod balance_p24;

fn projected_birth(u:f64,b:f64,energy:f64,grid:&CoordinateGrid) -> Result<(Cohort,MomentCertificate,Value),String> {
    let (mu,q)=birth_support(b,grid)?;
    let p=balance_p24::project(&mu,&q,PROJECT_TOL).map_err(str::to_string)?;
    let cohort=Cohort {u,b_birth:b,energy_birth:energy,mu,alpha:p.weights,role:"new_isotropic_P24".into()};
    cohort.validate()?;
    let cert=exact_moment_certificate(&cohort.mu,&cohort.alpha)?;
    Ok((cohort,cert,json!({"owner_algorithm":balance_p24::ID,"project_tol":PROJECT_TOL,
        "multipliers":p.multipliers,"f64_residuals":p.residuals,"evaluations":p.iterations})))
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

fn observe(bank:&FrozenBank,x:f64,state:[f64;3],clock_error:f64) -> Result<Observation,String> {
    let e=bank.eval(x,state)?; let [h,_,y]=state;
    let c=h*h-y*y-e.donor-e.energy-bank.cosmological_constant;
    let scale=h*h+y*y+e.donor+e.energy+bank.cosmological_constant;
    Ok(Observation {x,state,e_donor:e.donor,e_radiation:e.energy,pi:e.pi,
        sigma:3.0_f64.sqrt()*y.abs()/h,c,c_relative:c.abs()/scale,clock_error})
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
