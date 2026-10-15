//! Standalone source-pinned BASS FD96 / GL kinetic massive source in Rust std.
//! Research-only opt-in supplier. No native REI production driver modified.
//! Convention: (-,+,+,+); Delta=P_parallel-P_perp, Pi=Delta/3,
//! Sigma=sqrt(3)*|s|/H with signed shear s separately.
//!
//! Source contract: export_grid.py writes original immutable BASS q/rw,
//! angular mu/w and initial energy normalization from source-checked Python.
//! This kernel independently evaluates f(q,mu) via conserved Killing momenta.
//! No Cargo dependencies; rustc -C opt-level=3 kernel.rs -o native_stress
use std::env;
use std::fs::{self,File};
use std::io::{BufWriter,Write};
use std::time::Instant;

#[derive(Debug)]
struct Grid {
    m:f64, norm:f64, radial:Vec<(f64,f64)>, angle:Vec<(f64,f64,f64)>,
}
#[derive(Copy,Clone)]
struct Case {x:f64,b:f64,a:f64}
#[derive(Copy,Clone,Default)]
struct ResultRow {rho:f64,pp:f64,pa:f64,delta:f64,db_delta:f64}
fn fail(msg:&str)->!{eprintln!("BASS_NATIVE_STRESS_FAIL: {msg}"); std::process::exit(3)}
fn load_grid(path:&str)->Grid {
    let text=fs::read_to_string(path).unwrap_or_else(|_|fail("GRID_IO"));
    let mut it=text.split_whitespace();
    if it.next()!=Some("BASS_FD96_STRESS_V1"){fail("GRID_SCHEMA");}
    let nr=it.next().unwrap_or("").parse::<usize>().unwrap_or_else(|_|fail("RADIAL_COUNT"));
    let na=it.next().unwrap_or("").parse::<usize>().unwrap_or_else(|_|fail("ANGULAR_COUNT"));
    let m=it.next().unwrap_or("").parse::<f64>().unwrap_or_else(|_|fail("MASS"));
    let norm=it.next().unwrap_or("").parse::<f64>().unwrap_or_else(|_|fail("NORM"));
    if nr!=96 || na<8 || na>256 || !m.is_finite() || m<3. || m>1e5
        || !norm.is_finite() || norm<=0. {fail("GRID_PHYSICAL_DOMAIN");}
    let mut radial=Vec::with_capacity(nr);
    for _ in 0..nr {
        let q=it.next().unwrap_or("").parse::<f64>().unwrap_or_else(|_|fail("Q_PARSE"));
        let w=it.next().unwrap_or("").parse::<f64>().unwrap_or_else(|_|fail("Q_WEIGHT_PARSE"));
        if !(q.is_finite() && q>=0. && w.is_finite() && w>=0.){fail("Q_NONPOSITIVE");}
        radial.push((q,w));
    }
    let mut angle=Vec::with_capacity(na);
    for _ in 0..na {
        let mu=it.next().unwrap_or("").parse::<f64>().unwrap_or_else(|_|fail("MU_PARSE"));
        let w=it.next().unwrap_or("").parse::<f64>().unwrap_or_else(|_|fail("MU_WEIGHT_PARSE"));
        if !(mu.is_finite() && mu.abs()<=1. && w.is_finite() && w>0.){fail("MU_DOMAIN");}
        let z=mu*mu;
        angle.push((z,(3.*z-1.)*0.5,w));
    }
    if it.next().is_some(){fail("TRAILING_GRID");}
    let ref_norm=radial.iter().map(|(q,w)|w*m.hypot(*q)).sum::<f64>();
    if (norm/ref_norm-1.).abs()>2e-14{fail("ENERGY_NORMALIZATION");}
    let wsum=angle.iter().map(|(_,_,w)|w).sum::<f64>();
    if (wsum-1.).abs()>2e-14{fail("MU_WEIGHT_NORMALIZATION");}
    Grid {m,norm,radial,angle}
}
fn evaluate(g:&Grid,c:Case)->ResultRow {
    if !(c.x.is_finite()&&c.b.is_finite()&&c.a.is_finite()&&
        c.x>=0.&&c.x<=2.&&c.b.abs()<=1.&&c.a>=-1.&&c.a<=2.) {
        fail("CASE_PHYSICAL_DOMAIN");
    }
    let r=(-c.x).exp();let r2=r*r;let r3=r2*r;
    let tp=(2.*c.b).exp_m1();let tz=(-4.*c.b).exp_m1();
    // Exact continuum GL polynomial moments. At A=b=0, exactly zero.
    let poly=c.a/5.+tz*(1./3.+2.*c.a/15.)-tp*(1./3.-c.a/15.);
    let mut srho=0f64;let mut spbar=0f64;let mut sdelta=0f64;let mut ssus=0f64;
    for &(q,rw) in &g.radial {
        let k=r2*q*q;let e0=g.m.hypot(k.sqrt());let inv0=1./e0;
        let mut en_sum=0f64;let mut pb_sum=0f64;let mut tail=0f64;let mut sus=0f64;
        for &(z,p2,w) in &g.angle {
            let wa=w*(1.+c.a*p2);
            let d=tp*(1.-z)+tz*z;
            let e=(e0*e0+k*d).sqrt();
            let gh=p2+tz*z-tp*(1.-z)*0.5;
            let inv_diff=-k*d/(e*e0*(e+e0));
            en_sum+=wa*e;
            pb_sum+=wa*k*(1.+d)/(3.*e);
            tail+=wa*gh*inv_diff;
            // Exact partial_b DeltaP: second derivative of original rho.
            let dlb=-4.*(1.+tz)*z-(1.+tp)*(1.-z);
            let p=k*gh;
            sus+=wa*(k*dlb/e +2.*p*p/(e*e*e));
        }
        srho+=rw*en_sum;
        spbar+=rw*pb_sum;
        sdelta+=rw*k*(poly*inv0+tail);
        ssus+=rw*sus;
    }
    let coeff=r3/g.norm;
    let rho=coeff*srho;let pbar=coeff*spbar;
    let delta=coeff*sdelta;let db_delta=coeff*ssus;
    let pp=pbar-delta/3.;let pa=pbar+2.*delta/3.;
    if !(rho.is_finite()&&rho>0.&&pp.is_finite()&&pp>=-1e-15&&
       pa.is_finite()&&pa>=-1e-15&&delta.is_finite()&&db_delta.is_finite()){
        fail("NONPHYSICAL_EINSTEIN_SOURCE");
    }
    ResultRow{rho,pp,pa,delta,db_delta}
}
fn cases_from_file(path:&str)->Vec<Case> {
    let data=fs::read_to_string(path).unwrap_or_else(|_|fail("CASE_IO"));
    let mut out=Vec::new();
    for ln in data.lines(){
        let s=ln.trim();
        if s.is_empty()||s.starts_with('#'){continue;}
        let a:Vec<_>=s.split_whitespace().collect();
        if a.len()!=3{fail("CASE_FORMAT");}
        let mut v=[0f64;3];
        for j in 0..3 {v[j]=a[j].parse::<f64>().unwrap_or_else(|_|fail("CASE_PARSE"));}
        out.push(Case{x:v[0],b:v[1],a:v[2]});
    }
    if out.is_empty(){fail("NO_CASES");}
    out
}
fn evaluate_all(g:&Grid,cs:&[Case],threads:usize)->Vec<ResultRow> {
    if threads<1||threads>64{fail("THREAD_COUNT");}
    let mut out=vec![ResultRow::default();cs.len()];
    let batch=cs.len().div_ceil(threads).max(1);
    std::thread::scope(|scope|{
        for (oc,ic) in out.chunks_mut(batch).zip(cs.chunks(batch)) {
            scope.spawn(move || {
                for (target, &case) in oc.iter_mut().zip(ic){*target=evaluate(g,case);}
            });
        }
    });
    out
}
fn checksum(out:&[ResultRow])->(f64,f64) {
    // A deterministic, serial reduction independent of worker count.
    let mut sum=0f64; let mut sumabs=0f64;
    for v in out{
        sum+=v.rho+v.delta+v.db_delta*1e-3;
        sumabs+=v.delta.abs();
    }
    (sum,sumabs)
}
fn bench_cases(n:usize)->Vec<Case> {
    (0..n).map(|i|{
      let u=((i*31+7)%10007) as f64 / 10007.;
      let v=((i*169+13)%10009) as f64 / 10009.;
      let w=((i*77+17)%10037) as f64 / 10037.;
      let mut b=0.12*(v-0.5);
      let mut a=-0.9+2.8*w;
      if i%64==0{b=1e-16;a=0.}
      if i%64==1{b=0.;a=0.}
      Case{x:1.45*u,b,a}
    }).collect()
}
fn main(){
    let a:Vec<String>=env::args().collect();
    if a.len()!=6{fail("USAGE: eval GRID CASES OUT THREADS | bench GRID N THREADS REPEATS");}
    let g=load_grid(&a[2]);
    if a[1]=="eval" {
        let cases=cases_from_file(&a[3]);
        let threads=a[5].parse::<usize>().unwrap_or_else(|_|fail("THREAD_PARSE"));
        let rows=evaluate_all(&g,&cases,threads);
        let mut writer=BufWriter::new(File::create(&a[4]).unwrap_or_else(|_|fail("RESULT_WRITE")));
        writeln!(writer,"rho pp pa delta db_delta").unwrap();
        for r in rows{
            writeln!(writer,"{:0.17e} {:0.17e} {:0.17e} {:0.17e} {:0.17e}",
                     r.rho,r.pp,r.pa,r.delta,r.db_delta).unwrap();
        }
        println!("EVAL_PASS rows={} threads={} mass={} radial={} angular={}",
                 cases.len(),threads,g.m,g.radial.len(),g.angle.len());
    } else if a[1]=="bench" {
        let n=a[3].parse::<usize>().unwrap_or_else(|_|fail("BENCH_N"));
        let threads=a[4].parse::<usize>().unwrap_or_else(|_|fail("THREAD_PARSE"));
        let reps=a[5].parse::<usize>().unwrap_or_else(|_|fail("BENCH_REPS"));
        if n<10 || n>1_000_000 || reps<2 || reps>20 {fail("BENCH_BOUNDS");}
        let cases=bench_cases(n);
        let reference=evaluate_all(&g,&cases,1);
        let (refsum, refabs)=checksum(&reference);
        let mut times=Vec::with_capacity(reps);
        for _ in 0..reps {
            let t=Instant::now();
            let outputs=evaluate_all(&g,&cases,threads);
            let sec=t.elapsed().as_secs_f64();
            // bitwise oracle for every case, since elementwise independent.
            for (y,z) in outputs.iter().zip(&reference){
                if y.rho.to_bits()!=z.rho.to_bits() ||
                   y.pp.to_bits()!=z.pp.to_bits() ||
                   y.pa.to_bits()!=z.pa.to_bits() ||
                   y.delta.to_bits()!=z.delta.to_bits() ||
                   y.db_delta.to_bits()!=z.db_delta.to_bits() {fail("THREAD_PARITY");}
            }
            times.push(sec);
        }
        times.sort_by(|a,b|a.partial_cmp(b).unwrap());
        let median=times[times.len()/2];
        println!("BENCH_PASS n={} threads={} repeats={} median_s={:0.9} min_s={:0.9} checksum={:0.17e} sum_abs_delta={:0.17e} bitwise_parity=PASS",n,threads,reps,median,times[0],refsum,refabs);
    } else { fail("MODE");}
}
