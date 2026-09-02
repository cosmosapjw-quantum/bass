import edu.jas.arith.BigRational;
import edu.jas.poly.GenPolynomial;
import edu.jas.poly.GenPolynomialRing;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Independent exact polynomial oracle for the bounded XCAS-04 catalog.
 *
 * <p>The program uses Java Algebra System for parsing and zero testing.  It
 * does not call a Wolfram or SymPy simplifier and has no tensor, positivity,
 * or inequality authority.</p>
 */
public final class CheckSyncMap02fXcas04 {
    private static GenPolynomialRing<BigRational> ring;

    private CheckSyncMap02fXcas04() {}

    private static boolean isZero(String expression) {
        final GenPolynomial<BigRational> polynomial = ring.parse(expression);
        return polynomial.isZERO();
    }

    private static boolean isNonZero(String expression) {
        return !isZero(expression);
    }

    private static String quote(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    public static void main(String[] args) {
        final String[] variables = {
            "l", "d", "c", "sigma", "h", "b2", "x", "tp", "g", "q"
        };
        ring = new GenPolynomialRing<BigRational>(new BigRational(1), variables);

        final Map<String, Boolean> checks = new LinkedHashMap<>();
        checks.put("weighted_pullback_split", isZero("(l+d)*c-l*c-d*c"));
        checks.put("aberration_term_nonzero_generic", isNonZero("l*c"));
        checks.put(
            "harmonic_up_modulation_plus_aberration",
            isZero("(l+d)*c-(l*c+d*c)")
        );
        checks.put(
            "harmonic_down_modulation_plus_aberration",
            isZero("(0-(l+1-d)*c)-((0-(l+1)*c)+d*c)")
        );
        checks.put("d1_skew_pair", isZero("(l+1)*c+(0-(l+1)*c)"));
        checks.put("d0_not_skew_pair", isNonZero("l*c+(0-(l+2)*c)"));
        checks.put("general_adjoint_pair", isZero("(l+d)*c+(0-(l+d)*c)"));
        checks.put("rei_exact_delta", isZero("(0-h)-(0-h-sigma)-sigma"));
        checks.put("rei_wrong_sign_rejected", isNonZero("(0-sigma)-sigma"));
        checks.put("rei_wrong_factor_rejected", isNonZero("2*sigma-sigma"));
        checks.put("rei_foreign_constant_rejected", isNonZero("1-sigma"));
        checks.put(
            "regular_aberration_coefficient_mod_lorentz_constraint",
            isZero("(g-1)*(g+1)-b2*g^2-(g^2*(1-b2)-1)")
        );
        checks.put("missing_base_map_mutant_rejected", isNonZero("(1-x^2)*tp"));
        checks.put(
            "wrong_aberration_sign_mutant_rejected",
            isNonZero("2*(1-x^2)*tp")
        );

        final long passed = checks.values().stream().filter(Boolean::booleanValue).count();
        final boolean allPass = passed == checks.size();
        final String jarSha256 = System.getenv().getOrDefault("JAS_JAR_SHA256", "MISSING");

        final StringBuilder json = new StringBuilder();
        json.append('{');
        json.append("\"status\":").append(quote(allPass ? "PASS" : "FAIL"));
        json.append(",\"engine\":\"Java Algebra System\"");
        json.append(",\"version\":\"2.7.200\"");
        json.append(",\"java_version\":").append(quote(System.getProperty("java.version")));
        json.append(",\"jar_sha256\":").append(quote(jarSha256));
        json.append(",\"engine_role\":\"INDEPENDENT_EXACT_POLYNOMIAL_CAS\"");
        json.append(",\"checks_total\":").append(checks.size());
        json.append(",\"checks_passed\":").append(passed);
        json.append(",\"authority_effect\":\"NONE_EXTERNAL_ORACLE\"");
        json.append(",\"scope\":\"polynomial or cleared-denominator identities only; no tensor canonicalization, positivity, or inequality proof\"");
        json.append(",\"checks\":{");
        boolean first = true;
        for (Map.Entry<String, Boolean> entry : checks.entrySet()) {
            if (!first) {
                json.append(',');
            }
            first = false;
            json.append(quote(entry.getKey())).append(':').append(entry.getValue());
        }
        json.append("}}");
        System.out.println(json);

        if (!allPass) {
            System.exit(1);
        }
    }
}
