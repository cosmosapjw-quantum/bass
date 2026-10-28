# B3h: two-sided finite-horizon Lyalpha reset bound

UNIT=BASS_B3H_LYA_TWO_SIDED_FINITE_20261028
BASE_F=fed29a0195ca9bec270971abe4ed60c7d23cff29
BRANCH=research/bass-b3h-lya-two-sided-20261028
Original canonical DAG record28/88,delta0,AUTO_NEXT_NODE=false.

## Actual result
For the same prescribed future law and the saved two-state initial box, the outward displayed count/V0 interval is

    [-9.2377400195228746246075091729343930012548893614731e-23,
     -9.2228051494436688772104100455929123198766243548425e-23] m^-3.

The parent's interval had the same lower endpoint and upper endpoint0. Width decreases99.8383276640429%, but maximum absolute magnitude is unchanged. This is a deterministic conditional enclosure, not an observed native correction, physical accuracy improvement, statistical confidence interval or speedup. Exact numerators/denominators in the full source ZIP's evidence/PRIMARY.json are authoritative.

## Definition and proof
Let xdot=-M(t)x be the difference of two populations with identical future forcing, rates, observer and reference-volume convention. M=[[a,-beta],[-chi,d+R]], with affine non-Lyalpha endpoint coefficients, positive diagonal, beta/chi>=0 and0<=Rmin<=R<=Rmax. Output J=integral_0^D N R e2^T Phi(t,0)x0 dt. -M is Metzler, so Phi>=0; no commutation between different times is assumed. Proper time D is seconds, M/R/gamma have s^-1, N and output have m^-3, x is dimensionless. Parent(-,+,+,+),c,hbar,k_B,cQ/Q conventions remain.

Set km=min_endpoint(chi/a),sp=max_endpoint(d-beta*km)>0 and v2=N Rmin/(sp+Rmin),v1=km*v2. Then

    (M^T v-r)_1=(a*km-chi)v2<=0,
    (M^T v-r)_2<=(sp+R)v2-NR=N*sp*(Rmin-R)/(sp+Rmin)<=0.

Affine endpoint conditions cover the whole coefficient segment. For any other constant nonnegative lower witness z, its first inequality gives z1<=km*z2. The second inequality at Rmin then implies (d-beta*km+Rmin)z2<=N Rmin at each endpoint. Hence z2<=v2,z1<=v1: v is the componentwise greatest lower witness in this constant-vector family. This is not finite-trajectory or time-dependent-witness sharpness.

The parent upper vector w, computed using kp=max(chi/a),sm=min(d-beta*kp)>0,w2=N Rmax/(sm+Rmax),w1=kp*w2, obeys M^T w>=r and is reused exactly. For y>=0, integration of the two storage derivatives gives

    v.y(0)-v.y(D) <= J(y(0)) <= w.y(0)-w.y(D) <= w.y(0).

The lower terminal term cannot be dropped: the resulting claim is false at D0. Column sums give gamma=min_endpoint(a-chi,d-beta+Rmin)>0 and ||Phi(D,0)||1<=exp(-gamma D). For positive integer m, log(1+z/m)<=z/m yields exp(-z)<=B_m=(1+z/m)^(-m). At fixed m8, each integrated response coefficient h_i therefore satisfies

    L_i=max(0,v_i-max(v)*B_8) <= h_i <= U_i=min(w_i,N*Rmax*D).

Taking all four products of [L_i,U_i] and each signed initial component interval, then summing their extrema, gives the output enclosure. This is conservative; simultaneous attainability of all component endpoints is not claimed. D0 yields exactly0. Rmin0 yields v0 and no fabricated nonzero lower bound. A separately accepted same-model initial L1 error E widens both endpoints by max(U)*E.

## Source binding and scope
The new positive Rmin is extracted from a pinned saved producer and result, not recalculated by a historical driver. That producer stores gamma_saved=min(cmin0,cmin1+Rlo). An exact strict gamma_saved<cmin0 check identifies the second branch, hence Rlo=gamma_saved-cmin1. Here Rmin≈1.0829423210171585953s^-1,Rmax≈1.0835299335433259738s^-1. This source-specific inversion must not be applied to an arbitrary contraction bound.

D≈1707189026.6166900604s is the exact written duration-minus-cut literal, not a newly calibrated physical-time interval. All five copied input files and the producer identity are pinned in the full source package. The stored QSS interval is reused; no new QSS solve, native ODE, B3i, old quadrature/test/plot/campaign is run. E_QSS_old, physical/source radii and global physical completion remain null; L4=false. Future feedback or a changed source needs additional forcing terms and is outside this theorem.

The native v≈(1173657.3106044729,1260922.3261053292)m^-3 and w≈(1175574.7432335078,1262958.5843188426)m^-3. The terminal B upper is5.179109944254354e-85. An additionally accepted inherited cut error contributes<=1.829562619745571e-42m^-3. Even that conditional interval excludes zero; no unprovided physical uncertainty is inferred.

## Actual implementation and validation
code/bounds.py is the exact executed Fraction core. tests/test_bounds.py is the exact executed test file. On a separately authorized execution, the standalone focused command is `python -I -S tests/test_bounds.py` from this subtree. Do not automatically rerun completed evidence to verify delivery.

18unit methods: RED14failed methods/21assertion failure events(including subtests)/4passes, then identical GREEN18/18. Some later assertions in a method were not reached in RED after its earlier failure; no per-assertion RED claim. Single actual saved-input primary17/17. A different-method reference imports no production module:125/125,3lower vertices/2upper vertices,24triangular analytic fixtures at log2 with exact rational exponentials. Those fixtures validate the derived inequalities independently; they are not reruns of a native path. CAS4scalar zero residuals; no warnings observed.

The full source ZIP contains the actual saved-input driver, independent reference, five unchanged input files, exact primary/reference JSON, full proof/report,20-row ledger, commands and logs. Git is this runnable core/test plus concise proof/result projection; it is explicitly not the same whole file set. The artifact's reference method does not become a distinct-author review.

The first saved-results figure detected a clipped final tick and failed its layout assertion. Original files/receipt/code were retained. One right-margin-only repair (.96→.88) passed canvas bounds and was visually read. Same source hash/numbers, no science replay. The figure is a zoomed deterministic interval; parent upper0 is off-scale. Physical print and independent visual review NOT_RUN.

Measured new childCPU0.227957s/wall0.231051202s, wrapperCPU0.004601087s. First plotCPU3.719237467s/wall3.867381673s, repairCPU0.081621876s/wall0.081344020s. Known child+plotCPU4.028816343s/wall4.179776895s. Preparation/intake/model/network/preservation costs unknown,not0. New allocation closed; old allocations/remaining null unchanged and nontransferable. One diagnosed presentation repair, no scientific repair/replay. No whole-session speed or cost claim.

## Progress, survey and delivery
Work outputs18/20. Distinct-author R6/C9 remain NOT_RUN; parent217/215/212 holds are separate. Native delegation not exposed; serial fallback recorded. Canonical28/88,delta0; no central/foreign/main writes or merge. The parent1426-name inventory is reused and seven repositories' relevant current refs/updated PRs were checked, not a fresh exhaustive read of all branch bodies, conversations or backup bytes. BF3B/REC/WU changes are separate and not new inputs or extra DAG counts.

S0 publicationf8f830fbf5dc72a5a1a3aeb99cd418ff902b7cd8 has actual Drive1Lo_3OcHyxoy3FMbCRzZSaAmNWpn-CLhF and Dropboxid:BSpOijBcT10AAAAAAEDJVw completed ACKs plus separate44482byte metadata. Full-source backup and later receipt will use actual returned IDs; final FINAL_ACK.json is authoritative. Shared checkpoints are not20separate uploads.

Next obligation: one distinct-author R6/C9 saved-evidence review of this fixed unit, focusing on lower signs, terminal storage, active-min recovery, numeric semantics and the actual caller. Do not repeat the same self-audit or completed calculation without a concrete new defect. Stop before another node.

Literature context: Briat arXiv:1204.3554v3 SectionsII–III supplies positive-system/copositive-storage background. The finite-horizon specialization above is derived explicitly; no broad novelty or source-validation claim is imported from the paper.
