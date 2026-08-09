# Runtime interruption recovery

Do not inherit transcript-reported completion. On interruption:

1. Inventory the canonical tree, artifact/receipt trees, sizes, mtimes, SHA-256 values,
   current git head/status, processes, and partial outputs.
2. Reconcile every DAG node and claim against its required durable receipt.
3. Label artifacts `DURABLE_VERIFIED`, `DURABLE_UNVERIFIED`, `TRANSCRIPT_ONLY`, `MISSING`,
   or `INVALIDATED`.
4. Re-run the earliest missing/invalidated node; never advance from transcript-only state.
5. Write a recovery receipt and update `state/run_state.json` atomically.

Large symbolic/numerical jobs must emit heartbeat/checkpoint receipts no less frequently
than their declared recovery budget and preserve complete logs rather than `tail` output.
