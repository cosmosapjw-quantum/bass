# BF3-D S0: integrated-package local-source mapping

Parent integration PR223 / 5461d50b3f187b4736b62e0f9ecb3e85e413aaee. Verified integrated code25827103b79ae49287722e56277ef1943b562d85. Current runtime PYTHON_PASS. Native subagent/independent model review NOT_RUN. Scoped/source-mapped DAG8/15, upper BF3 PARTIAL; no production promotion.

Selected scope only: static positive periodic lapse N=exp(epsilon cos x), signature(-+++), coordinate u=t/Tstar, cbar=cTstar/Lstar; untilted cold elastic Thomson. Proper opacity nu_star=n_e_star sigma_T c, coordinate collision rate=N nu_star. No EFE/material/recoil/next memory stage.

Build inverse phase map from each final(x,n) using unchanged integrated TetradHistory. Local M(x) is integrated over final physical angles; global phase Jacobian is not a local angular weight. Use Y=N^4 E^T J E in the meridional screen about x: Y_t+cbar N mu Y_x-cbar N'(1-mu^2)Y_mu=N nu_star(K[Y]-Y). Smooth full-IQUV fields, especially axisymmetric fixtures; no amplitude expansion.

Compare Fourier/Legendre collocation method of lines with inverse-ray Fourier/barycentric remapping and exact local P8 collision in Strang order. They approximate the same continuum problem but are not presumed the same finite discretization. Separate time, spatial and angular errors. Preserve raw weights, signed differences and whole initial carrier; no clipping/renormalization.

Predeclared gates: algebra/source2e-11, inverse-ray8e-10, stationary4e-10, fine-time coupled error2e-4, observed Strang order>=1.7 on resolved fixture. Killing-energy and refinement errors measured separately, not certified bounds. Exact free translation, equilibrium N^-4, local-source map and constant-lapse N nu clock are required tests.

S0 source/derivation lock; S1 runnable implementation+tests; S2 bounded science+final report/DAG/handoff. Each stage receives create-only Drive/Dropbox backup and isolated Git publication. No next scientific unit or merge. Local runtime uses a selected exact numerical package projection; full installed-package CI is separate.
