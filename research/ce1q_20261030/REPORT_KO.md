# BASS CE1-Q | 실제 관측자계 angular-energy sky와 저차 조화계수

**2026-10-30 KST · scoped model physics result · original upper DAG 9/15**

## 1. Source reconstruction

- `cosmosapjw-quantum/bass` CE1-P physical-history parent Draft PR #258 HEAD `0656e98989750de4ea19c510ff2052654aaa3eda`, based on PR #253 `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0`.
- Independent sibling CE1-P BASS Rust E/P/J PR #257 HEAD `baa29ff5b5d0384f62e2627ebc8b37d34d7aa26b`, based on CE1-O PR #256. It provides BASS-native `Frame` parity and has successful CI; neither branch was imported or merged.
- Actual original frozen binary64 six-cell source from PR #253 with Git blob `fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`; source SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.
- REF8 exact current stored ray/mass SHA-256 pair: `9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba` and `c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211`. These matched **actual source-generated binary arrays** from the unchanged PR253 MPFR source module.
- Local Rust binary compiled against archived original BASS `_rustcore/src/kinetic/comoving.rs` Git blob `25669ec464ab279e1a4d2421400a8ed135ae9638` (2026-08 archive). Current GitHub BASS module at PR257 blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`; exact local byte equality must not be claimed. GitHub workflow should build/readback the live BASS blob before accepting Git CI.

## 2. Actual generated model data

All inputs remain Bianchi I diagonal all-expanding collisionless massless reflected positive six-cell table (no Λ, collisions, spectral assumptions, polarization or tilt), `u=t/Tstar` in `[0,.08]` and **unchanged** 41 time points from CE1-P physical E/P histories.

Run BASS original Rust `Frame::apply`, `Frame::det`, `phys_dirs`, `real_ylm_l` from `_rustcore/src/kinetic/comoving.rs` (linked via `#[path]`). Add only standard normalized complex spherical-harmonic projection for `l=0..4` over the observer sky `s=-n_photon`. All 8 sign octants are summed with `weight/8`; no false 8-fold mass increase. Data produced:

- `data/stored_ref{1,4,8,16}_alm.csv`: actual ray-defined **atomic angular measures**, not pixel brightness fields.
- `data/gl{24,40}_alm.csv`: independently integrated continuous piecewise-constant six physical angular cells.
- `data/gl40_observer_sky_map.npz`: pointwise *continuous six-cell* observer-sky energy density `U`, not a thermodynamic temperature or polarization.
- `data/results.json`: byte source identities, per-channel harmonic coefficients, normalized `C_l^U` and numerical residuals.
- Four rendered input-derived figures including the Mollweide physical energy-angular map, time evolution, multipole spectrum and refinement sensitivity.

At u=0.08, continuous GL40 source gives

| quantity | numerical value |
|---|---:|
| E | 0.7584190590089329 |
| P1 | 0.2613053182746639 |
| P2 | 0.22072840102240993 |
| P3 | 0.27638533971187335 |
| a20^U | 0.022309840575559355 |
| a22^U (real) | 0.015673816332176647 |
| a40^U | -0.008105712278762101 |
| a42^U (real) | 0.006838012277485907 |
| a44^U (real) | -0.01008372586040773 |
| C2^U | 0.00019781320466729784 |
| C4^U | 0.00004028693886843132 |

**Nontrivial result:** The initial six-cell angular source itself already has a nonzero quadrupole (`a20^U(0)=0.02365436739393533` GL40). Do not misattribute all later quadrupole power to expansion shear. Under the same frozen physical source and saved geometry, `C4^U(stored_ref)/C4^U(GL40)` at u=.08 is

| stored rays | f | C4 ratio |
|---|---:|---:|
| 6 | 1 | 33.31574352084062 |
| 96 | 4 | 1.5877340517253455 |
| 384 | 8 | 1.128227499869414 |
| 1536 | 16 | 1.0308835568784422 |

Therefore a coarse source-level ray quadrature can be excellent for the background E/P but grossly distort l=4 observed angular morphology. This is a **numerical observed ratio**, not a certified continuum error. GL24-vs-GL40 final maximum harmonic coefficient difference `5.412337245047638e-15`, also numerical only.

## 3. Physics and independent computation checks

Wolfram symbolic: Bianchi-I observer-sphere Jacobian minus `det M/r³` = 0. Derivation in `THEORY_R_KO.md`.

Across all 6×41 actual states, measured maximum absolute residuals:

| check | measured max |
|---|---:|
| Rust sky E/P vs saved CE1-P E/P | 1.7763568394002505e-13 |
| massless trace `Σ P_i-E` | 1.9484414082171497e-13 |
| harmonic monopole `sqrt(4π)a00-E` | 2.1671553440683056e-13 |
| pressure-derived complex quadrupole | 7.099182353087485e-14 |
| original BASS native real l=2 vs new complex l=2 | 5.4262150328554526e-15 |
| independent SciPy complex harmonic integration | 1.0380585280245214e-14 |
| all odd l and odd m amplitudes | 4.336808689942018e-17 |
| real-field negative-m conjugation | 0 |

The new focused `pytest` suite passed 12/12 locally with Python3.13.5, Rust1.94.1 (BASS archived comoving.rs), NumPy2.3.5 and SciPy1.17.0. Tested exact frozen-ref8 source byte identity, 246 state-level E/P/monopole/quadrupole/odd-m checks, independent SciPy harmonic, GL stability, stored-ray l4 response, positive map, and malformed/nonfinite input rejection.

**No observational CMB data** were ingested, and `C_l^U` is not thermodynamic CMB `C_l`. The all-sky positive-source field is continuous within cells but discontinuous at original cell boundaries; a low-l expansion does not reconstruct those boundaries without a truncation error. The source's parent geometry is DOP853 history, not the certified CE1-N four-panel RK4/Hermite path. No full source-to-sky MPFR interval enclosure, true distinct-author R6/C9 or whole production low-ell EB hierarchy is asserted.

## 4. Scientific admission and next DAG node

CE1-Q = `SCOPED_NATIVE_MODEL_OBSERVER_SKY_HARMONICS_NUMERICALLY_VERIFIED`, subject to current-GitHub CI/reader-identity status. No generic Bianchi family support, no polarization, no local boost/global tilt mixing, no observational fitting. Original top-level BASS = **9/15** (21 edges), CE-1 PARTIAL, production_ready=false, merge_ready=false, auto_next=false. Scoped R1–R5,R7–R10 and C1–C8,C10 count **18/20** only; R6/C9 truly independent authors NOT_RUN.

One next physical research object (not executed): build an explicitly specified **spectral phase-space distribution** or measured frequency-channel transfer, propagate it on the same null-flow, and only then test when an actual thermodynamic T or frequency-dependent intensity can be inferred. Keep existing source and angular-energy sky intact.

## 5. Preservation-level adversarial finding, fixed before publication

A local `rustfmt` formatting call recursively formatted the imported archived BASS child `comoving.rs`, changing its Git blob despite no requested physics edit. This was a **local byte-provenance drift**, not a demonstrated numerical-physics error. The exact offline original archive file was restored to Git blob `25669ec464ab279e1a4d2421400a8ed135ae9638` (13,188 bytes) before final compilation and test. The project now uses `rustfmt --check --config skip_children=true` and a hard Git-blob assertion to avoid repeating this drift. Final Rust native selftest, all 12 saved-data tests and Rust-format no-child-mutation check passed after the source restoration. Neither the parent GitHub `_rustcore` file nor any published branch was mutated by this local formatting incident.
