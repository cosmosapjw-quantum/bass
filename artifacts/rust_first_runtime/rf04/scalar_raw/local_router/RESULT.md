# RF-04 local-router exploratory result

- task_id: `bass-rf04-scalar-raw-api-map-20260829-r1`
- route: `LOCAL_FIRST`
- outcome: `SUCCESS`
- next_route: `RETURN_RESULT`
- model: `qwen3.6-35b-a3b`
- model_attribution: `RESPONSE_CONFIRMED`
- authority: `EXPLORATORY_NONAUTHORITATIVE`
- attempt_number: `1`
- result usage: advisory checklist only; no repository edit or claim admission

## Local model response

### Hazard checklist

- Module inclusion: duplicate symbol resolution across generated/runtime
  boundaries; crate visibility; and possible coupling-order hazards.
- API/contract: donor phi1 augmentation versus state-dimension basis clipping;
  opacity scaling placement; exact row-zero preservation; option alignment; and
  suppression of default fallbacks.
- Error mapping: shared-plan abort propagation; isolated malformed-member
  ALL_NAN/status/error serialization; strict PyO3 validation; and prevention of
  swallowed native errors or panics.
- Determinism: adaptive rejection bounds, floating-point order, bounded
  convergence, and grid/order agreement.
- Diagnostics: raw right-null defect scaling, projected-residual semantics,
  independent dense-oracle alignment, and mutation-test sensitivity.

### API map

- Entry: `kato_aem2_step_adaptive(directions, weights, axis, gamma, h,
  opacity_scale, q1, mid, q3, opacity_mid, y, options)`.
- Options: `m_init=12`, `m_min=8`, `m_max=20`, `tol=1e-11`,
  `max_substeps=4096`, `max_rejects=4096`.
- Supported mode: `scalar_intensity_v1` plus `fixed_grid_raw_v1`; reject all
  other combinations.
- Data contract: clip basis sizes to state dimension while retaining donor
  phi1 augmentation; preserve q1/K-half, A-mid minus K-mid, scaled raw
  collision, q3/K-half; exact input row zero; shared-plan abort and isolated
  malformed batch members.
- Boundary role: PyO3 validates and marshals only; no Python production
  fallback.

### Minimal call graph proposed by the local model

```text
PyO3 validate/marshal
  -> kinetic::rf04_typeii public owner
    -> typeii_krylov_adapt::kato_aem2_step_adaptive
      -> generated background/collision/Kato actions
      -> runtime transport and adaptive exp/phi1 actions
      -> AdaptiveKrylovStats ledger
  -> PyO3 result serialization or typed member error
```

### Uncertainties flagged

- Exact PyO3 array stride/layout contract.
- Exact point at which clipping interacts with augmented phi1.
- Native error-to-Python exception mapping.
- Dense/native grid alignment and diagnostic normalization.

The original response contained a few guessed internal symbol names in its call
graph; those names are not authority and must be checked against source before
use. No output was adopted as implementation.
