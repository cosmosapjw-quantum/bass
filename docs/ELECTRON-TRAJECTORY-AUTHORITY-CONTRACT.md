# Electron trajectory and optical-depth orientation authority

Status: **bounded Python authority; no production wiring or row promotion**.

## Claim

`bianchi.q.electron_trajectory` lifts the instantaneous exact-cold E3
total-cross-section decision onto a finite closed interval of Q Hubble time.
It binds six time-dependent inputs to one provenance-bound coordinate, forms
their exact closed support intersection, partitions at the union of all knots,
and records a conservative energy/temperature witness on every non-vacuum
segment.

This is not a direction-dependent scalar-Q collision generator.  It does not
certify the polarized differential Klein--Nishina kernel, a finite-temperature
electron tail, a production collision exponential, JAX/Rust integration, or a
finite-multipole hierarchy.

## Coordinate and units

The only accepted coordinate is the explicit identity binding
`q_hubble_time_tau`:

```text
tau_Q                  dimensionless, strictly future increasing
dt_phys/dtau_Q         1/H_normal
H_normal               s^-1 and >= smallest normal positive binary64
E_gamma,max            J
T_e                     K
nu_tau                  d optical_depth/dtau_Q >= 0
metric                  (-,+,+,+)
```

Redshift, conformal time, affine time, and nonidentity conversions are rejected
instead of inferred.  Every array is finite, immutable, and strictly increasing
in `tau_Q`, and every adjacent binary64 interval must itself be finite and
positive.  Thus nominally finite endpoints such as `(-DBL_MAX,+DBL_MAX)` that
would make the live interpolation weight `inf/inf` are rejected.  A requested
endpoint one binary64 ULP outside the common support is an error; there is no
clamp or extrapolation.

## Electron closures and frame transformation

The independent lane retains the exact E2 interpolation owner

\[
N_e^A(\tau_Q)=n_e^\star U_e^A
\]

piecewise linearly.  Its trajectory view exposes immutable four-current knots,
not a reinterpolated velocity.  Exact vacuum quotients the arbitrary electron
velocity.

The comoving lane retains a piecewise-linear proper density and requires a
separate provenance-bound live-fluid velocity profile.  At positive density
it enforces

\[
u_e=u_{\rm fluid}.
\]

The independent lane rejects a supplied fluid profile, and the comoving lane
rejects its absence.  Therefore a frame transform cannot silently turn one
closure into the other.

For one segment, the independent current is affine in a local coordinate
`w`.  With

\[
q(w)=(N^0)^2-|\mathbf N|^2,
\qquad \gamma_e(w)=N^0/\sqrt{q},
\]

the derivative of \(\gamma_e^2\) has a linear nontrivial factor.  The authority
checks both endpoints and its interior root, if the root lies in `(0,1)`.
For an affine source velocity, `|beta_source|^2` is convex, so its gamma maximum
is at an endpoint.  The declared conservative relative-frame bound is

\[
\bar\Gamma_{se}
 =\bar\gamma_e\bar\gamma_s
   (1+\bar\beta_e\bar\beta_s),
\qquad
\bar D=\bar\Gamma_{se}
 +\sqrt{(\bar\Gamma_{se}-1)(\bar\Gamma_{se}+1)}.
\]

The hard electron-frame energy and cold parameters are bounded by

\[
\bar E_e=\max(E_{s,0},E_{s,1})\bar D,
\quad
\bar x=\bar E_e/(m_ec^2),
\quad
\bar\theta_e=k_B\max(T_{e,0},T_{e,1})/(m_ec^2).
\]

The stationary calculation uses exact rational arithmetic over the stored
binary64 knot values.  A separate enclosure covers the actual binary64
multiply/add interpolation and, for independent electrons, the subsequent
component-wise current division used by the live schedule.  It bounds the
Minkowski timelike margin before deriving a velocity/gamma bound.  If that
enclosure cannot prove timelikeness or subluminality--including a moving
current that touches exact vacuum--the segment is
`unverified_numeric_domain`; it is never certified.  Source and live-fluid
beta profiles use the analogous component-error enclosure.  Normal-Hubble
knots below the smallest normal positive binary64 are rejected so interpolation
cannot silently underflow to zero.  Independent-current magnitudes must also
leave enough headroom for the live evaluator's norm and proper-density
reconstruction; finite knots near `DBL_MAX` therefore fail closed rather than
producing an unusable positive certificate.  The timelike margin must likewise
remain large enough that the live norm product cannot underflow to zero; tiny
positive currents that fail this check are unverified.  For a rest current
touching exact vacuum, the check additionally evaluates the next-representable
owner-time weight and requires its first positive temporal current to be above
the live norm-product floor; moving vacuum-touching currents remain
unverified.  Comoving-density interpolation receives an overflow enclosure as
well.  Energy and temperature maxima include the same scalar multiply/add
enclosure, covering the possible one-ULP overshoot of a nominally constant
binary64 profile.

Decimal100 is used only after exact-rational selection for square roots and
outward binary64 export.  Exact nonnegative zero is preserved as zero.
Bolometric, unknown, and effective-tail supports remain unverified.  Any
positive temperature remains an unverified finite-temperature-tail case even
when the caller's scalar theta predicate passes.

## Optical-depth roles

The positive local rate is shared, but the two derivatives and allowed
traversals are distinct:

```text
FUTURE_KINETIC_IVP
    dT_local/dtau_Q = +nu_tau
    tau_start <= tau_end

PAST_LIGHT_CONE_ACCUMULATION
    kappa(tau_Q) = integral_tau_Q^tau_observer nu_tau d tau_Q
    dkappa/dtau_Q = -nu_tau
    tau_start >= tau_end
```

For paired traversals of one physical segment,

\[
\int_a^b\nu_\tau d\tau_Q
=(-1)\int_b^a\nu_\tau d\tau_Q\ge0.
\]

The implementation integrates the piecewise-linear profile by exact
trapezoids.  Reverse traversal does not reverse or mutate canonical arrays.
Unsupported role/direction combinations raise.

The local ray-rate profile in E4 is a separately provenance-bound input used
only to certify support and orientation.  E4 does not claim that it was derived
from the supplied electron schedule, so an electron-vacuum segment can coexist
with a positive external rate.  Deriving and binding
`nu_tau = n_e sigma_T c D/H_normal` belongs to the later collision-generator
authority.

This reconciles the positive differential opacity and past-depth convention
in Seljak--Zaldarriaga,
\(\kappa(\tau)=\int_\tau^{\tau_0}\dot\kappa d\tau\), with the covariant
future-ray rate \(-k\!\cdot u>0\) used by Younsi--Wu--Fuerst:

- https://arxiv.org/pdf/astro-ph/9603033
- https://arxiv.org/pdf/1207.4234
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

## Statuses and stop boundary

Only `certified_cold_delta_trajectory` is a positive non-vacuum certificate.
Exact all-vacuum support is collision-off and vacuous, not certified.  Other
statuses fail closed for spectral support, numeric domain, the caller-owned
total-cross-section budget, the caller-owned theta predicate, or an unbounded
finite-temperature tail.

The certificate hash binds the coordinate origin and provenance, schedule
payload and upstream locator, all profiles, closures, union-segment witnesses,
budget, SI constants, and both orientation roles.  Metadata fixes all of the
following to false:

```text
q_collision_generator_wired
production_runtime_wired
rust_abi_wired
authority_row_promoted
```

Certificate construction is factory-only and re-derives status, certification
flag, and reasons from segment witnesses.  Segment witnesses also enforce
vacuum/cold/finite-temperature invariants.  Consequently nested dataclass
replacement cannot relabel an unverified result as certified.  The payload hash
remains a content commitment, not a signature or external trust anchor.
