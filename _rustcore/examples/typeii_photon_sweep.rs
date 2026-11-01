//! Source-bound original Type-II photon coefficient oracle; not production dispatch.
//! Stdin rows: SigmaPlus,SigmaMinus,Sigma13,N1,v2,nx,ny,nz.
//! Output: dn_x,dn_y,dn_z,dlnE,dlnI,Gamma,q,D (eight binary64 scalars).
use bianchi_rustcore::runtime::typeii_host::TypeIIState5;
use bianchi_rustcore::runtime::typeii_photon_host::{
    source_photon_coefficients, unit_rest_optical_depth_factor,
};
use std::io::{self, BufRead};

fn main() {
    for line in io::stdin().lock().lines() {
        let line = line.expect("stdin line");
        if line.trim().is_empty() {
            continue;
        }
        let scalars: Vec<f64> = line
            .split(',')
            .map(|s| s.trim().parse::<f64>().expect("f64 source row"))
            .collect();
        assert_eq!(
            scalars.len(),
            8,
            "five source-state + three direction scalars required"
        );
        let state = TypeIIState5 {
            x: [scalars[0], scalars[1], scalars[2], scalars[3], scalars[4]],
            gamma: 1.3,
        };
        let host = state.to_host().expect("canonical source chart");
        let n = [scalars[5], scalars[6], scalars[7]];
        let rates = source_photon_coefficients(&host, n).expect("source Liouville");
        let doppler = unit_rest_optical_depth_factor(&host, n).unwrap();
        let gamma = 1.0 / (1.0 - scalars[4] * scalars[4]).sqrt();
        let q = 1.0 - scalars[4] * n[1];
        println!(
            "{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            rates.direction_rate[0],
            rates.direction_rate[1],
            rates.direction_rate[2],
            rates.log_energy_rate,
            rates.log_bolometric_rate,
            gamma,
            q,
            doppler
        );
    }
}
