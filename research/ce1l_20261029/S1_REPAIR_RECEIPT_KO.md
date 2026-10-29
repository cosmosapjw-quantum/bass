# CE1-L S1 repair and verified stage backup

**Parent:** PR250 `4c08e7897392b482e99b567438a0664429c282c6`; candidate PR251 isolated Draft. Physics positive massless collisionless diagonal Bianchi I, Lambda0, signature (-,+,+,+), exact binary64 original 6-cell physical input; 4 RK4 panels, u<=.08, target max|Δh|<1e-5 unchanged. Top-level upper DAG **9/15**, CE-1 PARTIAL.

Actual repairs:
1. exact physical continuum table identity held by construction-time cell tuple and original raw float64 edges/table; disallow physical cell/energy metadata mismatch while permitting same-cardinality positive *numerical* ray/mass rebinding;
2. positive stored-ray MPFR fourth derivative energy majorant rejects any individually negative current ray mass, even if aggregate mass is positive;
3. public CE1-H initial continuum pressure helper checks the same frozen physical table precondition.

Adversarial RED on pinned parent: 5 failed / 2 passed physical table tests, 2 failed / 1 passed negative mass tests. GREEN latest local complete scoped suite **112 passed, 0 failed**, exit 0. Git source blobs:
- `einstein_tabulated_source.py`: `fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`
- `einstein_interval.py`: `abbab0990fdefaf535ccbf5191ae3e060cb19214`
- `einstein_tabulated_sharp.py`: `61560ed52a78c01fe6f21923a7480af732d9ec4f`.

Fresh four independent OS MPFR192 panel workers and identical exact ray/mass/RK4/Hermite SHA:
- ref16 CE1-G `3.7019164499698285e-6`
- ref16 CE1-H `3.675931156248731e-6`
- ref16 CE1-I `3.6749116877624083e-6`;
all historical gaps 0, strict original 1e-5 target MET. Fresh ref8 uniform source G/H/I remains `1.2322918653868093e-5`, `1.227583245284329e-5`, `1.2273903547843227e-5`, target NOT_MET.

Actual GitHub scoped CI [#40849142460](https://github.com/cosmosapjw-quantum/bass/actions/runs/40849142460) SUCCESS for the code and tests before the final CI/readout-only docs commits. RF-BENCH/CE1C/CE1F/CE1H tests also succeeded at same code head; native RF-00 tracked separately. No full repository or native production admission.

### Verified two-provider S0/S1 archive receipts
- S0 `BASS_CE1L_S0_HOSTILE_20261029.zip`: 6,286 bytes, SHA-256 `0b208d898ae6f95c8f123aece8b8c19111a774ff4b417cd080bad1d7e3d5ddd3`; Drive `1osZj2q8L-FtbxrpZz1KI-HPaFG9e1Oo6`, full byte readback MATCH; Dropbox `id:BSpOijBcT10AAAAAAEHVcg`, 6,286 bytes, content hash `52fc0523bb7b6e6443117993a0c621c49471eee84768de7275c02be78f635920` MATCH.
- S1 `BASS_CE1L_S1_REPAIR_20261029.zip`: 45,056 bytes, SHA-256 `1100cdb118f15fda09692310a458d6fa28cfc9247d8d72410aaf0c67565440c3`; Drive `1qILb7_zpp7V3ijkDUFKX6TXMw0mX5RI8`, full byte readback MATCH; Dropbox `id:BSpOijBcT10AAAAAAEHVcw`, 45,056 bytes, content hash `aa69f6db8659fc579fdb9b65174405b2ea457af9dbc715f580a21f05fc5df463` MATCH. Dropbox full-byte readback NOT_RUN. All local ZIP CRC PASS.

These are independent proof-premise repairs, not a claim of formal Python/MPFR machine verification or a distinct external human reviewer. Parent and main unmodified. `production_ready=false`, `merge_ready=false`, `auto_next=false`.
