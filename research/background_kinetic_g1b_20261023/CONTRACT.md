# G1B: smooth-source convergence contract

Parent: PR183 ce59a3fd50139a0414d77d5fc493df9d45cd5f49. Preserve its finite-measure core/characteristics and all completed evidence without replay.

S0: continuous FD/Planck source, fixed normalization and analytic omitted-tail bounds. S1: positive composite radial/full-sphere angular quadrature, new tests and fixed-state separate refinements. S2: new curved V/VIII controls with separate radial/angular/time refinements, dual audit, figures and handoff.

q=cp/(k_B T_ref), tau=ct/L, kappa=8*pi*G/c^4. FD means momentum-decoupled 1/(exp(q)+1), not massive equilibrium in energy. Planck photons use 1/(exp(q)-1) at mass zero. The old clipped exponential remains a distinct finite-node source. Normalizers are fixed continuum integrals, not recalculated on each quadrature grid.

Massless degree-one characteristics and degree-zero logweight rates allow exact radial integration. qbar=I3/I2 and number weights preserve N^a and T^ab for separable initial spectra under collisionless frequency-independent transport. This is not an exact replacement of higher spectral moments or collisions.

Frozen gates: local normalized moment/boost/separation identities <5e-12; scalar normalization checks <5e-13; selected fixed-state and curved grid/time comparisons <2e-8; core/kinetic constraints and independent rho/flux mismatch <2e-8. Error denominators must be recorded. Coarse grids remain diagnostic failures where appropriate. Tail source bound target <1e-12; it is conditional on a common prescribed field, not a nonlinear coupled-trajectory certificate.

Q=48, positive GL subintervals [0,4,12,24,48], orders 4/8/12/16. Angular mu orders 6/10/14/20/28/40/56, nphi=2*nmu. Curved window tau=[0,.8]; monitored envelope |h|<=2, ||sigma||2<=1, |a|<=.5, yielding conditional K<=exp(3tau), J<=exp(7tau). Hamiltonian initial h uses each discrete density; its discrepancy is included in grid comparisons. Density is never renormalized to conceal quadrature error.

Current Python/C++ probes succeeded. New implementation tests were first executed against stubs:7 expected failures and1 new homogeneity check passed. After implementation8/8 passed. Native subagent review NOT_RUN; serial checks and actual CAS are not an independent model review. No parent changes, merge, force push, old campaign replay or production activation.
