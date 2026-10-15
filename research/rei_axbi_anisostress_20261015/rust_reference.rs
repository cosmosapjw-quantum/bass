//! Independent source-parametrized stdlib-only LRS Einstein-Vlasov RK4.
 //! No native rei_bianchi solver integration. Validates Python DOP853 and
 //! original REI source parameters, 64-point angular Gaussian quadrature.
use std::env;
use std::f64::consts::PI;
fn error(msg:&str)->!{eprintln!("AXBI_PI_NATIVE_REJECT:{msg}");std::process::exit(3)}
fn parse(s:&str)->f64{
 let v=s.parse::<f64>().unwrap_or_else(|_|error("BAD_COSMO_PARAMETER"));
 if !v.is_finite(){error("NONFINITE")}v
}
#[derive(Clone,Copy)]
struct Bg {h0:f64,om:f64,orad:f64,ol:f64,ar:f64,ae:f64}
#[derive(Clone,Copy)]
struct Init{q:f64,ampl:f64,eta:f64}
#[derive(Clone,Copy)]
struct State{tau:f64,b:f64,u:f64}
impl State{
 fn scaled_add(self,v:State,h:f64)->Self{
  Self{tau:self.tau+h*v.tau,b:self.b+h*v.b,u:self.u+h*v.u}
 }
}
fn gauss64_positive()->Vec<(f64,f64)>{
 let mut nodes=Vec::with_capacity(32);
 for idx in 1..=32{
  let mut z=(PI*(idx as f64-0.25)/64.5).cos();
  let mut pp=0.0;
  for _ in 0..15{
   let mut p0=1.0;let mut p1=z;
   for n in 2..=64{
    let p=((2*n-1) as f64*z*p1-(n-1) as f64*p0)/(n as f64);
    p0=p1;p1=p;
   }
   pp=64.0*(z*p1-p0)/(z*z-1.0);
   let next=z-p1/pp;
   if (next-z).abs()<3e-16{z=next;break}
   z=next;
  }
  // Full n=64 Legendre weights w_i, whose positive-nodes sum is 1.
  let w=2.0/((1.0-z*z)*pp*pp);
  nodes.push((z,w));
 }
 let mass:f64=nodes.iter().map(|a|a.1).sum();
 if (mass-1.0).abs()>3e-13{error("GAUSS_WEIGHT_SOURCE_DRIFT")}
 nodes
}
fn moments(b:f64,amp:f64, nodes:&[(f64,f64)])->(f64,f64){
 let mut m0=0.0;let mut md=0.0;
 let e2=(2.0*b).exp();let e4=(-4.0*b).exp();
 for &(mu,w) in nodes{
  let mu2=mu*mu;
  let rsq=e2*(1.0-mu2)+e4*mu2;
  let r=rsq.sqrt();
  let mut curmu2=e4*mu2/rsq;
  curmu2=curmu2.clamp(0.0,1.0);
  let p2=0.5*(3.0*mu2-1.0);
  let weight=w*(1.0+amp*p2)*r;
  m0+=weight;md+=weight*0.5*(3.0*curmu2-1.0);
 }
 (m0,md)
}
fn href(cfg:Bg)->f64{cfg.h0*(cfg.om/cfg.ar.powi(3)+cfg.orad/cfg.ar.powi(4)+cfg.ol).sqrt()}
fn rates(x:f64,y:State,bg:Bg,ini:Init,nodes:&[(f64,f64)])->State{
 let hr=href(bg);let a=bg.ar*x.exp();let shear=hr*y.u;
 let (m0,md)=moments(y.b,ini.ampl,nodes);
 let h2=bg.h0*bg.h0*(bg.om/a.powi(3)+bg.ol+
  bg.orad/a.powi(4)*((1.0-ini.eta)+ini.eta*m0))+shear*shear;
 let h=h2.sqrt();
 let d=bg.h0*bg.h0*ini.eta*bg.orad/a.powi(4);
 State{tau:hr/h,b:hr*y.u/h,u:-3.0*y.u+(d/(hr*h))*md}
}
fn sample(x:f64,y:State,bg:Bg,ini:Init,nodes:&[(f64,f64)])->(f64,f64,f64,f64){
 let a=bg.ar*x.exp();let hr=href(bg);
 let (m0,md)=moments(y.b,ini.ampl,nodes);
 let s=hr*y.u;
 let h=(bg.h0*bg.h0*(bg.om/a.powi(3)+bg.ol+
  bg.orad/a.powi(4)*((1.0-ini.eta)+ini.eta*m0))+s*s).sqrt();
 (s/h,h,m0,md)
}
fn integrate(cfg:Bg,ini:Init,nodes:&[(f64,f64)],n:usize)->(State,f64,f64,f64,f64){
 if ini.eta<0.0||ini.eta>1.0||ini.ampl < -1.0||ini.ampl>2.0{error("NEGATIVE_COLLISIONLESS_DISTRIBUTION")}
 let span=(cfg.ae/cfg.ar).ln();let dx=span/n as f64;
 let mut y=State{tau:0.0,b:0.0,u:ini.q};
 for i in 0..n{
  let x=i as f64*dx;
  let a=rates(x,y,cfg,ini,nodes);
  let b=rates(x+dx/2.0,y.scaled_add(a,dx/2.0),cfg,ini,nodes);
  let c=rates(x+dx/2.0,y.scaled_add(b,dx/2.0),cfg,ini,nodes);
  let d=rates(x+dx,y.scaled_add(c,dx),cfg,ini,nodes);
  y=State{
   tau:y.tau+dx*(a.tau+2.0*b.tau+2.0*c.tau+d.tau)/6.0,
   b:y.b+dx*(a.b+2.0*b.b+2.0*c.b+d.b)/6.0,
   u:y.u+dx*(a.u+2.0*b.u+2.0*c.u+d.u)/6.0
  };
 }
 let (s_h,h,m0,md)=sample(span,y,cfg,ini,nodes);
 (y,s_h,h,m0,md)
}
fn main(){
 let args:Vec<String>=env::args().skip(1).collect();
 if args.len()!=7{error("ARG_H0_OM_OR_OL_AREF_AEND_STEPS")}
 let bg=Bg{h0:parse(&args[0]),om:parse(&args[1]),orad:parse(&args[2]),
  ol:parse(&args[3]),ar:parse(&args[4]),ae:parse(&args[5])};
 let steps=args[6].parse::<usize>().unwrap_or_else(|_|error("BAD_STEPS"));
 if steps<16||steps>65536{error("STEPS_DOMAIN")}
 let nodes=gauss64_positive();
 let cases=[
 Init{q:0.0,ampl:0.0,eta:0.0},Init{q:0.0,ampl:1.0,eta:1.0},
 Init{q:0.0,ampl:-1.0,eta:1.0},Init{q:0.01,ampl:0.0,eta:0.0},
 Init{q:0.01,ampl:0.0,eta:1.0},Init{q:0.01,ampl:1.0,eta:1.0},
 Init{q:0.01,ampl:-1.0,eta:1.0},Init{q:0.01,ampl:1.0,eta:0.2}
 ];
 println!("q_ref,A,eta,dt_s,b_end,s_over_H_end,H_end,M0_end,Mdelta_end");
 for ini in cases{
  let (y,s_h,h,m0,md)=integrate(bg,ini,&nodes,steps);
  println!("{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
   ini.q,ini.ampl,ini.eta,y.tau/href(bg),y.b,s_h,h,m0,md);
 }
}
