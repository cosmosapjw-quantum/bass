#ifndef BASS_TWO_CLOCK_ADAPTER_H
#define BASS_TWO_CLOCK_ADAPTER_H
/* beta is dimensionless v/c; L=d log(Gamma)/d tau_H. */
double bass_clock_gamma(double z);
double bass_clock_L(double z);
double bass_reaction_scale(double z);
int bass_thermal_enabled(void);
#endif
