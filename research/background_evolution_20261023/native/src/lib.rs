//! Fixed-scale spatially homogeneous Einstein--matter background operator.
//!
//! x=ct/L, h=L H_phys/c, sigma=L sigma_phys/c, N=L n_geom,
//! A=L a_geom, rho=kappa L^2 mu, flux=kappa L^2 F/c,
//! p=kappa L^2 p_phys, Pi=kappa L^2 pi_phys, lambda=Lambda L^2.
//! Here kappa=8*pi*G/c^4. No equation divides by h.
//!
//! Pack: h, sigma(xx,yy,xy,xz,yz), N(xx,yy,zz,xy,xz,yz),
//! A(x,y,z), alpha=ln(scale), all rho_s, then all flux_s(x,y,z).
//! Sigma and Pi are symmetric trace-free by their five-component encoding.
//! No constraint projection, clipping, EOS, or kinetic closure is applied.

use std::error::Error;
use std::fmt;

type Matrix = [[f64; 3]; 3];
type Vector = [f64; 3];

/// Prescribed normal-frame pressure, STF stress, and inter-sector transfers.
/// Transfer sums must vanish within 128 machine epsilons times their L1 scale.
#[derive(Debug, Clone)]
pub struct Sources {
    pub pressure: Vec<f64>,
    pub pi5: Vec<[f64; 5]>,
    pub energy_transfer: Vec<f64>,
    pub momentum_transfer: Vec<[f64; 3]>,
}

impl Sources {
    pub fn zeros(sectors: usize) -> Self {
        Self {
            pressure: vec![0.0; sectors],
            pi5: vec![[0.0; 5]; sectors],
            energy_transfer: vec![0.0; sectors],
            momentum_transfer: vec![[0.0; 3]; sectors],
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BackgroundError(pub String);

impl fmt::Display for BackgroundError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { f.write_str(&self.0) }
}
impl Error for BackgroundError {}

fn err(message: impl Into<String>) -> BackgroundError { BackgroundError(message.into()) }

pub fn packed_len(sectors: usize) -> Result<usize, BackgroundError> {
    sectors.checked_mul(4).and_then(|n| n.checked_add(16))
        .ok_or_else(|| err("sector count overflows state size"))
}

fn validate_state(sectors: usize, state: &[f64], lambda: f64) -> Result<(), BackgroundError> {
    let expected = packed_len(sectors)?;
    if state.len() != expected {
        return Err(err(format!("state length: expected {expected}, received {}", state.len())));
    }
    if !lambda.is_finite() || state.iter().any(|v| !v.is_finite()) {
        return Err(err("state and lambda must be finite"));
    }
    Ok(())
}

fn compensated_sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut sum = 0.0;
    let mut correction = 0.0;
    for value in values {
        let adjusted = value - correction;
        let next = sum + adjusted;
        correction = (next - sum) - adjusted;
        sum = next;
    }
    sum
}

fn check_balance(values: &[f64], label: &str) -> Result<(), BackgroundError> {
    let scale = values.iter().fold(0.0_f64, |m, &x| m.max(x.abs()));
    if scale == 0.0 { return Ok(()); }
    // Scaling preserves the requested L1-relative criterion without overflow.
    let total = compensated_sum(values.iter().map(|x| x / scale));
    let magnitude = compensated_sum(values.iter().map(|x| x.abs() / scale));
    let tolerance = 128.0 * f64::EPSILON * magnitude;
    if total.abs() > tolerance {
        return Err(err(format!("{label} transfers do not balance (scaled sum {total:.17e}, tolerance {tolerance:.17e})")));
    }
    Ok(())
}

fn validate_sources(sectors: usize, src: &Sources, rotation: Vector) -> Result<(), BackgroundError> {
    if src.pressure.len() != sectors || src.pi5.len() != sectors
        || src.energy_transfer.len() != sectors || src.momentum_transfer.len() != sectors {
        return Err(err("source lengths must equal sector count"));
    }
    let invalid = src.pressure.iter().chain(&src.energy_transfer).any(|v| !v.is_finite())
        || src.pi5.iter().flatten().any(|v| !v.is_finite())
        || src.momentum_transfer.iter().flatten().any(|v| !v.is_finite())
        || rotation.iter().any(|v| !v.is_finite());
    if invalid { return Err(err("sources and frame rotation must be finite")); }
    check_balance(&src.energy_transfer, "energy")?;
    for component in 0..3 {
        let column: Vec<_> = src.momentum_transfer.iter().map(|v| v[component]).collect();
        check_balance(&column, &format!("momentum component {component}"))?;
    }
    Ok(())
}

fn stf(v: &[f64]) -> Matrix {
    [[v[0], v[2], v[3]], [v[2], v[1], v[4]], [v[3], v[4], -v[0] - v[1]]]
}
fn sym(v: &[f64]) -> Matrix {
    [[v[0], v[3], v[4]], [v[3], v[1], v[5]], [v[4], v[5], v[2]]]
}
fn trace(x: Matrix) -> f64 { x[0][0] + x[1][1] + x[2][2] }
fn dot(x: Vector, y: Vector) -> f64 { x[0]*y[0] + x[1]*y[1] + x[2]*y[2] }
fn matvec(x: Matrix, y: Vector) -> Vector {
    std::array::from_fn(|i| dot(x[i], y))
}
fn matmul(x: Matrix, y: Matrix) -> Matrix {
    std::array::from_fn(|i| std::array::from_fn(|j| (0..3).map(|k| x[i][k]*y[k][j]).sum()))
}
fn commutator(x: Matrix, y: Matrix) -> Matrix {
    let xy=matmul(x,y); let yx=matmul(y,x);
    std::array::from_fn(|i| std::array::from_fn(|j| xy[i][j]-yx[i][j]))
}
fn cross_matrix(x: Vector) -> Matrix {
    [[0.0,-x[2],x[1]], [x[2],0.0,-x[0]], [-x[1],x[0],0.0]]
}
fn contraction(x: Matrix, y: Matrix) -> f64 {
    (0..3).map(|i| (0..3).map(|j| x[i][j]*y[i][j]).sum::<f64>()).sum()
}
fn epsilon_nx(n: Matrix, x: Matrix) -> Vector {
    let product=matmul(n,x);
    [product[1][2]-product[2][1], product[2][0]-product[0][2], product[0][1]-product[1][0]]
}

/// Scalar and STF spatial Ricci curvature in the fixed-scale variables.
/// This algebraic extension uses the symmetric Ricci part when N A != 0.
fn curvature(n: Matrix, a: Vector) -> (f64, Matrix) {
    let nn=matmul(n,n); let tn=trace(n);
    let b: Matrix=std::array::from_fn(|i| std::array::from_fn(|j| 2.0*nn[i][j]-tn*n[i][j]));
    let tb=trace(b);
    let cross=commutator(cross_matrix(a),n);
    let s=std::array::from_fn(|i| std::array::from_fn(|j| b[i][j]+cross[i][j]-if i==j {tb/3.0} else {0.0}));
    (-6.0*dot(a,a)-tb/2.0, s)
}

/// Hamiltonian C, Codazzi M[3], and Jacobi J[3].
/// C=3h^2-sigma:sigma/2+R3/2-sum(rho)-lambda;
/// M=sum(flux)-3 sigma A-epsilon(N,sigma); J=N A.
pub fn constraints(sectors: usize, state: &[f64], lambda: f64) -> Result<[f64; 7], BackgroundError> {
    validate_state(sectors,state,lambda)?;
    let h=state[0]; let sigma=stf(&state[1..6]); let n=sym(&state[6..12]);
    let a=[state[12],state[13],state[14]];
    let (r3,_)=curvature(n,a);
    let rho=compensated_sum(state[16..16+sectors].iter().copied());
    let mut flux=[0.0;3];
    for k in 0..3 { flux[k]=compensated_sum((0..sectors).map(|s| state[16+sectors+3*s+k])); }
    let sigma_a=matvec(sigma,a); let ens=epsilon_nx(n,sigma); let jacobi=matvec(n,a);
    let mut out=[0.0;7];
    out[0]=3.0*h*h-contraction(sigma,sigma)/2.0+r3/2.0-rho-lambda;
    for i in 0..3 { out[1+i]=flux[i]-3.0*sigma_a[i]-ens[i]; out[4+i]=jacobi[i]; }
    if out.iter().any(|v| !v.is_finite()) { return Err(err("nonfinite constraint diagnostic (arithmetic overflow)")); }
    Ok(out)
}

/// Full fixed-scale RHS. All sector stresses and transfers remain distinct.
/// Scalars and all frame components are differentiated with respect to x=ct/L.
pub fn rhs(sectors: usize, state: &[f64], src: &Sources, lambda: f64, rotation: Vector)
    -> Result<Vec<f64>, BackgroundError> {
    validate_state(sectors,state,lambda)?;
    validate_sources(sectors,src,rotation)?;
    let h=state[0]; let sigma=stf(&state[1..6]); let n=sym(&state[6..12]);
    let a=[state[12],state[13],state[14]];
    let (_,s3)=curvature(n,a); let w=cross_matrix(rotation);
    let rho=compensated_sum(state[16..16+sectors].iter().copied());
    let pressure=compensated_sum(src.pressure.iter().copied());
    let mut pi=[[0.0;3];3];
    for values in &src.pi5 {
        let sector=stf(values);
        for i in 0..3 { for j in 0..3 { pi[i][j]+=sector[i][j]; } }
    }
    let ws=commutator(w,sigma); let wn=commutator(w,n);
    let sn=matmul(sigma,n); let ns=matmul(n,sigma);
    let ds: Matrix=std::array::from_fn(|i| std::array::from_fn(|j| -3.0*h*sigma[i][j]-s3[i][j]+pi[i][j]+ws[i][j]));
    let dn: Matrix=std::array::from_fn(|i| std::array::from_fn(|j| -h*n[i][j]+sn[i][j]+ns[i][j]+wn[i][j]));
    let sa=matvec(sigma,a); let wa=matvec(w,a);
    let mut out=vec![0.0;state.len()];
    out[0]=-h*h-contraction(sigma,sigma)/3.0-(rho+3.0*pressure)/6.0+lambda/3.0;
    out[1..6].copy_from_slice(&[ds[0][0],ds[1][1],ds[0][1],ds[0][2],ds[1][2]]);
    out[6..12].copy_from_slice(&[dn[0][0],dn[1][1],dn[2][2],dn[0][1],dn[0][2],dn[1][2]]);
    for i in 0..3 { out[12+i]=-h*a[i]-sa[i]+wa[i]; }
    out[15]=h;
    for s in 0..sectors {
        let r=state[16+s]; let base=16+sectors+3*s;
        let flux=[state[base],state[base+1],state[base+2]];
        let stress=stf(&src.pi5[s]);
        out[16+s]=-3.0*h*(r+src.pressure[s])+2.0*dot(a,flux)-contraction(sigma,stress)+src.energy_transfer[s];
        let sf=matvec(sigma,flux); let pa=matvec(stress,a);
        let enp=epsilon_nx(n,stress); let wf=matvec(w,flux);
        for i in 0..3 { out[base+i]=-4.0*h*flux[i]-sf[i]+3.0*pa[i]+enp[i]+wf[i]+src.momentum_transfer[s][i]; }
    }
    if out.iter().any(|v| !v.is_finite()) { return Err(err("nonfinite RHS (arithmetic overflow)")); }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn close(a: f64,b: f64) { assert!((a-b).abs() <= 2e-14*(1.0+a.abs().max(b.abs())), "{a:.17e} != {b:.17e}"); }
    fn zero_constraints(s: usize, y: &[f64], lambda: f64) { for c in constraints(s,y,lambda).unwrap() { close(c,0.0); } }

    #[test]
    fn flat_flrw_dust_and_radiation_exact_time_derivatives() {
        for (h,rho,p,dh,drho) in [(2.0/3.0,4.0/3.0,0.0,-2.0/3.0,-8.0/3.0),(0.5,0.75,0.25,-0.5,-1.5)] {
            let mut y=vec![0.0;20]; y[0]=h;y[16]=rho;
            let mut src=Sources::zeros(1);src.pressure[0]=p;
            let f=rhs(1,&y,&src,0.0,[0.0;3]).unwrap();
            close(f[0],dh);close(f[16],drho);close(f[15],h);zero_constraints(1,&y,0.0);
            for k in 1..15 { close(f[k],0.0); }
        }
    }

    #[test]
    fn vacuum_kasner_exact_time_derivative() {
        let mut y=vec![0.0;16];y[0]=1.0/3.0;y[1]=-2.0/3.0;y[2]=1.0/3.0;
        let f=rhs(0,&y,&Sources::zeros(0),0.0,[0.0;3]).unwrap();
        close(f[0],-1.0/3.0);close(f[1],2.0/3.0);close(f[2],-1.0/3.0);zero_constraints(0,&y,0.0);
    }

    #[test]
    fn closed_dust_turnaround_h_zero_is_regular() {
        let mut y=vec![0.0;20];y[6]=1.0;y[7]=1.0;y[8]=1.0;y[16]=0.75;
        let f=rhs(1,&y,&Sources::zeros(1),0.0,[0.0;3]).unwrap();
        close(f[0],-0.125);close(f[15],0.0);close(f[16],0.0);zero_constraints(1,&y,0.0);
        assert!(f.iter().all(|x|x.is_finite()));
    }

    #[test]
    fn desitter_vacuum_is_fixed_geometry() {
        let mut y=vec![0.0;16];y[0]=1.0;
        let f=rhs(0,&y,&Sources::zeros(0),3.0,[0.0;3]).unwrap();
        close(f[0],0.0);close(f[15],1.0);zero_constraints(0,&y,3.0);
    }

    #[test]
    fn intersector_energy_and_momentum_balance_is_enforced() {
        let y=vec![0.0;24]; let mut src=Sources::zeros(2);
        src.energy_transfer=vec![2.0,-2.0];src.momentum_transfer=vec![[1.0,2.0,3.0],[-1.0,-2.0,-3.0]];
        let f=rhs(2,&y,&src,0.0,[0.0;3]).unwrap();close(f[16],2.0);close(f[17],-2.0);
        src.energy_transfer[1]=0.0;assert!(rhs(2,&y,&src,0.0,[0.0;3]).is_err());
        src.energy_transfer[1]=-2.0;src.momentum_transfer[1][2]=0.0;
        assert!(rhs(2,&y,&src,0.0,[0.0;3]).is_err());
        // No overflowing L1 sum can turn a large imbalance into acceptance.
        src.momentum_transfer=vec![[0.0;3];2];src.energy_transfer=vec![f64::MAX,-f64::MAX/2.0];
        assert!(rhs(2,&y,&src,0.0,[0.0;3]).is_err());
    }

    #[test]
    fn malformed_and_nonfinite_inputs_are_rejected() {
        let mut y=vec![0.0;20]; let src=Sources::zeros(1);
        assert!(rhs(1,&y[..19],&src,0.0,[0.0;3]).is_err());
        y[0]=f64::NAN;assert!(rhs(1,&y,&src,0.0,[0.0;3]).is_err());
        y[0]=0.0;let mut bad=src.clone();bad.pi5[0][2]=f64::INFINITY;
        assert!(rhs(1,&y,&bad,0.0,[0.0;3]).is_err());
        assert!(rhs(1,&y,&Sources::zeros(0),0.0,[0.0;3]).is_err());
    }

    #[test]
    fn flux_receives_the_same_rotation_as_every_spatial_vector() {
        let mut y=vec![0.0;20];y[17]=2.0;y[18]=-3.0;y[19]=4.0;
        let src=Sources::zeros(1);
        let f0=rhs(1,&y,&src,0.0,[0.0;3]).unwrap();
        let f=rhs(1,&y,&src,0.0,[0.0,0.0,0.5]).unwrap();
        close(f[17]-f0[17],1.5);close(f[18]-f0[18],1.0);close(f[19]-f0[19],0.0);
    }

    #[test]
    fn cancelling_stresses_retain_opposite_sector_work() {
        let mut y=vec![0.0;24];y[1]=0.2;y[2]=-0.1;
        let mut src=Sources::zeros(2);
        src.pi5=vec![[0.6,-0.3,0.0,0.0,0.0],[-0.6,0.3,0.0,0.0,0.0]];
        let f=rhs(2,&y,&src,0.0,[0.0;3]).unwrap();
        close(f[1],0.0);close(f[2],0.0);close(f[16],-0.18);close(f[17],0.18);
    }
}
