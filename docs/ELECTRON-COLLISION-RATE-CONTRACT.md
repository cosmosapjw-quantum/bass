# Electron collision-context rate and schedule contract

Status: `BOUNDED_IMPLEMENTATION — NOT PRODUCTION WIRED — NOT ROW PROMOTION`  
Date: 2026-08-23

## 1. Conventions and covariant authority

The metric is `(-,+,+,+)`, `c` is explicit, photon directions point along
propagation, and `n_e*` denotes the scalar electron-rest-frame proper density
in SI `m^-3`.  For a future-directed photon ray,

\[
d\tau_T=-\frac{n_e^\star\sigma_T}{c}\,u_{e a}\,dx^a.
\]

If `t_s` is the local ray time assigned by observer `s`,

\[
\frac{d\tau_T}{dt_s}
=n_e^\star\sigma_Tc\,D_{e\leftarrow s},\qquad
D_{e\leftarrow s}=\frac{E_e}{E_s}>0.
\]

`ElectronCollisionContext` exposes the source observer explicitly:

```text
rate_per_fluid_time_s(e_f, beta_f)       n_e* sigma_T c D_e<-f
rate_per_normal_time_s(e_n)              n_e* sigma_T c D_e<-n
rate_per_normal_hubble_time(e_n, H_n)    normal rate / H_n
```

This separation is mandatory.  Q defines its Hubble time from normal-
congruence physical time.  Therefore `fluid_rate/H_n` is wrong for a tilted
fluid.  Even when `u_e=u_f`, the fluid-time rate is isotropic while the
normal-time rate is generally direction dependent.  For
`beta_e=beta_f=0.6 xhat`, the normal-frame factors for parallel, head-on, and
transverse photons are exactly `0.5`, `2`, and `1.25`.

Primary authorities are Younsi–Wu–Fuerst Eqs. (11), (17), using the same
signature, and Challinor Eqs. (2.21), (3.7)–(3.10), (3.14), after converting
his opposite signature:

- https://arxiv.org/pdf/1207.4234
- https://arxiv.org/pdf/astro-ph/9911481
- https://arxiv.org/pdf/0809.3036

## 2. Exactly one relative-flux factor

The observer-ray rate contains one power of `D`.  It is distinct from the
representation factors `D^4` for bolometric intensity and `D^-2` for solid
angle.  Proper density is not boosted first:

\[
n_e^{(f)}=\Gamma_{ef}n_e^\star,
\]

so using `n_e^(f)` as `n_e*` and then multiplying by full `D` would duplicate
`Gamma`.  Likewise, `bianchi/matter/collision_moving.py` already applies
`lp/L=D` internally.  A future consumer of that kernel must pass the rest
opacity `n_e* sigma_T c`, not the new observer-ray rate, or it will create
`D^2`.

Backward integration does not make the local rate negative.  Integration
orientation belongs to the caller; this module returns a positive future-ray
rate only.

## 3. SI/cgs boundary

The only cross-section authority remains
`bianchi.thermo.history_api.SIGMA_T_CM2`:

```text
sigma_T = 6.6524587e-25 cm^2 = 6.6524587e-29 m^2
c       = 2.99792458e10 cm/s = 299792458 m/s
```

`density_cm3_to_m3` and `density_m3_to_cm3` convert an electron **proper**
density only.  `x_e n_H` from the legacy ionization history is a fluid/baryon-
frame density and is not automatically a generic-H2 proper density.  Automatic
legacy-history adaptation is therefore explicitly false.  The comoving lane
may use the same numerical density after the explicit unit conversion because
the electron and fluid frames coincide.

## 4. Prescribed schedules

Every schedule requires:

```text
source_id       non-empty locator
source_sha256   lowercase 64-hex source digest
payload_sha256  computed from canonical arrays and frozen semantics
support         closed finite tau interval; no extrapolation or clamp
```

`PrescribedIndependentElectronSchedule` interpolates the tetrad number current

\[
N_e^A=n_e^\star U_e^A
\]

linearly in Q Hubble time `tau`, with all components declared in the supplied
normal-tetrad gauge.  Exact-vacuum velocity representatives are zeroed before
current construction and payload hashing.  Positive interpolated currents are
reconstructed using the stable norm

\[
n_e^\star=\sqrt{(N^0-|\mathbf N|)(N^0+|\mathbf N|)}.
\]

This interpolation preserves the future timelike cone but is a modeling
choice, not linear proper-density interpolation.  Equal endpoint densities
with velocities `+0.8 xhat` and `-0.8 xhat` produce midpoint density
`(5/3)n_endpoint`.  The contract is tied to the declared normal-tetrad gauge;
it is not residual-`U(1)` descended and carries no AD/JVP claim.

`PrescribedComovingElectronSchedule` interpolates density only.  At every
positive-density query it receives the live fluid beta and constructs
`u_e=u_fluid` exactly; it never interpolates an independent electron beta.  At
exact vacuum the equality constraint is vacuous and the schedule returns the
canonical zero-current representative.

## 5. Vacuum and validity boundary

At `n_e*=0`, both observer rates are bit-exact positive zero for every valid
velocity representative and photon direction.  Requesting a standalone
electron Doppler factor raises `VacuumElectronFrameError`, since that factor is
not a physical collision observable on the velocity quotient.

The state is cold, but the spectral validity gate is not closed:

```text
DECLARED_COLD_THOMSON_ASSUMPTION / ENERGY_DOMAIN_UNVERIFIED
```

Recoil corrections scale with electron-frame photon energy
`E_e/(m_e c^2)=D E_source/(m_e c^2)`.  Mode A has no spectral upper-bound
provenance, so this module cannot certify the Thomson domain or exclude
Klein–Nishina corrections at runtime.  That requires a separate
provenance-bound `E_max` and tolerance authority.

## 6. Deliberate stop boundary

Implemented here:

- fluid- and normal-observer relative-flux rates;
- normal-Hubble-time normalization;
- exact comoving and vacuum limits;
- independent current schedule and live-fluid comoving schedule;
- strict provenance/support and SI/proper-cgs conversion;
- machine-readable non-promotion and validity status.

Not implemented or promoted:

- `Collision.v_b`, Q step loops, Rust ABI, or collision exponential wiring;
- automatic `x_e n_H` adaptation to generic H2;
- finite-ell boost closure or residual-`U(1)` quotient descent;
- spectral `E_max`/Klein–Nishina validity predicate;
- electron recoil, temperature, backreaction, or composition dynamics;
- authority row, solver, runtime, release, branch, commit, or PR promotion.

