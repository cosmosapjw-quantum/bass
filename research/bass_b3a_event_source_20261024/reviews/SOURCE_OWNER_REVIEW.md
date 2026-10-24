# REC source-owner intake for BASS B3a

Date: 2026-10-24. Reviewer: /root/source_owner_intake.
Method: read current GitHub PR metadata, full tree metadata and selected source/contract text;
hash local source copies against the repository Git blob identities. No source computation,
test campaign, IVP, provider archive download, remote mutation or physical promotion was performed.

## Decision

**PASS_SCOPED for a read-only, source-only connection to the declared REC LINE01
effective escaping-line model.** Choose the current REC PR130 tree as the immutable
container of the donor. Keep the LINE01 owner ID and its detached semantics.
The source provides separate nonnegative effective escaped emission and absorption
channels, a common physical frame/clock, the angular law and an explicit atomic
excitation-energy counterpart. This supplies enough information for an instantaneous
BASS event-measure adapter and its new small fixtures.

**Native coupled exchange / stock advancement remains HOLD.** The completed native
LINE02 and REC-HISTORY operators have distinct conventions and owners. Their signed
net ledgers must not be relabelled as a gross emission law. The selected LINE01 model
assumes an imposed blue radiation boundary; it does not supply a finite photon stock
or a self-consistent thermal/radiation evolution. Missing stock admission must produce
a refusal, not clipping or an invented emitter reservoir.

## Current identity and bounded survey

- Repository: cosmosapjw-quantum/rec_bianchi.
- Live PR130: Draft/open/unmerged; branch research/rec-history-boundary-20261023;
  HEAD `93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa`.
- PR129 native owner: `a7c46fd8338971e2cefa776f5dd7b25a46974990`, included in PR130 ancestry.
- Parent central authority: rei_bianchi `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`.
- Root REC AGENTS.md returned 404 at the live owner HEAD. The complete recursive tree
  was not truncated; its only AGENTS.md files are archived upstream-vendor copies in
  docs/rec_research/REC-PB02-20261004/survey/atomic/sources/, not ancestors of this lane.
- Bounded current survey inspected the most recently updated 12 open REC PRs and 12
  open HE PRs. HE has a newer PR93 source intake at
  `15053fe4445a32e0544d644e864fe27780d08743`, based on provider PR92
  `0a11bf9e1f6ffcc696625de0caf1c581c27cf7f0`.
  No HE empirical angular admission is inferred. REC was selected for the photon connection.
- This is not a census of all repositories, branches or backups.

## Contract established from actual source

| Field | Current donor fact | Adapter treatment |
|---|---|---|
| Physical model | One unpolarized effective coincident Lyα two-level model, quasi-stationary Sobolev transfer, statistical 1:2 sublevels and common frequency/profile/incident occupation for collapsed 2p | Preserve `H_LYA_EFFECTIVE_2P`, `collapsed_2p` and all closure labels |
| Units | SI proper densities m^-3; A,H in s^-1; energy J; angular law normalized by dΩ/(4π) | No comoving-density or ln(a)-rate substitution |
| Frame | Matter-comoving orthonormal frame, non-tilted homogeneous expanding flow | Require explicit source-frame/observer IDs; boost photon four-momenta while retaining invariant event weights |
| Clock | Proper time in seconds in that frame; local physical-volume rates | dR is per proper volume × proper time, equivalently a scalar four-volume event intensity up to the fixed c convention |
| Energy per photon | E21=10.198714553953742 eV, converted by exact EV_J; line frequency/wavelength also retained | Use the same energy in photon and atomic-internal charges |
| Downward channel | `A B n_u(1+f_plus)` | Nonnegative effective escaping emission, with stimulated part |
| Upward channel | `A B g n_l f_plus` | Separate nonnegative effective absorption; not a negative photon birth weight |
| Net rate | R=down−up, stable population defect D used by upstream | Combine only after both channel measures have been formed; scale comparisons by gross terms near balance |
| Angular law | q(n)=1+nᵀSn>0; t=A λ³(g n_l−n_u)/(8πH); βesc=(1−exp(−t/q))/(t/q) | Preserve all angular packets. B and Q alone do not determine boosted pressure rate |
| Partner | upper loss −R, lower gain +R; atomic internal energy −E R | Real donor is atomic excitation energy. No generic invented reservoir |
| Thermal/ionic terms | heat=0, free-electron yield=0, ionic yield=0 in the narrow-line recoil-free model | Do not assign line energy to gas heating or H/He ionization |
| Ownership | `standalone_detached`, `native_line_owner_active=False` enforced by source | Never append this source to active native Lyα |
| Validity | Δ=g n_l−n_u>0, n_l,n_u,f_plus≥0, H>0, qmin above frozen zero-speed band | Reject outside domain; no positivity repair |
| Missing coupling inputs | finite incoming photon inventory, accepted population transaction, evolving spectrum/history and source uncertainty calibration | Instantaneous outputs only; stock update HOLD |

The explicit nonnegative channels in the donor THEORY §2 are **effective reservoir
channels after eliminating resonance radiation**. They are not the full microscopic
counts of all trapped absorptions and reemissions at the profile-averaged occupation.
This distinction is part of the source contract, not a reason to discard the
well-defined escaping exchange.

## Exact formula-to-code connection

For a normalized angular quadrature `(n_i,a_i)`, sum a_i=1, define

```
b_i = beta_vector(t, 1 + n_i @ S @ n_i)
r_down_i = a_i * A * n_u * (1+f_plus) * b_i
r_up_i   = a_i * A * g * n_l * f_plus * b_i
p_i      = (E/c) * (1,n_i)
dR_net   = dR_down - dR_up
```

Apply the B3a event kernel separately to down/up with the same frame and clock.
Subtract their four-force and observer-dependent pressure-rate outputs.
In the donor rest frame the law is even, hence odd momentum is zero. The inherited
energy partner gives `Q_atomic=-Q_photon` at the instantaneous exchange interface.
It is not a claim that a finite-time atomic/photon transaction has been accepted.

The BASS normalization can then consume the net outputs:

```
U = kappa L^3 E_dot / c
J = kappa L^3 force_density
PiRate_hat = kappa L^3 PiRate_phys / c
```

The upstream `energy_PSTF_J_m3_s` or `radiation_spatial_injection_J_m3_s` are rates.
They must not be assigned directly to BASS's stored `Source.pi` stress.

## Minimal callable donor tree

Retain the paths relative to one LINE01 donor root:

```
code/line_source.py
code/escape_moments.py
vendor/hyrec_spike_transfer.py
vendor/rec_license.md
```

Dependencies: Python, NumPy, SciPy (`line_source.py` imports `scipy.optimize.brentq`
at module import even when only `exchange_source` is called). Add the donor
`code/` directory to sys.path, then import `line_source`; its angular module
finds `../vendor/hyrec_spike_transfer.py` relative to its own file.
Check immutable file hashes before importing.

`LineState(...)` with explicit source/angular provenance and
`exchange_source(state,n_mu=...,n_phi=...)` form the source API.
A new manufactured small LineState fixture is preferable for the adapter test.
It must be labelled manufactured, not a newly evaluated native saved state.
`native_snapshot_state` requires the separate 141089-byte snapshot CSV and is
not required for this new narrow unit.

### Critical quadrature detail

`escape_moments._principal_rule(n_mu,n_phi)` returns **squared** direction
components in one octant, together with weights that already represent the eight
reflection-equivalent octants for an even unboosted integrand. Its returned
`n2` is not a unit-vector packet list. Construct all eight signs of
`sqrt(n2)`, rotate by the eigenvectors from `validate_inputs`, and assign
weight/8 to each sign. This recovers the actual conditional angular distribution.

The denominator in the B3a observer-dependent kernel depends on β·n. Applying
the boost to a single unsigned octant, or boosting only upstream B and Q,
would use an incorrect event distribution. A full-sphere quadrature following
the donor's `lab_frame_oracle` is an alternative, but the octant reconstruction
reuses the upstream rule exactly.

The source validator projects S only inside its explicit 64-epsilon symmetry/
trace roundoff band and reports that correction; this is upstream tensor
representation handling. It does not clip populations, event rates or q to
force positivity.

## Native owner comparison and reusable saved evidence

The current native/history path has this API:

`history_boundary.line_ledger(d_in,xr_p,x1s,tau,nH_cm3,H,q=1,owner="boundary",
reference_occupation=0)`.

It evaluates `R=G_NATIVE H q (d_out-d_in)`, with
`G_NATIVE=3*1e6*LYA_FACT` and preserves the native constant convention.
It returns radiation `+E21_J R`, atomic internal `−E21_J R`,
`occupation_is_boundary_encoding=True`, `extra_radiation_source=0`.
Outgoing history is the same radiation event representation and cannot be
credited a second time. The interface returns a signed net boundary flux,
not uniquely determined gross trapped microscopic event counts.

Native LINE02's stored `ANGULAR_LEDGER.csv` at the current HEAD contains:

| Saved row | R [m^-3 s^-1] | radiation [J m^-3 s^-1] | atomic internal [J m^-3 s^-1] |
|---|---:|---:|---:|
| native_iso | 1.3726872952767989e-08 | 2.242990553943301e-26 | −2.242990553943301e-26 |

These values were read from the existing CSV, not recomputed. The scalar native
snapshot records that its directional angular distribution is NOT_STORED.
The triaxial/rotated entries use supplied angular fixtures. The LINE01
full-Planck/stimulated effective operator differs from native LINE02's
Wien/ground-state-opacity convention, as proved explicitly in LINE02 THEORY §8.
The new connection must retain LINE01's name and model boundary.

## Byte identity and provenance

`SOURCE_OWNER_INTAKE.json` records each read source path, immutable commit,
upstream Git blob and local SHA256/size. The first local text serialization
added an extra trailing newline to 13 files. The current-turn hash check
found every mismatch; removal of exactly that serialization newline restored
all 13 original Git blobs. The failed initial check and repair are retained
in `BYTE_IDENTITY_REPAIR.json`. This was an intake serialization issue,
not a change to upstream physics or evidence.

Two additional minimal donor files (spike transfer and license) were subsequently
saved without the added newline and checked against their Git blob pins.

## Remaining gates and exact next action

1. Implement the read-only LINE01 event packet adapter with separate down/up,
   explicit source/observer frame and proper-clock metadata; preserve donor bytes.
2. Test only the new adapter's small source fixture, zero-transfer case, sign
   separation, eight-octant reconstruction and gross-scaled parity against
   upstream rate/moment outputs. These are new B3a tests, not replay of old REC suites.
3. Reject stock advancement unless a current accepted photon/atomic population
   transaction is provided; no positivity clipping.
4. Keep native/history integration and B3b finite physical exchange at their
   existing gates. Actual angular history, source uncertainty, population
   feedback and finite-stock positivity remain source-owner obligations.

Scientific source-intake verdict: PASS_SCOPED for the selected conditional
detached owner. Coupled admission: NOT_ISSUED. Provider publication/backup:
not performed by this reviewer. Existing BASS remaining campaign budget=null,
budget_reset=false is unchanged.
