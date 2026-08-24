# Electron test-field and frame-adapter contract

Status: `BOUNDED_IMPLEMENTATION — NOT CANONICAL ROW PROMOTION`  
Date: 2026-08-23

Subsequent bounded companion: `docs/ELECTRON-COLLISION-RATE-CONTRACT.md`.
Section 7 below records the frame-adapter checkpoint boundary at the time it
was sealed; BASS-8B.1E.2 subsequently implements the rate/schedule seam without
production-loop or authority-row promotion.

## 1. Selected model

The authoritative selector is one encompassing model:

```text
H2_WITH_COMOVING_RESTRICTION
```

The independent cold-electron test field is the full model.  The former H1
choice is supported as its exact velocity restriction,

\[
\boldsymbol\beta_e=\boldsymbol\beta_f
\quad\Longleftrightarrow\quad
u_e^a=u_f^a.
\]

H1 and H2 are not recorded as two simultaneous XOR booleans.  Nor is a frame
change allowed to convert a generic H2 physical state into H1.  The invariant

\[
\Gamma_{ef}=-\frac{u_e\!\cdot u_f}{c^2}
\]

is greater than one for relative motion and exactly one on the comoving
submanifold.  A Lorentz transformation changes components, not this invariant.

## 2. State carrier

`bianchi.q.electron.ColdElectronTestField` owns the instantaneous collision
input

```text
n_e_free       finite proper free-electron density in SI m^-3, >= 0
beta_normal    finite dimensionless v_physical/c, shape (3,), |beta| < 1
closure        independent | comoving-electron
c_m_s          explicit positive physical boundary constant
```

and permanently declares:

```text
cold_electrons          true
test_field              true
background_backreaction false
```

The stored four-velocity is

\[
U_e^A=\Gamma_e(1,\boldsymbol\beta_e),\qquad
u_e^A=cU_e^A,\qquad u_e^Au_{eA}=-c^2,
\]

with \(g=(-,+,+,+)\).  The project orientation remains
\(\epsilon_{123}=+1\); this adapter does not introduce a competing orientation
or Stokes convention.

`n_e_free` is a Lorentz scalar proper density in SI `m^-3`; this matches the
adapter's default `c` in `m/s`.  The legacy history/rate lane uses `cm^-3` and
must perform an explicit conversion if it is wired later.  The comoving constructor copies
only the fluid velocity; it does not infer density from \(\Omega\), an equation
of state, composition, or ionization fraction.  A time-dependent field must
arrive through a separately provenance-bound prescribed schedule.

At a vacuum stratum the A.4 quotient may forget the fluid-velocity
representative.  This module therefore requires the caller to supply
`beta_fluid` and does not manufacture a comoving representative.  The vacuum
choice (`n_e_free=0`, retained representative, or undefined H1) remains a
separate authority decision.

## 3. Exact frame map

Both stored velocities are relative to the same normal tetrad.  With

\[
L(\boldsymbol\beta)=
\begin{pmatrix}
\Gamma&-\Gamma\beta_j\\
-\Gamma\beta^i&
\delta^i{}_j+\dfrac{\Gamma-1}{\beta^2}\beta^i\beta_j
\end{pmatrix},
\]

the implemented maps are

\[
\boxed{\Lambda_{e\leftarrow f}
=L(\boldsymbol\beta_e)L(-\boldsymbol\beta_f)},\qquad
\boxed{\Lambda_{f\leftarrow e}=\Lambda_{e\leftarrow f}^{-1}}.
\]

For non-collinear velocities this ordered product carries a spatial/Wigner
rotation.  It must not be replaced by a single boost using
`beta_e - beta_fluid`.

The photon transformation reuses `bianchi.q.boost.doppler` twice.  For a pure
source-to-target boost it agrees with

\[
D=\Gamma(1-\boldsymbol\beta\!\cdot\mathbf e),\qquad
\epsilon'=D\epsilon.
\]

The polarization transformation reuses the basis-free canonical transported
screen map `bianchi.q.polstate.boost_shape` twice.  It transforms the normalized
coherency shape, while bolometric Mode-A amplitude and angular weight transform
separately:

\[
\widehat G'=D^4\widehat G,\qquad d\Omega'=D^{-2}d\Omega.
\]

This separation prevents a passing polarization-shape test from hiding a
missing intensity Doppler factor.

## 4. Implemented public seam

```python
from bianchi.q.electron import ElectronTestField

electrons = ElectronTestField.independent(
    n_e_free=2.5e6,
    beta_normal=[-0.04, 0.09, 0.02],
)

comoving = ElectronTestField.comoving(
    n_e_free=2.5e6,
    beta_fluid=fluid_beta,
)

E_e, e_e, D = electrons.fluid_to_electron_photon(E_f, e_f, fluid_beta)
J_e, e_e, D = electrons.fluid_to_electron_polarization(J_f, e_f, fluid_beta)
lw_e, lG_e, e_e, D = electrons.fluid_to_electron_mode_a(
    lw_f, lG_f, e_f, fluid_beta
)
```

Inverse methods are supplied for every carrier.  `authority_metadata()` makes
the no-backreaction, proper-density, receipt, and promotion boundaries machine
readable.

## 5. Reused internal authority

- `bianchi/q/boost.py`: exact finite Doppler/aberration and Mode-A scaling.
- `bianchi/q/polstate.py`: canonical transported-screen coherency map.
- `bianchi/q/polarization.py`: basis-free nine-component screen carrier.
- `audit/p9_boost_screen.py`: independent pure-boost screen isometry oracle.
- `bianchi/matter/collision_moving.py`: independent full-distribution photon
  boost and the direction-dependent relative-flux warning.
- `docs/Q-CONTRACT.md`: signature, time, opacity, and Q-layer conventions.
- `Low-ell Bianchi Einstein–Boltzmann Solver.txt`: requires an exact
  electron-frame Thomson authority path and rejects shortcut transformations.

Source archive:

```text
bianchireview87.tar-1-.gz
sha256 6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84
```

## 6. Verification gates closed here

- valid red before the public module existed;
- identical focused command green after implementation;
- independent vs comoving construction and strict domain rejection;
- explicit-\(c\) four-velocity normalization;
- exact comoving identity for photon, polarization, and Mode A;
- non-collinear Lorentz metric/inverse checks;
- photon positive energy, nullness, and round trip;
- coherency target-screen transversality, unit trace, PSD, and round trip;
- direct full-4-vector/screen oracle over hostile random boosts;
- old independent `p9_boost_screen` audit remains green.

## 7. Deliberately not implemented or promoted

- no electron Einstein source, recoil, heating, or backreaction;
- no recombination/reionization or composition mapping for `n_e_free`;
- no time-dependent schedule owner or provenance ledger;
- no direction-dependent normal-time collision generator
  \(n_e^\star\sigma_TcD\);
- no change to legacy `Collision.v_b`, Python/Rust step loops, or Rust ABI;
- no claim that a finite \(\ell_{max}=8\) carrier is closed under finite boosts;
- no arbitrary global-Stokes-basis Wigner phase API;
- no residual-\(U(1)\) quotient descent proof;
- no completion of OD001–OD004 or the nine-key OD002 receipt;
- no row-7/row-8, solver, runtime, release, branch, commit, or PR promotion.

The runtime relative-flux factor is intentionally a later gate.  Energy remap,
\(D^4\), \(D^{-2}\), and the collision-rate \(D\) must each be applied exactly
once; the present adapter closes the first three representation transforms but
does not silently claim the fourth.

## 8. Primary literature cross-check

- [Pitrou, exact tetrad boost, screen projector, and polarization frame law](https://arxiv.org/pdf/0809.3036)
- [Challinor, covariant polarized radiation under observer changes](https://arxiv.org/pdf/astro-ph/9911481)
- [Beneke–Fidler, separate electron density/temperature/velocity inputs](https://arxiv.org/pdf/1003.1834)
- [Takahashi et al., distinct charged-species velocities](https://arxiv.org/pdf/astro-ph/0502283)
