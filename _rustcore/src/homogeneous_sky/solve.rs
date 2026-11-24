//! E-fold stepping of the photon distribution with either a native prescribed
//! background or active Einstein feedback of the transported normal-frame stress.
use super::ionization::Ionization;
use super::material::Material;
use super::replay::StepRecord;
use super::{
    geometric, initial_sky, moments, scatter_with, CollisionEvent, CollisionScheme, Photon,
    RadiationMoments,
};
use crate::kinetic::lie_history::{
    initial_lie_node, radiation_history, radiation_history_from_lie, required_flux, LieInitial,
    RayNode,
};
use crate::kinetic::radiation_feedback::{
    advance_mixture_with_options, refresh_mixture, ExpansionEquation, LieUpdate,
};
use crate::kinetic::tilted_dust::Dust;

pub struct Settings<'a> {
    pub family: &'a str,
    pub shear: f64,
    pub duration: f64,
    pub steps: usize,
    pub nmu: usize,
    pub nphi: usize,
    pub active: bool,
    pub recoil: bool,
    /// Fraction of initial matter energy placed in two counterstreaming dust fluids.
    pub dust_fraction: f64,
    pub dust_beta: [f64; 3],
    /// Time integrator of each Thomson depth cell.
    pub collision: CollisionScheme,
    /// Lambda/(3H^2) on the initial slice (active feedback only).
    pub omega_lambda: f64,
    /// Structure-constant update of the active Einstein step.
    pub lie_update: LieUpdate,
}
pub struct Snapshot {
    pub node: RayNode,
    pub radiation: RadiationMoments,
    pub omega_dust: f64,
    pub proper_depth: f64,
    pub collision_energy_defect: f64,
    pub host_beta: [f64; 3],
}
pub struct Solution {
    pub photons: Vec<Photon>,
    pub history: Vec<Snapshot>,
    pub initial_dust_mode: &'static str,
    /// Accepted steps with their collision events, for line-of-sight replay.
    pub records: Vec<StepRecord>,
}

struct CellResult {
    sky: Vec<Photon>,
    dust: Option<Dust>,
    depth: f64,
    energy_defect: f64,
    first: Vec<CollisionEvent>,
    second: Vec<CollisionEvent>,
}

fn collide_segment(
    result: &mut CellResult,
    cells: Vec<(f64, [f64; 3])>,
    photon_scale: f64,
    recoil: bool,
    scheme: CollisionScheme,
) -> Result<Vec<CollisionEvent>, String> {
    let mut events = Vec::new();
    for (tau, b) in cells {
        if recoil {
            let host = result
                .dust
                .as_mut()
                .ok_or("recoil requires massive matter")?;
            result.energy_defect += super::recoil::scatter_with_recoil_events(
                &mut result.sky,
                host,
                tau,
                photon_scale,
                scheme,
                &mut events,
            )?;
        } else {
            events.push(scatter_with(&mut result.sky, tau, b, scheme)?);
        }
        result.depth += tau;
    }
    Ok(events)
}

// Each half samples the host-rest density and H at its own geometric endpoint.
// In a massive stream D=m n_normal, E=gamma D, D(D/E)=m n_proper.
fn host_proper_mass(dust: &Option<Dust>) -> Result<f64, String> {
    let beam = dust
        .as_ref()
        .ok_or("ionization requires a massive host")?
        .beam(0)?;
    let proper = beam.normal_mass_density * (beam.normal_mass_density / beam.energy);
    if !proper.is_finite() || proper <= 0. {
        return Err("host proper mass density must be finite and positive".into());
    }
    Ok(proper)
}
struct Opacity<'a> {
    material: &'a Material,
    ionization: Option<(&'a Ionization, f64)>,
}
impl Opacity<'_> {
    fn cells(
        &self,
        start: f64,
        end: f64,
        stage: &RayNode,
        dust: &Option<Dust>,
    ) -> Result<Vec<(f64, [f64; 3])>, String> {
        if let Some((ion, initial_proper)) = self.ionization {
            ion.cells(
                start,
                end,
                host_proper_mass(dust)? / initial_proper,
                stage.hubble_ratio,
            )
        } else {
            self.material.cells(start, end)
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn evolve_cell(
    input: &[Photon],
    dust: &Option<Dust>,
    l: &RayNode,
    r: &RayNode,
    opacity: &Opacity,
    photon_scale: f64,
    recoil: bool,
    scheme: CollisionScheme,
) -> Result<CellResult, String> {
    let mid = (l.eta + r.eta) * 0.5;
    let mut result = CellResult {
        sky: input.to_vec(),
        dust: dust.clone(),
        depth: 0.,
        energy_defect: 0.,
        first: Vec::new(),
        second: Vec::new(),
    };
    let cells = opacity.cells(l.eta, mid, l, &result.dust)?;
    result.first = collide_segment(&mut result, cells, photon_scale, recoil, scheme)?;
    geometric(&mut result.sky, l, r)?;
    result.dust = move_dust(&result.dust, l, r)?;
    let cells = opacity.cells(mid, r.eta, r, &result.dust)?;
    result.second = collide_segment(&mut result, cells, photon_scale, recoil, scheme)?;
    Ok(result)
}

fn host_beta(d: &Option<Dust>) -> Result<[f64; 3], String> {
    Ok(match d {
        Some(dust) => dust.beam(0)?.beta,
        None => [0.; 3],
    })
}
struct Source {
    rad: f64,
    dust: f64,
    flux: [f64; 3],
    pressure: [[f64; 3]; 3],
}
fn source(
    rad: &RadiationMoments,
    photon_scale: f64,
    dust: &Option<Dust>,
    node: &RayNode,
) -> Result<Source, String> {
    let photon = rad.energy * photon_scale;
    let d = dust.as_ref().map(Dust::moments).transpose()?;
    let mass = d.as_ref().map_or(0., |x| x.energy);
    let total = photon + mass;
    let h2 = node.hubble_ratio.powi(2);
    if !total.is_finite() || total <= 0. || !(h2 > 0.) {
        return Err("invalid active energy".into());
    }
    let flux = std::array::from_fn(|i| {
        (photon * rad.flux[i] + d.as_ref().map_or(0., |x| x.flux[i])) / total
    });
    let pressure = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            (photon * rad.pressure[i][j] + d.as_ref().map_or(0., |x| x.pressure[i][j])) / total
        })
    });
    Ok(Source {
        rad: photon / h2,
        dust: mass / h2,
        flux,
        pressure,
    })
}

fn move_dust(d: &Option<Dust>, a: &RayNode, b: &RayNode) -> Result<Option<Dust>, String> {
    d.as_ref().map(|d| d.advance(a, b)).transpose()
}

pub fn solve(cfg: &Settings<'_>, mat: &Material) -> Result<Solution, String> {
    solve_with_inputs(cfg, mat, None, None)
}

pub fn solve_with_inputs(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
) -> Result<Solution, String> {
    solve_with_expansion(cfg, mat, lie, ionization, ExpansionEquation::Raychaudhuri)
}

pub fn solve_with_expansion(
    cfg: &Settings<'_>,
    mat: &Material,
    lie: Option<&LieInitial>,
    ionization: Option<&Ionization>,
    expansion: ExpansionEquation,
) -> Result<Solution, String> {
    if !cfg.active && expansion != ExpansionEquation::Raychaudhuri {
        return Err("Gauss-reduced expansion is available only for active feedback".into());
    }
    if ionization.is_some() && (!cfg.recoil || mat.has_scattering() || mat.has_prescribed_motion())
    {
        return Err(
            "dynamic ionization requires recoil feedback and replaces the prescribed optical input"
                .into(),
        );
    }
    if !cfg.duration.is_finite()
        || cfg.duration <= 0.
        || cfg.steps == 0
        || !(0.0..1.0).contains(&cfg.dust_fraction)
        || !cfg.shear.is_finite()
        || !cfg.dust_beta.iter().all(|v| v.is_finite())
        || cfg.dust_beta.iter().map(|v| v * v).sum::<f64>() >= 1.
    {
        return Err("invalid history, dust fraction or tilt".into());
    }
    if cfg.recoil && (!cfg.active || cfg.dust_fraction <= 0. || mat.has_prescribed_motion()) {
        return Err("recoil uses an active massive electron host and its own evolving velocity; input must supply the bare rate only".into());
    }
    if cfg.active && !cfg.recoil && mat.has_scattering() {
        return Err("active collisionless feedback requires zero optical rate: a prescribed scattering medium supplies no dynamical recoil".into());
    }
    if !cfg.active && cfg.dust_fraction != 0. {
        return Err("two dust streams require active geometry".into());
    }
    if !cfg.omega_lambda.is_finite() || cfg.omega_lambda < 0. {
        return Err("Omega_Lambda must be finite and nonnegative".into());
    }
    if !cfg.active && cfg.lie_update != LieUpdate::Additive {
        return Err("the congruence Lie update applies to active geometry; the tracer background uses its native QState step".into());
    }
    if !cfg.active && cfg.omega_lambda != 0. {
        return Err("a cosmological constant requires active geometry (the tracer background is radiation-only)".into());
    }
    if cfg.dust_fraction == 0. && cfg.dust_beta.iter().any(|b| *b != 0.) {
        return Err("dust tilt requires nonzero dust fraction".into());
    }
    // Material coverage must match the full evolution even for an optically empty segment.
    if let Some(ion) = ionization {
        ion.cells(0., cfg.duration, 1., 1.)?;
    } else {
        mat.cells(0., cfg.duration)?;
    }
    let dt = cfg.duration / (cfg.steps as f64);
    let profile = match (lie, cfg.active) {
        (Some(ic), true) => vec![initial_lie_node(ic)?],
        (Some(ic), false) => {
            radiation_history_from_lie(ic, cfg.duration, cfg.steps, cfg.nmu, cfg.nphi)?
        }
        (None, true) => radiation_history(cfg.family, cfg.shear, dt, 1, cfg.nmu, cfg.nphi)?,
        (None, false) => radiation_history(
            cfg.family,
            cfg.shear,
            cfg.duration,
            cfg.steps,
            cfg.nmu,
            cfg.nphi,
        )?,
    };
    let mut node = profile.first().ok_or("empty native geometry")?.clone();
    // Gauss fixes Omega_matter + Omega_Lambda; Lambda carries no flux or stress.
    node.omega_lambda = cfg.omega_lambda;
    let mut sky = initial_sky(cfg.nmu, cfg.nphi)?;
    let initial = moments(&sky)?;
    let total0 = node.omega_radiation - node.omega_lambda;
    if !total0.is_finite() || total0 <= 0. {
        return Err("Omega_Lambda leaves no positive matter density on the initial Gauss slice".into());
    }
    let scale = total0 * (1. - cfg.dust_fraction) / initial.energy;
    let required = required_flux(&node);
    let coflow = lie.is_some() && required.iter().map(|v| v * v).sum::<f64>().sqrt() > 1e-12;
    let (mut dust, initial_dust_mode) = if coflow {
        if !cfg.active || cfg.dust_fraction <= 0. {
            return Err("nonzero initial Codazzi flux with isotropic photons requires active massive matter".into());
        }
        if cfg.dust_beta.iter().any(|v| *v != 0.) {
            return Err("Codazzi determines the coflow velocity on this Lie initial slice".into());
        }
        let beta = std::array::from_fn(|i| {
            (required[i] - (1. - cfg.dust_fraction) * initial.flux[i]) / cfg.dust_fraction
        });
        (
            Some(
                Dust::coflow(total0 * cfg.dust_fraction, beta)
                    .map_err(|s| format!("Codazzi coflow: {s}"))?,
            ),
            "codazzi_coflow",
        )
    } else if cfg.dust_fraction == 0. {
        (None, "none")
    } else {
        (
            Some(Dust::opposed(total0 * cfg.dust_fraction, cfg.dust_beta)?),
            "opposed",
        )
    };
    let opacity = Opacity {
        material: mat,
        ionization: match ionization {
            Some(ion) => Some((ion, host_proper_mass(&dust)?)),
            None => None,
        },
    };
    let mut src = source(&initial, scale, &dust, &node)?;
    if cfg.active {
        refresh_mixture(&mut node, src.rad + src.dust, src.flux)?;
        node.omega_radiation = src.rad;
    }
    let mut history = vec![Snapshot {
        node: node.clone(),
        radiation: initial,
        omega_dust: src.dust,
        proper_depth: 0.,
        collision_energy_defect: 0.,
        host_beta: host_beta(&dust)?,
    }];
    let mut cumulative = 0.;
    let mut collision_defect = 0.;
    let mut records = Vec::with_capacity(cfg.steps);
    for step in 0..cfg.steps {
        let mut next = if cfg.active {
            let half = advance_mixture_with_options(
                &node,
                &node,
                dt * 0.5,
                src.rad + src.dust,
                src.pressure,
                src.flux,
                expansion,
                cfg.lie_update,
            )?;
            let predictor = evolve_cell(
                &sky,
                &dust,
                &node,
                &half,
                &opacity,
                scale,
                cfg.recoil,
                cfg.collision,
            )?;
            let hm = source(&moments(&predictor.sky)?, scale, &predictor.dust, &half)?;
            advance_mixture_with_options(
                &node,
                &half,
                dt,
                hm.rad + hm.dust,
                hm.pressure,
                hm.flux,
                expansion,
                cfg.lie_update,
            )?
        } else {
            profile[step + 1].clone()
        };
        // Set the independent clock by grid index; avoid a drift of a few ulps
        // beyond a material table's final endpoint on long integrations.
        next.eta = (step + 1) as f64 * dt;
        let step = evolve_cell(
            &sky,
            &dust,
            &node,
            &next,
            &opacity,
            scale,
            cfg.recoil,
            cfg.collision,
        )?;
        records.push(StepRecord {
            left: node.clone(),
            right: next.clone(),
            first: step.first,
            second: step.second,
        });
        let rad = moments(&step.sky)?;
        cumulative += step.depth;
        collision_defect += step.energy_defect;
        dust = step.dust;
        src = source(&rad, scale, &dust, &next)?;
        if cfg.active {
            refresh_mixture(&mut next, src.rad + src.dust, src.flux)?;
            next.omega_radiation = src.rad;
        }
        sky = step.sky;
        node = next;
        history.push(Snapshot {
            node: node.clone(),
            radiation: rad,
            omega_dust: src.dust,
            proper_depth: cumulative,
            collision_energy_defect: collision_defect,
            host_beta: host_beta(&dust)?,
        });
    }
    Ok(Solution {
        photons: sky,
        history,
        initial_dust_mode,
        records,
    })
}
