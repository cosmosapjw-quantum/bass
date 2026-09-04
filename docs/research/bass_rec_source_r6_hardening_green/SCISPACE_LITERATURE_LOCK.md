# SciSpace literature lock — R6 authority hardening GREEN

## Search question

How do rigorous kinetic or radiative-transfer moment methods bind source terms
to a specific moment map, statistics class, and realizability closure, and what
validation distinguishes a full-distribution source from a reduced-moment
source?

## Relevant results

### Pichard (2020)

**A moment closure based on a projection on the boundary of the realizability
domain: 1D case**  
*Kinetic and Related Models*  
DOI `10.3934/KRM.2020045`

The closure is constructed by reconstructing an underlying kinetic distribution
from a declared vector of moments and then evaluating the missing closure from
that reconstruction.  This supports explicit ownership by one moment map; it
does not support a representation-free integrated witness.

### Pichard (2022)

**A moment closure based on a projection on the boundary of the realizability
domain: Extension and analysis**  
*Kinetic and Related Models*  
DOI `10.3934/krm.2022014`

The extension analyzes the geometry of the chosen moment set and boundary
representation.  It reinforces that the admissible reduced state and its source
or closure are defined relative to a specific moment system.

### Abdelmalik, Cai and Pichard (2023)

**Moment methods for the radiative transfer equation based on
phi-divergences**  
*Computer Methods in Applied Mechanics and Engineering*  
DOI `10.1016/j.cma.2023.116454`

The paper begins from an explicitly chosen angular moment extraction, notes that
the resulting system is underdetermined without closure, and validates entropy,
equilibrium and symmetry properties using an exact quadrature suited to that
representation.  This supports separate projection, closure and discrete
validation contracts.

### Chan (2011)

**A class of physically motivated closures for radiation hydrodynamics**  
*The Astrophysical Journal* 727, 67  
DOI `10.1088/0004-637X/727/2/67`

The paper emphasizes that low-order radiation moments depend on omitted higher
moments and that a closure selects additional physical structure.  It is a
methodological warning against treating an integrated source number as if it
were the original kinetic source.

## Consequences for R6

The literature supports the following architecture:

```text
full kinetic source
  + declared projection/moment map
  + realizability or closure assumptions
  + representation-specific validation
  -> reduced source
```

It does not support:

```text
untyped integrated scalar
  -> interchangeable source for every reduced state
```

The R6 `IntegratedMomentMapBinding` is therefore methodologically appropriate:
it records the target state, moment map, radial-weight family and source
identity before any reduced source is admitted.

The papers do not determine BASS conventions, photon source coefficients,
binary64 policy, SHA-256 schemas, test counts, branch identities, solver
admission, or physical claims.

```text
LITERATURE_ROLE = METHODOLOGY_AND_REGRESSION_ONLY
AUTHORITY_EFFECT = NONE
```
