# BASS PR165: source-locked LRS Einstein–Vlasov → rei_bianchi proper-time geometry intake

2026-10-16 KST. Exact BASS PR164 `3c39bbbf46b6663e7c40277e194fd0ef48118472` dependent. Previous PR164 source remains an independently executable input, not upgraded to a native REI chemistry claim. Native original target for conditional typed adapter: REI PR150 `fe789b0b13b1883c5a74cbc907f72f6f963a5d66` at observation time. Original source owner and NCP full-run checkpoints remain unchanged.

## New executable deliverables

- `source_table.py`: SHA256/case/order/unit/positive-pressure/Hamiltonian/Raychaudhuri/signed-shear gates for PR164's original 968-point source; log-H and b cubic Hermite interpolation in `x=ln(a/aref)`, enforcing `s=H db/dx` at all interpolation points; elapsed proper time reconstructed by `integral dx/H` and invertible in source range. Independent kinematic consistency, *not exact intermediate Einstein RHS*.
- `export_native_geometry.py`: immutable, versioned proposed 968-row `BackgroundPoint`-compatible source table with SHA256 receipt. `sigma_signed=s/H`, `Sigma=sqrt(3)|s|/H`, `h_flrw_per_s` only a cold-reference diagnostic, and actual mean H kept independent.
- `tests/`: 15 newly executed positive/negative source controls, independent PR164 dense DOP853 check and actual clock inversion. Parent PR164 14 existing tests also rerun here (29 total). Test defaults are unchanged; earlier failures from first tests preserved in evidence.
- `refinement.py` and `evidence/REFINEMENT_STUDY/REFINEMENT.json`: 61/121/241 nodes, four representative non-identical physical cases, independent tighter DOP853 midpoint comparison. Max H relative midpoint error `5.3207960e-10`, `3.3748671e-11`, `2.1184166e-12`, compatible with fourth-order interpolation. Producer time mismatch plateaus about `2.3e-10` and is not claimed fourth order.
- `native_rust/`: independent Cargo binary candidate importing the actual `rei_microphysics::axbi_background::BackgroundPoint`, to be compiled **on NCP by Codex only after a clean pinned repo checkout**. In this environment `rustc`/Cargo are not installed, so this Rust source is `NOT_COMPILED/NOT_RUN`; no true Rust type check is claimed.
- `CODEX_HANDOFF_KO.md` and `NCP_PREFLIGHT.sh`: source identity, owner-driver noninterference, exact run commands, 64c NCP resource ceilings, positive gates, and strict return receipt.

## Science and normalization

Signature (-,+,+,+), axisymmetric metric `ds²=-c²dt²+a²[e^-2b(dx²+dy²)+e^4b dz²]`, `s=db/dt`, `Σ=sqrt(3)|s|/H`. Proper seconds and SI H, no silent natural unit conversion. FD96 massive kinetic pressure and source quadrupoles from PR164, with `Ω_m f_m` counted once and remaining cold dust. All original source CSV columns and receipt hashes are preserved, while REI native geometry field `sigma` is *signed*. The new background remains a conditional matter source only, with isotropic prescribed radiation and no evolved gamma/nu towers. Warm kinetic isotropic H(a) need not equal cold-dust FLRW H(a) when `f_m>0`.

## Actual tests and measured limits

```
cd research/rei_pr165_source_intake_20261016
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python -m unittest discover -s tests -v
(cd source_pr164 && python -m unittest -v test_kinetic_tangent test_export_bridge)
python export_native_geometry.py --source-csv source_pr164/PROPOSED_REI_BACKGROUND.csv --source-receipt source_pr164/PRODUCER_RECEIPT.json --out /tmp/bass_pr165_new_geometry
python refinement.py --out /tmp/bass_pr165_new_refinement
```

ChatGPT Python container: 15 new source-receiver tests PASS, parent 14 PASS. Original 968-row CSV SHA256 `5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133`, proposed new native geometry SHA256 `b406e60184d68fd4014dbee42250b8cf4645f48d1580caf44b336eac0fd93037`. Proper-time source-to-quadrature max relative mismatch `2.3151692135772128e-10`; at the new table's original knots `H` relative max ~`3.55e-15` and signed `s/H` absolute max ~`1.73e-18`. These are input/compiler-independent geometry checks, not HHe chemical convergence.

Standalone native type input is `evidence/NATIVE_GEOMETRY_INPUT/NATIVE_GEOMETRY.csv`, SHA held in `NATIVE_GEOMETRY_RECEIPT.json`. The Rust program's `Cargo.toml` intentionally includes `REPLACE_WITH_PINNED_REI_MICROPHYSICS_PATH`; Codex must bind this to the real immutable PR150 crate. To **run** the binary rather than merely discuss integration, follow `CODEX_HANDOFF_KO.md` and the host's available NCP SSH. The existing source005 full-run on NCP must be inspected and protected before any new job is launched.

## Claim gate and precise next action

`DERIVED`: kinematic interpolation construction, positivity and monotone proper time from positive H. `NUMERICALLY_CHECKED`: source/ROW validations, 4-case grid refinement and independent dense state comparison. `PYTHON_IMPLEMENTATION_VERIFIED`: 29 source and new tests. `NOT_RUN`: actual remote NCP execution, native Rust Cargo integration, native HHe coupled chemistry, full EoR plot, observational inference. `RUNTIME_BLOCKED`: Desktop Commander monthly quota; no workaround through unintended privilege or process reuse. Native ChatGPT subagents not exposed.

Next task is **NOT** more process documentation: compile the already supplied native Cargo candidate against exact REI PR150, repair any real compiler error, then implement/verify a feature-gated owner-bound `GeometryBackground` read-only source with new checkpoint/source identity and proper time. Run the first short same-event HHe trial with full number/energy/thermal/binding/ionization ledgers. Prescribed background supplies geometry only and cannot be identified with complete photon+gas backreaction. Return actual machine receipts to this thread.
