# BASS ↔ REI IGM mission realignment (2026-11-01)

## Decision and owners

**North star:** the physical, source-owned Bianchi-I IGM reionization calculation: H/He ionization fractions, matter temperature, evolving conserved photon number and energy, photoionization/heating, then anisotropic optical depth/visibility. A rigorous auxiliary gravitational/optical construction is valuable research, but it does **not** close the first physical H/He history.

- **REI `rei_bianchi/main` owns** the current D0 pathway, the R2C first canonical FLRW interval, node-level chemistry, group photon sinks, B2D source ensemble, B2E interface, and C0 Bianchi insertion.
- **BASS owns** metric/frame/screen/transport implementations and prospective typed geometry/time coupling. BASS CE1's fixed massless collisionless, reflection-even six-cell source is **not** REI's H/He IGM/opacity source. No shift in ownership is implicit.
- **REC owns** primordial recombination provider and its own source acceptance; VigilODE and REI F4 are independent research inputs unless a source-matched consumption witness exists.

Use `docs/development/REI_IGM_MISSION_DAG_20261101.json` for a **cross-repository dependency view**, not for authoritative node promotion. REI's `docs/roadmap/D0_PR_ROADMAP.md` and `docs/science/current_00_READ_FIRST.md` remain the REI owners' authority. BASS root `DAG.json` remains **ACCEL02**, not this graph. The BASS 15-node CE1 completion remains **9/15**; latest REI F4 **reported** 28/88 central, 33/88 working, but this is a separate ledger not independently reconciled with REI main D0. Never add counts across them.

## Order of science, not paperwork

1. **Central executable:** finish REI's first canonical FLRW thermochemistry interval from its accepted four-site 2048-partition microstep, under existing three-lane, error-width, positivity, photon ownership and thermal-energy requirements. The actual current next stage is `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-R1-UNCERTAINTY-QUALIFIED-FIRST-CANONICAL-INTERVAL-ADAPTIVE-HISTORY`. A single microstep is **not** that interval.
2. Close B2C2B photon/sink history, then B2C2C front, B2D source/moment closure, B2E FLRW interface, and only then C0 Bianchi-I H/He coupling. Preserve failures. The different IGM PR89 0.0008 manufactured acceptance is **not** a replacement for the current REI main science stage.
3. **BASS bridge work may run in parallel**: generate a *real* source/time/frame match for REI's accepted history with identical photon N/E, H/He rates, temperature, closure, opacity and uncertainty convention; test the FLRW limit before calling BASS geometry an eligible supplier. A source-matched transform is required, not just similar metric signatures.
4. Full physical anisotropic `tau_T`/visibility and observational inference follow a coupled, source-owned history. This ordering does **not** demand an unreleased CMB likelihood as a prerequisite for a first IGM history.

## Default selection and bounded exploration

When the active program target is explicitly **REI Bianchi IGM**, a generic “next theory/coding loop” **selects the next unclosed REI mission node**, not the newest CE1 PR. When the user instead targets autonomous BASS Type-II/classification work, follow `BASS_DAG_REALIGNMENT_20260821.md` and its independent owner path. An explicit request to explore CE1, CMB optics or other physically interesting areas remains fully authorized within its stated scope. Keep creative divergence available; classify it as `AUXILIARY` and never market it as accepted central progress.

After **two sequential auxiliary PRs with zero canonical progression**, perform a *single* mission re-evaluation: state the exact central target, which physical quantity the next candidate will change, and its causal dependency/evidence. Default subsequent work returns to central REI or a source-matched BASS bridge. This is **a routing decision, not an extra acceptance gate** and never deletes approved experiments.

Work that only extends CE1 harmonic order, curvature proof or beam optics without a REI consumer is deferred from the *default* central critical path. Existing valid CE1AL–AQ artifacts stay preserved, immutable and independently valuable.

## One claim = one typed evidence owner

For every scoped PR or handoff, state in the existing PR description or one brief checkpoint:
- **Which DAG** and exact owner/ref is changed; `BASS 9/15`, `REI F4 reported 28/88`, `REI D0 PR2 in progress` are **not interchangeable**.
- An actual changed **physical state, source, coupled history or observable**; its units, clock, initial/closure contract, source SHA, numerical or proof evidence, and explicit consumer.
- `CANONICAL_DELTA` only if the *owning REI/BASS acceptance criterion* was actually passed; scoped `1/1`, rows, plots, backup ZIPs, CI GREEN and same-author reviews do **not** promote any canonical node.
- Separate `derived`, `numerically checked`, `implementation verified`, `source-matched`, `owner-admitted`, `NOT_RUN` and `HOLD`. A same-author adversarial audit is not a distinct-author reviewer.

One science-first attempt, bounded targeted tests, one scoped technical/hostile verification pass, and a reusable source-inclusive checkpoint are generally sufficient. Stage-by-stage publication/backup status can point to the **same durable checkpoint**; do not produce twenty duplicative ZIPs merely to count R/C gates. Record explicit per-stage `completed/total` only when it refers to the actual selected DAG.

## Anti-drift decision for the next iteration

| Candidate | Default | Reason |
|---|---|---|
| REI first canonical interval | **EXECUTE next in REI owner** | Missing physical history on current program critical path |
| Original-source-matched BASS→REI time/opacity/H/He bridge | **ELIGIBLE parallel research** | Necessary for later C0 without replacing REI history |
| Further CE1 six-cell Weyl/low-ℓ/optical variants | **DEFER by default; explicit exploration permitted** | Different source and no demonstrated IGM admission |
| F4 CCC/BASS193 collision-only refinements | **Separate F4 lane** | Cannot automatically advance REI main D0 |
| Another audit of the same PR/ZIP | **NO** absent a new material defect | Validation consumed; return to physics |

No automatic merge, force-push, production/default or source replacement. The next PR is not created until it has a genuine new science/implementation deliverable, unless the user explicitly requests planning or audit as the output. Existing `docs/development/BASS_DAG_REALIGNMENT_20260821.md` remains historical evidence of earlier scope drift and is not rewritten.
