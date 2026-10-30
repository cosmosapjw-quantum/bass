# CE1-W reproduction and preservation

Frozen parent GL6/GL8 physical CSV is read directly from PR267. Current original CE1-T Python generator is used to rebuild exact-binary ray/mass lists with SHA-256 and physical source locks.

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 pytest==9.0.2
python research/ce1w_20261030/ce1w_transfer.py --out /tmp/ce1w
python -m pytest -q research/ce1w_20261030/test_ce1w_transfer.py
python -m compileall -q research/ce1w_20261030/ce1w_transfer.py
```

Expected output: 41 per GL order harmonics responses, 1681 per GL order two-time sensitivity records, 4 NPZ full geometry Jacobians, numerical summary. Native GitHub CI at https://github.com/cosmosapjw-quantum/bass/actions/runs/40985249699 completed SUCCESS on code HEAD `15f2187677edc263a7793f1336770e6e695b1690`. Exact complete local source ZIP (includes more extensive 18 tests, drawings and original inputs): SHA256 `6aa3e0e1a72bafca594b7e2317d6ccb5cda4b8f6615258126516844f36308d26`. Preserve conditional PR264/PR266 donor scope; PR266 certifies RK4/Hermite not DOP853; pressure error does not certify l4.
