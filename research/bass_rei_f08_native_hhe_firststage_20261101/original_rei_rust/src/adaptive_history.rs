//! Uniform FT03 backward-Euler trial over the incoming seven-coordinate box.
//! The returned half-step box is the next accepted parent; no radius is reset.
use crate::{
    ft03_implicit_step, ft03_interval_rhs, interval_ad::Jet, interval_math::Interval, ForwardError,
    Ft03Events, Ft03Model, HHeState, StepControl,
};

const N: usize = 7;
type V = [Interval; N];
type M = [[Interval; N]; N];
const IDS: [&str; 3] = ["FULL_BE_ENDPOINT", "HALF1_BE_ENDPOINT", "HALF2_BE_ENDPOINT"];
fn fail(code: &'static str) -> ForwardError {
    ForwardError::InvalidInput(code)
}
fn domain(_: crate::interval_math::IntervalError) -> ForwardError {
    fail("FT03_CERT_INTERVAL")
}
fn p(x: f64) -> Result<Interval, ForwardError> {
    Interval::point(x).map_err(domain)
}
fn z() -> Interval {
    Interval { lo: 0.0, hi: 0.0 }
}
fn one() -> Interval {
    Interval { lo: 1.0, hi: 1.0 }
}
fn add(a: Interval, b: Interval) -> Result<Interval, ForwardError> {
    a.add(&b).map_err(domain)
}
fn sub(a: Interval, b: Interval) -> Result<Interval, ForwardError> {
    a.sub(&b).map_err(domain)
}
fn mul(a: Interval, b: Interval) -> Result<Interval, ForwardError> {
    a.mul(&b).map_err(domain)
}
fn div(a: Interval, b: Interval) -> Result<Interval, ForwardError> {
    a.div(&b).map_err(domain)
}
fn abs(a: Interval) -> f64 {
    a.lo.abs().max(a.hi.abs())
}
fn ubadd(a: f64, b: f64) -> f64 {
    up(a + b)
}
fn ubmul(a: f64, b: f64) -> f64 {
    up(a * b)
}
fn down(x: f64) -> f64 {
    if !x.is_finite() {
        return x;
    }
    if x == 0.0 {
        -f64::from_bits(1)
    } else {
        f64::from_bits(if x > 0.0 {
            x.to_bits() - 1
        } else {
            x.to_bits() + 1
        })
    }
}
fn up(x: f64) -> f64 {
    if !x.is_finite() {
        return x;
    }
    if x == 0.0 {
        f64::from_bits(1)
    } else {
        f64::from_bits(if x > 0.0 {
            x.to_bits() + 1
        } else {
            x.to_bits() - 1
        })
    }
}
fn outer(lo: f64, hi: f64) -> Result<Interval, ForwardError> {
    Interval::new(down(lo), up(hi)).map_err(domain)
}
fn mid(a: Interval) -> f64 {
    a.lo / 2.0 + a.hi / 2.0
}
fn mm(a: &M, b: &M) -> Result<M, ForwardError> {
    let mut c = [[z(); N]; N];
    for i in 0..N {
        for j in 0..N {
            for k in 0..N {
                c[i][j] = add(c[i][j], mul(a[i][k], b[k][j])?)?;
            }
        }
    }
    Ok(c)
}
fn norm(a: &M) -> f64 {
    (0..N)
        .map(|i| (0..N).fold(0.0, |s, j| ubadd(s, abs(a[i][j]))))
        .fold(0.0, f64::max)
}
fn identity() -> M {
    std::array::from_fn(|i| std::array::from_fn(|j| if i == j { one() } else { z() }))
}
fn subtract_matrix(a: &M, b: &M) -> Result<M, ForwardError> {
    let mut c = [[z(); N]; N];
    for i in 0..N {
        for j in 0..N {
            c[i][j] = sub(a[i][j], b[i][j])?;
        }
    }
    Ok(c)
}
fn inverse(mut a: [[f64; N]; N]) -> Result<[[f64; N]; N], ForwardError> {
    let mut b = [[0.0; N]; N];
    for i in 0..N {
        b[i][i] = 1.0;
    }
    for k in 0..N {
        let pivot = (k..N)
            .max_by(|&i, &j| a[i][k].abs().total_cmp(&a[j][k].abs()))
            .unwrap();
        if !a[pivot][k].is_finite() || a[pivot][k].abs() < 1e-300 {
            return Err(fail("FT03_CERT_SINGULAR"));
        }
        a.swap(k, pivot);
        b.swap(k, pivot);
        let t = a[k][k];
        for j in 0..N {
            a[k][j] /= t;
            b[k][j] /= t;
        }
        for i in 0..N {
            if i != k {
                let t = a[i][k];
                for j in 0..N {
                    a[i][j] -= t * a[k][j];
                    b[i][j] -= t * b[k][j];
                }
            }
        }
    }
    Ok(b)
}
pub fn scaled(model: &Ft03Model, s: &HHeState) -> [f64; N] {
    let nh = model.gas.n_h_cm3;
    [
        s.fractions[0],
        s.fractions[1],
        s.fractions[2],
        s.u_erg_cm3 / (nh * model.gas.ev_erg),
        s.photon_cm3[0] / nh,
        s.photon_cm3[1] / nh,
        s.photon_cm3[2] / nh,
    ]
}
fn scaled_enclosure(model: &Ft03Model, s: &HHeState) -> Result<V, ForwardError> {
    let nh = p(model.gas.n_h_cm3)?;
    let ev = p(model.gas.ev_erg)?;
    Ok([
        p(s.fractions[0])?,
        p(s.fractions[1])?,
        p(s.fractions[2])?,
        div(p(s.u_erg_cm3)?, mul(nh, ev)?)?,
        div(p(s.photon_cm3[0])?, nh)?,
        div(p(s.photon_cm3[1])?, nh)?,
        div(p(s.photon_cm3[2])?, nh)?,
    ])
}
fn contains(b: &V, v: &V) -> bool {
    (0..N).all(|i| b[i].lo <= v[i].lo && v[i].hi <= b[i].hi)
}
fn residual(model: &Ft03Model, y: &V, parent: &V, dt: f64) -> Result<V, ForwardError> {
    let f = ft03_interval_rhs(model, y)?;
    let t = p(dt)?;
    let mut r = [z(); N];
    for i in 0..N {
        r[i] = sub(sub(y[i], parent[i])?, mul(t, f[i].value)?)?;
    }
    Ok(r)
}
fn a_matrix(j: &[Jet; N], dt: f64) -> Result<M, ForwardError> {
    let mut a = identity();
    let d = p(dt)?;
    for i in 0..N {
        for k in 0..N {
            a[i][k] = sub(a[i][k], mul(d, j[i].gradient[k])?)?;
        }
    }
    Ok(a)
}
fn preconditioner(
    model: &Ft03Model,
    center: &[f64; N],
    dt: f64,
) -> Result<[[f64; N]; N], ForwardError> {
    let at = center.map(p).map(|x| x.unwrap());
    let f = ft03_interval_rhs(model, &at)?;
    let a = a_matrix(&f, dt)?;
    inverse(std::array::from_fn(|i| {
        std::array::from_fn(|j| mid(a[i][j]))
    }))
}

#[derive(Clone, Debug)]
pub struct RootSite {
    pub id: &'static str,
    pub center: [f64; N],
    pub r#box: V,
    pub preconditioner: [[f64; N]; N],
    pub step_s: f64,
}
#[derive(Clone, Debug)]
pub struct CertifiedTrial {
    pub state: HHeState,
    pub events: Ft03Events,
    pub next_box: V,
    pub local_bounds: [f64; 4],
    pub public_widths: [[f64; 4]; 2],
    pub sites: [RootSite; 3],
}
struct SiteMath {
    site: RootSite,
    jac: M,
    hess: [M; N],
    jc: M,
    eta: f64,
}

fn certify_site(
    model: &Ft03Model,
    id: &'static str,
    center: [f64; N],
    parent: &V,
    parent_center: [f64; N],
    parent_eta: f64,
    dt: f64,
) -> Result<SiteMath, ForwardError> {
    let c = preconditioner(model, &center, dt)?;
    let ci: M = std::array::from_fn(|i| std::array::from_fn(|j| p(c[i][j]).unwrap()));
    let yc = center.map(p).map(|x| x.unwrap());
    let parent_mid = parent_center.map(p).map(|x| x.unwrap());
    let r0 = residual(model, &yc, parent, dt)?;
    let mut cr = [z(); N];
    for i in 0..N {
        for j in 0..N {
            cr[i] = add(cr[i], mul(ci[i][j], r0[j])?)?;
        }
    }
    let mut radii = [0.0; N];
    for i in 0..N {
        radii[i] = ubadd(
            ubmul(2.0, abs(cr[i])),
            ubmul(1e-12, center[i].abs().max(1.0)),
        );
    }
    let mut bx: V =
        std::array::from_fn(|i| outer(center[i] - radii[i], center[i] + radii[i]).unwrap());
    // A Krawczyk image is an enclosure of every root. Rebox near that image,
    // then validate strict inclusion on the final box. This avoids multiplying
    // inherited radii by an arbitrary factor at every accepted time step.
    let mut q = 0.0;
    let mut valid = false;
    for iteration in 0..7 {
        let fj = ft03_interval_rhs(model, &bx)?;
        let a = a_matrix(&fj, dt)?;
        let b = subtract_matrix(&identity(), &mm(&ci, &a)?)?;
        q = norm(&b);
        if !q.is_finite() || q >= 1.0 {
            return Err(fail("FT03_CERT_DERIVATIVE_UNBOUNDED"));
        }
        let mut k = [z(); N];
        for i in 0..N {
            let mut v = sub(yc[i], cr[i])?;
            for j in 0..N {
                v = add(v, mul(b[i][j], sub(bx[j], yc[j])?)?)?;
            }
            k[i] = v;
        }
        let weighted = (0..N)
            .map(|i| {
                let rad = (center[i] - bx[i].lo).min(bx[i].hi - center[i]);
                (0..N).fold(0.0, |s, j| {
                    ubadd(
                        s,
                        up(ubmul(
                            abs(b[i][j]),
                            (center[j] - bx[j].lo).max(bx[j].hi - center[j]),
                        ) / rad),
                    )
                })
            })
            .fold(0.0, f64::max);
        if (0..N).all(|i| bx[i].lo < k[i].lo && k[i].hi < bx[i].hi)
            && weighted < 1.0
            && iteration > 0
        {
            valid = true;
            break;
        }
        // The small relative margin is for strict inclusion and binary rounding.
        // Preserve the approximate centre in the reboxed interval.
        bx = std::array::from_fn(|i| {
            let width = (k[i].hi - k[i].lo)
                .abs()
                .max(1e-15 * center[i].abs().max(1.0));
            let margin = width * 1e-4 + 1e-14 * center[i].abs().max(1.0);
            outer(
                k[i].lo.min(center[i]) - margin,
                k[i].hi.max(center[i]) + margin,
            )
            .unwrap()
        });
    }
    if !valid {
        return Err(fail("FT03_CERT_ROOT_INCLUSION"));
    }
    let rc = residual(model, &yc, &parent_mid, dt)?;
    let mut delta: f64 = 0.0;
    for i in 0..N {
        let mut v = z();
        for j in 0..N {
            v = add(v, mul(ci[i][j], rc[j])?)?;
        }
        let mut bound = abs(v);
        for j in 0..N {
            bound = ubadd(bound, ubmul(abs(ci[i][j]), parent_eta));
        }
        delta = delta.max(bound);
    }
    let eta = up(delta / (1.0 - q));
    let ycenter: V = std::array::from_fn(|i| outer(center[i] - eta, center[i] + eta).unwrap());
    if !contains(&bx, &ycenter) {
        return Err(fail("FT03_CERT_CENTER_ERROR"));
    }
    let (jac, hess) = derivatives(model, &bx, dt, &ci)?;
    let (jc, _) = derivatives(model, &ycenter, dt, &ci)?;
    Ok(SiteMath {
        site: RootSite {
            id,
            center,
            r#box: bx,
            preconditioner: c,
            step_s: dt,
        },
        jac,
        hess,
        jc,
        eta,
    })
}

fn derivatives(model: &Ft03Model, bx: &V, dt: f64, c: &M) -> Result<(M, [M; N]), ForwardError> {
    let f = ft03_interval_rhs(model, bx)?;
    let a = a_matrix(&f, dt)?;
    let b = subtract_matrix(&identity(), &mm(c, &a)?)?;
    let q = norm(&b);
    if !q.is_finite() || q >= 1.0 {
        return Err(fail("FT03_CERT_DERIVATIVE_UNBOUNDED"));
    }
    let mut sum = identity();
    let mut term = identity();
    for _ in 0..8 {
        term = mm(&term, &b)?;
        for i in 0..N {
            for j in 0..N {
                sum[i][j] = add(sum[i][j], term[i][j])?;
            }
        }
    }
    let mut inv = mm(&sum, c)?;
    let mut qpower = one();
    for _ in 0..9 {
        qpower = mul(qpower, p(q)?)?;
    }
    let tail = div(mul(qpower, p(norm(c))?)?, sub(one(), p(q)?)?)?.hi;
    if !tail.is_finite() {
        return Err(fail("FT03_CERT_DERIVATIVE_UNBOUNDED"));
    }
    for row in &mut inv {
        for x in row {
            x.lo = down(x.lo - tail);
            x.hi = up(x.hi + tail);
        }
    }
    let d = p(dt)?;
    let mut h = [[[z(); N]; N]; N];
    for output in 0..N {
        for i in 0..N {
            for j in 0..N {
                let mut v = z();
                for k in 0..N {
                    for a in 0..N {
                        for bb in 0..N {
                            v = add(
                                v,
                                mul(
                                    mul(
                                        mul(mul(d, inv[output][k])?, f[k].hessian[a][bb])?,
                                        inv[a][i],
                                    )?,
                                    inv[bb][j],
                                )?,
                            )?;
                        }
                    }
                }
                h[output][i][j] = v;
            }
        }
    }
    Ok((inv, h))
}

fn obs(model: &Ft03Model, bx: &V) -> Result<[Jet; 4], ForwardError> {
    let y: [Jet; N] = std::array::from_fn(|i| Jet::variable(bx[i], i).unwrap());
    let nh = p(model.gas.n_h_cm3)?;
    let fhe = div(p(model.gas.n_he_cm3)?, nh)?;
    let temperature_factor = div(
        mul(p(2.0)?, p(model.gas.ev_erg)?)?,
        mul(p(3.0)?, p(model.gas.kb_erg_k)?)?,
    )?;
    let k = Jet::constant(temperature_factor).map_err(domain)?;
    let f = Jet::constant(fhe).map_err(domain)?;
    let onej = Jet::constant(one()).map_err(domain)?;
    let two = Jet::constant(p(2.0)?).map_err(domain)?;
    let particles = onej
        .add(&f)
        .and_then(|v| v.add(&y[0]))
        .and_then(|v| {
            y[2].mul(&two)
                .and_then(|h| y[1].add(&h))
                .and_then(|h| h.mul(&f))
                .and_then(|h| v.add(&h))
        })
        .map_err(domain)?;
    let logt = k
        .mul(&y[3])
        .and_then(|v| v.div(&particles))
        .and_then(|v| v.ln())
        .map_err(domain)?;
    Ok([y[0].clone(), y[1].clone(), y[2].clone(), logt])
}
fn compose(first: &SiteMath, second: &SiteMath) -> Result<(M, [M; N], M), ForwardError> {
    let j = mm(&second.jac, &first.jac)?;
    let jc = mm(&second.jc, &first.jc)?;
    let mut h = [[[z(); N]; N]; N];
    for o in 0..N {
        for i in 0..N {
            for jj in 0..N {
                let mut v = z();
                for a in 0..N {
                    v = add(v, mul(second.jac[o][a], first.hess[a][i][jj])?)?;
                    for b in 0..N {
                        v = add(
                            v,
                            mul(
                                mul(second.hess[o][a][b], first.jac[a][i])?,
                                first.jac[b][jj],
                            )?,
                        )?;
                    }
                }
                h[o][i][jj] = v;
            }
        }
    }
    Ok((j, h, jc))
}
struct Affine {
    a: f64,
    b: [f64; N],
    rho: f64,
    width: f64,
}
fn affine(
    model: &Ft03Model,
    root: &SiteMath,
    j: &M,
    h: &[M; N],
    jc: &M,
    radii: &[f64; N],
) -> Result<[Affine; 4], ForwardError> {
    let o = obs(model, &root.site.r#box)?;
    let yc = root.site.center.map(p).map(|x| x.unwrap());
    let oc = obs(model, &yc)?;
    let yerr: V = std::array::from_fn(|i| {
        outer(
            root.site.center[i] - root.eta,
            root.site.center[i] + root.eta,
        )
        .unwrap()
    });
    let oe = obs(model, &yerr)?;
    let mut result = Vec::with_capacity(4);
    for k in 0..4 {
        let mut coeff = [z(); N];
        for i in 0..N {
            for a in 0..N {
                coeff[i] = add(coeff[i], mul(oe[k].gradient[a], jc[a][i])?)?;
            }
        }
        let b = coeff.map(mid);
        let a = mid(oc[k].value);
        let mut epsa = abs(sub(oc[k].value, p(a)?)?);
        for i in 0..N {
            epsa = ubadd(epsa, ubmul(abs(o[k].gradient[i]), root.eta));
        }
        let mut rho = epsa;
        for i in 0..N {
            rho = ubadd(rho, ubmul(abs(sub(coeff[i], p(b[i])?)?), radii[i]));
        }
        for i in 0..N {
            for jj in 0..N {
                let mut hij = z();
                for a in 0..N {
                    hij = add(hij, mul(o[k].gradient[a], h[a][i][jj])?)?;
                    for bb in 0..N {
                        hij = add(
                            hij,
                            mul(mul(mul(o[k].hessian[a][bb], j[a][i])?, j[bb][jj])?, one())?,
                        )?;
                    }
                }
                rho = ubadd(rho, ubmul(0.5, ubmul(abs(hij), ubmul(radii[i], radii[jj]))));
            }
        }
        let mut radius = rho;
        for i in 0..N {
            radius = ubadd(radius, ubmul(b[i].abs(), radii[i]));
        }
        let width = ubmul(2.0, radius);
        result.push(Affine { a, b, rho, width });
    }
    Ok(result.try_into().map_err(|_| fail("FT03_CERT_INTERNAL"))?)
}

pub fn certified_ft03_trial(
    model: &Ft03Model,
    old: &HHeState,
    parent: &V,
    dt: f64,
    control: StepControl,
) -> Result<CertifiedTrial, ForwardError> {
    if !dt.is_finite() || dt <= 0.0 {
        return Err(fail("FT03_CERT_STEP_CONTROL"));
    }
    let old_exact = scaled_enclosure(model, old)?;
    if !contains(parent, &old_exact) {
        return Err(fail("FT03_CERT_PARENT_EXCLUDES_STATE"));
    }
    let center = scaled(model, old);
    let radii = std::array::from_fn(|i| {
        let c = p(center[i]).unwrap();
        abs(sub(parent[i], c).unwrap())
    });
    let full = ft03_implicit_step(model, old, dt, control)?;
    let half1 = ft03_implicit_step(model, old, dt / 2.0, control)?;
    let half2 = ft03_implicit_step(model, &half1.state, dt / 2.0, control)?;
    let f = certify_site(
        model,
        IDS[0],
        scaled(model, &full.state),
        parent,
        center,
        0.0,
        dt,
    )?;
    let h1 = certify_site(
        model,
        IDS[1],
        scaled(model, &half1.state),
        parent,
        center,
        0.0,
        dt / 2.0,
    )?;
    let h2 = certify_site(
        model,
        IDS[2],
        scaled(model, &half2.state),
        &h1.site.r#box,
        h1.site.center,
        h1.eta,
        dt / 2.0,
    )?;
    let (j, h, jc) = compose(&h1, &h2)?;
    let of = affine(model, &f, &f.jac, &f.hess, &f.jc, &radii)?;
    let oh = affine(model, &h2, &j, &h, &jc, &radii)?;
    let mut local = [0.0; 4];
    let mut widths = [[0.0; 4]; 2];
    for k in 0..4 {
        let mut v = ubadd(
            abs(sub(p(of[k].a)?, p(oh[k].a)?)?),
            ubadd(of[k].rho, oh[k].rho),
        );
        for i in 0..N {
            v = ubadd(
                v,
                ubmul(abs(sub(p(of[k].b[i])?, p(oh[k].b[i])?)?), radii[i]),
            );
        }
        local[k] = v;
        widths[0][k] = of[k].width;
        widths[1][k] = oh[k].width;
    }
    if local.iter().any(|x| !x.is_finite() || *x >= 2e-4) {
        return Err(fail("FT03_CERT_LOCAL_ERROR"));
    }
    if widths
        .iter()
        .flatten()
        .any(|x| !x.is_finite() || *x >= 2e-3)
    {
        return Err(fail("FT03_CERT_PUBLIC_WIDTH"));
    }
    let state = half2.state;
    let exact = scaled_enclosure(model, &state)?;
    let mut next = h2.site.r#box;
    for i in 0..N {
        next[i] = outer(next[i].lo.min(exact[i].lo), next[i].hi.max(exact[i].hi))?;
    }
    let events = half1.events.plus(half2.events);
    Ok(CertifiedTrial {
        state,
        events,
        next_box: next,
        local_bounds: local,
        public_widths: widths,
        sites: [f.site, h1.site, h2.site],
    })
}
pub fn try_certified_ft03_step(
    model: &Ft03Model,
    state: &mut HHeState,
    parent: &mut V,
    dt: f64,
    control: StepControl,
) -> Result<CertifiedTrial, ForwardError> {
    let trial = certified_ft03_trial(model, state, parent, dt, control)?;
    *state = trial.state;
    *parent = trial.next_box;
    Ok(trial)
}
