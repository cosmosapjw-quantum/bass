# Alternative-CAS and quadrature mutation CRAG

## Observed numerical probe

At `L=6`, a Condon–Shortley spherical-harmonic field satisfying the reality condition was synthesized and projected with:

```text
canonical rule      N_mu=7, N_phi=13
max residual        7.016294824576192e-15

underresolved mu    N_mu=6, N_phi=13
max residual        1.4000000000003076e-2

underresolved phi   N_mu=7, N_phi=12
max residual        4.669833716397564e-3
```

The proposed parity tolerance is `2e-13`. The canonical rule is below it; both one-node underresolution mutations exceed it by more than ten orders of magnitude.

## CRAG

- **Correctness:** the canonical result agrees with the polynomial/Fourier exactness count and the field remains positive on the test grid.
- **Retrieval:** the behavior is consistent with literature warnings that angular sampling and harmonic analysis must be matched explicitly.
- **Augmented:** SymPy found no Wigner triangle/parity violations among 204 nonzero bounded-regression symbols; mpmath verified seven-node Gauss–Legendre moments through degree 12 at 80 digits.
- **Generation:** R10 should produce a residual-versus-rank plot and preserve the strong separation between admitted and underresolved rules.

## Claim status

```text
survives: bounded quadrature contract and mutation sensitivity
narrowed: one manufactured scalar finite-rank fixture only
rejected: transport-level or arbitrary-source parity
```
