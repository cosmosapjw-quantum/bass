// Reflected pairs of the ORIGINAL 96 x 32 quadrature; not a 16-node rule.
// Neumaier's compensated sum: Ogita, Rump, Oishi (2005), introductory Eq. 1.3.
#include <cmath>

namespace {
struct Sum {
    double s = 0.0, c = 0.0;
    void add(double a) {
        const double t = s + a;
        c += std::fabs(s) >= std::fabs(a) ? (s - t) + a : (a - t) + s;
        s = t;
    }
    double value() const { return s + c; }
};
}
extern "C" int rei_moments_v1(const double* q2, const double* u,
                               const double* w, double mass,
                               double x, double b, double* out) {
    if (!q2 || !u || !w || !out || !std::isfinite(mass) || mass <= 0 ||
        !std::isfinite(x) || x < 0 || x > 4 || !std::isfinite(b) || std::fabs(b) > 1)
        return 1;
    const double r = std::exp(-x), r2 = r*r, r3 = r*r*r;
    const double ep = std::exp(2*b), ez = std::exp(-4*b), m2 = mass*mass;
    double R2[16], p2factor[16];
    for (int j=0; j<16; ++j) {
        R2[j] = ep*(1-u[j]) + ez*u[j];
        const double physical_u = ez*u[j]/R2[j];
        p2factor[j] = 3*physical_u - 1;
    }
    Sum j0, j1, j2;
    for (int i=0; i<96; ++i) {
        const double radial = r2*q2[i];
        for (int j=0; j<16; ++j) {
            const double p2 = radial*R2[j];
            const double E = std::sqrt(m2+p2);
            const double v2 = p2/(E*E);
            const double weighted = (r3*w[i*16+j])*E;
            const double moving = weighted*v2;
            j0.add(weighted);
            j1.add(moving);
            j2.add((moving*0.5)*p2factor[j]);
        }
    }
    out[0] = j0.value(); out[1] = j1.value(); out[2] = j2.value();
    return std::isfinite(out[0]) && std::isfinite(out[1]) && std::isfinite(out[2]) ? 0 : 2;
}
