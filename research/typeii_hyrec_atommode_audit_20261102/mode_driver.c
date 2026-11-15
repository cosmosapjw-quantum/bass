/* Source-locked compile-time HYREC model driver; rates are in original cgs/eV.
 * MODEL determines allocation, timestep, integrator and radiation history.
 * H/nH input grids are independent of the atomic evolution grid. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include "history.h"
static void die(const char *s){fprintf(stderr,"MODE_CONTRACT_ERROR: %s\n",s);exit(2);}
static double *grid(const char *path){
 FILE *f=fopen(path,"r");if(!f)die("grid missing");
 double *a=calloc(2248,sizeof(double));if(!a)die("grid allocation");
 for(int i=0;i<2248;i++)if(fscanf(f,"%lf",a+i)!=1||!isfinite(a[i])||a[i]<=0.)die("grid length or positivity");
 int c;do{c=fgetc(f);}while(c!=EOF&&isspace(c));if(c!=EOF)die("grid trailing values");
 fclose(f);return a;
}
int main(int argc,char **argv){
 if(argc!=5)die("expected H-grid nH-factor output metadata");
 double *h=grid(argv[1]),*f=grid(argv[2]);free(f);
 if(setenv("BASS_TYPEII_NH_FACTOR_FILE",argv[2],1)!=0)die("density factor environment");
 HYREC_DATA d={0};d.path_to_hyrec="";hyrec_allocate(&d,8000.,0.);
 if(d.error)die(d.error_message);
 rec_get_cosmoparam(stdin,NULL,d.cosmo);
 double dlna=MODEL==SWIFT?DLNA_SWIFT:DLNA_HYREC;
 if(fabs(d.cosmo->dlna-dlna)>1e-17||d.Nz!=(long)(log(8001.)/dlna)+2)die("allocation/step mismatch");
 rec_build_history(&d,MODEL,h);if(d.error)die(d.error_message);
 FILE *o=fopen(argv[3],"w");if(!o)die("output open");
 fprintf(o,"# z xe Tm_K; compile-time MODEL=%d\n",MODEL);
 for(int z=8000;z>=1;z--){
  double xe=hyrec_xe(z,&d),tm=hyrec_Tm(z,&d);
  if(d.error||!isfinite(xe)||!isfinite(tm)||xe<=0.||xe>1.+2.*d.cosmo->fHe+1e-6||tm<=0.)die("invalid native state");
  fprintf(o,"%d %.15e %.15e\n",z,xe,tm);
 }
 if(fclose(o))die("output close");
 o=fopen(argv[4],"w");if(!o)die("metadata open");
 fprintf(o,"{\"model\":%d,\"dlna\":%.17g,\"Nz\":%ld,\"H_grid_N\":2248,\"transfer_flags\":[%d,%d,%d,%d,%d]}\n",MODEL,dlna,d.Nz,EFFECT_A,EFFECT_B,EFFECT_C,EFFECT_D,DIFFUSION);
 fclose(o);hyrec_free(&d);free(h);return 0;
}
