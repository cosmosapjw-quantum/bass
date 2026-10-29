# BASS CE1-U S1 | 원본 여섯 cell의 새로운 coupled GL6/GL8 물리 데이터

**Completed/total BASS upper DAG: 9/15 (21 edges).** Frozen input source SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

The CE1-T Python `cellwise_gl_rust.make_cell_rays` generator is reused byte-for-byte, not rewritten. Exact stored ray/mass SHAs are recorded for GL6/GL8. Each actual source is a new finite positive quadrature of the same six original continuum cells with eight reflections. The zero-order Einstein source is NOT a fluid closure.

New actual physical work:

1. `source/ce1u_cert_source.py`: independent exact-rational Fourier/finite-binomial source difference on the entire `ell_i in [0, .08]` box, 559 monomial moments, K=12. Only exact arithmetic, rational pi/sqrt2 enclosures and immutable binary64 source bits are admitted to the theorem. Conservatively corrects stored ray off-unit norm. Produces source-bound JSON for GL6/GL8.
2. `source/ce1u_physical_histories.py`: fresh DOP853 integration of the **coupled** Einstein-Vlasov ODE with each new GLn source, proper time 41 records. Produces `ell_i,h_i,E,P_i,sigma2,Hamiltonian_C`, as well as actual observer-frame l=2,4 harmonics and time derivatives via positive kinetic fourth/sixth moments, no CMB temperature or polarization assumptions. Independent four-panel RK4 comparison included but is an empirical time integrator comparison, not a rigorous RK4 enclosure.
3. `source/ce1u_mpfr192_knots.py`: genuine `libmpfr.so.6`, 192-bit directed RNDD/RNDU source evaluation at five proper-time knots per channel, on exactly saved float64 `ell` and unchanged exact float64 `ray,weight`; this encloses *point source evaluations* only.
4. `source/ce1u_analyze.py`: GL40 numerical comparison at all 41 points, 5-point C2/C4 derivative diagnostics, physical plot and machine-readable science summary.
5. `tests/test_ce1u_science.py`: 20/20 verified scoped local tests, exact source identity and moment trace, independent SciPy `sph_harm_y`, positivity, constraints and continuity.

Summary of actual coupled outputs:

| channel | rays | max|C| across 41 | max|h−h(GL40)| numerical | 4-panel RK4-vs-DOP853 h endpoint | end C4' |
|---|---:|---:|---:|---:|---:|
| GL6 | 216 | 2.552e-13 | 4.108e-15 | 1.992e-9 | -0.00014789130142318007 |
| GL8 | 384 | 2.551e-13 | 7.772e-16 | 1.992e-9 | -0.00014789130274591168 |

These **new 82 actual model-generated physical rows** are not the earlier CE1-T *fixed GL40 geometry* result; they self-consistently evolve each GL source. GL40 is a useful numerical reference, NOT a certified true continuum history.

For the exact source comparison, the K=12 uniform continuum-vs-GL pressure source bounds are GL6 `3.010630537202566e-12` and GL8 `6.164277064237367e-14`; exact ODE geometry h bounds are GL6 `5.474586575721355e-13`, GL8 `1.1315891404909281e-14`, each below original 1e-5 target. They do not bound binary64 DOP853 itself.

MPFR192 directed 5-knot E/P evaluations: maximal Python binary64 offset beyond interval GL6 `1.3877787807814457e-16`, GL8 `2.7755575615628914e-16`. These tiny differences are **expected double rounding differences**, not errors in the exact source theorem. Full 4-panel source+time+runtime rounding MPFR IVP certificate: NOT_RUN.

No native subagent in current host; genuine independent-author R6/C9 NOT_RUN. Upper DAG 9/15 unchanged; no auto merge or production promotion.
