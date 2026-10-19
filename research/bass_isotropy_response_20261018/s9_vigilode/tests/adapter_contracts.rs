use bass_s9_vigilode::{Cohort, FrozenBank, ClockProblem, exact_moment_certificate, ode_problem};
use rodas5p_integrators::SmallProblem;
use std::sync::Arc;

fn bank() -> FrozenBank {
    // Three-node GL3 has exact reflection and represents P2/P4 to binary64
    // rounding. This is a development kernel fixture, not the production grid.
    let m=(3.0_f64/5.0).sqrt();
    FrozenBank {cohorts:vec![Cohort {u:0.0,b_birth:0.3,energy_birth:0.2,
        mu:vec![-m,0.0,m],alpha:vec![5.0/18.0,4.0/9.0,5.0/18.0],role:"old_isotropic".into()}],
        donor0:0.7,decay_lambda:0.7,exposure:0.0,cosmological_constant:0.1}
}

#[test]
fn exact_admission_rejects_bad_moment_without_weight_repair() {
    let b=bank(); let c=&b.cohorts[0];
    assert!(exact_moment_certificate(&c.mu,&c.alpha).unwrap().pass);
    assert!(!exact_moment_certificate(&[-1.0,1.0],&[0.5,0.5]).unwrap().pass);
    assert!(exact_moment_certificate(&[-1.0,1.0],&[-0.5,1.5]).is_err());
}

#[test]
fn parity_and_stock_hash_are_separate_contracts() {
    let b=bank(); let c=&b.cohorts[0]; c.validate().unwrap();
    let mut changed=c.clone(); changed.alpha[0]+=1e-16;
    assert_ne!(changed.digest(),c.digest());
    assert!(changed.validate().unwrap_err().contains("REFLECTION"));
    assert_eq!(b.digests(),b.clone().digests());
}

#[test]
fn birth_preserves_state_but_invalidates_rhs_ft_and_jacobian() {
    let before=bank(); let z=[1.01,0.3,0.08]; let w=0.02;
    let mut after=before.clone();
    // Choose analytic donor adjustment at x=0 and a normalized P24 birth.
    after.donor0-=w;
    let mut new=before.cohorts[0].clone(); new.energy_birth=w; new.role="new_isotropic_P24".into();
    after.cohorts.push(new);
    let a=before.eval(0.0,z).unwrap(); let b=after.eval(0.0,z).unwrap();
    assert!((b.rhs[0]-a.rhs[0]+w/(2.0*z[0])).abs()<5e-16);
    assert!((b.partial_t[0]-a.partial_t[0]-5.0*w/(2.0*z[0])).abs()<8e-16);
    assert!((b.jacobian[2][1]-a.jacobian[2][1]+8.0*w/(5.0*z[0])).abs()<5e-16);
    assert!((b.donor+b.energy-a.donor-a.energy).abs()<2e-16);
    assert_ne!(a.rhs,b.rhs); assert_ne!(a.partial_t,b.partial_t); assert_ne!(a.jacobian,b.jacobian);
    assert_eq!(before.cohorts[0].digest(),after.cohorts[0].digest());
    // Construction, not an unimplemented epoch convention, isolates the banks.
    ode_problem(Arc::new(before)).unwrap(); ode_problem(Arc::new(after)).unwrap();
}

#[test]
fn autonomous_clock_column_is_analytic_partial_t() {
    let b=bank(); let z=[0.91,0.36,0.04,0.2];
    let e=b.eval(z[3],[z[0],z[1],z[2]]).unwrap();
    let p=ClockProblem(Arc::new(b)); let mut f=[0.0;4]; let mut j=[[7.0;4];4];
    p.rhs(&z,&mut f); p.jacobian(&z,&mut j);
    assert_eq!(f[..3],e.rhs); assert_eq!(f[3],1.0); assert_eq!(j[3],[0.0;4]);
    for i in 0..3 {assert_eq!(j[i][..3],e.jacobian[i]); assert_eq!(j[i][3],e.partial_t[i]);}
}

#[test]
fn nonfinite_and_expanding_domain_fail_closed() {
    let b=bank();
    assert!(b.eval(0.0,[0.0,0.3,0.08]).is_err());
    assert!(b.eval(f64::NAN,[1.0,0.3,0.08]).is_err());
    assert!(b.jvp(0.0,[1.0,0.3,0.08],[f64::INFINITY,0.0,0.0]).is_err());
}
