# BG-02 B0 convention counterexample

Status: `PASS_REPRODUCED_CONVENTION_CONFLICT`; authority gate: `FAIL_W2_W3_BG02_CONVENTION_COMPOSITION`.

This diagnostic withdraws the earlier claim in BASS PR #124 comment 5545442852 that the published momentum sign was justified by the BASS derivative-first convention. That derivation mixed a raw-xAct Codazzi row with the BASS Ricci contraction.

## Exact source

- Parent: ac3186939ffe1e37ea1af15faa910df1e320277d.
- Tree: bb5f382e58d48d6ac889a12576c4555dee8cc763.
- Four source blobs are pinned and checked by the script.
- Local execution used an exact-byte source subset, not a full Git checkout. Full checkout failed at container DNS resolution.

## Result

With metric (-,+,+,+), K_ab=+h_a^c h_b^d nabla_c n_d, q_a=-h_a^c T_cd n^d, and kappa_G=8*pi*G/c^4:

```text
B_abcd = g(e_d, R(e_a,e_b)e_c)      BASS derivative-first view
X_abcd = -B_abcd                    raw xAct view
Ric_ab = g^cd B_cbad = g^cd X_acbd  same physical Ricci
```

The existing XCobaCurvatureWitnesses module already applies the -1 raw-to-BASS adapter. The uploaded pinned xAct 1.3.0 source begins Riemann[-a,-b,-c,d] with PD[-b][Christoffel[d,-a,-c]] and contracts Ricci[-a,-b] as Riemann[-a,-c,-b,c].

The W2 rows are consistent when both four- and three-dimensional Riemann tensors use the raw X view. They cannot be silently read as BASS B components. In the BASS view:

```text
B4_abcd|spatial = B3_abcd + K_bc K_ad - K_ac K_bd
B_abc n = -D_a K_bc + D_b K_ac
h_a^c n^d Ric_cd = divK_a - D_a K
M_a = -h_a^c n^d E_cd = -divK_a + D_a K - kappa_G q_a
```

The published component oracle uses the opposite geometric sign. The matter term -kappa_G q_a is unchanged. Do not negate the physical Ricci tensor or flip every W2 coefficient.

## Nonzero in-scope witness

Take the homogeneous Bianchi V metric, with tau=c*t:

```text
ds^2 = -d tau^2 + exp(2 H1 tau) dx^2
     + exp(2 H2 tau - 2 a0 x) dy^2
     + exp(2 H3 tau - 2 a0 x) dz^2.
```

The coordinate calculation gives Ric_x,tau=divK_x-D_xK=a0*(-2 H1+H2+H3). At tau=x=0, a0=H1=1/ell, H2=H3=0, q_x=0:

```text
coordinate -h E n       +2/ell^2
published component M   -2/ell^2
difference              +4/ell^2
```

This is an off-shell identity witness, not a vacuum solution or numerical evolution. A separate flat-FLRW Gauss witness and an inhomogeneous synchronous Codazzi witness detect the same representation mismatch.

REI-MATH-M1's spatial STF divergence remains valid. For the dimensional class-B carrier C3=nB22*sigma12+(nB23-3*aB1)*sigma13, the Einstein momentum is M3=-C3-kappa_G*q3. Hubble-normalised variables need their explicit conversion. No exceptional-branch native run is claimed.

## Executed evidence

CPython 3.13.5 / SymPy 1.14.0:

```text
33/33 diagnostic groups
789 exact-zero component residuals
5/5 nonzero authority-composition counterexamples
missing-source and changed-blob controls rejected
existing receipt overwrite rejected without changing its bytes
```

These are independent coordinate-oracle checks, not production MUnit tests. The attached native RED remains 13 methods, 1 pass, 12 failures, 0 errors. No new native replay is claimed.

Script SHA-256: 310c8d40bf8b16761ce1ec64b681a47fca7fd39af5ff868a07bfe26d244572f7.
Full local result SHA-256: d0e523d7fdfb1b8f5105309a154e7c330419ef9ec8ec8decc025448499b093f6.

Fresh connected Wolfram context and evaluator both returned HTTP 502 before kernel output. No native xTensor, second-CAS, Lean, constraint propagation, production repair, provider, RF04, ready or merge claim is made.

## Replay

From this BASS checkout, with SymPy 1.14.0 available:

```bash
python research/diagnostics/bg02_b0_20260905/audit_bg02_b0.py \
  --source-root . --output /tmp/bg02_b0_fresh_receipt.json
```

Choose a new output path. Exit 0 means the registered conflict was successfully reproduced; it does not admit the authority or native bridge.

## Next node

BG02-B0R1_TYPED_RIEMANN_VIEW_AND_MOMENTUM_AUTHORITY_REPAIR.

Explicitly type the W2/W3 curvature views and their contractions; correct the public momentum geometric sign and exceptional target; then reproduce the nonzero controls in pinned xAct before native bridge admission. Preserve historical evidence and scalar controls. This diagnostic changes no production formula or convention. The authority/public-formula amendment is a separate bounded repair. R10A and REC donor research remain independent.

Literature cross-check: Gourgoulhon, arXiv:gr-qc/0703035, Secs. 2.4.2, 2.5, 4.1.3, Eq. (4.22), with K_Gourgoulhon=-K_BASS. SciSpace discovery was method-level only and supplies no repository authority.
