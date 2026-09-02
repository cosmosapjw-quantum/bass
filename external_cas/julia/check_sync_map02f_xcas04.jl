#!/usr/bin/env julia

# Independent exact polynomial oracle for the bounded XCAS-04 catalog.
# Julia is the host language; Nemo supplies exact QQ polynomial arithmetic.
# The result has authority_effect=NONE and does not claim tensor
# canonicalization, positivity, inequalities, or consumer software parity.

using Nemo
using SHA

const EXPECTED_JULIA = v"1.12.7"
const EXPECTED_NEMO = v"0.56.1"

function json_escape(value::AbstractString)::String
    return replace(value, "\\" => "\\\\", "\"" => "\\\"")
end

function quoted(value::AbstractString)::String
    return "\"$(json_escape(value))\""
end

R, generators = polynomial_ring(
    QQ,
    [:l, :d, :c, :sigma, :h, :b2, :x, :tp, :g, :q],
)
l, d, c, sigma, h, b2, x, tp, g, q = generators

checks = Pair{String, Bool}[
    "weighted_pullback_split" => iszero((l + d) * c - l * c - d * c),
    "aberration_term_nonzero_generic" => !iszero(l * c),
    "harmonic_up_modulation_plus_aberration" =>
        iszero((l + d) * c - (l * c + d * c)),
    "harmonic_down_modulation_plus_aberration" =>
        iszero(-(l + 1 - d) * c - (-(l + 1) * c + d * c)),
    "d1_skew_pair" => iszero((l + 1) * c - (l + 1) * c),
    "d0_not_skew_pair" => !iszero(l * c - (l + 2) * c),
    "general_adjoint_pair" => iszero((l + d) * c - (l + d) * c),
    "rei_exact_delta" => iszero((-h) - (-h - sigma) - sigma),
    "rei_wrong_sign_rejected" => !iszero((-sigma) - sigma),
    "rei_wrong_factor_rejected" => !iszero(2 * sigma - sigma),
    "rei_foreign_constant_rejected" => !iszero(1 - sigma),
    "regular_aberration_coefficient_mod_lorentz_constraint" =>
        iszero((g - 1) * (g + 1) - b2 * g^2 - (g^2 * (1 - b2) - 1)),
    "missing_base_map_mutant_rejected" => !iszero((1 - x^2) * tp),
    "wrong_aberration_sign_mutant_rejected" => !iszero(2 * (1 - x^2) * tp),
]

julia_version_ok = VERSION == EXPECTED_JULIA
nemo_version = Base.pkgversion(Nemo)
nemo_version_ok = nemo_version == EXPECTED_NEMO
all_checks_pass = all(last(pair) for pair in checks)
all_pass = julia_version_ok && nemo_version_ok && all_checks_pass
passed = count(pair -> last(pair), checks)

manifest_path = joinpath(@__DIR__, "Manifest.toml")
manifest_sha256 = isfile(manifest_path) ? bytes2hex(sha256(read(manifest_path))) : "MISSING"

checks_json = join(
    ["$(quoted(first(pair))):$(last(pair) ? "true" : "false")" for pair in checks],
    ",",
)

fields = String[
    "\"status\":$(quoted(all_pass ? "PASS" : "FAIL"))",
    "\"engine\":\"Julia/Nemo\"",
    "\"julia_version\":$(quoted(string(VERSION)))",
    "\"expected_julia_version\":$(quoted(string(EXPECTED_JULIA)))",
    "\"nemo_version\":$(quoted(string(nemo_version)))",
    "\"expected_nemo_version\":$(quoted(string(EXPECTED_NEMO)))",
    "\"engine_role\":\"INDEPENDENT_EXACT_CAS_JULIA_FRONTEND_FLINT_BACKEND\"",
    "\"checks_total\":$(length(checks))",
    "\"checks_passed\":$(passed)",
    "\"manifest_sha256\":$(quoted(manifest_sha256))",
    "\"authority_effect\":\"NONE_EXTERNAL_ORACLE\"",
    "\"scope\":\"exact rational polynomial identities only; no tensor canonicalization, positivity, inequality, or runtime parity proof\"",
    "\"checks\":{$checks_json}",
]

println("{" * join(fields, ",") * "}")
exit(all_pass ? 0 : 1)
