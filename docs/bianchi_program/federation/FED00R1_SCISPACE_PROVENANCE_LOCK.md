# FED-00R1 SciSpace provenance methodology lock

**Stage:** `FED-00R1_CONTROL_LINE_DONOR_RECONCILIATION`  
**Status:** `METHODOLOGY_LOCK_ONLY / NOT_PHYSICS_AUTHORITY`

## Purpose

This lock records external methodology supporting formula-level ownership,
replay provenance and interoperable workflow receipts. It does not determine
BASS signs, Bianchi branch predicates, REC atomic physics, REI thermochemistry,
or any scientific claim.

## Admitted methodology references

### Yuan et al., *Utilizing Provenance in Reusable Research Objects* (2018)

DOI: `10.3390/informatics5010014`

Admitted use:

- provenance should support exact reference replay;
- a research object may be reused wholly, partially or in modified form;
- a summary graph may group detailed execution traces without replacing them.

Federation interpretation:

- GitHub exact objects are the detailed authority record;
- Dropbox reconstruction packets are durable replay objects;
- Atlassian is a summary/projection graph and must not replace formula truth.

### Khan et al., *Sharing interoperable workflow provenance: A review of best practices and their practical application in CWLProv* (2019)

DOI: `10.1093/gigascience/giz095`

Admitted use:

- hierarchical provenance should bind workflow, inputs, outputs and execution;
- interoperable provenance should use explicit relations rather than narrative similarity;
- a workflow-centric research object supports inspection and re-execution.

Federation interpretation:

- formula owner, consumer, adapter, oracle and audit roles are explicit edges;
- a consumer replay cannot self-promote to independent authority;
- cross-repository imports require immutable source identities.

### Leo et al., *Recording provenance of workflow runs with RO-Crate* (2023/2024)

Identifier: arXiv preprint on Workflow Run RO-Crate profiles.

Admitted use:

- run provenance may be packaged in interoperable profiles aligned with W3C PROV;
- prospective workflow description and retrospective run evidence must be distinguished.

Federation interpretation:

- formula-family registry and proposed DAG are prospective contracts;
- Wolfram, CI and restored-replay receipts are retrospective evidence;
- one must not infer execution PASS from a registry entry.

### Dhruv et al., *Managing Software Provenance to Enhance Reproducibility in Computational Science and Engineering* (2023)

Venue: *Computing in Science & Engineering*.

Admitted use:

- reproducibility depends on execution environment and software provenance;
- traceability must include the environment, not only source labels.

Federation interpretation:

- Wolfram version, xAct version where applicable, system ID, exact source blobs
  and backup reconstruction identities remain part of every durable receipt.

## Rejected uses

These papers do not authorize:

- automatic resolution of a physics-semantic conflict;
- replacement of theorem proofs by provenance metadata;
- scientific promotion from graph consistency;
- silent equivalence between different frames, units or approximation regimes;
- treating Confluence or Dropbox as the formula source of truth.

## Stage conclusion

The literature supports a three-surface architecture:

```text
GitHub exact authority
  -> Dropbox durable replay object
  -> Atlassian summary/DAG projection
```

with explicit prospective and retrospective provenance. The current
24-family graph remains a proposal until source-level semantic mapping and
owner review are complete.
