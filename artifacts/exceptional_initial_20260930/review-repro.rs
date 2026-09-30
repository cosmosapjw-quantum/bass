use bianchi_rustcore::geom::exceptional_initial::{CauchyData,ExceptionalGeometry,Expansion};
fn main(){
 let a=2_f64.powi(500);let b=2_f64.powi(1020);let c=3.0*a;let d=2_f64.powi(-100);
 let g=ExceptionalGeometry::new(a,b,c,d,2e-13).unwrap();
 let x=g.solve_transverse([0.0,0.0],1.0,1.0).unwrap();
 println!("normalization: shear={:?} reported={:?} actual_first={}",x.shear,x.constraint_residual,-(3.0*a+c)*x.shear[0]-d*x.shear[1]);
 let g=ExceptionalGeometry::new(1.0,0.0,3.0+1e-7,0.0,1e-6).unwrap();
 let data=CauchyData{in_plane:[0.0;3],flux:[0.0;3],kappa:1.0,rho:0.0,lambda:0.0};
 let chi2=g.amplitude_budget(data,3.0).unwrap();
 println!("nearbranch: budget={} construction={:?}",chi2,g.initial_data(data,chi2.sqrt(),Expansion::Expanding));
}
