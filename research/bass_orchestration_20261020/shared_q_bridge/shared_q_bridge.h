#ifndef BASS_SHARED_Q_BRIDGE_H
#define BASS_SHARED_Q_BRIDGE_H

/* Additive C99 reference/FFI adapter. No dynamics or source model is selected. */
#ifdef __cplusplus
extern "C" {
#endif

enum bass_q_status {
    BASS_Q_OK = 0, BASS_Q_INVALID = 1, BASS_Q_RANGE = 2,
    BASS_Q_INSUFFICIENT_DONOR = 3
};
enum bass_q_clock { BASS_Q_PER_PROPER_SECOND = 1, BASS_Q_PER_LNA = 2 };
enum bass_q_frame { BASS_Q_NORMAL_COMOVING_NON_TILTED = 1 };
enum bass_q_energy_kind {
    BASS_Q_NOMINAL_SPECTRAL_SOURCE = 1,
    BASS_Q_MEASURED_DEPOSITED_ENERGY = 2
};
enum bass_q_flags { BASS_Q_HAS_SUBNORMAL = 1 };

struct bass_q_rate {
    double Q_J_m3_s;
    double S_J_m3_lna;
    double donor_dt;
    double radiation_dt;
    double donor_dlna;
    double radiation_dlna;
    int energy_kind;
    int flags;
};

/* nH is proper m^-3; qH is eV per H nucleus per stated clock.
 * H is the local proper-time expansion rate in s^-1, strictly positive.
 * qH already owns fesc, source band and angular normalization; none is added.
 * output is unchanged on failure. Source signs are exact unary negations.
 */
int bass_q_normalize(double nH_proper_m3, double qH_eV, double H_s,
                     int clock, int frame, int energy_kind,
                     struct bass_q_rate *output);

struct bass_q_jump {
    double donor_after_J_m3;
    double radiation_after_J_m3;
    double requested_J_m3;
    double realized_donor_debit_J_m3;
    double realized_radiation_credit_J_m3;
    double rounding_balance_defect_J_m3;
};

/* A local source event with a frozen volume/frame. Expansion/work is a separate
 * owner. delta must be the same MEASURED deposited energy used by radiation.
 * No clipping or renormalization is applied. Balance defect is the rounded sum
 * of error-free TwoSum event residuals, not a difference of rounded increments.
 * Requires round-to-nearest binary64, gradual underflow, and no fast-math.
 */
int bass_q_transfer_event(double donor_J_m3, double radiation_J_m3,
                         double delta_J_m3, struct bass_q_jump *output);

#ifdef __cplusplus
}
#endif
#endif
