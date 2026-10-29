//! CE1-P scoped Rust oracle using BASS's *existing* covariant-momentum Frame.
//!
//! This is a binary64 independent implementation of the massless collisionless
//! stored ray E/P/Jacobian, not an outward MPFR192 certificate. The authoritative
//! certified source remains CE1-M/N/O; the output must never be promoted to a
//! production/claim-bearing residual merely because the native oracle agrees.
//!
//! Input protocol (ASCII decimal u64 raw binary64 words, whitespace separated):
//!   NRAY  ell0_bits ell1_bits ell2_bits
//!   mass_bits nx_bits ny_bits nz_bits      [NRAY records]
//! Output protocol:
//!   E_bits P0_bits P1_bits P2_bits J00_bits ... J22_bits (hex u64)
//!
//! BASS physically identifies the comoving frame by p^i = M^i_j q^j.
//! For diagonal Bianchi I, M=diag(exp(-ell_i)) and det M=exp(-sum ell).
//! E=det(M)*sum_a mass_a |M n_a|;
//! P_i=det(M)*sum_a mass_a (M n_a)_i^2/|M n_a|.
//! J_ij=-(1+2 delta_ij) P_i + det(M)*sum mass_a (M n)_i^2 (M n)_j^2/|M n|^3.
//! The row sum of J is -4P_i. No finite-difference approximation is required.

#[path = "../../_rustcore/src/kinetic/comoving.rs"]
mod bass_comoving;

use bass_comoving::Frame;
use std::io::{self, Read};

#[derive(Debug, Clone)]
struct Stress {
    energy: f64,
    pressure: [f64; 3],
    jacobian: [[f64; 3]; 3],
}

fn finite(x: f64, label: &str) -> Result<f64, String> {
    if x.is_finite() { Ok(x) } else { Err(format!("nonfinite {label}")) }
}

fn stress(ell: [f64; 3], rays: &[(f64, [f64; 3])]) -> Result<Stress, String> {
    if rays.is_empty() || rays.len() > 20_000 { return Err("invalid ray cardinality".into()); }
    let mut m = [0.0; 9];
    for k in 0..3 { m[4*k] = finite((-finite(ell[k], "ell")?).exp(), "exponential scale")?; }
    let frame = Frame { m };
    let det = finite(frame.det(), "frame determinant")?;
    if det <= 0.0 { return Err("nonpositive frame determinant".into()); }
    let mut e = 0.0;
    let mut p = [0.0; 3];
    let mut r = [[0.0; 3]; 3];
    for (mass, q) in rays.iter() {
        let mass = finite(*mass, "stored mass")?;
        if mass <= 0.0 { return Err("nonpositive stored ray mass".into()); }
        if q.iter().any(|v| !v.is_finite()) { return Err("nonfinite stored ray".into()); }
        let a = frame.apply(q);
        let a2 = [a[0]*a[0], a[1]*a[1], a[2]*a[2]];
        let norm2 = a2[0]+a2[1]+a2[2];
        let norm = finite(norm2.sqrt(), "stored ray norm")?;
        if norm <= 0.0 { return Err("zero stored ray norm".into()); }
        e += mass * norm;
        for i in 0..3 {
            p[i] += mass * a2[i]/norm;
            for j in 0..3 {
                // Algebraically a2[i]*a2[j]/norm^3; divide early to
                // avoid unneeded intermediate overflow at typical scales.
                r[i][j] += mass * (a2[i]/norm) * (a2[j]/norm2);
            }
        }
    }
    e = finite(det*e,"energy")?;
    for i in 0..3 {p[i] = finite(det*p[i],"pressure")?;}
    let mut jacobian=[[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            jacobian[i][j] = finite(-(1.0 + if i==j {2.0} else {0.0})*p[i] + det*r[i][j],"jacobian")?;
        }
    }
    Ok(Stress{energy:e, pressure:p, jacobian})
}

fn parse_bits(token: Option<&str>) -> Result<f64,String> {
    let s=token.ok_or("missing binary64 token")?;
    // Numeric bits are UNSIGNED DECIMAL; no float token parsing or locale.
    let b=s.parse::<u64>().map_err(|_|"malformed binary64 word")?;
    Ok(f64::from_bits(b))
}

fn parse_message(s: &str) -> Result<Stress, String> {
    let mut it=s.split_ascii_whitespace();
    let n=it.next().ok_or("missing ray count")?
        .parse::<usize>().map_err(|_|"invalid ray count")?;
    if n==0 || n>20_000 {return Err("invalid ray count".into());}
    let mut ell=[0.0;3];
    for item in &mut ell { *item=parse_bits(it.next())?; }
    let mut rays=Vec::with_capacity(n);
    for _ in 0..n {
        let mass=parse_bits(it.next())?;
        let mut q=[0.0;3];
        for item in &mut q { *item=parse_bits(it.next())?; }
        rays.push((mass,q));
    }
    if it.next().is_some() {return Err("unexpected trailing words".into());}
    stress(ell,&rays)
}

fn main(){
    if std::env::args().nth(1).as_deref()==Some("--self-test") {
        tests::run();
        println!("CE1P_RUST_SELFTEST_4_PASS");
        return;
    }
    let mut s=String::new();
    if io::stdin().read_to_string(&mut s).is_err() {eprintln!("invalid stdin");std::process::exit(2);}
    match parse_message(&s) {
        Ok(x) => {
            let mut words=Vec::with_capacity(13);
            words.push(x.energy.to_bits());
            for p in x.pressure {words.push(p.to_bits());}
            for row in x.jacobian {for j in row {words.push(j.to_bits());}}
            let result=words.iter().map(|x|format!("{x:016x}")).collect::<Vec<_>>().join(" ");
            println!("{result}");
        },
        Err(e) => {eprintln!("CE1P_REJECT: {e}");std::process::exit(2);}
    }
}

mod tests {
    pub fn run(){
        isotropic_six_axis_ray_stress_and_trace();
        common_shift_exact_massless_pressure_scaling();
        actual_bass_native_frame_step_isotropic_and_anisotropic();
        malicious_source_fail_closed();
    }
    use super::*;
        fn isotropic_six_axis_ray_stress_and_trace(){
        let rays = vec![
            (0.1,[1.,0.,0.]),(0.1,[-1.,0.,0.]),
            (0.1,[0.,1.,0.]),(0.1,[0.,-1.,0.]),
            (0.1,[0.,0.,1.]),(0.1,[0.,0.,-1.]),
        ];
        let x=stress([0.;3],&rays).unwrap();
        assert!((x.energy-0.6).abs()<1e-15);
        for p in x.pressure {assert!((p-0.2).abs()<1e-15);}
        assert!((x.pressure.iter().sum::<f64>()-x.energy).abs()<1e-15);
        for i in 0..3 {
            assert!((x.jacobian[i].iter().sum::<f64>()+4.*x.pressure[i]).abs()<1e-14);
        }
    }
        fn common_shift_exact_massless_pressure_scaling(){
        let rays = vec![(0.25,[0.3,0.4,0.5]),(0.75,[0.8,0.7,0.1])];
        let x=stress([0.04,0.02,0.01],&rays).unwrap();
        let s=0.017;
        let y=stress([0.04+s,0.02+s,0.01+s],&rays).unwrap();
        let f=(-4.*s).exp();
        assert!((y.energy-x.energy*f).abs()<2e-15);
        for i in 0..3 {assert!((y.pressure[i]-x.pressure[i]*f).abs()<2e-15);}
    }
        fn actual_bass_native_frame_step_isotropic_and_anisotropic(){
        let mut f=Frame::identity();
        let s=[0.0;6];let rot=[0.0;3];
        for _ in 0..100 {f=f.step(&s,&rot,&s,&rot,0.001);}
        let exact=(-0.1_f64).exp();
        for i in 0..3 {assert!((f.m[4*i]-exact).abs()<3e-15);}
        assert!((f.det()-exact.powi(3)).abs()<5e-15);
        let mut g=Frame::identity();
        let shear=[0.2,-0.13,-0.07,0.0,0.0,0.0];
        for _ in 0..100 {g=g.step(&shear,&rot,&shear,&rot,0.001);}
        for i in 0..3 {assert!((g.m[4*i]-(-(1.0+shear[i])*0.1).exp()).abs()<3e-15);}
    }
        fn malicious_source_fail_closed(){
        assert!(stress([0.;3],&[(1.0,[0.;3])]).is_err());
        assert!(stress([0.;3],&[(-1.0,[1.,0.,0.])]).is_err());
        assert!(stress([0.;3],&[(f64::NAN,[1.,0.,0.])]).is_err());
        assert!(stress([f64::INFINITY,0.,0.],&[(1.0,[1.,0.,0.])]).is_err());
        assert!(parse_message("0 0 0 0").is_err());
    }
}
