# SYNC-MAP-02C Plot-Driven CRAG Audit

**Status:** `SURVIVING_CLASSIFICATION / NARROWED_TRANSPORT_CLAIM`  
**Python plot status:** `NOT_RUN_ENVIRONMENT_CLIENT_ERROR`  
**Fallback evidence:** Wolfram-generated displays plus deterministic source-bound SVG/CSV artifacts  
**Claim effect:** `NONE`

## Generated evidence

1. `REI_RELATION_CLASS_COUNTS.csv`
2. `REI_RELATION_CLASS_COUNTS.svg`
3. `REI_IMPACT_DAG_FIX2.svg`
4. connected-Wolfram relation-class bar chart
5. connected-Wolfram layered DAG view

The inability to execute Python in this runtime is retained as an environment gap. The charts are not described as Python-generated.

## Direct plot reading

### Relation-class plot

The dominant bar is `OWNED_EXTENSION = 5`. Two smaller bars have count two: exact external artifact imports and adapter specializations. The FLRW control and feasibility gate each have count one. The chart therefore supports an ownership statement: most inspected active relations are REI-owned microphysics/closure relations.

It does **not** support an implementation-maturity statement. Five owned relations do not imply a Bianchi background, angular transport closure, canonical interval or provider.

### Corrected impact-DAG plot

The plot has two noninterchangeable upstream lanes:

```text
formula / transport:
BASS energy drift + direction flow
  -> shared FormulaIR export

background / artifact:
BASS BG-02
  -> background provider schema + exact lock
  -> REI numerical background lock
```

They converge only at `REI.ANISOTROPIC_GROUP_REDSHIFT_CLOSURE`. Independent runtime-bridge and capacity gates also enter before the first canonical interval. The visual therefore rejects the older coarse idea that a scalar BASS `H` pin alone could close REI Bianchi transport.

## CRAG

### C — Correctness

- Bar heights reproduce the exact class counts `2,1,2,5,1`.
- The DAG is acyclic and preserves provider-after-interval ordering.
- Formula export and numerical background admission are visibly distinct.
- The H-only control is not drawn as the anisotropic closure.

Verdict: `PASS`.

### R — Retrieval

- Exact REI source states that no numerical BASS lock is implemented.
- Exact REI source states that no Bianchi geometry is implemented in the FLRW control stage.
- The BASS photon formula authority contains direction-dependent energy drift.
- The inspected microphysics paths contain the classified H/He, transmission, allocation and capacity relations.

Verdict: `PASS_WITH_BOUNDED_SOURCE_SCOPE`.

### A — Augmented checks

1. **Radiation-term augmentation.** Adding an `Omega_r a^-4` background term changes the FLRW control but not ownership; the active code omits it.
2. **Angular-isotropy mutation.** Setting every radiation multipole above the monopole to zero removes the shear average exactly.
3. **Quadrupole mutation.** A nonzero STF quadrupole produces `2 sigma_ab Q^ab/15`, invalidating generic H-only redshift.
4. **HeIII charge mutation.** Replacing `2 x_HeIII` by `x_HeIII` leaves residual `n_He x_HeIII` and is detected.
5. **Opacity-residual mutation.** Treating the signed unattributed residual as a nonnegative extinction coefficient violates the source contract.
6. **Gate bypass mutation.** Connecting provider export without the first interval violates the DAG.

Verdict: `PASS`; the generic group-transport claim is narrowed.

### G — Generation / predictions

The corrected graph predicts the next evidence required:

- shared FormulaIR records for energy drift and direction flow;
- a BASS background-provider schema and exact numerical lock;
- an REI angular hierarchy or declared moment closure;
- convergence and residual evidence showing that the closure does not hide quadrupole/shear transport;
- only then a BASS-coupled first interval.

These are testable predictions, not completed work.

## Figure-hostile check

| Risk | Severity | Repair |
| --- | --- | --- |
| count-five bar may be read as 5/11 solver completion | P2 | subtitle and caption state ownership-only interpretation |
| formula and artifact lanes may look sequential rather than parallel | P2 | separate vertical lanes and convergence node retained |
| blocked nodes may be read as implemented grey boxes | P2 | labels explicitly say `not implemented` or `blocked` |
| dashed runtime/capacity nodes may be missed at small print size | P3 | keep double-column use or split the graph for single-column print |

At single-column width, the impact DAG should be split into formula and background panels. At double-column width, the current SVG is legible.

## Adversarial claim disposition

### Surviving

- active REI relations are classified with bounded exact-source provenance;
- no active BASS geometry duplicate authority was detected;
- REI microphysics ownership is distinct from BASS geometry/background ownership;
- the four shared BASS frame/photon Formula IDs remain the correct formula-export set.

### Narrowed

- `REI.REL.GROUP_REDSHIFT_FLOW.001` is an FLRW/isotropic-angular adapter, not generic Bianchi group transport;
- a BASS scalar background value alone is insufficient;
- `SYNC-MAP-02C` opens both a formula-export lane and a separate background/closure lane.

### Rejected

- REI already implements Bianchi reionization transport;
- a numerical BASS background lock exists;
- the current H-only group path is valid for arbitrary anisotropic radiation;
- relation ownership counts measure solver completeness;
- provider or science promotion follows from this stage.

## Final CRAG verdict

```text
SURVIVING CLAIM:
active-lineage relation ownership and dependency classification

NARROWED CLAIM:
current group-redshift implementation is FLRW/isotropic-subspace only

REJECTED CLAIM:
generic Bianchi REI transport or provider readiness
```
