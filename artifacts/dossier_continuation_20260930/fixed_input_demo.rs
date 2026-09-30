use bianchi_rustcore::microphysics::frame::MaterialFrame;
use bianchi_rustcore::microphysics::visibility::{ElectronState,integrate_visibility};
use bianchi_rustcore::microphysics::population::FrozenPopulation;
use bianchi_rustcore::kinetic::realizability::{check_moments,MomentKind};
fn main(){
 let electrons=ElectronState::new(200.0,16.0,1.0,0.5,0.5).unwrap();
 let frame=MaterialFrame::new([0.6,0.0,0.0]).unwrap();
 println!("fixed_input_only; densities=m^-3; time=normal_seconds; beta_x=0.6");
 println!("electron_density={:.12e}",electrons.number_density_m3());
 for (name,d) in [("parallel",[1.0,0.0,0.0]),("antiparallel",[-1.0,0.0,0.0])]{let q=electrons.scattering_rate_per_normal_second(frame,d).unwrap();let v=integrate_visibility(&[0.0,1e17],&[q],0.0).unwrap();println!("{name}: q={q:.12e}; tau={:.12e}; scattered_mass={:.12e}; unscattered={:.12e}",v.optical_depth[0],v.interval_probability[0],v.survival[0]);}
 let moments=check_moments(3.0,[0.0;3],[[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]],MomentKind::Photons,1e-12).unwrap();println!("isotropic_photon_necessary_conditions={}",moments.admissible);
 let g=FrozenPopulation::new(&[2.0,1.0],&[vec![0.0,3.0],vec![1.0,0.0]]).unwrap();let a=g.advance(&[0.5,0.0],0.5,24).unwrap();println!("population={:?}; weighted_inventory={:.16}; truncation_bound={:.12e}",a.populations,2.0*a.populations[0]+a.populations[1],a.weighted_l1_error_bound);
}
