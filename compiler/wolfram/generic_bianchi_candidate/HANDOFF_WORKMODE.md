# Work-mode validation handoff

1. Read `SOURCE_REF.json`, `AUTHORITY_STATUS.json`, and verify `MANIFEST.sha256`.
2. Reuse `WOLFRAM-WORKMODE-20260824-R1`; do not rerun its xAct/PSTF probes.
3. Use Wolfram Language 15.0.1 and the already verified xAct 1.3.0 archive bytes.
4. Run only `run_workmode_validation.wls` and the focused fixture checks here.
5. Provide the packet root, a fresh output directory, and the verified xAct root.
6. Example: `wolframscript -file run_workmode_validation.wls --packet-root . --output-dir RESULT --xact-root XACT_ROOT`.
7. Do not execute any repository-wide Python/Rust suite.
8. The driver must reject antisymmetry, Jacobi, closure, representation, or hash errors.
9. Confirm equivalent exact representations produce one canonical spec hash.
10. Confirm I, II, VI_0, VII_0, VIII, IX-D, V, and VI*_-1/9 fixtures.
11. Confirm Type-II rank-one specialization never activates for VI_0/VII_0/VIII.
12. Confirm the exceptional adapter activates by exact Codazzi-map rank loss.
13. Confirm cold and warm canonical result bytes are identical for every fixture.
14. Run `python verify_result.py --result-dir RESULT` from the packet directory.
15. Return aggregate/result manifests, exact SHA-256 values, and raw failure logs.
16. A PASS may establish only `VALIDATED_NEW_CANDIDATE`.
17. Historical formula bytes remain absent; never claim recovered historical authority.
18. Do not connect SymIR v2 output to SymIR v1 or production Rust.
