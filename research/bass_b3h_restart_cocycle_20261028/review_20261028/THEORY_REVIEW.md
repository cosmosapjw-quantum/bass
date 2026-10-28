# Restart review: clock/model mismatch and accumulated rewards

Status: directly derived and serially checked; distinct-author R6/C9 admission remains pending. This is a corrective continuation of PR212, not a new canonical node. Old theory and numerical results remain immutable.

## 1. What survives the previous theory
The affine map composition, binomial global-clock rebase and the same-law contraction estimate are algebraically consistent. Population contraction does not imply contraction of an accumulated reward. The old result is explicitly conditional on the same operator and reward law. Applying it to a changed clock without additional terms would be outside its assumptions; the old same-law theorem itself is not refuted.

## 2. Perturbed law and exact error identities
On [c,c+D], let p'=b-Mp, z'=a+Lp. Let the represented comparison obey p_hat'=b_hat-M_hat*p_hat+r_p and z_hat'=a_hat+L_hat*p_hat+r_z. All quantities are in one fixed proper-time, frame and reference-volume convention. Define e=p_hat-p, d=z_hat-z, delta b=b_hat-b, delta M=M_hat-M, and analogously delta a,delta L. Subtract, rather than re-closing the equations:

    e' = -M e + f,       f=delta b-delta M*p_hat+r_p;
    d' = L e + g,        g=delta a+delta L*p_hat+r_z.

No commutativity between M at different times is assumed. In particular, a clock change affecting only reward evaluation gives e=0 but need not give g=0.

Assume mu_1(-M(t))<=-gamma, gamma>=0; ||e(c)||_1<=epsilon_p; |d(c)|<=epsilon_z; ||f(t)||_1<=rho; ||L(t)||_infinity<=ell; and |g(t)|<=zeta on the entire interval. For vector rewards this applies to each separately unit-qualified row. The upper-right Dini derivative of ||e||_1 obeys

    D+||e||_1 <= -gamma||e||_1+rho.

An integrating factor and then a second integration give

    ||e(c+s)||_1 <= exp(-gamma*s)*epsilon_p+rho*phi_gamma(s),
    |d(c+D)| <= epsilon_z+ell*epsilon_p*phi_gamma(D)
                    +ell*rho*psi_gamma(D)+zeta*D,
    phi_gamma(D) = integral_0^D exp(-gamma*s) ds,
    psi_gamma(D) = integral_0^D (D-s)*exp(-gamma*s) ds.

For gamma>0, phi=(1-exp(-gamma*D))/gamma and psi=D/gamma-(1-exp(-gamma*D))/gamma^2. For gamma=0 their integral definitions directly give D and D^2/2; no singular formula is evaluated. These proofs require whole-interval bounds, not sampled values.

Units: gamma has s^-1; rho has population-unit/s; ell has reward-unit/(population-unit*s); zeta has reward-unit/s; phi has s and psi has s^2. Thus all four reward terms have the same units. The underlying (-,+,+,+), common V0 and cQ versus Q conventions are unchanged; this scalar error argument does not introduce natural units.

## 3. Exact-rational conservative implementation
For nonnegative gamma,D, exp(-gamma*s)<=1 implies phi<=D and psi<=D^2/2. For gamma>0, integration to infinity gives phi<=1/gamma, while (D-s)<=D gives psi<=D/gamma. Therefore

    Phi_bar=min(D,1/gamma), Psi_bar=min(D^2/2,D/gamma)

are valid positive upper envelopes; at gamma=0 use D,D^2/2. Substitution yields a conservative bound containing only rational arithmetic. code/checked_restart.py::reward_upper implements it using Fraction. Strings mean their exact decimal/rational literals, integers and Fractions are accepted, and floats/bools are refused to avoid silently choosing source semantics. This is exact for supplied rational bounds, not evidence that those inputs bound a physical universe. It is not claimed sharp; the exponential formula is generally tighter.

## 4. A diagnostic that population-only checks cannot see
In fixture units with T_star=1 s, choose p=1, b=M=1 s^-1, a=0, L(t)=t/T_star^2. Restart at c=1 s but evaluate L_hat(t)=(t-c)/T_star^2 through t=2 s. The population and its RHS are unchanged. Yet d(2)=-c*D/T_star^2=-1. Here epsilon_p=epsilon_z=rho=0, while zeta=c/T_star^2. The new direct reward term zeta*D is necessary and attained. This is a finite counterexample to discarding that term, not a universal impossibility theorem.

## 5. Actual code finding and smallest repair
The archived load_checkpoint checks textual identity and finite fields but does not bind t, step, dt to the fixed global scheduler. At checkpoint32 it accepts t=1.25 although rk4 starts from step*dt=0.25. Changing step or dt separately is accepted too. This is an execution-contract gap, not evidence that the original valid trajectory is wrong.

The new load_for_execution requires the caller's expected_dt and state_size, finite complete state/reward slots, and t==step*dt in exactly the scheduler's represented arithmetic. No new tolerance is introduced. It preserves the historical generic codec and schema. The two-line driver patch switches the actual manufactured restart call to this explicit boundary. The three original packets are accepted with identical float-hex values and counters. The full historical study is not rerun. No adaptive-controller, FSAL, pending-journal or native B4 restart support is claimed.

## 6. Saved native QSS reset interpretation
The stored reset_norm compares a represented cut population with a numerically evaluated QSS state. If comparing instead to the exact same-law nominal trajectory, include the inherited cut error E_cut as well as any separately supplied QSS evaluation error E_QSS. A conservative future-count bound is

    B_ref <= K*(delta_represented+E_cut+E_QSS),
    K=NH*Ralpha_upper/gamma.

The saved E_cut is present, so K*E_cut is computed separately in NATIVE_BOUND_QUALIFICATION.json using exact source-decimal rationals. E_QSS and physical/source errors are not newly supplied. The numerical delta and known contribution must not be called a new completed physical certificate. No new native trajectory or quadrature is needed for this distinction.

## 7. Evidence and limits
Soderlind2006, BIT46(3),631-652, DOI10.1007/s10543-006-0069-9 supplies logarithmic-norm background; this invocation confirmed its publisher/university bibliographic record and abstract, not the full article. The new inequalities above are proved here. Baake/Schlaegel Peano-Baker full text was read in the parent; a current web re-fetch returned Cache miss and is not reported as a new full read. SciSpace discovery found adjacent perturbation/output-error literature; none is imported as BASS-specific evidence or a missing physical input.

One Wolfram evaluator returned four zero residuals, zero-gap limits D and D^2/2, and the counterexample -1. Its Power::infy and Infinity::indet warnings are retained; warning origin is not established. The elementary integral proof does not depend on a warning-free CAS verdict. Native subagents and distinct-author review remain NOT_RUN. Original DAG28/88, stage18/20, physical radii null, L4=false.
