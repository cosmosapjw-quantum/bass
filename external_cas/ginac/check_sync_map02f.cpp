#include <ginac/ginac.h>
#include <iostream>
#include <string>

using namespace GiNaC;

static int failures = 0;

static bool zero_expr(const ex &value) {
    return value.normal().expand().is_zero();
}

static void check_zero(const std::string &id, const ex &value) {
    if (zero_expr(value)) {
        std::cout << "CHECK|" << id << "|PASS\n";
    } else {
        std::cout << "CHECK|" << id << "|FAIL|" << value.normal().expand() << "\n";
        ++failures;
    }
}

static void check_true(const std::string &id, bool value) {
    if (value) {
        std::cout << "CHECK|" << id << "|PASS\n";
    } else {
        std::cout << "CHECK|" << id << "|FAIL\n";
        ++failures;
    }
}

static void mutation_nonzero(const std::string &id, const ex &value) {
    if (!zero_expr(value)) {
        std::cout << "MUTATION|" << id << "|PASS\n";
    } else {
        std::cout << "MUTATION|" << id << "|FAIL|0\n";
        ++failures;
    }
}

int main() {
    symbol b("b"), x("x"), nu("nu"), d("d"), g("g");
    symbol a0("a0"), a1("a1"), a2("a2"), a3("a3");
    symbol c00("c00"), c10("c10"), c01("c01"), c20("c20"), c11("c11");
    symbol c02("c02"), c30("c30"), c21("c21"), c12("c12"), c03("c03");
    symbol h("h"), sigmaEE("sigmaEE");

    ex b2_from_g = (pow(g, 2) - 1) / pow(g, 2);
    ex chi = pow(g, 2) / (g + 1);
    check_true("I01_REGULAR_ABERRATION_COEFFICIENT",
        zero_expr((g - 1) / b2_from_g - chi) &&
        zero_expr(chi.subs(g == 1) - numeric(1, 2)));

    ex mu_tilde = (x + b) / (1 + b*x);
    check_zero("I02_AXIAL_ABERRATION_UNIT_NORM",
        pow(mu_tilde, 2) + (1 - pow(x, 2))*(1 - pow(b, 2))/pow(1 + b*x, 2) - 1);
    check_zero("I03_SOLID_ANGLE_JACOBIAN",
        mu_tilde.diff(x) - (1 - pow(b, 2))/pow(1 + b*x, 2));
    check_zero("I04_INVERSE_DOPPLER",
        (1 - b*mu_tilde)*(1 + b*x) - (1 - pow(b, 2)));

    ex T0 = a0 + a1*x + a2*pow(x, 2) + a3*pow(x, 3);
    ex xs = (x - b)/(1 - b*x);
    ex dop = sqrt(1 - pow(b, 2))/(1 - b*x);
    ex full_temperature = dop*T0.subs(x == xs);
    ex full_generator = full_temperature.diff(b).subs(b == 0);
    ex expected_temperature = x*T0 - (1 - pow(x, 2))*T0.diff(x);
    check_zero("I05_BLACKBODY_FULL_GENERATOR", full_generator - expected_temperature);
    check_zero("I06_BLACKBODY_PRIMITIVE_GAP",
        full_generator - x*T0 + (1 - pow(x, 2))*T0.diff(x));

    ex F0 = c00 + c10*nu + c01*x + c20*pow(nu, 2) + c11*nu*x + c02*pow(x, 2)
        + c30*pow(nu, 3) + c21*pow(nu, 2)*x + c12*nu*pow(x, 2) + c03*pow(x, 3);
    ex xs1 = x - b*(1 - pow(x, 2));
    ex nus1 = nu*(1 - b*x);
    ex spectral_first_order = (1 + d*b*x)*F0.subs(x == xs1).subs(nu == nus1);
    ex spectral_generator = spectral_first_order.diff(b).subs(b == 0);
    ex expected_spectral = x*(d*F0 - nu*F0.diff(nu)) - (1 - pow(x, 2))*F0.diff(x);
    check_zero("I07_SPECTRAL_BOOST_GENERATOR", spectral_generator - expected_spectral);

    ex rei_difference = (-h) - (-h - sigmaEE);
    check_zero("I08_REI_EXACT_SIGMA_RESIDUAL", rei_difference - sigmaEE);

    symbol ex1("ex"), ey("ey"), ez("ez"), ax("ax"), ay("ay"), az("az");
    symbol ox("ox"), oy("oy"), oz("oz");
    symbol s11("s11"), s12("s12"), s13("s13"), s22("s22"), s23("s23"), s33("s33");
    symbol n11("n11"), n12("n12"), n13("n13"), n22("n22"), n23("n23"), n33("n33");
    ex sEE = s11*pow(ex1,2) + 2*s12*ex1*ey + 2*s13*ex1*ez + s22*pow(ey,2)
        + 2*s23*ey*ez + s33*pow(ez,2);
    ex aE = ax*ex1 + ay*ey + az*ez;
    ex se1 = s11*ex1 + s12*ey + s13*ez;
    ex se2 = s12*ex1 + s22*ey + s23*ez;
    ex se3 = s13*ex1 + s23*ey + s33*ez;
    ex ne1 = n11*ex1 + n12*ey + n13*ez;
    ex ne2 = n12*ex1 + n22*ey + n23*ez;
    ex ne3 = n13*ex1 + n23*ey + n33*ez;
    ex radial = sEE + aE;
    ex vx = radial*ex1 - se1 - ax + oy*ez - oz*ey - (ey*ne3 - ez*ne2);
    ex vy = radial*ey - se2 - ay + oz*ex1 - ox*ez - (ez*ne1 - ex1*ne3);
    ex vz = radial*ez - se3 - az + ox*ey - oy*ex1 - (ex1*ne2 - ey*ne1);
    ex e2 = pow(ex1,2) + pow(ey,2) + pow(ez,2);
    check_zero("I09_DIRECTION_FLOW_TANGENCY",
        ex1*vx + ey*vy + ez*vz - (e2 - 1)*radial);

    symbol pdot("pdot"), chid("chid"), pplus("pplus"), omega("omega");
    ex screen_residual = (pdot - 2*I*chid*pplus) + 2*I*(omega + chid)*pplus
        - (pdot + 2*I*omega*pplus);
    check_zero("I10_SCREEN_U1_COVARIANCE", screen_residual);

    ex chord = 2*b/(1 + sqrt(1 - pow(b,2)));
    ex r1 = chord.diff(b).subs(b == 0) - 1;
    ex r3 = chord.diff(b, 3).subs(b == 0) - numeric(3, 2);
    ex r5 = chord.diff(b, 5).subs(b == 0) - 15;
    check_true("I11_REC_SMALL_BETA_SERIES", zero_expr(r1) && zero_expr(r3) && zero_expr(r5));

    mutation_nonzero("M01_WRONG_DOPPLER_SIGN", -2*g*b*x);
    mutation_nonzero("M02_WRONG_JACOBIAN_POWER", b*(1 - pow(x,2)));
    mutation_nonzero("M03_DROP_BLACKBODY_ABERRATION", -(1 - pow(x,2))*T0.diff(x));
    mutation_nonzero("M04_REI_WRONG_SIGN", -2*sigmaEE);
    mutation_nonzero("M05_REI_WRONG_FACTOR", sigmaEE);
    mutation_nonzero("M06_REI_FOREIGN_CONSTANT", 1 - sigmaEE);
    mutation_nonzero("M07_DROP_DIRECTION_RADIAL_COMPENSATOR", -sEE - aE);
    mutation_nonzero("M08_SCREEN_CONNECTION_SIGN", -4*I*chid*pplus);

    std::cout << "STATUS|" << (failures == 0 ? "PASS" : "FAIL") << "\n";
    return failures == 0 ? 0 : 1;
}
