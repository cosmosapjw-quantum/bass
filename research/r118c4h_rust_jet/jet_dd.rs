//! C4H double-double coefficient kernel. Stage tables carry hi+lo components.
use std::{io::{Read,BufReader},ops::{Add,Sub,Mul,Div,Neg}};
#[derive(Clone,Copy,Debug,Default)]struct D(f64,f64);
impl D{
 const Z:Self=Self(0.,0.);const ONE:Self=Self(1.,0.);
 fn val(self)->f64{self.0+self.1}
 fn sum(a:f64,b:f64)->Self{let s=a+b;let z=s-a;Self(s,(a-(s-z))+(b-z))}
 fn rat(a:f64,b:f64)->Self{Self(a,0.)/Self(b,0.)}
 fn sqrt(self)->Self{let v=Self(self.0.sqrt(),0.);v+(self-v*v)/(2.*v)}
 fn em1(self)->Self{assert!(self.0.abs()<0.5,"Taylor small-exponent domain");let mut term=self;let mut z=term;for k in 2..=28{term=term*self/(k as f64);z=z+term;}z}
 fn exp(self)->Self{Self::ONE+self.em1()}
}
impl Add for D{type Output=Self;fn add(self,b:Self)->Self{let a=Self::sum(self.0,b.0);Self::sum(a.0,a.1+self.1+b.1)}}
impl Neg for D{type Output=Self;fn neg(self)->Self{Self(-self.0,-self.1)}}
impl Sub for D{type Output=Self;fn sub(self,b:Self)->Self{self+(-b)}}
impl Mul for D{type Output=Self;fn mul(self,b:Self)->Self{let p=self.0*b.0;let e=self.0.mul_add(b.0,-p)+self.0*b.1+self.1*b.0+self.1*b.1;Self::sum(p,e)}}
impl Div for D{type Output=Self;fn div(self,b:Self)->Self{let q=Self(self.0/b.0,0.);let r=self-b*q;Self::sum(q.0,r.val()/b.0)}}
impl Mul<f64> for D{type Output=D;fn mul(self,b:f64)->D{self*D(b,0.)}}
impl Mul<D> for f64{type Output=D;fn mul(self,b:D)->D{D(self,0.)*b}}
impl Div<f64> for D{type Output=D;fn div(self,b:f64)->D{self/D(b,0.)}}
type V=[D;5];type B=[D;14];
#[derive(Clone,Copy)]struct State{s:V,b:V,i:V,p:V,bb:B}
fn read_f(r:&mut impl Read)->f64{let mut b=[0;8];r.read_exact(&mut b).unwrap();f64::from_le_bytes(b)}
fn take(r:&mut impl Read)->D{D(read_f(r),read_f(r))}
fn add(a:V,b:V,c:D)->V{std::array::from_fn(|i|a[i]+c*b[i])}
fn bil(j:&[[[D;5];5];14],s:V,p:V)->B{std::array::from_fn(|k|{let mut a=D::Z;for i in 0..5{for l in 0..5{a=a+j[k][i][l]*s[i]*p[l];}}a})}
fn stream(mut x:State,s:V,d:D,tau:D,j:&[[[D;5];5];14])->State{
 let hh=d/2.;x.i=add(x.i,s,-4.*hh);let a=bil(j,s,x.p);
 for k in 0..14{x.bb[k]=x.bb[k]+hh*a[k];}
 let p3=D::rat(3.,10.);let p7=D::rat(7.,10.);let e=(-tau).exp();let f=(-p3*tau).exp()*(-(-p7*tau).em1())/p7;
 let old=x.i;let p1=D::rat(1.,10.);let p4=D::rat(4.,10.);let p15=D::rat(15.,100.);let p6=D::rat(6.,10.);
 for k in 0..5{x.i[k]=e*old[k]+f*(p1*old[k]-p4*x.p[k]);x.p[k]=e*x.p[k]+f*(-p15*old[k]+p6*x.p[k]);}
 let a=bil(j,s,x.p);for k in 0..14{x.bb[k]=e*x.bb[k]+hh*a[k];}x.i=add(x.i,s,-4.*hh);x
}
#[derive(Clone,Copy)]struct Stage{rho:D,tr:D,g:D,j:[D;6],rad:D,ne:D}
fn stage(r:&mut impl Read)->Stage{Stage{rho:take(r),tr:take(r),g:take(r),j:std::array::from_fn(|_|take(r)),rad:take(r),ne:take(r)}}
fn rhs(a:Stage,h:D,x:State,c:&[[D;7];5],ol:D)->(D,V){let h2=h*h;let q=(a.rho+a.tr-2.*ol)/(2.*h2);(q,std::array::from_fn(|k|{let mut src=D::Z;for v in 0..6{src=src+a.j[v]*c[k][v+1];}let p=src-a.g*x.b[k]+a.rad*x.i[k];(q-D(2.,0.))*x.s[k]+3.*p/h2}))}
fn main(){
 let a:Vec<_>=std::env::args().collect();let mut r=BufReader::new(std::fs::File::open(&a[1]).unwrap());let n=take(&mut r).val() as usize;let nc=take(&mut r).val() as usize;let ol=take(&mut r);let k0=take(&mut r);
 let j:[[[D;5];5];14]=std::array::from_fn(|_|std::array::from_fn(|_|std::array::from_fn(|_|take(&mut r))));
 let cs:Vec<[[D;7];5]>=(0..nc).map(|_|std::array::from_fn(|_|std::array::from_fn(|_|take(&mut r)))).collect();
 let mut xs:Vec<State>=cs.iter().map(|c|State{s:std::array::from_fn(|k|c[k][0]),b:[D::Z;5],i:[D::Z;5],p:[D::Z;5],bb:[D::Z;14]}).collect();let mut h=D::Z;
 for k in 0..n{let dt=take(&mut r);let a=stage(&mut r);let m=stage(&mut r);if k==0{h=(a.rho+ol).sqrt();}
 let q=(a.rho+a.tr-2.*ol)/(2.*h*h);let hm=h*(-dt/2.*(D::ONE+q)).exp();let qm=(m.rho+m.tr-2.*ol)/(2.*hm*hm);
 for (x,c) in xs.iter_mut().zip(cs.iter()){
 let (_,f)=rhs(a,h,*x,c,ol);let sm=add(x.s,f,dt/2.);let bm=add(x.b,x.s,dt/2.);
 let mut mid=stream(*x,x.s,dt/2.,k0*(a.ne+m.ne)/2./h*dt/2.,&j);mid.s=sm;mid.b=bm;
 let (_,fm)=rhs(m,hm,mid,c,ol);let mut y=stream(*x,sm,dt,k0*m.ne/hm*dt,&j);y.s=add(x.s,fm,dt);y.b=add(x.b,sm,dt);*x=y;
 }
 h=h*(-dt*(D::ONE+qm)).exp();
 }
 let mut b=[0;1];assert_eq!(r.read(&mut b).unwrap(),0);println!("h,{:.17e}",h.val());for(k,x)in xs.iter().enumerate(){print!("{k}");for v in x.bb{print!(",{:.17e}",v.val());}println!();}
}
#[cfg(test)]mod tests{use super::*;#[test]fn retains_small_delta(){let a=D::ONE+D(1e-24,0.);assert!(((a-D::ONE).val()-1e-24).abs()<1e-38);}
#[test]fn exp_series(){let a=D::rat(-1.,10.);let y=a.exp()*(-a).exp();assert!((y-D::ONE).val().abs()<1e-28);}}
