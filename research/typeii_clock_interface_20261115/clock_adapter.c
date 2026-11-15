#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "history.h"
#include "clock_adapter.h"
static int lane=-1,loaded=0;
static double beta[2248],betaprime[2248];
static void fail(const char *s){fprintf(stderr,"CLOCK_ADAPTER_ERROR: %s\n",s);exit(7);}
static int config(void){
 if(lane<0){
  const char *s=getenv("BASS_CLOCK_LANE");if(!s)fail("missing lane");
  const char *names[]={"legacy","reaction","thermal","both","zero","global"};
  for(int i=0;i<6;i++)if(strcmp(s,names[i])==0)lane=i;
  if(lane<0)fail("unknown lane");
 }
 return lane;
}
static void load(void){
 if(loaded)return;const char *s=getenv("BASS_CLOCK_TABLE");if(!s)fail("missing clock table");
 FILE *f=fopen(s,"r");if(!f)fail("clock table not found");char header[512];
 if(!fgets(header,sizeof(header),f)||header[0]!='#')fail("clock table header");
 for(int i=0;i<2248;i++)if(fscanf(f,"%lf %lf",beta+i,betaprime+i)!=2||!isfinite(beta[i])||!isfinite(betaprime[i])||fabs(beta[i])>=1.)fail("clock table bad row");
 double extra;if(fscanf(f,"%lf",&extra)==1)fail("clock table extra row");fclose(f);loaded=1;
}
static double field(double *a,double z){
 if(!isfinite(z)||z<0.||z>8000.)fail("clock z outside 0..8000");
 int err=0;char msg[SIZE_ErrorM]={0};double x=rec_interp1d(0.,8000./2248,a,2248,z,&err,msg);
 if(err||!isfinite(x))fail("clock interpolation failed");return x;
}
double bass_clock_gamma(double z){
 int k=config();if(k==4||z>=1700.)return 1.;load();double b=field(beta,z);
 if(fabs(b)>=1.)fail("interpolated beta superluminal");return 1./sqrt(1.-b*b);
}
double bass_clock_L(double z){
 int k=config();if(k==4||z>=1700.)return 0.;load();double b=field(beta,z),bp=field(betaprime,z);
 return b*bp/(1.-b*b);
}
double bass_reaction_scale(double z){int k=config();return (k==1||k==3||k==4)?1./bass_clock_gamma(z):1.;}
int bass_thermal_enabled(void){int k=config();return k==2||k==3||k==4;}
