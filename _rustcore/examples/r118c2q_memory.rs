use bianchi_rustcore::kinetic::massive_memory::FermiMemory;
fn main() {
    println!(
        "mass,a,rho,p,chi,dchi,J0,J1,J2,J3,J4,stress0,stress1,stress2,stress3,stress4,mem,loss"
    );
    for m in [0., 0.001, 0.01, 0.05, 0.1, 0.3] {
        let s = FermiMemory::new(m, 0.00016763891604963858, 3.7562511328953514e-5, 128).unwrap();
        let j: Vec<_> = s
            .nodes()
            .iter()
            .map(|y| {
                let w = y * y / (y * y + 9.);
                [1. - w, 0.2 * w, w, 0.1 * w, -0.3 * (1. - w)]
            })
            .collect();
        for i in 0..=128 {
            let a = (1. / 21.) * (21_f64 / 5.).powf(i as f64 / 128.);
            let r = s.response(a, [0.2, -0.1, 0.3, 0.05, -0.2], &j).unwrap();
            print!(
                "{m:.17e},{a:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                r.rho_a4, r.pressure_a4, r.chi_a4, r.dchi_a4
            );
            for x in r.preferred.iter().chain(r.stress_a4.iter()) {
                print!(",{x:.17e}");
            }
            println!(
                ",{:.17e},{:.17e}",
                r.memory_energy_a4, r.memory_dissipation_a4
            );
        }
    }
}
