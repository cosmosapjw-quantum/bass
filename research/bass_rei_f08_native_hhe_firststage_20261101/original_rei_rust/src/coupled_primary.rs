//! Conditional FT03 gas/primary-packet stage. Packet energies are fixed here;
//! geometry, emission, and spectral transport belong to the enclosing history.
use crate::*;

const CHI: [f64; 3] = [13.598_434_599_702, 24.587_389_011, 54.417_76];
fn fail(code: &'static str) -> ForwardError {
    ForwardError::InvalidInput(code)
}
fn ie(_: impl std::fmt::Debug) -> ForwardError {
    fail("PRIMARY_INTERVAL_DOMAIN")
}

#[derive(Clone, Debug)]
pub struct PrimaryPacket {
    pub energy_ev: f64,
    pub per_h: f64,
}
#[derive(Clone, Debug)]
pub struct PrimaryState {
    pub fractions: [f64; 3],
    pub w_ev_per_h: f64,
    pub escape_ev_per_h: f64,
    pub packets: Vec<PrimaryPacket>,
}
#[derive(Clone, Copy, Debug)]
pub struct PrimaryStage {
    pub n_h_cm3: f64,
    pub f_he: f64,
    pub h_mean_per_s: f64,
}
#[derive(Clone, Debug)]
pub struct PrimaryEvents {
    pub photo_per_h: Vec<[f64; 3]>,
    pub collision_per_h: [f64; 3],
    pub recombination_per_h: [f64; 3],
    pub dr_per_h: [f64; 2],
    pub thermal_work_ev_per_h: f64,
}
#[derive(Clone, Debug)]
pub struct PrimaryStep {
    pub state: PrimaryState,
    pub events: PrimaryEvents,
    pub iterations: usize,
    pub residual: f64,
}
#[derive(Clone, Debug)]
pub struct PrimaryBox {
    pub gas: [Interval; 4],
    pub photons: Vec<Interval>,
}
#[derive(Clone, Debug)]
pub struct PrimaryRoot {
    pub centre: [f64; 4],
    pub gas: [Interval; 4],
    pub photons: Vec<Interval>,
    pub preconditioner: [[f64; 4]; 4],
    pub q: f64,
}

fn model(stage: &PrimaryStage) -> Result<Ft03Model, ForwardError> {
    if !stage.n_h_cm3.is_finite()
        || stage.n_h_cm3 <= 0.0
        || !stage.f_he.is_finite()
        || stage.f_he <= 0.0
        || !stage.h_mean_per_s.is_finite()
        || stage.h_mean_per_s < 0.0
        || !(stage.n_h_cm3 * stage.f_he).is_finite()
        || stage.n_h_cm3 * stage.f_he == 0.0
    {
        return Err(fail("PRIMARY_STAGE_DOMAIN"));
    }
    let mut m = Ft03Model::controlled()?;
    m.gas.n_h_cm3 = stage.n_h_cm3;
    m.gas.n_he_cm3 = stage.n_h_cm3 * stage.f_he;
    Ok(m)
}
fn signatures(old: &PrimaryState) -> Result<Vec<[f64; 3]>, ForwardError> {
    let provider = AtomicProvider::reference();
    old.packets
        .iter()
        .map(|p| {
            if !p.energy_ev.is_finite()
                || p.energy_ev <= 0.0
                || !p.per_h.is_finite()
                || p.per_h < 0.0
            {
                return Err(fail("PRIMARY_PACKET_DOMAIN"));
            }
            Ok([
                provider.cross_section(Absorber::HI, p.energy_ev)?,
                provider.cross_section(Absorber::HeI, p.energy_ev)?,
                provider.cross_section(Absorber::HeII, p.energy_ev)?,
            ])
        })
        .collect()
}
fn valid(m: &Ft03Model, s: &PrimaryState) -> Result<f64, ForwardError> {
    let [x, a, b] = s.fractions;
    if !x.is_finite()
        || x < 0.0
        || x > 1.0
        || !a.is_finite()
        || a < 0.0
        || !b.is_finite()
        || b < 0.0
        || a + b > 1.0
        || !s.w_ev_per_h.is_finite()
        || s.w_ev_per_h <= 0.0
        || !s.escape_ev_per_h.is_finite()
        || s.escape_ev_per_h < 0.0
    {
        return Err(fail("PRIMARY_STATE_DOMAIN"));
    }
    let g = &m.gas;
    let particles = 1.0 + g.n_he_cm3 / g.n_h_cm3 + x + g.n_he_cm3 / g.n_h_cm3 * (a + 2.0 * b);
    let t = 2.0 * s.w_ev_per_h * g.ev_erg / (3.0 * g.kb_erg_k * particles);
    if !t.is_finite() || !(30_000.0..=110_000.0).contains(&t) {
        return Err(fail("PRIMARY_TEMPERATURE_DOMAIN"));
    }
    Ok(t)
}
fn raw(m: &Ft03Model, s: &PrimaryState) -> Result<Ft03Rhs, ForwardError> {
    valid(m, s)?;
    ft03_rhs(
        m,
        &HHeState {
            fractions: s.fractions,
            u_erg_cm3: s.w_ev_per_h * m.gas.n_h_cm3 * m.gas.ev_erg,
            photon_cm3: [0.0; 3],
            escaped_erg_cm3: 0.0,
        },
    )
}
fn lower(stage: &PrimaryStage, s: &PrimaryState) -> [f64; 3] {
    [
        1.0 - s.fractions[0],
        stage.f_he * (1.0 - s.fractions[1] - s.fractions[2]),
        stage.f_he * s.fractions[1],
    ]
}
fn positive_product(factors: &[f64]) -> Result<f64, ForwardError> {
    if factors.iter().any(|v| !v.is_finite() || *v < 0.0) {
        return Err(fail("PRIMARY_PRODUCT_DOMAIN"));
    }
    if factors.contains(&0.0) {
        return Ok(0.0);
    }
    let mut value = 1.0;
    for factor in factors {
        value *= factor;
        if !value.is_finite() || value == 0.0 {
            return Err(fail("PRIMARY_POSITIVE_PRODUCT_RANGE"));
        }
    }
    Ok(value)
}
fn photons(
    stage: &PrimaryStage,
    old: &PrimaryState,
    guess: &PrimaryState,
    sigma: &[[f64; 3]],
    dt: f64,
    c: f64,
) -> Result<Vec<f64>, ForwardError> {
    let l = lower(stage, guess);
    old.packets
        .iter()
        .zip(sigma)
        .map(|(p, sig)| {
            let mut opacity = 0.0;
            for a in 0..3 {
                opacity += positive_product(&[c, stage.n_h_cm3, l[a], sig[a]])?;
            }
            let v = p.per_h / (1.0 + dt * opacity);
            if !v.is_finite() || v < 0.0 || (p.per_h > 0.0 && v == 0.0) {
                Err(fail("PRIMARY_PHOTON_OVERFLOW"))
            } else {
                Ok(v)
            }
        })
        .collect()
}
fn photo_rates(
    stage: &PrimaryStage,
    s: &PrimaryState,
    sigma: &[[f64; 3]],
    c: f64,
) -> Result<Vec<[f64; 3]>, ForwardError> {
    let l = lower(stage, s);
    s.packets
        .iter()
        .zip(sigma)
        .map(|(p, sig)| {
            let mut result = [0.0; 3];
            for a in 0..3 {
                result[a] = positive_product(&[c, stage.n_h_cm3, l[a], sig[a], p.per_h])?;
            }
            Ok(result)
        })
        .collect()
}
fn photo_heat(rates: &[[f64; 3]], packets: &[PrimaryPacket]) -> Result<f64, ForwardError> {
    let mut total = 0.0;
    for (r, p) in rates.iter().zip(packets) {
        for a in 0..3 {
            if r[a] > 0.0 {
                total += positive_product(&[r[a], p.energy_ev - CHI[a]])?;
            }
        }
    }
    if !total.is_finite() {
        return Err(fail("PRIMARY_HEAT_OVERFLOW"));
    }
    Ok(total)
}
fn energy(stage: &PrimaryStage, s: &PrimaryState) -> f64 {
    s.w_ev_per_h
        + CHI[0] * s.fractions[0]
        + stage.f_he * (CHI[1] * s.fractions[1] + (CHI[1] + CHI[2]) * s.fractions[2])
        + s.escape_ev_per_h
        + s.packets.iter().map(|p| p.energy_ev * p.per_h).sum::<f64>()
}
fn endpoint(
    stage: &PrimaryStage,
    m: &Ft03Model,
    old: &PrimaryState,
    s: &PrimaryState,
    sigma: &[[f64; 3]],
    dt: f64,
) -> Result<(f64, PrimaryEvents), ForwardError> {
    let r = raw(m, s)?;
    let nh = stage.n_h_cm3;
    let ev = m.gas.ev_erg;
    let rates = photo_rates(stage, s, sigma, m.gas.c_cm_s)?;
    let mut d = [
        r.derivative[0],
        r.derivative[1],
        r.derivative[2],
        r.derivative[3] / (nh * ev) - 2.0 * stage.h_mean_per_s * s.w_ev_per_h,
    ];
    for (k, pr) in rates.iter().enumerate() {
        d[0] += pr[0];
        d[1] += (pr[1] - pr[2]) / stage.f_he;
        d[2] += pr[2] / stage.f_he;
        let _ = k;
    }
    d[3] += photo_heat(&rates, &s.packets)?;
    let mut norm = 0.0_f64;
    let x0 = [
        old.fractions[0],
        old.fractions[1],
        old.fractions[2],
        old.w_ev_per_h,
    ];
    let x1 = [s.fractions[0], s.fractions[1], s.fractions[2], s.w_ev_per_h];
    for i in 0..4 {
        norm = norm
            .max(((x1[i] - x0[i] - dt * d[i]) / if i == 3 { old.w_ev_per_h } else { 1.0 }).abs());
    }
    for (k, p) in s.packets.iter().enumerate() {
        let loss = rates[k].iter().sum::<f64>();
        norm = norm.max(
            ((p.per_h - old.packets[k].per_h + dt * loss)
                / if old.packets[k].per_h > 0.0 {
                    old.packets[k].per_h
                } else {
                    1.0
                })
            .abs(),
        );
    }
    let escape_rate = r.escaped_energy_rate / (nh * ev);
    norm = norm.max(
        ((s.escape_ev_per_h - old.escape_ev_per_h - dt * escape_rate)
            / energy(stage, old).max(1e-30))
        .abs(),
    );
    let events = PrimaryEvents {
        photo_per_h: rates
            .into_iter()
            .map(|p| {
                let mut result = [0.0; 3];
                for a in 0..3 {
                    result[a] = positive_product(&[dt, p[a]])?;
                }
                Ok(result)
            })
            .collect::<Result<Vec<_>, ForwardError>>()?,
        collision_per_h: r.collision_per_cm3_s.map(|v| dt * v / nh),
        recombination_per_h: r.recombination_per_cm3_s.map(|v| dt * v / nh),
        dr_per_h: r.dr_per_cm3_s.map(|v| dt * v / nh),
        thermal_work_ev_per_h: positive_product(&[2.0, stage.h_mean_per_s, dt, s.w_ev_per_h])?,
    };
    if !norm.is_finite()
        || events
            .photo_per_h
            .iter()
            .flatten()
            .chain(events.collision_per_h.iter())
            .chain(events.recombination_per_h.iter())
            .chain(events.dr_per_h.iter())
            .any(|v| !v.is_finite() || *v < 0.0)
        || !events.thermal_work_ev_per_h.is_finite()
    {
        return Err(fail("PRIMARY_ENDPOINT_OVERFLOW"));
    }
    Ok((norm, events))
}

pub fn primary_stage_step(
    stage: &PrimaryStage,
    old: &PrimaryState,
    dt: f64,
    control: StepControl,
) -> Result<PrimaryStep, ForwardError> {
    let m = model(stage)?;
    signatures(old)?;
    valid(&m, old)?;
    if !dt.is_finite()
        || dt < 0.0
        || control.max_iterations == 0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(fail("PRIMARY_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok(PrimaryStep {
            state: old.clone(),
            events: PrimaryEvents {
                photo_per_h: vec![[0.0; 3]; old.packets.len()],
                collision_per_h: [0.0; 3],
                recombination_per_h: [0.0; 3],
                dr_per_h: [0.0; 2],
                thermal_work_ev_per_h: 0.0,
            },
            iterations: 0,
            residual: 0.0,
        });
    }
    let sigma = signatures(old)?;
    let mut guess = old.clone();
    for iteration in 1..=control.max_iterations {
        let temperature = valid(&m, &guess)?;
        let coeff = ft03_coefficients(temperature)?;
        let ne = stage.n_h_cm3
            * (guess.fractions[0] + stage.f_he * (guess.fractions[1] + 2.0 * guess.fractions[2]));
        let pn = photons(stage, old, &guess, &sigma, dt, m.gas.c_cm_s)?;
        let mut next = guess.clone();
        for (p, v) in next.packets.iter_mut().zip(pn) {
            p.per_h = v;
        }
        let ion = std::array::from_fn::<_, 3, _>(|a| {
            ne * coeff.beta_ci_cm3_s[a]
                + next
                    .packets
                    .iter()
                    .zip(&sigma)
                    .map(|(p, z)| m.gas.c_cm_s * stage.n_h_cm3 * z[a] * p.per_h)
                    .sum::<f64>()
        });
        let rr = coeff.alpha_rr_cm3_s.map(|v| ne * v);
        let dr = ne * coeff.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let (a, b, c, d) = (dt * ion[1], dt * (rr[1] + dr), dt * ion[2], dt * rr[2]);
        let he0 = 1.0 - old.fractions[1] - old.fractions[2];
        next.fractions[1] =
            (old.fractions[1] + he0 * a / (1.0 + a) + old.fractions[2] * d / (1.0 + d))
                / (1.0 + b / (1.0 + a) + c / (1.0 + d));
        next.fractions[2] = (old.fractions[2] + c * next.fractions[1]) / (1.0 + d);
        let r = raw(&m, &next)?;
        let rates = photo_rates(stage, &next, &sigma, m.gas.c_cm_s)?;
        let heat = photo_heat(&rates, &next.packets)?;
        next.w_ev_per_h = (old.w_ev_per_h
            + dt * (r.derivative[3] / (stage.n_h_cm3 * m.gas.ev_erg) + heat))
            / (1.0 + 2.0 * dt * stage.h_mean_per_s);
        next.escape_ev_per_h =
            old.escape_ev_per_h + dt * r.escaped_energy_rate / (stage.n_h_cm3 * m.gas.ev_erg);
        valid(&m, &next)?;
        let (norm, events) = endpoint(stage, &m, old, &next, &sigma, dt)?;
        if norm <= control.residual_tolerance {
            let e0 = energy(stage, old);
            let e1 = energy(stage, &next) + events.thermal_work_ev_per_h;
            if !e0.is_finite() || !e1.is_finite() || e0 <= 0.0 {
                return Err(fail("PRIMARY_ENERGY_INVARIANT"));
            }
            let packets_ok = next
                .packets
                .iter()
                .zip(&old.packets)
                .zip(&events.photo_per_h)
                .all(|((p, previous), loss)| {
                    let denom = if previous.per_h > 0.0 {
                        previous.per_h
                    } else {
                        1.0
                    };
                    (previous.per_h - p.per_h - loss.iter().sum::<f64>()).abs() / denom <= 1e-12
                });
            if (e1 - e0).abs() / e0 > 1e-12 || !packets_ok {
                guess = next;
                continue;
            }
            return Ok(PrimaryStep {
                state: next,
                events,
                iterations: iteration,
                residual: norm,
            });
        }
        guess = next;
    }
    Err(fail("PRIMARY_NONCONVERGENCE"))
}
pub fn try_primary_stage_step(
    stage: &PrimaryStage,
    state: &mut PrimaryState,
    dt: f64,
    control: StepControl,
) -> Result<PrimaryStep, ForwardError> {
    let result = primary_stage_step(stage, state, dt, control)?;
    *state = result.state.clone();
    Ok(result)
}

fn ic(x: f64) -> Result<Jet, ForwardError> {
    Jet::constant(Interval::point(x).map_err(ie)?).map_err(ie)
}
fn jadd(a: &Jet, b: &Jet) -> Result<Jet, ForwardError> {
    a.add(b).map_err(ie)
}
fn jsub(a: &Jet, b: &Jet) -> Result<Jet, ForwardError> {
    a.sub(b).map_err(ie)
}
fn jmul(a: &Jet, b: &Jet) -> Result<Jet, ForwardError> {
    a.mul(b).map_err(ie)
}
fn jdiv(a: &Jet, b: &Jet) -> Result<Jet, ForwardError> {
    a.div(b).map_err(ie)
}
fn jprod(xs: &[Jet]) -> Result<Jet, ForwardError> {
    let mut v = ic(1.0)?;
    for x in xs {
        v = jmul(&v, x)?;
    }
    Ok(v)
}
fn ia(a: &Interval, b: &Interval) -> Result<Interval, ForwardError> {
    a.add(b).map_err(ie)
}
fn is(a: &Interval, b: &Interval) -> Result<Interval, ForwardError> {
    a.sub(b).map_err(ie)
}
fn im(a: &Interval, b: &Interval) -> Result<Interval, ForwardError> {
    a.mul(b).map_err(ie)
}
fn ip(x: f64) -> Result<Interval, ForwardError> {
    Interval::point(x).map_err(ie)
}

/// Eliminate each backward-Euler packet exactly, then differentiate all four
/// coupled gas coordinates. The parent packet boxes remain interval parameters.
fn interval_rhs(
    stage: &PrimaryStage,
    m: &Ft03Model,
    old: &PrimaryState,
    gas: &[Interval; 4],
    pi: &[Interval],
    sigma: &[[f64; 3]],
    dt: f64,
) -> Result<([Jet; 4], Vec<Interval>), ForwardError> {
    let mut nonphoto = *m;
    nonphoto.gas.sigma_cm2 = [[0.0; 3]; 3];
    let dummy = ip(1.0)?;
    let all = [gas[0], gas[1], gas[2], gas[3], dummy, dummy, dummy];
    let raw = ft03_interval_rhs(&nonphoto, &all)?;
    let y: [Jet; 4] =
        std::array::from_fn(|i| Jet::variable(gas[i], i).expect("validated gas interval"));
    let one = ic(1.0)?;
    let lower = [
        jsub(&one, &y[0])?,
        jmul(&ic(stage.f_he)?, &jsub(&jsub(&one, &y[1])?, &y[2])?)?,
        jmul(&ic(stage.f_he)?, &y[1])?,
    ];
    let mut f = [
        raw[0].clone(),
        raw[1].clone(),
        raw[2].clone(),
        raw[3].clone(),
    ];
    let mut photons = Vec::with_capacity(pi.len());
    for k in 0..pi.len() {
        let mut opacity = ic(0.0)?;
        for a in 0..3 {
            opacity = jadd(&opacity, &jmul(&lower[a], &ic(sigma[k][a])?)?)?;
        }
        opacity = jmul(&opacity, &jmul(&ic(m.gas.c_cm_s)?, &ic(stage.n_h_cm3)?)?)?;
        let pk = jdiv(
            &Jet::constant(pi[k]).map_err(ie)?,
            &jadd(&one, &jmul(&ic(dt)?, &opacity)?)?,
        )?;
        photons.push(Interval::new(pk.value.lo.max(0.0), pk.value.hi).map_err(ie)?);
        let mut r = [ic(0.0)?, ic(0.0)?, ic(0.0)?];
        for a in 0..3 {
            r[a] = jprod(&[
                lower[a].clone(),
                jmul(&ic(m.gas.c_cm_s)?, &ic(stage.n_h_cm3)?)?,
                ic(sigma[k][a])?,
                pk.clone(),
            ])?;
            f[3] = jadd(
                &f[3],
                &jmul(&r[a], &jsub(&ic(old.packets[k].energy_ev)?, &ic(CHI[a])?)?)?,
            )?;
        }
        f[0] = jadd(&f[0], &r[0])?;
        f[1] = jadd(&f[1], &jdiv(&jsub(&r[1], &r[2])?, &ic(stage.f_he)?)?)?;
        f[2] = jadd(&f[2], &jdiv(&r[2], &ic(stage.f_he)?)?)?;
    }
    f[3] = jsub(
        &f[3],
        &jmul(&jmul(&ic(2.0)?, &ic(stage.h_mean_per_s)?)?, &y[3])?,
    )?;
    Ok((f, photons))
}

fn inverse4(a: [[f64; 4]; 4]) -> Result<[[f64; 4]; 4], ForwardError> {
    let mut aug = [[0.0; 8]; 4];
    for i in 0..4 {
        for j in 0..4 {
            aug[i][j] = a[i][j];
        }
        aug[i][4 + i] = 1.0;
    }
    for j in 0..4 {
        let pivot = (j..4)
            .max_by(|&a, &b| aug[a][j].abs().total_cmp(&aug[b][j].abs()))
            .unwrap();
        if !aug[pivot][j].is_finite() || aug[pivot][j].abs() < 1e-100 {
            return Err(fail("PRIMARY_SINGULAR_PRECONDITIONER"));
        }
        aug.swap(j, pivot);
        let d = aug[j][j];
        for k in 0..8 {
            aug[j][k] /= d;
        }
        for i in 0..4 {
            if i != j {
                let z = aug[i][j];
                for k in 0..8 {
                    aug[i][k] -= z * aug[j][k];
                }
            }
        }
    }
    let c = std::array::from_fn(|i| std::array::from_fn(|j| aug[i][4 + j]));
    if c.iter().flatten().any(|x| !x.is_finite()) {
        return Err(fail("PRIMARY_PRECONDITIONER_OVERFLOW"));
    }
    Ok(c)
}
fn box_about(x: f64, r: f64) -> Result<Interval, ForwardError> {
    if !r.is_finite() || r <= 0.0 {
        return Err(fail("PRIMARY_INTERVAL_RADIUS"));
    }
    let lo = is(&ip(x)?, &ip(r)?)?.lo;
    let hi = ia(&ip(x)?, &ip(r)?)?.hi;
    Interval::new(lo, hi).map_err(ie)
}
fn contains(b: &Interval, x: f64) -> bool {
    b.lo <= x && x <= b.hi
}
fn krawczyk(
    centre: &[f64; 4],
    parent: &PrimaryBox,
    y: &[Interval; 4],
    f0: &[Jet; 4],
    fy: &[Jet; 4],
    dt: f64,
    c: &[[f64; 4]; 4],
) -> Result<([Interval; 4], f64), ForwardError> {
    let mut b = [[ip(0.0)?; 4]; 4];
    let mut q = 0.0_f64;
    for i in 0..4 {
        let mut row = ip(0.0)?;
        for j in 0..4 {
            let mut v = ip(if i == j { 1.0 } else { 0.0 })?;
            for k in 0..4 {
                let ak = is(
                    &ip(if k == j { 1.0 } else { 0.0 })?,
                    &im(&ip(dt)?, &fy[k].gradient[j])?,
                )?;
                v = is(&v, &im(&ip(c[i][k])?, &ak)?)?;
            }
            row = ia(&row, &ip(v.lo.abs().max(v.hi.abs()))?)?;
            b[i][j] = v;
        }
        q = q.max(row.hi);
    }
    let mut k = [ip(0.0)?; 4];
    for i in 0..4 {
        let mut v = ip(centre[i])?;
        for j in 0..4 {
            let resid = is(
                &is(&ip(centre[j])?, &parent.gas[j])?,
                &im(&ip(dt)?, &f0[j].value)?,
            )?;
            v = is(&v, &im(&ip(c[i][j])?, &resid)?)?;
            v = ia(&v, &im(&b[i][j], &is(&y[j], &ip(centre[j])?)?)?)?;
        }
        k[i] = v;
    }
    Ok((k, q))
}

pub fn primary_stage_root(
    stage: &PrimaryStage,
    old: &PrimaryState,
    parent: &PrimaryBox,
    dt: f64,
    control: StepControl,
) -> Result<PrimaryRoot, ForwardError> {
    let m = model(stage)?;
    let sigma = signatures(old)?;
    valid(&m, old)?;
    if !dt.is_finite() || dt <= 0.0 || parent.photons.len() != old.packets.len() {
        return Err(fail("PRIMARY_ROOT_INPUT"));
    }
    let oldgas = [
        old.fractions[0],
        old.fractions[1],
        old.fractions[2],
        old.w_ev_per_h,
    ];
    for i in 0..4 {
        if !parent.gas[i].lo.is_finite()
            || !parent.gas[i].hi.is_finite()
            || parent.gas[i].lo > parent.gas[i].hi
            || !contains(&parent.gas[i], oldgas[i])
        {
            return Err(fail("PRIMARY_PARENT_GAS"));
        }
    }
    for (b, p) in parent.photons.iter().zip(&old.packets) {
        if !b.lo.is_finite()
            || !b.hi.is_finite()
            || b.lo < 0.0
            || b.lo > b.hi
            || !contains(b, p.per_h)
        {
            return Err(fail("PRIMARY_PARENT_PHOTON"));
        }
    }
    // Qualification covers the entire incoming gas box, including its
    // temperature domain, rather than only the actual incoming point.
    interval_rhs(stage, &m, old, &parent.gas, &parent.photons, &sigma, dt)?;
    let point = primary_stage_step(stage, old, dt, control)?;
    let centre = [
        point.state.fractions[0],
        point.state.fractions[1],
        point.state.fractions[2],
        point.state.w_ev_per_h,
    ];
    let centre_box = centre.map(ip).into_iter().collect::<Result<Vec<_>, _>>()?;
    let cb = [centre_box[0], centre_box[1], centre_box[2], centre_box[3]];
    let (f0, _) = interval_rhs(stage, &m, old, &cb, &parent.photons, &sigma, dt)?;
    let jac: [[f64; 4]; 4] = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            let z = f0[i].gradient[j];
            (z.lo + z.hi) * 0.5
        })
    });
    let a = std::array::from_fn(|i| {
        std::array::from_fn(|j| (if i == j { 1.0 } else { 0.0 }) - dt * jac[i][j])
    });
    let c = inverse4(a)?;
    let mut radius: [f64; 4] = std::array::from_fn(|i| {
        let p = &parent.gas[i];
        (p.hi - p.lo).abs() * 2.0 + centre[i].abs() * 1e-12 + 1e-13
    });
    let mut accepted: Option<PrimaryRoot> = None;
    for attempt in 0..24 {
        let y = [
            box_about(centre[0], radius[0])?,
            box_about(centre[1], radius[1])?,
            box_about(centre[2], radius[2])?,
            box_about(centre[3], radius[3])?,
        ];
        let (fy, photons) = interval_rhs(stage, &m, old, &y, &parent.photons, &sigma, dt)?;
        let (k, q) = krawczyk(&centre, parent, &y, &f0, &fy, dt, &c)?;
        if q < 1.0
            && (0..4).all(|i| y[i].lo < k[i].lo && k[i].hi < y[i].hi)
            && point
                .state
                .packets
                .iter()
                .zip(&photons)
                .all(|(p, b)| contains(b, p.per_h))
        {
            accepted = Some(PrimaryRoot {
                centre,
                gas: y,
                photons,
                preconditioner: c,
                q,
            });
            let refined: [f64; 4] = std::array::from_fn(|i| {
                let r = (k[i].lo - centre[i]).abs().max((k[i].hi - centre[i]).abs());
                r * 1.00001 + 32.0 * f64::EPSILON * centre[i].abs().max(1.0)
            });
            if attempt >= 8 || (0..4).all(|i| refined[i] >= radius[i] * 0.999) {
                return Ok(accepted.unwrap());
            }
            radius = refined;
            continue;
        }
        for i in 0..4 {
            let want = (k[i].lo - centre[i]).abs().max((k[i].hi - centre[i]).abs());
            radius[i] = (radius[i] * 1.5).max(want * 1.5);
        }
    }
    accepted.ok_or_else(|| fail("PRIMARY_ROOT_NONCONVERGENCE"))
}

// Additive numerical variant; original map, roots and point API retained verbatim.
pub fn primary_stage_step_conservative(
    stage: &PrimaryStage,
    old: &PrimaryState,
    dt: f64,
    control: StepControl,
    incoming_w_comp: f64,
) -> Result<(PrimaryStep, f64), ForwardError> {
    if !incoming_w_comp.is_finite() {
        return Err(fail("PRIMARY_ENERGY_COMPENSATION"));
    }
    let m = model(stage)?;
    signatures(old)?;
    valid(&m, old)?;
    if !dt.is_finite()
        || dt < 0.0
        || control.max_iterations == 0
        || !control.residual_tolerance.is_finite()
        || control.residual_tolerance <= 0.0
    {
        return Err(fail("PRIMARY_STEP_CONTROL"));
    }
    if dt == 0.0 {
        return Ok((
            PrimaryStep {
                state: old.clone(),
                events: PrimaryEvents {
                    photo_per_h: vec![[0.0; 3]; old.packets.len()],
                    collision_per_h: [0.0; 3],
                    recombination_per_h: [0.0; 3],
                    dr_per_h: [0.0; 2],
                    thermal_work_ev_per_h: 0.0,
                },
                iterations: 0,
                residual: 0.0,
            },
            incoming_w_comp,
        ));
    }
    let sigma = signatures(old)?;
    let mut guess = old.clone();
    for iteration in 1..=control.max_iterations {
        let temperature = valid(&m, &guess)?;
        let coeff = ft03_coefficients(temperature)?;
        let ne = stage.n_h_cm3
            * (guess.fractions[0] + stage.f_he * (guess.fractions[1] + 2.0 * guess.fractions[2]));
        let pn = photons(stage, old, &guess, &sigma, dt, m.gas.c_cm_s)?;
        let mut next = guess.clone();
        for (p, v) in next.packets.iter_mut().zip(pn) {
            p.per_h = v;
        }
        let ion = std::array::from_fn::<_, 3, _>(|a| {
            ne * coeff.beta_ci_cm3_s[a]
                + next
                    .packets
                    .iter()
                    .zip(&sigma)
                    .map(|(p, z)| m.gas.c_cm_s * stage.n_h_cm3 * z[a] * p.per_h)
                    .sum::<f64>()
        });
        let rr = coeff.alpha_rr_cm3_s.map(|v| ne * v);
        let dr = ne * coeff.alpha_dr_cm3_s.iter().sum::<f64>();
        next.fractions[0] = (old.fractions[0] + dt * ion[0]) / (1.0 + dt * (ion[0] + rr[0]));
        let (a, b, c, d) = (dt * ion[1], dt * (rr[1] + dr), dt * ion[2], dt * rr[2]);
        let he0 = 1.0 - old.fractions[1] - old.fractions[2];
        next.fractions[1] =
            (old.fractions[1] + he0 * a / (1.0 + a) + old.fractions[2] * d / (1.0 + d))
                / (1.0 + b / (1.0 + a) + c / (1.0 + d));
        next.fractions[2] = (old.fractions[2] + c * next.fractions[1]) / (1.0 + d);
        let r = raw(&m, &next)?;
        let rates = photo_rates(stage, &next, &sigma, m.gas.c_cm_s)?;
        let _heat = photo_heat(&rates, &next.packets)?;
        // Cancellation-safe conservative form of the same backward-Euler energy equation.
        let binding_change = CHI[0] * (next.fractions[0] - old.fractions[0])
            + stage.f_he
                * (CHI[1] * (next.fractions[1] - old.fractions[1])
                    + (CHI[1] + CHI[2]) * (next.fractions[2] - old.fractions[2]));
        let packet_change = next
            .packets
            .iter()
            .zip(&old.packets)
            .map(|(a, b)| a.energy_ev * (a.per_h - b.per_h))
            .sum::<f64>();
        let escape_change = dt * r.escaped_energy_rate / (stage.n_h_cm3 * m.gas.ev_erg);
        let dilation = 2.0 * dt * stage.h_mean_per_s;
        let thermal_change =
            (-binding_change - packet_change - escape_change - dilation * old.w_ev_per_h)
                / (1.0 + dilation);
        let compensated_change = thermal_change - incoming_w_comp;
        next.w_ev_per_h = old.w_ev_per_h + compensated_change;
        let outgoing_w_comp = (next.w_ev_per_h - old.w_ev_per_h) - compensated_change;
        next.escape_ev_per_h =
            old.escape_ev_per_h + dt * r.escaped_energy_rate / (stage.n_h_cm3 * m.gas.ev_erg);
        valid(&m, &next)?;
        let (norm, events) = endpoint(stage, &m, old, &next, &sigma, dt)?;
        if norm <= control.residual_tolerance {
            let e0 = energy(stage, old);
            let e1 = energy(stage, &next) + events.thermal_work_ev_per_h;
            if !e0.is_finite() || !e1.is_finite() || e0 <= 0.0 {
                return Err(fail("PRIMARY_ENERGY_INVARIANT"));
            }
            let packets_ok = next
                .packets
                .iter()
                .zip(&old.packets)
                .zip(&events.photo_per_h)
                .all(|((p, previous), loss)| {
                    let denom = if previous.per_h > 0.0 {
                        previous.per_h
                    } else {
                        1.0
                    };
                    (previous.per_h - p.per_h - loss.iter().sum::<f64>()).abs() / denom <= 1e-12
                });
            if (e1 - e0).abs() / e0 > 1e-12 || !packets_ok {
                guess = next;
                continue;
            }
            return Ok((
                PrimaryStep {
                    state: next,
                    events,
                    iterations: iteration,
                    residual: norm,
                },
                outgoing_w_comp,
            ));
        }
        guess = next;
    }
    Err(fail("PRIMARY_NONCONVERGENCE"))
}
