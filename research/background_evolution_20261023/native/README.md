# Fixed-scale Bianchi background: independent Rust operator

This crate has no external dependencies. It implements the Einstein background
and per-sector energy/flux equations in fixed reference units; it is an RHS and
constraint evaluator, while the surrounding campaign supplies time integration
and matter/radiation closures.

The variables use `x=ct/L`, `h=L H_phys/c`, `sigma=L sigma_phys/c`,
`N=L n_geom`, `A=L a_geom`, `rho=kappa L^2 mu`, `flux=kappa L^2 F/c`,
`p=kappa L^2 p_phys`, `Pi=kappa L^2 pi_phys`, `lambda=Lambda L^2`,
with `kappa=8*pi*G/c^4`. No division by the instantaneous Hubble rate occurs.
Frame vectors receive `+R cross v`; tensors receive the corresponding commutator.
The full derivation and source normalization are in the parent campaign's theory note.

## Build and verify

```sh
cargo test --offline
cargo build --release --offline
python3 verify_cli.py
```

If the standalone toolchain is not on PATH, set `RUSTC` and `RUSTDOC` to its
absolute executable paths and invoke its absolute `cargo` path. Cargo.lock is
committed; the dependency list contains only this package.

Public Rust functions are `rhs(sectors, state, sources, lambda, rotation)` and
`constraints(sectors, state, lambda)`. Both return `Result` and reject malformed
or nonfinite inputs. The RHS also rejects unbalanced sector transfers, using
`abs(sum) <= 128 * f64::EPSILON * sum(abs)` component by component. The balance
check rescales by the largest magnitude before summing to avoid overflow.
Zero sectors are allowed for vacuum. No state is projected, clipped, or silently
replaced by a closure.

## CLI line protocol

Each nonempty input line is one independent state. Tokens are separated by whitespace.

1. A nonnegative integer sector count `s`.
2. State: `h`, sigma `(xx,yy,xy,xz,yz)`, N `(xx,yy,zz,xy,xz,yz)`, A `(x,y,z)`,
   `alpha=ln(scale)`, all `rho_s`, then all sector flux triples. State length is `16+4s`.
3. All pressures (`s` values).
4. All sector stress five-tuples `(xx,yy,xy,xz,yz)` (`5s` values).
5. All energy transfers (`s` values).
6. All momentum transfer triples (`3s` values).
7. `lambda`, then frame rotation `(R_x,R_y,R_z)`.

The total input length is `21+14s` tokens, including `s`. STF stress and shear
have `zz=-xx-yy` by representation.

Each valid output line contains `16+4s` RHS values in state order, followed by
seven diagnostics: Hamiltonian `C`, Codazzi `M_x,M_y,M_z`, Jacobi `J_x,J_y,J_z`.
Numbers use 17 digits after the decimal in scientific notation. Invalid input
produces a concise stderr diagnostic and nonzero exit code. Earlier valid lines,
if any, retain their output.

The diagnostics are

```text
C = 3h^2 - sigma:sigma/2 + R3/2 - sum(rho) - lambda
M = sum(flux) - 3 sigma A - epsilon(N,sigma)
J = N A
```

Tests use analytic flat dust/radiation FLRW derivatives, vacuum Kasner,
closed dust at H=0, de Sitter, rotation of flux, opposing sector work, and
invalid-input/transfer rejection. Python-versus-Rust family/random parity and
time-history checks are performed by the parent campaign.
