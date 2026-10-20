//! Fixed VigilODE APIs with an immutable, fresh evaluator for each segment.
use crate::{Evaluator, FrozenBank, Mode};
use rodas5p_core::{CoreError, CoreResult};
use rodas5p_integrators::{OdeProblem,SmallProblem};
use std::sync::Arc;

fn state3(v:&[f64]) -> CoreResult<[f64;3]> {
    v.try_into().map_err(|_|CoreError::Dimension("BASS state must have dimension three".into()))
}
fn core_error(e:String) -> CoreError {CoreError::InvalidInput(e)}

pub(crate) fn ode_problem(bank:Arc<FrozenBank>,mode:Mode) -> CoreResult<OdeProblem> {
    let evaluator=Arc::new(Evaluator::from_arc(bank,mode));
    let (br,bj,bt)=(evaluator.clone(),evaluator.clone(),evaluator);
    OdeProblem::new("BASS S9 independent Raychaudhuri frozen bank",3,
        Arc::new(move |x,z,out| {
            out.copy_from_slice(&br.eval(x,state3(z)?).map_err(core_error)?.rhs);Ok(())
        }),None,None,
        Some(Arc::new(move |x,z,v,out| {
            out.copy_from_slice(&bj.jvp(x,state3(z)?,state3(v)?).map_err(core_error)?);Ok(())
        })),
        Some(Arc::new(move |x,z,out| {
            out.copy_from_slice(&bt.eval(x,state3(z)?).map_err(core_error)?.partial_t);Ok(())
        })),false,None,None)
}

pub(crate) struct ClockProblem(Evaluator);
impl ClockProblem {
    pub(crate) fn new(bank:Arc<FrozenBank>,mode:Mode)->Self {
        Self(Evaluator::from_arc(bank,mode))
    }
}
impl SmallProblem<4> for ClockProblem {
    fn rhs(&self,z:&[f64;4],out:&mut[f64;4]) {
        match self.0.eval(z[3],[z[0],z[1],z[2]]) {
            Ok(e)=>{out[..3].copy_from_slice(&e.rhs);out[3]=1.0;},
            Err(_)=>out.fill(f64::NAN),
        }
    }
    fn jacobian(&self,z:&[f64;4],out:&mut[[f64;4];4]) {
        *out=[[0.0;4];4];
        match self.0.eval(z[3],[z[0],z[1],z[2]]) {
            Ok(e)=>for i in 0..3 {out[i][..3].copy_from_slice(&e.jacobian[i]);out[i][3]=e.partial_t[i];},
            Err(_)=>*out=[[f64::NAN;4];4],
        }
    }
}
