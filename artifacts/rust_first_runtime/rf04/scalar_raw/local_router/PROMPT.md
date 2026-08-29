Read-only exploratory RF-04 scalar/raw integration check. Return only a concise
hazard checklist and API map; do not edit code and do not claim scientific
validation. Target owner: `_rustcore/src/kinetic/rf04_typeii.rs`. It must bridge
unchanged `generated/rust/typeii/{typeii_background,typeii_collision,typeii_kato}.rs`
and `runtime/rust/typeii/{typeii_runtime,typeii_krylov_adapt}.rs` into the existing
`_rustcore` crate, then call
`kato_aem2_step_adaptive(directions,weights,axis,gamma,h,opacity_scale,q1,mid,q3,opacity_mid,y,options)`.
Contract options are `m_init=12,m_min=8,m_max=20,tol=1e-11`,
`max_substeps=max_rejects=4096`, each basis clipped to state dimension while
phi1 keeps donor augmented behavior. Only `scalar_intensity_v1` +
`fixed_grid_raw_v1` is supported. Preserve q1 K half, A_mid-K_mid, raw collision
scaled by opacity_scale*opacity_mid, q3 K half; row0 exact; no clipping; shared-plan
errors abort, malformed batch member yields ALL_NAN/status/error. PyO3 is
validation/marshalling only; production fallback forbidden. Diagnostics must be
independently meaningful, especially raw right-null defect and
`AdaptiveKrylovStats.max_accepted_error_ratio` as a projected-residual target
ratio, not forward error. Public tests compare six real native calls to a dense
SciPy oracle; compiled mutants must kill central-K sign, rate dependence, and
q1/mid/q3 collapse. Identify likely module-inclusion/API/error-mapping/
determinism/diagnostic hazards and the minimal call graph. Do not suggest legacy
qe_evolve/qe_ensemble, formula/tolerance changes, polarized/AP capability claims,
or test weakening. Clearly label uncertainties.
