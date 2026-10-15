use rei_microphysics::igm_background::{FlatFlrwBackground,FlatFlrwConfig};
fn fail() -> ! {panic!("SOURCE_COSMO_INVALID")}
fn main(){
 let a:Vec<String>=std::env::args().skip(1).collect();if a.len()!=10{fail();}
 let f=|i:usize|->f64{a[i].parse().unwrap_or_else(|_|fail())};
 let h0=f(0);let om=f(1);let or=f(2);let ol=f(3);let ob=f(4);
 let y=f(5);let tcmb=f(6);let ar=f(7);let ae=f(8);
 let points:usize=a[9].parse().unwrap_or_else(|_|fail());
 let config=FlatFlrwConfig{h0_per_s:h0,omega_m:om,omega_r:or,omega_lambda:ol,
  omega_b:ob,helium_mass_fraction:y,tcmb0_k:tcmb,ln_a_min:ar.ln(),
  ln_a_max:ae.ln(),parameter_source:"original REI AX03 family lock from BASS source parity".into()};
 let bg=FlatFlrwBackground::new(config).unwrap();
 println!("index,a,zbar,H,n_H_cm3,n_He_cm3,Tbar_CMB_K,dt_dln_a_s");
 for i in 0..points{
  let f=i as f64/(points-1) as f64;
  let x=if i==0{ar.ln()}else if i==points-1{ae.ln()}else{ar.ln()+f*(ae.ln()-ar.ln())};
  let p=bg.at_ln_a(x).unwrap();
  println!("{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
   i,p.a,p.redshift,p.hubble_per_s,p.n_h_cm3,p.n_he_cm3,p.tcmb_k,p.dt_dln_a_s);
 }
}
