# SciSpace literature lock — R6 authority hardening

## Search question

What evidence is required in kinetic-transport software to bind an integrated source witness to a particular moment map or radial-weight family rather than reuse it across inequivalent moment systems?

## Retrieved methodological anchors

### Pichard (2022)

**A moment closure based on a projection on the boundary of the realizability domain: Extension and analysis**  
Kinetic and Related Models  
DOI `10.3934/krm.2022014`

The paper constructs a specific closure from the geometry of a specific moment set and studies the resulting system. Its relevance here is negative and methodological: a moment-source relation belongs to a declared moment map; it is not representation-free metadata.

### Laiu, Hauck, McClarren, O'Leary and Tits (2016)

**Positive Filtered P_N Moment Closures for Linear Kinetic Equations**  
SIAM Journal on Numerical Analysis  
DOI `10.1137/15M1052871`

The work distinguishes kinetic positivity from a finite harmonic approximation and enforces positivity through an explicit constrained reconstruction. It supports the rule that a property of an underlying distribution does not automatically descend to every finite moment representation without a named map and condition.

### Pichard (2023)

**Some recent advances on the method of moments in kinetic theory**  
ESAIM Proceedings and Surveys  
DOI `10.1051/proc/202375086`

The review identifies realizability, hyperbolicity and entropy dissipation as properties that a chosen moment system and closure must establish. It supports keeping the source projection, realizability domain and numerical state type together.

### Schäfer (2025)

**Maximum likelihood discretization of the transport equation**  
DOI `10.48550/arxiv.2505.10713`

The paper interprets Galerkin discretization as an inference/moment procedure and replaces it with a Fisher-Rao construction to protect positivity. Its relevance is that the projection metric and retained data are part of the discretization contract rather than incidental labels.

## Consequences for R6

1. `SOURCE_INTEGRATED_WITNESS` is not sufficient authority by itself.
2. An integrated witness must bind the exact target state, moment map and radial-weight family.
3. Positivity of the full distribution does not validate an arbitrary finite moment source update.
4. The source receiving type should reject underdetermined representation pairings before solver execution.
5. Entropy or realizability constructions may motivate later closures, but they do not authorize one implicitly.

## Relation to the attached TEFF papers

Paper I proves that radial spectral and angular information losses are independent resources. Paper II explicitly treats number-energy and velocity-dressed moment maps as specified kinematic coarse grainings and warns that its charts are not time-evolution solvers. Those project papers therefore support the same firewall: each integrated witness belongs to one declared information map.

## Authority boundary

```text
LITERATURE_SUPPORTS_TYPED_MOMENT_MAP_AND_REALIZABILITY_CONTRACTS
LITERATURE_DOES_NOT_DEFINE_BASS_HASHES_UNITS_OR_ADMISSION
AUTHORITY_EFFECT_NONE
```
