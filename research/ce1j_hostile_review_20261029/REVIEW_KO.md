# CE1-J external-reviewer-style adversarial R6/C9 audit (2026-10-29)

**Subject:** [PR #246](https://github.com/cosmosapjw-quantum/bass/pull/246) HEAD `4474f8acb13614ffda7a30524a815976e306efc9`. Original PR/main source **unchanged**. Upper DAG **9/15**, CE-1 PARTIAL. This is one model's hostile review with independent Python and Wolfram CAS checks, **not** an actual distinct-author peer review or native subagent.

## Verdict: REQUEST_CHANGES (conditional mutable-input certificate unsound)

The strongest defensible existing claim is a positive exact-binary massless collisionless expanding diagonal Bianchi-I source/whole-panel error bound for a **fixed, correctly matched** first-octant angular cell table. I independently reran the existing 95 focused tests: **95 PASS**. For 24 positive randomized original-cell cases ×10 positions, GL56 original-cell quadrature discrepancy stayed below declared pressure bounds (maximum observed error/bound **0.03382438**, falsification only). Independent Wolfram single-ray pressure Jacobian identity residual was 0 for all 9 components, and `sum_j R_ij-P_i=0`. Those checks **do not certify arbitrary inputs**.

### P0 for advertised/current mutable-source API: mismatched stored ray/cell cardinality is silently accepted

In `bianchi/nonperturbative/einstein_tabulated_source.py`, `_stored_data` lacks a guard `source.n.shape==(len(source.cells),3)`, `source.mass.shape==(len(source.cells),)`. `certified_tabulated_pressure` uses `zip(source.cells,squared,stored_masses)` and silently **drops extra positive stored rays** while `TabulatedRadiation.moments` and `einstein_interval._source_stored_binary` use the complete current stored ray/mass array. `certified_tabulated_energy` has a separate truncating `zip`. Positive same-cardinality ray/mass rebinding is explicitly supported by previous PR243/244/246 tests; changing cardinality should instead be explicitly rejected.

**Exact analytic pressure-premise witness.** Construct one isotropic original physical angular cell `E0=float(.9)`, shear=0, normal proper `u=t/Tstar`, append one stored ray `n=(1,0,0)` with mass `1` after construction. The object retains positive rays/masses and accepts certification. At `u=0`, MPFR192 outward gives `P_Q,x - P_cont,x ∈[1.0,1.0000000000000002]`, while `certified_tabulated_pressure(..., upper=[.08]*3)` returns `η_x=0.037910063880682444`. This violates the REQUIRED `|P-P_Q|<=η` source hypothesis by a factor at least **26.3782**.

**Whole-path countercheck.** The original continuum exact FLRW radiation solution is `h(u)=h0/(1+2*h0*u)`, `ell(u)=log(1+2*h0*u)/2`, `h0=sqrt(E0/3)`. Four reconstructed Hermite panels from an independent DOP853 integration of the changed positive stored source are accepted by `certify_local_tabulated_path`. Actual computed `||Δh||∞=0.06736023040427652`, but the returned bound is `0.0016681761537905627` (**40.3796× smaller**). Since DOP853 is not certified, this endpoint comparison is a numerical falsification. The initial source premise failure is an MPFR outward interval proof witness independent of DOP853.

**Not refuted:** the unchanged original six-cell/ref16 source and its reported `3.6749116877624083e-6<1e-5` numerical output; the Einstein-Vlasov equations; the pressure Jacobian theorem; the fixed-cell topology case. The defect is an *unchecked out-of-contract representation* causing false certification.

### RED/GREEN and minimal required change

Independent test file `test_reviewer_shape_contract.py`: original **2 expected FAIL + 1 PASS**, exit1. In an *isolated local copy only*, insert into `_stored_data`:

```python
ncell=len(source.cells)
if np.shape(source.n)!=(ncell,3) or np.shape(source.mass)!=(ncell,):
    raise ValueError("Stored ray/cell cardinality and shape contract violated")
```

Then **98 PASS**, exit0 (95 inherited+3 hostile). This retains positive mass/ray **same-cardinality** rebinding. A standalone ZIP with original RED/green logs, analytic and MPFR witnesses, runnable scripts, proposed diff, source map and handoff has SHA256 `6254db68646e080dec43a1967e437e62a9c5d10d859d397ec6c9ec3e8825954e` (17,001 bytes, 16 members, CRC PASS).

## Other open obligations

Formal Python/MPFR implementation proof: NOT_RUN. Native Rust or independent distinct-author R6/C9: NOT_RUN. Root policy RF-00/`bianchi.__all__` and RF-BENCH/`source_adapter_sha256` failures: separate CI problems, not fixed here. No merger, no production admission, no auto-next node. This review owns only an adversarial finding and patch proposal, not an applied code fix. **Next minimum work:** fix cardinality/shape preconditions in a separately authorized implementation unit, run new hostile regression and previously passed 95 tests, then compare fixed/ref8/ref16 source and geometry, preserve all proofs and unrelated science.
