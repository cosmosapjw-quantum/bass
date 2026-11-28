// Cancellation-free B3 quadratic coefficient of the C3X midpoint/Strang map.
use std::io::{Read,BufReader};
type V=[f64;5];
type B=[f64;14];
#[derive(Clone,Copy)]struct State{s:V,b:V,i:V,p:V,bb:B,comp:B}
fn take(r:&mut impl Read)->f64{let mut a=[0;8];r.read_exact(&mut a).unwrap();f64::from_le_bytes(a)}
fn add(a:V,b:V,c:f64)->V{std::array::from_fn(|k|a[k]+c*b[k])}
fn bil(j:&[[[f64;5];5];14],s:V,p:V)->B{std::array::from_fn(|k|{let mut sum=0.;let mut c=0.;for i in 0..5{for l in 0..5{let v=j[k][i][l]*s[i]*p[l];let y=v-c;let t=sum+y;c=(t-sum)-y;sum=t;}}sum})}
fn acc(x:&mut State,a:B,c:f64){for k in 0..14{let y=c*a[k]-x.comp[k];let t=x.bb[k]+y;x.comp[k]=(t-x.bb[k])-y;x.bb[k]=t;}}
fn stream(mut x:State,s:V,d:f64,tau:f64,j:&[[[f64;5];5];14])->State{
 let hh=d/2.;x.i=add(x.i,s,-4.*hh);let a=bil(j,s,x.p);acc(&mut x,a,hh);
 let e=(-tau).exp();let f=(-0.3*tau).exp()*(-(-0.7*tau).exp_m1())/0.7;
 let old=x.i;for k in 0..5{x.i[k]=e*old[k]+f*(0.1*old[k]-0.4*x.p[k]);x.p[k]=e*x.p[k]+f*(-0.15*old[k]+0.6*x.p[k]);}
 for k in 0..14{x.bb[k]*=e;x.comp[k]*=e;}let a=bil(j,s,x.p);acc(&mut x,a,hh);x.i=add(x.i,s,-4.*hh);x
}
#[derive(Clone,Copy)]struct Stage{rho:f64,tr:f64,g:f64,j:[f64;6],rad:f64,ne:f64}
fn stage(r:&mut impl Read)->Stage{Stage{rho:take(r),tr:take(r),g:take(r),j:std::array::from_fn(|_|take(r)),rad:take(r),ne:take(r)}}
fn rhs(a:Stage,h:f64,x:State,ctrl:&[[f64;7];5],ol:f64)->(f64,V){let h2=h*h;let q=(a.rho+a.tr-2.*ol)/(2.*h2);(q,std::array::from_fn(|k|{let src=(0..6).map(|v|a.j[v]*ctrl[k][v+1]).sum::<f64>();let stress=src-a.g*x.b[k]+a.rad*x.i[k];(q-2.)*x.s[k]+3.*stress/h2}))}
fn main(){
 let a:Vec<_>=std::env::args().collect();assert!(a.len()==2);
 let mut r=BufReader::new(std::fs::File::open(&a[1]).unwrap());let n=take(&mut r) as usize;let nc=take(&mut r) as usize;let ol=take(&mut r);let k0=take(&mut r);
 let j:[[[f64;5];5];14]=std::array::from_fn(|_|std::array::from_fn(|_|std::array::from_fn(|_|take(&mut r))));
 let cs:Vec<[[f64;7];5]>=(0..nc).map(|_|std::array::from_fn(|_|std::array::from_fn(|_|take(&mut r)))).collect();
 let mut xs:Vec<State>=cs.iter().map(|c|State{s:std::array::from_fn(|k|c[k][0]),b:[0.;5],i:[0.;5],p:[0.;5],bb:[0.;14],comp:[0.;14]}).collect();let mut h=0.;
 for k in 0..n{let dt=take(&mut r);let a=stage(&mut r);let m=stage(&mut r);if k==0{h=(a.rho+ol).sqrt();}
 let q=(a.rho+a.tr-2.*ol)/(2.*h*h);let hm=h*(-dt/2.*(1.+q)).exp();let qm=(m.rho+m.tr-2.*ol)/(2.*hm*hm);
 for (x,c) in xs.iter_mut().zip(cs.iter()){
 let (_,f)=rhs(a,h,*x,c,ol);let sm=add(x.s,f,dt/2.);let bm=add(x.b,x.s,dt/2.);
 let mut mid=stream(*x,x.s,dt/2.,k0*(a.ne+m.ne)/2./h*dt/2.,&j);mid.s=sm;mid.b=bm;
 let (_,fm)=rhs(m,hm,mid,c,ol);let mut y=stream(*x,sm,dt,k0*m.ne/hm*dt,&j);y.s=add(x.s,fm,dt);y.b=add(x.b,sm,dt);*x=y;
 }
 h*=(-dt*(1.+qm)).exp();
 }
 let mut b=[0;1];assert_eq!(r.read(&mut b).unwrap(),0);println!("h,{h:.17e}");for(k,x)in xs.iter().enumerate(){print!("{k}");for v in x.bb{print!(",{v:.17e}");}println!();}
}
#[cfg(test)]mod tests{use super::*;#[test]fn zero_and_collision(){let j=[[[0.;5];5];14];let x=State{s:[0.;5],b:[0.;5],i:[1.;5],p:[0.;5],bb:[1.;14],comp:[0.;14]};let y=stream(x,x.s,0.1,0.3,&j);assert!((y.bb[0]-(-0.3_f64).exp()).abs()<1e-15);assert!(y.p[0]<0.);assert!(y.i[0]<1.);}}
