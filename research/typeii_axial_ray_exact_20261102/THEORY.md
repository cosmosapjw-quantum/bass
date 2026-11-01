# Original BASS Type-II axial ray exact physical research

## R1. 계약과 범위

원본 BASS PR #325의 C9 시점 고정 소스(HEAD a3bf54708db1388227b34a313ff3c8e6c250d7f5), original main 9c6506e4e2087129a8b674ff10438e5db1a55c9d 및 원본 9/9 Git blob을 기준으로, Type II 401-state 정상 tetrad의 ±ey 정확 불변광선과 conditional Thomson 단위 고유 opacity를 연구한다. 성공 조건은 정확한 수식, parent CSV의 401×2 원본 ray 및 독립 적분 일치, hostile controls, 재현 코드와 외부 백업이다. Production dispatch/real recombination/observational claims는 범위 밖이다.
## R2. 원전 및 코드 대응

Primary physical context: Pontzen & Challinor, Bianchi model CMB polarization (MNRAS 2007, arXiv:0706.2075), and Davis & Gammie, covariant radiative transfer (ApJ 888 94, DOI:10.3847/1538-4357/ab5950). Numerical authority is original BASS `runtime/rust/typeii/typeii_polarized_liouville.rs`, `generated/rust/typeii/typeii_collision.rs` and `compiler/validation/typeii_fixture_canonical.json`. Previous PR #325 `PHOTON_RAYS_401X26.csv` is the comparison target, not a proof premise for deriving the analytic formula.
