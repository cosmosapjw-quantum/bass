# BASS-8B control-path reconciliation

**Date:** 2026-08-23  
**Decision class:** bounded DAG-seam adjudication / BASS-8B.2A preflight  
**Decision:** `CRITICAL_PATH_NEXT_BASS_8B_2A__E5_DEFERRED_RATE_SUBNODE`  
**Execution status:** `PASS_DECISION_ONLY__NO_AUTHORITY_ROW_PROMOTION`

## 1. Conflict reconciled

Two durable records named different next actions:

1. E4 named `BASS-8B.1E.5`, a direction-dependent local Q-time Thomson-rate
   binding;
2. BASS-8B.1 named `BASS-8B.2A` typed electron-state binding, followed by
   `BASS-8B.2B` finite carrier/projector/left-functional work.

These tasks are not mutually exclusive. They close different contracts.

## 2. Exact dependency distinction

Write the collision action schematically as

\[
C(\tau,\mathbf n)=\nu_\tau(\tau,\mathbf n)\,\widehat C[\beta_e(\tau)],
\]

where `nu_tau` is a nonnegative scalar local rate and `Chat` is the collision
shape obtained from the electron-frame rest operator and frame map.

For `nu_tau != 0`, scalar multiplication leaves the right kernel, left kernel,
rank, nullity, equilibrium carrier, and normalized rank-one projector unchanged.
At `nu_tau=0`, the entire carrier becomes a collision kernel, so the collision-off
slice cannot identify or close the nontrivial projector/left-functional authority.
The Kato connection `K=[Pdot,P]` depends on the state dependence of `P`, not on
an overall scalar rate multiplying `Chat`.

Therefore:

- E5 is required for a complete direction-dependent collision generator and
  optical-depth owner;
- E5 is **not** a prerequisite for defining rows 7–8 projector and paired-left
  authority;
- E5 cannot by itself unblock BASS-3 or Join J1.

## 3. Existing E1–E4 evidence admitted into BASS-8B.2A

The existing bounded Python authority already supplies substantial 2A input:

- independent cold-electron proper density and general three-velocity;
- an exact comoving velocity restriction as a separate constructor;
- proper-density and relative-flux/rate conventions;
- prescribed independent number-current and comoving-density schedules;
- a provenance-bound Q-Hubble-time coordinate and finite trajectory support;
- fail-closed timelike/subluminal checks and vacuum velocity quotient;
- explicit separation from production runtime and local observer/output boosts.

This evidence is reusable but does not close 2A.

## 4. Remaining BASS-8B.2A gaps

### 4.1 Missing discriminated authority union

The current E1–E4 classes do not yet provide the exact decision-level union

```text
IndependentElectronState(...)
ComovingWithMatterSpecies(species_id, plasma_identity, equality_proof, ...)
CollisionOff(reason, kappa=0)
```

The present comoving constructor copies a supplied fluid velocity, but it does
not bind an explicit ionized-baryon/electron-plasma species identity and proof
object. Vacuum is handled as a quotient/collision-off behavior but not as an
explicit typed decision state with a reason and exact-zero opacity contract.

### 4.2 Missing state jet / derivative authority

The independent schedule interpolates the electron number current linearly,
but its metadata explicitly records `ad_jvp_certified = false`. No public exact
state-jet contract currently supplies derivatives sufficient for `Pdot`.

For an open schedule segment with affine number current

\[
N^A(\tau)=N_i^A+s(\tau)(N_{i+1}^A-N_i^A),
\]

an admissible exact segment jet is

\[
\dot N^A=\frac{N_{i+1}^A-N_i^A}{\tau_{i+1}-\tau_i},
\quad
n_e=\sqrt{(N^0)^2-\mathbf N^2},
\]

\[
\dot n_e=\frac{N^0\dot N^0-\mathbf N\cdot\dot{\mathbf N}}{n_e},
\qquad
\dot\beta_e^i=\frac{\dot N^iN^0-N^i\dot N^0}{(N^0)^2}.
\]

This is valid only on a proven future-timelike non-vacuum segment. At knots the
left and right derivatives generally differ; the authority must require an event
split and an explicit side rather than inventing a central derivative. At exact
vacuum the electron frame is quotiented and projector derivatives are not
identified by the collision-off state.

For a comoving species, `beta_e=beta_species` and its derivative must come from
an exact live-species/background derivative authority together with the species
identity/equality proof.

## 5. Adjudicated ordering

```text
BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING          CRITICAL PATH / NEXT
  -> BASS-8B.2B_FINITE_CARRIER_PROJECTOR_LEFT_FUNCTIONAL
  -> BASS-8B.3_ROWS7_8_READJUDICATION

BASS-8B.1E.5_DIRECTION_DEPENDENT_LOCAL_RATE      SIDE SUBNODE
```

E5 may run after 2A or in parallel with 2B if resources permit, but its result
must remain classified as collision-rate ownership, not projector closure. It
becomes mandatory before any complete direction-dependent collision generator,
optical-depth integration, or production collision path is claimed.

## 6. Minimal BASS-8B.2A implementation contract

1. Add one discriminated binding type with the three decision branches.
2. Reuse the existing independent/current and comoving/density schedule owners;
   do not rewrite their interpolation semantics.
3. Add a provenance-bound `ElectronStateJet` returning
   `(n_e, beta_e, dn_e/dtau, dbeta_e/dtau, segment, side_policy)`.
4. Fail closed at vacuum, null/spacelike current, support escape, unbound species,
   and an interior knot without an explicit side.
5. Require a named plasma identity plus equality-proof hashes before constructing
   `ComovingWithMatterSpecies`.
6. Keep rate binding, finite carrier, projector, JAX/Rust, production wiring, and
   VI0 classifier out of the 2A patch.
7. Set `ad_jvp_certified=true` only for the exact declared segment-jet contract,
   not for generic AD or solver-wide JVP.

## 7. Required tests

- independent constant-current zero jet;
- generic affine timelike current against exact formulas;
- future-timelike and subluminal domain failure;
- exact vacuum -> typed `CollisionOff`, no retained velocity representative;
- left/right knot derivatives and unspecified-knot rejection;
- support escape rejection;
- comoving species identity/equality proof required;
- generic-fluid or observer-boost substitution rejected;
- proper spatial-rotation covariance of the state jet;
- Type-II aligned trajectory admitted only as a restriction of the generic
  three-vector schema;
- scalar-rate mutation shown not to alter the nonzero-rate kernel/projector;
- zero-rate mutation shown to destroy projector identifiability.

## 8. Hard boundaries

```text
rows 7–8              BLOCKED
BASS-3 classifier      DO_NOT_START
solver/runtime         DO_NOT_START
production path        DO_NOT_START
new scientific PR      DO_NOT_OPEN
Join J1                BLOCKED
```
