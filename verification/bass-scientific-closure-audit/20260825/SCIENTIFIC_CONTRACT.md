# Scientific contract

- Metric signature `(-,+,+,+)`; spatial orientation `epsilon_123=+1`; keep dimensional constants explicit unless a local source declares otherwise.
- Photon propagation direction, observed sky direction, electron-rest frame, normal frame, global tilt and output-only local boost are distinct typed roles.
- Formula authority is exact homogeneous polarized transport under cold non-tilted electron-rest Thomson assumptions. It is not a solver, finite-tilt theorem, recombination/reionization module or likelihood.
- Selected discrete non-vacuum carrier must satisfy `C r=0`, `a^T C=0`, `a^T r=1`, `P^2=P`, `C P=P C=0`, differentiated null identities, projector tangent identity, `K=[Pdot,P]`, `[K,P]=Pdot`.
- Exact vacuum does not select a nontrivial collision projector; fail closed.
- Registry/interface support is not output readiness. Smoke tests are not physics validation. `C_ell` agreement is not harmonic/map honesty.
- Speedup is valid only for identical equations, state, cutoff, tolerance, observable and fitting gate.
- Active reference/frontend is pure Python; backend target is locked/offline Rust 1.94.1; JAX/JAXlib/Equinox/Diffrax are excluded active targets.
- Every task must close, bind, test, reproduce, document or optimize an existing authority. If new physics is required, stop and request new authorization.