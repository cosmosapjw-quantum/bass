# R6-N1 — pre-execution metric clarification

This addendum closes the independent R6 request without changing any equation,
source, initial state, interval or frozen threshold. It is part of the input
contract before the first scientific Python execution.

For coarse result a and fine result b on the same final tau:

- `geometry`: max absolute difference of h, all three sigma_i, alpha and all
  three beta_i, divided by the fixed initial h0=1 (dimensionless in this client).
- `x`: abs(x_a-x_b)/x_b, where the selected fixture has x_b>0.
- `photon_number`: abs(n_gamma,a-n_gamma,b)/n_gamma,b; n_gamma,b>0 here.
- `photon_tensor`: maximum absolute component of T_gamma,a-T_gamma,b divided
  by rho_gamma,b>0, all in fixed alphaL units. The tensor includes its energy,
  flux and spatial components; it does not compare different cohort labels.
- `maximum`: maximum of these four distances. The final64/128 gate is2e-8.
  The tighter-A128 comparison uses these same definitions and2e-10.

Constraint means unchanged `core.relative_constraint` at each saved source/
drift state. Do not divide a small stress component by itself. Atom-number
relative residual is abs(exp(3alpha)*N/N0-1). Excitation-plus-photon residual
is abs(exp(3alpha)*(N*x+n_gamma)/(N0*x0)-1), threshold5e-12. Energy-work residual
is abs(u(t)+W(t)-u(0))/u(0), u=rho_exc+rho_gamma, threshold2e-10. Ground rest
energy is excluded from this denominator. Source original256eps checks remain.

For each successive pair distance e_n=dist(result_n,result_2n), report
p_n=log2(e_n/e_2n) only if BOTH distances exceed4096*machine_eps and are
strictly positive. Otherwise set the order to null with
`ROUNDING_UNRESOLVED`, retaining the actual distances. The same rule applies
to oracle errors for prescribed Lie/Strang runs. The [1.8,2.2] order gate applies
to resolved source/radiation distances at the finest available triplet; at
least one resolved source/radiation distance must demonstrate it for a numerical
second-order claim. A component near roundoff cannot support that claim.
Geometry order is diagnostic because source backreaction can be very small.

Prescribed oracle uses a monotone scalar residual distinct from the parent's
log-flow call and scipy quadrature over its exact exposure variable. Integrate
dimensionless moments before SI conversion with epsabs=2e-13, epsrel=2e-12,
and record quadrature error estimates. These are numerical estimates.

The f_plus=0 support theorem concerns the outgoing side of the unresolved
Sobolev line. It does not assert that any emitted photon never reinteracts in
a physically resolved finite-width line wing. Existing native absorption/
finite-receiver ownership remains open.

Implementation must use stored n_u and the source's multiplication order for
rho_exc=scale.density_factor*E*n_u when calling the parent transaction, so a
last-bit reassociation cannot incorrectly trigger insufficient donor energy.
The lower population and total N must be constructed consistently with actual
LineState before the transaction; retain all physically relevant residuals.

Ground mass inputs use the CODATA2022 recommended proton/electron masses,
https://physics.nist.gov/cuu/Constants/ and
https://physics.nist.gov/cuu/pdf/JPCRD2022CODATA.pdf . M0=mp+me is an explicit
approximation to constant ground rest energy, separate from numerical accuracy.

R6-N1 disposition: CLOSED by these pre-execution definitions. No second broad
review is required; C9 will read the implemented formulas against this contract.
