# BG-02 B0R1 typed-view reference candidate

Status: `PASS_REFERENCE_CANDIDATE_NATIVE_PENDING`. This is a child of diagnostic PR #128, not a replacement for the BASS production kernel or canonical formula registry.

## Recovery

The exact PR #128 audit script was recovered from GitHub and the four audited source files were recovered from mounted source packets and the attached traceback. All four Git blobs match. A fresh CPython 3.13.5 / SymPy 1.14.0 execution reproduced 33/33 groups, 789 exact-zero component residuals and five nonzero convention-composition counterexamples. The full receipt SHA-256 again equals d0e523d7fdfb1b8f5105309a154e7c330419ef9ec8ec8decc025448499b093f6.

Direct container Git transport failed DNS, so no full checkout/build is claimed. The user's 13-method source-adversarial RED is historical evidence, not a new MUnit execution.

## Implemented reference functions

`candidate/typed_views.py` introduces an explicit `CurvatureView` enum and separate Riemann-component conversion and physical-Ricci contraction. Unknown/untyped views, incompatible layouts and missing momentum arguments are rejected.

```text
B_abcd = g(e_d,R(e_a,e_b)e_c)
X_abcd = -B_abcd
Ric_ab = g^cd B_cbad = g^cd X_acbd

K_ab = +h_a^c h_b^d nabla_c n_d
q_a = -h_a^c T_cd n^d
M_a = -D^b K_ab + D_a K - kappa_G q_a
kappa_G = 8*pi*G/c^4
```

Do not negate physical Ricci when changing Riemann view. Do not negate the matter term while fixing the geometric momentum sign. Input arrays are assumed to be genuine algebraic Riemann tensors; this helper validates layout, not all tensor symmetries or field equations. Coordinates in the unit sentinel tests are measured in one fixed length unit; the parent diagnostic retains symbolic ell and tau=c*t.

The generic dimensional class-B carrier is derived in the new tests from structure constants and the Koszul connection, independently of the candidate:

```text
C3 = D_b sigma^(3b) = nB22*sigma12 + (nB23-3*aB1)*sigma13
M3 = -C3 - kappa_G*q3
```

This is not an exceptional VI_-1/9 branch certificate, and Hubble-normalised inputs require an explicit adapter.

## Executed behavioral tests

```text
new candidate absent    9 tests / 9 assertion failures / 0 errors
reference candidate    9 tests / 9 pass / 0 errors
old momentum restored  9 tests / 3 failures / 0 errors
```

The three mutant detections are the nonzero Bianchi V momentum, nonzero spatial-gradient momentum, and Koszul-derived class-B momentum. FLRW is a control, not a sufficient momentum witness.

One test initially used structural equality between expanded and factorised expressions. It was changed to exact zero of their difference, without changing the expected polynomial. The failed attempt is retained in the downloadable recovery packet. This review was a separate self-review pass, not an independent agent audit.

## Replay

```bash
python research/diagnostics/bg02_b0_20260905/test_b0r1_candidate.py
```

`candidate/B0R1CoordinateReplay.wls` supplies a plain Wolfram coordinate cross-check. It is prepared but unexecuted here, and deliberately does not load xAct:

```bash
BASS_B0R1_RECEIPT=/tmp/bg02_b0r1_wl_new.json \
  timeout --kill-after=5s 90s wolframscript -file \
  research/diagnostics/bg02_b0_20260905/candidate/B0R1CoordinateReplay.wls
```

Connected Wolfram Context and Evaluator returned MCP SSE HTTP 404 before kernel output in this recovery turn. This differs from the prior 502 and is not a mathematical failure.

## Next node and boundaries

`BG02-B0R1-NATIVE_TYPED_VIEW_CALIBRATION`: reproduce the nonzero Bianchi V witness in the user's pinned xAct environment with explicit X/B views and their Ricci contractions. Collect this primary receipt independently of auxiliary CAS. Then apply an explicitly versioned public momentum/formula amendment in a separate bounded repair, preserving old evidence. The full Gauss-Codazzi bridge, constraint propagation, solver and providers remain unimplemented/unadmitted.

No production file, canonical registry, workflow, provider, ready state, merge state, or peer-repository source was changed by this candidate. R10A and REC donor research remain parallel.

Primary literature check: E. Gourgoulhon, arXiv:gr-qc/0703035, Secs. 2.4.2 and 4.1.3, Eq. (4.22), with K_Gourgoulhon=-K_BASS. SciSpace is literature discovery only, not repository authority.
