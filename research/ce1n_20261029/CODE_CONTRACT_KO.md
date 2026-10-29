# CE1-N math-to-code contract and stop boundary

Exact source/path bytes are inherited from fixed PR253/PR251. Changed surface ONLY:

- `bianchi/nonperturbative/einstein_tabulated_intrapanel.py`: opt-in `certify_panel_growth_rates`, `repropagate_certified_panel_source`, `propagate_intrapanel_source`, `run_intrapanel_rk4`.
- `tests/nonperturbative/test_ce1n_intrapanel.py`: exact rational Bernstein check, n=1 identity, dyadic strict decrease, 65-digit mpmath forcing integral, invalid source/physical/shear/path negative cases, backend admission and substep bound.
- `research/ce1n_20261029/`: reproducible real ref1/ref8, SHA-verified inherited ref16 source forcing, 120 synthetic mpmath exact comparisons, overhead timings and inspected figures.

Dependency baseline source is `certify_canonical_panel_source` (PR253) and identity guard is the exact current source/path SHA. The source and continuum physical-table lock, positive stored-ray and current-input topology are checked by PR251's `_source` and `_stored_data`. Fast reuse is allowed **only with trusted in-memory previously certified `canonical`**, not an authenticated proof for arbitrary JSON payloads. Initial shear must regenerate the exact stored path initial state; mismatch rejects rather than transporting an incorrectly chosen continuum derivative lower.

The new comparison changes neither source integrals nor original 4 RK4 panels/time residuals. All n comparisons are nonnegative MPFR192 directed; the stored path derivative certificate uses exact Fraction Bernstein. n=1 exact CE1-M upper is required, n=32 lower than n=1, no change of 1e-5 target. Equal source/path hashes are required for archived ref16 reuse. No general solver benchmark or observed sky claim.

Positive next action: after scoped CI+preservation, return to independent-author R6/C9 or actual formal MPFR/Python program verification. Original upper DAG 9/15, CE-1 PARTIAL, R/C scoped 18/20. Do not auto-merge, produce native, or start a new research loop on the strength of this scoped certificate alone.
