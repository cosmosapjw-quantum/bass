# BASS CE1-AF | 실제 원본 물리 데이터 및 claim ledger

- 2026-10-30 KST; direct parent PR #283 HEAD `50d417cb6ab9c50feaafda594a539dcbb8e2dce2`, original six positive physical cells source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.
- Horizon u∈[0,.08], metric (-,+,+,+), Λ=0, original shear, original h threshold=1e-5 unchanged, normal-frame nonthermal bolometric fractional sky.
- NEW `CE1AF_PHYSICAL_TIMELINE.csv`: 1604 actual Einstein-Vlasov states, 43 physical columns, 4 GL orders 6/8/16/64, 401 epochs each; DOP853 47 RHS evaluations each. 3 real scientific plots.
- NEW moment hierarchy identities: `E'=-θE-h·P`, `P_i'=-(θ+2h_i)Pi+Σ_jh_jRij`, `σ_i'=-3Hσ_i+Π_i`; exchange laws `E'+4HE=-W`, `Sσ'+6HSσ=W`.
- NEW exact original continuous six-cell initial moment gate: `W(0)>0.007175` (exact binary64 masses and shears; rational √2/π lower). This is NOT a uniform time-horizon positive sign theorem.

## 물리 결과 (GL64; GL16 agrees numerically)

| Quantity | u=0 | u=.08 |
|---|---:|---:|
| Fractional C2 | 0.06373396691693 | 0.05430708977646 |
| Raw energy-weighted C2 | 0.000326916048916 | 0.000197813204667 |
| Shear work W | 0.007278479477728 | 0.003852596533853 |
| Shear energy Sσ | 0.030900000000000 | 0.024299195907637 |
| Energy E | 0.900000000000000 | 0.758419059008956 |

Integrated work/E from u=0 to .08 = `0.0005201231900633711`. Volume-compensated radiation energy ratio = `0.9994800120505548`; **-0.0520%** relative to isotropic-volume dilution for this fixed model. GL16/GL64 agree in cited values to better than ~4e-12 absolute. Source quadrature convergence is **empirical**, not an exact-continuum operator enclosure.

## Validation and bottleneck

- `pytest`: original source immutable SHA and exact saved GL6/GL8 history SHA; positive 6×GL² weights; `R` symmetric PSD, R contracted to P and E; independent normal-frame Y20/Y22 direct harmonic reconstruction; finite-difference angular Liouville energy and P' at arbitrary physical ell,h; FLRW H-only limit; shear Einstein transfer; exact initial six-cell Fraction bound; correct source-tamper failure; 1604 row-data and GL16/64 convergence.
- Scoped local 24/24 tests PASS and compileall PASS (with full original 1604-row SHA-frozen data snapshot numeric replay check). Need actual test command stdout/exit and CI results before claiming remote PASS.
- Blind referee same-context: physical work is not entropy production (collisionless reversible), no temperature/P_Boltzmann assumption, not an actual CMB angular likelihood; W>0 only initially certified, sign positive in stored GL time data, but full continuous physical sign proof unresolved. `P`/`R` hierarchy is physical new observable bridge, not l4 independent new high-rank kernel proof.
- Upper BASS DAG **9/15**, 21 edges, CE1 PARTIAL; new upper closed nodes 0; scoped original R/C 18/20; native subagent NOT_AVAILABLE, genuinely distinct-author R6/C9 NOT_RUN; production_ready=false, merge_ready=false, auto_next=false.
