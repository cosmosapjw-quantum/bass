# C9 source-availability precheck

Reviewer: /root/b3g_rec_recovery. Role: read-only independent scientific/code reviewer.
No implementation authored; no scientific execution, native solve or old campaign replay.
This is a source/contract precheck, not final implementation admission.

## Inputs actually read

- FROZEN_CONTRACT.md and theory/TRANSPORT_AND_GEOMETRY.md in this lane.
- Restored B3c code/bounded_background.py, ADMISSION.json, raw/VALIDATION.json,
  and both raw/{ISO,ANISO}_N256_{PATH,SOURCE_HISTORY}.json.
- Unchanged B3f source file locations in sibling bass_b3f_cohort_input_error_20261025/code.
- Earlier direct REC source recovery, actual owner input contracts and current central AGENTS.
- Checkout HEAD observed d6af237b66e78ca6ed4572068f6bc1a805bbb2d9; this lane is additive/untracked.
  No governing BASS root/research AGENTS found; nested historical copies remain evidence.

## Structural observations

1. ISO source receipts256 and path endpoints257; ANISO source receipts256 and
   path endpoints257. The contract's512birth/514endpoint counts are supported.
2. Every selected source receipt has positive proper source duration and
   ledger.up_m3=0. Every selected already_applied_U entry is0.
3. Source code implements half transport -> source_kick -> half transport.
   source_arguments uses dt_s=(L/c)dtau. The source kick records
   global_time_advanced_by_source=0; the recorded transferred number is already
   integrated over the source subflow. Multiplying it by duration again would
   be a consumer error.
4. Source receipts supply midpoint_N_m3, midpoint_H_s_inv and midpoint_S,
   but no beta-bearing key. Full PATH endpoints contain alpha,beta1,beta2.
   H and S specify the instantaneous beta derivative, not midpoint beta.
   The exact missing midpoint beta/interpolation-bound obligation is correct.
5. Saved state data explicitly supply rho_R,rho_X,rho_gamma and pi_gamma,
   enabling the stated sector bridge without another IVP. Scalar flux_relative
   is a diagnostic, not a stored flux vector. Using exact antipodal zero flux
   is a declared symmetry closure and should retain its label.
6. The source is the manufactured cold/non-tilted/recoil-free detached
   f_plus=0 finite14 B3c model, with H_LYA_EFFECTIVE_2P card. Actual saved
   model outputs are not an admitted calibrated REC or isotope-resolved source.
7. The owner records model uncertainty NOT_PROVIDED_ON_TABLE. Small arithmetic
   residuals, exact polynomial angular moments at R=I and finite14 birth
   exactness do not close eS,en,eE. R(t_b,t_b)=I supplies only the birth
   identity eR=0. B3f missing-radius status must remain conditional.
8. Stored atom stocks are much larger than an individual emitted count.
   Atom-stock cancellation checks require their declared stock scale; the
   photon packet/moment checks require E_b*n_b, never rest-energy scale.
9. Historical B3c admission is PASS_SCOPED for its manufactured finite14
   tau[0,.1] model. Its temporal/numerical evidence and costs remain separate
   from new consumer representation checks and from physical input uncertainty.

## Wording finding C9-S1

Target: theory/TRANSPORT_AND_GEOMETRY.md section2:
"N_b=N0 exp(-3 alpha_b) recovers alpha_b exactly within the stored representation."

Evidence: the producer evaluates a binary64 exp and multiplies by N0 before
storing N_b. Inverting the rounded N_b with a binary64 logarithm reconstructs a
nominal alpha; it need not recover the producer's original alpha bits exactly.

Impact: no birth moment formula or missing-beta conclusion changes; the phrase
can overstate the reconstruction's identity/error status.

Minimum correction: state that -log(N_b/N0)/3 reconstructs the nominal alpha_b,
with arithmetic reconstruction error separate from physical input uncertainty.
No source rewrite or numerical replay is needed.

## Precheck disposition

Source availability supports the frozen bounded consumer plan. C9-S1 is a
wording correction. Implementation review, actual raw outputs, metered cost
and actual plot review remain PENDING; no final scientific admission here.

