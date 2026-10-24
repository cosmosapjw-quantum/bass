# Independent physics and figure review

## Decision

**PASS_SCOPED.** The frozen implementation satisfies the mathematical and physical contract for (i) the integrated gross ledger of the frozen, thick LINE01 model with a prescribed incoming occupation and (ii) its canonical matter-rest, \(f=0\), finite atomic-excitation-to-photon state transaction. No blocking physics or figure defect was found in this pass. This is one independent agent review of the actual source, contract, implementation, tests, recorded outputs and rendered figure. It is not an independent-model validation.

Reviewed unit: BASS_B3B_FINITE_LINE_EXCHANGE_20261024. Reviewer: /root/b3b_theory_review. The separate code auditor's result is not inferred by this decision. Remote backup, publication, merge and production status are outside this review.

## Mathematical construction and its numerical realization

The prior independent derivation in [THEORY_REVIEW.md](THEORY_REVIEW.md) and the actual current [Wolfram response](../evidence/WOLFRAM_CURRENT_RESPONSE.json) are reused. No formula suite, historical campaign or IVP was rerun for this review. The Wolfram evidence comprises 19 zero residual groups; its already-recorded kernel wall and CPU measurements are not new reviewer runtime.

Let \(b=g+1\), \(F=1+bf\), \(x_e=gf/F\), \(d_e=g/F\), and \(k=8\pi H/(N\lambda^3)\). The unchanged owner flow obeys
\[
\dot x=-\frac{kF(x-x_e)}{g-bx},\qquad
\omega=\frac{kF^2}{g}\Delta t=v+z_0(1-e^{-v}),
\quad z_0=-\frac{b(x_0-x_e)}{d_e}.
\]
With \(a=1-e^{-v}\) and \(r=v-a\), the implemented positive decomposition is
\[
D_\downarrow=\frac{N(1+f)}{F}\,[x_0a+x_er],\qquad
D_\uparrow=\frac{Ngf}{F}\,[(1-x_0)a+(1-x_e)r].
\]
All factors are nonnegative on the admitted, non-inverted domain. The stable net remains the owner's \(-N\Delta x\), rather than rounded subtraction of two gross counts.

The exact-LTE branch correctly replaces the owner's net-only \(u=0\) shortcut by \(v=\omega\). This gives equal, nonzero gross channels \(Nkf(1+f)\Delta t\) for \(f,\Delta t>0\), while the net is zero. At \(x_0=0,f>0\), the down channel comes from \(x_er\), retaining its quadratic onset. The small-\(v\) alternating series for \(r\) avoids cancellation; its next-term bound is explicitly a mathematical truncation bound, not an interval enclosure of floating arithmetic. Underflow and unresolved state increments cause explicit errors, with no positivity clipping or renormalization.

The recorded independent original-rate quadrature covers emission, absorption start, absorption, near-LTE and exact LTE. Its largest listed individual-channel relative discrepancy is below \(6\times10^{-16}\). The tiny absorption-start case at \(\omega=10^{-12}\) retains \(D_\downarrow=4.2950853810910675\times10^{-17}\ {\rm m}^{-3}\); it is not rounded to zero. Decimal checks through \(v=10^{-100}\) support the small-\(v\) evaluation. Full-step versus two-half-step composition checks both the population map and the integrated gross/net counts, with the largest reported normalized count discrepancy \(1.7351413293804478\times10^{-16}\). These are bounded validations of the frozen model, not time-dependent source evolution. See [VALIDATION.json](../results/VALIDATION.json) and [test_finite_exchange.py](../tests/test_finite_exchange.py).

## Actual finite stock and BASS receiver

The committed branch has \(f=0\): \(D_\uparrow=0\) and \(0\le D_\downarrow=D_{\rm net}\le n_{u,0}\). It debits the actual finite upper population, credits the lower population, and transfers exactly the represented excitation increment \(E D_{\rm net}\) from the atomic sector to the photon sector. The required excitation energy already belongs to the caller's atomic sector; no extra donor reservoir, thermal yield, recoil or ionization yield is introduced. Additional caller-owned atomic energy and pressure/stress remain part of that sector.

The 14-node construction uses six axes with weights \(1/15\) and eight cube corners with weights \(3/40\). Its exact rational moments through degree five give
\[
\sum_j\Delta n_j=D_{\rm net},\quad
\sum_j\Delta n_jn_j=0,\quad
\sum_j\Delta n_jn_jn_j^{\mathsf T}
=D_{\rm net}\left(\frac I3+\frac{2S}{15}\right),
\]
for \(\Delta n_j=D_{\rm net}A_j(1+n_j^{\mathsf T}Sn_j)>0\). The rational oracle checks 56 monomials and remains exact. The rotated STF check and the actual BASS kinetic moment calls support the analytic tensor relation.

With \(\alpha_L=\kappa_{\rm grav}L^2\), packet momenta \(k_j=E n_j/(cP_\star)\) and finite state weights \(\Delta w_j=\alpha_LcP_\star\Delta n_j\) give
\[
\Delta\rho_\gamma=\alpha_LE D_{\rm net},\quad
\Delta p_\gamma=\Delta\rho_\gamma/3,\quad
\Delta\pi_\gamma=2\Delta\rho_\gamma S/15.
\]
This is a finite state increment. The interval-average rate instead contains \(\kappa_{\rm grav}L^3/c\); integration over \(\Delta\tau=c\Delta t/L\) recovers the same increment. Recorded scale checks give factors four and eight respectively and zero recorded relative integration discrepancy. Source.pi receives state stress, never PiRate_hat.

The tests actually use core.State, core.Source and the existing kinetic moment function for both an exact vacuum and an occupied photon stock. In the displayed transaction fixture, upper population decreases from \(3.0\times10^8\) to \(1.1666903809207943\times10^8\ {\rm m}^{-3}\), and the photon increment is \(1.8333096190792057\times10^8\ {\rm m}^{-3}\). No epsilon photon seed is used. Packet rho/flux/pressure/STF discrepancies are below \(1.4\times10^{-16}\) on the reported emitted-energy scale.

The geometry is frozen. Total density and flux are preserved to the reported floating bounds, so the actual constraint residuals are preserved. **The initial residuals are nonzero:** preservation is not a claim that the fixtures solve the Einstein constraints. Population residuals use the total population scale \(N\); energy residuals use the recorded state/gross energy scale. These certificates do not assert uniformly small relative error for every nearly unrepresentable transfer.

The implementation rejects a nonzero advance that leaves a population or sector energy unchanged in floating arithmetic. It also rejects prescribed-boundary \(f>0\) stock commits, insufficient excitation energy, inconsistent photon moments, mismatched physical bindings or geometry, and repeated physical transfer keys. The addendum's zero incoming U/J condition prevents an already-applied finite transaction from erasing or double-integrating unrelated rate sources. Return values are copies, and refusal tests verify unchanged inputs. See [CONTRACT_ADDENDUM.md](../CONTRACT_ADDENDUM.md), [finite_exchange.py](../code/finite_exchange.py), and [test_finite_exchange.py](../tests/test_finite_exchange.py).

## Failure history and targeted repair

The execution record is not a first-pass success. The first command ran 16 tests with 15 passing and one failing: the floating rotated-cubature normalization residual was \(3.3306690738754696\times10^{-16}\), just above the initial absolute tolerance \(3\times10^{-16}\). The correction to \(32\epsilon=7.105427357601002\times10^{-15}\) is reasonable for the finite sequence of floating dot products, square roots and summation. It changes only that floating identity test; the exact rational oracle and \(256\epsilon\) physical transaction gates are unchanged.

The preserved failure, second successful command and final successful command are present in [REPAIR_HISTORY.json](../results/REPAIR_HISTORY.json) and [EXECUTION_LEDGER.json](../results/EXECUTION_LEDGER.json). The final record contains 16/16 passing tests and 49 figure rows. The cache-directory adjustment and figure title clarification are also retained. No failed result was relabeled PASS.

## Actual figure inspection

The reviewer opened and visually inspected [FINITE_LINE_EXCHANGE.png](../results/FINITE_LINE_EXCHANGE.png), and compared its presentation with [FIGURE_DATA.csv](../results/FIGURE_DATA.csv).

- The title explicitly identifies synthetic frozen parameters and the actual source and BASS receiver.
- The left panel labels the incoming occupation as a prescribed boundary, \(f=0.1\). Positive gross down/up curves, the stable net, equal LTE gross channels and the zero LTE net are distinct and legible. Their continued gross growth alongside a saturating net correctly illustrates repeated external-boundary exchange.
- The right panel explicitly states \(f=0\) and initial vacuum. The depleted upper population and created photons sum to the initial donor fraction \(0.3\), with the reference line shown. The final plotted values \(0.010148375485310078\) and \(0.28985162451468993\) match the CSV.
- Both horizontal axes identify dimensionless frozen source time \(\omega=\eta\Delta t\); the vertical axes state normalization by \(N\). The panels use their respective source parameters. They are local-step evaluations at different durations, not a claimed cosmological IVP trajectory.
- Labels, legends and curves are readable without clipping. The figure makes no claim of a solved constraint manifold or a closed finite absorbing photon bath.

No figure repair is required by this pass.

## Explicit acceptance boundary

This decision admits the frozen thick-model ledger and the canonical-rest, \(f=0\), fixed-geometry finite source substep. It does not admit finite-stock absorption at \(f>0\), a new gross-channel finite-opacity relative certificate, an evolved REC/HE cosmological source history, higher angular/spectral closure, or a coupled production IVP. Existing owner finite-opacity envelopes retain their FLOAT_NOT_INTERVAL qualification.

The finite packet representation is exact for the stated rest-frame moments. It does not replace the changed-observer event-rate functional with its rational energy denominator. A later snapshot boost of a completed state is a distinct operation from changing the clock or hypersurface of the finite source transaction. The present implementation correctly limits the commit to the canonical frame and clock.

B1/B2 historical acceptance gaps, prior partial elapsed subtotals and campaign budget metadata are unchanged. This review grants no merge or production activation.

## Review method and runtime accounting

This pass read the frozen contract/addendum, source implementation, complete test file, validation/repair/runtime records, figure CSV and actual PNG. It reused the earlier independent analytic derivation and current recorded Wolfram results. No concrete unresolved physics risk required another scientific process.

New reviewer scientific probes: **0**; scientific argv: none; scientific wall/CPU: **0/0**; new IVP: **0**; old campaign replay: **0**. File reads and visual inspection are review/orchestration work, not scientific execution; their total wall time is unmeasured. No external actions were performed by this reviewer. The previously recorded implementation science remains 4.957068316012737 wall seconds and 4.924338 CPU seconds; those measurements are not duplicated in reviewer totals.

Exact reviewed artifact hashes are in [PHYSICS_AND_FIGURE_REVIEW.json](PHYSICS_AND_FIGURE_REVIEW.json).
