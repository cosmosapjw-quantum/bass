# BASS CE1-S | Physical fractional bolometric sky data closeout (2026-10-30)

## Summary and provenance

One new scoped observer-frame physics data unit extending CE1-R, not redoing original Einstein–Vlasov evolution. Independent Draft branch from PR #261 pinned `c30f7e9a4987a0f1e57d003da56738bbafe49525`; original BASS-native Rust CI run `40908995659` compiled the live original `Frame` and produced 4 channel x 41 proper-time data. PR #258 physical-history archive SHA `162097533f0bc88ec5ddee8f10edcc08aaf4b81cbf2e4c14c42982dbf73ca6b7`. PR #259 archive SHA `cc4d9cba73e4e290d2b44d892b151a429d84d6db157f029dade4c929d9183042`. Native Rust CI artifact zip SHA `21fe3b9b91b9de4e23f80fb5cba4df4b56b44b3c388bcb6999df9ad838231aa9`. Exact original binary64 six-cell input SHA `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

## Theory

Normal observer, signature (-,+,+,+), massless collisionless positive reflection-even diagonal Bianchi I Λ=0, same six-cell initial measure, proper u=t/Tstar. Define δ_U=4π U/E -1 for original *bolometric* angular-energy intensity U on the observed sky. For l>=1, Cdelta_l=(4π/E)^2 C_l, Cdelta'_l=(4π/E)^2(C'_l - 2(E'/E)C_l). This is exact for source-defined angular-energy moments. Analytic BASS Rust Liouville evolution supplies a_lm, da_lm/du, E, dE/du; **no** extra blackbody spectrum, polarization, collision, likelihood, or fluid closure.

## Actual scientific data (4 x 41 = 164 rows; GL40 not certified)

| Source channel | Rays (positive octant) | Δ Cdelta_2/Cdelta_2(0) | Δ Cdelta_4/Cdelta_4(0) | dCdelta_2/du at .08 | dCdelta_4/du at .08 |
|---|---:|---:|---:|---:|---:|
| stored_ref8 | 384 | -14.800433% | +4.197281% | -0.089747364 | +0.004433280 |
| stored_ref16 | 1536 | -14.793342% | +4.727244% | -0.089727364 | +0.004640584 |
| gl24 | 3456 | -14.790978% | +4.917324% | -0.089720694 | +0.004706450 |
| gl40 | 9600 | -14.790978% | +4.917324% | -0.089720694 | +0.004706450 |

GL40: `Cdelta_2(0)=0.063733966916931825`, `Cdelta_2(.08)=0.054307089776459157`; `Cdelta_4(0)=0.010541886035181436`, `Cdelta_4(.08)=0.011060264705919911`. The quadrupolar fractional power decreases while the hexadecapolar fractional power increases for this locked initial distribution. This does not isolate geometry alone because the initial U0 is anisotropic.

`GL24 vs GL40 max |Δ Cdelta_2|=2.0768e-14` and `max |Δ Cdelta_4|=3.4139e-15` over all 41 epochs. Independent five-point time derivative vs analytical Rust-driven Cdelta' GL40 gaps l2=`5.8668e-11`, l4=`2.8549e-12`. Simpson integral closed ΔCdelta l2=`6.0493e-13`, l4=`1.4996e-14`. No interval-certified GL40 continuum enclosure; these are empirical comparisons of source-locked numerical channels.

**New actual pointwise physical sky maps** of original continuum angular density and fractional contrast at u=0,.04,.08, each 160x320 observer pixels; numerical maps are display grids, not continuous-sphere quadrature certificates. Archived CE1-Q original GL40 map at u=.08 agrees pointwise max difference `4.1633e-17`. 164-line numeric CSV and three-epoch NPZ map are newly generated on top of original archived Rust outputs.

## Validation, boundaries, and DAG

Portable complete pinned-input package generation PASS; new local pytest `10/10 PASS`, compileall PASS, CAS Wolfram normalized-power derivative and isotropic null derivative both exactly 0 residual. Native original Rust CI `SUCCESS` at PR #261 on pinned source; **this does not certify current CE1-S Python on a new GitHub CI**. Source byte identity and ZIP CRC tested. No true independent distinct-author R6/C9 or native subagent execution; `R6/C9=NOT_RUN`.

Each R1-R10/C1-C10 has a status record under `stage_checkpoints/`, included in preserved archive and GitHub ledger; individual stages are not claimed as 20 independent remote uploads. Scoped completed 18/20. **Canonical BASS upper DAG remains 9/15 (21 edges), CE1 PARTIAL**, because an angular-energy contrast atlas alone does not establish top-level physical production/likelihood/inference gates. `production_ready=false`, `merge_ready=false`, `auto_next=false`. No merge of #258/#259/#260/#261 or sibling branches.

## Smallest safe next physics unit (not automatically started)

CE1-T: build same-source, two-epoch observer-sky angular cross-correlation K_l(u,v) = Σ_m a_lm(u) a_lm*(v)/(2l+1), plus a time-normalized counterpart; retain original six cells and source provenance and test two-time symmetry/positivity/time-diagonal equal to C_l. Do not claim stationarity, primordial stochastic predictions, or thermodynamic CMB until independently modeled. Independently review CE1-R/S analytical and implementation changes before production promotion.
