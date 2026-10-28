# B3h: signed Lyalpha initial-memory enclosure

UNIT=BASS_B3H_LYA_DUAL_WITNESS_20261028
BASE_F=5c3623cb06280561853b00b33d74ae638ab24c82
STATUS=EXACT_CONDITIONAL_DUAL_BOUND_IMPLEMENTED_INDEPENDENT_REVIEW_PENDING
Outputs18/20; distinct-author R6/C9 NOT_RUN. Original canonical DAG record28/88,delta0,AUTO_NEXT_NODE=false. Parent PR215/212 review holds remain separate.

## Scientific result
A constant nonnegative dual storage vector reduces the same-source scalar count ceiling by26.35492789785144%. Both comparators receive the same known sign. The new outward displayed signed count/V0 interval is[-9.23774001952287462461e-23,0]m^-3, versus the same-input scalar magnitude1.25435955941624615155e-22m^-3. Old/new magnitude ratio1.35786410611827685. This improves a conditional bound, not physical accuracy, an observed correction, or runtime speed.

For the same prescribed future law, x=p_reset-p_carry satisfies xdot=-M(t)x and the output is DeltaC=integral N*R(t)*x2dt. The same R appears in M22 and the count row. M=[[a,-beta],[-chi,d+R]], with positive diagonal and nonpositive off-diagonal entries; its non-Lyalpha coefficients are affine between the actual saved cut and right endpoint. Proper time is in seconds, p dimensionless,N in m^-3,R in s^-1,w in m^-3. Common V0=1m3 and source cQ/Q conventions are unchanged; metric(-,+,+,+), c/hbar/k_B retained.

## Derivation and exact scope
Let k=max_endpoint chi/a and s=min_endpoint(d-beta*k)>0. The linear-fractional ratio has endpoint extrema. Define w2=N*Rmax/(s+Rmax),w1=k*w2. For0<=R<=Rmax, the first component of M^T*w-N*R*e2 is(a*k-chi)*w2>=0. The second is at least N*s*(Rmax-R)/(s+Rmax)>=0. Affinity covers the whole endpoint/rate box, not only its sampled corners.

The positive forward propagator Phi obeys, for y=Phi*v with v>=0,

    d(w^T*y)/dt <= -N*R*y2,
    0 <= integral N*R*y2 <= w^T*v-w^T*y(T) <= w^T*v.

Splitting signed x into positive and negative parts gives

    -w^T*x_minus <= DeltaC <= w^T*x_plus.

Use max(-lower_i,0) and max(upper_i,0) for a saved initial box. Incoming is unchanged, so net-count and outgoing-count differences agree in this scope. No commutativity assumption or exp(-integral M) replacement is used. Locally bounded measurable coefficients suffice. The native application stops at the recorded cell endpoint; it is not extrapolated beyond that source domain.

Any feasible constant nonnegative v has v1>=k*v2. The second endpoint constraints at Rmax therefore require v2>=N*Rmax/(s+Rmax), and hence v1>=w1. Thus w is componentwise least within this constant-witness rectangular family. This is not sharpness of the actual finite trajectory or of time-dependent witnesses. If s<=0 the routine refuses this sufficient construction; it does not prove instability or rule out other certificates.

Native values: k≈0.930810208529154584,s≈213.613844000694911s^-1,w≈(1175574.7432335077565,1262958.5843188426145)m^-3. Both saved initial-difference components are negative. If the inherited cut L1 error is separately accepted, its added count magnitude is<=1.82956261974557054613e-42m^-3 and the sign remains negative. Physical/source errors and E_QSS_old staynull; global physical completionnull,L4false.

## Verification and retained discrepancy
14 new test methods: initial13 failing methods with24 assertion-failure events including subtests,1 pass; then unchanged14/14pass. Run from this subtree: python -I -S tests/test_dual.py. The published core and tests match the executed local Git blobs exactly.

One first primary launcher failed at local import under Python-I, before input/science. An explicit owned-code sys.path fixed only the import boundary. One actual saved-input consumer then returned exit0: all8 mandatory checks passed;11 of12 observation flags were true. The false exact-equality flag is retained. Parent scalar evaluation first rounded cut p onto512-bit intervals; new assembly subtracts exact written cut p from the same saved QSS intervals. The entire ceiling difference1.1910246553853464e-148m^-3 equals K*sum_i[ceil(2^512*p_i)/2^512-p_i] exactly. Both scalar enclosures contain the new interval; no raw result or tolerance was edited.

A separate Fraction halfspace-intersection algorithm, importing neither primary module, passes56/56 checks. It finds2 native feasible vertices and verifies4 nonnegative objectives, rational interior points and the exact constant-matrix gain M^-T*r. Removing shared R from loss while keeping it in output, or using the wrong transpose, produces negative dual residuals. Wolfram returns4 scalar zero residuals plus exact fixture and negative-control values, no warnings. These different algorithms/CAS are not distinct-author reviews.

## Literature, preservation and delivery
Linear copositive storage/L1 performance is established context: Briat, arXiv1204.3554v3, DOI10.1002/rnc.2859. Exa read its introduction/preliminaries, not every theorem. Baake/Schlaegel arXiv1011.1775 supplies nonautonomous flow context. The specialized two-state proof is given here; broad novelty is not claimed. SciSpace returns are discovery evidence, not native data.

Git contains this concise derivation, exact executed core/tests and summary. The immutable full source ZIP additionally contains run.py/reference.py, exact input/rational results, full theory/report/handoff/20-rowledger, failed/success logs, CAS, figure and unchanged parent ZIP. It is the restorable scientific record, not a claim of identical Git/ZIP file sets. FINAL_ACK.json is added only after actual provider completion. Do not regenerate ZIPs to include later ACKs.

New childCPU0.257890s/wall0.261343792s; wrapperCPU0.006777971s; saved-plot kernelCPU0.683744267s/wall0.685780548s separately. Preparation/import/network/model/preservation costs unknown,not0. Fresh allocation closed; old allocations closed and nontransferable. New nativeODE/QSSsolve/B3i/quadrature/oldcampaign0. No full-repo CI or production activation claim.

Survey:7repo unfiltered branch-name queries returned1426 entries and each reached terminal; this is sequential non-atomic metadata, not all branch bodies or all conversation/backup contents. Latest central observed3d8bcdb79a7062459adaad9be6d7fe951f86a17a, unchanged here. Central/foreign/main writes0,merge0. Existing native second-order particular/knot-memory results were discovered and reused rather than duplicated. Next obligation is one distinct-author saved-evidence R6/C9 review of this unit only.
