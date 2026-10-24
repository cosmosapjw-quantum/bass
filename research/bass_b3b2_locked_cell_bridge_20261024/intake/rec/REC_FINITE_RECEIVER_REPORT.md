# BASS B3b2 REC finite receiver intake — recovered report

## Recovery classification

This report reconstructs the original 2026-10-24 intake findings after the shared scratch workspace was observed missing. Its prose byte identity with the lost report is not claimed. The scientific source and input bytes are independently exact: 31 text files match their pinned Git blobs and all three NPZs match Git blob, byte size and the explicit PR43 SHA256 locks.

The original source census remains an observation from approximately 04:58 UTC. The later recovery performed one successful owner-ref readback after a URL-admission failure, confirming the same HEAD. It did not repeat the full census or any scientific computation. RECOVERY_TRANSPORT_RECORD.json distinguishes original acquisition, raw-store recovery, targeted source refetch, reconstructed metadata and unavailable preloss document hashes.

## Decision

A real, source-owned finite discrete photon occupation state exists in REC. Its actual 35 frequency states, 26 angular directions, mode measures and photon momentum scales are available. This supports a bounded REC inventory-to-BASS snapshot representation bridge.

The examined source does not supply a closed finite-stock LINE01 f_plus>0 atomic absorption update. f_plus is an incident boundary occupation. No source-owned identification with the finite COM cell average or completed native/COM atomic replacement has been established. This is a specific missing link and ownership obligation, not a statement that finite photon cells do not exist.

Admitted next unit: preserve the actual discrete number current and stress tensor of the saved source-derived bootstrap state using the stored G_i, p_i, A_j, directions and f_ij. No line-rate integration, newly chosen bandwidth, face closure, atomic debit or invented bath is needed for that snapshot unit.

## Fresh survey retained from original intake

Repository: cosmosapjw-quantum/rec_bianchi.

| Item | Original observed result |
|---|---|
| Latest-created PR | 132, research/rec-history-characteristic-resume-20261024 |
| Source HEAD | ae189694c15e09c6f96c44ef6b74b48afc2632ac |
| Branch census | 150 entries, pages 100 + 50, exhausted |
| All-state PR census | 132 entries, pages 100 + 32, exhausted |
| Selected current tree | 6,183 entries, truncated=false |
| Governing REC AGENTS | Root 404; complete tree contains three archived foreign-repository survey copies, no governing ancestor of selected source paths |
| Current source files originally checked | 28 |
| Relevant parallel source files originally checked | 3 |
| Scientific execution by intake | 0 |
| New IVP / old campaign replay / archive download | 0 / 0 / 0 |
| Remote mutations | 0 |

This exhausts accessible REC branch/PR metadata at the recorded time. It does not claim every blob in all 150 branches was read. Targeted source inspection covered current receiver/source/history code and relevant alternative lineages: PR34/36/42/43/47/63/70/71/73/75/78/80 and target-grid refinement. Their preserved readbacks are in PARALLEL_PR_READBACK.json.

The fixed central authority and the user's explicit physmath 1.0.0 workflow remain applicable.

## Exact input bytes

All three input blobs are identical between current PR132 and the inspected prior owner lineage. They total 746,322 bytes.

| File under inputs/data | Git blob | Bytes | Selected arrays |
|---|---|---:|---|
| z1100_direct_network_node.npz | 40e49ae67f2894a75f97bace372bb70b9a91ce4a | 127,382 | mode_measure_m3[35], momentum_scale[35], state_intervals[35,2], temperature_K |
| pr01c_background_snapshots_v048.npz | fdcbb6e84c398773ca4ef084c9d38213f1759670 | 613,650 | directions[26,3], angular_weights[26] |
| pr05c2c1b2b1e0_source_derived_parent_v073.npz | efb59de1e8f9109282cfdcbefaf7ce136f60ffc9 | 5,290 | occupation[35,26], scalar_occupation[35], state_intervals[35,2] |

SHA256 locks, respectively:

- e6a28194d183658a87f0974afe3f46323106382970a85338f9ce94c20c7b5736
- df136bca7c120054cc45cf2b4fc2bd52acc3d60e6159b0f63c2622de03f2f03c
- c74a2a0e69d6d34c338d19af2f123d1eb32130ac103a68e4494a2c9542eaa958

During initial intake the containers were opened with allow_pickle=False for array schema inspection only. During recovery the original base64 responses survived in functions.store; all three original binaries were decoded and hash checked without another network acquisition.

## What the saved state means

Current source_derived_parent.py, blob e04e590d43f4c2d7dfa184106fc4492e5bdb63de, specifies:

1. The accepted scalar-history endpoint must match the atomic snapshot index and redshift.
2. The source's own point-characteristic rule is evaluated at the arithmetic COM frequency centres.
3. Each query selects the least native source energy strictly above its target and queries strict-past history in eta=ln(a).
4. The total occupation is Planck reference plus the signed distortion.
5. The scalar result is lifted isotropically over the supplied hydrogen-frame directions under the explicit scalar/unpolarized initial-data axiom.
6. The result is a bootstrap INITIAL-DATA state, with coupled_macro_endpoint=False.

The builder is restricted to the validated Bianchi-II background branch. The stored state is not a completed coupled endpoint and does not reconstruct missing anisotropic native data. A general adapter may use separately labeled anisotropic diagnostic arrays, while preserving this qualification for the actual input.

## Finite-state normalization and energy authority

The actual REC number routine uses

n_ij = G_i A_j f_ij,
n_gamma = sum_ij G_i A_j f_ij,

with G_i in m^-3, f_ij dimensionless and normalized angular weights sum_j A_j=1. HarmonicGrid.from_directions normalizes the raw angular weights by their sum. No additional 4*pi or polarization factor belongs in this formula.

The analytic full-angle two-polarization frequency measure is

G_i = 8*pi*(nu_hi^3 - nu_lo^3)/(3*c^3).

frequency_liouville.py checks this expression against the locked network for a compatible supplied frequency coordinate. It does not authorize inferring native cell boundaries from zero-width spike centres or choosing a new Doppler width.

The actual discrete energy authority is

E_i = c*p_i,
p_i = CollisionNetwork.momentum_scale[i].

It must be taken from the stored array. The analytic uniform-cell centroid is a diagnostic, not an alternative owner.

### Correction history retained

Early source exploration suggested using a recomputed geometric centroid energy. Fresh PR43 reading showed that this repeats an already repaired owner error: PR42's reconstructed target energy differed from the locked momentum owner by up to about 5.5440192880951145e-08 eV. PR43 corrected its witness to momentum_scale*c/electron_volt. The selected RED witness discrepancy was 5.540597669551062e-08 eV.

The intake and theory agents corrected their proposal before new scientific implementation/execution. The first suggestion is not rewritten as initially source-valid.

PR43 HEAD: 37a943347bf319af998230bb77c6f89827feddff.

- physical_split_reference.py blob: 57532b974c29ad51c6ec1ed79e3dbc7f9280f77a.
- Momentum-scale repair record blob: 2993b61d341edf3a6b152e7ce536da4484bf14df.

The same source rejects a default-3000-K substitution for the actual direct-node measure and leaves the native-versus-modern Doppler choice unselected. The proposed snapshot bridge requires only the stored G_i and p_i.

## Actual ownership and call graph

| Lane | Actual path | Scope |
|---|---|---|
| Saved finite radiation | Accepted scalar history → point characteristic → source-derived bootstrap parent → stored f_ij with G_i,p_i,A_j,n_j | Finite radiation initial data eligible for snapshot conversion |
| COM recoil | BoseCollisionRuntime.evaluate → nonlinear Bose pair/same-cell operator | Photon-number-conserving redistribution; no LINE01 upper/lower population owner |
| Frequency transport | ConservativeFrequencyLiouville._face_flux → evaluate | Internal upwind cell traces; supplied native red/blue occupations; exact face energy and representation correction kept distinct |
| Far-domain interface | ExchangePacket → BoundaryTransferAccumulator → FarBoundaryAdapter → CoupledInterfaceProblem | FR00/FB02 at x=-21.25/+21.25, Delta f=sign*nH*q/G_i; pure representation transport, zero atomic source |
| Detached LINE01 | LineState → exchange_source / thick_local_step | Detached two-level populations and line internal energy; f_plus remains fixed external input |
| Native atomic/history | Original 2+311 atomic algebra and strict-past outgoing history → boundary → line_ledger | Boundary occupation encoding and signed net line ledger, without a duplicate extra radiation source |
| PR132 characteristic | Retarded constant-shear crossing → supplied angular history field → reference conversion → inherited boundary/ledger | Specified characteristic improvement, no admitted finite LINE01 bath |

The interface really has a finite occupation increment, but CoupledInterfaceProblem constrains each supplied packet scale by rho-1=0. It is not evidence of a self-consistent finite reservoir driving LINE01.

The actual recoil operator constructs opposite photon/atom four-force contributions for redistribution. That does not introduce an atomic excitation stock owner.

## Atomic and photon event ownership

LINE01 source blob 5ac2a3107b80710504e63705ff16562131b5d1cf distinguishes

R_down = A*escape_mean*n_u*(1+f_plus),
R_up = A*escape_mean*g*n_l*f_plus,
R = R_down - R_up.

It assigns dn_u=-R, dn_l=R and dn_gamma=R, with du_internal=-E_line*R, du_radiation=E_line*R and du_thermal=0. Its finite map keeps f_plus fixed. These formulas alone do not supply a finite photon-stock absorption debit.

history_boundary.line_ledger uses the signed native occupation jump and an exclusive boundary/event owner, and returns occupation_is_boundary_encoding=True, extra_radiation_source=0. Adding another radiation source to the same boundary encoding would double count.

full_2012_atomic_source.py returns an uncommitted outgoing-history candidate. The native real departures and 311 zero-width virtual spikes are not COM cell number densities.

dynamic_macro_ownership.py, blob a196840d164aa7497b27178c1a38ca0f9627c426, states that current COM is a valid collision/transport subproblem; native atomic source remains full, COM atomic source is disabled, replacement_complete=False. The resolved split-domain configuration is a contract witness rather than an implemented operator.

## Frame and clock

Selected directions and finite modes are in the local hydrogen tetrad. A snapshot inventory conversion assigns no emission clock and infers no U/J/PiRate.

BackgroundSnapshot carries physical rates and cosmic time. hydrogen_frame_characteristic uses R_H=R_normal+D0_log_D, retaining the same derivative D0. It is not automatically a generic hydrogen proper-clock rate. Scalar history uses eta=ln(a); detached LINE01 uses its declared local proper-time interval. A future event-rate coupling must identify and transform those clocks explicitly.

BASS's state packet weight transformation w_new=w*E_new/E is a state-density rule. It must not be applied to the B3a invariant event-rate measure dR.

## Related-branch conclusions retained

- PR34's native-proxy split candidate remained blocked. PR36 added context and deposition components without admitting a physical replacement.
- PR43 closed the locked momentum-energy witness defect but selected no physical deposition map; scalar history rank 1 did not identify the required 26-direction face.
- PR47 provided directional contracts and source assembly while preserving the absent physical face.
- PR63 completed a typed numerical deposition adapter; physical source/map authentication and provider admission remained false.
- PR71–75's older BASS ModeB/read/scatter work and actual original component calls do not authenticate a finite LINE01 absorption reservoir.
- PR78's entropy counterexample shows why number and energy conservation alone cannot authenticate arbitrary read/scatter choices.
- The target-grid-refinement branch explicitly used a manufactured reference measure 8*(1+u^2)du m^-3. It is not an actual photon phase-space or BASS cell authority.

These findings reuse old evidence and read actual source. No historical numerical loop was rerun.

## Exact remaining fields for finite LINE01 absorption

1. A source-qualified identification of incident f_plus with a finite occupation state and its upstream trace/characteristic, frame and clock.
2. A physically owned frequency/angle reconstruction and channel allocation consistent with that trace.
3. One atomic population/internal-energy owner with native overlap terms removed or replaced.
4. One transaction committing atomic populations, photon depletion/emission and genuine boundary/history transfers once.
5. An energy rule matching actual absorbed photon energy to the atomic transition; any mismatch must belong to an existing physical recoil/thermal owner.
6. Dynamic derivative, input uncertainty, accepted-state and restart contracts if this is later evolved.

No reservoir, native bandwidth, positive seed, positivity clipping or arbitrary background replacement was introduced.

## Independent R6 review and recovery status

The separate PHYS_MATH_REVIEW.md preserves the original independent review: initial P0=0/P1=0/P2=3, one documentation repair, then PASS_SCOPED with no open findings. The three corrections clarify the scalar density boost notation, actual isotropic bootstrap qualification and absence of Source construction. That review was not rerun during recovery.

| Stage | Scientific disposition | Storage/publication disposition |
|---|---|---|
| Original REC census | Accessible metadata survey complete at recorded time | Preserved structured records reserialized after loss |
| Original source intake | 31/31 source identities checked | All 31 now recovered exactly |
| Original new finite inputs | 3/3 source objects identified and byte checked | All 3 now exact from preserved base64, no redownload |
| R6 theory review | PASS_SCOPED after recorded P2 closure | Review write text and closure patch replayed; preloss file hash not available to child |
| Initial S0 package | No science promotion from package creation | LOST_BEFORE_UPLOAD, no publication/backup ACK |
| Recovery package | Controller-owned subsequent work | Must have a new archive identity and actual provider ACK |
| Snapshot implementation | Separate subsequent gate | Intake did not run science |
| LINE01 finite-bath coupling | Specific missing ownership/link retained | No implementation or publication claim |

All historical remaining campaign budgets remain null; budget_reset=false. No elapsed historical subtotal is repurposed as a remaining budget. Merge and production activation remain prohibited.

## New post-reset metadata epoch: 08:33 UTC

A separately requested full REC metadata refresh found 151 branches (100+51) and 133 PRs (100+33), with pagination exhausted. Relative to the original 04:58 observation there is one added branch/PR and no changed existing branch or PR HEAD.

The new PR133 is research/rec-history-refinement-envelope-delivery-20261024 at a67044c411b4bef8d5762b4171c0c088fa34f161, Draft/open, based on the selected ae189694 parent. Its scope is the stored h2/h4 history discrepancy envelope; the PR body retains physical-target calibration and production limits and separates stage publication from prior numerical work.

NEW_POST_RESET_CENSUS.json and NEW_POST_RESET_RAW_METADATA.json preserve this fresh epoch separately from the historical census. A complete nontruncated tree at the pinned new head confirms all three NPZ blobs and six relevant source-owner modules are unchanged (9/9). See PR133_SELECTED_SOURCE_IDENTITY.json and PR133_TREE_METADATA_DIFF.json. The selected scientific input authority remains ae189694 and no new state evolution, history input or LINE01 finite bath was adopted.

