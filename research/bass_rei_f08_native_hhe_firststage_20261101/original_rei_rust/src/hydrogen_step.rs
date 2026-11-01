//! Exact constant-rate hydrogen oracle; no H/He, physical-rate or interval claim.
use crate::ForwardError;

/// Constant ionization rates per neutral H and recombination rate per H ion [s^-1].
#[derive(Debug, Clone, Copy)]
pub struct HydrogenRates {
    pub photo_per_s: f64,
    pub collisional_per_s: f64,
    pub secondary_per_s: f64,
    pub recombination_per_s: f64,
}

/// Dimensionless endpoint and nonnegative cumulative event counts per H nucleus.
#[derive(Debug, Clone, Copy)]
pub struct HydrogenStep {
    pub x_next: f64,
    pub photo_events: f64,
    pub collisional_events: f64,
    pub secondary_events: f64,
    pub recombination_events: f64,
}

/// Solve dx/dt = I(1-x)-Rx with independent photo/collisional/secondary ledgers.
/// Inputs and arithmetic overflow are errors; no endpoint or event is clipped.
/// Reversible cycles use min(q*dt,R*dt)*max(q,R)/(I+R) to avoid losing a
/// representable event count when the rate ratio itself underflows.
pub fn hydrogen_step(x: f64, dt: f64, rates: HydrogenRates) -> Result<HydrogenStep, ForwardError> {
    let channels = [
        rates.photo_per_s,
        rates.collisional_per_s,
        rates.secondary_per_s,
    ];
    if !x.is_finite()
        || !(0.0..=1.0).contains(&x)
        || !dt.is_finite()
        || dt < 0.0
        || channels
            .iter()
            .chain([rates.recombination_per_s].iter())
            .any(|v| !v.is_finite() || *v < 0.0)
    {
        return Err(ForwardError::InvalidInput("INVALID_HYDROGEN_STEP_INPUT"));
    }
    let i = channels.iter().sum::<f64>();
    let r = rates.recombination_per_s;
    let k = i + r;
    let depth = k * dt;
    if !k.is_finite() || !depth.is_finite() {
        return Err(ForwardError::InvalidInput("HYDROGEN_STEP_OVERFLOW"));
    }
    if dt == 0.0 || k == 0.0 {
        return Ok(HydrogenStep {
            x_next: x,
            photo_events: 0.0,
            collisional_events: 0.0,
            secondary_events: 0.0,
            recombination_events: 0.0,
        });
    }
    // A depth rounded to zero also has zero representable event count.
    let (loss, phi1, complement) = if depth == 0.0 {
        (0.0, 1.0, 0.0)
    } else {
        let loss = -(-depth).exp_m1();
        (loss, loss / depth, one_minus_phi1(depth))
    };
    let eq = i / k;
    let x_next = if eq >= x {
        x + (eq - x) * loss
    } else {
        eq + (x - eq) * (-depth).exp()
    };
    let cycles = |q: f64| (q * dt).min(r * dt) * (q.max(r) / k) * complement;
    let ion_events = channels.map(|q| (q * dt) * (1.0 - x) * phi1 + cycles(q));
    let rec_events = (r * dt) * x * phi1 + cycles(i);
    let result = HydrogenStep {
        x_next,
        photo_events: ion_events[0],
        collisional_events: ion_events[1],
        secondary_events: ion_events[2],
        recombination_events: rec_events,
    };
    if !x_next.is_finite()
        || !(0.0..=1.0).contains(&x_next)
        || ion_events
            .iter()
            .chain([rec_events].iter())
            .any(|v| !v.is_finite() || *v < 0.0)
    {
        return Err(ForwardError::InvalidInput("HYDROGEN_STEP_NUMERICAL_DOMAIN"));
    }
    Ok(result)
}

// Managed Devstral candidate, externally checked against Decimal(90).
// At most 7 alternating terms through t^7/8! for t<0.01. At that cap,
// the first omitted term is <= t^8/9! (<2.8e-22 at the switch). Early
// termination uses the last retained term < 1e-16*abs(sum); its truncation
// bound is the next alternating term. Rounding error is separate. No clipping.
pub fn one_minus_phi1(t: f64) -> f64 {
    if t == 0.0 {
        return 0.0;
    }
    const SMALL_T: f64 = 0.01;
    if t < SMALL_T {
        let mut sum: f64 = t / 2.0;
        let mut term: f64 = t / 2.0;
        let mut n: i32 = 1;
        loop {
            term *= -t / (n as f64 + 2.0);
            sum += term;
            n += 1;
            if n > 6 || term.abs() < sum.abs() * 1e-16 {
                break;
            }
        }
        sum
    } else {
        1.0 - (-(-t).exp_m1()) / t
    }
}
