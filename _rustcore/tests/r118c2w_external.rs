use bianchi_rustcore::kinetic::{
    owned_thomson::{ExternalContribution, ExternalMatter, ThomsonOwner},
    owned_vlasov::OwnedState,
};
struct Dummy;
impl ExternalMatter for Dummy {
    type State = ();
    fn contribution(&mut self, _: &(), _: &OwnedState) -> Result<ExternalContribution, String> {
        Ok(ExternalContribution {
            rho: 0.,
            pressure: [[0.; 3]; 3],
            photon_rho: 0.,
            ne_m3: 100.,
        })
    }
    fn advance(
        &mut self,
        _: &(),
        _: &OwnedState,
        _: &OwnedState,
        _: &OwnedState,
    ) -> Result<(), String> {
        Ok(())
    }
}
#[test]
fn zero_external_stress_matches_native_step() {
    let m = ThomsonOwner::new(0.03, 24, 8, 16, 4, 8, 16).unwrap();
    let s = m.initial(1. / 21., [0.01, 0., 0., 0., 0.0075]).unwrap();
    let (a, _) = m.step(&s, 0.0001, 100., 100.).unwrap();
    let (b, _, _) = m.step_external(&s, &(), &mut Dummy, 0.0001).unwrap();
    assert_eq!(a.geometry.h, b.geometry.h);
    assert_eq!(a.geometry.s, b.geometry.s);
    assert_eq!(a.sky.coefficients, b.sky.coefficients);
}
