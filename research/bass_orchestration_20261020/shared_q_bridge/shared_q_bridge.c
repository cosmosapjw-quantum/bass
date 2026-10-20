#include "shared_q_bridge.h"
#include <math.h>
#include <stddef.h>

static const double EV_J = 1.602176634e-19;

/* Knuth TwoSum: for finite event sums without overflow, sum + residual = a+b
 * in exact real arithmetic (binary64 round-to-nearest, gradual underflow).
 * Captures losses that recomputing rounded debit/credit can conceal. */
static double sum_residual(double a, double b, double sum) {
    double bb = sum - a;
    return (a - (sum - bb)) + (b - bb);
}

/* frexp keeps each nonzero factor normal during intermediate arithmetic.
 * scalbn performs the only final exponent-range conversion. */
static double scaled_product(double a, double b, double h, int hpower) {
    int ea, eb, ec, eh, exponent;
    double m;
    if (a == 0.0 || b == 0.0) return 0.0;
    m = frexp(a, &ea) * frexp(b, &eb) * frexp(EV_J, &ec);
    exponent = ea + eb + ec;
    if (hpower > 0) { m *= frexp(h, &eh); exponent += eh; }
    if (hpower < 0) { m /= frexp(h, &eh); exponent -= eh; }
    return scalbn(m, exponent);
}

int bass_q_normalize(double n, double q, double h, int clock, int frame,
                     int energy_kind, struct bass_q_rate *output) {
    struct bass_q_rate next;
    if (output == NULL || !isfinite(n) || !isfinite(q) || !isfinite(h)
        || n < 0.0 || q < 0.0 || h <= 0.0
        || (clock != BASS_Q_PER_PROPER_SECOND && clock != BASS_Q_PER_LNA)
        || frame != BASS_Q_NORMAL_COMOVING_NON_TILTED
        || (energy_kind != BASS_Q_NOMINAL_SPECTRAL_SOURCE
            && energy_kind != BASS_Q_MEASURED_DEPOSITED_ENERGY))
        return BASS_Q_INVALID;
    next.Q_J_m3_s = scaled_product(n, q, h, clock == BASS_Q_PER_LNA ? 1 : 0);
    next.S_J_m3_lna = scaled_product(n, q, h, clock == BASS_Q_PER_PROPER_SECOND ? -1 : 0);
    if (!isfinite(next.Q_J_m3_s) || !isfinite(next.S_J_m3_lna)
        || (n > 0.0 && q > 0.0
            && (next.Q_J_m3_s == 0.0 || next.S_J_m3_lna == 0.0)))
        return BASS_Q_RANGE;
    next.donor_dt = -next.Q_J_m3_s;
    next.radiation_dt = next.Q_J_m3_s;
    next.donor_dlna = -next.S_J_m3_lna;
    next.radiation_dlna = next.S_J_m3_lna;
    next.energy_kind = energy_kind;
    next.flags = (fpclassify(next.Q_J_m3_s) == FP_SUBNORMAL
                  || fpclassify(next.S_J_m3_lna) == FP_SUBNORMAL)
                 ? BASS_Q_HAS_SUBNORMAL : 0;
    *output = next;
    return BASS_Q_OK;
}

int bass_q_transfer_event(double donor, double radiation, double delta,
                         struct bass_q_jump *output) {
    struct bass_q_jump next;
    if (output == NULL || !isfinite(donor) || !isfinite(radiation)
        || !isfinite(delta) || donor < 0.0 || radiation < 0.0 || delta < 0.0)
        return BASS_Q_INVALID;
    if (delta > donor) return BASS_Q_INSUFFICIENT_DONOR;
    next.donor_after_J_m3 = donor - delta;
    next.radiation_after_J_m3 = radiation + delta;
    if (!isfinite(next.radiation_after_J_m3)) return BASS_Q_RANGE;
    next.requested_J_m3 = delta;
    next.realized_donor_debit_J_m3 = donor - next.donor_after_J_m3;
    next.realized_radiation_credit_J_m3 = next.radiation_after_J_m3 - radiation;
    next.rounding_balance_defect_J_m3 =
        -(sum_residual(donor, -delta, next.donor_after_J_m3)
          + sum_residual(radiation, delta, next.radiation_after_J_m3));
    *output = next;
    return BASS_Q_OK;
}
