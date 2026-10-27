# B3h native effective-H Lyα: source input intake

## Scope and actual result

This is a fresh read-only source intake for one native scalar FLRW incoming photon tube. No old tests/consume/plot, native solve, IVP, Ks/GEO computation, finite absorption transaction, or B3i RHS was executed. Only source retrieval, byte identities, NPZ metadata, and exact input extraction were performed. Scientific runtime costs for earlier campaigns and their unknown remaining budgets are unchanged; data I/O/metadata costs are not asserted to be zero.

The latest relevant REC branch is `research/rec-source-synthesis-20261027`, PR139, HEAD `d6dbe39a4923439547c01695d9020ba39367ea90`, verified at entry and again at closeout. PR138 stays `4a8e541030ee2cbd02e26ba671083b705d309d49`; LINE02 PR129 stays `a7c46fd8338971e2cefa776f5dd7b25a46974990`. The current complete tree has 7,581 entries and no root/ancestor AGENTS for the inspected source paths. Root AGENTS GET returned 404. Three AGENTS under docs/.../survey/atomic/sources are archived foreign-repo instructions, not ancestors. Live REC open PRs were inspected; no assertion of every repository or every blob search is made.

PR139 adds exact piecewise-linear fixed-source history retiming and knot/chord remainders, not a finite atomic reservoir. Its completed history results (313 bindings, 1,240 retimings, 313 chords, 30 controls) can be reused by identity. H5 physical epsilon/outgoing bound remains null and coverage 0/313.

## Exact prepared input

`FINITE_TUBE_INPUT_SLICE.json` is ready for the delegated arithmetic. It contains the actual native time cell [5126,5127] that contains eta=-log1p(1100), original binary64 eta0/h and stored endpoints, virtual row140 values at source knots 5123..5126, energy140, E21, source cosmology constants, and all 22 META fields from the actual target snapshot. Floating inputs are encoded as float.hex and remain round-trippable; eta0+k*h interpreted in exact real arithmetic is explicitly distinct from the stored rounded eta array.

Parent source:
- repo `cosmosapjw-quantum/rec_bianchi`, HEAD above.
- `data/pr05b2_source_history_v060.npz`
- 35,239,470 bytes, Git blob `de43b1a2642fa0aa049abbfd1b0a7d775d684b1b`
- SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`
- 7,489 eta knots, DLNA=8.49e-05, outgoing_virtual shape (311,7489), outgoing_lyman (3,7489), average_virtual (311,7489).
- Provenance locks the original HyRec October-2012 ZIP and hydrogen.c.
- This NPZ has no nH, x1s, x2p/xr2p, xe or atomic replenishment arrays. Actual key/shape inventory is in `HISTORY_METADATA.json`.

The source clock has a real finite interval, rather than an invented dt. The native Lyα face mapping is
```
incoming source = outgoing_virtual[140]
Esource = 10.199581 eV
E21 = 10.198714553953742 eV
eta_query = eta_face - log(Esource/E21)
```
The shifted tube crosses a piecewise-linear history knot; the implementation must split there or use the exact PL primitive. It must preserve strict-past reads. The prepared slice excludes index5127 from incoming history because the accepted prefix at the right face is 5127.

Source-bound map authority:
- `src/full_bianchi_hyrec/trajectory/causal_history.py`, blob `aebe34ba0b214bd8e283887db94f68fd48156847`, build_original_hyrec_queries / construct_original_hyrec_incoming.
- `research/rec_history_boundary_20261023/code/history_boundary.py`, blob `1aa7f134c332bc4596372df18c7c47306260ecfc`.
- `scripts/run_pr05b2_causal_history_stage.py`, blob `a1f606661e7bdbbdf78da66fa227c3a15d9572ae`, parse_raw_history and execute_hyrec.
- `scripts/c_harness/instrument_original_hyrec_pr05b2.py`, blob `f05e313b7ae5f2503c0a1e3d79232665e3c79340`, original diagnostic export.

## Source geometry, volume, proper clock and thermal reference

The actual source is the original standalone HyRec scalar FLRW model. Its original ZIP was obtained and byte-checked:
`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, 726,954 bytes, SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, Git blob `e02869896ab3b826eb64d8233f2a1272366c1fc8`.

`native_archive/HyRec/input.dat` gives T0=2.728 K, obh2=.021976, omh2=.13, okh2=0, odeh2=.343, w0=-1, wa=0, Y=.24, Nnueff=3.04. The original standalone source fixes fsR=meR=1; the pinned target snapshot independently reports these values. Original kBoltz=8.617343e-5 eV/K must be retained.

`history.c` uses TR=kBoltz*T0*(1+z); `hydrogen.c` rescales by fsR² meR. Hence for this source
```
TR(eta) = kBoltz*T0*exp(-eta)
f_ref(eta) = exp[-E21/TR(eta)]
f_in(eta) = f_ref(eta) + PL(outgoing_virtual[140], eta_query)
nH(eta) = 11.223846333047 * obh2*(1-Y)*exp(-3 eta)  [m^-3]
H(eta) = 3.2407792896393e-18 *
 sqrt(omh2*exp(-3 eta)+odeh2
      +4.48162687719e-7*T0^4*(1+0.227107317660239*Nnueff)*exp(-4 eta)) [s^-1]
```
This matches the selected native model assumptions; the cosmology is not a new inference from a modern cosmological fit. Actual proper duration is the finite integral of dη/H(η). Counts use H dt=dη, so no ad hoc frozen proper duration is needed.

Choosing a common comoving cell and the right endpoint reference slice gives J_V=exp[3(eta-eta_ref)]. The choice of reference is a stated representation convention, and the volume ratio follows the actual native FLRW geometry. The native line crossing measure then is
```
dmu = (3e6*LYA_FACT) * J_V * dη * dΩ/(4π),
LYA_FACT = 4.662899067555897e15 cm^-3.
```
This supplies a source-bound incoming finite count. It does not put the tube on the older B3g Bianchi geometry; either use the native FLRW map in the existing transport library or separately obtain a supported clock/geometry map. The old finite14 maps remain reusable in their own scope.

## Atomic owner search and exact remaining input

The current native hydrogen source explicitly computes x1s=1-xHII, solves xr and all virtual states algebraically at each native call, and writes outgoing Lyα departure = xr[1]/(3*x1s). The recorded Lyα row therefore exposes a ratio, not an absolute upper stock. The diagnostic outgoing row in the prepared slice is marked as such.

At z=1099.9986525171403, source index5127, the actual snapshot supplies:
- x1s=0.85507000330964777.
- nH_cm3=250.18675437302318.
- H=4.9696512229238343e-14 s^-1.
- TR_rescaled=0.25882399309326415 eV.
- native incoming/outgoing Lyα departures and the direct matrix coefficients.

These are one point; assigning them to the whole macro interval would introduce a frozen-coefficient model. The source-owned integrated atomic replenishment over the selected real tube is not present in this snapshot.

The existing PR05C1 macro was inspected instead of being assumed unavailable:
- `data/pr05c1_adaptive_short_trajectory_v062.npz`, 8,476 bytes, SHA256 `9323ca4ddac51f68522aa6d08a7de3b141d77c8e0ad0241a5d2d0fb2d8aaab3c`.
- It contains three final 314-component states and residual/controller summaries for z≈1300/1100/900.
- `adaptive_macro.py` frozen_coefficient_backward_euler_trial and `history_ownership.py` frozen_coefficient_backward_euler_step explicitly hold the source coefficient/snapshot values and incoming history fixed, evolve the electron variable, and keep 2s/2p/virtual populations algebraic.
- No per-channel gross direct-Lyα stock debit, lower/upper inventory history or non-Lyα replenishment ledger is stored in that NPZ. Its typed history append/rollback result is valid controller evidence but does not close the selected continuous-native-tube atomic owner.

REC PR43 `37a943347bf319af998230bb77c6f89827feddff` was also checked. It is LOCAL-02 momentum-owner binding, not an actual native finite-atomic macro. Its declared directional face reconstruction remains absent. The current scalar FLRW tube does not require inventing a 26-direction reconstruction.

The remaining minimum for a full finite absorption transaction is the matched absolute atomic population/stock and direct-Lyα versus non-Lyα replenishment owner on this same interval, with the corresponding internal-energy/recoil accounting. The original direct bound-bound event convention supplies equal/opposite radiation and atomic internal E21 transfer and zero recoil/kinetic heat for its declared approximation. It does not identify the full-network integrated replenishment over the interval. Physical eS/en/eE/geometry/total radii remain null.

The native photon counts must use HISTORY01's boundary law A=1-exp(-tau/q), not B3b LINE01's stimulated bath gross_counts. B3b's packet/stock conservation structures may be reused after binding the distinct native gross counts. Incoming stock alone is not permission to assume an unlimited upper-state source.

## Minimal next work

Execute the root-selected photon-tube calculation with the prepared input and original source conventions. Report its incoming count, proper duration, common-volume conversion and transported radiation stress as a completed photon subunit. Keep finite absorption count and B3i absorption consumption pending until the exact atomic interval owner is provided. A narrowly instrumented REC return should supply matched endpoint x1s/x2p, nH and source coefficients/opacity plus the interval's direct-line and replenishment ledger or an already accepted native finite substep, preserving its own source and cost provenance. No other future species/provider is added as a prerequisite.

All source reads and original bytes are locally available under this directory; `SOURCE_IDENTITIES.json` and `NATIVE_ARCHIVE_MEMBER_IDENTITIES.json` provide the identity list. The parent will incorporate selected results into the Git-backed deliverable and handle publication/backup ACKs.

