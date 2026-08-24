Continue the BASS native reproducibility recovery using only fresh remote evidence.

FIRST ACTION (mandatory): authenticate GitHub access and read back both refs and the receipt before relying on any prior conversation:

```bash
git ls-remote https://github.com/cosmosapjw-quantum/bass refs/heads/artifact/native-repro-bundle-20260824-r1
git ls-remote https://github.com/cosmosapjw-quantum/bass refs/heads/agent/recovery/native-repro-closeout-20260824-r1
git clone --depth 1 --branch agent/recovery/native-repro-closeout-20260824-r1 https://github.com/cosmosapjw-quantum/bass bass-closeout-readback
jq . bass-closeout-readback/repro/native/BASS-NATIVE-REPRO-20260824T065249Z/REMOTE_ARTIFACT_RECEIPT.json
```

Repository and authority:

- Repository: `https://github.com/cosmosapjw-quantum/bass`; visibility `PRIVATE`; authenticated Git is required.
- Canonical source branch: `agent/recovery/background-evolution-v87-integrated-20260824`.
- Source head / historical anchor: `0d1203da778c5e92fce4c9bbf24c8044c5b46018`.
- Source tree: `675213f191477b1f47c725892e9f4c804c623ab0`.
- Anchor ancestry result: `PASS_EQUAL` (`merge-base --is-ancestor` exit 0; head equals anchor).
- Cargo.lock SHA-256: `d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`.

Remote delivery:

- Artifact branch: `artifact/native-repro-bundle-20260824-r1`.
- Artifact head: `3030887d999cf5d6ce9d4a2505552b10f3ab595b`.
- Artifact commit URL: `https://github.com/cosmosapjw-quantum/bass/commit/3030887d999cf5d6ce9d4a2505552b10f3ab595b`.
- Artifact path: `repro/native/BASS-NATIVE-REPRO-20260824T065249Z`.
- Closeout branch: `agent/recovery/native-repro-closeout-20260824-r1`.
- Closeout branch URL: `https://github.com/cosmosapjw-quantum/bass/tree/agent/recovery/native-repro-closeout-20260824-r1`.
- Exact closeout head is the commit containing this prompt. Resolve it in the mandatory first action; embedding its own SHA would be a cryptographic self-reference.
- Draft PR was necessarily absent when this single closeout commit was constructed. After remote SHA verification, query `gh pr list --repo cosmosapjw-quantum/bass --head agent/recovery/native-repro-closeout-20260824-r1 --state all --json number,url,state,isDraft,title`; do not infer its URL.

Artifact identity:

- Archive: `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz`.
- Archive size: `176301104` bytes.
- Archive SHA-256: `033b408558b1c908b1604b80ed3f942f9720120c2f15dae0b231ecb4547f8db1`.
- Content-manifest SHA-256: `fb9cffaea6213c4f74b9bd244197cb0ccc970e5299bd98d4417c925a41007dfa`; 8,741 covered regular files; NUL-terminated lexical path-byte order.
- BUNDLE_MANIFEST.json SHA-256: `c981bc7c13d2f68564941ba74830542039d61b05ea7972d7244b0b24f509c1ae`.
- Parts: 22; hard caps 8,388,608 bytes per part, 32 parts, 268,435,456 archive bytes.
- Native wheel: `bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl`, 1,050,262 bytes, SHA-256 `b1661295a9e5a7e9a9f1260e8c8ea5e26aef00e13a4e8530d0746a7d9ad1eb46`, SOABI `cpython-312-x86_64-linux-gnu`, import/backend/deterministic call PASS.

Ordered parts (this order is authoritative; never trust a filename glob):

- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0000` — 8388608 bytes — SHA-256 `7dfc5a9f471d9921eae25f1443f581b2b3941c9cd794f0caf68f49088d7e5b53`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0001` — 8388608 bytes — SHA-256 `b6faffeebebd0920ee4c9b1c590dacc3e8a3e1fac12a4187996c4648053106cc`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0002` — 8388608 bytes — SHA-256 `eed21abd9a07680f142c47acf6e32c9abf00f965eaa624d03b1f1be49aced8da`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0003` — 8388608 bytes — SHA-256 `26e16bb844bbac32bf6268fa62b6b0a2498510868d5bb04913611b1db7053182`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0004` — 8388608 bytes — SHA-256 `a8aed9f777fde1b3b876bd455ba0c6b0f1da080cd04218e350c17f37d6bc714d`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0005` — 8388608 bytes — SHA-256 `3f4f445254d10d2f6e1fc52c7833b224933160d6275bf98bb5773171e33d1e66`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0006` — 8388608 bytes — SHA-256 `f6251cc2499670722dc5c481e0bd1c2b87551c873fdd9460247659402556a655`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0007` — 8388608 bytes — SHA-256 `a53b3872ae1ebd4e5bc902901389008062fbfc9ff3dcdf39a0c5022f887a3fd8`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0008` — 8388608 bytes — SHA-256 `0a2a2ee4aba0b6fea7b71deba45b9d6d3411797ff902a307d69b31c2b8cb818f`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0009` — 8388608 bytes — SHA-256 `2a159dce11f3271b07cff51692c1d75839a44034ac96613b41ecc555c768f5dd`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0010` — 8388608 bytes — SHA-256 `0fb8cb630775dc0561d6368e7fbb6374fdae16da602fdbaf61f15385ac11881e`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0011` — 8388608 bytes — SHA-256 `7f7cffbcd996156a967764729fd5d3fc222d22dbd48c1a4f3e8593057a538253`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0012` — 8388608 bytes — SHA-256 `f2c6a023b49573e7197c3512a5a7e550d6efd364d42a5ff9b10eed7094cb40d5`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0013` — 8388608 bytes — SHA-256 `d9a6a80a6224ca7a0cc00b5857cf5b052792a273de32e0a92e0bfb07da3a4ce2`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0014` — 8388608 bytes — SHA-256 `01d8a22121fe9c2086cf994723bf766d04f843b597271d9d75162488a00f246c`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0015` — 8388608 bytes — SHA-256 `8c5139936ca6bc40aab4276371dd47ed2d171689b0b476c65423f09d1c889b38`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0016` — 8388608 bytes — SHA-256 `d061b61e7c9d89b346cc89a94e1e19893f424ad0e5848c6db557b491f67cb80e`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0017` — 8388608 bytes — SHA-256 `cefe1beeade416163d671772174c036d6e09bfe481fd878e56720e8df0584910`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0018` — 8388608 bytes — SHA-256 `ac087f162d1be162697cc4f66c600d916e2fc494d22d65762384ff72a698319a`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0019` — 8388608 bytes — SHA-256 `d8e0686365cf9615d7e6a0c1857c4225fd401616fcbade252ec76e770b164308`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0020` — 8388608 bytes — SHA-256 `6ef695df290f7f3a26443f36eb12b93f918f48c7d16792a9a0ad3d828dbb1375`
- `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz.part-0021` — 140336 bytes — SHA-256 `c0c248a57311a7a1fc719acfc6d3013b762515039d78c5d513f671a33b973270`

Authenticated reassembly and verification:

```bash
git clone --depth 1 --branch artifact/native-repro-bundle-20260824-r1 https://github.com/cosmosapjw-quantum/bass bass-artifact-readback
cd bass-artifact-readback/repro/native/BASS-NATIVE-REPRO-20260824T065249Z
sha256sum -c BUNDLE_MANIFEST.sha256
python3 reassemble_bundle.py --manifest BUNDLE_MANIFEST.json --parts-dir parts --output BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz
printf '%s  %s
' '033b408558b1c908b1604b80ed3f942f9720120c2f15dae0b231ecb4547f8db1' 'BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz' | sha256sum -c -
xz -t BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz
```

To materialize source separately:

```bash
git clone https://github.com/cosmosapjw-quantum/bass bass-source
git -C bass-source checkout --detach 0d1203da778c5e92fce4c9bbf24c8044c5b46018
test "$(git -C bass-source rev-parse HEAD)" = 0d1203da778c5e92fce4c9bbf24c8044c5b46018
test "$(git -C bass-source rev-parse 'HEAD^{tree}')" = 675213f191477b1f47c725892e9f4c804c623ab0
```

If this environment can materialize binary parts, perform the authenticated clone/reassembly above. If it cannot, ask the user for exactly one file: the verified reconstructed `BASS_NATIVE_REPRO_BASS-NATIVE-REPRO-20260824T065249Z.tar.xz` whose SHA-256 is `033b408558b1c908b1604b80ed3f942f9720120c2f15dae0b231ecb4547f8db1`.

Exact environment: Ubuntu 24.04.4 LTS; Linux 7.0.0-29-generic x86_64; glibc 2.39; AMD Ryzen 9 5900X 12-Core; CPython 3.12.3; SOABI `cpython-312-x86_64-linux-gnu`; rustc 1.94.1 (`e408947bf`); cargo 1.94.1 (`29ea6fb6a`); rustfmt 1.8.0; clippy 0.1.94; maturin 1.14.1; WolframKernel 15.0.0 binary; wolframscript 1.14.0.

Gate matrix:

- Cargo vendor/checksums/config/lock/tracked-byte integrity: PASS (176 registry packages, 176 dirs, 8,397 vendor files).
- Cargo metadata offline: PASS. Cargo workspace test offline: PASS, 122 passed.
- Cargo fmt: FAIL. Cargo clippy `-D warnings`: FAIL.
- Offline maturin wheel build and independent import/call: PASS.
- Native differential: PASS, 112 passed.
- Background/classification/constraint: PASS, 174 passed.
- E1-E4: PASS, 74 passed plus 46 subtests.
- Compiler full: FAIL, 92 passed and one generated-byte failure.
- Full feasible Python: FAIL, 1,833 passed, three failed, 46 subtests, one warning in 1,768.62 seconds.
- M11 rays and CMB: NOT_RUN; exact commands are in TEST_MATRIX.json.
- Python/SymPy to Rust: FAIL. Type-II `--verify`/`--check` input binding mismatch; PSTF and coefficient-table drift; Riemann and thermo byte-identical. Tracked source was not overwritten.
- Wolfram/xAct environment: BLOCKED_NO_VALID_WOLFRAM_LICENSE (Kernel exit 63 before package probe). Project replay: BLOCKED_NO_PROJECT_DRIVER. No xAct-to-Rust claim.

Authority chain:

- Historical formula-authority SHA label: `3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361`; named formula bytes ABSENT, so that lane is BLOCKED.
- SymIR SHA-256: `f7585b05d629ee6aff4bd7274f2bc20aca0ffbdf94af2e6e8c29e46bb8004b70`.
- Scalar lowering SHA-256: `57a4d5aab9f5df084062f0cca56bf6a4ecbd002b2da0b3baeae52a15557e227a`.
- Historical generated-bundle SHA label: `ea1b0bbf981a28ecaf1a2db09fe59c8f41e124c2e1451145833ea1bfcf4b1cde`.
- Current four-file recomputation: `a8e9154044e399e1b0f9eb700020f689593183d64ea6861ec674b8786f853bfe`; mismatch is tied to current polarized `mod.rs` versus stale scalar manifest.

Audit summary:

- PHYS-MATH: metric `(-,+,+,+)`, units, signs/orientation, boundary/initial domain, cold-delta firewall, selected conservation/positivity regression are PASS; PSTF normalization provenance is P0 CONCERN; analytic limits are P1 CONCERN because M11 was not run; formula bytes and xAct replay are P0 BLOCKED. Plot lane NOT_APPLICABLE.
- PHYS-MATH-CODE: offline Cargo test/native import/differential/background/E1-E4 are PASS; fmt/clippy, R5b strict parity, compiler generated-byte, Type-II binding, and PSTF/coeff replay are FAIL; M11 NOT_TESTED; xAct BLOCKED. No silent collisional fallback was used.

Failed attempts and retry policy:

- gh 2.45 rejected unsupported `--slurp`; one syntax-adjusted `--paginate --jq` retry passed.
- unprivileged `unshare -n` was blocked; no retry, with offline Cargo/vendor as core evidence.
- a post-build verifier initially treated expected `target/` outputs as forbidden; one tracked-only adjustment passed all 598 source files.
- staging exclusion initially confused vendored `cc/src/target` with build target; one exact-path adjustment passed.
- archive global-sort assertion exceeded GNU tar depth-first semantics; one header-check adjustment passed, while two full archive builds were byte-identical.
- artifact README trailing whitespace stopped the pre-commit check; one whitespace-only correction passed before the sole commit.
- Deterministic Cargo/codegen/parity failures were not retried. No timeout occurred. Never retry the same failure more than once without a changed precondition.

Unresolved blockers and forbidden claims: required fmt/clippy are red; two R5b parity cases are red; codegen/receipt provenance is red; formula bytes are absent; M11 is unrun; Wolfram license/driver are blocked. Do not claim full solver readiness, numerical maturity, output/statistics/publication readiness, performance, native end-to-end Wolfram replay, production collision wiring, or scientific authority promotion.

Exactly one DAG-correct scientific next step after the mandatory remote evidence readback is `BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING`, as named by the canonical recovery state. Do not merge main, merge either branch, ready/merge the draft PR, alter scientific tolerances, or promote any claim without explicit user approval.
