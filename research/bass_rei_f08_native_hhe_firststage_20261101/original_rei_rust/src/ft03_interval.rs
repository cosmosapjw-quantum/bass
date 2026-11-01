//! Outward second-order enclosure of the static FT03 map in the seven scaled
//! parent coordinates. The fit parameters are binary64 values from FT03.
use crate::{interval_ad::Jet, interval_math::Interval, ForwardError, Ft03Model};

fn err(_: crate::interval_math::IntervalError) -> ForwardError {
    ForwardError::InvalidInput("FT03_INTERVAL_DOMAIN")
}
type R<T> = Result<T, crate::interval_math::IntervalError>;
fn c(x: f64) -> R<Jet> {
    Jet::constant(Interval::point(x)?)
}
fn add(a: &Jet, b: &Jet) -> R<Jet> {
    a.add(b)
}
fn mul(a: &Jet, b: &Jet) -> R<Jet> {
    a.mul(b)
}
fn div(a: &Jet, b: &Jet) -> R<Jet> {
    a.div(b)
}
fn neg(a: &Jet) -> R<Jet> {
    a.neg()
}
fn sub(a: &Jet, b: &Jet) -> R<Jet> {
    a.sub(b)
}
fn product(items: &[Jet]) -> R<Jet> {
    let mut out = c(1.0)?;
    for item in items {
        out = mul(&out, item)?;
    }
    Ok(out)
}

pub fn ft03_interval_rhs(model: &Ft03Model, bx: &[Interval; 7]) -> Result<[Jet; 7], ForwardError> {
    let g = &model.gas;
    g.validate()?;
    if g.n_h_cm3 <= 0.0 || g.n_he_cm3 <= 0.0 {
        return Err(ForwardError::InvalidInput("FT03_NUCLEAR_DENSITY_DOMAIN"));
    }
    for x in bx {
        if x.lo <= 0.0 || x.valid().is_err() {
            return Err(ForwardError::InvalidInput("FT03_INTERVAL_DOMAIN"));
        }
    }
    if bx[0].hi >= 1.0 || bx[1].hi + bx[2].hi >= 1.0 {
        return Err(ForwardError::InvalidInput("FT03_INTERVAL_DOMAIN"));
    }
    let calc = || -> R<[Jet; 7]> {
        let y: [Jet; 7] =
            std::array::from_fn(|i| Jet::variable(bx[i], i).expect("validated interval"));
        let one = c(1.0)?;
        let two = c(2.0)?;
        let three = c(3.0)?;
        let nh = c(g.n_h_cm3)?;
        let nhe = c(g.n_he_cm3)?;
        let ev = c(g.ev_erg)?;
        let kb = c(g.kb_erg_k)?;
        let fhe = div(&nhe, &nh)?;
        let particles = add(
            &add(&add(&one, &fhe)?, &y[0])?,
            &mul(&fhe, &add(&y[1], &mul(&two, &y[2])?)?)?,
        )?;
        let t = div(
            &mul(&mul(&two, &ev)?, &y[3])?,
            &mul(&mul(&three, &kb)?, &particles)?,
        )?;
        if t.value.lo < 30_000.0 || t.value.hi > 110_000.0 {
            return Err(crate::interval_math::IntervalError);
        }
        let ne = add(
            &mul(&nh, &y[0])?,
            &mul(&nhe, &add(&y[1], &mul(&two, &y[2])?)?)?,
        )?;
        let lower = [
            mul(&nh, &sub(&one, &y[0])?)?,
            mul(&nhe, &sub(&sub(&one, &y[1])?, &y[2])?)?,
            mul(&nhe, &y[1])?,
        ];
        let upper = [mul(&nh, &y[0])?, mul(&nhe, &y[1])?, mul(&nhe, &y[2])?];
        let lambda = [315_614.0, 570_670.0, 1_263_030.0];
        let ci_a = [21.11, 32.38, 19.95];
        let ci_p = [-1.089, -1.146, -1.089];
        let ci_c = [0.354, 0.416, 0.553];
        let ci_r = [0.874, 0.987, 0.735];
        let ci_d = [1.101, 1.056, 1.275];
        let mut j = [c(0.0)?, c(0.0)?, c(0.0)?];
        let mut pd = [c(0.0)?, c(0.0)?, c(0.0)?];
        let mut w = c(0.0)?;
        for a in 0..3 {
            let l = div(&c(lambda[a])?, &t)?;
            let (alpha, slope) = if a == 1 {
                (mul(&c(3e-14)?, &l.powf(0.654)?)?, c(-0.654)?)
            } else {
                let u = div(&l, &c(0.522)?)?.powf(0.470)?;
                let alpha = div(
                    &product(&[
                        c(if a == 2 { 2.0 } else { 1.0 })?,
                        c(1.269e-13)?,
                        l.powf(1.503)?,
                    ])?,
                    &add(&one, &u)?.powf(1.923)?,
                )?;
                let slope = add(
                    &c(-1.503)?,
                    &div(
                        &product(&[c(1.923)?, c(0.470)?, u.clone()])?,
                        &add(&one, &u)?,
                    )?,
                )?;
                (alpha, slope)
            };
            let beta = div(
                &product(&[
                    c(ci_a[a])?,
                    t.powf(-1.5)?,
                    neg(&div(&l, &two)?)?.exp()?,
                    l.powf(ci_p[a])?,
                ])?,
                &add(&one, &div(&l, &c(ci_c[a])?)?.powf(ci_r[a])?)?.powf(ci_d[a])?,
            )?;
            let kinetic = product(&[kb.clone(), t.clone(), alpha.clone(), add(&c(1.5)?, &slope)?])?;
            let ci = div(&product(&[lower[a].clone(), ne.clone(), beta])?, &nh)?;
            let rr = div(&product(&[upper[a].clone(), ne.clone(), alpha])?, &nh)?;
            j[a] = sub(&ci, &rr)?;
            w = sub(
                &sub(&w, &mul(&c(g.threshold_ev[a])?, &ci)?)?,
                &div(
                    &product(&[upper[a].clone(), ne.clone(), kinetic])?,
                    &mul(&nh, &ev)?,
                )?,
            )?;
            for k in 0..3 {
                let ph = product(&[
                    c(g.c_cm_s)?,
                    lower[a].clone(),
                    c(g.sigma_cm2[a][k])?,
                    y[4 + k].clone(),
                ])?;
                j[a] = add(&j[a], &ph)?;
                pd[k] = sub(&pd[k], &ph)?;
                w = add(
                    &w,
                    &mul(
                        &sub(&c(g.photon_energy_ev[k])?, &c(g.threshold_ev[a])?)?,
                        &ph,
                    )?,
                )?;
            }
        }
        let dr_a = f64::from_bits(0x3f5f8b1ba9b90acb);
        let b1 = f64::from_bits(0x411caf2e364afdee);
        let b12 = f64::from_bits(0x412135e886f9cb6f);
        for (factor, b) in [(1.0, b1), (0.3, b12)] {
            let dr = div(
                &product(&[
                    upper[1].clone(),
                    ne.clone(),
                    c(factor)?,
                    c(dr_a)?,
                    t.powf(-1.5)?,
                    neg(&div(&c(b)?, &t)?)?.exp()?,
                ])?,
                &nh,
            )?;
            j[1] = sub(&j[1], &dr)?;
            w = sub(&w, &div(&product(&[dr, kb.clone(), c(b)?])?, &ev)?)?;
        }
        Ok([
            j[0].clone(),
            div(&sub(&j[1], &j[2])?, &fhe)?,
            div(&j[2], &fhe)?,
            w,
            pd[0].clone(),
            pd[1].clone(),
            pd[2].clone(),
        ])
    };
    calc().map_err(err)
}
