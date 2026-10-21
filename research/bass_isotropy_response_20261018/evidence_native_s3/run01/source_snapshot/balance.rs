//! Standalone optional BASS source-angular KL projection. No native REI mutation.
//! rustc --edition=2021 -O balance.rs -o balance_probe
//! rustc --edition=2021 --test balance.rs -o balance_tests
use std::fs::{self,OpenOptions};
use std::io::Write;

pub const ID: &str = "BASS_LRS_SOURCE_KL_P2_V1";
#[derive(Debug)]
pub struct Projection { pub weights:Vec<f64>, pub multiplier:f64, pub residual:f64, pub iterations:usize }
fn sum(xs:impl Iterator<Item=f64>)->f64 {
    let(mut s,mut c)=(0.0_f64,0.0_f64);
    for x in xs {let t=s+x;c+=if s.abs()>=x.abs(){(s-t)+x}else{(x-t)+s};s=t;}
    s+c
}
fn evaluated(logq:&[f64],p:&[f64],l:f64)->(Vec<f64>,f64) {
    let logs:Vec<f64>=logq.iter().zip(p).map(|(q,z)|q+l*z).collect();
    let top=logs.iter().copied().fold(f64::NEG_INFINITY,f64::max);
    let mut w:Vec<f64>=logs.iter().map(|x|(x-top).exp()).collect();
    let den=sum(w.iter().copied());for x in &mut w {*x/=den;}
    let m=sum(w.iter().zip(p).map(|(a,z)|a*z));(w,m)
}
pub fn project(mu:&[f64],prior:&[f64],tol:f64)->Result<Projection,&'static str>{
    let n=mu.len();
    if n<2||n>4096||prior.len()!=n||!tol.is_finite()||tol<1e-16||tol>1e-10{
        return Err("ANGULAR_INPUT_DOMAIN");}
    for i in 0..n {
        if !mu[i].is_finite()||mu[i].abs()>1.0||!prior[i].is_finite()||prior[i]<=0.0||
            (i>0&&mu[i]<=mu[i-1]){return Err("ANGULAR_INPUT_DOMAIN");}
    }
    let scale=prior.iter().copied().fold(0.0_f64,f64::max);
    let mut q:Vec<f64>=prior.iter().map(|v|v/scale).collect();let den=sum(q.iter().copied());
    for v in &mut q {*v/=den;if *v<=0.0{return Err("NUMERIC_POSITIVE_SUPPORT_LOSS");}}
    for i in 0..n {if (mu[i]+mu[n-1-i]).abs()>5e-14||(q[i]-q[n-1-i]).abs()>5e-14{
        return Err("REFLECTION_SOURCE_REQUIRED");}}
    let p:Vec<f64>=mu.iter().map(|m|(3.0*m*m-1.0)/2.0).collect();
    let low=p.iter().copied().fold(f64::INFINITY,f64::min);
    let high=p.iter().copied().fold(f64::NEG_INFINITY,f64::max);
    if !p.iter().all(|x|*x==0.0)&&!(low<0.0&&high>0.0){return Err("INFEASIBLE_ANGULAR_SUPPORT");}
    let before=sum(q.iter().zip(&p).map(|(a,z)|a*z));
    if before.abs()<=tol{return Ok(Projection{weights:q,multiplier:0.0,residual:before,iterations:0});}
    let logq:Vec<f64>=q.iter().map(|x|x.ln()).collect();
    let(mut lo,mut hi)=(-1.0,1.0);
    for _ in 0..60 {if evaluated(&logq,&p,lo).1<=0.0{break;}lo*=2.0;}
    for _ in 0..60 {if evaluated(&logq,&p,hi).1>=0.0{break;}hi*=2.0;}
    if evaluated(&logq,&p,lo).1>0.0||evaluated(&logq,&p,hi).1<0.0{return Err("BRACKET_FAILURE");}
    for k in 1..=160 {
        let l=lo+(hi-lo)/2.0;let(w,m)=evaluated(&logq,&p,l);
        if m.abs()<=tol {
            if w.iter().any(|x|!x.is_finite()||*x<=0.0){return Err("NUMERIC_POSITIVE_SUPPORT_LOSS");}
            return Ok(Projection{weights:w,multiplier:l,residual:m,iterations:k});
        }
        if m<0.0{lo=l;}else{hi=l;}
    }
    Err("MOMENT_NOT_CONVERGED")
}
fn run()->Result<(),String>{
    let args:Vec<String>=std::env::args().collect();
    if args.len()!=3{return Err("USAGE balance_probe INPUT OUTPUT".into());}
    if fs::metadata(&args[1]).map_err(|e|e.to_string())?.len()>2_000_000{return Err("INPUT_SIZE".into());}
    let data=fs::read_to_string(&args[1]).map_err(|e|e.to_string())?;
    let mut it=data.split_whitespace();
    if it.next()!=Some(ID){return Err("INPUT_SCHEMA".into());}
    let n:usize=it.next().ok_or("CASE_COUNT")?.parse().map_err(|_|"CASE_COUNT")?;
    if n==0||n>512{return Err("CASE_COUNT".into());}
    let mut lines=Vec::new();let mut ids=std::collections::HashSet::new();
    for _ in 0..n{
        let id=it.next().ok_or("CASE_ID")?;
        if id.contains(',')||!ids.insert(id){return Err("CASE_ID".into());}
        let m:usize=it.next().ok_or("RAY_COUNT")?.parse().map_err(|_|"RAY_COUNT")?;
        if m<2||m>4096{return Err("RAY_COUNT".into());}
        let(mut mu,mut q)=(Vec::with_capacity(m),Vec::with_capacity(m));
        for _ in 0..m{
            mu.push(it.next().ok_or("TRUNCATED")?.parse::<f64>().map_err(|_|"NUMBER")?);
            q.push(it.next().ok_or("TRUNCATED")?.parse::<f64>().map_err(|_|"NUMBER")?);
        }
        let r=project(&mu,&q,3e-15).map_err(str::to_string)?;
        let weights=r.weights.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(",");
        lines.push(format!("{},{},{:.17e},{:.17e},{},{}",id,m,r.multiplier,r.residual,r.iterations,weights));
    }
    if it.next().is_some(){return Err("TRAILING_INPUT".into());}
    // No partial output on rejected input; no overwrite of existing results.
    let mut output=OpenOptions::new().write(true).create_new(true).open(&args[2]).map_err(|e|e.to_string())?;
    writeln!(output,"{} {}",ID,n).map_err(|e|e.to_string())?;
    for row in lines{writeln!(output,"{}",row).map_err(|e|e.to_string())?;}
    writeln!(output,"END {}",n).map_err(|e|e.to_string())?;
    println!("BALANCE_PASS cases={}",n);Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("BALANCE_ERROR {}",e);std::process::exit(3);}}
#[cfg(test)] mod tests{
    use super::*;
    #[test]fn analytic_two_pair_solution(){
        let r=project(&[-0.8,-0.2,0.2,0.8],&[0.1,0.4,0.4,0.1],3e-15).unwrap();
        assert!((r.weights[0]-0.44/(2.0*0.9)).abs()<1e-14);
        assert!(r.residual.abs()<=3e-15);assert!(r.weights.iter().all(|x|*x>0.0));
    }
    #[test]fn no_positive_support(){assert!(project(&[-0.2,-0.1,0.1,0.2],&[0.25;4],3e-15).is_err());}
    #[test]fn rejects_odd_source(){assert!(project(&[-0.8,-0.2,0.2,0.8],&[0.1,0.4,0.3,0.2],3e-15).is_err());}
    #[test]fn rejects_nan(){assert!(project(&[-0.8,-0.2,0.2,0.8],&[f64::NAN,0.4,0.4,0.1],3e-15).is_err());}
    #[test]fn idempotence(){let r=project(&[-0.8,-0.2,0.2,0.8],&[0.1,0.4,0.4,0.1],3e-15).unwrap();let q=project(&[-0.8,-0.2,0.2,0.8],&r.weights,3e-15).unwrap();assert!(q.weights.iter().zip(r.weights).all(|(a,b)|(a-b).abs()<5e-16));}
}
