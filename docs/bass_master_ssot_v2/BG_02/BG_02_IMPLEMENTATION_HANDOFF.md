# BG-02 production implementation handoff

## Exact base

```text
repository  cosmosapjw-quantum/bass
base PR     #91
base branch research/bass-master-ssot-v2-alg01r2-geo02r2-w2-geo03-compose-20260902-r1
base commit 80d271cc528e1a0ffa813ecd3e3fb7610f3fa755
base tree   3fd8818938eaa0988988c6927cff799455a7a31d
```

PR #93 is a parallel EquationIR-export child.  Do not use it as the scientific
base unless its export files are intentionally stacked without changing the
PR #91 geometry modules.

## Required production paths

```text
wolfram/BASS/Kernel/Background/EinsteinProjection.wl
tests/wolfram/BASS/Background/EinsteinProjection.wlt
wolfram/BASS/Kernel/init.wl
docs/bass_master_ssot_v2/BG_02/
```

## Required public APIs

```text
BASS`Background`EinsteinResidualTensor
BASS`Background`EinsteinProjectionRegistry
BASS`Background`HamiltonianProjection
BASS`Background`MomentumProjection
BASS`Background`SpatialTraceProjection
BASS`Background`SpatialPSTFProjection
```

Add rate helpers only after the four projections pass:

```text
BASS`Background`SpatialTraceRate
BASS`Background`ADMTraceRate
BASS`Background`RaychaudhuriRate
BASS`Background`ShearLieRate
BASS`Background`ShearProjectedRate
```

## Implementation order

1. Define one abstract residual tensor
   `E_ab = G_ab + Lambda g_ab - kappaG T_ab`.
2. Derive all four projections from that object in xTensor.
3. Generate an EquationIR registry with exact dependencies on W2/W3 formula
   IDs.
4. Add homogeneous ONF adapters that call the composed curvature APIs.
5. Add the three expansion-rate forms and exact off-shell identities.
6. Add Lie/projected shear-rate adapters with derivative-kind metadata.
7. Add known-limit and adversarial tests.
8. Build a complete source packet and replay it in a fresh native xAct kernel.
9. Run PHYS-MATH, then PHYS-MATH-CODE, then plot-based adversarial audit.
10. Only then publish a Draft PR and append remote receipts.

## Mandatory design rules

1. Keep the complete residual tensor off shell.
2. Use `kappaG` or `kappa_G`; never overload Thomson `kappa`.
3. Return derivative-kind metadata for every shear rate.
4. Use `ONFRicciTensor` / `ONFScalarCurvature`, or the exact
   `ConnectionToLockedGammaOrder[LeviCivitaConnection[a,n]]` route.
5. Do not embed another Koszul formula.
6. Do not hand-enter formulas for Bianchi I through IX.
7. Keep physical `A_a=n^b nabla_b n_a` distinct from Bianchi `a_B_a`.
8. Keep the exceptional `VI_-1/9` off-diagonal momentum carrier.
9. Do not project a state onto the Hamiltonian surface inside a rate helper.
10. Store raw, ADM and Raychaudhuri rates separately.
11. Use the raw spatial-trace projection as the derivational authority;
    identify ADM/Raychaudhuri equivalence through explicit residuals.
12. Preserve exact `c` factors through `kappaG=8 pi G/c^4` and the
    `nabla_n=(1/c)d/dt` time adapter.

## Required RED-to-GREEN tests

### API and registry

- The six production APIs are absent at RED.
- The loader imports exactly one Background implementation.
- Formula IDs are unique and dependency edges are closed.
- Every projection has dimension `L^-2`.

### Physics

- Hamiltonian projection matches contracted Gauss.
- Momentum projection matches positive-K contracted Codazzi.
- Spatial trace and PSTF projections reconstruct the corresponding parts of
  the single residual tensor.
- All three off-shell rate identities reduce to zero.
- Lie and projected shear rates satisfy their exact adapter identity.

### Limits

- Flat FLRW Friedmann and `dot H` recovery.
- Flat de Sitter gives all three rates zero.
- Kasner vacuum gives `Hres=0` and
  `F_trace=F_ADM=F_Ray=-1/(3 tau^2)`.
- Bianchi I/V/II/IX scalar-curvature witnesses.
- Exceptional `VI_-1/9` momentum carrier.

### Adversarial guards

- Feeding canonical connection storage directly into locked curvature order
  must fail V and II witnesses.
- An I+IX-only witness set is explicitly rejected as insufficient.
- Reusing bare `kappa` for GR coupling must fail dimension/name validation.
- Replacing projected shear rate by Lie shear rate without metadata must fail.
- Deleting `Sigma13` after diagonalizing `n_B` must fail the exceptional
  carrier test.

### Reproducibility

- Native xTensor/xCoba reconstructs all four projections.
- Compact homogeneous ONF oracle agrees with the native route.
- Source packet includes all parent geometry, authority, IR and test files.
- Fresh replay reports zero failed and zero not evaluated.

## Required diagnostics for the later numerical node

Expose, but do not yet integrate:

```text
Hamiltonian residual Hres
momentum residual vector M_a
spatial trace residual Tres
spatial PSTF residual S_ab
F_trace - F_ADM
F_trace - F_Ray
F_ADM - F_Ray
```

The exact normalized expectations are

```text
(F_ADM-F_trace)/H^2 = -Hres/(2 H^2)
(F_trace-F_Ray)/H^2 = -Hres/(6 H^2)
(F_ADM-F_Ray)/H^2 = -2 Hres/(3 H^2)
```

## Next node after implementation

```text
BG-02C_CONSTRAINT_PROPAGATION_AND_RESIDUAL_MONITOR_DESIGN
```

That node must use Bianchi-identity propagation, not infer propagation from
constraint construction or smoke tests.

## Forbidden claims after implementation-only GREEN

```text
CONSTRAINT_PROPAGATION_VERIFIED
MATTER_DYNAMICS_CLOSED
ALL_FAMILY_BACKGROUND_INTEGRATION
NUMERICAL_PARITY
REC_REI_PROVIDER_ADMISSION
OBSERVABLE_READY
STATISTICS_READY
SCIENCE_VALIDITY
```
