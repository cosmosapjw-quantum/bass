use bianchi_rustcore::kinetic::{
    massive_memory::FermiMemory,
    memory_mixture::{stf_components, stf_matrix, MemoryMixture, MemorySpecies},
};
#[test]
fn native_geometry_memory_source() {
    let f = FermiMemory::new(0.05, 1.6764e-4, 3.7e-5, 64).unwrap();
    let j = vec![[0., 1e-5, 2e-5, 0., 0.]; f.nodes().len()];
    let mix = MemoryMixture::new(
        vec![MemorySpecies {
            provider: f,
            memory: j,
        }],
        5.4e-5,
        0.31,
        0.68,
    )
    .unwrap();
    let a = 0.1;
    let beta = [0.; 5];
    let s = [0.; 5];
    let aa = [0.; 5];
    let m = mix.moments(a, beta, aa).unwrap();
    let d = mix.shear_rhs(a, s, beta, aa).unwrap();
    for k in 0..5 {
        assert!((d[k] - 3. * m.pi[k]).abs() < 1e-15);
    }
    let s = [1e-5, -2e-5, 3e-5, -1e-5, 2e-5];
    let m0 = stf_components(stf_matrix(s));
    for i in 0..5 {
        assert!((m0[i] - s[i]).abs() < 1e-19);
    }
}
