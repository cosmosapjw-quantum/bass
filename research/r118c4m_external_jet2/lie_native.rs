use bianchi_rustcore::{geom::lie::{LieData,canonical_algebra,photon_potentials},kinetic::{lie_hierarchy::LieHierarchy,spin_sht::{index,C64}}};
use nalgebra::Matrix3;
type V=Vec<Vec<C64>>;
fn ax(a:&V,b:&V,c:f64)->V{a.iter().zip(b).map(|(x,y)|x.iter().zip(y).map(|(x,y)|*x+c*y).collect()).collect()}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let h=LieHierarchy::new(8,true,4.)?;let base=h.zero_state();let mut y=base.clone();y[0][0]=C64::new((4.*std::f64::consts::PI).sqrt(),0.);y[0][index(2,0)]=C64::new(0.012,0.);y[1][index(2,0)]=C64::new(-0.003,0.);y[2][index(2,0)]=C64::new(-0.003,0.);
 let dt=0.013;println!("family,eps,primal_gap,first_rel,second_rel,B3second_norm");
 for family in ["I","II","III","IV","V","VI0","VIstar","VII0","VIh:-0.25","VIIh:0.25","VIII","IX"]{
  let(n,a)=canonical_algebra(family,0.1,&Matrix3::identity())?;
  let d=LieData{shear:[[0.02,0.003,-0.005],[0.003,-0.012,0.002],[-0.005,0.002,-0.008]],n,a,rotation:[0.;3]};
  let pot=photon_potentials(&d);let norm=|x:&V|x.iter().flatten().map(|v|v.norm_sqr()).sum::<f64>().sqrt();
  let rhs=|u:&[V;3]|->[V;3]{let mut v=std::array::from_fn(|_|h.zero_state());let mut t=h.zero_state();h.rhs(&pot,&u[0],&mut v[0]);h.rhs(&pot,&u[1],&mut v[1]);v[1]=ax(&v[1],&v[0],1.);h.rhs(&pot,&u[2],&mut v[2]);h.rhs(&pot,&u[1],&mut t);v[2]=ax(&v[2],&t,1.);v};
  let x=[y.clone(),base.clone(),base.clone()];let add=|k:&[V;3],c:f64|std::array::from_fn(|i|ax(&x[i],&k[i],c));
  let k1=rhs(&x);let k2=rhs(&add(&k1,dt/2.));let k3=rhs(&add(&k2,dt/2.));let k4=rhs(&add(&k3,dt));
  let z:[V;3]=std::array::from_fn(|i|ax(&x[i],&ax(&ax(&k1[i],&k2[i],2.),&ax(&k4[i],&k3[i],2.),1.),dt/6.));
  let run=|p:f64|->Result<V,String>{let s=1.+p;let v=LieData{shear:d.shear.map(|r|r.map(|x|s*x)),n:d.n.map(|r|r.map(|x|s*x)),a:d.a.map(|x|s*x),rotation:[0.;3]};let mut w=y.clone();h.stream_centered(&mut w,&v,&v,dt)?;Ok(w)};
  let z0=run(0.)?;let gap=norm(&ax(&z[0],&z0,-1.));let b3=( -3..=3).map(|m|{let k=index(3,m);(z[2][1][k]-z[2][2][k]).norm_sqr()/4.}).sum::<f64>().sqrt();
  for e in [0.01,0.003,0.001]{let p=run(e)?;let m=run(-e)?;let a=ax(&p,&m,-1.);let b=ax(&ax(&p,&m,1.),&z0,-2.);
   let a=a.iter().map(|v|v.iter().map(|x|*x/(2.*e)).collect()).collect();let b=b.iter().map(|v|v.iter().map(|x|*x/(2.*e*e)).collect()).collect();
   println!("{family},{e:.17e},{gap:.17e},{:.17e},{:.17e},{b3:.17e}",norm(&ax(&z[1],&a,-1.))/norm(&z[1]),norm(&ax(&z[2],&b,-1.))/norm(&z[2]));}
 }Ok(())
}
