# C2I support-preserving characteristic quadrature and historical SourceLedger

Scope: fixed accepted non-tilted LRS-I geometry or analytic FLRW; live H/He
packet chemistry; source-born UV with below-HI outflow, CMB Thomson tracer
and isotropic thermal bath. No self-consistent geometry feedback.

- Endpoint compression within ray, current threshold interval, bounded log
  energy width preserves N and U, and consequently the instantaneous ray
  stress. Endpoint birth labels are actual supports, not exact original
  cohort weights. Nonlinear rates, future threshold crossing and cumulative
  spectral error are not exactly preserved.
- Exact FLRW characteristic fast path alone did not remove a numerical
  angular quadrupole (see initial campaign and fast-path probe). For exactly
  isotropic geometry, empty initial UV and isotropic source, with compression
  explicitly enabled, evolve the single angular-integrated UV spectrum and
  lift it to the source angular quadrature at the end. This is exact angular
  symmetry reduction of the adopted model, not stress clipping. Short BASS
  geometry paths with nonzero shear (including small numerical shear) are
  not reduced. CMB remains full-angular. History packet counts are the
  internal stored count, while final packets.tsv is angular-expanded.
- PR171 SI stress convention is applied to actual photon inventory and
  compared to independent NumPy quadrature. Below-HI outflow is not included
  in this UV stress; no claim of total radiation stress or emitter four-force.
- Historical PR173 original probe, fixtures, matched oracle, and output
  recovered from BASS 4e2d1fa820d6f7baae1069b615fb82a08d53403b.
  Probe changes only compile-time identity constants. Original validation
  gate extracted verbatim from historical native_runner.py by AST.
  Current REI pin restores original fixed-q implementation. This test is
  source-only and does not establish chemistry equivalence.
- RESULTS.json is final-pin campaign; FLRW_ANGULAR_TRIAL.json and
  FLRW_FAST_PATH_PROBE.json retain diagnosed unsuccessful symmetry trials.
- Covariant REI long run is checkpointed by runtime cap, not complete.
  Fixed-q and characteristic endpoint routes differ in closure and low
  energy treatment. Convergence of all physical observables remains open.

Commands (from BASS root):
  cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example rei_live_characteristics --example sourceledger_recovered
  python research/r118c2i_support/run_campaign.py --binary _rustcore/target/release/examples/rei_live_characteristics --donor ~/Downloads/rec_r118c2g_boundary/normal.json --out NEW_CAMPAIGN_DIR
  python research/r118c2i_support/replay_sourceledger.py --binary _rustcore/target/release/examples/sourceledger_recovered --out NEW_LEDGER_DIR
  python research/r118c2i_support/verify_results.py --raw

No native subagent dispatch available. Local independent numerical oracles
and recovered historical validation are scoped; no R78 promotion.
