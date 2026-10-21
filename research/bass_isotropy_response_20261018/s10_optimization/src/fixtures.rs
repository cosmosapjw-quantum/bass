//! Deterministic positive reflection-symmetric kernel fixtures. These are
//! frozen kernel banks, not newly admitted P24 birth sources or new histories.
use crate::{Cohort,FrozenBank};

pub fn synthetic_bank(nodes:usize,cohorts:usize)->Result<FrozenBank,String> {
    if nodes<4 || nodes%2!=0 || nodes>512 || cohorts==0 || cohorts>64 {
        return Err("SYNTHETIC_BANK_DOMAIN".into());
    }
    let positives:Vec<_>=(0..nodes/2).map(|i|(2*i+1) as f64/nodes as f64).collect();
    let mut mu:Vec<_>=positives.iter().rev().map(|m|-*m).collect();
    mu.extend(positives);
    let alpha=vec![1.0/nodes as f64;nodes];
    let mut bank=FrozenBank {cohorts:vec![],donor0:0.7,decay_lambda:0.7,
        exposure:0.35,cosmological_constant:0.1};
    for j in 0..cohorts {
        let cohort=Cohort {u:0.005*j as f64,b_birth:0.3+0.0125*((j%9) as f64-4.0),
            energy_birth:0.01/(j+1) as f64,mu:mu.clone(),alpha:alpha.clone(),
            role:format!("synthetic_frozen_{j}")};
        cohort.validate()?;
        bank.cohorts.push(cohort);
    }
    Ok(bank)
}
