# BASS CE1-OBS (2026-10-30) | Actual observer angular-energy sky and l≤4 multipoles

## Scientific delta

Using immutable original CE1-P physical histories, generated 41 time samples × six channels: stored_ref1/4/8/16 and continuum GL24/GL40. Each contains E,P1,P2,P3 and real a00,a20,a22,a40,a42,a44; antisymmetric and imaginary channels are controlled by eight reflected octants. Generated a 9600-node positive-octant (76,800 rays with reflections) GL40 observed sky at u=.08 with initial and observed directions, r, Jacobian, initial/observed cell intensities and angular weights. These data are computed from the actual model histories, not surrogates or observational CMB data.

Mathematical map and proof in THEORY_KO.md. Importantly, stored rays yield an **atomic angular measure**, while the continuum GL samples yield an approximate angular density. The two are not silently conflated.

## Numerical scientific evidence (binary64)

GL40 at u=0: E=0.8999999999999999, P=(0.31751054387190353, 0.2574894561280961, 0.32500000000000034), a00=0.2538853125964904, a20=0.02365436739393913, a22=0.023184597772802927, a40=-0.009917395023299781, a42=0.008031380259108557, a44=-0.011386387919651936.

GL40 at u=.08: E=0.7584190590089558, P=(0.26130531827467146, 0.22072840102240887, 0.27638533971187473); a00=0.21394606652847198, a20=0.022309840575555663, a22=0.015673816332179034, a40=-0.008105712278761622, a42=0.006838012277487496, a44=-0.010083725860408028. For this one deterministic sky, C2=0.0001978132046672949 and C4=0.00004028693886843662.

Max |angular re-evaluation minus parent E| over all 246 snapshots: 7.77e-16. Max |angular re-evaluation minus parent P_i|: 4.22e-15. For actual GL intensity × transformed solid-angle weights, max |E_sky minus parent E|=3.33e-16 and max |P_sky minus parent P_i|=4.16e-15. Independent SciPy full-octant spherical harmonics versus polynomial evaluation at 9 channel/time anchors: max 5.55e-16. Max odd-l amplitude over selected anchor checks: 2.97e-17. The remaining parity and conjugate checks are below numerical roundoff thresholds.

## Angular discretization convergence: max over u∈[0,.08] vs GL40

| channel | |Δa20| max | |Δa40| max |
|---|---:|---:|
| stored_ref1 | 1.7863703571e-4 | 9.5647765336e-2 |
| stored_ref4 | 1.1644514534e-5 | 6.2491641037e-3 |
| stored_ref8 | 2.9170255777e-6 | 1.5656807605e-3 |
| stored_ref16 | 7.2962462459e-7 | 3.9163204855e-4 |
| GL24 | 1.2490009027e-16 | 4.7184478547e-16 |

This is a meaningful warning about numerical quadrature: source ray refinements that reproduce energy/pressure well can still give O(10^-4) absolute error in l=4 even at ref16. The source's MPFR pressure certificate is not a bound on l=4. GL24 and GL40 differ at binary64 roundoff for the short-history cell-aware integration, but neither is an interval enclosure.

## Verification actually run

- Manifest source SHA and every recorded member SHA: PASS; exact parent ZIP SHA check PASS.
- Independent direct solid-angle Jacobian finite differences at four interior directions: PASS; Wolfram determinant identity (Jacobian ratio → 1): PASS.
- Inverse tetrad map, redshift, isotropic test fixture, conservation/pressure reconstruction, zero parity, GL normalization, persistent source tamper detection: PASS.
- `python -m pytest -q tests/test_observer_sky.py`: 11/11 PASS after correcting one overly strict ~4e-16 roundoff assertion; `compileall`: PASS.
- Native delegated subagents: NOT_RUN (not exposed). Distinct-author R6/C9: NOT_RUN. No independent MPFR enclosure of the l=4 sky. Current PR-specific CI: NOT_RUN/unknown. No production validation.

## DAG and stop

Upper DAG **9/15**, 21 edges, unchanged. CE1 PARTIAL. The scoped CE1-OBS theoretical/coding construction is checked within the one bounded research unit; independent-author R6/C9 remain not run. Production_ready=false, merge_ready=false, auto_next=false. Do not merge parent PR258 or sibling branches.
