# KM3: independent polarized Volterra source solve

**COMPLETE_SCOPED_UNTILTED_INDEPENDENT_VOLTERRA**. Additive research on KM1 PR194,
parent `cc22af0b900dc9d2e6987e70f6ba9581f971831b`. No production code, owner branch,
old campaign budget, or main branch is changed. No merge is requested.

## What is new

Unlike KM1's supplied-source Duhamel check, `VolterraHistory` independently solves
unknown M(t). The quadratic source interpolant uses left/midpoint/right nodes;
midpoint and right sources are obtained from one causal 18x18 linear system per
panel. GL4 product quadrature integrates the kernel and interpolation weights.
A per-initial-direction 2x2 history buffer is algebraically equivalent to the
uncompressed Volterra sum, checked by `solve_global_history`. This is not a
nine-state closure or a demonstrated memory/speed optimization.

Keep full initial X0, raw det(A)/mu^3 angular measure, time-ordered screens,
bolometric full polarization, and u=t/T_star (not Q Hubble time).
`moment(t)` is an integral-reconstructed source. `source_polynomial(t)` is the
quadrature interpolant and has a separate, larger off-grid error. M is the
scattering source, not the full stress-energy or anisotropic stress.

## Verification

8 unique pytest items passed, including a monkeypatch test that forbids direct
source calls. The new science validator used7geometry histories,7direct IVPs,
23Volterra solves and1uncompressed solve; no parent campaign was rerun.

On the same10x20 angular grid, endpoint source errors for8/16/32/64/128panels were
1.8686e-7/1.1676e-8/7.2986e-10/4.5756e-11/3.0043e-12; full carrier error at128panels
was5.8692e-13. First coarse orders were4.00033 and3.99980. Fine-time gate3e-9 and
algebraic gate2e-11 were fixed before execution. Off-grid reconstructed-source
error3.3820e-11 differs from interpolant error1.7124e-8 (separate gate4e-8).

Angular endpoint differences6->10 and10->16 are1.1628e-5 and3.7173e-10, not hidden
behind same-grid agreement. Raw collision-energy balance defects are recorded.
Static P8, transparent finite-shear, positive screen, initial-source-null tail,
prefix causality, full-history assembly, product quadrature and tolerance checks
are in the raw evidence. The initial.13 Z40 tail has M(0) approximately0 but
Mzz(.55)=-.001682914925108451; dropping full X0 loses this signal.

Wolfram confirms the constant-eigenchannel endpoint expansion through order4,
with order5 coefficient `-(lambda-1)^3*lambda*(4lambda-3)/2880` relative to the
exact exponential. General variable-field order4 is empirical, not a global
certified bound. Native subagent and independent-model review are NOT_RUN.

## Reproduce

From this directory, with dependencies in requirements.txt:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests/test_volterra.py -q
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_km3.py

The second command runs only the new bounded study, not old campaigns. Vendor
files preserve exact Git blobs: source_memory9d500e36fefaa4ddc22300a2f03d9eb9cfe98403,
P8 7448ea6701f236fd41d22f3c5cadfd80f482d82f, DL2 dictionary
639c9a3b2626783da82d759a7a792bf339ec4be9. Source identities are in SOURCE_MAP.json.

The complete immutable ZIP includes detailed REPORT_KO.md, OPERATOR_CONTRACT.json,
DAG_UPDATED.json, raw rows, CAS code/result, test logs, figures and checksums.
The separate publication/delivery receipt identifies the exact archive and
verified Drive/Dropbox objects. A delivery receipt is not a scientific gate.

## Next and limitations

DAG_STATE records5/15 source-mapped/scoped units, not overall physical completion.
Next is the DV1 full-polarized harmonic streaming first slice, then the same-physics
three-path comparison. Scalar-only H/J must not be used as a full-polarized
finite-time oracle. Generic tilted normal-clock wiring, curved Bianchi, spectral
recoil, spatial averaging, Einstein feedback, production Rust/QState/Strang,
stiff-uniform convergence and independent model review remain open. Do not make
all future atomic providers prerequisites of the prescribed-field comparison.
