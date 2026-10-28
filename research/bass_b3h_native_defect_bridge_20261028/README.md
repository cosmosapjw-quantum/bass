# B3h native saved-reference defect bridge

UNIT=BASS_B3H_NATIVE_DEFECT_BRIDGE_20261028
BASE_F=46e7e2bd802cf2f69d98c0fb66d0c3a892c9b3b3
Original DAG record28/88,delta0,AUTO_NEXT_NODE=false.

## Scope and result
Consume the actual recorded two-panel whole residual, endpoint errors, frozen matrices and clock enclosures. Compare two declared reconstructions: second-order slow particular alone, or that particular plus its written frozen exponential layer. Full-cell and saved-suffix comparisons use the same respective initial datum. No native ODE/QSS/B3i/old quadrature/campaign execution. The original adjoint-moment Nout certificate is a different reconstruction/method and is not replaced.

Conditional count-error upper bounds, in m^-3, upward-rounded display:
- whole cell, slow-only:8.2305041074671535906249388455325e-21
- whole cell, with layer:1.5927767772508444342608112569140e-26
- saved suffix, slow-only:5.5065487220842250479639179175344e-28
- saved suffix, with layer:6.7251645849826109732436977958449e-31

The upper-bound ratios are approximately516739.33 and818.798. These are comparisons of upper bounds for different declared reconstructions, not measured actual errors, solver speedup, physical accuracy, or new native output. Whole-cell slow-only is dominated by its initial mismatch; with-layer by frozen/variable-M discrepancy. The suffix with-layer bound is dominated by the inherited slow residual.

## Derivation and equation-to-code map
For p'=b-Mp, let -M be Metzler with columnsum(M)>=gamma>0. Proper time is seconds, p is dimensionless, n0=N_H/V0 has units m^-3 and0<=R<=Rhi in s^-1. Define J=integral n0 R p2 dt. Identical incoming drive cancels in a path comparison.

For piecewise smooth Q, e=Q-p, f=Q'+MQ-b and interior jump j=Q_plus-Q_minus. Variation of constants on each panel gives

    J(Q)-J(p)=h(0).e(0)+integral h.f+sum h(tk).jk,
    h(s)=integral_s^T Phi(t,s)^T n0 R(t)e2 dt.

Positivity and one-norm contraction yield ||h||inf<=K=n0 Rhi/gamma, hence

    |error|<=K*(Einit+sum Fpanel+sum Jk).

The terminal knot has h(T)=0. Joint L1 residual mass is charged once, not separately in each coordinate. Code output_bound and knot_mass implement the composition with exact Fraction arithmetic.

For Q=q+exp(-B tau)z, beta=min columnsum(B)>0, Z=||z||1,

    f=r_slow+(M-B)exp(-B tau)z,
    Flayer<=Z*min(C*Phi,alpha*Phi+L*Psi),
    Phi=min(Dhi,1/beta), Psi=min(Dhi^2/2,1/beta^2).

Here C bounds ||M-B|| on the panel, alpha bounds its start value, and L bounds ||M'||. Psi is integral tau*exp(-beta tau), NOT the earlier double-integral kernel. gap_bound uses convex norm envelopes at theta/R box vertices plus the inherited coefficient margin. Local theta intervals preserve source duration errors. Finite endpoint tails use(1+beta*Dlo/8)^(-8); they are not set to zero. initial/jump masses retain endpoint evaluation errors and exact written differences. The exact written z=p_start-part_start defines the new reconstruction; last-digit differences from the old stored z are preserved diagnostically.

The integral proof follows from the standard nonautonomous variation-of-constants construction. Residual/adjoint context: Cao/Petzold2004 DOI10.1137/S1064827503420969 and Estep1995 DOI10.1137/0732001; current bibliographic/abstract verification is not full algorithm adoption. Full derivation and source-specific mapping are in the immutable source ZIP.

## Source binding and discovered repair
Native S1=e35673b96c94dfad576c76c5b0b12f4873dd13e4. Raw ENDPOINT_RESULT17398524bytes/SHA256acf56f5aefe556d1d86e4f93f3063c5d38078cb8c7f9a627b141c4ef9582f3bd restored and matched. Selected NATIVE_SLICE10931bytes/SHA2560ffb0682d250559cf7ba605360889ff83bfafc1fc35841cbbd7c2871f300ddc3 is a named-field projection. Supplier code is read-only, never imported.

First primary stopped before panel computation: the literal endpoint-column lower bound minus source margin is1.09847857810191380415656487078086136009754551319221425e-67s^-1 below the separately written gamma. Raw source, failure and code remain. Use gamma_used=min(gamma_saved,gamma_literal)>0; no tolerance widening or physical-law change. Primary attempts2, successful saved-input consumptions1. The discrepancy is an exact representation observation, consistent with separate finite-precision aggregation/serialization, not evidence of a physical failure.

## Verification and reproduction
From this subtree, run `python -I -S tests/test_defect.py` for the standalone core tests. Recorded RED18failed methods/28assertion events/3passes, then identical GREEN21/21. Primary19/19. Separate production-import-free Decimal80/closed-form verifier76/76, including24constant/affine fixtures. Fixed tol1e-60; largest native relative discrepancy1.397735309109064e-78. CAS6scalar residual zeros and2zero-duration boundary zeros. An inserted jump gives nonzero output despite zero open-panel residual; a tiny layer endpoint does not imply zero integrated memory.

Git contains the executed core/tests plus concise documentation/results. The full source ZIP contains code/run.py, code/reference.py, exact inputs, all raw logs/results, full theory/report/handoff,20-row ledger and figure. Commands for the full saved-input consumer apply only to that archive. Do not rerun completed science for delivery verification.

One saved-results figure was generated and read, with no clipping found; it is a log-scale upper-bound comparison, not a confidence or convergence plot. Single-column physical print and distinct-author visual review were not performed.

## Admission, resources and preservation
Stage outputs18/20; distinct-author R6/C9 NOT_RUN. Serial alternate methods and CAS do not satisfy those reviews. Parent review holds remain separate. Conditional supplier analytic/MP allowances are hypotheses; exact consumer arithmetic does not certify physical input accuracy. Physical radii/globalcompletion/E_QSS_old=null,L4false.

Tests/science childCPU1.045317s/wall1.050285394s,wrapperCPU0.006106184s. PlotCPU3.696334762s/wall3.828997285s separately. Known child+plotCPU4.741651762s/wall4.879282679s; preparation/network/model/preservation costsunknown. Allocation closed; historical allocations remain closed/nontransferable. Central/main/foreign writes0,merge0. Next action is one distinct-author saved-evidence R6/C9 review of this fixed unit, not another automatic node.
