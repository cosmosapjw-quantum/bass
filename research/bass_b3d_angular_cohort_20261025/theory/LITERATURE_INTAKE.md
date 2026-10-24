# B3d angular-cohort literature and independent theory intake

Read-only intake for `BASS_B3D_ANGULAR_COHORT_20261025`. This worker performed no numerical scientific execution, IVP, old campaign replay, NPZ/archive download, or remote write. The formulas below are an independent paper-and-pencil specialization and proposed diagnostics; root owns the frozen domain, numerical gates and scientific admission.

## Actual discovery, sources and access limits

Three SciSpace searches actually returned ten papers each. Exact natural-language queries and raw-response SHA256/size receipts are in `LITERATURE_TOOL_RECEIPTS.json`. The broad spherical-rule search and the targeted Lebedev1976 title/DOI question did **not** retrieve the original paper; these searches are discovery records, not evidence of exhaustive literature coverage. The Bianchi search returned Lee–Nungesser–Tod among other, often less relevant, results. Raw external text is temporary; this public note contains citations and short source summaries only.

1. **J. Mark Heinzle and Claes Uggla, “Dynamics of the spatially homogeneous Bianchi type I Einstein-Vlasov equations,” Classical and Quantum Gravity 23 (2006), 3463–3490.** DOI [10.1088/0264-9381/23/10/016](https://doi.org/10.1088/0264-9381/23/10/016); [primary full text, arXiv gr-qc/0512031v1](https://arxiv.org/html/gr-qc/0512031v1). Read Section2, Eqs(2c)–(2f),(3)–(5). The distribution is time independent when expressed in covariant momenta. Energy and stress use a common inverse spatial-volume factor, with one energy factor for density and an inverse energy in spatial stress. Its diagonal class additionally imposes reflection symmetry. The paper's units and time variables must be translated into the BASS fixed-scale convention; no asymptotic theorem is imported into this finite test.

2. **Ho Lee, Ernesto Nungesser and Paul Tod, “On the future of solutions to the massless Einstein-Vlasov system in a Bianchi I cosmology,” General Relativity and Gravitation (2020).** DOI [10.1007/s10714-020-02699-7](https://doi.org/10.1007/s10714-020-02699-7); [primary arXiv1911.04937v2 PDF](https://arxiv.org/pdf/1911.04937). Read Section2.2, printed pages5–6, Eqs(12)–(16). Conserved covariant momenta solve the homogeneous Vlasov equation, while anisotropic stress depends on higher angular moments. This supports examining finite angular closure after anisotropic transport. Its small-anisotropy future theorem is not a numerical error certificate for this cohort comparison.

3. **SciPy1.17.0 official Lebedev documentation and implementation.** [Documentation](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.lebedev_rule.html); [official source](https://github.com/scipy/scipy/blob/v1.17.0/scipy/integrate/_lebedev.py), Git blob `6e45d40e7950780c724523809a7c18fc957fa576`. Read the order/point map, `get_lebedev_sphere` cases14/26, and recurrence types1/2/3. Order5 maps to14points and order7 to26points. The generator returns weights summing to4π; divide by4π for a normalized sphere average. Official source values give the positive rational weights in the table below. The current generic documentation redirects to1.18.0; the independently read1.17.0 pin is the adopted implementation citation.

4. **V. I. Lebedev, “Quadratures on a sphere,” U.S.S.R. Computational Mathematics and Mathematical Physics16(2) (1976),10–24; Russian original293–306.** DOI [10.1016/0041-5553(76)90100-2](https://doi.org/10.1016/0041-5553(76)90100-2); [MathNet publisher record](https://www.mathnet.ru/eng/zvmmf6092). Bibliographic metadata was found. Full text was **not read**: two web opens timed out, a direct landing-page read returned HTTP503, and the ScienceDirect page returned HTTP403. No formula is attributed to an unread table. Exactness below is established directly from the actual rule, independently of this access limit.

## Canonical rules and the actual owner boundary

Write the normalized sphere average as `<F>=(4π)^−1∫F dΩ`.

| Orbit | Directions | Count | 14-rule weight per point | 26-rule weight per point |
|---|---|---:|---:|---:|
| Axes | permutations of `(±1,0,0)` |6|1/15|1/21|
| Edge centers | permutations of `(0,±1/√2,±1/√2)` |12|absent|4/105|
| Cube corners | `(±1,±1,±1)/√3` |8|3/40|9/280|

These are canonical degree5 and degree7 positive Lebedev rules. The BASS parent's actual `cubature14()` supplies the14rule. Its `commit_emission` assigns `dn=D*A*(1+n^T S_birth n)`, `k=E_birth*n/(c*Pstar)` and `w=alphaL*c*Pstar*dn`; the current angular study reuses that source form.

The inspected actual REC `nonlinear_bose_runtime.py` imports `scipy.integrate.lebedev_rule` and divides its weights by4π. Its `positive_harmonic_grid` actually selects orders29/41/53 for ell_max12/20/24. It does **not** select order7 in that function. A constructed26point cohort is therefore a new canonical-rule comparator, not a claim that the saved35×26 REC inventory was consumed or that this worker re-created its runtime path. No NPZ is needed for this angular comparison.

## Independent physical specialization: one finite birth cohort

Let `n` be a **birth-frame direction label**, `D>0` the cohort's birth number density, `E_b>0` its monochromatic birth energy, and

`q_b(n)=1+n^T S_b n`, with real symmetric `tr(S_b)=0` and `lambda_min(S_b)>−1`.

For diagonal homogeneous collisionless transport let `R=diag(r_x,r_y,r_z)`, with every `r_i>0`. Each `r_i=a_i(birth)/a_i(now)`. Define `u(n)=|R n|` and `chi=det(R)=V_birth/V_now`. Then

`p(now,n)=(E_b/c)R n`, `E(now,n)=E_b u(n)`, and the number weight in the fixed birth label receives the **common factor chi**.

The dimensionless stress components are

`rho_bar = <q_b u>`,

`P_bar_ij = <q_b (R n)_i (R n)_j/u>`,

and physical `rho=E_b*D*chi*rho_bar`, `P_ij=E_b*D*chi*P_bar_ij`. The photon number is `D*chi` because `<q_b>=1`. The energy flux vanishes by antipodal symmetry. Stress is positive semidefinite and `tr(P_bar)=rho_bar`. Current state anisotropic stress is `Pi_bar=P_bar−rho_bar*I/3`; this is not PiRate.

For the actual packet convention, transport changes `k` by `R` and `w` by `chi`. There is no extra direction-dependent energy weight multiplying `w`. The B3b2 Lorentz state-boost formula `w'=Doppler*w` is a change of observer at one event; it is not this cosmological evolution. Neither formula is an invariant emission-rate transformation. A Jacobian for the map from birth direction to current direction belongs only if the integration variable is actually changed; adding it while still integrating over birth directions would count it twice. Similarly, `q_b` remains the cohort's birth angular distribution and must not be replaced by a source quadrupole evaluated at the later time.

At fixed `S_b`, differentiation gives `d rho_bar/d ln(r_i)=P_bar_ii`. For the physical density the volume factor also differentiates, giving `d rho/d ln(r_i)=rho+P_ii`. Consequently along a diagonal history, `rho_dot=−sum_i H_i*(rho+P_ii)`. This is a local cohort work identity, not an IVP result.

For common redshift `R=rI`, both rules integrate the moments exactly:

`rho_bar=r`, `P_bar=r*(I/3+2*S_b/15)`.

If some diagnostic relative `r_i` exceeds1 after factoring out common expansion, that shape parameter should not be described as a proven physical no-reabsorption trajectory. The endpoint angular calculation and a full zero-blue-trace support proof are separate claims.

## Direct polynomial exactness and its first failures

Sign symmetry makes every monomial with an odd exponent vanish. The sphere's even moments are

`<nx^(2a) ny^(2b) nz^(2c)> = (2a−1)!!(2b−1)!!(2c−1)!! / (2a+2b+2c+1)!!`,

with `(−1)!!=1`. This follows by separating Cartesian Gaussian moments and their radial integral.

The14rule gives `Q1=1`, `Qnx²=1/3`, `Qnx⁴=1/5`, `Qnx²ny²=1/15`. Symmetry completes degree5 exactness. It fails at degree6:

`Q14(nx^6)=7/45`, `<nx^6>=1/7`, difference `4/315`;

`Q14(nx^4 ny²)−<nx^4 ny²>=−2/315`;

`Q14(nx² ny² nz²)−<nx² ny² nz²>=4/315`.

The26rule additionally gives `Qnx^6=1/7`, `Qnx^4ny²=1/35`, and `Qnx²ny²nz²=1/105`, establishing degree7 exactness. Its first axis monomial failure is

`Q26(nx^8)=37/315`, `<nx^8>=1/9`, difference `2/315`.

Therefore exact source number/flux/stress at birth does not establish exact continuum moments after unequal directional redshifts: the square root and reciprocal square root create higher angular degrees. These direct algebraic results require no novelty/no-go claim about spherical quadrature or collisionless reduction.

## Axisymmetric diagnostic and predicted small-strain orders

This is a proposed independent analytic diagnostic, not a replacement for root's frozen cases. Set `R=diag(1,1,s)`, `epsilon=s²−1`, `S_b=diag(−a/2,−a/2,a)`, and `mu=n_z`. Thus `q=1+a*(3mu²−1)/2`, positive for `−1<a<2`.

The continuum reduces to one-dimensional integrals:

`rho_bar=integral_0^1 q(mu)*sqrt(1+epsilon*mu²) dmu`,

`P_bar_zz=(1+epsilon)*integral_0^1 q(mu)*mu²/sqrt(1+epsilon*mu²) dmu`,

with `P_xx=P_yy=(rho−P_zz)/2`. These supply a reference independent of a general two-angle implementation. Differentiation gives `P_bar_zz=2*(1+epsilon)*d rho_bar/d epsilon`.

The14rule collapses to mu²=0,1,1/3 with total weights4/15,2/15,3/5. The26rule collapses to mu²=0,1,1/2,1/3 with total weights12/35,2/21,32/105,9/35. Multiplying each by `q(mu)` gives direct finite formulas, avoiding any time integrator.

Let Delta mean **quadrature minus continuum**, with the common physical factor removed. Direct Taylor expansion and the exact monomial gaps give:

| Source | Rule | Leading Delta rho_bar | Leading Delta P_bar_zz |
|---|---|---|---|
| fixed nonzero `a` |14|`−a*epsilon²/420 + O(epsilon³)`|`−a*epsilon/105 + O(epsilon²)`|
| fixed nonzero `a` |26|`+a*epsilon³/1680 + O(epsilon⁴)`|`+a*epsilon²/280 + O(epsilon³)`|
| `a=0` |14|`+epsilon³/1260 + O(epsilon⁴)`|`+epsilon²/210 + O(epsilon³)`|
| `a=0` |26|`−epsilon⁴/4032 + O(epsilon⁵)`|`−epsilon³/504 + O(epsilon⁴)`|

These orders concern **small differential redshift**, not temporal solver refinement. For Pi, subtract Delta rho/3 from each diagonal pressure error. A small or vanishing Pi component is unsuitable as its own relative-error denominator; a declared cohort energy scale keeps the comparison meaningful.

## Minimal finite comparison and remaining limits

A bounded comparison needs a finite selected table of `S_b` and strictly positive `R`, source `q_min` checks, the same birth-frame normalization, and a declared energy/tensor norm. It can compare the actual14rule and constructed canonical26rule directly with a two-angle continuum integral, while the axisymmetric one-dimensional reduction and the exact birth/isotropic-redshift identities provide independent controls. Fix the reference quadrature and its refinement comparison before observing errors. Grid agreement or a library error estimate is numerical evidence; it is not an automatic rigorous interval bound.

Number, positivity, zero flux and trace checks are useful, but trace forced by storing `Pi_zz=−Pi_xx−Pi_yy` is an algebraic representation identity, not an independent conservation test. Inspect the raw spatial tensor or independently summed diagonal pressure for that purpose. A shared erroneous extra `u(n)` in number weights could make an energy integrand polynomial and spuriously hide the angular error; the number dilution and actual packet convention prevent that mistake.

This finite cohort work can measure an angular error and compare rules without rerunning the completed temporal B3c IVPs. It does not on its own certify all cohorts of the saved B3c trajectory, the coupled geometry's response to a changed angular rule, finite absorption, an actual REC boundary field, general Bianchi domains, or B4/B5.
