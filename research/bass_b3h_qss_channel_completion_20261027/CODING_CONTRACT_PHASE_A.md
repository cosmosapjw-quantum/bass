# Frozen Phase A: source operands and effective energy moments

Root scientific authority, 2026-10-27. Implementation is delegated. This phase is a new calculation on newly selected diffusion traces and source operators. Old scientific result programs are not invoked.

## Immutable data and source

Use `NATIVE_QSS_STORED_INPUT_5126_5127.json`, SHA256 `c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710`, its exact eleven original source/table members, the inherited completed inverse result and finite-tube result, and the H-only phase witness. The right snapshot is validation-only; values taken from it must never feed reconstruction.

The source phase witness establishes xe=xHII for the selected solver era. Set xHII=1-x1s from the completed inverse and use xe=xHII as that original source convention. The two real-row inversions for xe are independent checks, not an assumption about exact physical helium ionization.

## New diffusion reconstruction

For b=100 and179 and each of the two knots, form r=(favg-fin)/(fout-fin), recover tau from F(tau)=1/(1-exp(-tau))-1/tau using the already qualified scalar inverse function or an equivalent stable implementation. Reusing this helper is allowed; calling the old full inverse/result is not. Preserve signs and reject nonadmissible ratios; no clipping. All selected tau must exceed1e-6 before applying the source exponential relation.

Compute Gamma=8*pi*H*tau/(x1s*nH_cm3*lambda_cm^3). Obtain the radiative contribution from the full original normalized two-photon table and source coefficients. At b100, Adn=0 and Gamma-Gamma_rad=Aup100; at b179, Aup=0 and Gamma-Gamma_rad=Adn179. The positive boundary coefficient gives

Tm=(Gamma-Gamma_rad)*mH*(DeltaEb)^2/(2*E21^2*A1s_b)

for fsR=meR=1. All energies and Tm are in source eV convention. The primary trace inverse uses b100; b179 is an independent bin check. Record cancellation/ratio conditioning and propagate the existing assumed32ulp trace/input model through tau, Gamma and Tm. This is a numerical diagnostic assumption, not a physical radius or a proof of original source accuracy. A 70-decimal reference inverts the exact binary64 trace values independently.

Pre-execution source-intake addition: independently evaluate original `history.c::rec_Tmss` at the completed xe,H,TR. In Kelvin, Tm_ss=TR_K/[1+H*(1+xe+fHe)/(4.91466895548409e-22*TR_K^4*xe)], fHe=Y/(1-Y)/3.97153, for fixed fsR=meR=1. The local steady-temperature guard is1-Tm/TR<5e-4. Its observed satisfaction does not establish an unrecorded whole-prefix branch history. Require both diffusion reconstructions to agree with this source formula within2e-8 relative and the right snapshot check below. On that actual agreement use Tm_ss for downstream native coefficient reconstruction, retaining all four independent trace-inverse values and errors. This source formula avoids carrying the poorly conditioned trace inversion's roundoff into tiny thermal energy moments. If agreement fails preserve results and return to root; no switch or tolerance relaxation is automatic.

## Rate tables, source blocks and channels

Transcribe the original C `read_rates`, `interpolate_rates`, `read_twog_params`, `populate_Diffusion`, and `populateTS_2photon` equations. Preserve native source switches, constants, normalization, table ordering, nH in cm^-3, and the distinct small-tau branch used for other virtual bins. Do not rerun the native history solver. A direct evaluation of the source's coefficient formulas at two saved states is the work selected here.

Use completed endpoint TR,nH,H,x1s and the independently trace-qualified source Tm_ss. Construct Alpha,DAlpha,Beta,R2p2s, all block matrices and sources, and separate additive row contributions: bound-free, effective real-state mixing, Lyα, Lyβ/γ, two-photon/Raman, core diffusion, and virtual diffusion. Label components by their actual source lines. Store the complete reconstructed endpoint operands for Phase B reuse.

With the stored real and virtual departures, recover sr_req=Trr*xr+Trv*xv and compare with independently constructed source sr. For each real row, solve

xe_i=[(sr_req_i-line_in_i)/nH - s*x1s*DAlpha_i + Alpha_i*s*x1s]/(Alpha_i*xHII)

and compare with the source H-only xe. Keep gross term scales alongside cancellation-sensitive differences.

Compute W=Tvv^-1*Tvr and v=Tvv^-1*sv using the native diagonal-outside/tridiagonal-inside structure. The reduced two-real-state operator is M=Trr-Trv*W and s_eff=sr-Trv*v. Evaluate block residuals on stored populations; a new native trajectory/old inverse is not needed. Store eigenvalues, sign structure and the exact source-versus-absolute Wiener shift terms. Temperatures here mean energy k_B T.

## New energy-moment closure

At fixed TR use the original cubic log-rate interpolation to evaluate the partial Tm derivative analytically. Define

Krec_i(Tm,TR)=3*Tm/2+Tm^2*partial_Tm(log Alpha_i),
Kion_i(TR)=3*TR/2+TR^2*partial_Tm(log Alpha_i)|Tm=TR.

The partial derivative fixes TR, including all cascade probabilities and stimulated-radiation factors. It is not the derivative along Tm=TR. Compare the implemented derivative with independent70-digit differentiation of the explicit interpolation polynomial. Preserve exact table-boundary cell selection. This is a derived Maxwellian kernel moment evaluated with a newly selected table-interpolant closure; original native heat output was not supplied.

For each successful effective continuum↔interface channel, let R_i=nH*xe*xHII*Alpha_i and I_i=Beta_i*p_i. Per hydrogen nucleus and proper second, with chi_i=EI-E21,

Q_atom_i=-chi_i*(R_i-I_i),
Q_kin_i=-Krec_i*R_i+Kion_i*I_i,
Q_rad_i=(chi_i+Krec_i)*R_i-(chi_i+Kion_i)*I_i.

Record individual positive gross events and energy contributions and the sum-zero identity. Multiply by nH_reference and explicit eV_J to obtain common-reference-volume rates. The probability-path/differential-detailed-balance derivation must be included in the theory artifact before scientific admission. Continuum-return null cycles are a separately unselected channel; do not claim their rates or thermal contribution from Alpha_i alone.

## Fixed acceptance and checks

1. Four diffusion inversions are admissible and remain on the original exponential branch. Primary/reference tau and Tm relative difference <=2e-10, measured against nonzero own quantities.
2. Tm from b100 and b179 agree within2e-8 relative. Right primary Tm versus validation snapshot <=2e-8. Report the propagated assumed intervals and whether they cover the holdout separately.
3. Right Alpha/Beta/R2p2s, source block matrix entries and source components agree with the original snapshot within5e-8 relative to their stated nonzero entry or row-gross scale. Exact structural zeros remain zero. Do not divide by cancellation-zero entries or turn a gross-scale result into a net-relative claim.
4. Stored-state real/virtual row residuals <=5e-8 of each row's sum of absolute operands. Independently inferred xe from each real row agrees with H-only xe within5e-8 relative.
5. Tvv Thomas denominators and reduced M eigenvalues are positive; reduced off-diagonals nonpositive within explicit arithmetic tolerance. Preserve actual values; no eigenvalue clipping.
6. Krec and Kion are finite and positive at both selected states; analytic versus independent70-digit derivative/energy moments <=2e-10 relative. Check a fixed-TR synthetic Maxwellian kernel with a known energy moment to distinguish partial and diagonal derivatives. Synthetic controls remain separate from actual native data.
7. Channel energy cancellation residual <=5e-14 times sum of absolute gross energy terms. Keep source units and SI conversion explicit.
8. A small number of targeted bad-input/domain controls cover ratio invalidity, input identity, negative diffusion coefficient, wrong partial derivative direction, and physical-radius null preservation. No broad old suite.

On a failure preserve inputs, stdout/stderr and partial results, then return the actual failure to root. A targeted correction may proceed under the remaining allocation with its own recorded execution; do not silently change a tolerance or input/model.

## Fresh bounded allocation and outputs

New unit cumulative scientific allocation: child CPU60s, wall180s, peak RSS768MiB, one BLAS/OpenMP thread. This allocation covers Phase A, a later independently frozen finite Phase B, and one saved-result-only plot. It does not reopen any older allocation or fill unknown historical budgets. Record scientific subprocess and wrapper costs separately. Unmeasured model/network/preparation cost remains unknown. No scientific run before the S0 source backup/publication checkpoint is confirmed by root.

Phase A is one metered invocation containing its targeted controls and actual source-operand evaluation. Save `results/SOURCE_OPERANDS.json`, `results/PHASE_A_CHECKS.json`, stdout/stderr, exit code, exact command and cumulative execution ledger. New B3i calls in Phase A:0. Source estimates from Phase A are immutable inputs to Phase B; Phase A is not automatically rerun there.

Phase B equations, closure/clock choice, donor capacities, actual energy owners, numerical tolerances and any once-only B3i call will be fixed in a separate root-authored contract after inspecting these operands and the independent theory result.
