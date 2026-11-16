# TypeII finite cascades and conservative effective-rate bridge

Frozen parent PR337 d29a08cb6e368339015dadb2b791044ba6af9848. Current Draft PR338. Four local phases K1-K4. Upper DAG stays9/15 scoped/source-mapped, zero new full upper nodes.

## Actual construction
Six unaligned hydrogen levels1s,2s,2p,3s,3p,3d plus an ion tracer at prescribed proper ne. Parent finite-band Milne kernels remain unchanged. Added five E1 channels, analytically constructed from Coulomb radial integrals with independent quadrature and NIST-scale checks, and original-source2s-1s two-photon quadrature with leading E1E1 angular correlation. The original HYREC standard/hires spectra are normalized once to8.2206 s^-1. Parent binding-energy differences close every energy loop. Finite-mass source spectrum sharing is explicitly mapped to the infinite-mass parent gap; this adaptation is not a new precision-isotope claim. No resonant high-n two-photon addition double-counts E1 cascades.

## Conservative elimination
The n=3 interior block is eliminated using N=(-Q_FF)^-1, L=NQ_FR, P=Q_RF N, S=Q_RR+Q_RF L. Positive effective rates and column-conservative nuclei flow are proved and tested. Full stationary fractions require reconstruction of fast states and total normalization, not just a normalized retained vector. Microscopic photon/electron-kinetic/bound-energy readouts are lifted along with populations. The stationary Schur matrix is NOT the exact time generator: exact elimination has a memory kernel and initial fast-population term. Low-frequency storage and its conserved-mass identity are supplied separately.

## Actual TypeII source results
Generated358 source local generators,358 reduced matrices/lifts and1074 retained direct/effective capture/photoionization records. At mean z1100:
- n=1,l=0: alpha_direct=2.9683725713375357e-19 and alpha_eff=3.3462440241813508e-19 m^3/s; beta_direct=3.4248997093005203e-15, beta_eff=3.7991967818810606e-15 s^-1.
- n=2,l=0: alpha_direct=4.370940142911038e-20 and alpha_eff=4.878455192783293e-20 m^3/s; beta_direct=35.295424772059619, beta_eff=39.270147915520816 s^-1.
- n=2,l=1: alpha_direct=1.1243877919810881e-19 and alpha_eff=1.7061131991922826e-19 m^3/s; beta_direct=30.249815346937314, beta_eff=45.43261406326026 s^-1.
These are finite n<=3 local rates in a fixed optically-thin bath, not full HYREC effective coefficients or a new cosmological xe result. Source two-photon down/up rates at z1100 are8.3936018128737864/7.8763531394098327e-17 s^-1. Standard/hires down-rate difference over actual source states reaches6.1813861189641273e-05 relative, kept separate from algebraic/solver residuals.

Stationary full/reconstructed relative gap<=5.9553695308522947e-11; exit-probability sum defect<=2.2204460492503131e-16. Microscopic and reduced-lift energy-ledger residuals<=5.056945962141159e-16 and5.2434383074042056e-16 relative to gross exchange. Exact memory resolvents, including initially occupied fast states, agree with the original7-state response to machine precision. Matrix-exponential vs independent Radau gap=1.574740338128322e-12. Instant fast-state routing instead has retained L1 error1 at the initial time: it drops the real residence time.

The photon-number-changing loop3p->2s->1s->3p has log-affinity2eta for an isotropic BE photon bath, not zero, despite valid individual channel relations. In the actual boosted z1100 source its affinity is0.29850154055576539. A maintained nonthermal radiation field can therefore drive cyclic stationary currents; no global equilibrium or thermodynamic H-theorem for that field is claimed.

## Actual verification and one same-author hostile pass
16 contracts x normal/-O=32 executions;12 malformed inputs reject; eight physics outputs replay byte-exact under optimized Python. Independent radial/angle/frame quadrature, thermal limits, source-lift energy and dynamic resolvents were checked. Original4 HYREC source files and BASS9 blobs remain unchanged.

A real false-admission defect was found: normalizing conservation error by the globally largest transition rate hid a slow-column imbalance of1/3 as1.77e-16. A RED regression was preserved, then per-column scaling repaired the admission condition without changing physical rates or tolerances. Stationary conditioning weights now reject zero/nonfinite inputs before solving. A separate scalar ndarray diagnostic max error was repaired and its failure log retained.

Other wrong-model controls: duplicate source half-spectrum ->vacuum16.4412 s^-1, omit stimulated factors ->thermal ratio error0.021037352047801106, discard angle correlations at T8000/beta0.2 ->two-photon upward relative error-0.0044526890699071453. Adding direct capture again on top of S double counts it. Omitting lifted fast populations loses actual stored nuclei. Reviewer is same-author hostile, not genuinely blind or independent; native subagent and distinct-author referee NOT_RUN.

## Claim gate and next unit
Admit a finite microscopic source network, conservative stationary effective rates, energy/population reconstruction, chemical-cycle test and exact local linear memory interface. Do not admit a complete cosmological atom, high-n/helium effective rates, nonlinear electron feedback, line trapping/escape, solved radiation/polarization, momentum/thermal/Einstein backreaction, native HYREC replacement, or observed CMB. No new native xe or optical-depth run.

Local4/4 scoped complete; upper9/15 scoped/source-mapped, new full upper nodes0. StageII historical11/11/current canonical chain unestablished; JoinJ1 0/2 HOLD. Production_ready=false, merge_ready=false, auto_next=false.

Next unit: LYMAN_LINE_TRANSPORT_AND_CONSERVATIVE_ESCAPE_INTERFACE. Couple the cascade readouts to a line-photon balance with explicit directional frequency drift, optically-thin/thermal limits and correct reaction time. Do not introduce a generic Sobolev factor without checking the required monotonicity/scale conditions. Independently retain StageII canonical evidence recovery.
