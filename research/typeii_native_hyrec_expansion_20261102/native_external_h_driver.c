/* Standalone experiment using the ORIGINAL HYREC-2 rec_build_history Hubble-array API.
 * The five original C source/atom rate files remain byte-identical on owner host.
 * Run ONLY inside isolated native_run child directories: this output file is
 * the sole HYREC controlled output and must not touch the original distribution.
 * H(z_i) array grid z_i = 8000 * i / Nz, 0 <= i < Nz.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "history.h"

static void fail(const char *msg) {
    fprintf(stderr, "BASS_NATIVE_HYREC_ERROR: %s\n", msg);
    exit(2);
}
static void print_output(HYREC_DATA *rec) {
    FILE *out = fopen("output_xe.dat", "w");
    if (!out) fail("output_xe.dat cannot open in isolated CWD");
    for (double z=8000.; z>0.; z-=1.) {
        double xe=hyrec_xe(z,rec), t=hyrec_Tm(z,rec);
        if (!isfinite(xe)||!isfinite(t)||xe<0.||t<=0.) fail("nonphysical output");
        fprintf(out,"%f %1.10E %1.10E\n",z,xe,t);
    }
    fclose(out);
}
int main(int argc,char **argv) {
    if (argc<2 || argc>3) fail("usage: hyrec_h_adapter {builtin|emit_FLRW_H|external_H} [positive_H_grid_file]");
    HYREC_DATA data = {0};
    data.path_to_hyrec = "";
    hyrec_allocate(&data,8000.,0.);
    if (data.error) fail("HyRec allocate failed");
    rec_get_cosmoparam(stdin,stderr,data.cosmo);
    if (strcmp(argv[1],"builtin")==0) {
        double sentinel[] = {-1.0};
        rec_build_history(&data,MODEL,sentinel);
        if (data.error) {
            fprintf(stderr,"Native HyRec error: %s\n",data.error_message);
            return 3;
        }
        print_output(&data);
    } else if (strcmp(argv[1],"emit_FLRW_H")==0 || strcmp(argv[1],"external_H")==0) {
        long N=data.Nz;
        if (N<4 || N>2000000) fail("unexpected native Nz");
        double *h=(double*)calloc((size_t)N,sizeof(double));
        if (!h) fail("cannot allocate H array");
        if (strcmp(argv[1],"emit_FLRW_H")==0) {
            FILE *out=fopen("H_grid.dat","w");
            if (!out) fail("cannot open H_grid.dat");
            for (long i=0;i<N;i++) {
                double z=8000. * ((double)i)/N;
                h[i]=rec_HubbleRate(data.cosmo,z);
                if(!isfinite(h[i])||h[i]<=0.) fail("source native FLRW H bad");
                fprintf(out,"%.17e %.17e\n",z,h[i]);
            }
            fclose(out);
        } else {
            if(argc!=3) fail("external_H needs H grid file");
            FILE *in=fopen(argv[2],"r");
            if(!in) fail("external H file not found");
            for(long i=0;i<N;i++){
                if(fscanf(in,"%lf",&h[i])!=1) fail("incomplete external H table");
                if(!isfinite(h[i])||h[i]<=0.) fail("nonpositive or nonfinite external H");
            }
            double extra;
            if(fscanf(in,"%lf",&extra)==1) fail("external H table too many rows");
            fclose(in);
            rec_build_history(&data,MODEL,h);
            if(data.error) {
                fprintf(stderr,"Native HyRec original rec_build_history failed: %s\n",data.error_message);
                return 4;
            }
            print_output(&data);
        }
        free(h);
    } else {
        fail("unknown source-native H mode");
    }
    hyrec_free(&data);
    return 0;
}
