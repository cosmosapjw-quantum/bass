# PHYS-MATH-CODE audit — BASS-8B.2B carrier preflight

## Code-path reality

The witness implements the project-validated sequence

```text
fixed electron-rest quadrature
-> inverse aberration to paired normal nodes
-> Doppler/Jacobian weight map
-> basis-free screen tensor boost
-> rest Thomson gain-loss
-> normal-time relative-flux action
-> paired right/left/projector tests
```

It does not call the production solver and does not mutate E1–E4 owners.

## Fresh verification

```text
pytest                         6/6 PASS
exact SymPy counterexample     PASS
paired right-null max          9.690270078462301e-16
paired left-null max           4.1855216120648364e-16
P^2-P max                      6.661338147750939e-16
physical nullity               1 in all 33 sweep cases
minimum physical spectral gap  0.2147904457756587
SO(3) collision residual       8.881784197001252e-15
SO(3) projector residual       3.9968028886505635e-15
```

## Hostile controls

- fixed-normal finite-boost equilibrium residual grows far above roundoff;
- omitting the direction-dependent factor from the dual produces defects from
  `1.22e-3` upward over the tested finite-speed sweep;
- unchanged-left exact mutation fails in the two-node SymPy witness.

## Remaining P0/P1 risks

- **P0:** row 8 cannot close until the E2 rate/time map and the discrete dual
  are bound in one exact contract.
- **P0:** bundle-aware derivatives are absent; the axis-aligned fixed-node
  `P_,v` formula is not generic-vector authority.
- **P1:** only one numerical implementation of the generic-vector extension is
  present.
- **P1:** refinement and conditioning beyond Lebedev-26 and `|beta|<=0.5`
  remain untested in this package.
