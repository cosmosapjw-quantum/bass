# BG-02 mandatory dual audit

## PHYS-MATH AUDIT

Disposition:

```text
PASS_FORMULA_DESIGN_WITH_P0_IMPLEMENTATION_GUARD
```

### Passed

- Metric signature remains `(-,+,+,+)`.
- The positive-expansion extrinsic-curvature sign is used consistently.
- `kappa_G = 8 pi G/c^4` is not confused with Thomson opacity `kappa`.
- All four projections descend from one off-shell residual tensor.
- Hamiltonian, raw spatial-trace, trace-reversed ADM and Raychaudhuri
  expansion rates are related by explicit residual identities rather than
  silently identified.
- Physical normal acceleration `A_a` is distinct from Bianchi `a_B_a`.
- Every projection and rate has dimension `L^-2`.
- Flat FLRW, flat de Sitter and Kasner limits pass.
- The homogeneous scalar-curvature invariant passes modulo `n_B . a_B = 0`.
- The exceptional `VI_-1/9` momentum carrier is retained.
- Lie and projected-covariant shear derivatives are explicitly distinguished.

### P0 — canonical connection index order

Canonical connection storage is

```text
Gamma[[gamma,alpha,beta]]
```

whereas curvature consumes the locked view

```text
GammaLocked[[alpha,beta,gamma]].
```

Omitting the adapter gives exact but false results:

```text
Bianchi V    R3: -6   -> +4
Bianchi II   R3: -1/2 -> +3/2
```

This is silent physics corruption, not a cosmetic convention issue.  A source
guard and explicit V/II negative-control test are mandatory.

### P1

1. The current connector Wolfram kernel does not expose xTensor/xCoba, so the
   BG-02 four-projection construction has not received native xAct replay.
2. Constraint propagation is not implied by deriving the constraints.
3. Matter-provider dynamics and conservation equations are outside BG-02.
4. Every shear-rate API must declare whether it returns a Lie derivative or a
   projected covariant derivative.
5. A solver must not silently project its state onto the Hamiltonian surface.

### P2

- Free symbolic names trigger a connector-wrapper warning.  The replay is
  accepted because all eleven Boolean checks reduce to literal `True`, but the
  production test should use declared xTensor objects or locally scoped
  symbols so a clean run emits no warning.

## PHYS-MATH-CODE AUDIT

Disposition:

```text
PASS_HANDOFF_READY / PRODUCTION_NOT_IMPLEMENTED
```

### Existing durable prerequisites

- PR #91 is the exact scientific parent at
  `80d271cc528e1a0ffa813ecd3e3fb7610f3fa755`.
- PR #91 reports a fresh `158 succeeded / 0 failed / 0 not evaluated`
  Wolfram/xAct replay for composed W2/W3 geometry.
- Parallel PR #93 exports fourteen canonical BASS formulas and fifteen
  dependency edges with `175/175` fresh replay.
- The pre-existing BG-02 RED contract names six absent production APIs.

### Added by this design stage

- Complete four-projection formula contract.
- Raw/ADM/Raychaudhuri off-shell identities.
- Lie/projected shear derivative adapter.
- Homogeneous ONF momentum and scalar-curvature formulas.
- Exceptional `VI_-1/9` regression carrier.
- Exact V/II connection-order negative control.
- Executable pure-Wolfram design oracle.
- Scoped SciSpace literature lock.

### Still absent

```text
wolfram/BASS/Kernel/Background/EinsteinProjection.wl
loader registration
native xAct four-projection construction
production WLT tests
source-packet workflow
fresh connected source-packet replay
constraint-propagation module
background integrator
matter-provider closure
```

No documentation or design receipt may convert these absences into a PASS.

### Minimum implementation closeout

BG-02 implementation closes only if a fresh exact source packet reproduces:

1. one residual tensor and all four projections;
2. all three off-shell expansion-rate identities;
3. flat FLRW, de Sitter and Kasner limits;
4. I/V/II/IX curvature witnesses;
5. the deliberate wrong-index negative control;
6. the exceptional `VI_-1/9` momentum carrier;
7. exact dimensions and source ownership;
8. zero failed and zero not-evaluated tests in native Wolfram/xAct.

## Joint claim boundary

Authorized now:

```text
BG02_FORMULA_CONTRACT_DESIGNED
BG02_PURE_WOLFRAM_ORACLE_11_OF_11
BG02_CONNECTION_ORDER_P0_GUARD_IDENTIFIED
BG02_EXCEPTIONAL_MOMENTUM_CARRIER_VERIFIED
BG02_IMPLEMENTATION_HANDOFF_READY
```

Withheld:

```text
BG02_PRODUCTION_IMPLEMENTED
NATIVE_XACT_BG02_PROJECTION_PASS
CONSTRAINT_PROPAGATION_VERIFIED
BACKGROUND_NUMERICAL_EVOLUTION
ALL_FAMILY_BACKGROUND_READY
PROVIDER_ADMISSION
OBSERVABLE_READY
STATISTICS_READY
SCIENCE_VALIDITY
```
