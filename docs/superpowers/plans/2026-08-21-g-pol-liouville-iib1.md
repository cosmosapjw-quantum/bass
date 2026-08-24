# G-POL-LIOUVILLE-II-B1 implementation plan

1. RED: require tensor/Stokes roundtrip and canonical `packed[8]=-V/2`.
2. RED: require passive `exp(-2 i psi)` and active `exp(+2 i psi)` finite witnesses.
3. RED: require active/passive inverse composition and handedness mutation.
4. GREEN: implement validated local screen dyad and finite SO(3) tensor congruence.
5. Add independent complex-Hermitian Python oracle.
6. Mutate passive phase, active phase, and V extraction; each mutation must fail.
7. Replay the complete locked/offline RustCore and record the claim boundary.
