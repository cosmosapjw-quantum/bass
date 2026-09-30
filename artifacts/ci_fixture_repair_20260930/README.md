# CI fixture repair — 2026-09-30

Host validation-only followup to PR #132. Production source, benchmark corpus, exact output digest comparator and scientific tolerances are unchanged.

- Runner synthetic config used an obsolete adapter SHA. The fixture now hashes the actual adapter; the unchanged authority comparison still rejects a deliberately wrong SHA in a new regression.
- Package lazy exports already include runtime. The test now checks all three public module identities and the complete explicit export list.
- Native source-wheel CI deliberately runs as unverified development. Its warm-construction output has build_profile=null and optional_features=[]; the frozen reference has release and cpu/pyo3 extension features. Reproducing these unknown fields produced the exact CI digest 7b718708513a04993aaeb61947e090587e327395404c4c0d744010440928b26f. This is packaging/provenance metadata, not a numerical result failure.

The native test preserves the actual unknown fields and requires equality with the capability report. Only its architecture comparison substitutes the existing reference metadata into a separate copy before comparing the unchanged golden digest. Actual adapter output, the corpus and its exact-output benchmark gate are untouched. This does not make a development build eligible for a controlled benchmark or production dispatch.

Validation: 94 portable/runner tests pass, 2 skip; 13 focused adapter tests pass against the newly built debug extension. Full native-policy result is in native-policy-after.log. This local extension was loaded from a temporary correctly suffixed copy with the documented explicit development override; it was not installed over the user's environment. The hosted workflow independently builds its release wheel.
