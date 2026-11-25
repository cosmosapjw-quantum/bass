//! Material histories in Hubble e-fold time. Each supplied density is proper
//! to the electrons. A normal clock supplies c sigma_T n_e/H exactly once.
use std::path::Path;

#[derive(Clone, Copy, Debug)]
pub struct MaterialNode {
    pub eta: f64,
    pub rate: f64,
    pub beta: [f64; 3],
}
#[derive(Clone, Debug)]
pub struct Material {
    nodes: Vec<MaterialNode>,
}

impl Material {
    pub fn new(nodes: Vec<MaterialNode>) -> Result<Self, String> {
        if nodes.len() < 2
            || nodes.windows(2).any(|x| x[0].eta >= x[1].eta)
            || nodes.iter().any(|n| {
                !n.eta.is_finite()
                    || !n.rate.is_finite()
                    || n.rate < 0.0
                    || !(n.beta.iter().map(|b| b * b).sum::<f64>() < 1.0)
            })
        {
            return Err(
                "material nodes need increasing finite eta, nonnegative rate and subluminal beta"
                    .into(),
            );
        }
        Ok(Self { nodes })
    }
    pub fn constant(duration: f64, tau: f64, beta: [f64; 3]) -> Result<Self, String> {
        Self::new(
            [0., duration]
                .map(|eta| MaterialNode {
                    eta,
                    rate: tau / duration,
                    beta,
                })
                .to_vec(),
        )
    }
    pub fn load(path: &Path) -> Result<Self, String> {
        let body = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        let mut lines = body
            .lines()
            .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'));
        if lines
            .next()
            .map(|line| line.split_whitespace().collect::<Vec<_>>())
            != Some(vec!["eta", "rate_per_eta", "beta_x", "beta_y", "beta_z"])
        {
            return Err("material header must be eta rate_per_eta beta_x beta_y beta_z".into());
        }
        let mut nodes = Vec::new();
        for l in lines {
            let v: Vec<f64> = l
                .split_whitespace()
                .map(str::parse::<f64>)
                .collect::<Result<_, _>>()
                .map_err(|e| e.to_string())?;
            if v.len() != 5 {
                return Err("expected five material columns".into());
            }
            nodes.push(MaterialNode {
                eta: v[0],
                rate: v[1],
                beta: [v[2], v[3], v[4]],
            });
        }
        Self::new(nodes)
    }
    pub fn cells(&self, start: f64, end: f64) -> Result<Vec<(f64, [f64; 3])>, String> {
        if !start.is_finite() || !end.is_finite() || start >= end {
            return Err("invalid material interval".into());
        }
        let tol = 32. * f64::EPSILON * (1. + start.abs() + end.abs());
        let end_source = self.nodes.last().unwrap().eta;
        if start < self.nodes[0].eta - tol || end > end_source + tol {
            return Err("optical input does not cover the requested clock interval".into());
        }
        let mut result = Vec::new();
        let i = self
            .nodes
            .partition_point(|n| n.eta <= start)
            .saturating_sub(1);
        for pair in self.nodes[i..].windows(2) {
            let (a, b) = (pair[0], pair[1]);
            if a.eta >= end {
                break;
            }
            let x = start.max(a.eta);
            let y = end.min(b.eta);
            if y <= x {
                continue;
            }
            let u = (0.5 * (x + y) - a.eta) / (b.eta - a.eta);
            let rate = a.rate + (b.rate - a.rate) * u;
            let beta = std::array::from_fn(|k| a.beta[k] + (b.beta[k] - a.beta[k]) * u);
            if rate > 0. {
                result.push((rate * (y - x), beta));
            }
        }
        Ok(result)
    }
    /// Add a constant rate offset to each linear segment, integrating it
    /// exactly. Reject negative rates at either segment endpoint; no clamp.
    pub(super) fn cells_shifted(
        &self,
        start: f64,
        end: f64,
        offset: f64,
    ) -> Result<Vec<(f64, [f64; 3])>, String> {
        if !offset.is_finite() || start >= end {
            return Err("invalid shifted material interval".into());
        }
        self.rate_at(start)?;
        self.rate_at(end)?;
        if offset == 0. {
            return self.cells(start, end);
        }
        let mut out = Vec::new();
        let i = self
            .nodes
            .partition_point(|n| n.eta <= start)
            .saturating_sub(1);
        for pair in self.nodes[i..].windows(2) {
            let (a, b) = (pair[0], pair[1]);
            if a.eta >= end {
                break;
            }
            let x = start.max(a.eta);
            let y = end.min(b.eta);
            if x >= y {
                continue;
            }
            let u0 = (x - a.eta) / (b.eta - a.eta);
            let u1 = (y - a.eta) / (b.eta - a.eta);
            let r0 = a.rate + (b.rate - a.rate) * u0 + offset;
            let r1 = a.rate + (b.rate - a.rate) * u1 + offset;
            if !r0.is_finite() || !r1.is_finite() || r0 < 0. || r1 < 0. {
                return Err("nonphysical species-offset electron fraction".into());
            }
            let rate = 0.5 * r0 + 0.5 * r1;
            let depth = rate * (y - x);
            if !depth.is_finite() {
                return Err("nonfinite shifted depth".into());
            }
            if depth > 0. {
                let u = 0.5 * (u0 + u1);
                out.push((
                    depth,
                    std::array::from_fn(|k| a.beta[k] + u * (b.beta[k] - a.beta[k])),
                ));
            }
        }
        Ok(out)
    }

    /// Linearly interpolated rate at `eta` (no extrapolation beyond the knots).
    pub fn rate_at(&self, eta: f64) -> Result<f64, String> {
        let first = self.nodes[0].eta;
        let last = self.nodes.last().unwrap().eta;
        let tol = 32. * f64::EPSILON * (1. + first.abs() + last.abs());
        if !eta.is_finite() || eta < first - tol || eta > last + tol {
            return Err("material rate requested outside its clock interval".into());
        }
        let eta = eta.clamp(first, last);
        let i = self
            .nodes
            .partition_point(|n| n.eta <= eta)
            .saturating_sub(1)
            .min(self.nodes.len() - 2);
        let (a, b) = (self.nodes[i], self.nodes[i + 1]);
        let u = (eta - a.eta) / (b.eta - a.eta);
        Ok(a.rate + (b.rate - a.rate) * u)
    }
    pub fn has_prescribed_motion(&self) -> bool {
        self.nodes.iter().any(|n| n.beta.iter().any(|v| *v != 0.))
    }
    pub fn has_scattering(&self) -> bool {
        self.nodes.iter().any(|n| n.rate > 0.)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn integrates_kinks_once_and_rejects_extrapolation() {
        let n = |eta, rate| MaterialNode {
            eta,
            rate,
            beta: [0.; 3],
        };
        let m = Material::new(vec![n(0., 0.), n(0.3, 4.), n(1., 0.)]).unwrap();
        assert!((m.cells(0., 1.).unwrap().iter().map(|s| s.0).sum::<f64>() - 2.).abs() < 1e-14);
        assert!(m.cells(0., 1.1).is_err());
        assert!(Material::new(vec![n(0., 0.), n(0., 1.)]).is_err());
    }
}
