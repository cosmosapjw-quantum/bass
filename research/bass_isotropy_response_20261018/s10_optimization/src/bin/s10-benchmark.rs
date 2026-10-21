//! Fixed S10 paired benchmark. Serialization, comparison, and file writes are
//! outside timed regions. No timing-dependent repetition count or solver tuning.
use bass_s10_optimization::{Evaluator,Mode,run_with_mode,run_independent,scientific_value};
use bass_s9_vigilode::{Cohort,FrozenBank,Evaluation,Input,RunReceipt};
use serde_json::{Value,json};
use sha2::{Digest,Sha256};
use std::{fs,path::Path,str::FromStr,time::Instant,hint::black_box};

#[cfg(feature="allocation-probe")]
mod allocations {
    use std::alloc::{GlobalAlloc,Layout,System};
    use std::sync::atomic::{AtomicBool,AtomicU64,Ordering::Relaxed};
    pub struct Counting;
    static ACTIVE:AtomicBool=AtomicBool::new(false);
    static CALLS:AtomicU64=AtomicU64::new(0);
    static BYTES:AtomicU64=AtomicU64::new(0);
    unsafe impl GlobalAlloc for Counting {
        unsafe fn alloc(&self,l:Layout)->*mut u8 {
            if ACTIVE.load(Relaxed) {CALLS.fetch_add(1,Relaxed);BYTES.fetch_add(l.size() as u64,Relaxed);}
            unsafe {System.alloc(l)}
        }
        unsafe fn alloc_zeroed(&self,l:Layout)->*mut u8 {
            if ACTIVE.load(Relaxed) {CALLS.fetch_add(1,Relaxed);BYTES.fetch_add(l.size() as u64,Relaxed);}
            unsafe {System.alloc_zeroed(l)}
        }
        unsafe fn realloc(&self,p:*mut u8,l:Layout,n:usize)->*mut u8 {
            if ACTIVE.load(Relaxed) {CALLS.fetch_add(1,Relaxed);BYTES.fetch_add(n as u64,Relaxed);}
            unsafe {System.realloc(p,l,n)}
        }
        unsafe fn dealloc(&self,p:*mut u8,l:Layout) {unsafe {System.dealloc(p,l)}}
    }
    pub fn count<T>(f:impl FnOnce()->T)->(T,u64,u64) {
        CALLS.store(0,Relaxed);BYTES.store(0,Relaxed);ACTIVE.store(true,Relaxed);
        let r=f();ACTIVE.store(false,Relaxed);
        (r,CALLS.load(Relaxed),BYTES.load(Relaxed))
    }
}
#[cfg(feature="allocation-probe")]
#[global_allocator]
static ALLOCATOR:allocations::Counting=allocations::Counting;
const MODES:[&str;6]=["baseline","stream","prepared","cache","simd","simd_cache"];
const CASES:[&str;4]=["closed_mf_into_ls_r2","closed_small_clock4_r2","flrw_mf_into_ls_fine","flrw_small_clock4_fine"];
const ROUNDS:usize=7;
fn mode(s:&str)->Mode {Mode::from_str(s).unwrap()}
fn sha(b:&[u8])->String {format!("{:x}",Sha256::digest(b))}
fn write(p:&Path,v:&Value) {fs::write(p,serde_json::to_vec_pretty(v).unwrap()).unwrap();}
fn record(f:&mut std::fs::File,v:&Value) {use std::io::Write;writeln!(f,"{}",v).unwrap();f.flush().unwrap();}
fn same_value(r:&RunReceipt)->(Value,String) {let v=scientific_value(r);let hash=sha(&serde_json::to_vec(&v).unwrap());(v,hash)}
fn eval_bits(e:&Evaluation)->Vec<u64> {
    e.rhs.iter().chain(e.jacobian.iter().flatten()).chain(&e.partial_t)
        .chain([e.energy,e.pi,e.pi_b,e.donor].iter()).map(|x|x.to_bits()).collect()
}
fn bank(n:usize,k:usize)->FrozenBank {
    let mu:Vec<f64>=(0..n).map(|i|(2*i+1) as f64/n as f64-1.0).collect();
    let alpha=vec![1.0/n as f64;n];
    FrozenBank {cohorts:(0..k).map(|j|Cohort {u:j as f64*0.003,
        b_birth:(j%5) as f64*0.01-0.02,energy_birth:(j+1) as f64/(k+1) as f64,
        mu:mu.clone(),alpha:alpha.clone(),role:"synthetic_fixed_anisotropic_stock".into()}).collect(),
        donor0:0.7,decay_lambda:0.7,exposure:0.8,cosmological_constant:0.1}
}
fn query(i:usize,trace:&str)->(f64,[f64;3],[f64;3]) {
    let p=if trace=="changing" {i%32} else {(i/16)%32};
    (0.8+p as f64*0.001,[1.1+p as f64*0.01,0.3+p as f64*0.002,0.08-p as f64*0.0001],
        [0.3+(i%16) as f64*0.01,-0.2,0.1-(i%7) as f64*0.003])
}
fn exercise(ev:&Evaluator,calls:usize,trace:&str) {
    for i in 0..calls {let (x,s,v)=query(i,trace);
        if trace=="changing" {black_box(ev.eval(black_box(x),black_box(s)).unwrap());}
        else {black_box(ev.jvp(black_box(x),black_box(s),black_box(v)).unwrap());}
    }
}
fn preparation(out:&Path) {
    let mut f=fs::File::create(out.join("PREPARE_SAMPLES.jsonl")).unwrap();
    for n in [16,64,256] {for k in [2,16,64] {let b=bank(n,k);
        for m in MODES {black_box(Evaluator::new(b.clone(),mode(m)));}
        for round in 0..ROUNDS {for offset in 0..6 {
            let m=MODES[(offset+round)%6];let owned=b.clone();
            let begin=Instant::now();let ev=Evaluator::new(owned,mode(m));let seconds=begin.elapsed().as_secs_f64();
            black_box(&ev);
            record(&mut f,&json!({"kind":"prepare","n":n,"cohorts":k,"mode":m,"round":round,"seconds":seconds,
                "input_bank_clone_included":false,"drop_included":false,"timer_resolution_caution":true}));
        }}
    }}
}
fn micro(out:&Path) {
    preparation(out);
    let mut f=fs::File::create(out.join("MICRO_SAMPLES.jsonl")).unwrap();
    let mut proof=vec![];
    for n in [16,64,256] {for k in [2,16,64] {let b=bank(n,k);
        for c in &b.cohorts {c.validate().unwrap();}
        let evs:Vec<_>=MODES.iter().map(|s|Evaluator::new(b.clone(),mode(s))).collect();
        for trace in ["changing","jvp_reuse"] {
            let calls=(1_048_576/(n*k)).clamp(64,8192);
            for (mi,ev) in evs.iter().enumerate() {
                let mut exact=true;let mut bits=vec![];
                for i in 0..64 {let (x,s,v)=query(i,trace);
                    let a=if trace=="changing" {eval_bits(&evs[0].eval(x,s).unwrap())}
                        else {evs[0].jvp(x,s,v).unwrap().map(f64::to_bits).to_vec()};
                    let z=if trace=="changing" {eval_bits(&ev.eval(x,s).unwrap())}
                        else {ev.jvp(x,s,v).unwrap().map(f64::to_bits).to_vec()};
                    exact &= a==z;bits.extend(z);
                }
                proof.push(json!({"n":n,"cohorts":k,"trace":trace,"mode":MODES[mi],"exact":exact,
                    "queries":64,"output_bits_sha256":sha(&serde_json::to_vec(&bits).unwrap()),"backend":format!("{:?}",ev.backend())}));
                if !exact {write(&out.join("MICRO_PROOF.json"),&json!(proof));panic!("MICRO_BIT_IDENTITY_FAILURE");}
                exercise(ev,calls,trace); // exactly one untimed warmup per mode/trace/grid
            }
            for round in 0..ROUNDS {for ci in 0..5 {let cand=1+(ci+round)%5;
                let order=if (ci+round)%2==0 {[0,cand]} else {[cand,0]};
                for mi in order {
                    let begin=Instant::now();exercise(&evs[mi],calls,trace);let seconds=begin.elapsed().as_secs_f64();
                    record(&mut f,&json!({"kind":"micro","n":n,"cohorts":k,"trace":trace,"candidate":MODES[cand],
                        "round":round,"order":order.map(|j|MODES[j]),"mode":MODES[mi],"calls":calls,"seconds":seconds}));
                }
            }}
            for m in MODES {let ev=Evaluator::with_diagnostics(b.clone(),mode(m));exercise(&ev,64,trace);
                record(&mut f,&json!({"kind":"diagnostic","n":n,"cohorts":k,"trace":trace,"mode":m,
                    "calls":64,"counters":ev.counters(),"timing_claim":false}));}
        }
    }}
    write(&out.join("MICRO_PROOF.json"),&json!(proof));
}
fn load_inputs(root:&Path)->Vec<Input> {CASES.iter().map(|s|serde_json::from_slice(&fs::read(root.join(s).join("INPUT.json")).unwrap()).unwrap()).collect()}
fn history(inputs:&[Input],out:&Path) {
    let mut f=fs::File::create(out.join("HISTORY_SAMPLES.jsonl")).unwrap();
    let mut expected=vec![];
    for (idx,input) in inputs.iter().enumerate() {
        let mut hashes=vec![];
        for m in MODES {
            let r=run_with_mode(input.clone(),mode(m)); // one warmup; preserve representative outside timing
            let (v,h)=same_value(&r);
            fs::write(out.join(format!("{}_{}.json",CASES[idx],m)),serde_json::to_vec_pretty(&r).unwrap()).unwrap();
            if r.status!="completed" || (!hashes.is_empty() && hashes[0]!=h) {
                record(&mut f,&json!({"kind":"warmup_failure","case":CASES[idx],"mode":m,"status":r.status,"hash":h,"baseline_hash":hashes.first(),"scientific_value":v}));
                panic!("HISTORY_BIT_IDENTITY_OR_COMPLETION_FAILURE");
            }
            hashes.push(h.clone());
            record(&mut f,&json!({"kind":"warmup_proof","case":CASES[idx],"mode":m,"status":r.status,"scientific_sha256":h,"exact":true}));
        }
        expected.push(hashes[0].clone());
        for round in 0..ROUNDS {for ci in 0..5 {let cand=1+(ci+round)%5;let order=if (round+ci)%2==0 {[0,cand]} else {[cand,0]};
            for mi in order {let owned=input.clone();let begin=Instant::now();let r=run_with_mode(owned,mode(MODES[mi]));let seconds=begin.elapsed().as_secs_f64();
                let (_,h)=same_value(&r);let exact=h==hashes[0];
                record(&mut f,&json!({"kind":"history","case":CASES[idx],"candidate":MODES[cand],"round":round,
                    "order":order.map(|j|MODES[j]),"mode":MODES[mi],"seconds":seconds,"internal_seconds":r.elapsed_seconds,
                    "status":r.status,"scientific_sha256":h,"exact":exact}));
                if r.status!="completed" || !exact {panic!("REPEATED_HISTORY_IDENTITY_FAILURE");}
            }
        }}
    }
    write(&out.join("EXPECTED_HISTORY_HASHES.json"),&json!({"cases":CASES,"hashes":expected}));
}
fn parallel(inputs:&[Input],out:&Path) {
    let expected:Value=serde_json::from_slice(&fs::read(out.join("EXPECTED_HISTORY_HASHES.json")).unwrap()).unwrap();
    let mut f=fs::File::create(out.join("PARALLEL_SAMPLES.jsonl")).unwrap();
    for workers in [1,2,4] {for m in ["baseline","simd_cache"] {
        let rows=run_independent(inputs.to_vec(),mode(m),workers).unwrap();
        for (i,r) in rows.iter().enumerate(){assert_eq!(r.status,"completed");assert_eq!(same_value(r).1,expected["hashes"][i].as_str().unwrap());}
        record(&mut f,&json!({"kind":"parallel_warmup","workers":workers,"mode":m,"jobs":inputs.len(),"exact":true}));
    }
    for round in 0..ROUNDS {let order=if round%2==0 {["baseline","simd_cache"]}else {["simd_cache","baseline"]};
        for m in order {let owned=inputs.to_vec();let begin=Instant::now();let rows=run_independent(owned,mode(m),workers).unwrap();let seconds=begin.elapsed().as_secs_f64();
            let hashes:Vec<_>=rows.iter().map(|r|same_value(r).1).collect();
            let exact=hashes.iter().enumerate().all(|(i,h)|Some(h.as_str())==expected["hashes"][i].as_str());
            let completed=rows.iter().all(|r|r.status=="completed");
            record(&mut f,&json!({"kind":"parallel","workers":workers,"round":round,"mode":m,"order":order,
                "seconds":seconds,"pool_construction_included":true,"jobs":inputs.len(),"hashes":hashes,"exact":exact,"all_completed":completed}));
            if !exact || !completed {panic!("PARALLEL_IDENTITY_FAILURE");}
        }
    }}
}
#[cfg(feature="allocation-probe")]
fn allocation_probe(out:&Path) {
    let mut rows=vec![];
    for n in [16,64,256] {for k in [2,16,64] {let b=bank(n,k);
        for m in MODES {let owned=b.clone();let (ev,setup_calls,setup_bytes)=allocations::count(||Evaluator::new(owned,mode(m)));
            for trace in ["changing","jvp_reuse"] {
                // Setup excluded; explicit fresh evaluator prevents prior cache state.
                let ev2=Evaluator::new(b.clone(),mode(m));
                let (_,calls,bytes)=allocations::count(||exercise(&ev2,64,trace));
                rows.push(json!({"n":n,"cohorts":k,"mode":m,"trace":trace,"evaluation_calls":64,
                    "allocation_or_reallocation_calls":calls,"requested_bytes_total":bytes,
                    "setup_allocation_calls":setup_calls,"setup_requested_bytes":setup_bytes,
                    "bank_clone_excluded_from_setup":true,"not_live_or_peak_bytes":true}));
            }
            black_box(ev);
        }
    }}
    write(&out.join("ALLOCATION_PROBE.json"),&json!({"schema":"BASS_S10_ALLOCATION_PROBE_V1","instrumentation":"GlobalAlloc single-thread counted only in explicit regions; separate binary from timings","rows":rows}));
}
fn main() {
    let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),4,"s10-benchmark micro|history|parallel|allocations INPUT_ROOT OUTPUT_DIR");
    let out=Path::new(&args[3]);fs::create_dir_all(out).unwrap();
    match args[1].as_str() {
        "micro"=> {assert!(!cfg!(feature="allocation-probe"),"timing binary must not instrument allocations");micro(out)},
        "history"=>{assert!(!cfg!(feature="allocation-probe"));history(&load_inputs(Path::new(&args[2])),out)},
        "parallel"=>{assert!(!cfg!(feature="allocation-probe"));parallel(&load_inputs(Path::new(&args[2])),out)},
        #[cfg(feature="allocation-probe")]
        "allocations"=>allocation_probe(out),
        _=>panic!("invalid benchmark command or feature")
    }
}
