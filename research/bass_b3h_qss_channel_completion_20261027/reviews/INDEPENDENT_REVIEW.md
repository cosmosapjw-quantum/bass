# Independent R6 / C9 review: QSS channel completion

## Decision and review boundary

**Phase A: PASS_SCOPED.** The frozen source transcription, four new diffusion-temperature inversions, effective bound-free energy moments, source-operand reconstruction, right-snapshot holdout and actual bounded execution support their stated finite numerical claims. No Phase A implementation repair or rerun is requested. The root retains scientific-admission authority.

**R6 theory: accepted for the selected effective radiative model, with the finite-propagator restart correction below incorporated in the root Phase B contract.** The root accepted that correction during this same review pass. Phase B's actual contract, channel maps, finite integration and B3i representation are new dependencies; their future review does not reopen the accepted Phase A calculation.

Reviewer: `/root/native_atomic_intake`. The reviewer prepared source intake and exact stored-data extraction, but did not author the reviewed Phase A implementation or the primary energy/dynamic theory. This is one integrated independent pass, including static review and subsequent inspection of the one actual run. Reviewer scientific executions: **0**. Native-history executions, old tests/consume/plot replays, remote writes and B3i calls by reviewer: **0**. Read-only JSON selection and byte-identity checks are not scientific reruns.

Original DAG remains **27/88**, delta **0** at this Phase A review. The old 512 cohorts, two B3i consumptions and previous completed inverse remain reusable evidence. Historical remaining CPU/wall budgets stay null. Physical eS/en/eE/geometry/total radii remain null; this review creates no physical uncertainty radius.

## Current-source observation and actual run identity

The reviewer read the actual canonical reference and AGENTS before this review at 2026-10-27 12:52:19 UTC. Canonical central HEAD was `152b82cac23fedcb75a9effe0c159bae3d800c01`; central AGENTS blob was `429a5a13ee75b1222bc50627f8d5973d01dd21c4`. The previous BASS inverse branch was `6bf4a5d90b05f7e583be698854e521d259287837`. Parallel-agent state was observed rather than inferred. This review applies the current personal-research trust model, typed-identity rule, tiered delegation and finite execution-transition policy; it introduces no additional assurance layer.

The root subsequently published S0 `b581ad6f9ab92ee2efac816e2f2d2a63994c77c6`, tree `1e47b5b484d458e8f27ab1a74236e10f901c61d8`, expected parent equal to the previous inverse final, non-force, with actual ref readback MATCH. Recorded source ZIP: 313,696 bytes, SHA256 `72597bbc94d92ad64b39327c6567399e4759f687527e3e4004569b8d14020c51`. Parent-recorded actual Drive upload plus metadata ACK identifies `17xgJbn1Z5kAZPZxpUOMxZyNHLwZ4Jg8r`, 313,696 bytes. Actual Dropbox upload/poll ACK identifies `id:BSpOijBcT10AAAAAAEDHmQ`, 313,696 bytes. The reviewed receipt does not yet claim a separate Dropbox metadata read. The reviewer inspected these recorded observations; the reviewer did not independently perform their uploads.

The actual Phase A pre-node record at 12:55:47 UTC retains central HEAD/AGENTS and records the S0 BASS HEAD and active root/reviewer/implementer identities. `inputs/EXECUTION_FREEZE_PHASE_A.json` SHA256 is `40ffe4241c7c4c1d4e89b6eae0523bae3ada8c6c995939b0c1f2bc9694d10a88`; all 32 frozen members match their recorded bytes. The wrapper's final change selected this Phase A freeze filename while preserving the historical preparation freeze. Its executed SHA256 is `88999c0507849a5d2f79a39cc6bd206e51dfd01e897203da9a30029c60ab483d`.

Reviewed immutable inputs include the original `hydrogen.c` SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`, the original Alpha/R/two-photon tables and history source, exact stored knot packet, earlier H-only witness, local steady-temperature branch witness, reused finite photon result and completed inverse. The right snapshot is explicitly validation-only. The local guard witness is not promoted to a claim about every earlier native history step.

## R6: theory and ownership

### Effective Maxwellian energy moments

The selected effective rates have the form

\[
\alpha_i(T_m,T_r)=C T_m^{-3/2}\int W_i(\epsilon;T_r)e^{-\epsilon/T_m}\,d\epsilon.
\]

At fixed radiation temperature, radiative interior branching probabilities are independent of matter temperature. Differentiating this integral gives

\[
K_{\mathrm{rec},i}=\tfrac32T_m+T_m^2\partial_{T_m}\log\alpha_i(T_m,T_r).
\]

The differential Milne relation and detailed-balance reciprocity of the eliminated interior inverse give the reverse effective kernel. Its mean is

\[
K_{\mathrm{ion},i}=\tfrac32T_r+T_r^2\left.\partial_{T_m}\log\alpha_i(T_m,T_r)\right|_{T_m=T_r}.
\]

The derivative is a partial derivative at fixed second argument. Differentiating the equilibrium diagonal in both arguments would be a different, incorrect moment. The implementation and its independent polynomial derivative use the correct partial derivative. This conclusion is scoped to the selected radiative effective model: introducing collision-dependent branching would change the premise. It does not require unselected continuum-return loops to be supplied in advance.

With \(\chi_i=E_I-E_{21}\), each successful recombination assigns atomic energy \(-\chi_i\), radiation energy \(\chi_i+K_{\rm rec,i}\), and gas relative-motion kinetic energy \(-K_{\rm rec,i}\). Reverse events use their own \(K_{\rm ion,i}\). These sum to zero event by event. The effective cascade telescopes in total energy, while a complete spectrum would require additional conductance information. This construction is a new effective finite energy account; the original history code did not evolve an explicit recombination-heating ledger. It is not an electron-only heat claim.

Primary texts were independently retrieved through Exa after the built-in web opens failed. Relevant checks were the primitive Maxwell integral and detailed-balance relations in Ali-Haimoud and Hirata, [Ultrafast effective multi-level atom method for primordial hydrogen recombination](https://arxiv.org/html/1006.1355), and the differential Milne relation, matrix orientation and inverse reciprocity in Ali-Haimoud, [Effective conductance method for the primordial recombination spectrum](https://ar5iv.labs.arxiv.org/html/1211.4031). These support the rate/kernel premises; the finite energy construction is the present derivation. The first paper's title should receive a nonblocking bibliographic correction in the theory note; its linked paper and PRD identity are already the intended ones.

### Absolute diffusion and channel-energy signs

Writing absolute state \(X=x+q\), the native departure diffusion gives \(-T_{\rm diff}(X-q)\). The additional drive required for literal absolute diffusion is therefore

\[
d=-T_{\rm diff}q,
\qquad c_{\rm diff}=d_r-T_{rv}T_{vv}^{-1}d_v.
\]

Both signs in the theory are correct. `T_diff` must contain the diffusion edges alone, including the two real/virtual core edges. It is not the entire optically eliminated virtual diagonal \(\Gamma/P\). The saved Phase A full affine Wien shifts convert variables and are not themselves this physical diffusion correction. Phase A retains the raw diffusion coefficients and pre-diffusion radiative coefficients needed to construct it without ambiguity.

For a core-to-wing event, atomic internal energy changes by \(-E_{21}\), tracked photon energy by \(+E_b\), and gas kinetic energy by \(E_{21}-E_b\). For a virtual edge \(b\to c\), the gas receives \(E_b-E_c\), opposite to the photon energy change. The corresponding detailed-balance/Wien signs in the theory are consistent with the actual source coefficients and the \(T_m<T_r\) thermal direction.

For a non-diffusive two-photon/Raman event, the companion energy \(E_{21}-E_b\) belongs to radiation. It must not also be booked as gas heat. Folded Ly-beta/gamma similarly place \(-E_{32}\) or \(-E_{42}\) in the companion radiation bath. Direct source Ly-alpha recoil is zero in the selected model; that fact does not set off-line diffusion heating to zero. Build the radiative channel maps from the saved pre-diffusion coefficients, then add each diffusion edge once. Adding diffusion to already augmented real/virtual coefficients would double count it.

### Finite clock and inventory

The finite atomic inventory uses \(N_g=N_H-N_c-N_s-N_p\). Its exact ground count is distinct from the original effective opacity \(g=1-x_{\rm HII}\); this separation is explicit and sound. The chosen prepared-density bound-free coefficients define a finite step whose actual continuum/electron inventories must be checked for positivity. They do not imply an infinite reservoir or a nonlinear rate-feedback solution.

Preparing and interpolating actual gross channel maps before summing their stoichiometry preserves the affine reduced equation. An independently interpolated matrix plus unrelated channel rates would not suffice. The native Ly-alpha identity with \(R_\alpha={\rm LYA\_FACT}H/(n_Hg)\), the \(e^{3u}\) crossing measure and \(e^{4u}\) transported energy weight is correct. The completed photon result can be reused as a baseline, with only the newly derived dynamic outgoing correction integrated. Event energy and cosmological transport/geometry work remain distinct.

### Finding F1: carry the numerical error across segment restarts

The trial-trajectory residual in `FINITE_DYNAMIC_CLOCK_CONTRACT.md` equation (10) is correct. Equations (11)-(12), as originally written, apply only to zero error at the segment start. Enforcing population continuity at a later segment does not make its accumulated numerical error zero.

For a carried bound \(\|e(t_j)\|_1\le E_j\), the corrected state and integrated bounds are

\[
\|e(t)\|_1\le e^{-\gamma(t-t_j)}E_j+
\int_{t_j}^{t}e^{-\gamma(t-s)}\|r(s)\|_1\,ds,
\]

\[
\int_{t_j}^{t_{j+1}}\|e(t)\|_1dt\le
\frac{1-e^{-\gamma\Delta t_j}}{\gamma}E_j+
\frac1\gamma\int_{t_j}^{t_{j+1}}
[1-e^{-\gamma(t_{j+1}-s)}]\|r(s)\|_1ds.
\]

Carry the resulting endpoint bound into the next segment. The looser sum \(E_j/\gamma+\gamma^{-1}\int\|r\|_1dt\) is also valid. This finding concerns the subsequent finite-model error bound and does not affect Phase A. Root accepted inclusion in the Phase B contract during this pass; no extra review round is required. The residual remains numerical error, never a physical refill owner.

## C9: implementation inspection

The complete reviewed implementation comprises `native.py`, `diffusion_inverse.py`, `energy.py`, `phase_a.py` and `metered.py`, against R1 and the frozen Phase A coding contract.

- Source transcription preserves the original table layout, source grid construction and interpolation stencil, explicit rate normalization, operation ordering relevant to native cancellation, Gamma-before-core-diffusion update, two diffusion recurrences and source small-optical-depth branch. The H-only relation is supported by the actual preserved source-era witness. The steady matter temperature uses the original Kelvin operation order.
- The four new inverse calculations use the stored bin 100/179 traces and exact source radiative subtraction. Admissibility, positive diffusion remainder and the native optical-depth branch are checked without clipping. The separate 70-digit calculation uses the same actual binary64 input values; it is not a replay of the old inverse campaign. The assumed 32-ulp propagated interval is a declared diagnostic, not an empirically established physical bound.
- The energy derivative uses the local native polynomial with fixed radiation temperature and includes an independent high-precision derivative and a synthetic control that distinguishes the wrong total derivative. The selected source table remains the numerical object being differentiated.
- Full source and reduced operands are reconstructed before the right snapshot is opened. The snapshot validates; it is not used to infer the new state, coefficients or energy moments. Real/virtual residual scales and exact structural-zero checks are scientifically appropriate. The native cancellation-sensitive coefficients are judged by the frozen numerical tolerance, not demanded to be byte-identical.
- The wrapper binds the actual freeze, root execution signal, source checkpoint ACKs and pre-node observation, permits one invocation, records an interrupted or failed debit, and does not automatically retry. Its one-thread, 60 CPU-second, 180 wall-second, 768 MiB limits debit the fresh combined allocation. Requested model and unknown observed runtime model remain distinct. Historical budget balances remain null.

## Actual saved outcomes inspected

The reviewer inspected all 67 saved checks, the raw operand structure and relevant entries, summary, stdout/stderr, execution ledger, actual receipt and holdout comparisons. Hash identities were mechanically confirmed; no production module was imported or run.

| Actual evidence | Observed result |
|---|---:|
| Scientific invocations | 1 |
| Numerical checks | 67/67 PASS; 0 failed |
| Child CPU / wall | 1.129564 s / 1.2450745230016764 s |
| Peak child RSS | 32,892 KiB |
| Wrapper CPU, separately recorded | 0.029937999999999992 s |
| Fresh allocation remaining | CPU 58.870436 s; wall 178.75492547699832 s |
| Old inverse/tube/native history replay; new B3i; plot | 0 / 0 / 0; 0; 0 |
| Requested / observed runtime model | gpt-6.1-sol / null |

| Quantity | Knot 5126 | Knot 5127 |
|---|---:|---:|
| Source steady \(T_m\), eV | 0.25884325362029575 | 0.25882127610727856 |
| Bin 100 inverse \(T_m\), eV | 0.2588432535166457 | 0.25882127625683937 |
| Bin 179 inverse \(T_m\), eV | 0.25884325350862136 | 0.2588212760895028 |
| Two-bin relative discrepancy | 3.1000842579685825e-11 | 6.465333586553066e-10 |
| Steady branch deficit, limit 5e-4 | 1.048717440133018e-5 | 1.0497427047506669e-5 |
| Slow reduced eigenvalue, s^-1 | 164.19038064908932 | 164.01311053231404 |
| \(K_{\rm rec,2s}\), eV | 0.19993168787699173 | 0.1999167537700027 |
| \(K_{\rm rec,2p}\), eV | 0.154098098174049 | 0.15408658597987437 |
| \(K_{\rm ion,2s}\), eV | 0.19993376548417574 | 0.1999188332557037 |
| \(K_{\rm ion,2p}\), eV | 0.15409966701618286 | 0.15408815623713557 |

The largest primary/reference-70 temperature relative discrepancy is 1.325353896415409e-13. The largest two-bin discrepancy is 6.465333586553066e-10, within the frozen 2e-8 criterion. Source steady temperature exactly matches the saved right temperature; both assumed propagated intervals cover it, reported separately as an interval diagnostic.

The largest actual real-row gross-scaled residual is 5.2685145849511814e-15; the virtual counterpart is 2.2034736914934763e-10. The independently recovered electron fractions agree within relative 2.0626636482251524e-13. Positive Thomas denominators and the actual reduced M-matrix signs/eigenvalues support the subsequent reduced construction.

Right-holdout Alpha, Beta, DAlpha, mixing rate, Trr, Trv, Tvr, Gamma and diffusion coefficients match exactly. Cancellation-sensitive Tvv, sv and one-minus-P differ by at most about 1.55103138e-8 relative, below the frozen 5e-8 tolerance; structural zeros match. The correct claim is numerical agreement of these blocks, not bitwise equality of every original operand.

The largest analytic/reference partial-derivative discrepancy is 1.271069881369937e-12, and moment discrepancy is 1.1974451620518157e-12, both below 2e-10. Every selected moment is finite and positive. The largest gross-scaled three-sector energy-sum residual is 3.5248286086679557e-17, below 5e-14. The synthetic wrong-diagonal control separates 1.02 from the correct 0.66 moment.

Raw output identities:

- `results/SOURCE_OPERANDS.json`: 709,128 bytes, SHA256 `179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd`.
- `results/PHASE_A_CHECKS.json`: 16,039 bytes, SHA256 `2d37795777076329db19114735922e8f27bd2eb98d0b95f1bf01d6ac21538864`.
- `results/EXECUTION_LEDGER.jsonl`: SHA256 `2ad4cf97a4182e90501399f4fcfce5e3de3a705ae243f07066b596a789e88820` at the Phase A checkpoint. Later authorized stages may append to the cumulative ledger; the separate Phase A receipt preserves this identity.

## Claim ceiling and next executable transition

The actual inputs now support source-defined endpoint channels and a constructive finite two-interface completion. They do not yet constitute integrated finite stock/energy transfer, a completed Phase B trajectory, a new B3i consumption, or a physical continuum error estimate. Endpoint QSS refill is not renamed a finite physical refill, and a numerical residual is not an invented owner.

The next executable transition is the root-frozen Phase B construction using absolute diffusion, endpoint gross-channel maps, the native exact Ly-alpha clock, common finite stocks and the corrected carried-error bound. Phase A remains accepted and is not replayed. Any later concrete failure is interpreted for its selected claim, followed by the already allowed targeted repair or narrower executable subunit; it does not trigger a new supplier census or optional review layer.

The ANISO continuum–finite14 joint difference `3.447529542803539e-5`, approximately `1e-11` reconstruction residual and `2e-8` continuum numerical allowance retain their separate meanings. None is repurposed as a physical radius by this review.
