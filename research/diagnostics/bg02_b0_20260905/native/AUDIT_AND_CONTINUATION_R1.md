# BG-02 recovery R1: sequential audits and exact continuation

## Evidence precedence

The 2026-09-05 13:17 KST user checkpoint remains the requested contract.
Direct readback now finds the historical native run in REI PR #67 at
`76f7f70d1510b268a6a06c3ae9722ef68fe0ce47`. That is evidence custody, not a
transfer of BASS geometry ownership. BASS #130 source remains unchanged.
The previous conversation's assertion that no durable native receipt exists
is superseded by these fetched files, not by memory or an inferred PASS.

Two states must coexist:

- Historical PR #130 suite: actual native component calibration recorded as
  12/12, with a setup-message scope finding.
- Requested recovery-checkpoint suite: NATIVE_PENDING; no claim that the two
  sets of twelve obligations are the same.

## PHYS-MATH review — first, by this assistant

### Source-grounded survivors

At BASS commit `477371143f15ef2625a7de21a5d178b09ffc1c32`, the native
calibration source obtains Riemann and Ricci from xCoba and compares them
with separately assembled coordinate Christoffel calculations. The original
native receipt records all twelve declared Boolean checks as true.

For the locked all-lower views,

    B_abcd = g(e_d, R(e_a,e_b)e_c),  X_abcd = -B_abcd,
    Ric_ab = g^cd B_cbad = g^cd X_acbd.

Consequently a raw first-fourth contraction g^cd X_cbad is -Ric_ab. It is
not the physical X-view Ricci contraction. The variable `rawContraction`
in calibrate.wls actually uses X_acbd: it must not be cited as an independently
stored raw first-fourth contraction. No physical Ricci negation is licensed.

### Reproducible analytic witness, not a new CAS/native execution

Take tau=c*t and the source metric

    ds^2 = -d tau^2 + A^2 dx^2 + B^2 dy^2 + C^2 dz^2,
    A=exp(H1*tau), B=exp(H2*tau-a0*x), C=exp(H3*tau-a0*x).

H1,H2,H3,a0 are independent real constants of dimension L^-1. Coordinates
have length dimension, the normal is n=partial_tau, lapse is one, shift zero,
and K=+h h nabla n. Define S=H1+H2+H3.

Metric differentiation, rather than insertion of a predicted K, gives

    K_ij = (partial_tau h_ij)/2,
    K^i_j = diag(H1,H2,H3),  K=S,
    K_ij K^ij = H1^2+H2^2+H3^2.

The nonzero spatial Christoffels needed for the divergence are

    Gamma^y_xy = Gamma^z_xz = -a0,
    Gamma^x_yy = a0 B^2/A^2,
    Gamma^x_zz = a0 C^2/A^2.

For diagonal mixed K, D_j K^j_x is

    sum_j Gamma^j_jx (H1-Hj)
      = a0*(H2+H3-2*H1),

and D_x K=0. Thus C_x=(div K-D K)_x=a0*(H2+H3-2*H1), with
C_y=C_z=0. The independent coordinate curvature contraction yields
R_x0=C_x; g_x0=0 then gives G_x0=C_x.

At each fixed tau the spatial Ricci is

    Ric3_ij = -2*a0^2/A^2 * h_ij,
    R3 = -6*a0^2/A^2.

The spacetime contraction can also be written

    R00 = -(H1^2+H2^2+H3^2),
    Rii/hii = Hi*S - 2*a0^2/A^2  (no sum),
    R4 = S^2 + H1^2+H2^2+H3^2 - 6*a0^2/A^2.

Therefore

    Gnn = H1*H2 + H1*H3 + H2*H3 - 3*a0^2/A^2
        = (R3+K^2-K_ij K^ij)/2.

With T_ab=rho*n_a*n_b+n_a*q_b+q_a*n_b+p*h_ab, n_a=(-1,0,0,0),
Tnn=rho and Ti0=-qi. Keep kappa_G=8*pi*G/c^4. For
E_ab=G_ab+Lambda*g_ab-kappa_G*T_ab,

    H = E_nn = (R3+K^2-K_ij K^ij)/2-Lambda-kappa_G*rho,
    M_i = -h_i^a n^b E_ab = -C_i-kappa_G*q_i.

At tau=x=0, a0=H1=1/ell, H2=H3=0, ell>0, and q_x=0,
C_x=-2/ell^2, corrected M_x=+2/ell^2, old geometric M_x=-2/ell^2,
and their difference is +4/ell^2. This agrees with the historical native
receipt's stored discrepancy. Setting a0=0 or H1=H2=H3 removes the geometric
momentum signal, so those controls cannot expose this sign defect.

Every curvature/K-square/derivative term has dimension L^-2, as do Lambda,
kappa_G*rho and kappa_G*q_i. No Einstein on-shell condition, energy condition,
EOS, initial-value solution, full exceptional branch or non-unit-lapse claim
is introduced. The Hamiltonian difference identity being zero does NOT say
E_nn=0 for an arbitrary injected off-shell stress tensor.

### Requested twelve obligations versus historical receipt

| Recovery item | Historical evidence | Remaining explicit obligation |
| --- | --- | --- |
| 1 Metric inverse | Inverse is used internally. | No separately recorded inverse-identity check. |
| 2 Physical spatial Ricci | Full spacetime Ricci and spatial Gauss arrays survive. | Explicit spatial-Ricci view and independent BASS intrinsic/Gauss comparison. |
| 3 Raw first-fourth record | Full raw-to-BASS Riemann array is tested. | Store g^cd X_cbad separately; do not relabel X_acbd as that object. |
| 4 Physical R3 trace | Independent coordinate R3 enters Hamiltonian. | Separately named physical spatial Ricci trace comparison. |
| 5 Metric/normal-derived K | NORMAL_POSITIVE_K compares metric derivative with Gamma^0_ij. | Preserve this independent route and add the explicit fixture prediction record. |
| 6 Nonzero Bianchi V | NONZERO_BIANCHI_V reports discrepancy 4/ell^2. | Preserve the nonzero sentinel and generic pre-sentinel checks. |
| 7 Momentum/Codazzi | CODAZZI_POSITIVE_K and MOMENTUM_MATTER pass historically. | Carry exact signed comparison into the recovered contract. |
| 8 Direct Gnn/Gauss | HAMILTONIAN compares the native Einstein channel with Gauss. | Expose the direct Gnn and Gauss operands explicitly. |
| 9 Direct Gni/Codazzi | MIXED_RICCI plus the negative normal projection is checked. | Explicit Gni operand/typed-view record. |
| 10 Tnn=rho | Supported inside the symbolic Hamiltonian difference. | Dedicated native matter-projection check rather than inferred admission. |
| 11 Tni=-qi | Supported by arbitrary symbolic flux in MOMENTUM_MATTER. | Dedicated typed matter-projection check. |
| 12 Hamiltonian residual | Off-shell formula difference is tested. | Preserve that meaning; do not silently impose the Einstein constraint. |

The table is a source-based crosswalk, not twelve newly executed checks.

## PHYS-MATH-CODE review — second, by the same assistant

This is a sequential review, not a second independent reviewer.

1. `run_native.py` only sets old `test_counts` when the complete exact set is
   available. Incomplete results lose successful and failed counts.
2. Native early-exit receipts omit explicit succeeded/failed/not-evaluated
   accounting. The future native code must journal completed checks before
   possible later aborts; a wrapper cannot recover results never serialized.
3. `$MessageList` is scoped around nativeBody, after activation/xCoba load.
   Raw stdout proves one setup warning escaped this scope. Rendered-log
   scanning helps but is not proof about suppressed messages.
4. Correction to the prior chat diagnosis: Python `json.loads(tmp) != data`
   and Wolfram `back =!= safe` ALREADY compare with actual serialized payloads.
   Keep the existing writer as a regression control; do not invent a constant
   twelve-pass round-trip defect in these source bytes.
5. The inherited native-bridge implementation plan predates the B0R1 sign
   correction. Its exceptional carrier C3 is not the complete M3. Do not
   implement that old text as an unadapted momentum authority.
6. The new tests are source-only. No Python parsing, import or assertions ran
   in this session. All synthetic fixtures are explicitly test-only and must
   never be counted as native xAct evidence.

### Actual CI result, not expected RED

Test source commit: `49727115c3a85f1f5c0bbe049016812e7b7ac73f`.
Tree: `aee609c07713b538fb221e7a77fb26693b0ba2f8`.
Run: https://github.com/cosmosapjw-quantum/bass/actions/runs/33945232638
Job: `101249997056`.

The single push-triggered software workflow ended FAILURE with an empty step
list. The decoded job-log fetch returned HTTP 404 BlobNotFound. The check run
reports one annotation, but the connector rejected its annotation endpoint;
the underlying pre-step cause was NOT retrieved. Do not guess billing,
capacity, YAML syntax or a scientific cause. No retry was made.

Declared software methods: 14. Evaluated methods: 0. Therefore this is
CI_PRE_STEP_EXECUTION_BLOCKER_NOT_TEST_RED. The TDD precondition for writing
the implementation is not met. No native source, launcher, production formula,
canonical registry or peer code was changed. No GREEN is claimed.

## Continuation contract

Use this isolated child branch without replacing the historical native
receipts. First obtain an executable Python/Git environment and run exactly
this prepared test file:

    python3 -B research/diagnostics/bg02_b0_20260905/native/test_receipt_accounting.py

Record interpreter/source identity, individual results and stderr. Import,
syntax or infrastructure errors are not an accepted expected RED. Once the
feature-missing assertion failures are actually observed, implement only the
bounded launcher accounting/strict JSON/rendered-message guard described in
RECEIPT_RECOVERY_R1.md, then rerun the identical tests. Keep the original
atomic writer unless a real failing control requires a change.

After that software slice, separately implement native per-check journaling,
activation-message coverage and the explicit recovered-twelve mapping. A
fresh native run of changed source is new evidence, never a replacement for
the REI-held first run. Historical native success alone does not admit the
revised recovered contract.

The next public mathematical integration is a versioned BASS typed-view and
momentum registry/consumer amendment. Abstract four-projection equivalence,
exceptional native witnesses, constraint propagation, background evolution,
provider/science/RF04 and ready/merge gates remain open or withheld.
No whole-project completion percentage is inferred from test counts.

## Primary documentation and unresolved validation

Wolfram's $MessageList documentation limits its collection to the current
input evaluation and permits explicit resets; General::shdw documents the
context-name ambiguity. These support the message-scope diagnosis, not a
new physics claim. xCoba documentation distinguishes component work from
abstract xTensor work. SciSpace's broad search yielded no new accepted
formula-level sign authority in this bounded pass.

No plot was generated or visually audited: there was no new numerical run,
and local execution was blocked. No native/parser/software PASS can be
inferred from this written audit. The analytic witness above is a transparent
manual derivation and source cross-check, not a new CAS execution certificate.
