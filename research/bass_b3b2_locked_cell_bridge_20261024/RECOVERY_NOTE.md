# Environmental recovery note

This note qualifies the original README's statements about retained local files.

After the initial implementation, single C9 repair, nine recorded scientific
commands and successful local S0 package readback, the shared ephemeral scratch
was observed to be completely empty and the runtime clock had jumped forward.
The old S0 ZIP had no durable external acknowledgement at that point. Its
previously observed SHA-256 and byte count are historical observations; its
original ZIP bytes are lost and are not claimed restored.

The four frozen scientific files were reconstructed from their exact original
tool-write arguments and verified against the previously recorded full SHA-256
identities. The pre-C9 implementation and tests were also reconstructed and
matched their previously recorded full hashes. The original three NPZ byte
identities were restored from the intake agent's surviving data; unchanged
vendor files were restored from the pinned BASS parent. No scientific equation,
tolerance, input byte, implementation or test was changed during recovery.

The historical expanded input-identity metadata document could not be recovered
byte for byte. Its observed old identity was 13141 bytes, SHA-256
4d767059b5afb14a3fd119be659e47a36a65d807bea435e52fcf6481ceda1d04.
A transcript-based expanded presentation now contains the same immutable NPZ
path/size/hash identities. The current metadata presentation identity is recorded
in RECOVERY_COMPARISON.json. The adapter's grid identity uses the three actual
NPZ hashes and arrays; it does not use metadata-document bytes.

One new current-unit artifact-generation call was explicitly authorized.
The unchanged code/reference_runner.py ran through artifacts/recovery_runner.py,
a copy of the byte-exact original bounded wrapper with only the ledger filename
and log filename prefix changed. Its actual argv/cwd, UTC start, exit status,
wall/CPU time, environment and full code/input hashes are recorded separately in
artifacts/RECOVERY_EXECUTION_LEDGER.json. The new stdout/stderr are
RECOVERY_COMMAND_01.stdout.txt and RECOVERY_COMMAND_01.stderr.txt. No historical
campaign, unit-test suite or C9 affected-check script was replayed.

This single new call passed. All 16 previously observed final aggregate values
were reproduced with exact floating equality, including the repaired inverse
errors. RECOVERY_COMPARISON.json records the field-by-field comparison and the
new figure/data hashes. The current PNG/PDF/CSV/VALIDATION files are newly
generated recovery artifacts; their old byte identities are not invented.

The original full EXECUTION_LEDGER.json serialization, per-command UTC starts,
some original raw output identities, old CSV row bytes, original PNG/PDF bytes,
original implementation manifest bytes, full C9 old/new row receipt and S0
packaging bytes were not present in surviving storage. They remain explicitly
lost. HISTORICAL_EXECUTION_TRANSCRIPT.json preserves the nine observed argv/cwd,
exit statuses, measured durations and available displayed outputs. It is
labelled a transcript reconstruction throughout and is not represented as the
original raw ledger.

Before this new experiment, restored file bytes were copied to the persistent
functions store. After the call, the complete regenerated lane, including the
fresh binary figure bytes and receipt, was copied there as well. Parent
publication/checkpoint acknowledgements must refer to the current recovered
payload and its actual new checksums.

## Later independent recovery readback

The independent reviewer retained the old CSV and PNG hashes in its review
metadata, although this implementation agent had not retained those metadata.
Comparison after regeneration established exact byte identity for all three
CSV files and the PNG. The PNG SHA-256 is
08479a47282e21337be1eb29e4765774c3ce3edad7c22bb8189c7182cdd6510e.
This recovers those scientific output bytes through one separately recorded
new execution. It does not reconstruct the missing original command logs or
their original serialization. The old PDF byte identity was not recovered;
the current PDF is a distinct regenerated artifact. See
reviews/RECOVERY_READBACK_REVIEW.json for the independent readback.
