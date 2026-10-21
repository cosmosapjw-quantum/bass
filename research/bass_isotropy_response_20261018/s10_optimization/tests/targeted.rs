//! Targeted source-only tests: run only after the publication/preregistration gate.
//! No new source model or full S9 reassurance campaign is embedded here.
use bass_s10_optimization::{Backend,Evaluation,Evaluator,FrozenBank,Input,Mode,
    fixtures::synthetic_bank,run_independent,run_with_mode,scientific_bytes};

fn eval_bits(e:&Evaluation)->Vec<u64> {
    e.rhs.iter().chain(e.jacobian.iter().flatten()).chain(&e.partial_t)
        .chain([e.energy,e.pi,e.pi_b,e.donor].iter()).map(|v|v.to_bits()).collect()
}
fn assert_eval(reference:&FrozenBank,evaluator:&Evaluator,x:f64,state:[f64;3]) {
    let a=reference.eval(x,state).unwrap();
    let b=evaluator.eval(x,state).unwrap();
    assert_eq!(eval_bits(&a),eval_bits(&b),"eval at x={x:?}, state={state:?}");
}
fn assert_jvp(reference:&FrozenBank,evaluator:&Evaluator,x:f64,state:[f64;3],v:[f64;3]) {
    let a=reference.jvp(x,state,v).unwrap();
    let b=evaluator.jvp(x,state,v).unwrap();
    assert_eq!(a.map(f64::to_bits),b.map(f64::to_bits),"JVP at x={x:?}, state={state:?}, v={v:?}");
}

#[test]
fn kernel_grid_all_variants_match_original_bits() {
    for nodes in [16,64,256] {
        for cohorts in [2,16,64] {
            let bank=synthetic_bank(nodes,cohorts).unwrap();
            for mode in Mode::ALL {
                let evaluator=Evaluator::new(bank.clone(),mode);
                for (x,state) in [(0.0,[1.0,0.3,0.08]),(0.4,[0.9,-1.7,-0.08]),
                    (1.2,[0.5,2.3,0.0]),(-0.0,[1.0,-0.0,-0.0])] {
                    assert_eval(&bank,&evaluator,x,state);
                    for v in [[1.0,0.0,0.0],[-0.5,1.25,-2.0],[0.0,-0.0,0.0]] {
                        assert_jvp(&bank,&evaluator,x,state,v);
                    }
                }
            }
        }
    }
}

#[test]
fn simd_scalar_fallback_and_partial_vector_tail_match() {
    // n=6 exercises a two-element tail while n=4 exercises one full vector.
    for nodes in [4,6,16] {
        let bank=synthetic_bank(nodes,2).unwrap();
        for mode in [Mode::Simd,Mode::SimdCache] {
            let fallback=Evaluator::with_scalar_fallback(bank.clone(),mode);
            let auto=Evaluator::new(bank.clone(),mode);
            assert_eq!(fallback.backend(),Backend::Scalar);
            for b in [-1.75,0.0,0.25,2.25] {
                assert_eval(&bank,&fallback,0.4,[1.0,b,-0.0]);
                assert_eval(&bank,&auto,0.4,[1.0,b,-0.0]);
            }
        }
    }
}

#[test]
fn matching_large_time_and_birth_time_is_not_split_into_exponentials() {
    let mut bank=synthetic_bank(16,2).unwrap();
    for c in &mut bank.cohorts {c.u=1e300;c.b_birth=0.25;}
    for mode in Mode::ALL {
        let evaluator=Evaluator::new(bank.clone(),mode);
        for b in [-1.75,0.25,2.25] { // exact differences d=-2,0,+2
            assert_eval(&bank,&evaluator,1e300,[1.0,b,0.08]);
            assert_jvp(&bank,&evaluator,1e300,[1.0,b,0.08],[0.2,-0.3,0.4]);
        }
    }
}

#[test]
fn cache_slots_are_separate_and_direction_is_never_cached() {
    let bank=synthetic_bank(16,2).unwrap();
    for mode in [Mode::Cache,Mode::SimdCache] {
        let evaluator=Evaluator::with_diagnostics(bank.clone(),mode);
        let state=[1.0,0.3,0.08];
        assert_eval(&bank,&evaluator,0.2,state); // one kernel computation
        assert_eval(&bank,&evaluator,0.2,state); // RHS hit
        assert_jvp(&bank,&evaluator,0.2,state,[1.0,0.0,0.0]); // transfer RHS->JVP
        assert_eval(&bank,&evaluator,0.201,[0.999,0.301,0.079]); // RHS stage replaces RHS slot
        assert_jvp(&bank,&evaluator,0.2,state,[0.0,1.0,0.0]);
        assert_jvp(&bank,&evaluator,0.2,state,[-0.2,0.3,0.4]);
        let counters=evaluator.counters();
        assert!(counters.enabled);
        assert_eq!(counters.kernel_evaluations,2);
        assert_eq!(counters.rhs_cache_hits,1);
        assert_eq!(counters.jvp_rhs_transfers,1);
        assert_eq!(counters.jvp_cache_hits,2);
    }
}

#[test]
fn all_key_coordinates_and_signed_zeros_are_distinguished() {
    let bank=synthetic_bank(16,2).unwrap();
    let evaluator=Evaluator::with_diagnostics(bank.clone(),Mode::Cache);
    let x=0.2_f64;
    let state=[1.0_f64,0.3_f64,0.08_f64];
    let mut points=vec![(x,state),(f64::from_bits(x.to_bits()+1),state)];
    for i in 0..3 {
        let mut changed=state;changed[i]=f64::from_bits(changed[i].to_bits()+1);
        points.push((x,changed));
    }
    points.extend([(0.0,state),(-0.0,state),(x,[1.0,0.0,0.08]),
        (x,[1.0,-0.0,0.08]),(x,[1.0,0.3,0.0]),(x,[1.0,0.3,-0.0])]);
    for &(x,z) in &points {assert_eval(&bank,&evaluator,x,z);}
    assert_eq!(evaluator.counters().kernel_evaluations,points.len() as u64);
    assert_eq!(evaluator.counters().rhs_cache_hits,0);
}

#[test]
fn a_new_bank_at_the_same_point_cannot_reuse_old_evaluation() {
    let mut bank=synthetic_bank(16,2).unwrap();
    let evaluator=Evaluator::with_diagnostics(bank.clone(),Mode::Cache);
    let old=evaluator.eval(0.4,[1.0,0.3,0.08]).unwrap();
    // Only the caller-owned source clone changes; the evaluator has its own Arc.
    bank.cohorts[0].energy_birth*=2.0;
    bank.exposure+=0.01;
    assert_eq!(eval_bits(&old),eval_bits(&evaluator.eval(0.4,[1.0,0.3,0.08]).unwrap()));
    let new_evaluator=Evaluator::with_diagnostics(bank.clone(),Mode::Cache);
    let new=new_evaluator.eval(0.4,[1.0,0.3,0.08]).unwrap();
    assert_ne!(old.energy.to_bits(),new.energy.to_bits());
    assert_eq!(eval_bits(&bank.eval(0.4,[1.0,0.3,0.08]).unwrap()),eval_bits(&new));
    assert_eq!(new_evaluator.counters().kernel_evaluations,1);
    assert_eq!(new_evaluator.counters().rhs_cache_hits,0);
}

#[test]
fn domain_errors_and_precedence_match_original_then_recover() {
    let bank=synthetic_bank(16,2).unwrap();
    for mode in Mode::ALL {
        let evaluator=Evaluator::with_diagnostics(bank.clone(),mode);
        let good=[1.0,0.3,0.08];
        assert_eval(&bank,&evaluator,0.4,good);
        for (x,state) in [(f64::NAN,good),(f64::INFINITY,good),
            (0.4,[0.0,0.3,0.08]),(0.4,[-0.0,0.3,0.08]),
            (0.4,[-1.0,0.3,0.08]),(0.4,[1.0,f64::NAN,0.08]),
            (0.4,[1.0,0.3,f64::NEG_INFINITY]),(-1000.0,good)] {
            assert_eq!(bank.eval(x,state).unwrap_err(),evaluator.eval(x,state).unwrap_err());
        }
        for v in [[f64::NAN,0.0,0.0],[0.0,f64::INFINITY,0.0]] {
            assert_eq!(bank.jvp(f64::NAN,good,v).unwrap_err(),
                evaluator.jvp(f64::NAN,good,v).unwrap_err());
        }
        assert_eval(&bank,&evaluator,0.4,good);
        assert_jvp(&bank,&evaluator,0.4,good,[0.2,0.3,0.4]);
    }
}

fn short_input(arm:&str,birth:bool)->Input {
    let mut input:Input=serde_json::from_str(include_str!("../../s9_vigilode/inputs/base.json")).unwrap();
    input.config.k=if birth {1}else{0};
    if !birth {input.config.decay_lambda=0.0;}
    input.config.birth_end=0.02;
    input.config.x_end=0.03;
    input.output_times=vec![0.0,0.01,0.02,0.03];
    input.solver.arm=arm.into();
    input.solver.rtol=1e-10;
    input.solver.atol=1e-12;
    input.solver.initial_step=0.001;
    input.solver.max_step=0.01;
    input
}

#[test]
fn short_no_birth_and_one_birth_keep_the_entire_scientific_receipt() {
    for (arm,birth) in [("mf_into_ls",false),("small_clock4",true)] {
        let input=short_input(arm,birth);
        let baseline=bass_s9_vigilode::run(input.clone());
        assert_eq!(baseline.status,"completed", "baseline fixture: {:?}",baseline.failure);
        for mode in Mode::ALL {
            let candidate=run_with_mode(input.clone(),mode);
            assert_eq!(scientific_bytes(&baseline),scientific_bytes(&candidate),"mode={mode:?}, arm={arm}");
        }
    }
}

#[test]
fn input_failure_receipt_keeps_every_field() {
    let mut input=short_input("mf_into_ls",false);
    input.expected_old_digests[0]="deliberately_wrong_test_digest".into();
    let baseline=bass_s9_vigilode::run(input.clone());
    assert_eq!(baseline.status,"failed");
    for mode in Mode::ALL {
        assert_eq!(scientific_bytes(&baseline),scientific_bytes(&run_with_mode(input.clone(),mode)));
    }
}

#[test]
fn independent_histories_keep_input_order_and_worker_cap() {
    let a=short_input("mf_into_ls",false);
    let b=short_input("small_clock4",false);
    let expected=[bass_s9_vigilode::run(a.clone()),bass_s9_vigilode::run(b.clone())];
    for workers in [1,2,4] {
        let actual=run_independent(vec![a.clone(),b.clone()],Mode::Cache,workers).unwrap();
        assert_eq!(actual.len(),expected.len());
        for (actual,expected) in actual.iter().zip(&expected) {
            assert_eq!(scientific_bytes(actual),scientific_bytes(expected));
        }
    }
    for workers in [0,3,5,16] {
        assert_eq!(run_independent(vec![],Mode::Cache,workers).unwrap_err(),"WORKER_CAP_DOMAIN_1_2_4");
    }
}

#[test]
fn exact_receipt_comparison_retains_signed_zero_and_non_timing_fields() {
    let input=short_input("mf_into_ls",false);
    let mut a=bass_s9_vigilode::run(input);
    let mut b=a.clone();
    a.elapsed_seconds=1.0;b.elapsed_seconds=2.0;
    assert_eq!(scientific_bytes(&a),scientific_bytes(&b));
    a.input.config.y0=0.0;b.input.config.y0=-0.0;
    assert_ne!(scientific_bytes(&a),scientific_bytes(&b));
    b=a.clone();b.status="changed_status".into();
    assert_ne!(scientific_bytes(&a),scientific_bytes(&b));
}
