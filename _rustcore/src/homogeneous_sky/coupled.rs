//! R117 partitioned SDIRK chemistry / conservative second-order BASS
//! radiation-geometry step. NOT monolithic RK on the combined state.
//! Each accepted subinterval uses a linear bare rate through the two
//! actual endpoint states. A scalar nonlinear solve closes its right rate.
use super::*;
use crate::homogeneous_sky::{material::MaterialNode, recoil, M, V};
use rec_microphysics::species_thermal::{sdirk_first, sdirk_second, ReferenceNode, SDIRK_GAMMA};
use rec_microphysics::thomson_history::C_SIGMA_T_M3_S;

#[derive(Clone, Debug)]
pub struct CoupledStageReceipt {
    pub stage: usize,
    pub eta: f64,
    pub xe: f64,
    pub x_heii: f64,
    pub tm_k: f64,
    pub n_h_m3: f64,
    pub h_s: f64,
    pub gamma: f64,
    pub beta_prime: [f64; 3],
    pub expansion_ratio: f64,
    pub rate_left: f64,
    pub rate_used: f64,
    pub rate_rebuilt: f64,
    pub relative_residual: f64,
    pub depth: f64,
    pub iterations: usize,
    pub chemistry_iterations: usize,
    pub chemistry_residual: f64,
}

pub(super) struct Segment {
    pub(super) node: RayNode,
    pub(super) cell: CellResult,
    pub(super) receipt: CoupledStageReceipt,
    pub(super) state: ThermalState,
    pub(super) compton_temperature_k: f64,
}
pub(super) struct MacroStep {
    pub(super) middle: Segment,
    pub(super) end: Segment,
    pub(super) diagnostics: ThermalDiagnostics,
}
pub(super) struct Context<'a> {
    pub(super) cfg: &'a Settings<'a>,
    pub(super) reference: &'a ReferenceHistory,
    pub(super) initial_proper: f64,
    pub(super) scale: f64,
    pub(super) nu_scale: f64,
    pub(super) expansion: ExpansionEquation,
}

impl Context<'_> {
    fn physical(&self, node: &RayNode, dust: &Option<Dust>) -> Result<(f64, f64), String> {
        let a = self.reference.nodes()[0];
        let n = a.n_h_m3 * host_proper_mass(dust)? / self.initial_proper;
        let h = a.h_s * node.hubble_ratio;
        if !n.is_finite() || !h.is_finite() || n <= 0. || h <= 0. {
            return Err("invalid stage physical anchors".into());
        }
        Ok((n, h))
    }
    fn bare(&self, node: &RayNode, dust: &Option<Dust>, y: ThermalState) -> Result<f64, String> {
        let (n, h) = self.physical(node, dust)?;
        let k = C_SIGMA_T_M3_S * n * y.xe() / h;
        if !k.is_finite() || k < 0. {
            return Err("invalid stage bare rate".into());
        }
        Ok(k)
    }
    fn advance(
        &self,
        left: &RayNode,
        sky: &Field,
        nu: Option<&Field>,
        dust: &Option<Dust>,
        end: f64,
        k0: f64,
        k1: f64,
    ) -> Result<(RayNode, CellResult), String> {
        let dt = end - left.eta;
        let material = Material::new(vec![
            MaterialNode {
                eta: left.eta,
                rate: k0,
                beta: [0.; 3],
            },
            MaterialNode {
                eta: end,
                rate: k1,
                beta: [0.; 3],
            },
        ])?;
        let opacity = Opacity {
            material: &material,
            ionization: None,
            delta_xe: 0.,
            strict_species_offset: false,
        };
        let nm = nu.map(Field::moments).transpose()?;
        let src = source(
            &sky.moments()?,
            self.scale,
            nm.as_ref().map(|x| (x, self.nu_scale)),
            dust,
            left,
        )?;
        let mut half = advance_mixture_with_options(
            left,
            left,
            dt * 0.5,
            src.rad + src.nu + src.dust,
            src.pressure,
            src.flux,
            self.expansion,
            self.cfg.lie_update,
        )?;
        half.eta = left.eta + dt * 0.5;
        let pred = evolve_cell(
            sky,
            nu,
            dust,
            left,
            &half,
            &opacity,
            self.scale,
            true,
            self.cfg.collision,
        )?;
        let pn = field_moments(&pred.nu)?;
        let hm = source(
            &pred.sky.moments()?,
            self.scale,
            pn.as_ref().map(|x| (x, self.nu_scale)),
            &pred.dust,
            &half,
        )?;
        let mut next = advance_mixture_with_options(
            left,
            &half,
            dt,
            hm.rad + hm.nu + hm.dust,
            hm.pressure,
            hm.flux,
            self.expansion,
            self.cfg.lie_update,
        )?;
        next.eta = end;
        let cell = evolve_cell(
            sky,
            nu,
            dust,
            left,
            &next,
            &opacity,
            self.scale,
            true,
            self.cfg.collision,
        )?;
        let nn = field_moments(&cell.nu)?;
        let s = source(
            &cell.sky.moments()?,
            self.scale,
            nn.as_ref().map(|x| (x, self.nu_scale)),
            &cell.dust,
            &next,
        )?;
        refresh_mixture(&mut next, s.rad + s.nu + s.dust, s.flux)?;
        next.omega_radiation = s.rad;
        Ok((next, cell))
    }
    fn material_point(
        &self,
        node: &RayNode,
        cell: &CellResult,
        k: f64,
    ) -> Result<(ThermalPoint, f64, [f64; 3], f64), String> {
        let dust = cell.dust.as_ref().ok_or("missing stage host")?;
        let beam = dust.beam(0)?;
        let p = V::from(dust.streams[0].p);
        let b = V::from(beam.beta);
        let gamma = 1f64.hypot(p.x).hypot(p.y).hypot(p.z);
        let photons = cell.sky.photons()?;
        let force = if k == 0. {
            V::zeros()
        } else {
            match &cell.sky {
                Field::Harmonic(h) if h.continuum_work_lmax.is_some() => {
                    recoil::continuum_momentum_gain_per_depth(&h.moments()?, b)?
                }
                _ => recoil::momentum_gain_per_depth(&photons, b)?,
            }
        };
        let dp = V::from(dust.free_momentum_rhs(0, node)?)
            + force * (k * self.scale / beam.normal_mass_density);
        let db = (M::identity() - b * b.transpose()) * dp / gamma;
        let expansion = 3. + gamma * gamma * b.dot(&db) - 2. * V::from(node.a).dot(&b);
        let (n, h) = self.physical(node, &cell.dust)?;
        let ms = material_directional_sky(
            &photons,
            node,
            b.into(),
            db.into(),
            self.reference.nodes()[0].tr_k,
        )
        .map_err(|err| {
            let f = photons
                .iter()
                .map(|ray| {
                    super::super::rec_bridge::material_expansion_factor(
                        node,
                        ray.direction(),
                        b.into(),
                        db.into(),
                    )
                })
                .collect::<Result<Vec<_>, _>>();
            match f {
                Ok(f) => format!(
                    "stage material source eta {:.17e}: {err}; minimum Sobolev expansion {:.17e}",
                    node.eta,
                    f.iter().copied().fold(f64::INFINITY, f64::min)
                ),
                Err(e) => format!(
                    "stage material source eta {:.17e}: {err}; expansion evaluation: {e}",
                    node.eta
                ),
            }
        })?;
        let ds = DirectionalSky {
            weights: &ms.weights,
            temperature_k: &ms.temperature_k,
            expansion_factor: &ms.expansion_factor,
        };
        let point = ThermalPoint::new(&ds, n, h, gamma, expansion, 0., self.reference.helium())
            .map_err(|e| format!("stage thermal source eta {}: {e:?}", node.eta))?;
        Ok((point, gamma, db.into(), expansion))
    }
    #[allow(clippy::too_many_arguments)]
    fn stage<T>(
        &self,
        left: &RayNode,
        sky: &Field,
        nu: Option<&Field>,
        dust: &Option<Dust>,
        left_y: ThermalState,
        right: ReferenceNode,
        number: usize,
        solve: impl Fn(&ThermalPoint, &ThermalPoint) -> Result<(ThermalState, T, usize, f64), String>,
    ) -> Result<(Segment, T), String> {
        let k0 = self.bare(left, dust, left_y)?;
        let (n0, h0) = self.physical(left, dust)?;
        let mut k = C_SIGMA_T_M3_S * n0 * right.state.xe() / h0;
        let reference = self
            .reference
            .point(right)
            .map_err(|e| format!("stage reference: {e:?}"))?;
        let mut previous: Option<(f64, f64)> = None;
        for i in 1..=24 {
            let (node, cell) = self.advance(left, sky, nu, dust, right.eta, k0, k)?;
            let (p, gamma, beta_prime, expansion) = self.material_point(&node, &cell, k)?;
            let (state, payload, ci, cr) = solve(&p, &reference)?;
            let rebuilt = self.bare(&node, &cell.dust, state)?;
            let residual = rebuilt - k;
            let relative = residual.abs() / rebuilt.abs().max(k.abs()).max(1e-30);
            if relative <= 128. * f64::EPSILON {
                let (n, h) = self.physical(&node, &cell.dust)?;
                let receipt = CoupledStageReceipt {
                    stage: number,
                    eta: node.eta,
                    xe: state.xe(),
                    x_heii: state.x_heii,
                    tm_k: state.tm(self.reference.f_he()),
                    n_h_m3: n,
                    h_s: h,
                    gamma,
                    beta_prime,
                    expansion_ratio: expansion,
                    rate_left: k0,
                    rate_used: k,
                    rate_rebuilt: rebuilt,
                    relative_residual: relative,
                    depth: cell.depth,
                    iterations: i,
                    chemistry_iterations: ci,
                    chemistry_residual: cr,
                };
                return Ok((
                    Segment {
                        node,
                        cell,
                        receipt,
                        state,
                        compton_temperature_k: p.compton_temperature_k(),
                    },
                    payload,
                ));
            }
            let mut candidate = rebuilt;
            if let Some((old_k, old_r)) = previous {
                let dr = residual - old_r;
                if dr != 0. {
                    let secant = k - residual * (k - old_k) / dr;
                    if secant.is_finite()
                        && secant >= 0.
                        && (secant - k).abs() <= 4. * residual.abs()
                    {
                        candidate = secant;
                    }
                }
            }
            previous = Some((k, residual));
            k = candidate;
        }
        Err(format!("coupled opacity fixed point did not converge at eta {} stage {number}; refine macro grid",right.eta))
    }
    pub(super) fn advance_macro(
        &self,
        left: &RayNode,
        sky: &Field,
        nu: Option<&Field>,
        dust: &Option<Dust>,
        prev: ThermalState,
        end: f64,
    ) -> Result<MacroStep, String> {
        let h = end - left.eta;
        let r0 = self
            .reference
            .at(left.eta)
            .map_err(|e| format!("reference start: {e:?}"))?;
        let r1 = self
            .reference
            .at(left.eta + SDIRK_GAMMA * h)
            .map_err(|e| format!("reference stage1: {e:?}"))?;
        let r2 = self
            .reference
            .at(end)
            .map_err(|e| format!("reference stage2: {e:?}"))?;
        // Match the stage clock to the geometry node exactly even when reference
        // interpolation snaps a few ulps to an endpoint.
        let r1 = ReferenceNode {
            eta: left.eta + SDIRK_GAMMA * h,
            ..r1
        };
        let r2 = ReferenceNode { eta: end, ..r2 };
        let fhe = self.reference.f_he();
        let (middle, first) = self.stage(left, sky, nu, dust, prev, r1, 1, |p, r| {
            let a = sdirk_first(prev, r0.state, r1.state, h, fhe, p, r)
                .map_err(|e| format!("SDIRK stage1 eta {}: {e:?}", r1.eta))?;
            let (state, iterations, residual) = (a.state(), a.iterations(), a.scaled_residual());
            Ok((state, a, iterations, residual))
        })?;
        let (finish, diagnostics) = self.stage(
            &middle.node,
            &middle.cell.sky,
            middle.cell.nu.as_ref(),
            &middle.cell.dust,
            middle.state,
            r2,
            2,
            |p, r| {
                let (y, d) = sdirk_second(&first, r2.state, p, r)
                    .map_err(|e| format!("SDIRK stage2 eta {}: {e:?}", r2.eta))?;
                Ok((y, d, d.iterations - first.iterations(), d.scaled_residual))
            },
        )?;
        Ok(MacroStep {
            middle,
            end: finish,
            diagnostics,
        })
    }
}
