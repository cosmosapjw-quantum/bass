Off Statistics;
Symbols b,x,nu,d,g,a0,a1,a2,a3,c00,c10,c01,c20,c11,c02,c30,c21,c12,c03;
Symbols h,sigmaEE,ex,ey,ez,ax,ay,az,ox,oy,oz;
Symbols s11,s12,s13,s22,s23,s33,n11,n12,n13,n22,n23,n33;
Symbols pdot,chid,pplus,omega,ii,sEE,aE,e2;

#define T0 "(a0+a1*x+a2*x^2+a3*x^3)"
#define TP "(a1+2*a2*x+3*a3*x^2)"
#define XS "(x-b+b*x^2)"
#define NS "(nu-b*nu*x)"
#define F0 "(c00+c10*nu+c01*x+c20*nu^2+c11*nu*x+c02*x^2+c30*nu^3+c21*nu^2*x+c12*nu*x^2+c03*x^3)"
#define FN "(c10+2*c20*nu+c11*x+3*c30*nu^2+2*c21*nu*x+c12*x^2)"
#define FX "(c01+c11*nu+2*c02*x+c21*nu^2+2*c12*nu*x+3*c03*x^2)"
#define FPULL "(c00+c10*`NS'+c01*`XS'+c20*`NS'^2+c11*`NS'*`XS'+c02*`XS'^2+c30*`NS'^3+c21*`NS'^2*`XS'+c12*`NS'*`XS'^2+c03*`XS'^3)"

Local I01 = g^2*(g^2-1) - (g-1)*g^2*(g+1);
Local I02 = (x+b)^2 + (1-x^2)*(1-b^2) - (1+b*x)^2;
Local I03 = (1+b*x) - b*(x+b) - (1-b^2);
Local I04 = (1+b*x) - b*(x+b) - (1-b^2);
Local I05 = (1+b*x)*(a0+a1*`XS'+a2*`XS'^2+a3*`XS'^3)
  - (`T0' + b*(x*`T0'-(1-x^2)*`TP'));
Local I06 = (1+b*x)*(a0+a1*`XS'+a2*`XS'^2+a3*`XS'^3)
  - (`T0' + b*x*`T0') + b*(1-x^2)*`TP';
Local I07 = (1+d*b*x)*`FPULL'
  - (`F0' + b*(x*(d*`F0'-nu*`FN')-(1-x^2)*`FX'));
Local I08 = (-h)-(-h-sigmaEE)-sigmaEE;

Local se1 = s11*ex+s12*ey+s13*ez;
Local se2 = s12*ex+s22*ey+s23*ez;
Local se3 = s13*ex+s23*ey+s33*ez;
Local ne1 = n11*ex+n12*ey+n13*ez;
Local ne2 = n12*ex+n22*ey+n23*ez;
Local ne3 = n13*ex+n23*ey+n33*ez;
Local radial = s11*ex^2+2*s12*ex*ey+2*s13*ex*ez+s22*ey^2+2*s23*ey*ez+s33*ez^2+ax*ex+ay*ey+az*ez;
Local I09 = ex*(radial*ex-se1-ax+oy*ez-oz*ey-ey*ne3+ez*ne2)
 + ey*(radial*ey-se2-ay+oz*ex-ox*ez-ez*ne1+ex*ne3)
 + ez*(radial*ez-se3-az+ox*ey-oy*ex-ex*ne2+ey*ne1)
 - (ex^2+ey^2+ez^2-1)*radial;
Local I10 = (pdot-2*ii*chid*pplus)+2*ii*(omega+chid)*pplus-(pdot+2*ii*omega*pplus);

id b^2 = 0;
.sort

#write <stdout> "EXPR_CHECK|I01_REGULAR_ABERRATION_COEFFICIENT|%E", I01
#write <stdout> "EXPR_CHECK|I02_AXIAL_ABERRATION_UNIT_NORM|%E", I02
#write <stdout> "EXPR_CHECK|I03_SOLID_ANGLE_JACOBIAN|%E", I03
#write <stdout> "EXPR_CHECK|I04_INVERSE_DOPPLER|%E", I04
#write <stdout> "EXPR_CHECK|I05_BLACKBODY_FULL_GENERATOR|%E", I05
#write <stdout> "EXPR_CHECK|I06_BLACKBODY_PRIMITIVE_GAP|%E", I06
#write <stdout> "EXPR_CHECK|I07_SPECTRAL_BOOST_GENERATOR|%E", I07
#write <stdout> "EXPR_CHECK|I08_REI_EXACT_SIGMA_RESIDUAL|%E", I08
#write <stdout> "EXPR_CHECK|I09_DIRECTION_FLOW_TANGENCY|%E", I09
#write <stdout> "EXPR_CHECK|I10_SCREEN_U1_COVARIANCE|%E", I10

Local M01 = -2*g*b*x;
Local M02 = b*(1-x^2);
Local M03 = -(1-x^2)*`TP';
Local M04 = -2*sigmaEE;
Local M05 = sigmaEE;
Local M06 = 1-sigmaEE;
Local M07 = -sEE-aE;
Local M08 = -4*ii*chid*pplus;
.sort

#write <stdout> "EXPR_MUTATION|M01_WRONG_DOPPLER_SIGN|%E", M01
#write <stdout> "EXPR_MUTATION|M02_WRONG_JACOBIAN_POWER|%E", M02
#write <stdout> "EXPR_MUTATION|M03_DROP_BLACKBODY_ABERRATION|%E", M03
#write <stdout> "EXPR_MUTATION|M04_REI_WRONG_SIGN|%E", M04
#write <stdout> "EXPR_MUTATION|M05_REI_WRONG_FACTOR|%E", M05
#write <stdout> "EXPR_MUTATION|M06_REI_FOREIGN_CONSTANT|%E", M06
#write <stdout> "EXPR_MUTATION|M07_DROP_DIRECTION_RADIAL_COMPENSATOR|%E", M07
#write <stdout> "EXPR_MUTATION|M08_SCREEN_CONNECTION_SIGN|%E", M08
.end
