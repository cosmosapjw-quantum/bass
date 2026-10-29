# BASS CE1-J scoped research and code report, 2026-10-29

## Decision

CE1-J constructed a *stronger certificate for the same original Einstein–Vlasov fixture*, rather than altering the solver. At ref16 the upper bound max|Delta h_i| is 3.0184081966517434e-06 versus inherited CE1-I 3.6749939320347266e-06, 17.866308% lower. This meets original strict 1e-5 target. The first refinement to meet target changed from ref16 (1536 rays) to **ref8 (384 rays)**: 9.6386522249386591e-06 vs ref8 CE1-I 1.22740577476654e-05. This is an angular-discretization resource reduction, not a measured 4x wall-time speedup. Ref1/2/4 remain NOT_MET. Upper DAG remains 9/15 with CE-1 PARTIAL.

## Provenance

- Original parent BASS PR242 head 99473c0e6ba8f9d7172cc3fb730f5ac32c7e4677, parent PR240 head 0fd95e4baadf8982cdb1f9f81725b7b8e8fd0aa1; immutable original CE1-I archive SHA-256 83eb664e6695adecdaac1dacfd41041dd15df1207f2f20ab99ed7ee3bd15e60e, CE1-H archive SHA-256 e4ed87dfe9fe99f9e9ce061c95cebc65b97f7884690517cb5b5a646f8f7a12d2.
- Latest independent PR243 (fresh source majorant current mass) and PR244 (same and exact binary Hermite panel-origin) were actually inspected. Both P1 witnesses reproduced RED before local repairs and GREEN after. The corrections are adopted as **selectively repaired semantics**, not by merging those branches; original physical input, RK4 recurrence and target unchanged.
- 8 related repositories examined: bass, BASS_HE, bass_cr, rec_bianchi, rei_bianchi, WU088_HH, htt_base, vigilode. External chemistry/reionization/collision/rate contracts NOT_IMPORTED into this collisionless module.

## Scientific computation

CE1-J derives the exact e^-4s homogeneity of continuum and discrete fixed-ray pressure, transferring source discrepancy into four rigorously shrinking boxes. Fresh MPFR192 source re-certification at ref16 took 34.559s; the ref16 source/path SHA match preserved CE1-I original. **Whole-panel time residual is inherited by SHA, not independently rerun for this current CE1-J source ref16 run**. The ref1/2/4/8 paths are fresh in the current sweep. Non-autonomous CE1-I pressure Lipschitz comparison remains unchanged. Geometry/source Emax stays 0.9.

Panel caps ref16: 3.569278983e-05, 2.990264761e-05, 2.460332649e-05, 1.975937505e-05; original global cap 3.569278983e-05. Error components ref16 h: initial 1.8658990870173474e-16; source 2.2025201494088541e-06; time+jump 8.1588804705629915e-07; total 3.0184081966517434e-06.

## Verification

- Current scoped Python pytest: **94 passed** (inherited 86 CE1-I + 8 CE1-J/PR243/244 guards), 14.80s, exit 0; targeted red/green mutation exact tests 3 FAIL pre-repair, then 8 PASS post-repair. See included logs and source/test files.
- Wolfram independent symbolic ray ratio/row derivative: {1,0}.
- Plot-based review: CE1J_SOURCE_CAP.png monotone cap shrink across panels; CE1J_REFINEMENT.png shows ref8 strict target transition, ref1/2/4 not met. Both output plots were opened and read; no claim of extra measured-sky validation.
- Fresh MPFR192 current source caps; saved validated CE1-I exact binary Hermite/time residual imported by SHA identity; no formal proof of Python/MPFR program; no native Rust production; native subagents NOT_RUN (not exposed).
- R6 and C9 **distinct-author** reviews NOT_RUN; separate RF-00/RF-BENCH-00 policy failures remain. Source/cardinality tests do not confer solver, output or statistics readiness.

## Risk ledger

P0: none newly observed for frozen positive fixed binary measure. P1: inherited stale mass/ray cache and missing panel-origin identity independently reproduced/repaired on isolated child only; independent end-to-end audit and formal MPFR toolchain remain open. P2: panelwise source cert dominates runtime, and only original source input calibrated; sample constraints exclude generic sky, spatial modes and time-varying rates. P3: stage metadata and plot legibility are auxiliary.

## Publication and next

CE1-J remains additive Draft-only, no merge. Upper DAG **9/15**, parent CE-1 PARTIAL, 15 nodes/21 edges; R/C scoped scientific stage completion **18/20**, R6/C9 distinct-author hold. Production false, merge false, auto-next false. Next safe action is distinct-author R6/C9 of CE1-G/H/I/J and targeted independent MPFR program-level assurance before any production claim. Additional physics expansion only after provenance and claim gates.
