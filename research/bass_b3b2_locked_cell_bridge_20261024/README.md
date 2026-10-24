# BASS B3b2 locked-cell snapshot bridge

> **Environmental recovery:** The original nine-command raw ledger/log files
> were not fully recoverable after an observed scratch wipe. Current numerical
> data and figures come from one separately authorized recovery run of the exact
> frozen code. Its receipt is `artifacts/RECOVERY_EXECUTION_LEDGER.json`.
> [RECOVERY_NOTE.md](RECOVERY_NOTE.md) qualifies the historical retention
> statements below and distinguishes transcript observations from original raw
> files and fresh recovery artifacts.

This opt-in research adapter represents the actual REC 35 × 26 locked discrete
photon inventory as 910 massless BASS packets. It preserves the represented
number four-current and stress-energy tensor, supports an explicit active state
boost and its inverse, and preserves the original cell and angular labels.
Physical energy is exclusively `299792458 * saved momentum_scale`.

The source occupation is the scalar, unpolarized, isotropic bootstrap
**INITIAL-DATA** supplied by the REC Bianchi II source-derived parent, with
`coupled_macro_endpoint=false`. The anisotropic experiment is a clearly labelled
synthetic perturbation of that actual angular grid. No rate clock, boundary
transaction, atomic source, `Source` object, collision operator or IVP is added.

## Small public API

`code/locked_bridge.py` defines `Units(kappa,L,Pstar)`, `LockedGrid`, and
`PacketState`; `load_actual_inputs`, `to_packets`, `fixed_grid_inverse`,
`state_boost`, `physical_sums`, and `packet_observables` perform the operations.
The loader checks each NPZ SHA-256 and byte size against `inputs/IDENTITY.json`
before loading with `allow_pickle=False`. It reproduces REC angular normalization
`A=raw/sum(raw)` and records the raw sum (1.0 here). The general grid constructor
requires already normalized angular weights and rejects invalid inputs.

The fixed-grid inverse requires the original input/grid identity, cell labels,
angular labels, massless momentum grid and original frame. A boosted state must
first be explicitly inverse-boosted; it is never silently rebinned. State boosts
reuse the unchanged vendor plus-sign active boost, including `w′=(E′/E)w`.
Weights are state-density quadrature weights, not invariant event-rate weights.

`vendor/core.py`, `vendor/kinetic.py`, and `vendor/__init__.py` are byte-identical
copies from the existing B3b lane. Their local dependency inspection finds only
`vendor.core`, NumPy and Python standard-library imports. No solver is changed.

## Reproduction and receipts

From any working directory, invoke the bounded wrapper with an absolute or
correctly resolved path; the wrapper records and sets the scientific cwd to this
lane:

```bash
python code/run_bounded.py python -m unittest discover -s tests -v
python code/run_bounded.py python code/reference_runner.py
```

Those literal commands are correct when launched from this lane. The complete
actual invocations, cwd, exit status, wall/CPU time, input/code SHA-256 hashes,
thread environment and stdout/stderr filenames are in
`artifacts/EXECUTION_LEDGER.json`. Each scientific subprocess has a 30-second
wall guard, 20-second CPU guard and one-thread environment. The prospective
aggregate check reserves one whole command within the 120-second wall and
60-second CPU unit envelope. No IVP or historical suite is run.

`tests/test_locked_bridge.py` contains eleven tests for actual data, exact vacuum,
isotropic and synthetic anisotropic states, unit rescalings, an independent
rational oracle, axial and non-axial covariance and inverse boosts, incompatible
inverses, invalid inputs, and explicit arithmetic underflow/overflow. Tests also
reject wrong normalization of G, competing energy ownership, and omission of the
state-density boost weight. The arithmetic checks explicitly guard both `w*E`
and the unchanged vendor tensor's `w/E` coefficient against positive underflow.

No tolerance was changed during implementation. The acceptance limits are
512 machine epsilon for sums/covariance and 128 epsilon for individual positive
occupation roundtrips, with exact zero preservation. The direct oracle uses SI
cell sums independently of the packet formula. Its residual denominator is a
global L1 sum of absolute contributions; symmetry-forced zero tensor components
do not become small denominators. These are floating checks, not interval proofs.

## Measured result

The actual stock is **106530.54352303005 m⁻³**, with energy density
**1.740735402878829 × 10⁻¹³ J m⁻³**. The direct bridge residuals are
`4.018991460485999e-19` for N and `2.279091117273708e-16` for T.
Across 36 covariance rows (actual isotropic state and synthetic angular
perturbation, axial/non-axial boosts, |β|=0 through 0.8), maximum residuals are
`1.1775832543398129e-15` for N and `3.717949182316828e-16` for T.
After the targeted C9 inverse repair, the maximum positive-f inverse-boost
roundtrip error is `1.1102230246251565e-15`; the actual original-frame positive-f
roundtrip error is exactly zero in the recorded floating operations.

The deliberately omitted boost-weight mutation reaches a T covariance residual
of `0.07371223129259362`. Substituting the actual competing parent target-energy
array for saved `c*p` leaves the total photon number unchanged in floating
arithmetic and shifts energy density by `-6.274855397481909e-9` relative. This is
a rejected ownership substitution, not a Doppler width or a new physical model.

The four-panel figure is `artifacts/LOCKED_CELL_BRIDGE.png` and `.pdf`. Its exact
data are `CELL_STOCK.csv`, `BOOST_COVARIANCE.csv`, and
`ENERGY_OWNER_MUTATION.csv`; `VALIDATION.json` records results and versions.
All stored zero residuals remain numeric zero, and are plotted at zero. An exact
floating zero means equality in the recorded floating operation, not an interval
certificate or a universal exact conservation theorem. Tiny spatial components
in the isotropic direct sum are floating cancellation residues.

## Retained failure and repairs

COMMAND_01 is a failed intake diagnostic: numeric inspection succeeded, then an
unnecessary UTF-8 decode of the opaque `uint8 parent_payload` raised
`UnicodeDecodeError`. Its original argv, stdout and stderr are retained. No
pickle loading or opaque payload deserialization was attempted. The adapter
needs only the explicitly named numeric NPZ arrays.

COMMAND_02 passed all ten tests; COMMAND_03 passed the experiment, with a
Matplotlib cache-location warning. A targeted arithmetic guard extension and
regression passed in COMMAND_04. COMMAND_05 and COMMAND_06 regenerated the same
numerical results while repairing plot annotations/energy ticks and setting a
writable Matplotlib cache. No equations, input ownership, tolerances or claim
boundaries changed. Final code and input identities are recorded in the final
execution receipt and `IMPLEMENTATION_MANIFEST.json`.

The independent C9 probe then exposed one real inverse defect: a valid large
measure/small occupation state (`G=1e301`, `f=1e-301`) was accepted forward but
rejected by the inverse's unnecessary dummy `f=1` packet construction. One
targeted repair removes that construction, validates expected momentum/labels
directly, and reverses forward scaling as `n=w/weight_factor`, then `f=n/(G*A)`.
The pre-repair code, tests, manifest, ledger and inverse-error data are retained
under `artifacts/PRE_C9_REPAIR/`. COMMAND_07 passes the new regression and the two
affected inverse/covariance tests; COMMAND_08 passes the actual inventory check.
COMMAND_09 refreshes only the actual inverse error and all 36 inverse-boost error
fields. All forward N/T values, covariance residuals, mutation values and plotted
values remain unchanged, so the already inspected figure is reused. This is the
single scientific review repair; no tolerance or vendor change was made.

The result closes the locked finite inventory → BASS state-representation and
observer-covariance edge. It does not reconstruct unresolved spectral moments,
the LINE01 incident boundary, a full anisotropic history, native atomic event
ownership or a coupled time-dependent background. It claims no strong no-go,
merge or production activation.
