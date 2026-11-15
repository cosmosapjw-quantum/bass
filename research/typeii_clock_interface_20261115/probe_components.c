/* Native component probes, not a cosmological integration. */
#include <stdio.h>
#include <math.h>
#include "history.h"
#include "clock_adapter.h"
#include "bass_proper_density.h"
double bass_legacy_dxHIIdlna(HYREC_DATA*,int,double,double,double,double,double,double,unsigned,double);
double Tm_implicit(double,double,double,REC_COSMOPARAMS*,double,double,double);
int main(void){
 HYREC_DATA d={0};d.path_to_hyrec="";hyrec_allocate(&d,8000.,0.);if(d.error)return 2;
 rec_get_cosmoparam(stdin,NULL,d.cosmo);
 double zs[]={1500.,1100.,800.,300.};
 for(int i=0;i<4;i++){
  double z=zs[i],H=1e-13,xe=.2,Tr=d.cosmo->T0*(1+z),Tm=.8*Tr;
  double g=bass_clock_gamma(z),L=bass_clock_L(z),nH=bass_hydrogen_density(d.cosmo,z);
  double raw=bass_legacy_dxHIIdlna(&d,EMLA2s2p,xe,xe,nH,H,kBoltz*Tm,kBoltz*Tr,0,z);
  double scaled=rec_dxHIIdlna(&d,EMLA2s2p,xe,xe,nH,H,kBoltz*Tm,kBoltz*Tr,0,z);
  double K=4.91466895548409e-22*pow(Tr,4)*xe/(1+xe+d.cosmo->fHe);
  printf("%.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g\n",z,g,L,Tr,K,Tm,rec_Tmss(z,xe,d.cosmo,0.,H),rec_dTmdlna(z,xe,Tm,d.cosmo,0.,H),Tm_implicit(z,xe,Tm,d.cosmo,0.,H,.001),scaled/raw);
 }
 if(d.error){fprintf(stderr,"%s",d.error_message);return 3;}hyrec_free(&d);return 0;
}
