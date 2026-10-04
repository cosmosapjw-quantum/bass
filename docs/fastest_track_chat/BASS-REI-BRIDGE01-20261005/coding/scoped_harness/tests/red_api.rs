use bianchi_rustcore::microphysics::rei_visibility::electron_state_from_hhe;
#[test]
fn source_density_bridge_exists() {
 let model = rei_microphysics::HHeModel::controlled_fixture();
 let state = rei_microphysics::HHeState::controlled_fixture(&model);
 assert!(electron_state_from_hhe(&model, &state).is_ok());
}
