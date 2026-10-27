# Independent DAG and delivery-metadata review

Reviewer: `/root/b3g_midpoint_intake`, independent of metadata assembly.
Scope: source pointers, claim scope, original-contract/dependency preservation,
selected current-status updates and publication binding. No tests, moments,
core RHS calls, IVPs, scientific reruns, figures or publication actions were
performed for this review.

## Fresh authority and reviewed scope

The canonical ref was read again before this metadata node and remained
`rei_bianchi@a5db4bac9dafadae29685bbea3cec7f43ab990b2` on
`research/orchestration-sandbox-20261022`. The fresh AGENTS blob remained
`429a5a13ee75b1222bc50627f8d5973d01dd21c4`, matching the policy already read.
Parallel PR233–236 remain attributed to their separate unmerged branches in
CENTRAL_RETURN.json; no result or budget from them was adopted here.

The reviewed source documents are the new unit's ADMISSION.json, REPORT_KO.md,
CENTRAL_RETURN.json, local DAG.json and the central assembly from the immutable
`central_base_b3g_20261027` snapshot into `central_b3g_20261027`.
The R9 review file hash matches the reference recorded in ADMISSION.json.

Claim interpretation is consistent:

- Roughly 1e-11 is the reconstructed finite14-versus-saved-finite14 tensor
  consistency residual, on the positive photon-energy scale.
- The 2e-8 checks concern the operational numerical error budgets of the
  higher angular rule on the same prescribed geometry. They are not physical
  error certificates.
- ANISO continuum-versus-finite14 joint difference is
  `3.447529542803539e-5`. ADMISSION explicitly says finite14 does not agree with
  continuum at 2e-8, and REPORT explains the angular-model distinction.
- Physical eS/en/eE/geometry/total radii remain null. Original midpoint bytes,
  historical floating interval enclosure, continuous nonlinear tube,
  continuum-feedback trajectory and native finite absorption are not admitted.
- The geometry consumer keeps separate matter/radiation T and zero cQ/U/J.
  Whole physical completion is null, L4=false, B4/B5 NOT_RUN.

## Independent preservation comparison of the initial assembly

The reviewer compared objects by node ID and also checked ID order, list
lengths and every nonselected object, rather than relying only on the
assembler's reported booleans.

| Item | Observed result |
|---|---:|
| Central nodes before/after | 88 / 88, same IDs/order |
| Nested original contracts unchanged | 88 / 88 |
| Nonselected central node objects unchanged | 85 / 85 |
| Current-status rows before/after | 88 / 88 |
| Nonselected status rows unchanged | 85 / 85 |
| Authorities unchanged | 15 / 15 |
| Integration edges unchanged | 17 / 17 |
| Dependencies, conditional dependencies, external prerequisites | all unchanged |
| Other central DAG top-level fields | unchanged |
| Previous BASS return file | bytes unchanged |
| Local BASS nodes before/after | 16 / 16 |
| Local nested contracts unchanged | 16 / 16 |
| Local nonselected node objects unchanged | 13 / 13 |
| Canonical changed paths | exactly 9 |

The three selected nodes are B3g-actual-cohort-binding,
B3i-calibrated-geometry and B2-G1C-error-transport. The nine changed paths are
the central DAG, CURRENT_STATUS, three contract wrappers, three node plans,
and the new BASS_B3G_MIDPOINT_TRANSPORT_20261027 return. B3c/B3h and all foreign
nodes are preserved.

## Initial metadata findings requiring a small repair

### D1: active status-observation pointer remained on the prior result

The initial assembler wrote a new `node.observation` while leaving the
established `node.status_observation={source_file,json_pointer,value}` unchanged.
For all three selected DAG/contract/node-plan/local-DAG wrappers,
`current_status` therefore described the new midpoint result, while the active
status pointer still referenced BASS_B3G_ACTUAL_BINDING_20261025 and its older
status. The new observation contents themselves were correct.

Minimal repair: update the established status_observation wrapper to
`returns/BASS_B3G_MIDPOINT_TRANSPORT_20261027.json#/observations/<node-id>`,
with value equal to the corresponding new observation. Remove the newly
introduced duplicate observation field from those wrappers. CURRENT_STATUS
already uses its own `observation` field, which should retain that existing
schema. The new observation's prior_evidence and the unchanged old return
preserve the prior result. Nested scientific contracts remain untouched.

The node-plan `Source:` header actually names the original authority contract
(`authority/numerics/BASS_CONTRACTS.json#/nodes/N`); that is correct and should
remain. It is distinct from the updated current-status evidence pointer.

### D2: local current-base provenance inherited an unqualified old snapshot

The initial local DAG relabelled base_central_commit as a5db4bac while retaining
`provenance/CENTRAL_DAG_REFRESH_3f28727.json` and its older snapshot hash as
though they were current new-lane snapshot coordinates. That relative path
does not identify the new base in the new lane.

Minimal repair: give the current base a pinned a5db4bac source URL (and actual
current snapshot identity if locally included), while explicitly qualifying
the old snapshot as historical parent-unit evidence. Do not rewrite the old
snapshot's hash or scientific content to make it appear current. This is a
locator/attribution correction, not a new scientific gate.

## Publication binding at this review stage

The three consumer_source_commit fields are null before an actual science
commit acknowledgement, with explicit BIND_ONLY_AFTER_ACKNOWLEDGED_SCIENCE_COMMIT
status. This is honest and expected. After the actual ACK, only the intended
commit-binding fields and their current-observation mirrors should change.
An acknowledged source commit is not yet evidence that the canonical DAG or
dual-provider uploads have completed; those require their own actual receipts.

## Transition

The structural and scientific-scope parts pass. Correct only D1 and D2 in the
existing metadata assembly, then recheck the changed pointers/provenance and
preservation comparison. No scientific rerun is requested. The final result
of that targeted metadata check is appended below.

## Targeted metadata rereview — PASS_SCOPED_METADATA / GO_FOR_PUBLICATION

Root authorized the small D1/D2 correction; the lower-tier assembler applied
it and regenerated metadata only. The reviewer inspected the changed fields
and independently compared the resulting objects again.

**D1 CLOSED.** All nine selected DAG/contract/node-plan wrappers now use the
established status_observation pointer to the new return. Every pointer/value
resolves to the exact matching observation, and each current_status agrees.
The three contract wrappers and node-plan JSON objects equal their canonical
DAG nodes. The new duplicate observation field is absent there. The local
three wrappers mirror the same source pointers. CURRENT_STATUS retains its
established observation field and matches all three return values. All
node-plan Source headers still identify the unchanged authority contract.

**D2 CLOSED.** The current base is explicitly located at the pinned URL
`https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5db4bac9dafadae29685bbea3cec7f43ab990b2/research/orchestration_expansion_20261025/DAG.json`.
Inherited snapshot fields retain their old identity and are labelled
`HISTORICAL_PARENT_3f287279c9ae4e8bcd4949a56b8c4cc0601b1eb8_NOT_CURRENT_BASE`.
They are not represented as current new-lane snapshot evidence.

The independent reread confirms the preservation counts above: 88 contracts,
85 nonselected nodes/status rows, 15 authorities, 17 edges and every original
dependency remain unchanged; the prior BASS return is byte-preserved. The
local 16 contracts and 13 nonselected nodes remain unchanged. Exactly the
same nine canonical paths differ from the base. Selected wrappers change
only current_status, pass_next_action and status_observation.

The repaired assembly script SHA256 is
`81595e022a3b5821bd39523ea7455fd0f6349cabff7d1e35792cd7be36bcbf69`.
At this review point all new consumer_source_commit values are still null.
After an actual source-commit ACK, the intended binding-only mutation is
allowed; fresh expected-SHA/non-force canonical publication and actual backup
receipts remain root-owned execution steps.

**Remaining metadata blockers: 0.** Proceed with acknowledged source binding,
the nine-path canonical update, final source ZIP and dual backup. No change
to scientific code, raw output, tolerances, budgets or scientific admission
is required, and no scientific rerun is requested.
