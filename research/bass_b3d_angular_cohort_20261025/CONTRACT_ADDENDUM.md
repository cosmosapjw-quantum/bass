# Pre-execution R6 clarifications

This addendum is frozen before the first numerical Python execution. It changes
no model, fixture, tolerance, quadrature order, or scientific claim.

1. The independent octant reference applies to the diagonal aligned fixtures.
   Only reflection-even energy and diagonal-pressure integrands may be
   integrated on one octant and reflected with equal values. Off-diagonal
   pressure and flux acquire signs under reflections: obtain their full-sphere
   values by explicit sign cancellation or the analytic value zero. Do not
   multiply a positive-octant cross term by eight.
2. With Delta=rule minus continuum, the exact main14 leading coefficients are:
   ANISO DeltaF=-9*eta^2/35000,
   DeltaP=eta*diag(13,-11,-2)/10500;
   ISO DeltaF=-9*eta^3/17500,
   DeltaP=eta^2*diag(13,-11,-2)/3500.
   These were independently derived and all were verified exactly by Wolfram.
   Candidate26 coefficients and their residual evidence are in the theory and
   WOLFRAM_ANGULAR_PARSED.json; unresolved small values do not establish slopes.
3. Gate4 compares signed coefficients. For energy use
   abs(DeltaF/eta^p-c)/abs(c). For pressure use
   maxabs(DeltaP/eta^p-C)/maxabs(C). Here p,c,C are the exact leading order and
   coefficient of the corresponding fixture. The fixed5% gate applies at
   eta=1/128 to the four14-rule quantities; no normalization by a small stress
   component and no fitted coefficient. The original continuum-F normalized
   errors remain the separate angular accuracy observables.
4. The finest resolved triplet consists of the smallest three successive
   positive eta values for which all relevant errors exceed4096eps. For the
   intended14 fixtures these are1/128,1/64,1/32 if actually resolved. Both
   adjacent order estimates in that triplet must meet the frozen order bin.
   Preserve unresolved rows as null and identify the actual triplet used.
5. The selected q_b shape is the parent's admitted thick-source angular form
   applied to a declared unit cohort. This unit calls no finite emission or
   absorption transaction and does not establish a finite-opacity identity.

R6 clarification disposition: CLOSED once the implementation follows these
definitions. The actual source/code and results are still examined in C9;
no second broad contract-review loop is required.
