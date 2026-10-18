# PR150 native source intake and bolometric boundary

The immutable native owner is REI commit `0e25846433170d0f420c4cda44a0bedbf02cd177`.
The copied source files are byte-identified in `evidence/native_source_snapshot/`:

| file | SHA-256 |
| --- | --- |
| `axbi_sources.rs` | `606e3c2ec367dd9951ebbf2f53486f2232b49c0218896d66d8dc13dd5ee83bfe` |
| `axbi_covariant_transport.rs` | `9d2d97881ca7b9b58d68dbeffad937e16ca8af237b3d9ba01de0fb5e00b67aa7` |
| `axbi_driver.rs` | `41c969a5308070c0a27708cf7443a96f83bdb2a7685edd5ee8819c46a8e96414` |

`AxbiSource::at_redshift` supplies a photon number emissivity.  It defines
`proper_photons_cm3_s = comoving/MPC_CM^3 (1+z)^3` and
`per_h_s = comoving/(MPC_CM^3 n_H0)`.  Hence its proper hydrogen density is
`n_H = n_H0/a^3`, and `n_H * per_h_s = proper_photons_cm3_s` at the same
clock.  The source spectrum is BB50k on 13.6--100 eV, partitioned by Simpson
number fractions; its directions use Gauss--Legendre `count_fraction` values
whose sum is one.  The source is already 4-pi integrated.

In PR150 `Driver::tentative`, the driver calculates the interval proper time,
maps to `sqrt(a_old*a_to)`, then calls `inject`; that injection evaluates
`zbar=1/a-1` at this geometric midpoint.  The chemistry stage uses that same
midpoint state, before a final map to `a_to`.

The energy actually represented by `CovariantTransport::inject` is not simply
the Simpson cell mean.  It divides each Simpson fraction by a GL8 source norm,
then deposits GL8 moments over intersections with the 128-cell log transport
grid.  The Python control mirrors this distinction.  Its source Simpson mean
is `20.276595394872462 eV`; the represented reference-grid mean is
`20.276595394981342 eV`.  This approximately `5.37e-12` relative quadrature
difference is expected from distinct numerical operators.

For the instantaneous convention only,

\[
j_{\rm proper}=\dot n_{\gamma,\rm proper}\,\bar E_{\rm transport},\qquad
S(x)=j_{\rm proper}/H,
\]

and a REI source injection over the control duration `dt=1/H` gives
`n_H * (per_h_s * Ebar/H) = S`.  This is a unit and clock conversion check.
It does **not** measure a Rust `SourceLedger`, establish finite-step source
accuracy, or authorize a checkpoint/restart.

The detached PR150 crate compiled with `cargo test axbi_sources --lib` using
Rust `1.99.0`; it exited zero but selected zero tests.  A first attempt used
the non-workspace `rust/` directory and exited 101; no owner source was
modified.  Both are build facts, not a native source-injection measurement.
