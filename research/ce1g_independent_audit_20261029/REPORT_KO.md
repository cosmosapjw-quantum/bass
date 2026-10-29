# CE1-G independent scoped audit, 2026-10-29

## Authority and stop boundary
Parent CE1-G [Draft PR240](https://github.com/cosmosapjw-quantum/bass/pull/240) HEAD `0fd95e4baadf8982cdb1f9f81725b7b8e8fd0aa1`; parent CE1-F PR239 and alternate PR241 untouched. This is an isolated child candidate, **not** promotion or merge. Upper DAG **9/15**, CE-1 PARTIAL; `auto_next=false`, `merge_ready=false`, `production_ready=false`.

## Reproduced defects
1. **P1 unsafe unkeyed ray majorant cache.** `stored_ray_energy_majorant` cached `source._ce1c_stored_mass_cap` even though the public CE1-G certification and inherited test allow rebinding `source.mass`. Red test: after `mass *=64`, the majorant incorrectly stayed `0.9`; the correct refreshed value is `57.6`. The full-panel fourth derivative majorant must use the *current* positive mass/ray measure. Analytic falsifier on `ell_i(u)=u/2`: `P_i(u)=P_i(0)*exp(-2u)`, hence `|P_i''''(0)|=16P_i(0)`. A simple six-cell ray approximation gives true maximum ~332.8 against the obsolete bound ~168.3 at 64x. This invalidates a premise on mutable data, **not** a demonstrated final returned geometry-bound violation for the unmodified physical table.
2. **P1 missing cubic-origin identity.** `certify_tabulated_computed_path` compared the stored initial node to the source's initial state but did not check every cubic's constant coefficients against its stored left knot. A `+0.01` change to `path.coefficients[0,0,3]` was silently accepted. The initial error and inter-panel jumps refer to stored knots, so the identity is necessary.

## Bounded repair
Remove the unkeyed majorant cache so `Ecap=sum mass*||ray||` is recomputed for the present input. Reject nonidentical `path.coefficients[:,0,:]` and `path.states[:-1]`. No alteration to physical RHS, original cells/masses, RK4 method, MPFR192 precision, Taylor3+fourth formula, propagator or error tolerance. Three focused adversarial tests added.

## Actual validation
- Google Drive original CE1-G ZIP downloaded; 15,527,023 bytes, SHA256 `8657f6e7ad51b516896c0a9988644b12790b6cdc48372e14945f8232c4942448`, CRC PASS. Extracted source exact Git blob identities match PR240.
- Baseline original code: **72 targeted tests PASS**.
- Red before repair: **2 FAIL / exit 1**, specified cache and Hermite-origin witnesses.
- Green after repair: **75 targeted tests PASS / exit 0**, 3 new +72 inherited. Direct mass mutation: cap `0.9 -> 57.6`; first-panel fourth majorant `2377.899825988017 -> 136457.79434430896`.
- Independent ref8 replay `max|Delta h| <= 1.2322918653868093e-5`; matches preserved CE1-G original to quoted precision; ref8 target NOT_MET.
- Ref16 replay attempted but timed out; **NOT_PASS_THIS_RUN**. Original PR240 ref16 certificate `3.7019164499698285e-6 < 1e-5` remains historical and unmodified-fixture scoped evidence. The repair doesn't change unmodified source arithmetic, but a fresh full ref16 PASS is not claimed.
- Original CI run `40790375589` on SHA `2033870582a3` successfully executed 72 tests+wheel smoke; PR240 final HEAD's source/test/workflow blobs are identical. New isolated CI must be checked separately.
- Python 3.13.5 PYTHON_PASS; native subagent NOT_RUN; formal program proof, whole-repository policy CI, native Rust and production gates NOT_RUN/FAIL separately.

## Mathematical binding
For positive measure `partial_ell_j P_i=-(1+2delta_ij)P_i+R_ij`, `sum_j R_ij=P_i`, so `sum_j |partial_ell_j P_i|=4P_i`. In expanding h, the matrix measure of `-theta h` is `h_i-theta<=0`. These support the Dini comparison only if the current `Emax` and fourth-derivative majorant cover their **actual recorded inputs**. Hermite right-knot jumps already exist and are kept intact. The two repairs close input-identity holes only.

## Decision
`candidate_minimal_repair=LOCAL_AND_GIT_POSTED`; `independent_distinct_author_R6_C9=NOT_CLOSED`; `upper_DAG=9/15`. Review new scoped CI before accepting, do not merge automatically. Existing RF-00/RF-BENCH-00 failures remain separate.
