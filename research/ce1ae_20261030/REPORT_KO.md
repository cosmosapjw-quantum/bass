# CE1-AE 연구 결과 · original six-cell integrated physical kernel

증거: 조건부 정확 유리 정리 `lambda3(G)>1e-23`; 실제 원본 GL4채널 6차원 Einstein-Vlasov 시간 진화·물리 방사 sky 데이터 1604개. 숫자 적분의 λ3는 엄격 물리 오차포락이 아니다.

| GL | rays | epoch | λ1(G), numeric | λ2(G), numeric | λ3(G), numeric | <C4 fractional> | <C4 raw energy> |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 | 216 | 401 | 8.659925698485e-04 | 7.035645563849e-08 | 1.012357849153e-13 | 1.082578658007e-02 | 4.684134415383e-05 |
| 8 | 384 | 401 | 8.659925708887e-04 | 7.035645302095e-08 | 1.012353928004e-13 | 1.082578659304e-02 | 4.684134421180e-05 |
| 16 | 1536 | 401 | 8.659925708887e-04 | 7.035645302061e-08 | 1.012353927518e-13 | 1.082578659304e-02 | 4.684134421180e-05 |
| 64 | 24576 | 401 | 8.659925708887e-04 | 7.035645302061e-08 | 1.012353927649e-13 | 1.082578659304e-02 | 4.684134421180e-05 |

New physical data: `data/COUPLED_SIXCELL_DENSE_TIME_SKY.csv` (1604 rows), E, P_i, ell_i, h_i, X40/42/44, normalized and raw C4, constraint; `data/CONTINUOUS_TIME_INTEGRATED_PHYSICS.json` with Gram eigenvalues, time averages, cumulative powers, 401 vs 1601 and source-frozen Hermite comparisons.

Two competing physical statements correctly separated: normalized angular pattern C4 increases, while raw energy-sky C4^U decreases over the specified short horizon because expansion dilution dominates. This is a deterministic nonthermal radiation statement, not CMB temperature data.

## Evidence bounds
- Strict continuous integral eigenvalue λ3>1e-23 is conditional on CE1-AD #281 λ3(S41)>3e-12; rational and positivity derivations in THEORY_KO.md.
- Exact rational `G_simpson_dyadic` λ3>1e-13 validates only finite quadrature of the *stored binary64 source samples*, not the exact integral.
- No extrapolation to long-time isotropization rate, observed cosmological CMB, polarization, likelihood, or full Boltzmann closure.
- Original BASS upper DAG 9/15; original scoped R/C 18/20; R6/C9 distinct author NOT_RUN; production=false; no merge; auto_next=false.

## Independent source provenance
- Parent: cosmosapjw-quantum/bass Draft #281 pinned HEAD `f80f03d33a8b98cd49dfb9cda85ae316d868cdf6`.
- Six-cell byte identity: `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.
- GL6/GL8 original frozen input saved-state SHA256 locked (source proof), GL16/GL64 freshly computed numeric GL rays; no source mutation.
