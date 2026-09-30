# Exceptional VI_-1/9 Cauchy data — 2026-09-30

This increment supplies a dimensional Rust initial-data constructor in
`geom::exceptional_initial`, following the owner-supplied Dossier I, §§5.1 and
6.1–6.6, equations (29)–(53). The PDF is reference material, not task authority.
Base: `ab132b7ca9160becd203177dcc553c39129d386e`.

For `a=(A,0,0)` and the transverse commutator block `[[B,C],[C,D]]`,
`A != 0` and `BD-C²=-9A²` define the exceptional branch. The transverse
Codazzi map is `L=[[-(3A+C),-D],[B,C-3A]]`. Both rows are enforced, including
charts where either row vanishes. The constructor checks the longitudinal
constraint independently; satisfying the Hamiltonian alone is insufficient.

The transverse shear is `-κ L⁺q + χ v`, where `L⁺=Lᵀ/||L||F²` and `v` is a
unit kernel vector. Its largest absolute component fixes a nonnegative
orientation. The returned orthogonal image and row projectors have different
roles. Flux outside the image is rejected; it is not replaced by projected
material data. The caller supplies total normal-frame flux, density, gravitational
coupling and cosmological constant. This utility does not establish matter
realizability.

`CauchyData.in_plane` stores `[σ11, σ22, σ23]`. All geometry, shear and Hubble
components use inverse-length geometric units; `κρ`, `κq`, and `Λ` have units
of inverse length squared. They must not be passed directly into a Hubble-normalized
HHW chart or interpreted as inverse SI seconds without the appropriate conversion.

The full symmetric trace-free shear gives
`R3=-6A²-(B-D)²/2-2C²` and
`H²=(2κρ+2Λ-R3+σ:σ)/6`.
`Expansion` selects the sign of H. `amplitude_budget` fixes H and returns the
allowed `χ²`; a negative value is rejected without clipping. A zero value
selects minimum norm; a positive value permits either sign of χ.

A numerical tolerance is explicit and capped at `1e-6`. It allows floating-point
residuals, not a claim of exact rank or a change to the geometry. Nonfinite and
unsupported floating-point arithmetic fail explicitly. The module documents its
precise numeric domain and returned residuals.

## Validation scope

Host-frozen tests in `_rustcore/tests/exceptional_initial_contract.rs` cover both
zero-row charts, orthogonal projectors, incompatible flux, the analytic vacuum
family, independent longitudinal and Hamiltonian rejection, expansion/contraction,
rotated transverse frames and geometric scales from `1e-100` through `1e100`.
The existing `BianchiGroup` curvature supplies a separate comparison.

Validation: **161 Rust tests passed** (138 unit, 23 integration), as did full
workspace formatting, warnings-denied Clippy, Python-binding compilation, and exact
REC/REI dependency-pin checks. Evidence: `artifacts/exceptional_initial_20260930/`.

A fresh native Astra/xhigh review of the Sol/high candidate identified two P2
numerical defects. Host reproduced both, rejected normalization that loses a
nonzero geometry coefficient, evaluated residuals against the original geometry,
and checked both signed amplitudes before returning a positive budget. Two inline
regressions and the original unchanged frozen tests pass. This was one Host repair
episode followed by external revalidation; the repaired bytes did not receive a
second independent review. Runtime settings were confirmed from native transcripts;
read-only review describes actions, not an OS-enforced sandbox.

The determinant uses the requested relative tolerance; equation residuals use
`max(tolerance, 32*EPSILON)` times their local magnitude scale, without a
dimensionful absolute floor. A near-branch geometry can be accepted yet reject
nonzero amplitudes; its returned budget must pass the actual transverse equations.

No evolution equations, REC/REI pins, thresholds in the
existing classifier, or Python bindings are changed. Rank-changing off-branch
families, full coupled microphysics, reference histories and scientific admission
remain separate work.
