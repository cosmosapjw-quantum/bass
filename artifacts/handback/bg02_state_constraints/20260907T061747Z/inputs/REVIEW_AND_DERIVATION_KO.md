# BG02 candidate AUX acceptance and state-to-constraint code slice

Date: 2026-09-07 KST. Main-thread source/result review; newly authored code is PREPARED_UNEXECUTED.

## Accepted evidence, not a new replay

Publication `2e1b6e2f12cc766c8ffe1160d6371a88730064a8`, tree `adaf75ab7f695e2210c76b68cd450d152dc319fe` contains the user's returned comparison under `artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/`.

The main thread read the handoff, source comparison, source identities, the complete repair1 final JSON, original stdout, actual repair1 process receipt, the raw momentum TestEvaluated event, the loader patch, the actual BG02Convention owner and EinsteinProjection consumer. The publication commit/tree was independently read through the GitHub Git-data GET API. A whole-archive local rehash was not performed.

Observed previous local executions:

| Lane | Success | Failure | Unevaluated | Exit | Meaning |
|---|---:|---:|---:|---:|---|
| Historical, reused | 16 | 1 | 0 | 1 | Historical physical sign conflict preserved |
| Candidate original | 0 | 0 | 17 | 2 | BLOCKED_RICCI_NOT_EVALUATED before TestReport |
| Candidate repair1 | 17 | 0 | 0 | 0 | PASS_AUXILIARY_ONLY |

The repair1 run was 2026-09-07T05:32:25.046547Z to 05:32:29.413943Z (14:32 KST), elapsed 4.366318712942302 s. The final JSON reports all 17 exact IDs, all actual_messages `{}`, runtime_failures `{}`, and equal before/after WL source hashes. The original run is not 17 failed mathematical identities. It did not evaluate the suite.

The read loader diff inserts only `Authority/BG02Convention.wl` before the former four Get entries. This is required by the candidate's actual typed Ricci and owner momentum calls, and agrees with the separately read candidate init.wl load order. Original driver, original failure and repaired driver remain separate. No scientific-source change was made by that loader repair.

The actual owner uses coefficients {-1,1,-1} for {divK,gradK,kappaG*q}. The actual candidate event for AUX13_MOMENTUM_CONSUMER_SIGN is HoldForm[0], Outcome Success. The historical polynomial 2*C1 remains unchanged. We accept the comparison as component evidence that the inherited owner amendment removes that conflict in the tested path, not as new native tensor admission or a new sign repair by the main thread.

Actual candidate identity recorded and returned: `e404f914c0817b4c2ab3a0ff4632a8457e026fde`, direct parent `3c36458a8dbc9fe4092a24d5a09203327877f8d8`, tree `e2fc64860631e781082cceb3bef5b24fb8a06084`. Its necessary six files are now readable on GitHub inside the returned source snapshot; a missing top-level remote candidate ref does not block consuming that explicitly identified snapshot.

## Chosen next slice

The completed AUX tests computed sigma2 in the test and passed it to the scalar consumer. They do not test a path that takes a full shear tensor and obtains the norm and connection terms inside that path. We add one research-only map of raw ONF state to Hamiltonian and momentum residuals; we do not add a production RHS, integrator, family classifier, native suite, or another copy of the geometry generator.

Input keys are exactly `Hgeom,aB,nB,sigma,rho,q,Lambda,kappaG`. All entries must be exact, real under explicitly supplied consistent assumptions; kappaG>0; nB must be symmetric, sigma symmetric and trace-free, and nB.aB=0 must be established. Unknown or false structural identities return Failure, not projection. Approximate Real input is deliberately unsupported: floating tolerance and numerical domain policy have not been established in this slice. Einstein constraints may be nonzero. No positivity/energy condition for arbitrary matter is inferred.

## Derivation and equation-to-code map

Signature (-,+,+,+), epsilon_123=+1, K_ij=Hgeom delta_ij+sigma_ij, q_i=-h_i{}^a T_ab n^b, kappaG=8 pi G/c^4. Hgeom=H_time/c. No natural-unit convention is introduced. Hgeom,sigma,aB,nB have dimension L^-1; rho and q have energy-density dimensions; kappaG*rho and all constraint residuals have dimension L^-2.

For homogeneous tetrad components, e_j K_ik=0, but

```
D^j K_ij = -sum_{j,m} [ gamma^m_(j i) K_(m j) + gamma^m_(j j) K_(i m) ].
```

The storage is `gamma[[output,derivative,basis]]`, the actual existing generator contract. `StateConstraints.wl` calls `LeviCivitaConnection` and performs these two contractions directly; it does not hardcode a class-B divergence formula.

It calls the existing `ONFRicciTensor`, takes R3=Tr(Ricci), and computes sigma2=Tr(sigma.sigma) from the full input tensor. It then supplies the calculated carriers to the existing HamiltonianProjection and MomentumProjection. Homogeneity fixes GradientK=0 inside this map. It does not accept caller overrides named sigma2, R3 or DivergenceK.

The consumed authority is

```
Hres = (R3 + 6 Hgeom^2 - Tr(sigma.sigma) - 2 Lambda - 2 kappaG rho)/2
M_i = -D^j K_ij - kappaG q_i .
```

No equation is imposed by altering the input. The unmodified input is returned alongside the calculated carriers so this local mapping can be checked. This does not yet cover serialization, production state update, or an actual solver caller.

## Nonzero acceptance witnesses

For ell>0 and real u, set

```
aB=(1,0,0)/ell
nB=[[0,0,0],[0,2,3],[0,3,0]]/ell
sigma=[[0,0,u],[0,0,0],[u,0,0]]/ell
Hgeom=sqrt((13+u^2)/3)/ell
rho=q=Lambda=0.
```

Direct algebra gives R3=-26/ell^2, sigma2=2u^2/ell^2, Hres=0, and M=0. Delete only sigma13=sigma31, retaining the same Hgeom: the new M remains zero but Hres becomes u^2/ell^2. This is an input mutation in the test, not an allowed hidden projection in the map. It catches a map that discards exceptional shear even though the momentum test alone remains green.

A second exact class-B fixture with all independent shear entries nonzero and nonzero flux is

```
aB=(2,0,0), nB=[[0,0,0],[0,1,3],[0,3,-2]],
sigma=[[1,2,4],[2,-3,5],[4,5,2]],
q=(1/5,-2/7,3/11), kappaG=2.
```

In fixed reference units its directly derived divK is (-36,-10,-10) and M=(178/5,74/7,104/11). A proper rational rotation acts on aB,q as vectors and on nB,sigma as rank-two tensors. Hres is invariant and M rotates covariantly; the test does not use a zero momentum vector for this comparison.

The tests also cover I, II, V, an Hgeom=0 IX input, invalid shape/symmetry/STF/Jacobi conditions, and forbidden derived-scalar overrides. SC18 checks the existing owner's general divK/gradK/q arithmetic slots independently, but does not claim a spacetime gradient-operator proof. No family-wide solver readiness follows from these samples.

## Evidence-driven plots, not expected-value decoration

The test file evaluates five raw full-shear states u=-2,-1,0,1,2 at fixed Hgeom=sqrt(14/3) and ell*=1, plus their deletion mutations. It returns the mapper's actual Hfull/Hdeleted values. SC19 compares those evaluated results with the derived curves 1-u^2 and 1. The Python plot script reads only a genuine runner final JSON, preserves it, and plots those observed values and their difference. It neither invokes Wolfram nor substitutes expected constants if the run is absent or fails. The output is not time evolution or convergence evidence. Ratios at Hres=0 are not used.

## Review and execution status

The new tests were authored before the map. No observed new RED/GREEN exists. Main-thread Container and Python each returned ClientError before output, so no new source evaluation, syntax compilation, test pass, plot generation or plot inspection is claimed. The code is a concrete research draft, not deployed by BASS init.wl. Static review checked contraction slots, positive-K/q signs, sigma2 factor, H=0 regularity, no input projection, full-tensor rotation, result provenance and failure/unevaluated separation. Static drafting corrections are not advertised as runtime bug fixes. This is one author's sequential math/code review, not independent audit.

19 SC-prefixed cases are defined; their main-thread observed evaluation count is zero. Existing AUX13/AUX14, native17 and capture6 definitions and evidence are untouched. The accepted AUX result is not invalidated by this next slice being unexecuted.

## Primary sources and provenance

Actual project authority is the returned BG02Convention.wl and BG_02_CONVENTION_V2.json, with the returned consumer/geometry code. SciSpace discovery and arXiv abstract/metadata were consulted for H. van Elst and C. Uggla, gr-qc/9603026, and C. G. Hewitt et al., gr-qc/0211071. Those references motivate the orthonormal-frame and exceptional-model setting; no fresh full-text equation audit or new literature theorem is claimed here. The fixture and map equations above are explicit direct derivations using the already inspected project convention.

https://arxiv.org/abs/gr-qc/9603026
https://arxiv.org/abs/gr-qc/0211071
https://reference.wolfram.com/language/ref/TestReportObject.html

No GitHub Actions execution or dispatch is used. Final code/runtime validation and visual inspection of actual plots are the next narrowly scoped local-host task, specified only in the accompanying handoff file.
