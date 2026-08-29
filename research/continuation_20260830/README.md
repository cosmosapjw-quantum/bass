# bass: research followthrough (2026-08-30)

This direct-text delivery imports the tested lane's tricode modules and adds
source-relevant research utilities. Read CODEX_HANDOFF.md for the exact local
work. No production scientific PASS is earned by these manufactured tests.

Run this isolated research set from the repository root:

```sh
python research/continuation_20260830/verify_payload.py --repo .
cd research/continuation_20260830
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:tests python -m pytest -q tests
```

Use an existing compatible research environment (NumPy,SciPy,SymPy,mpmath,pytest).
Do not alter production requirements/Cargo locks to run the reference suite.
The shared algebra is bounded dense reference code, not a scalable Krylov port.
Current source base: `2aaad1d72064ddeb60b27a0ec15536d0a2ec6a28`. Existing branches/evidence are unchanged.
