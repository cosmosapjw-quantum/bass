use bianchi_rustcore::microphysics::axisym_observables::{
    fixed_time_optical_depth, with_observer_tail, ObserverTail,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("scope,MANUFACTURED_PRESCRIBED_COMPONENT_PAIR");
    println!("proper_time_s,case,tau_fixed_time");
    for case_name in ["flrw", "axisym"] {
        let slab =
            fixed_time_optical_depth(&[0., 1.], &[1e6], 0., 1.).map_err(|e| format!("{e:?}"))?;
        let out = with_observer_tail(slab, ObserverTail::Unknown).map_err(|e| format!("{e:?}"))?;
        println!("1,{case_name},{:.17e}", out.slab.optical_depth);
    }
    println!("observer_tail,UNKNOWN");
    Ok(())
}
