use rei_microphysics::flrw_three_equations::*;
use rei_microphysics::RecombinationCase;
fn near(a:f64,b:f64,scale:f64){assert!((a-b).abs()<=2e-12*scale.abs()+1e-30,"{a:.17e} != {b:.17e}; scale {scale:e}");}
fn unit(a:f64,b:f64){assert!((a-b).abs()<=2e-14,"{a:.17e} != {b:.17e}");}
fn input(n:f64,x:f64)->CellInput{CellInput{scale_factor:0.1,hubble_s:1e-16,temperature_k:1e4,
    n_h_proper_cm3:n,x_hii:x,case:RecombinationCase::A,include_collisions:false,
    photon_energy_ev:[20.0,35.0,70.0],photon_proper_cm3:[2e-5,2e-6,2e-7],
    source_proper_cm3_s:[3e-17,4e-18,5e-19],other_absorption_proper_cm3_s:[1e-18,2e-19,3e-20],
    edge_energy_ev:[13.598434599702,24.587389011,54.41776,200.0],edge_n_per_cm3_ev:[3e-8,2e-9,1e-10,2e-12]}}
fn empty_photons()->PhotonInput{PhotonInput{scale_factor:0.2,hubble_s:2e-16,
    comoving_photons_cm3:[1e-6,2e-6,3e-6],edge_energy_ev:[10.0,20.0,40.0,80.0],
    edge_n_per_cm3_ev:[0.0;4],source_proper_cm3_s:[0.0;3],absorption_proper_cm3_s:[0.0;3]}}
fn example_ensemble()->Ensemble{ensemble(&[(0.4,connected_cell(input(1e-4,0.1)).unwrap()),
    (0.6,connected_cell(input(4e-4,0.9)).unwrap())]).unwrap()}
#[test]
fn actual_event_rate_reduces_to_local_fraction_equation(){
    let mut i=input(2e-4,0.3);i.include_collisions=true;
    let c=connected_cell(i).unwrap();
    let rhs=(1.0-i.x_hii)*(c.gamma_hi_s+c.electron_proper_cm3*c.ci_cm3_s)
        -c.alpha_cm3_s*c.electron_proper_cm3*i.x_hii;
    near(c.x_dot_s,rhs,c.gamma_hi_s+c.alpha_cm3_s*c.electron_proper_cm3);
    near(c.n_h_proper_cm3*c.x_dot_s,c.photo_proper_cm3_s+c.collision_proper_cm3_s-c.recombination_proper_cm3_s,
         c.photo_proper_cm3_s+c.collision_proper_cm3_s+c.recombination_proper_cm3_s);
}
#[test]
fn c_mpc_photo_bridge_is_same_actual_event_count(){
    for a in [0.03,0.1,0.7,1.0]{let mut i=input(2e-4,0.3);i.scale_factor=a;
        let c=connected_cell(i).unwrap();near(c.photo_bridge_residual_proper_cm3_s,0.0,c.photo_proper_cm3_s);}
}
#[test]
fn fraction_has_no_expansion_dilution_term(){
    let mut i=input(2e-4,0.3);i.hubble_s=0.0;let zero=connected_cell(i).unwrap();
    i.hubble_s=1e-12;let expanded=connected_cell(i).unwrap();
    near(zero.x_dot_s,expanded.x_dot_s,zero.x_dot_s.abs());
    let mutant=expanded.x_dot_s-3.0*i.hubble_s*i.x_hii;
    assert!((mutant-zero.x_dot_s).abs()>1e-13);
}
#[test]
fn comoving_no_three_h_and_proper_dilution(){
    let i=empty_photons();let p=photon_balance(i).unwrap();
    assert_eq!(p.comoving_dot_cm3_s,[0.0;3]);
    for g in 0..3{near(p.proper_dot_cm3_s[g],-3.0*i.hubble_s*i.comoving_photons_cm3[g]/i.scale_factor.powi(3),1e-18);}
    assert!((-3.0*i.hubble_s*i.comoving_photons_cm3[0]).abs()>1e-23);
}
#[test]
fn shared_edges_telescope_and_keep_upper_inflow(){
    let mut i=empty_photons();i.scale_factor=1.0;i.hubble_s=0.5;
    i.edge_energy_ev=[1.0,2.0,4.0,8.0];i.edge_n_per_cm3_ev=[4.0,3.0,2.0,1.0];
    let p=photon_balance(i).unwrap();assert_eq!(p.edge_flux_comoving_cm3_s,[2.0,3.0,4.0,4.0]);
    assert_eq!(p.comoving_dot_cm3_s,[1.0,1.0,0.0]);assert_eq!(p.boundary_net_loss_comoving_cm3_s,-2.0);
    assert_eq!(p.summed_balance_residual,0.0);
    let wrong_drop_lower=4.0;assert!((wrong_drop_lower-p.comoving_dot_cm3_s.iter().sum::<f64>()).abs()>1.0);
}
#[test]
fn edge_energy_not_bin_center_enters_threshold_flux(){
    let i=input(1e-4,0.2);let c=connected_cell(i).unwrap();
    let exact=i.scale_factor.powi(3)*i.hubble_s*i.edge_energy_ev[0]*i.edge_n_per_cm3_ev[0];
    let mutant=i.scale_factor.powi(3)*i.hubble_s*i.photon_energy_ev[0]*i.edge_n_per_cm3_ev[0];
    near(c.photon.edge_flux_comoving_cm3_s[0],exact,exact);
    assert!((mutant-exact).abs()>0.4*exact);
}
#[test]
fn correlated_cells_separate_volume_and_mass_averages(){
    let e=ensemble(&[(0.5,connected_cell(input(1e-4,0.1)).unwrap()),
        (0.5,connected_cell(input(4e-4,0.9)).unwrap())]).unwrap();
    unit(e.x_volume,0.5);unit(e.x_mass,0.74);unit(e.density_ionization_covariance,0.24);
}
#[test]
fn recombination_average_does_not_factor_into_means(){
    let a=connected_cell(input(1e-4,0.1)).unwrap();let b=connected_cell(input(4e-4,0.9)).unwrap();
    let exact=0.5*(a.recombination_proper_cm3_s+b.recombination_proper_cm3_s);
    let mean_ne=0.5*(a.electron_proper_cm3+b.electron_proper_cm3);
    let mutant=a.alpha_cm3_s*mean_ne*mean_ne;
    assert!(exact>1.5*mutant);
}
#[test]
fn combined_inventory_cancels_actual_absorption(){
    let e=example_ensemble();
    let scale=e.source_per_h_s+e.recombination_per_h_s+e.collision_per_h_s+e.other_absorption_per_h_s+e.redshift_boundary_per_h_s.abs();
    near(e.combined_inventory_residual_s,0.0,scale);
    near(e.x_mass_dot_s+e.eta_dot_s,e.source_per_h_s-e.recombination_per_h_s+e.collision_per_h_s-e.other_absorption_per_h_s-e.redshift_boundary_per_h_s,scale);
}
#[test]
fn full_filling_defect_needs_external_geometry_derivative(){
    let e=example_ensemble();let d=filling_defect(e,0.35,7e-15,2e-13).unwrap();
    near(d.observed_defect_s,d.reconstructed_defect_s,e.source_per_h_s+e.x_mass_dot_s.abs()+e.eta_dot_s.abs()+1e-12);
    unit(d.xi,e.x_mass-0.35);
    let other=filling_defect(e,0.7,-4e-15,2e-13).unwrap();
    assert!((d.xi-other.xi).abs()>0.3);
}
#[test]
fn omitting_photon_storage_is_detected(){
    let e=example_ensemble();let d=filling_defect(e,0.35,7e-15,2e-13).unwrap();
    assert!(e.eta_dot_s.abs()>1e-14);
    let mutant=d.reconstructed_defect_s-d.storage_term_s;
    near(mutant-d.observed_defect_s,e.eta_dot_s,e.eta_dot_s.abs());
}
#[test]
fn conditional_sharp_uniform_density_recovers_standard_q_equation(){
    let mut rows=Vec::new();
    for (w,x) in [(0.4,1.0),(0.6,0.0)]{
        let mut i=input(2e-4,x);i.case=RecombinationCase::B;i.other_absorption_proper_cm3_s=[0.0;3];
        i.edge_n_per_cm3_ev=[0.0;4];i.source_proper_cm3_s=[0.0;3];
        let first=connected_cell(i).unwrap();i.source_proper_cm3_s[0]=first.photo_proper_cm3_s;
        rows.push((w,connected_cell(i).unwrap()));
    }
    let e=ensemble(&rows).unwrap();unit(e.x_mass,0.4);
    near(e.eta_dot_s,0.0,e.source_per_h_s);
    let p=SharpPhaseInput{q_v:0.4,ionized_density_contrast:1.0,contrast_dot_s:0.0,fully_ionized_neutral_sharp_phases_declared:true};
    let r=sharp_filling_rhs(e,p).unwrap();
    let invt=rows[0].1.alpha_cm3_s*e.mean_n_h_proper_cm3;
    near(r.q_v_dot_s,e.source_per_h_s-0.4*invt,e.source_per_h_s+0.4*invt);
    near(r.identity_residual_s,0.0,e.source_per_h_s+0.4*invt);
}
#[test]
fn sharp_phase_rejects_missing_closure_and_endpoints(){
    let e=example_ensemble();let p=SharpPhaseInput{q_v:0.4,ionized_density_contrast:e.x_mass/0.4,contrast_dot_s:0.0,fully_ionized_neutral_sharp_phases_declared:true};
    assert!(sharp_filling_rhs(e,p).is_ok());
    assert!(sharp_filling_rhs(e,SharpPhaseInput{fully_ionized_neutral_sharp_phases_declared:false,..p}).is_err());
    for q in [0.0,1.0]{assert!(sharp_filling_rhs(e,SharpPhaseInput{q_v:q,..p}).is_err());}
    assert!(sharp_filling_rhs(e,SharpPhaseInput{contrast_dot_s:f64::NAN,..p}).is_err());
    assert!(sharp_filling_rhs(e,SharpPhaseInput{ionized_density_contrast:1.0,..p}).is_err());
    assert!(sharp_filling_rhs(e,SharpPhaseInput{ionized_density_contrast:4.0,..p}).is_err());
}
#[test]
fn sharp_density_drift_is_not_silently_omitted(){
    let e=example_ensemble();let p=SharpPhaseInput{q_v:0.4,ionized_density_contrast:e.x_mass/0.4,contrast_dot_s:3e-13,fully_ionized_neutral_sharp_phases_declared:true};
    let drift=sharp_filling_rhs(e,p).unwrap();let fixed=sharp_filling_rhs(e,SharpPhaseInput{contrast_dot_s:0.0,..p}).unwrap();
    near(drift.q_v_dot_s-fixed.q_v_dot_s,-p.q_v*p.contrast_dot_s/p.ionized_density_contrast,1e-12);
}
#[test]
fn case_b_recycling_changes_sink_without_adding_tracked_photons(){
    let mut i=input(1e-4,0.4);let a=connected_cell(i).unwrap();i.case=RecombinationCase::B;let b=connected_cell(i).unwrap();
    assert!(a.alpha_cm3_s>b.alpha_cm3_s);
    for g in 0..3{near(a.photon.comoving_dot_cm3_s[g],b.photon.comoving_dot_cm3_s[g],a.photon.comoving_dot_cm3_s[g].abs());}
    let wrong_duplicated_ground_photons=(a.recombination_proper_cm3_s-b.recombination_proper_cm3_s)/i.n_h_proper_cm3;
    assert!(wrong_duplicated_ground_photons>0.0);
}
#[test]
fn photon_storage_can_grow_without_instantaneous_h_ionization(){
    let mut i=input(1e-4,1.0);i.source_proper_cm3_s=[1e-12,0.0,0.0];i.other_absorption_proper_cm3_s=[0.0;3];i.edge_n_per_cm3_ev=[0.0;4];
    let e=ensemble(&[(1.0,connected_cell(i).unwrap())]).unwrap();
    near(e.eta_dot_s,e.source_per_h_s,e.source_per_h_s);assert!(e.x_mass_dot_s<0.0);
    near(e.x_mass_dot_s,-e.recombination_per_h_s,e.recombination_per_h_s);
}
#[test]
fn ensemble_weight_normalization_and_background_guard(){
    let a=connected_cell(input(1e-4,0.1)).unwrap();let b=connected_cell(input(4e-4,0.9)).unwrap();
    let e=ensemble(&[(0.4,a),(0.6,b)]).unwrap();let f=ensemble(&[(4.0,a),(6.0,b)]).unwrap();
    unit(e.x_mass,f.x_mass);unit(e.x_volume,f.x_volume);near(e.eta_dot_s,f.eta_dot_s,e.eta_dot_s.abs());
    assert!(ensemble(&[]).is_err());assert!(ensemble(&[(0.0,a)]).is_err());
    assert!(ensemble(&[(1.0,a),(1.0,CellResult{hubble_s:3e-16,..b})]).is_err());
}
#[test]
fn photon_domain_errors_are_explicit(){
    let mut p=empty_photons();p.edge_energy_ev[1]=p.edge_energy_ev[0];assert!(photon_balance(p).is_err());
    let mut p=empty_photons();p.edge_n_per_cm3_ev[0]=-1.0;assert!(photon_balance(p).is_err());
    let mut p=empty_photons();p.hubble_s=-1.0;assert!(photon_balance(p).is_err());
    let mut p=empty_photons();p.comoving_photons_cm3[0]=f64::NAN;assert!(photon_balance(p).is_err());
    let mut p=empty_photons();p.scale_factor=0.0;assert!(photon_balance(p).is_err());
}
#[test]
fn connected_cell_rejects_wrong_domains(){
    let mut i=input(1e-4,1.1);assert!(connected_cell(i).is_err());
    i=input(1e-4,0.3);i.temperature_k=99.0;assert!(connected_cell(i).is_err());
    i=input(1e-4,0.3);i.photon_energy_ev[0]=30.0;assert!(connected_cell(i).is_err());
    i=input(0.0,0.3);assert!(connected_cell(i).is_err());
}

#[test]
fn externally_modified_ensemble_cannot_bypass_finite_domain_gate(){
    let e=example_ensemble();
    let p=SharpPhaseInput{q_v:0.4,ionized_density_contrast:e.x_mass/0.4,
        contrast_dot_s:0.0,fully_ionized_neutral_sharp_phases_declared:true};
    for bad in [Ensemble{x_mass:f64::NAN,..e},Ensemble{x_volume:f64::INFINITY,..e},
                Ensemble{x_mass:1.1,..e},Ensemble{eta:-0.1,..e},
                Ensemble{mean_n_h_proper_cm3:0.0,..e}] {
        assert!(filling_defect(bad,0.4,0.0,1e-13).is_err());
        assert!(sharp_filling_rhs(bad,p).is_err());
    }
}

#[test]
fn forged_cell_result_cannot_hide_invalid_inputs_in_positive_aggregate(){
    let good=connected_cell(input(4e-4,0.7)).unwrap();
    let other=connected_cell(input(1e-4,0.2)).unwrap();
    // The first mutation still gives a positive weighted mean density.
    for bad in [CellResult{n_h_proper_cm3:-1e-5,..other},
                CellResult{x_hii:f64::NAN,..other},
                CellResult{x_dot_s:f64::INFINITY,..other}] {
        assert!(ensemble(&[(0.5,good),(0.5,bad)]).is_err());
        assert!(ensemble(&[(1.0,good),(0.0,bad)]).is_err());
    }
}
