use bianchi_rustcore::microphysics::axisym_observables::{
    fixed_time_optical_depth, with_observer_tail, ObserverTail,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let slab = fixed_time_optical_depth(&[0., 1., 2.], &[1e6, 1e6], 0., 2.)
        .map_err(|e| format!("{e:?}"))?;
    let out = with_observer_tail(slab, ObserverTail::Unknown).map_err(|e| format!("{e:?}"))?;
    println!("scope,MANUFACTURED_PRESCRIBED_COMPONENT_PROBE");
    println!("proper_time_s,tau_fixed_time");
    println!("2,{:.17e}", out.slab.optical_depth);
    println!("observer_tail,UNKNOWN");
    Ok(())
}
