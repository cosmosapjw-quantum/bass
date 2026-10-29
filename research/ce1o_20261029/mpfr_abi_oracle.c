/* CE1-O independent x86_64 LP64 C/MPFR ABI and directed-rounding oracle.
 * No mpfr.h dev headers in this environment. This declares the documented
 * MPFR 4-field layout and independently calls SONAME libmpfr.so.6.
 * It is a conditional ABI cross-check, NOT a general formal proof.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

_Static_assert(sizeof(long)==8 && sizeof(int)==4 && sizeof(void*)==8, "LP64 required");
typedef struct { long prec; int sign; long exp; unsigned long *d; } mpfr_t;
_Static_assert(sizeof(mpfr_t)==32, "mpfr struct mismatch");
_Static_assert(offsetof(mpfr_t,prec)==0, "prec offset mismatch");
_Static_assert(offsetof(mpfr_t,sign)==8, "sign offset mismatch");
_Static_assert(offsetof(mpfr_t,exp)==16, "exp offset mismatch");
_Static_assert(offsetof(mpfr_t,d)==24, "d offset mismatch");

extern const char* mpfr_get_version(void);
extern void mpfr_init2(mpfr_t*, long);
extern void mpfr_clear(mpfr_t*);
extern int mpfr_set_str(mpfr_t*, const char*, int, int);
extern int mpfr_set(mpfr_t*, const mpfr_t*, int);
extern int mpfr_number_p(const mpfr_t*);
extern int mpfr_cmp(const mpfr_t*, const mpfr_t*);
extern double mpfr_get_d(const mpfr_t*, int);
extern int mpfr_add(mpfr_t*,const mpfr_t*,const mpfr_t*,int);
extern int mpfr_sub(mpfr_t*,const mpfr_t*,const mpfr_t*,int);
extern int mpfr_mul(mpfr_t*,const mpfr_t*,const mpfr_t*,int);
extern int mpfr_div(mpfr_t*,const mpfr_t*,const mpfr_t*,int);
extern int mpfr_exp(mpfr_t*,const mpfr_t*,int);
extern int mpfr_sqrt(mpfr_t*,const mpfr_t*,int);
extern int mpfr_sinh(mpfr_t*,const mpfr_t*,int);
extern int mpfr_cosh(mpfr_t*,const mpfr_t*,int);
extern int mpfr_tanh(mpfr_t*,const mpfr_t*,int);

enum { RNDU=2, RNDD=3 };
static void die(const char *err) {fprintf(stderr,"ERR %s\n",err); exit(3);}
static void parse(mpfr_t lo[1],mpfr_t hi[1],const char*str){
 if(mpfr_set_str(lo,str,10,RNDD)!=0||mpfr_set_str(hi,str,10,RNDU)!=0)die("parse");
 if(!mpfr_number_p(lo)||!mpfr_number_p(hi))die("nonfinite");
}
static void pair_op(mpfr_t out[1],const mpfr_t a[1],const mpfr_t b[1],int round,const char*op){
 if(!strcmp(op,"add"))mpfr_add(out,a,b,round);
 else if(!strcmp(op,"sub"))mpfr_sub(out,a,b,round);
 else if(!strcmp(op,"mul"))mpfr_mul(out,a,b,round);
 else if(!strcmp(op,"div"))mpfr_div(out,a,b,round);
 else die("bad op");
}
static void unary_op(mpfr_t out[1],const mpfr_t a[1],int round,const char*op){
 if(!strcmp(op,"exp"))mpfr_exp(out,a,round);
 else if(!strcmp(op,"sqrt"))mpfr_sqrt(out,a,round);
 else if(!strcmp(op,"sinh"))mpfr_sinh(out,a,round);
 else if(!strcmp(op,"cosh"))mpfr_cosh(out,a,round);
 else if(!strcmp(op,"tanh"))mpfr_tanh(out,a,round);
 else die("bad unary");
}
int main(int argc,char**argv){
 if(argc==2&&!strcmp(argv[1],"layout")){
  printf("layout size=%zu prec=%zu sign=%zu exp=%zu d=%zu mpfr=%s\n",
   sizeof(mpfr_t),offsetof(mpfr_t,prec),offsetof(mpfr_t,sign),
   offsetof(mpfr_t,exp),offsetof(mpfr_t,d),mpfr_get_version());return 0;
 }
 if(argc<3)die("usage op a [b]");
 const char*op=argv[1];
 mpfr_t a[2],b[2],z[2],lo[1],hi[1],tmp[1];
 for(int i=0;i<2;i++){mpfr_init2(&a[i],192);mpfr_init2(&b[i],192);mpfr_init2(&z[i],192);}
 mpfr_init2(lo,192);mpfr_init2(hi,192);mpfr_init2(tmp,192);
 parse(&a[0],&a[1],argv[2]);
 const int is_unary =(!strcmp(op,"sqrt")||!strcmp(op,"exp")||
       !strcmp(op,"sinh")||!strcmp(op,"cosh")||!strcmp(op,"tanh"));
 if(is_unary){
  if(!strcmp(op,"sqrt") && mpfr_get_d(&a[0],RNDD)<0)die("negative sqrt");
  if(!strcmp(op,"cosh") && mpfr_get_d(&a[0],RNDD)<0)die("negative cosh");
  unary_op(&z[0],&a[0],RNDD,op);unary_op(&z[1],&a[1],RNDU,op);
 }else{
  if(argc!=4)die("binary op needs b");
  parse(&b[0],&b[1],argv[3]);
  if(!strcmp(op,"div") && mpfr_cmp(&b[0],&b[1])<=0 &&
      mpfr_get_d(&b[0],RNDD)<=0 && mpfr_get_d(&b[1],RNDU)>=0)die("division by zero");
  if(!strcmp(op,"add")){
   pair_op(&z[0],&a[0],&b[0],RNDD,op);
   pair_op(&z[1],&a[1],&b[1],RNDU,op);
  }else if(!strcmp(op,"sub")){
   pair_op(&z[0],&a[0],&b[1],RNDD,op);
   pair_op(&z[1],&a[1],&b[0],RNDU,op);
  }else if(!strcmp(op,"mul")||!strcmp(op,"div")){
   pair_op(&z[0],&a[0],&b[0],RNDD,op);
   pair_op(&z[1],&a[0],&b[0],RNDU,op);
   for(int i=0;i<2;i++)for(int j=0;j<2;j++)if(i||j){
     pair_op(tmp,&a[i],&b[j],RNDD,op);
     if(mpfr_cmp(tmp,&z[0])<0)mpfr_set(&z[0],tmp,RNDD);
     pair_op(tmp,&a[i],&b[j],RNDU,op);
     if(mpfr_cmp(tmp,&z[1])>0)mpfr_set(&z[1],tmp,RNDU);
   }
  }else die("unknown op");
 }
 if(!mpfr_number_p(&z[0])||!mpfr_number_p(&z[1]))die("nonfinite result");
 printf("lo=%a hi=%a\n", mpfr_get_d(&z[0],RNDD),mpfr_get_d(&z[1],RNDU));
 mpfr_clear(tmp);mpfr_clear(lo);mpfr_clear(hi);
 for(int i=0;i<2;i++){mpfr_clear(&a[i]);mpfr_clear(&b[i]);mpfr_clear(&z[i]);}
 return 0;
}
