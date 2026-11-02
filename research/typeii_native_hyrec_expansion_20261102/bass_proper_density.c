/* BASS source-conditional tilted class-A proper hydrogen current adapter.
 *
 * Only used in scratch copies of original HYREC history.c and helium.c.
 * Ratio(z) = Gamma(zanchor)/Gamma(z) for z<=1700, =1 for z>1700.
 * Class-A conservation: Gamma nH_rest = N0 (1+zmean)^3.
 * Original original HYREC input cosmology/atom rate sources are unchanged.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "history.h"
#include "bass_proper_density.h"

static double *gamma_ratio=NULL;
static long count=0;

static void load_factor(void) {
    const char *path=getenv("BASS_TYPEII_NH_FACTOR_FILE");
    if (!path || !*path) {
        fprintf(stderr,"BASS_NH_ERROR: missing BASS_TYPEII_NH_FACTOR_FILE\n");
        exit(6);
    }
    FILE *f=fopen(path,"r");
    if (!f) {fprintf(stderr,"BASS_NH_ERROR: no factor file\n");exit(6);}
    long cap=4096;
    gamma_ratio=(double*)malloc((size_t)cap*sizeof(double));
    if (!gamma_ratio){fprintf(stderr,"BASS_NH_ERROR: alloc\n");exit(6);}
    double x;
    while (fscanf(f,"%lf",&x)==1) {
        if (!isfinite(x)||x<=0.) {fprintf(stderr,"BASS_NH_ERROR: invalid ratio\n");exit(6);}
        if(count==cap) {fprintf(stderr,"BASS_NH_ERROR: table too long\n");exit(6);}
        gamma_ratio[count++]=x;
    }
    fclose(f);
    if(count<2000||count>3000) {fprintf(stderr,"BASS_NH_ERROR: not source Nz\n");exit(6);}
}
double bass_hydrogen_density(REC_COSMOPARAMS *cosmo, double z) {
    if (!gamma_ratio) load_factor();
    double nH=cosmo->nH0*cube(1.+z);
    if (!isfinite(nH)||nH<=0.) {fprintf(stderr,"BASS_NH_ERROR: invalid base\n");exit(6);}
    /* external C grid covers z=0..8000*(Nz-1)/Nz: above the last grid point
     * the source ratio is identically unity by construction (z>1700).
     */
    double maxz=8000.*(count-1.)/count;
    if (z>maxz) return nH;
    if(z<0.){fprintf(stderr,"BASS_NH_ERROR: negative z\n");exit(6);}
    int err=0;
    char msg[SIZE_ErrorM]={0};
    double factor=rec_interp1d(0.,8000./count,gamma_ratio,(unsigned)count,z,&err,msg);
    if (err || !isfinite(factor)||factor<=0.) {
        fprintf(stderr,"BASS_NH_ERROR: interpolation %s\n",msg);
        exit(6);
    }
    return nH*factor;
}
