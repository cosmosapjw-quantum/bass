# Type-II Codazzi initialization evidence

The legacy/source tilted-fluid implementation defines

`q_flux = 3 * gamma * Omega * v / G_plus`.

The Type-II geometric momentum in direction 1 vanishes for diagonal
`N=diag(N1,0,0)`, so the first Codazzi constraint forces
`3 gamma Omega v1 / G_plus = 0`. For physical `gamma>0`, `Omega>0`,
`G_plus>0`, WSC-3 therefore initializes `v1=0`.

This is branch-specific and is not generalized to other Bianchi types.
