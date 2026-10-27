# Reproduction commands, not current execution authorization

Restore the D source archive into an isolated directory. It contains the new unit and the five pinned files needed under its sibling `bass_b3h_endpoint_channel_interpolation_20261027`. Use the recorded dependency versions; the source pin, not package availability, determines the accepted input. All current science is already computed and the allocation is closed.

For an explicitly authorized future reproduction only, from this unit directory:

```sh
python -m pytest tests -q
python code/run_study.py ../bass_b3h_endpoint_channel_interpolation_20261027
python code/plot_saved.py
```

The commands above are direct reproduction commands and do not by themselves grant a resource allocation. The historical `meter.py` limits child resources but is not a production permission gate. A future run must create a distinct output/work directory and new resource contract; never overwrite the accepted evidence. New study outputs are `results/SYNTHETIC.json`, `NATIVE_RESTART.json`, `NATIVE_PANEL_COUNTS.json` and three JSON checkpoints. Plots consume only saved SYNTHETIC.json.

The two-state fixed-grid checkpoint is not an adaptive solver checkpoint. It preserves all fixture state/reward components, global step/time, identity and attempted work and rejects pending transactions. Native high-precision cut values are stored as decimal strings; they are not fed through the binary64 fixture checkpoint adapter.

R6/C9 review can inspect the saved evidence without running these commands. Public Git stores a code/theory/summary projection. The full new raw results, failure logs, figures and pinned inputs are in the immutable source ZIP; use `delivery/FINAL_ROOT_ACK.json` for the actual archive identity and provider locations.
