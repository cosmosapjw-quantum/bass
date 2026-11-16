# Source-conditioned cascade results

Original parent PR337 is unchanged. The present local model has six bound states plus an ion tracer, with proper electron density supplied by the parent and held fixed during each local kinetic test. This is not a new closed cosmological charge/electron solution.

K3 generated 358 source-state generators, 358 Schur generators, 358 fast-population lifts and1074 retained effective capture/photoionization records. At zmean1100 the effective capture enhancements for1s,2s,2p are1.1272991997340644,1.116111187359855,1.5173707962323546. They are conditional on the explicit n<=3 optically thin model and are NOT the complete HYREC infinite-n effective coefficients. No parent coefficients are overwritten or added a second time.

The original six-state stationary solution and the Schur stationary vector reconstructed to seven states agree to maximum5.955369530852295e-11 relative. Exit probability columns sum to one within2.220446049250313e-16. Microscopic and reconstructed reduced energy ledgers have maximum relative residuals5.056945962141159e-16 and5.243438307404206e-16, normalized by gross exchanged energy.

At zmean1100 the two-photon downward rate is8.393601812873786 s^-1 versus the source vacuum normalization8.2206 s^-1; upward rate7.876353139409833e-17 s^-1. The standard/hires two-photon down-rate difference over the actual source reaches6.181386118964127e-5 relative, distinct from thermal/balance algebraic residuals.

The finite model includes a photon-number-changing cycle 3p->2s->1s->3p. In a Planck bath without tilt its affinity vanishes. In a BE bath with chemical parameter eta and zero tilt it is2eta, not zero; channelwise detailed balance does not imply global radiative chemical equilibrium at eta!=0. At the boosted zmean1100 field it is0.2985015405557654. A fixed nonthermal photon bath may support stationary cyclic currents; do not label the full bath an equilibrium system.

The frequency-dependent Schur response including the eliminated-state initial term reproduces the full resolvent at machine precision. A bare zero-frequency Schur response has a nonzero frequency error; first-order storage improves the low-frequency response in this specific example but has no general positivity guarantee. An initially pure3s atom has a finite residence time: instant routing to exit states differs at t=0 by retained L1 mass1. Independent Radau versus full matrix exponential evolution differs by1.574740338128322e-12 absolute on the finite test window. This is an explicit counterexample to treating stationary elimination as exact chronological evolution.

A diagnostic Python reduction initially used built-in max over matrix rows and raised an ambiguous-array exception. It was replaced by np.max for the intended scalar flux scale, without changing physical formulas, source data or acceptance thresholds. The failed log is retained.
