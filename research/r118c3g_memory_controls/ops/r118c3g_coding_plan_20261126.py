from r118c3g_stage_driver_20261126 import *
if __name__=='__main__':
 assert len({(x['stage'],x['repo']) for x in map(json.loads,receipt.read_text().splitlines())})==30
 note('C1',[
  'Acceptance: reproduce R7 principal bound within 1e-12; compare actual native runs with configurable third mass, weight and initial S4. A zero bound is permission for a mathematical null, not proof of dynamic reachability. No changes to production default.',
  'Acceptance: shared gas x,T and accepted outgoing local window, exact H-only control and angular-on with same H and prefix. Require physical x,T, strictly causal source, full occupation >=0, normalized atom residual <1e-10, and time refinement. Export only local typed packet, not full REI donor. Independent physical stock remap conservation.',
  'Acceptance: same signed spectral energy/number ledgers, refined actual accepted C3B clock, local implicit prescribed-composition gas response. Energy residual <1e-14 eV/H per cell, positivity, source identity; compare n and xmin. No V11 production mutation.'])
 note('C2',[
  'Existing interfaces: _rustcore/examples/r118c3f_multi.rs calls ThomsonOwner::with_species; third mass, weight, S4 initial ratio and orientation can be parameterized in a new example. Projected wedge calculation uses old Gram and electron clock rei_q256.csv, no donor relabeling.',
  'Existing interfaces: run_history.py uses HMLAFlrwSource, original atomic source, canonical_history.step. Reuse exactly. C3F FULL_128 prefix supplies original gas and outgoing. Temperature equation is affine for fixed xe (H-only); physical source is original 2012, no replacement of archived data.',
  'Existing interfaces: SignedKompaneets.advance, FreeFree.advance, accepted history.csv and table_stages.csv. Gas-coupled candidate evaluation uses midpoint electron temperature/clock and fixed per-step composition. Explicit eV/H energy convention, no second Compton sink.'])
 note('C3',[
  'Algorithm: orthonormal span U via full SVD; induced basis wedge^2 U; compute singular values P3D; independent commutator projection. Extend native example with CLI parameters. W solve DOP853 as prior. Compare both bound and actual projected fraction; handle nonzero wedge norm.',
  'Algorithm: compute incoming once per accepted endpoint, solve scalar x with bracketed root after eliminating T analytically; keep history immutable across candidate evaluations. Use trapezoid and backward Euler with refinement. Separate conservative overlap in canonical q with explicit outside stock. Complexity O(Nray*Nbin*Ntime) history storage plus local atom solves.',
  'Algorithm: compute d from immutable old signed stock for each trial T; symmetric split C-FF-C; implicit gas residual using bracket between adiabatic prediction and radiation temperature when possible. Refine n and cutoff; record total energy ledger including expansion scaling. Boundary escape must be explicit, not silent clamping.'])
 note('C4',[
  'Execution: 4 native configurations (base, axial span, third mass and weight varied), low-resolution finite diagnostic; use existing cargo target and bounded parallelism; no new worktree. Then refined selected case if resources allow.',
  'Execution: 64/128/256 time levels and 32 rays, one 128-ray test if practical. Preserve actual accepted shared gas histories, complete one angular history, all errors. Stock remap on actual source state with manufactured oracle. Use same host src environment.',
  'Execution: replay fixed clock n=2048 and 4096 plus cutoff case; coupled prescribed-composition gas at n=256/512/1024 if feasible. Independent analytic instantaneous moment and sink ledger tests. Reuse existing data, no new worktree.'])
