/* Fixed input spectrum energy moments. No atomic radiation rate is replaced.
 * Arrays share the original 2248-point uniform-z grid; native atomic step is independent.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include "history.h"
#include "clock_adapter.h"
#include "radiation_adapter.h"
static int lane=-1,loaded=0;
static double a[5][2248];
static void fail(const char *msg){fprintf(stderr,"SPECTRAL_ADAPTER_ERROR: %s\n",msg);exit(8);}
static int config(void){
 if(lane<0){
  const char *s=getenv("BASS_SPECTRAL_LANE");if(!s)fail("missing lane");
  const char *names[]={"zero","moments","energy_scalar","monopole"};
  for(int j=0;j<4;j++)if(strcmp(s,names[j])==0)lane=j;
  if(lane<0)fail("unknown lane");
 }
 return lane;
}
static void load(void){
 if(loaded)return;const char *path=getenv("BASS_SPECTRAL_TABLE");if(!path)fail("missing table");
 FILE *f=fopen(path,"r");if(!f)fail("table not found");char line[1024];
 if(!fgets(line,sizeof(line),f)||line[0]!='#')fail("table header");
 for(int i=0;i<2248;i++){
  if(fscanf(f,"%lf %lf %lf %lf %lf",&a[0][i],&a[1][i],&a[2][i],&a[3][i],&a[4][i])!=5)fail("table short or invalid");
  for(int j=0;j<5;j++)if(!isfinite(a[j][i]))fail("table nonfinite");
  if(a[0][i]<=0.||a[1][i]<=0.||a[3][i]<=0.)fail("nonpositive energy or target");
 }
 int c;do{c=fgetc(f);}while(c!=EOF&&isspace(c));if(c!=EOF)fail("table extra values");
 fclose(f);loaded=1;
}
static double field(int j,double z){
 int err=0;char msg[SIZE_ErrorM]={0};double r=rec_interp1d(0.,8000./2248,a[j],2248,z,&err,msg);
 if(err||!isfinite(r))fail("field interpolation");return r;
}
int bass_rad_identity(double z){
 if(!isfinite(z)||z<0.||z>8000.)fail("redshift domain");
 return config()==0||z>=1700.;
}
void bass_rad_values(double z,double *u,double *t,double *r){
 if(bass_rad_identity(z)){*u=1.;*t=1.;*r=-1.;return;}
 load();*u=field(0,z);
 if(lane==1){*t=field(1,z);*r=-1.+field(2,z);}
 else if(lane==3){*t=field(3,z);*r=-1.+field(4,z);}
 else {
  double g=bass_clock_gamma(z),L=bass_clock_L(z),b2=1.-1./(g*g);
  *t=pow(*u,.25);*r=-1.+.25*(2.*L+2.*L/(3.*g*g*(1.+b2/3.)));
 }
 if(*u<=0.||*t<=0.||!isfinite(*r))fail("interpolated moments invalid");
}

/* Native phase-switch criterion must measure distance to the same Compton
 * target used by the tracking equation. Keep the old arithmetic in identity
 * cases. This changes the target, NOT the source DLNT_MAX tolerance. */
double bass_spectral_tracking_lag(double Tm,double z,double T0){
 if(!isfinite(Tm)||Tm<=0.)fail("nonphysical temperature before phase switch");
 if(bass_rad_identity(z))return fabs(1.-Tm/T0/(1.+z));
 double u,t,r;bass_rad_values(z,&u,&t,&r);
 return fabs(1.-Tm/(T0*(1.+z)*t));
}
