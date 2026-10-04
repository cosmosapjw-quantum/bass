use bianchi_rustcore::microphysics::{
    frame::MaterialFrame,
    rei_visibility::{electron_state_from_ft03, electron_state_from_hhe, integrate_rei_visibility, ReiOpacityCell, ReiVisibilityError},
    visibility::{C_M_S, SIGMA_T_M2},
};
use rei_microphysics::{ft03_rhs, Ft03Model, HHeModel, HHeState};

fn fixture() -> (HHeModel, HHeState) {
    let g = HHeModel::controlled_fixture();
    (g, HHeState::controlled_fixture(&g))
}
fn close(a: f64, b: f64) { assert!((a-b).abs() <= 3e-14 * a.abs().max(b.abs()).max(1e-300), "{a:e} != {b:e}"); }
fn rest() -> MaterialFrame { MaterialFrame::new([0.0;3]).unwrap() }

#[test]
fn source_density_has_exact_unit_and_charge_weights() {
    let (mut g, mut s) = fixture(); g.n_h_cm3=2.0;g.n_he_cm3=3.0;s.fractions=[0.5,0.25,0.5];
    let n=electron_state_from_hhe(&g,&s).unwrap().number_density_m3();
    assert_eq!(n,4.75e6); close(n,g.electron_density(&s).unwrap()*1e6);
}
#[test]
fn neutral_and_absent_element_edges_follow_source_domain() {
    let (mut g,mut s)=fixture();s.fractions=[0.0;3];
    assert_eq!(electron_state_from_hhe(&g,&s).unwrap().number_density_m3(),0.0);
    g.n_he_cm3=0.0;s.fractions=[1.0,0.0,0.0];
    assert_eq!(electron_state_from_hhe(&g,&s).unwrap().number_density_m3(),100.0);
    g.n_h_cm3=0.0;assert!(matches!(electron_state_from_hhe(&g,&s),Err(ReiVisibilityError::Source(_))));
}
#[test]
fn complete_source_state_and_model_are_validated_even_when_neutral() {
    let (g,mut s)=fixture();s.fractions=[0.0;3];
    for i in 0..3 {let mut bad=s;bad.photon_cm3[i]=-1.0;assert!(electron_state_from_hhe(&g,&bad).is_err());}
    s.u_erg_cm3=f64::NAN;assert!(electron_state_from_hhe(&g,&s).is_err());
    let (_,s)=fixture();let mut bad=g;bad.alpha_cm3_s[0]=-1.0;assert!(electron_state_from_hhe(&bad,&s).is_err());
    bad=g;bad.c_cm_s=0.0;assert!(electron_state_from_hhe(&bad,&s).is_err());
}
#[test]
fn conversion_overflow_is_reported_before_neutral_shortcut() {
    let (mut g,mut s)=fixture();g.n_h_cm3=1e303;g.n_he_cm3=0.0;s.fractions=[0.0;3];
    assert!(g.electron_density(&s).is_ok());
    assert!(matches!(electron_state_from_hhe(&g,&s),Err(ReiVisibilityError::DensityConversionOverflow)));
}
#[test]
fn ft03_density_snapshot_does_not_certify_temperature_rhs() {
    let g=Ft03Model::controlled().unwrap();let mut s=g.initial_state();s.u_erg_cm3=0.0;
    assert!(electron_state_from_ft03(&g,&s).is_ok());assert!(ft03_rhs(&g,&s).is_err());
    s.photon_cm3[1]=f64::NAN;assert!(electron_state_from_ft03(&g,&s).is_err());
}
#[test]
fn varying_snapshot_frame_and_direction_use_d_once() {
    let (g,s)=fixture();let f=Ft03Model::controlled().unwrap();let fs=f.initial_state();
    let moving=MaterialFrame::new([0.6,0.0,0.0]).unwrap();
    let cells=[ReiOpacityCell::HHe{model:&g,state:&s,frame:moving,e_normal:[1.0,0.0,0.0]},ReiOpacityCell::Ft03{model:&f,state:&fs,frame:moving,e_normal:[-1.0,0.0,0.0]}];
    let r=integrate_rei_visibility(&[0.0,2.0,5.0],&cells,0.4).unwrap();
    for (i,d) in [0.5,2.0].into_iter().enumerate(){close(r.interval_rates_s_inverse[i],r.electron_density_m3[i]*C_M_S*SIGMA_T_M2*d);}
    assert_eq!(r.visibility.optical_depth[2],0.4);
    close(r.visibility.survival[0]+r.visibility.interval_probability.iter().sum::<f64>(),(-0.4_f64).exp());
}
#[test]
fn neutral_snapshot_does_not_bypass_direction_check() {
    let(g,mut s)=fixture();s.fractions=[0.0;3];
    let c=ReiOpacityCell::HHe{model:&g,state:&s,frame:rest(),e_normal:[0.0;3]};
    assert!(integrate_rei_visibility(&[0.0,1.0],&[c],0.0).is_err());
}
#[test]
fn grid_tail_and_nonfinite_cell_width_follow_host_validation() {
    let(g,s)=fixture();let c=ReiOpacityCell::HHe{model:&g,state:&s,frame:rest(),e_normal:[1.0,0.0,0.0]};
    for (e,t) in [(vec![],0.0),(vec![0.0,1.0,2.0],0.0),(vec![1.0,0.0],0.0),(vec![0.0,f64::NAN],0.0),(vec![-f64::MAX,f64::MAX],0.0),(vec![0.0,1.0],-1.0),(vec![0.0,1.0],f64::INFINITY)]{assert!(integrate_rei_visibility(&e,&[c],t).is_err());}
}
#[test]
fn source_speed_is_not_reused_as_a_second_opacity_constant() {
    let(mut g,s)=fixture();g.c_cm_s*=2.0;
    let c=ReiOpacityCell::HHe{model:&g,state:&s,frame:rest(),e_normal:[1.0,0.0,0.0]};
    let r=integrate_rei_visibility(&[0.0,1.0],&[c],0.0).unwrap();
    close(r.interval_rates_s_inverse[0],r.electron_density_m3[0]*C_M_S*SIGMA_T_M2);
}
#[test]
fn independent_element_models_are_used_per_cell() {
    let(g,s)=fixture();let mut g2=g;g2.n_h_cm3*=3.0;g2.n_he_cm3*=5.0;
    let cells=[ReiOpacityCell::HHe{model:&g,state:&s,frame:rest(),e_normal:[1.0,0.0,0.0]},ReiOpacityCell::HHe{model:&g2,state:&s,frame:rest(),e_normal:[1.0,0.0,0.0]}];
    let r=integrate_rei_visibility(&[0.0,1.0,2.0],&cells,0.0).unwrap();
    close(r.electron_density_m3[1],g2.electron_density(&s).unwrap()*1e6);
    assert_ne!(r.electron_density_m3[0],r.electron_density_m3[1]);
}
