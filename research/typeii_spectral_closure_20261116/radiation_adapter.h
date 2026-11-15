#ifndef BASS_SPECTRAL_RADIATION_ADAPTER_H
#define BASS_SPECTRAL_RADIATION_ADAPTER_H
int bass_rad_identity(double z);
double bass_spectral_tracking_lag(double Tm,double z,double T0);
void bass_rad_values(double z,double *energy_ratio,double *target_ratio,double *target_log_derivative);
#endif
