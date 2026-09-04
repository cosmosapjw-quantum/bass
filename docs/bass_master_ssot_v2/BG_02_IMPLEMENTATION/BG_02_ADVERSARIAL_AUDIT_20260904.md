# BG-02 adversarial audit and claim correction — 2026-09-04

## Exact audited state

```text
repository  cosmosapjw-quantum/bass
PR          #124
head        9fe87d4938b8290f97c9e0975e0e8f5b2b9e0f4f
base        80d271cc528e1a0ffa813ecd3e3fb7610f3fa755
status      OPEN / DRAFT / NOT MERGED
```

Scientific code ancestry remains PR #91.  PR #94 is the BG-02 design authority.  PR #120 is a semantic dependency reference and is not code ancestry.

## Audit verdict

```text
STOP_INVALID_AS_BG02_PRODUCTION_GREEN
PASS_COMPONENT_FORMULA_ORACLE_ONLY
NATIVE_XTENSOR_GAUSS_CODAZZI_BRIDGE_REQUIRED
```

The scalar formulas and known limits are useful and several independent algebra checks pass, but the current implementation does not yet satisfy the central design requirement: one actual xTensor residual tensor whose four projections are reduced to the component formulas through the locked Gauss–Codazzi geometry.

## Severity-ranked findings

### P0-1 — API/representation mismatch

`BASS`Background`EinsteinResidualTensor` currently returns an `Association` produced by `residualComponents`; it is not an indexed xTensor expression.  Therefore the statements “one residual tensor is implemented” and “all projections are derived from that tensor” are not established.

Required correction: separate the current formulas into a clearly named component oracle and implement a distinct native xTensor residual/projection layer.  The public tensor API may be admitted only when `xTensorQ`/tensor-expression checks and exact reconstruction residuals pass.

### P0-2 — circular projection checks

The current Hamiltonian, momentum, spatial-trace and spatial-PSTF residuals subtract each component formula from the same formula returned by the same association.  These are algebraic self-comparisons, not a bridge from spacetime curvature.

Required correction: construct

```text
E_ab = G_ab + Lambda g_ab - kappa_G T_ab
```

as an actual xTensor expression and compute

```text
H_native   = n^a n^b E_ab
M_native_a = -h_a^c n^d E_cd
T_native   = h^ab E_ab / 3
S_native_ab= h_a^c h_b^d E_cd - T_native h_ab
```

before applying independently registered Gauss, Codazzi and Ricci projection rules.

### P0-3 — hard-coded positive audit claims

The production source hard-codes positive values for `dependency_graph_closed`, `single_off_shell_residual_authority`, `I_IX_only_witness_set_rejected`, and `second_koszul_implementation_absent`.  `normal_acceleration_distinct_from_bianchi_a` is implemented as syntactic `UnsameQ` between two symbols.  None of these are independent proofs.

Required correction: every positive gate must be computed from source/registry structure or exact symbolic residuals.  A pending or unavailable computation must return `False`, `Missing[...]`, or `Failure[...]`, never literal `True`.

### P0-4 — exceptional VI_-1/9 witness is tautological

The current exceptional residual is the expression

```text
X - X
```

and the deletion mutant merely checks that a free symbolic product is not identically zero.  This does not derive the carrier from the homogeneous momentum projection.

Required correction: evaluate the normal-spatial Einstein projection in the exceptional branch and compare the resulting third component with

```text
N22 Sigma12 + (N23 - 3 A) Sigma13.
```

The negative mutation must be applied to the derived branch expression.

### P1-1 — duplicate manual curvature path in production source

`wrongOrderScalarCurvature` manually constructs a Riemann/Ricci/scalar expression inside the production module.  Even though it is labelled a negative control, this creates a second curvature path in the production source and makes the claim `second_koszul_implementation_absent -> True` misleading.

Required correction: move all wrong-order controls into a test-only module.  Production may call only `ONFRicciTensor`, `ONFScalarCurvature`, or `ConnectionToLockedGammaOrder[LeviCivitaConnection[...]]`.

### P1-2 — silent malformed-input fallback

`state[_] := <||>` silently turns malformed input into a symbolic default state, and projection `Lookup` calls return the whole association when a key is absent.

Required correction: malformed state types and missing component keys must return explicit `Failure` objects.  Symbolic defaults may be requested only through `Automatic`.

### P1-3 — native runner cannot preserve the failures it is meant to diagnose

The published runner does not activate pinned xAct before loading BASS, uses `NameQ` as package evidence, exits before writing receipts on early failures, and validates JSON round trips against all-GREEN counts `26/0/0`.  A legitimate `25/1/0` diagnostic RED is therefore not durably representable.

Required correction: activate the exact xAct archive before full BASS init; verify `$Packages` plus real definitions; route every exit through one atomic receipt writer; compare round-tripped counts with the serialized receipt, while retaining `26/0/0` only as the final promotion gate.

### P1-4 — fixed count is weaker than a named-test contract

A count of 26 can pass with the wrong set of tests.

Required correction: record and validate the exact required `TestID` set and its canonical hash, together with failed and not-evaluated IDs.

### P1-5 — optional CAS lanes were allowed to block the primary physics execution

SymPy, Octave, SageMath, Singular and Lean largely check copied forms of the same three scalar polynomial identities.  They are useful corroboration but are not five independent derivations of the tensor geometry.  Serially gating xAct on every auxiliary executable created a meta-loop and delayed the only load-bearing physics check.

Required correction: run the pinned xAct structural/bridge lane independently.  Auxiliary CAS lanes publish per-lane receipts and may gate a multi-CAS corroboration claim, but they must not prevent collection of the native xAct receipt.

### P2-1 — c-factor adapter remains documentary

The registry states `kappa_G=8 pi G/c^4` and `nabla_n=(1/c)d/dt`, but no executable physical-time adapter is present.

Required correction: keep the geometric evolution in proper-length derivative `nabla_n`; add a separately named physical-time adapter and a dimensional test before numerical evolution.

## Results that survive the audit

The following statements remain valid within their stated scope:

```text
- the PR #91 W2 sign registry fixes (-,+,+,+) and K_ab=+h h nabla n;
- the component Hamiltonian, spatial-trace, ADM and Raychaudhuri formulas are mutually consistent off shell;
- the three scalar rate identities vanish exactly;
- flat FLRW, flat de Sitter and Kasner scalar controls are consistent;
- locked/wrong connection-order scalar-curvature witnesses discriminate V and II;
- SageMath and Singular exact scalar checks passed locally;
- Lean/mathlib resolved and compiled the three scalar identities in a local Lake environment;
- none of these facts establishes the native tensor bridge.
```

## Corrected mathematical target

Let

```text
h_ab = g_ab + n_a n_b,
n^a n_a = -1,
K_ab = H h_ab + sigma_ab,
E_ab = G_ab + Lambda g_ab - kappa_G T_ab.
```

For symmetric `E_ab`, define

```text
H = n^a n^b E_ab,
M_a = -h_a^c n^d E_cd,
T = h^ab E_ab/3,
S_ab = h_a^c h_b^d E_cd - T h_ab.
```

The first exact theorem is the representation identity

```text
E_ab = H n_a n_b + 2 n_(a M_b) + T h_ab + S_ab,
```

with `n^a M_a=0`, `n^a S_ab=0`, `h^ab S_ab=0`, and `S_[ab]=0`.

The second exact theorem is the Gauss–Codazzi/Ricci bridge under the PR #91 sign registry:

```text
H = (R3 + K^2 - K_ab K^ab)/2 - Lambda - kappa_G rho,
M_a = D^b K_ab - D_a K - kappa_G q_a,
T = -R3/6 - 2 L_n H - 3 H^2 - sigma^2/2
    + 2(D.A+A^2)/3 + Lambda - kappa_G p,
S_ab = R3_<ab> + (L_n K_ab)_<ab> + K K_<ab>
     - 2 K_c<a K_b>^c - D_<a A_b> - A_<a A_b> - kappa_G pi_ab.
```

Only the exact vanishing of the four native-minus-component residuals may set the native derivation gate true.

## Corrected execution order

```text
1. claim correction and adversarial RED
2. structural xTensor decomposition of an arbitrary symmetric E_ab
3. matter and Lambda projection-sign tests
4. executable Gauss/Codazzi/Ricci bridge rules
5. four native-minus-component residuals
6. homogeneous ONF/xCoba dual witnesses, including V, II and VI_-1/9
7. named MUnit contract and atomic receipts
8. auxiliary CAS corroboration in parallel
9. PHYS-MATH and PHYS-MATH-CODE reviews
10. bounded implementation closeout
```

## Claim ceiling after this audit

Authorized:

```text
BG02_COMPONENT_FORMULA_ORACLE_AVAILABLE
BG02_SCALAR_OFF_SHELL_IDENTITIES_MULTI_CAS_PASS
BG02_PR91_SIGN_REGISTRY_PINNED
BG02_NATIVE_BRIDGE_ADVERSARIAL_AUDIT_COMPLETE
```

Withheld:

```text
BG02_SOURCE_GREEN
BG02_PRODUCTION_IMPLEMENTATION_COMPLETE
NATIVE_XACT_BG02_PROJECTION_PASS
GAUSS_CODAZZI_COMPONENT_BRIDGE_PASS
CONSTRAINT_PROPAGATION_VERIFIED
BACKGROUND_NUMERICAL_EVOLUTION
PROVIDER_ADMISSION
OBSERVABLE_READY
LIKELIHOOD_READY
SCIENCE_VALIDITY
PASS_RF04
READY_OR_MERGE
```
