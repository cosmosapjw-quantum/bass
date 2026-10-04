use rei_microphysics::{hhe_rhs, HHeModel, HHeState};
use rei_microphysics::he_rct::*;

fn provider(source: RctSource) -> RctProvider {
    RctProvider::new(source, RctScenario::W82GroundStateCommonTemperatureZeroDrift, true).unwrap()
}
fn fixture(nh: f64, nhe: f64, x: [f64; 3], t: f64) -> (HHeModel, HHeState) {
    let mut m = HHeModel::controlled_fixture();
    m.n_h_cm3 = nh; m.n_he_cm3 = nhe;
    let ne = nh*x[0] + nhe*(x[1]+2.0*x[2]);
    let s = HHeState { fractions: x, u_erg_cm3: 1.5*m.kb_erg_k*t*(nh+nhe+ne),
        photon_cm3: [2e-5,2e-6,2e-7], escaped_erg_cm3: 0.0 };
    (m,s)
}
fn close(a: f64, b: f64) {
    assert!((a-b).abs() <= 2e-14*a.abs().max(b.abs()).max(1e-300), "{a:e} != {b:e}");
}
fn selected(p: RctProvider, e: f64) -> RctSelection {
    RctSelection::Escaping { provider: p, closure: EscapingMeanPhotonEnergy::research_input_ev(e).unwrap() }
}

#[test]
fn source_conflict_ack_is_mandatory() {
    assert_eq!(RctProvider::new(RctSource::Kf96Nominal,
        RctScenario::W82GroundStateCommonTemperatureZeroDrift, false).unwrap_err().code(),
        "RCT_SOURCE_CONFLICT_NOT_ACKNOWLEDGED");
}
#[test]
fn exact_source_endpoints_and_seventeen_fold_alternatives() {
    let a=provider(RctSource::Kf96Nominal); let b=provider(RctSource::Gm25Constant);
    for t in [1000.0,5000.0,1e7] { assert_eq!(a.coefficient_cm3_s(t).unwrap(),1e-14); }
    for t in [200.0,5000.0,10000.0] { assert_eq!(b.coefficient_cm3_s(t).unwrap(),1.7e-13); }
    close(b.coefficient_cm3_s(5000.0).unwrap()/a.coefficient_cm3_s(5000.0).unwrap(),17.0);
}
#[test]
fn temperature_window_is_strict_without_switch_clamp_or_extrapolation() {
    for (src, ts) in [(RctSource::Kf96Nominal, [999.0,1e7+1.0]),
                      (RctSource::Gm25Constant,[199.0,10001.0])] {
        for t in ts { assert_eq!(provider(src).coefficient_cm3_s(t).unwrap_err().code(),"RCT_TEMPERATURE_DOMAIN"); }
    }
    for t in [f64::NAN,f64::INFINITY,f64::NEG_INFINITY,-1.0,0.0] {
        assert!(provider(RctSource::Kf96Nominal).coefficient_cm3_s(t).is_err());
    }
}
#[test]
fn source_metadata_keeps_provenance_and_missing_moments() {
    for src in [RctSource::Kf96Nominal,RctSource::Gm25Constant] {
        let r=provider(src).record();
        assert_eq!(r.snapshot_commit.len(),40); assert_eq!(r.provider_git_blob.len(),40);
        assert_eq!(r.packet_git_blob.len(),40); assert!(!r.physical_admission);
        assert!(!r.source_conflict_resolved); assert_eq!(r.uncertainty,None);
        assert_eq!(r.photon_energy_moment_ev,None);
    }
    let r=RctSource::Kf96Nominal.record();
    assert!(r.lower_endpoint_approximate_in_source); assert!(!r.isotope_source_resolved);
}
#[test]
fn event_rate_and_density_normalizations_follow_reactant_pair() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0);
    let e=provider(RctSource::Kf96Nominal).events(&m,&s).unwrap();
    close(e.n_hi_cm3,1.5); close(e.n_heiii_cm3,1.2); close(e.event_rate_cm3_s,1.8e-14);
    close(e.fraction_rate_s[0],9e-15); close(e.fraction_rate_s[1],6e-15);
    close(e.fraction_rate_s[2],-6e-15);
}
#[test]
fn scalar_only_ledger_does_not_claim_energy_closure() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0);
    let e=provider(RctSource::Kf96Nominal).events(&m,&s).unwrap();
    assert_eq!(e.thermal_photon_closure,RctClosureStatus::IncompleteScalarOnly);
    assert_eq!(e.emitted_photon_count_cm3_s,e.event_rate_cm3_s);
    assert_eq!(e.free_electron_rate_cm3_s,0.0);
}
#[test]
fn nuclei_and_free_charge_conserved_event_by_event() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0);
    let e=provider(RctSource::Gm25Constant).events(&m,&s).unwrap();
    let n=e.species_rate_cm3_s;
    assert_eq!(n[0]+n[1],0.0); assert_eq!(n[2]+n[3]+n[4],0.0);
    assert_eq!(n[1]+n[3]+2.0*n[4]-n[5],0.0);
    let ne_dot=m.n_h_cm3*e.fraction_rate_s[0]
        +m.n_he_cm3*(e.fraction_rate_s[1]+2.0*e.fraction_rate_s[2]);
    assert!(ne_dot.abs()<=4e-16*e.event_rate_cm3_s);
}
#[test]
fn absent_species_policy_is_zero_rct_fraction_derivative() {
    for (nh,nhe) in [(0.0,3.0),(2.0,0.0)] {
        let (m,s)=fixture(nh,nhe,[0.25,0.1,0.4],5000.0);
        let e=provider(RctSource::Kf96Nominal).events(&m,&s).unwrap();
        assert_eq!(e.event_rate_cm3_s,0.0); assert_eq!(e.fraction_rate_s,[0.0;3]);
    }
}
#[test]
fn missing_reactants_produce_no_rct_events() {
    for x in [[1.0,0.1,0.4],[0.25,0.1,0.0]] {
        let (m,s)=fixture(2.0,3.0,x,5000.0);
        assert_eq!(provider(RctSource::Kf96Nominal).events(&m,&s).unwrap().event_rate_cm3_s,0.0);
    }
}
#[test]
fn zero_event_does_not_bypass_selected_source_temperature_domain() {
    let (m,s)=fixture(2.0,3.0,[1.0,0.1,0.4],500.0);
    assert_eq!(provider(RctSource::Kf96Nominal).events(&m,&s).unwrap_err().code(),"RCT_TEMPERATURE_DOMAIN");
}
#[test]
fn state_and_model_validation_are_reused() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0); let p=provider(RctSource::Kf96Nominal);
    for x in [[f64::NAN,0.1,0.4],[-0.1,0.1,0.4],[0.1,0.8,0.4]] {
        let mut bad=s; bad.fractions=x; assert!(p.events(&m,&bad).is_err());
    }
    let mut bad=m; bad.n_h_cm3=-1.0; assert!(p.events(&bad,&s).is_err());
    let mut bad=s; bad.u_erg_cm3=f64::INFINITY; assert!(p.events(&m,&bad).is_err());
}
#[test]
fn reaction_q_uses_model_thresholds_and_rejects_nonpositive_release() {
    let (mut m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0); let p=provider(RctSource::Kf96Nominal);
    m.threshold_ev[0]=12.0;
    close(p.events(&m,&s).unwrap().q_ev,54.41776-12.0);
    m.threshold_ev[2]=11.0;
    assert_eq!(p.events(&m,&s).unwrap_err().code(),"RCT_Q_DOMAIN");
}
#[test]
fn explicit_mean_energy_allows_signed_heat_and_conserves_energy() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0); let p=provider(RctSource::Kf96Nominal);
    let q=m.threshold_ev[2]-m.threshold_ev[0];
    for delta in [-1.0,0.0,1.0] {
        let e=p.closed_events(&m,&s,EscapingMeanPhotonEnergy::research_input_ev(q+delta).unwrap()).unwrap();
        let residual=e.event.chemical_energy_rate_erg_cm3_s
            +e.thermal_energy_rate_erg_cm3_s+e.escaped_energy_rate_erg_cm3_s;
        assert!(residual.abs()<=5e-16*e.escaped_energy_rate_erg_cm3_s);
        close(e.thermal_energy_rate_erg_cm3_s,-delta*m.ev_erg*e.event.event_rate_cm3_s);
        assert_eq!(e.tracked_photon_rate_cm3_s,[0.0;3]); assert!(!e.physical_closure_admission);
        assert_eq!(e.escaped_photon_count_cm3_s,e.event.event_rate_cm3_s);
    }
}
#[test]
fn missing_zero_negative_and_nonfinite_photon_moments_are_not_closed() {
    for e in [0.0,-1.0,f64::NAN,f64::INFINITY,f64::NEG_INFINITY] {
        assert_eq!(EscapingMeanPhotonEnergy::research_input_ev(e).unwrap_err().code(),"RCT_ESCAPE_MOMENT_DOMAIN");
    }
}
#[test]
fn overflowing_event_is_rejected() {
    let (m,s)=fixture(1e180,1e180,[0.25,0.1,0.4],5000.0);
    assert_eq!(provider(RctSource::Kf96Nominal).events(&m,&s).unwrap_err().code(),"RCT_OVERFLOW");
}
#[test]
fn overflowing_energy_moment_product_is_rejected() {
    let (m,s)=fixture(1e20,1e20,[0.25,0.1,0.4],5000.0);
    assert_eq!(provider(RctSource::Kf96Nominal).closed_events(&m,&s,
        EscapingMeanPhotonEnergy::research_input_ev(f64::MAX).unwrap()).unwrap_err().code(),"RCT_OVERFLOW");
}
#[test]
fn disabled_default_is_bit_identical_to_actual_baseline() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0);
    let base=hhe_rhs(&m,&s).unwrap(); let out=combined_hhe_rhs(&m,&s,RctSelection::default()).unwrap();
    for (a,b) in base.derivative.iter().zip(out.combined.derivative) { assert_eq!(a.to_bits(),b.to_bits()); }
    assert_eq!(base.escaped_energy_rate.to_bits(),out.combined.escaped_energy_rate.to_bits());
    assert_eq!(base.photo_per_cm3_s,out.combined.photo_per_cm3_s);
    assert_eq!(base.collision_per_cm3_s,out.combined.collision_per_cm3_s);
    assert_eq!(base.recombination_per_cm3_s,out.combined.recombination_per_cm3_s);
    assert!(out.rct.is_none());
}
#[test]
fn disabled_has_no_rct_temperature_constraint() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],1e8);
    assert!(combined_hhe_rhs(&m,&s,RctSelection::Disabled).is_ok());
}
#[test]
fn composed_rhs_adds_event_and_energy_but_preserves_old_event_arrays() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0); let p=provider(RctSource::Gm25Constant);
    let q=m.threshold_ev[2]-m.threshold_ev[0];
    let out=combined_hhe_rhs(&m,&s,selected(p,q+1.0)).unwrap(); let e=out.rct.unwrap();
    for i in 0..3 { assert_eq!(out.combined.derivative[i],out.baseline.derivative[i]+e.event.fraction_rate_s[i]); }
    assert_eq!(out.combined.derivative[3],out.baseline.derivative[3]+e.thermal_energy_rate_erg_cm3_s);
    assert_eq!(&out.combined.derivative[4..],&out.baseline.derivative[4..]);
    assert_eq!(out.combined.photo_per_cm3_s,out.baseline.photo_per_cm3_s);
    assert_eq!(out.combined.recombination_per_cm3_s,out.baseline.recombination_per_cm3_s);
    assert_eq!(out.combined.escaped_energy_rate,out.baseline.escaped_energy_rate+e.escaped_energy_rate_erg_cm3_s);
}
#[test]
fn complete_composed_energy_balance_uses_actual_baseline() {
    let (m,s)=fixture(2.0,3.0,[0.25,0.1,0.4],5000.0);
    let out=combined_hhe_rhs(&m,&s,selected(provider(RctSource::Gm25Constant),43.0)).unwrap();
    let d=out.combined.derivative;
    let chemical=m.ev_erg*(m.n_h_cm3*d[0]*m.threshold_ev[0]
        +m.n_he_cm3*(d[1]*m.threshold_ev[1]+d[2]*(m.threshold_ev[1]+m.threshold_ev[2])));
    let photons=m.ev_erg*(0..3).map(|g|m.photon_energy_ev[g]*d[4+g]).sum::<f64>();
    let residual=chemical+photons+d[3]+out.combined.escaped_energy_rate;
    let scale=chemical.abs()+photons.abs()+d[3].abs()+out.combined.escaped_energy_rate.abs();
    assert!(residual.abs()<=2e-15*scale);
}

#[test]
fn ft03_disabled_preserves_actual_successor_bit_identity() {
    let m=rei_microphysics::Ft03Model::controlled().unwrap(); let s=m.initial_state();
    let b=rei_microphysics::ft03_rhs(&m,&s).unwrap();
    let o=combined_ft03_rhs(&m,&s,RctSelection::default()).unwrap();
    for(a,c)in b.derivative.iter().zip(o.combined.derivative){assert_eq!(a.to_bits(),c.to_bits());}
    assert_eq!(b.escaped_energy_rate.to_bits(),o.combined.escaped_energy_rate.to_bits());
    assert_eq!(b.photo_per_cm3_s,o.combined.photo_per_cm3_s);
    assert_eq!(b.collision_per_cm3_s,o.combined.collision_per_cm3_s);
    assert_eq!(b.recombination_per_cm3_s,o.combined.recombination_per_cm3_s);
    assert_eq!(b.dr_per_cm3_s,o.combined.dr_per_cm3_s); assert!(o.rct.is_none());
}
#[test]
fn ft03_wrapper_preserves_nonzero_rr_ci_dr_and_adds_only_rct() {
    let m=rei_microphysics::Ft03Model::controlled().unwrap(); let s=m.initial_state();
    let o=combined_ft03_rhs(&m,&s,selected(provider(RctSource::Kf96Nominal),42.0)).unwrap();
    let e=o.rct.unwrap(); let b=o.baseline;
    assert!(b.recombination_per_cm3_s.iter().all(|x|*x>0.0));
    assert!(b.collision_per_cm3_s.iter().all(|x|*x>0.0));
    assert!(b.dr_per_cm3_s.iter().all(|x|*x>0.0));
    assert_eq!(b.photo_per_cm3_s,o.combined.photo_per_cm3_s);
    assert_eq!(b.collision_per_cm3_s,o.combined.collision_per_cm3_s);
    assert_eq!(b.recombination_per_cm3_s,o.combined.recombination_per_cm3_s);
    assert_eq!(b.dr_per_cm3_s,o.combined.dr_per_cm3_s);
    for i in 0..3 {assert_eq!(o.combined.derivative[i],b.derivative[i]+e.event.fraction_rate_s[i]);}
    assert_eq!(o.combined.derivative[3],b.derivative[3]+e.thermal_energy_rate_erg_cm3_s);
    assert_eq!(&o.combined.derivative[4..],&b.derivative[4..]);
    assert_eq!(o.combined.escaped_energy_rate,b.escaped_energy_rate+e.escaped_energy_rate_erg_cm3_s);
}
#[test]
fn ft03_gas_legacy_rhs_is_a_wrong_adapter_negative_control() {
    let m=rei_microphysics::Ft03Model::controlled().unwrap(); let s=m.initial_state();
    let correct=rei_microphysics::ft03_rhs(&m,&s).unwrap();
    let wrong=hhe_rhs(&m.gas,&s).unwrap();
    assert_eq!(wrong.recombination_per_cm3_s,[0.0;3]);
    assert_eq!(wrong.collision_per_cm3_s,[0.0;3]);
    assert!(correct.recombination_per_cm3_s.iter().sum::<f64>()>0.0);
    assert!(correct.dr_per_cm3_s.iter().sum::<f64>()>0.0);
    assert_ne!(correct.derivative,wrong.derivative);
    assert_ne!(correct.escaped_energy_rate,wrong.escaped_energy_rate);
}
#[test]
fn ft03_domain_intersection_accepts_kf96_and_rejects_gm25() {
    let m=rei_microphysics::Ft03Model::controlled().unwrap();
    for t in [30001.0,50000.0,109999.0] {
        let mut s=m.initial_state(); let ne=m.gas.electron_density(&s).unwrap();
        s.u_erg_cm3=1.5*m.gas.kb_erg_k*t*(m.gas.n_h_cm3+m.gas.n_he_cm3+ne);
        assert!(combined_ft03_rhs(&m,&s,selected(provider(RctSource::Kf96Nominal),42.0)).is_ok());
        assert_eq!(combined_ft03_rhs(&m,&s,selected(provider(RctSource::Gm25Constant),42.0)).unwrap_err().code(),"RCT_TEMPERATURE_DOMAIN");
    }
}
