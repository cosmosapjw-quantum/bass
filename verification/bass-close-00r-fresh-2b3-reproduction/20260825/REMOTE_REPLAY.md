# Remote replay order

1. Run `./restore_content_capsule.sh`.
2. Enter the restored content root.
3. Run `./run_content_replay.sh` for core 53, transport controls 14, exact
   witnesses, numerical 500/80/120, and byte-identical figure regeneration.
4. Record a fresh-context verdict without editing the sealed source.
5. Only then run the separate rows-7/8 R2 re-adjudication.
