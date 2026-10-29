//! CE1-R | BASS Rust-native collisionless observer-sky Liouville derivative.
//!
//! Uses the existing `Frame::apply`, `Frame::det`, `phys_dirs` from BASS.
//! `u=t/Tstar`, h_i = d ell_i / du; do NOT use `Frame::step`'s e-fold tau as u.
//! Unpolarized *energy-integrated* massless sky, NOT temperature/polarization CMB.
//!
//! Input ASCII (binary64 values encoded as decimal u64 bits):
//! `nrays ntimes lmax`, then `mass qx qy qz` per ray,
//! then `u ell1 ell2 ell3 h1 h2 h3` per time. Eight octant reflections.
//! Output CSV `u,E,dE,P1,dP1,P2,dP2,P3,dP3,a_l_m_re,im,da_l_m_re,im`.
//!
//! a_lm = det(M) sum_ray (w r/8) sum_sign Y*_lm(s),
//! M=diag(exp(-ell_i)), r=|M q|, s=-M q /r,
//! a'_lm = det(M) sum (w r/8) sum_sign [-(theta+Hn)Y*+grad Y* . s']
//! theta=sum(h_i), Hn=sum_i h_i s_i^2, s'_i=(Hn-h_i)s_i.
//! Polynomial harmonic Y*_lm = N_lm (-1)^m d_z^m P_l(z) (x-iy)^m,
//! so its analytic derivative is regular even on polar directions.

#[path = "../../_rustcore/src/kinetic/comoving.rs"]
mod bass_comoving;
use bass_comoving::{phys_dirs, Frame};
use std::f64::consts::PI;
use std::io::{self, Read};

#[derive(Clone, Copy, Debug, Default)]
struct Complex { re:f64, im:f64 }
impl Complex {
    fn new(re:f64, im:f64)->Self { Self{re,im} }
    fn add(self,b:Self)->Self{Self::new(self.re+b.re,self.im+b.im)}
    fn mul(self,b:Self)->Self{Self::new(self.re*b.re-self.im*b.im,self.re*b.im+self.im*b.re)}
    fn scale(self,s:f64)->Self{Self::new(self.re*s,self.im*s)}
    fn conj(self)->Self{Self::new(self.re,-self.im)}
    fn powu(self,m:usize)->Self{let mut out=Self::new(1.,0.);for _ in 0..m{out=out.mul(self);}out}
}
fn legendre_derivative(l:usize,m:usize,z:f64)->f64 {
    if m>l{return 0.;}
    let coef:[f64;5]= match l {
        0=>[1.,0.,0.,0.,0.], 1=>[0.,1.,0.,0.,0.],
        2=>[-0.5,0.,1.5,0.,0.], 3=>[0.,-1.5,0.,2.5,0.],
        4=>[0.375,0.,-3.75,0.,4.375],_=>unreachable!()
    };
    let mut value=0.;
    for i in m..=l{
        let mut c=coef[i];for k in 0..m{c*=(i-k) as f64;}
        value+=c*z.powi((i-m) as i32);
    }
    value
}
fn harmonic_and_derivative(l:usize,m:usize,s:[f64;3],sd:[f64;3])->(Complex,Complex) {
    let mut ratio=1.;for i in (l-m+1)..=(l+m){ratio/=i as f64;}
    let sign=if m%2==0{1.}else{-1.};
    let n=sign*(((2*l+1) as f64)/(4.*PI)*ratio).sqrt();
    let z=s[2];let dz=sd[2];
    let w=Complex::new(s[0],-s[1]);
    let dw=Complex::new(sd[0],-sd[1]);
    let wm=w.powu(m);
    let p=legendre_derivative(l,m,z);
    let dp=legendre_derivative(l,m+1,z);
    let y=wm.scale(n*p);
    let term1=wm.scale(dp*dz);
    let term2=if m>0{w.powu(m-1).mul(dw).scale((m as f64)*p)}else{Complex::default()};
    (y,term1.add(term2).scale(n))
}
#[derive(Clone,Copy)]struct Ray{mass:f64,n:[f64;3]}
fn bit(it:&mut std::str::SplitAsciiWhitespace<'_>)->Result<f64,String>{
    let s=it.next().ok_or("missing f64 word")?;
    let u=s.parse::<u64>().map_err(|_| "invalid bit word")?;
    let v=f64::from_bits(u);
    if !v.is_finite(){return Err("nonfinite f64 word".into());}
    Ok(v)
}
fn count(it:&mut std::str::SplitAsciiWhitespace<'_>)->Result<usize,String>{
    it.next().ok_or("missing count")?.parse().map_err(|_|"invalid count".into())
}
fn off(l:usize,m:usize)->usize{l*(l+1)/2+m}
#[derive(Clone)]struct Row{
    energy:f64,energy_dot:f64,p:[f64;3],p_dot:[f64;3],
    a:Vec<Complex>,adot:Vec<Complex>,trace_gap:f64,continuity_gap:f64,
}
fn compute(ell:[f64;3],h:[f64;3],rays:&[Ray],lmax:usize)->Result<Row,String>{
    if ell.iter().any(|v|!v.is_finite()||*v<0.)||h.iter().any(|v|!v.is_finite()||*v<=0.){
        return Err("invalid all-expanding proper-time geometry".into());
    }
    let mut m=[0.;9];for i in 0..3{m[4*i]=(-ell[i]).exp();}
    let f=Frame{m};let det=f.det();
    if !det.is_finite()||det<=0.{return Err("invalid frame determinant".into());}
    let nn=(lmax+1)*(lmax+2)/2;
    let mut row=Row{energy:0.,energy_dot:0.,p:[0.;3],p_dot:[0.;3],a:vec![Complex::default();nn],adot:vec![Complex::default();nn],trace_gap:0.,continuity_gap:0.};
    let theta=h.iter().sum::<f64>();
    for ray in rays{
        let q=f.apply(&ray.n);
        let (nback,mu)=phys_dirs(&f,&ray.n);
        let r=(q.iter().map(|x|x*x).sum::<f64>()).sqrt();
        if !r.is_finite()||r<=0.||!mu[0].is_finite()|| (mu[0]-r).abs()>5e-13 ||
            (0..3).any(|i|(nback[i]-q[i]/r).abs()>5e-13){return Err("BASS Frame direction mismatch".into());}
        let weight=det*ray.mass*r/8.;
        if !weight.is_finite()||weight<=0.{return Err("invalid comoving energy weight".into());}
        for signx in [-1.,1.]{for signy in [-1.,1.]{for signz in [-1.,1.]{
            let s=[-signx*q[0]/r,-signy*q[1]/r,-signz*q[2]/r];
            let hn=h.iter().enumerate().map(|(i,v)|v*s[i]*s[i]).sum::<f64>();
            let ds=[(hn-h[0])*s[0],(hn-h[1])*s[1],(hn-h[2])*s[2]];
            let dw=-(theta+hn)*weight;
            row.energy+=weight;row.energy_dot+=dw;
            for i in 0..3{row.p[i]+=weight*s[i]*s[i];row.p_dot[i]+=dw*s[i]*s[i]+2.*weight*s[i]*ds[i];}
            for l in 0..=lmax{for mm in 0..=l{
                let (y,yd)=harmonic_and_derivative(l,mm,s,ds);
                let j=off(l,mm);
                row.a[j]=row.a[j].add(y.scale(weight));
                row.adot[j]=row.adot[j].add(y.scale(dw).add(yd.scale(weight)));
            }}
        }}}
    }
    row.trace_gap=(row.p.iter().sum::<f64>()-row.energy).abs();
    row.continuity_gap=(row.energy_dot+theta*row.energy+(0..3).map(|i|h[i]*row.p[i]).sum::<f64>()).abs();
    Ok(row)
}
fn signed_complex(data:&[Complex],l:usize,m:i32)->Complex{
    if m>=0{return data[off(l,m as usize)];}
    let v=data[off(l,(-m) as usize)].conj();if m%2!=0{v.scale(-1.)}else{v}
}
fn run(inp:&str)->Result<String,String>{
    let mut it=inp.split_ascii_whitespace();
    let nr=count(&mut it)?;let nt=count(&mut it)?;let lmax=count(&mut it)?;
    if nr==0||nr>100_000||nt==0||nt>500||lmax>4{return Err("invalid ray/time/lmax cardinality".into());}
    let mut rays=Vec::with_capacity(nr);let mut total=0.;
    for _ in 0..nr{
        let mass=bit(&mut it)?;if mass<=0.{return Err("nonpositive stored ray mass".into());}
        let n=[bit(&mut it)?,bit(&mut it)?,bit(&mut it)?];
        if n.iter().any(|x|*x<0.)|| (n.iter().map(|x|x*x).sum::<f64>()-1.).abs()>1e-11{return Err("invalid positive-octant unit ray".into());}
        total+=mass;rays.push(Ray{mass,n});
    }
    if (total-0.9).abs()>5e-12{return Err("frozen six-cell source mass mismatch".into());}
    let mut times=Vec::with_capacity(nt);let mut prev=-1.;
    for _ in 0..nt{
        let u=bit(&mut it)?;let ell=[bit(&mut it)?,bit(&mut it)?,bit(&mut it)?];
        let h=[bit(&mut it)?,bit(&mut it)?,bit(&mut it)?];
        if !(0.0..=0.08).contains(&u)||u<=prev{return Err("out-of-order proper-time input".into());}
        prev=u;times.push((u,ell,h));
    }
    if it.next().is_some(){return Err("unexpected trailing tokens".into());}
    let mut out=String::new();out.push_str("u,E,Eprime,P1,P1prime,P2,P2prime,P3,P3prime,trace_gap,continuity_gap");
    for l in 0..=lmax{for m in -(l as i32)..=(l as i32){
        out.push_str(&format!(",a_{l}_{m}_re,a_{l}_{m}_im,da_{l}_{m}_re,da_{l}_{m}_im"));
    }}out.push('\n');
    for (u,ell,h) in times{
        let r=compute(ell,h,&rays,lmax)?;
        out.push_str(&format!("{u:.17e},{:.17e},{:.17e}",r.energy,r.energy_dot));
        for i in 0..3{out.push_str(&format!(",{:.17e},{:.17e}",r.p[i],r.p_dot[i]));}
        out.push_str(&format!(",{:.17e},{:.17e}",r.trace_gap,r.continuity_gap));
        for l in 0..=lmax{for m in -(l as i32)..=(l as i32){
            let a=signed_complex(&r.a,l,m);let d=signed_complex(&r.adot,l,m);
            out.push_str(&format!(",{:.17e},{:.17e},{:.17e},{:.17e}",a.re,a.im,d.re,d.im));
        }}out.push('\n');
    }Ok(out)
}
fn main(){
    if std::env::args().nth(1).as_deref()==Some("--selftest"){
        let rays=[Ray{mass:0.9,n:[1.,0.,0.]}];
        let r=compute([0.;3],[0.5;3],&rays,4).unwrap();
        assert!((r.energy-0.9).abs()<4e-15);
        assert!((r.energy_dot+1.8).abs()<4e-15);
        assert!(r.trace_gap<1e-14 && r.continuity_gap<1e-14);
        assert!((r.adot[0].re+(2.0*0.9)/(4.0*PI).sqrt()).abs()<1e-14);
        let pole=harmonic_and_derivative(4,4,[0.,0.,1.],[0.,0.,0.]);
        assert!(pole.0.re.abs()<1e-14&&pole.1.re.abs()<1e-14);
        let bad=[Ray{mass:-0.9,n:[1.,0.,0.]}];
        assert!(compute([0.;3],[0.5;3],&bad,4).is_err()); // Invalid negative weight is never allowed.
        println!("CE1R_BASS_RUST_LIOUVILLE_SELFTEST_PASS");return;
    }
    let mut input=String::new();io::stdin().read_to_string(&mut input).expect("stdin");
    match run(&input){Ok(x)=>print!("{x}"),Err(e)=>{eprintln!("CE1R_RUST_REJECT: {e}");std::process::exit(2);}}
}
