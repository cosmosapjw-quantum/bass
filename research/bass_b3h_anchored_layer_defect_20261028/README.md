# B3h: anchored coefficients for the identical frozen-layer reconstruction

UNIT=BASS_B3H_ANCHORED_LAYER_DEFECT_20261028
BASE_F=e5898d8d6edabd9c5f8e175b4f87a6a4647eae59
Original canonical record28/88,delta0,AUTO_NEXT_NODE=false.

## Actual scoped result
For the same saved Q=q+exp(-B tau)z, the whole-cell conditional count-defect upper bound changes from1.59277677725084443426081125691396049610412837e-26 to6.72651202785221736785708947519876926590743302e-31 m^-3. The suffix changes from6.72516458498261097324369779584487008018522517e-31 to6.71452244464414866758605729264087058671006694e-31 m^-3. Displays are rounded upwards; exact rational PRIMARY in the source archive is authoritative. Previous/new ratios are approximately23679.0891126886 and1.00158494374339. These are same-reconstruction bound improvements, not observed trajectory-error reduction, physical accuracy or speedup. Original Nout and reset certificates remain separate.

## Derivation and implementation binding
Use proper time[s], dimensionless population, M[s^-1],n0=N_H/V0[m^-3]. The unchanged source law is M=A0+theta(A1-A0)+R(u)E22. At each fixed native anchor, use the parent's true-clock theta interval and an interval for R at that same u. Convexity of the induced one-norm proves alpha_local=max_corner||A0+theta(A1-A0)+R E22-B||1+epsilon_M over the full containing rectangle. It is not an empirical four-point fit. Take min(alpha_old,alpha_local) only after common-source binding.

Only R(u=0) is newly enclosed at256/384bits using the unchanged outward-dyadic engine. The original512bit cut-rate interval is reused, not evaluated again by the primary and not obtained through another QSS solve. JSONfloat constants mean exact binary64; strings exact decimals. Native A1-A0 versus QSS stored delta_M serialization difference is measured and bounded; the native matrix difference is retained, and only the matrix-independent R_cut is reused.

For Q=q+y,y=exp(-B tau)z, f_Q=f_q+(M-B)y. Inherited ||M'||1<=L and beta=min columnsum(B)>0 give ||M-B||1<=alpha+L tau and ||y||1<=Z exp(-beta tau). Thus retain F_layer<=Z min(C Phi,alpha Phi+L Psi), Phi=min(Dhi,1/beta),Psi=min(Dhi^2/2,1/beta^2). The terms have the correct time/rate units. No commutation is assumed. For B=diag(2,3),C=[[0,0],[-1,1]],M=B+tau C,z=(1,0),alpha=0 but the residual is(0,-tau exp(-2tau)); discarding L is wrong.

Two anchor alphas decrease from about3.1167e-4 s^-1 to6.478083e-51 s^-1, dominated by the inherited coefficient margin. The final bound is then mostly limited by the existing slow residual, not this anchor arithmetic. Exactly preserve B,z,slow residual,L,clock,duration,gamma=min(saved,literal),K=n0Rhi/gamma,initial mismatch,interior jumps and finite endpoint tails. Replace only the layer ledger port: new_total=old_total-old_layer+K*sum(new_layer_mass). Joint L1 mass is not duplicated. The inherited analytic/MP/clock bounds remain conditional; exact consumer arithmetic does not supply physical/source uncertainty.

## Executed validation
Twenty identical unit methods: RED18failed methods/34assertion events/2passes, then GREEN20/20. Single primary28/28. A production-import-free Decimal180 and signed-column dual-norm oracle passes85/85, including60scalar closed-form fixtures. Fixed assembled comparison tolerance1e-90; observed max relative difference1.48931e-180. Separate Decimal rate values lie inside the new first-rate and saved cut-rate intervals. CAS5scalar zero residuals+2zero-duration values, nonzero commutator and nonzero residual retained. No observed evaluator warnings. CAS discovery parsing is not treated as validation.

Run only the new core tests from this subtree: `python -I -S tests/test_anchor.py`. The completed saved-input drivers are in the full source ZIP and should not be automatically replayed. Existing scientific campaigns, nativeODE,QSS,B3i and quadrature executions0. No full-repository CI claim.

Two saved-result figures were generated and directly read. First ratio annotation overlapped the upper spine despite a passing canvas check; original code/images/receipt retained. One ratio-only y-extent repair removed it without changing values or rerunning science; first count figure was not regenerated. Physical print test and independent visual review NOT_RUN.

## Progress, provenance and delivery
Work18/20; distinct-author R6/C9 NOT_RUN. Same-author alternative arithmetic/CAS are not independent admission. Parent222/221/220/217/215/212 holds remain separate. Native delegation is not exposed; serial parent execution is recorded. Full source ZIP contains all drivers,exact inputs/results,logs,proof,report,ledger and figures. Git contains runnable core/tests and this concise projection; these are different complete file sets. Later actual ACKs are separate and do not cause archive regeneration.

S0 commit8bab63b2979494055196fd2a1d7f819a8d80e16c; source capsule56955bytes,SHA2566cf8d78c02c5ef01973959b666ce463689ca21ac77ab4217aeb32ab920741083. Actual Drive1dgfyA2E64hKwUv7GeLGNvjm-1mwu6O0j and Dropboxid:BSpOijBcT10AAAAAAEDLqw/rev65ee1501f679a0af03d47 completed with separate56955byte metadata.

Fresh test/science childrenCPU0.192436s/wall0.262731361s;wrapperCPU0.006463888s. Including first/repaired plots,knownCPU4.516803761s/wall4.712024447s. Preparation,restore,network,model,preservation and remoteCAS CPU remain unknown. Freshallocationclosed;oldremainingnull,no reset/transfer.

Current intake supplements historical1426-name inventory with7repo changedPR query,relevant current refs/AGENTS/backup metadata,limited conversation search and terminal BASS15/REC5 dated-name queries. Not all branch bodies/transcripts/archivebytes were read. Central7937ed4a...HEQUARTIC12 and other owner results are not overwritten or imported as physical radii. No central/main/foreignwrite,merge or auto-next. Physicalradii/globalcompletion/E_QSS_old=null,L4false.

Literature background: Baake/Schlaegel arXiv1011.1775 and Cao/Petzold DOI10.1137/S1064827503420969. The anchor specialization is derived here; neither citation validates BASS inputs. Next obligation: one distinct-author R6/C9 saved-evidence review of this fixed source, not repeated same-author audit or automatic new node.
