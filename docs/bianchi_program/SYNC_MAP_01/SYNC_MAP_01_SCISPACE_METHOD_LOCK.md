# SYNC-MAP-01 SciSpace methodology lock

**Search question:** Which peer-reviewed methods support single ownership,
machine-readable provenance, exact semantic identifiers and independently
replayable derivations across coupled scientific-software repositories?

## Admitted methodological references

1. A. M. Ellison, E. R. Boose, B. S. Lerner, E. Fong and M. Seltzer,
   “The End-to-End Provenance Project,” *Patterns* **1** (2020) 100016,
   DOI `10.1016/j.patter.2020.100016`.

   Admitted use: computational provenance should be machine-readable and bind
   inputs, transformations and outputs so analyses can be reproduced and
   scientific conclusions validated.

2. J. Mwebaze, D. Boxhoorn and E. A. Valentijn,
   “Astro-WISE: Tracing and Using Lineage for Scientific Data Processing,”
   NBIS 2009, DOI `10.1109/NBIS.2009.48`.

   Admitted use: backward lineage over changing distributed scientific data
   supports reuse, reprocessing and explicit dependency reconstruction.

3. R. Di Cosmo and S. Zacchiroli,
   “The Software Heritage Open Science Ecosystem,” arXiv:`2310.10295`.

   Admitted use: source history and immutable software objects can be arranged
   as a Merkle DAG and referenced through persistent identifiers rather than
   copied into every consumer.

4. S. Casas and C. Fidler,
   “TOPO: Time-Ordered Provable Outputs,” arXiv:`2411.00072`.

   Admitted use: deterministic cryptographic fingerprints and ordered output
   records are useful integrity controls in astrophysical computation.

## Scope firewall

These references justify provenance, lineage and integrity architecture only.
They do not determine:

- the BASS/REC/REI formula owner for a scientific expression;
- semantic equivalence of any two formulas;
- Bianchi sign, frame or screen conventions;
- the REC physical face;
- the REI first canonical interval;
- provider compatibility or a scientific claim.

The owner and equivalence decisions remain project-owned, exact-lineage,
formula-level tasks under `SYNC-MAP-02` and later review.
