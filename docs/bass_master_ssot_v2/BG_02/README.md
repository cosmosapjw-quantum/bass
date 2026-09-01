# BASS Master SSOT v2 — BG-02 GR Background Constraint Design

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `BG_02`  
**Exact predecessor:** `c35177409909b7eef0f5c99c0c61a456b5e55117`  
**Predecessor tree:** `c2fa8cd3f34b46b9522479501a502d1ecd5ded6a`

BG-02 defines the generic spatially homogeneous GR projection and constraint
system in the locked `(-,+,+,+)` convention, with

```text
D0 = (1/c) partial_t = d/ds,
K_ab = H_geom h_ab + sigma_ab,
kappa_E = 8 pi G / c^4.
```

The authority frame is a geodesic, hypersurface-orthogonal normal congruence
with a Fermi-propagated spatial orthonormal frame. Nonzero lapse gradients,
normal vorticity and rotating component-frame terms are deferred to typed
adapters.

## Closed formula families

- normal-normal/Hamiltonian projection;
- homogeneous momentum/Codazzi projection;
- Raychaudhuri and unadjusted spatial-Einstein trace formulations;
- shear evolution;
- Bianchi structure-vector and structure-matrix evolution;
- Jacobi-constraint propagation;
- homogeneous Einstein-constraint propagation;
- normal-frame energy-balance residual;
- exact Kasner, de Sitter and Milne limits;
- an independent Type-V coordinate-metric divergence audit.

## Off-shell policy firewall

Two equation sets are physically equivalent on the constraint surface but not
identical off it:

```text
spatial_einstein_unadjusted:
    D0 H = RaychaudhuriRHS - C_H/12
    D0 C_H = -3 H C_H - 2 D_a C_M^a

raychaudhuri_adjusted:
    D0 H = RaychaudhuriRHS
    D0 C_H = -2 H C_H - 2 D_a C_M^a
```

The current legacy Type-V metric audit corresponds to the first policy. A
runtime must declare its policy; silent mixing is forbidden.

## Run

```bash
wolframscript -file wolfram/scripts/run_stage.wls --stage BG_02
```

## Claim ceiling

```text
PASS_BG02_GR_PROJECTION_DESIGN
PASS_BG02_CONSTRAINT_PROPAGATION_DESIGN
PASS_BG02_TYPE_V_METRIC_AUDIT

NO_ALL_ELEVEN_BRANCH_BACKGROUND_SUPPORT
NO_MATTER_MODEL_CLOSURE
NO_TILTED_MATTER_EVOLUTION
NO_CHART_EVENT_IMPLEMENTATION
NO_NUMERICAL_PARITY
NO_GENERIC_ELL_COMPILER_CORRECTNESS
NO_CROSS_REPOSITORY_COMPATIBILITY
NO_SCIENCE_VALIDITY
NO_PASS_RF04
```
