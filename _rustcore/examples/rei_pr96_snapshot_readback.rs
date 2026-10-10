//! Fixed scalar receiver for the immutable REI PR96 snapshots; no evolution.
use std::io::{self, Read};

use bianchi_rustcore::microphysics::{
    frame::MaterialFrame,
    rei::electron_state_from_rei,
    visibility::{ElectronState, VisibilityError},
};
use rei_microphysics::{GroupParams, PchipTable, State};

fn receive(v: &[f64; 6]) -> Result<[f64; 5], VisibilityError> {
    // Only proper densities and ionic fractions are consumed by the legacy
    // adapter. The remaining fields are explicitly inert API fixture values;
    // they do not represent a four-group reduction of the source photons.
    let table = PchipTable::new(
        vec![-2., 0., 2.],
        [vec![0.; 2], vec![0.; 2], vec![0.25; 2], vec![-3., -2.5]],
    )
    .expect("fixed inert PCHIP fixture");
    let params = GroupParams {
        redshift: 0.,
        n_h_proper_per_cm3: v[1],
        n_he_proper_per_cm3: v[2],
        hubble_per_s: 0.,
        sigma_hi_cm2: [0.; 4],
        sigma_hei_cm2: [0.; 4],
        sigma_heii_cm2: [0.; 4],
        redshift_coeff: [0.; 4],
        source_fraction: [0.; 4],
        lowgroup_log_opacity: [table.clone(), table],
    };
    let state = State {
        n_comoving_per_cmpc3: [0.; 4],
        x_hii: v[3],
        helium: [1. - v[4] - v[5], v[4], v[5]],
        u_erg_per_cm3: 0.,
        gamma_hi_per_s: 0.,
    };
    let direct = ElectronState::new(v[1] * 1e6, v[2] * 1e6, v[3], v[4], v[5])?;
    let legacy = electron_state_from_rei(&state, &params)?;
    let frame = MaterialFrame::new([0.; 3])?;
    Ok([
        v[0],
        direct.number_density_m3(),
        legacy.number_density_m3(),
        legacy.scattering_rate_per_normal_second(frame, [1., 0., 0.])?,
        legacy.scattering_rate_per_normal_second(frame, [0., 0., 1.])?,
    ])
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    for (i, line) in input.lines().enumerate() {
        let values: Vec<f64> = line
            .split_whitespace()
            .map(str::parse)
            .collect::<Result<_, _>>()?;
        let row: [f64; 6] = values.try_into().map_err(|_| format!("ROW_WIDTH_{i}"))?;
        if !row[0].is_finite() {
            return Err(format!("NONFINITE_TIME_{i}").into());
        }
        let result = receive(&row).map_err(|e| format!("RECEIVER_ROW_{i}: {e:?}"))?;
        println!(
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            result[0], result[1], result[2], result[3], result[4]
        );
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use bianchi_rustcore::microphysics::visibility::{C_M_S, SIGMA_T_M2};

    #[test]
    fn helium_double_charge_and_single_si_conversion() {
        let row = receive(&[0., 2., 3., 0.5, 0.3, 0.5]).unwrap();
        assert_eq!(row[1], 4.9e6);
        assert_eq!(row[1], row[2]);
        assert_eq!(row[3], row[4]);
        assert!((row[3] / (C_M_S * SIGMA_T_M2 * 4.9e6) - 1.).abs() < 1e-15);
    }

    #[test]
    fn neutral_and_nonphysical_snapshots() {
        assert_eq!(receive(&[0., 2., 3., 0., 0., 0.]).unwrap()[1], 0.);
        for row in [
            [0., 2., 3., 1.1, 0., 0.],
            [0., 2., 3., 0.5, 0.8, 0.3],
            [0., f64::MAX, 3., 1., 0., 0.],
            [0., 2., 3., f64::NAN, 0., 0.],
        ] {
            assert!(receive(&row).is_err());
        }
    }
}
