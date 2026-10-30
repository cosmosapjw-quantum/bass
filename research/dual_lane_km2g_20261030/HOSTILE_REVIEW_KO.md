# KM-2G bounded blind referee / hostile verification (self-review, NOT distinct author)

Scope: exact original photon P8 and old Einstein KM2F source, new ideal neutral e+p split and physical opacity. A failed check is classified by failure kind; no false PASS promotion.

1. **Critical physics challenge:** Is a single cold-electron momentum inertia legitimate for neutral hydrogen? **No.** e+p identical velocity but total momentum inertia is m_e+m_p. Wrong electron-only closure amplifies recoil by 1/μ_e ≈ 1837. Required adversarial counterexample passed.
2. **Critical angular issue:** raw finite-GL photon force is not identical to analytic covariant force. Preserve δF, show Hamiltonian/momentum constraint source and nθ12/16 changes; cannot claim full exact angular continuum. Checked.
3. **Conserved current:** n_e=n_p and U_e=U_p imply J_em^a=0 identically. This does **not** solve Maxwell–Ohm–Coulomb dynamics and finite conductivity. Tested exactly for 30 raw states.
4. **Thomson normalization:** ν0 derives from proper n_e, σ_T, c, Tstar, not an arbitrary fluid opacity. Checked CODATA and SI dimension/synthetic γ0². Exact matching-ν0 limit recovers KM2F; distinct physical normalizations do not represent one observed universe.
5. **Charge transfer and orthogonality:** Fγ+F_e,net+F_p,net cancels, and Coulomb internal e/p opposite. Naive subtraction caused binary64 cancellation; stable algebra -μ_e Fγ is used with roundoff guards.
6. **Actual provider/evidence:** CI #41037404278 success, 15 pytest pass, original source hashes pinned; nested ZIP SHA/CRC all pass. Earlier CI #41037211857 failed *before science* because S0 archiver imported NumPy before dependency setup. Fixed by moving same pinned dependency installation before S0, no science changes.
7. **Independence:** Wolfram symbolic algebra and independent JSON re-summing are same-operator checks; no distinct-author R6/C9, native subagent, or full formal code proof.

Independent saved-data reaggregation across 30 rows: 
  * `rho` max absolute: `1.4210854715202004e-14`
  * `q` max absolute: `1.7763568394002505e-15`
  * `pressure` max absolute: `4.4408920985006262e-16`
  * `force` max absolute: `1.1368683772161603e-13`
  * `coulomb` max absolute: `0`
  * `electric_charge` max absolute: `0`
  * `electric_current` max absolute: `0`
  * `number` max absolute: `0`
  * `opacity` max absolute: `3.5527136788005009e-15`

`VERDICT=PASS_SCOPED_PHYSICAL_MODEL`; `PRODUCTION_READY=false`; `UPPER_DAG=9/15`; `KM2=PARTIAL`.
