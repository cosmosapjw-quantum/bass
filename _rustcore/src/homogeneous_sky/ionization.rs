//! An externally supplied recombination fraction evaluated on the *host*
//! normal clock. Eta = ln(a/a_emit), n_H is beam-rest hydrogen density.
use super::material::{Material, MaterialNode};
use std::path::Path;

use rec_microphysics::thomson_history::C_SIGMA_T_M3_S;

pub struct Ionization {
    unit_exposure: Material,
    emission_exposure_per_eta: f64,
}

impl Ionization {
    pub fn load(path: &Path, n_h_emit_m3: f64, h_emit_s: f64) -> Result<Self, String> {
        let input = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        Self::parse(&input, n_h_emit_m3, h_emit_s)
    }

    fn parse(input: &str, n_h_emit_m3: f64, h_emit_s: f64) -> Result<Self, String> {
        if !n_h_emit_m3.is_finite()
            || n_h_emit_m3 <= 0.0
            || !h_emit_s.is_finite()
            || h_emit_s <= 0.0
        {
            return Err("n_H,emit [m^-3] and H_emit [s^-1] must be finite and positive".into());
        }
        let mut lines = input
            .lines()
            .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'));
        if !lines
            .next()
            .is_some_and(|l| l.split_whitespace().eq(["eta", "xe_per_H"]))
        {
            return Err("ionization header must be eta xe_per_H".into());
        }
        let mut nodes = Vec::new();
        for line in lines {
            let mut fields = line.split_whitespace();
            let parse = |s: Option<&str>| {
                s.ok_or("missing ionization field")?
                    .parse::<f64>()
                    .map_err(|_| "invalid ionization number")
            };
            let eta = parse(fields.next())?;
            let xe = parse(fields.next())?;
            if fields.next().is_some() {
                return Err("expected two ionization fields".into());
            }
            nodes.push(MaterialNode {
                eta,
                rate: xe,
                beta: [0.; 3],
            });
        }
        if nodes.first().map(|p| p.eta) != Some(0.0) {
            return Err("ionization eta must start at emission, eta=0".into());
        }
        let scale = C_SIGMA_T_M3_S * n_h_emit_m3 / h_emit_s;
        if !scale.is_finite() || scale <= 0.0 {
            return Err("invalid emission exposure".into());
        }
        // This normalized material has rate x_e per unit hydrogen exposure.
        // Material handles knot ordering, positivity, interpolation and coverage.
        Ok(Self {
            unit_exposure: Material::new(nodes)?,
            emission_exposure_per_eta: scale,
        })
    }

    /// The host freezes n_H/rest and H on this geometry substep. Each knot
    /// contributes its exact integral of linearly interpolated x_e. The
    /// electron velocity and directional boost belong to the recoil operator.
    pub fn cells(
        &self,
        start: f64,
        end: f64,
        host_proper_ratio: f64,
        hubble_ratio: f64,
    ) -> Result<Vec<(f64, [f64; 3])>, String> {
        if !host_proper_ratio.is_finite()
            || host_proper_ratio <= 0.0
            || !hubble_ratio.is_finite()
            || hubble_ratio <= 0.0
        {
            return Err("host proper-density and Hubble ratios must be finite and positive".into());
        }
        let scale = self.emission_exposure_per_eta * (host_proper_ratio / hubble_ratio);
        if !scale.is_finite() || scale <= 0.0 {
            return Err("invalid host exposure".into());
        }
        let mut cells = self.unit_exposure.cells(start, end)?;
        for (depth, _) in &mut cells {
            *depth *= scale;
            if !depth.is_finite() {
                return Err("nonfinite Thomson exposure".into());
            }
        }
        Ok(cells)
    }
}
impl Ionization {
    /// Tabulated electron fraction per hydrogen at `eta` (linear between knots).
    pub fn xe_at(&self, eta: f64) -> Result<f64, String> {
        self.unit_exposure.rate_at(eta)
    }

    /// Cells of the table plus a constant offset `delta_xe` of the electron
    /// fraction on [start, end] (R113 matched recombination). The offset rescales
    /// the tabulated cells so that their total exposure integrates x_e + delta_xe;
    /// a zero offset returns exactly [`Self::cells`].
    pub fn cells_with_offset(
        &self,
        start: f64,
        end: f64,
        host_proper_ratio: f64,
        hubble_ratio: f64,
        delta_xe: f64,
    ) -> Result<Vec<(f64, [f64; 3])>, String> {
        let mut cells = self.cells(start, end, host_proper_ratio, hubble_ratio)?;
        if delta_xe == 0.0 {
            return Ok(cells);
        }
        if !delta_xe.is_finite() {
            return Err("nonfinite electron-fraction offset".into());
        }
        let scale = self.emission_exposure_per_eta * (host_proper_ratio / hubble_ratio);
        let added = scale * delta_xe * (end - start);
        let total: f64 = cells.iter().map(|c| c.0).sum();
        if total > 0.0 {
            let factor = ((total + added) / total).max(0.0);
            for (depth, _) in &mut cells {
                *depth *= factor;
            }
        } else if added > 0.0 {
            cells.push((added, [0.0; 3]));
        }
        Ok(cells)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn offset_cells_integrate_the_shifted_fraction_and_interpolate() {
        let ion =
            Ionization::parse("eta xe_per_H\n0 0.2\n1 0.1\n", 1.0 / C_SIGMA_T_M3_S, 1.).unwrap();
        assert!((ion.xe_at(0.5).unwrap() - 0.15).abs() < 1e-16);
        assert!(ion.xe_at(1.5).is_err());
        let base: f64 = ion
            .cells(0.25, 0.75, 2., 4.)
            .unwrap()
            .iter()
            .map(|c| c.0)
            .sum();
        let zero = ion.cells_with_offset(0.25, 0.75, 2., 4., 0.0).unwrap();
        assert_eq!(zero, ion.cells(0.25, 0.75, 2., 4.).unwrap());
        let shifted: f64 = ion
            .cells_with_offset(0.25, 0.75, 2., 4., 0.01)
            .unwrap()
            .iter()
            .map(|c| c.0)
            .sum();
        assert!((shifted - base - 0.5 * 0.01 * 0.5).abs() < 1e-15);
    }
    #[test]
    fn charge_fraction_integrates_knots_and_truncations_on_normal_host_clock() {
        let ion = Ionization::parse("eta xe_per_H\n0 0\n0.25 2\n1 0\n", 1.0 / C_SIGMA_T_M3_S, 1.)
            .unwrap();
        let cells = ion.cells(0.125, 0.625, 3., 2.).unwrap();
        assert_eq!(cells.len(), 2);
        assert!((cells[0].0 - 1.5 * 0.125 * 1.5).abs() < 2e-15);
        assert!((cells[1].0 - 1.5 * 0.375 * 1.5).abs() < 2e-15);
        assert!(cells.iter().all(|x| x.1 == [0.; 3]));
        assert!(ion.cells(0.0, 1.0001, 1., 1.).is_err());
        assert!(ion.cells(-0.1, 0.1, 1., 1.).is_err());
        assert!(ion.cells(0., 1., 1., 0.).is_err());
    }
    #[test]
    fn rejects_wrong_columns_invalid_material_anchors_and_clock() {
        for input in [
            "eta ne_m3\n0 1\n1 1",
            "eta xe_per_H\n0 0 9\n1 1",
            "eta xe_per_H\n0 0\n0 1",
            "eta xe_per_H\n0 0\n1 NaN",
            "eta xe_per_H\n1 0\n2 1",
            "eta xe_per_H\n0 -1\n1 1",
        ] {
            assert!(Ionization::parse(input, 1., 1.).is_err(), "{input}");
        }
        let vacuum = "eta xe_per_H\n0 0\n1 0";
        assert!(Ionization::parse(vacuum, 0., 1.).is_err());
        assert!(Ionization::parse(vacuum, 1., f64::INFINITY).is_err());
        assert!(Ionization::parse(vacuum, 1., 1.)
            .unwrap()
            .cells(0., 1., 1., 1.)
            .unwrap()
            .is_empty());
    }
}
