# Independent PHYS-MATH R6 review — locked REC inventory / BASS snapshot bridge

**Current disposition after the focused repair readback: PASS_SCOPED; all three P2 items closed.** The initial findings and temporary documentation HOLD below remain as the first-pass record; the closing addendum identifies the repaired targets.

Reviewer: /root/b3b2_rec_receiver_intake  
Review time: 2026-10-24 05:11 UTC  
Mode: one bounded, read-only physics/mathematics review; no scientific execution.  
Author separation: this reviewer performed REC source intake and reported source-owner corrections; this reviewer did not author the reviewed contract or theory equations.

## Disposition

**PASS_SCOPED for the selected snapshot equations and implementation direction.**

- P0: 0.
- P1: 0.
- P2: 3 documentation/provenance clarifications, listed below.
- Numerical implementation, regression, figure and final scientific admission: **NOT_REVIEWED / NOT_RUN by this reviewer**.
- Publication documentation: **HOLD for the three P2 corrections**, which require no change to the bridge equations or frozen tolerances.
- The selected implementation may continue. The unselected conditional closed-cell and B3c alternatives are not admitted by this review.

This is a scientific review of the declared finite discrete representation. It is not an approval of LINE01 finite absorption, native/COM physical replacement, a trajectory, a production source, or a repository merge.

## Exact review targets

| File | SHA256 at review |
|---|---|
| b3b2_work/FROZEN_CONTRACT.md | e3fd629fadfdcdfc560b6c758be5404f95453b950d7422ebf84de8adc9cc7a1d |
| b3b2_work/theory/SNAPSHOT_BRIDGE_THEORY.md | ea03af7bee906cf1e522e4172b58ccb05ed01bb896f37b70765530380c5cf8fe |

Actual source used:

| Source | Verified Git blob |
|---|---|
| B3b vendor/kinetic.py | 1fef508f01479508e5489cf8a167d2aff8184a81 |
| B3b vendor/core.py | 3e95a652715b346a47f097fde2131540237390a4 |
| REC nonlinear_bose_runtime.py | 67c39313fdaf29100296ba1381293f2478107e09 |
| REC nonlinear_bose_release.py | df06f46252b44ad6d169cb95e7c0f8b551ae4a25 |
| REC source_derived_parent.py | e04e590d43f4c2d7dfa184106fc4492e5bdb63de |
| REC PR43 physical_split_reference.py | 57532b974c29ad51c6ec1ed79e3dbc7f9280f77a |
| REC dynamic_macro_ownership.py | a196840d164aa7497b27178c1a38ca0f9627c426 |

The three NPZ input identities were already checked against their source locks during intake. This review did not recompute their moments or replay their generators.

## Checked mathematical content

### 1. Number current, stress tensor and units — PASS

With n_ij = G_i A_j f_ij and ell_j=(1,n_j), the equations

N^a = c sum(n_ij ell_j^a)

T^ab = sum(c p_i n_ij ell_j^a ell_j^b)

have the correct conventions for physical four-momentum p^a=(E/c,p). N^0/c is number density and c*T^0i is energy flux. G has units m^-3, f and A are dimensionless, and c*p_i is in joules.

Using kappa_grav=8*pi*G_Newton/c^4 gives alphaL=kappa_grav*L^2 with units m^3/J. Hence w=alphaL*c*Pstar*n_ij and k=(p_i/Pstar)*n_j are dimensionless. The lack of an extra c in T and the factor c in N are consistent.

The actual REC number routine uses sum(G_i*f_ij*A_j). HarmonicGrid.from_directions explicitly divides raw angular weights by their sum. The contract correctly confines that source-compatible normalization to the input loader and requires a normalized grid in the general bridge.

No extra 4*pi, polarization factor, cell bandwidth, or radiation reference field should be added.

### 2. Agreement with unchanged BASS kinetic owner — PASS

The actual kinetic owner computes:

- rho = sum(w*e);
- flux = sum(w*k);
- pressure_ab = sum((w/e)*k_a*k_b);
- tensor_ab = sum((w/e)*p4_a*p4_b).

For mass=0, e=p_i/Pstar. Substituting the proposed k and w therefore gives alphaL times the physical T component by component. Mean pressure is rho/3 and the state pi is the spatial trace-free part. The source's small algebraic STF assignment is not a positivity operation or a physical change to the moments.

This verifies the proposed normalization from actual source algebra, rather than from naming conventions alone.

### 3. Locked photon energy — PASS

The proposed use E_i=c*network.momentum_scale[i] is correct for the actual discrete owner.

PR43 explicitly separates this energy from reconstructed geometric centroids, arithmetic-centre target energies and competing Doppler conventions. The theory preserves the earlier centroid suggestion and its correction, rather than describing all attempts as initially valid. This is required provenance.

The proposed wrong-energy witness is meaningful: photon number and trace zero can survive a wrong p_i, while the energy moment changes. It checks an independent source-authority risk.

### 4. Inverse, labels, vacuum and numerical domain — PASS, with implementation obligations

The inverse f_ij=w_ij/(alphaL*c*Pstar*G_i*A_j) is a left and right inverse on the fixed labeled representation when its stored k/mass/grid/frame/epoch/scale binding is verified.

It is not an inverse of arbitrary BASS packet aggregation or a conservative remap. The contract correctly requires rejecting off-grid packets and ambiguous labels.

The existing kinetic packet validator rejects an empty array but accepts nonempty massless packets with zero weights and nonzero momenta. Therefore the implementation must either retain canonical zero-weight entries for vacuum or explicitly handle an empty representation outside the existing tensor/moment call. It must not quietly pass an empty list to the unchanged kinetic owner. This is a concrete implementation obligation, not a defect in the equations.

Positive-underflow and nonfinite-arithmetic rejection are appropriate. Algebraic invertibility does not promise binary64 representability for arbitrary positive inputs. The review does not certify the prospective tolerance values numerically.

### 5. State boost covariance and event distinction — PASS

Existing kinetic.boost uses an active plus-sign Lorentz matrix and w_new=w*E_new/E.

Writing D=E'/E and ell'=Lambda*ell/D, the new-frame density n'_ij=D*n_ij gives N'=Lambda*N and T'=Lambda*T*Lambda^T. The transformed number density is a weight on the transformed observer's state measure. It is not a replacement occupation f on the untransformed original grid.

The theory correctly requires returning through an explicit inverse boost and checking the original grid, or carrying a complete transformed representation, before using the inverse formula.

The invariant spacetime event measure dR from B3a does not acquire this state-density multiplier. The theory explicitly distinguishes Q and observer-clock K from the state N/T transformation. No contradiction with the B3a event counterexample or G1B reduction was found.

### 6. Snapshot frame and clock — PASS

A local state inventory conversion needs no emission clock. Its quantities are densities/moments at a fixed local snapshot, not time rates. The contract prohibits constructing U/J/PiRate from the state.

The source angular directions are hydrogen-frame directions. The current REC characteristic rate R_H is formed with the same D0 derivative as its normal-frame counterpart, so using a new proper-H clock multiplier without a separate derivation would be unjustified. The snapshot bridge avoids that operation.

### 7. Scientific boundary — PASS with provenance wording correction below

The theory correctly keeps absent LINE01 trace binding, atomic-source replacement, finite emission/absorption ownership and coupled dynamics outside the adopted unit.

The actual stored occupation has a stronger, specific meaning that should be carried directly into the frozen documents: source-owned scalar point-characteristic sampling, Planck-plus-distortion restoration, an explicit hydrogen-frame isotropic lift, and an accepted bootstrap initial-data role. It is not a completed coupled endpoint or reconstructed anisotropic native history. The general bridge equations can still be tested on separately labeled anisotropic diagnostics.

## P2 findings: required before publication

### R6-P2-01 — Make the boosted scalar density notation unambiguous

Location: FROZEN_CONTRACT.md, boost paragraph.

Current text has “n'=D n” immediately after defining directions n_j elsewhere. This is correct only when n denotes the packet number density. Multiplying a direction by D would violate the unit-direction condition.

Required correction: write “n_ij'=D_j*n_ij” explicitly, retain “ell_j'=Lambda*ell_j/D_j”, and call n_ij a scalar number-density contribution. No equation or implementation behavior changes.

### R6-P2-02 — Carry actual bootstrap provenance into the theory and contract

Location: FROZEN_CONTRACT.md source scope and SNAPSHOT_BRIDGE_THEORY.md actual-input section.

The intake report contains the exact saved-state qualification, but the two frozen theory/implementation documents do not yet directly name it. “Source-conditioned saved occupation” alone does not distinguish a bootstrap initial datum from a completed physical trajectory or a native anisotropic field.

Required correction: add a concise source-bound statement:

- scalar native-history point-characteristic samples at COM centres;
- total occupation restored as Planck plus distortion;
- explicit scalar/unpolarized hydrogen-frame isotropic initial-data axiom;
- source builder restricted to the validated Bianchi-II branch;
- coupled_macro_endpoint=False;
- anisotropic tests are diagnostics of the general adapter, not relabeling of the actual isotropic input.

This does not disqualify the snapshot bridge. It defines the exact source state it preserves.

### R6-P2-03 — Align Source.pi wording with the no-Source-construction scope

Location: SNAPSHOT_BRIDGE_THEORY.md section 3.

The phrase “Source.pi receives the state stress” and the optional zero-transfer container wording can be read as authorizing a Source construction, whereas the frozen contract explicitly excludes one.

Required correction: say that the returned pi_hat has the same state-stress meaning as Source.pi if consumed in a separate future container, and that this unit itself constructs no Source or transfer fields. The mathematical pi formula remains unchanged.

## Unselected sections

The conditional closed-cell model and B3c transport/source composition are explicitly marked outside the frozen implementation. Their presence does not authorize a new finite absorption update or IVP.

This review checked that their claim boundaries remain conditional; it does not promote them to implemented or numerically validated results. Any selection of those sections requires its own actual source binding and frozen research unit.

## Review work and non-actions

Read-only text/source inspection, independent substitution and dimensional/Lorentz reasoning were performed. Metadata hashes were computed to bind this review. No tests, scientific Python program, symbolic kernel, source operator, IVP or old campaign was run.

No code, source input, contract, theory equation, historical receipt, tolerance or repository policy was edited by this reviewer. Only this review file was written. Historical remaining budgets remain null and budget_reset=false.

The controller can close the three P2 items by a single documentation repair and a focused readback of those changes. No old numerical work is required for that repair.

## Focused documentation repair readback — closed

The controller applied one documentation repair. This reviewer reread only the requested notation, source qualification and Source-scope changes, together with the affected surrounding paragraphs. No scientific execution or broad reaudit was performed.

| Finding | Observed correction | Final status |
|---|---|---|
| R6-P2-01 | Contract now writes number-density n_ij'=D*n_ij and w_ij'=D*w_ij, separately states ell_j'=Lambda*ell_j/D, and explicitly distinguishes the spatial direction rule | CLOSED |
| R6-P2-02 | Both frozen documents now state scalar-history Planck-plus-distortion sampling, isotropic unpolarized hydrogen-frame bootstrap INITIAL-DATA, validated Bianchi-II builder, coupled_macro_endpoint=false, and separately labeled synthetic anisotropic diagnostics | CLOSED |
| R6-P2-03 | Theory now identifies the returned state pi convention while explicitly saying the adapter constructs no Source, writes no source fields and infers no U/J/PiRate | CLOSED |

Repaired review-target SHA256 values:

- FROZEN_CONTRACT.md: df63c3328c2ab4ab8c7f5ac5e5c122b354c892a3845dd09f69645500027cc653
- theory/SNAPSHOT_BRIDGE_THEORY.md: 396e6e802955a4eb6256e2b43dd7e4fc58a5929d9fc103a394b0107a92069ad3

**Final R6 disposition: PASS_SCOPED, P0=0, P1=0, P2 open=0.** The temporary documentation HOLD is lifted for these repaired targets. The bridge equations and selected snapshot scope are admitted for implementation; numerical implementation/figure verification and final science/publication admission remain subsequent controller gates. The first-pass findings are not relabeled as initially absent.

