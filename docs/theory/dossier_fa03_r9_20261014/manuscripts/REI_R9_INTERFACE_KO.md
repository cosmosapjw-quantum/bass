# REI 동시 보조: signed clock의 엄밀한 사차 전개 범위와 source-bound milestone 접합

**2026-10-14.** 이 문서는 BASS FA03-R9의 실질적인 cross-lane 공급이며 `rei_bianchi`의 외부 실행 소유권을 유지한다. 최신 live 입력은 실제 `BACKGROUND_FAMILY_LOCK.json` SHA256 `46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0` 및 `SCENARIO_LOCK.json` SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`이다. Universe metric `ds²=-c²dt²+a²e^{-2b}(dx²+dy²)+a²e^{4b} dz²`, non-tilted gas, `b(a_*)=0`, `a_*=1/21`, `a_f=1/5`, prescribed stress-free family, `q=s(a_*)/H_F(a_*)` fixed signed amplitude. Do not interchange `q` with evolving `Σ=s/H`.

## [REI-R9-CLOCK2] Signed-even clock and analytic fourth-order remainder

\[
H_F(a)^2=H_0^2(\Omega_ra^{-4}+\Omega_ma^{-3}+\Omega_\Lambda),\quad
s(a,q)=qH_F(a_*)\left(\frac{a_*}{a}\right)^3,
\quad H(a,q)=\sqrt{H_F(a)^2+s^2}.
\]

Set `g(a)=H_F(a_*)(a_*/a)^3/H_F(a)` and `d\tau(a,q)=d\ln a/H(a,q)`. With positive \(\Omega_r,\Omega_m,\Omega_\Lambda\), and `a>=a_*`, one has

\[
\frac{d\log g}{d\log a}=-\frac{2\Omega_ra^{-4}+3\Omega_ma^{-3}+6\Omega_\Lambda}{2(\Omega_ra^{-4}+\Omega_ma^{-3}+\Omega_\Lambda)}<0,
\quad g(a_*)=1,\quad 0<g(a)\le1.
\tag{REIR9.1}
\]

(The numerator is equivalent to `-(Omega_r a^-4 + 3/2 Omega_m a^-3 +3 OmegaLambda)` after the factor 1/2.) Since `H(a,q)` is even in q, the proper elapsed clock from the common \(\bar z=20\) origin is **exactly** even in q. Define `A_j(a)=∫_{a_*}^{a}g(a')^j/H_F(a') dln a'` for j=2,4. By the exact scalar Taylor inequality valid for all `x>=0`,

\[
0\le \frac{x}{2}-\left[1-(1+x)^{-1/2}\right]\le\frac{3x^2}{8},
\quad x=q^2g(a)^2,
\]

the signed-even **geometric** clock shift obeys

\[
\boxed{
-\frac{q^2}{2}A_2(a)\le\tau(a,q)-\tau(a,0)
\le-\frac{q^2}{2}A_2(a)+\frac{3q^4}{8}A_4(a).}
\tag{REIR9.2}
\]

Importantly, `0<=A4<=A2` because `g<=1`, therefore the width relative to the absolute leading quadratic term is bounded **analytically** by `3q²/4`, at most `7.5e-5` for `|q|<=.01`. This is a *theorem for the prescribed clock*, not an empirical error bar on a chemical history. The simple finite definite integrals `A2,A4` are evaluated numerically by `mpmath` in `code/rei_clock.py`; the code labels its quadrature rounding **not rigorous interval-enclosed**. Exact theorem versus numerical displays are separated. No original clock history is rerun.

At \(\bar z=4\), the frozen numerical cosmological law produces

\[
\Delta\tau(0.01)\simeq-7891.36627003\ \mathrm{Julian\ yr},\quad
A_2\simeq4.98079245245\times10^{15}\ \mathrm{s},\quad
A_4\simeq1.87807260401\times10^{15}\ \mathrm{s}.
\]

The analytic `q^4` addition to the quadratic clock bound has a numerical width of about `7.04e6 s = 0.2232 Julian yr` at `|q|=.01`. At `q=.005`, its width is 16 times smaller, not simply 4 times. All such digits are reproducible deterministic numeric evaluations of the *prescribed background* with its rounded cosmological parameters; not a physical observational uncertainty. The exact real geometry is q-sign symmetric, but the scalar ionization/temperature histories need **not** be exactly sign symmetric, since `tr sigma³=6s³` survives.

## [REI-R9-MILESTONE-SPLIT] Completed, source-bound signed case

When both **completed, reviewed** signed and ZERO histories provide the first upward crossing scale factors `a_{x,q}` and `a_{x,0}` for a declared local scalar threshold (`x_HII` not Q_V), the true *model identity* is

\[
\tau_q(a_{x,q})-\tau_0(a_{x,0})
=\underbrace{\tau_q(a_{x,0})-\tau_0(a_{x,0})}_{\rm pure\ geometric\ clock}
+\underbrace{\int_{a_{x,0}}^{a_{x,q}}\frac{d\log a}{H(a,q)}}_{\rm shifted\ crossing\ position}.
\tag{REIR9.3}
\]

It holds for any order of the two `a` values because the second integral is oriented. The first term is **even** in `q` at fixed ZERO crossing. The second is not generally q-even, and contains actual source/chemistry and thermal response. Never infer a resolved physical shear effect from the first term alone. To use this at higher accuracy one needs the independently refined crossing locations and their true-continuum interpolation envelopes. R7's first-passage helper `REIM.1-4` must receive whole-interval accuracy, not just node errors or nominal 1e-7 floor. Even after the two contributions are computed, source/IC/atomic/geometry errors remain distinct.

`milestone_decomposition()` in this capsule is deliberately a consumer, not a dispatcher. It refuses if `source_pair_bound=False` or either history lacks scoped completion/review flags. These Boolean flags are supplied by the owner with evidence IDs; this helper does *not* independently verify the external reviewer credentials or run files. Geometry-only `geometry_clock()` is available separately with `no chemistry` assumptions. Sample code:

```python
from rei_clock import geometry_clock, milestone_decomposition
geometry_clock('0.2','0.01')
# milestone_decomposition(a_zero,a_signed,'0.01',
#     source_pair_bound=True,actual_case_reviewed=True,actual_zero_reviewed=True)
```

Calling the second function without the actual reviewed signed data returns `HOLD`, rather than silently inventing a milestone response. All returned times are elapsed gas proper seconds since common z20. The source law remains the same comoving emissivity law vs a; matching equal a does not simultaneously match proper time.

## Current owner and distinct suppliers

The live branch `codex/rux-science-delivery-20261014` had HEAD `45f166adee36d57cabe712ff66209926d1aa1556` when first read (2026-10-14 13:09 UTC); `AX07=COMPLETED` with conditional full ZERO z20→4, `AX08=IN_PROGRESS`, original signed `HALF_MINUS` process running; `AX11/AX12=PENDING`. The owner comparator `compare_histories.py` and README were **dirty**, so this R9 did not modify any active REI file or relaunch a solver. Actual current state may advance; Codex must reread before consumption.

WU088_HH PR70 (successor of PR69) has already adapted the source semantic relation guard to the actual current reducer SHA `35e1499e...` in a temporary copy and passed 10 integration tests. BASS_HE PR53 produced a combined optional exact-union PL norm/source comparison patch and already recognized the owner-corrected electron `xe` floor. Reuse these existing source/consumer patches, do not create a second competing one. The present `rei_clock.py` only supplies a physically distinct scalar formula and positive execution step to AX11 once histories actually exist. Keep its status **SUPPLIER_READY_FOR_OWNER_IMPORT**, not canonical AX11 READY or PASS. No new mandatory gate is imposed on unfinished signed execution.

BASS_CR PR62's kinetic Coulomb-only finite-volume source is not the cold REI atomic supplier. HH70's continuum scattering bound likewise does not activate optional HH physics. REC84's three-case parity is partial and cannot yield unmeasured half-amplitude/refinement uncertainty. All CR/RCT/HH remain OFF for the selected AXBI scenario, and optional tau/visibility stays nonblocking for the abundance-first target.

## Actual symbolic checks and literature

Wolfram cloud 15.0.1 checked the exact scalar inequality, negative `d ln g/d ln a` and Stokes eigenvalues. Remote Wolfram 15.0.0/xTensor 1.3.0 returned 8 exact-zero groups including the LRS stress-work `sigma:pi=2s(\Delta P)`. All raw remote code and output are saved with SHA evidence. These checks validate kinematic signs and analytic factors under the specified signature, not the adopted empirical ionization network.

Original geodesic/optical conventions: Fleury, Pitrou & Uzan, Phys Rev D 91 043511 (2015), DOI:10.1103/PhysRevD.91.043511. General numerical/model-error segregation in transport: Han, Applicable Analysis 94 (2015), DOI:10.1080/00036811.2014.992423. Their results motivate structure, not a direct REI photon/chemistry validation.
