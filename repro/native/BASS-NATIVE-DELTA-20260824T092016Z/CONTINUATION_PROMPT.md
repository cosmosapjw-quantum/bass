Continue BASS from the delta-only native recovery state. Do not start the recovery from scratch, modify immutable r1 evidence, or rerun a PASS merely for reassurance.

FIRST ACTION — AUTHENTICATED REMOTE READBACK

Run these read-only commands first. The closeout commit and draft-PR identities are external self-references created after the atomic commit containing this prompt, so authenticated remote readback—not an embedded guessed SHA—is authoritative for them.

```bash
git ls-remote --heads https://github.com/cosmosapjw-quantum/bass \
  refs/heads/artifact/native-repro-bundle-20260824-r2 \
  refs/heads/agent/recovery/native-repro-closeout-20260824-r2 \
  refs/heads/agent/recovery/native-repro-delta-fixes-20260824-r1 \
  refs/heads/agent/recovery/background-evolution-v87-integrated-20260824

gh pr list --repo cosmosapjw-quantum/bass --state all \
  --head agent/recovery/native-repro-closeout-20260824-r2 \
  --json number,url,state,isDraft,headRefOid,baseRefName,mergeStateStatus

git clone --depth 1 --branch agent/recovery/native-repro-closeout-20260824-r2 \
  https://github.com/cosmosapjw-quantum/bass bass-native-closeout-r2
python3 -m json.tool \
  bass-native-closeout-r2/repro/native/BASS-NATIVE-DELTA-20260824T092016Z/REMOTE_ARTIFACT_RECEIPT.json
```

The artifact head must read back as `61045b6e5a0d7b026437e0d3586df66706578161`; the delta head must be `bff2852af3536d0d9e8badc3e5e2ad024f299278`; the canonical head must remain `0d1203da778c5e92fce4c9bbf24c8044c5b46018`. The closeout head must equal both the branch readback and the draft PR `headRefOid`. Do not merge or mark the PR ready.

If this environment can materialize binary parts, authenticated-clone r2 and use the manifest-declared order as shown below. If it cannot, ask the user for exactly one file: the verified reconstructed `BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz`. Do not ask for r1 or individual parts.

CANONICAL SOURCE

- repository/visibility: `https://github.com/cosmosapjw-quantum/bass`, private
- canonical branch: `agent/recovery/background-evolution-v87-integrated-20260824`
- canonical commit: `0d1203da778c5e92fce4c9bbf24c8044c5b46018`
- canonical tree: `675213f191477b1f47c725892e9f4c804c623ab0`
- Cargo.lock SHA-256: `d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`
- historical-anchor ancestry at delta: `PASS_DESCENDANT`

IMMUTABLE R1 EVIDENCE — DO NOT MODIFY OR REASSEMBLE FOR REASSURANCE

- artifact: `artifact/native-repro-bundle-20260824-r1` at `3030887d999cf5d6ce9d4a2505552b10f3ab595b`
- archive SHA-256: `033b408558b1c908b1604b80ed3f942f9720120c2f15dae0b231ecb4547f8db1`
- content manifest SHA-256: `fb9cffaea6213c4f74b9bd244197cb0ccc970e5299bd98d4417c925a41007dfa`
- bundle manifest SHA-256: `c981bc7c13d2f68564941ba74830542039d61b05ea7972d7244b0b24f509c1ae`
- wheel SHA-256: `b1661295a9e5a7e9a9f1260e8c8ea5e26aef00e13a4e8530d0746a7d9ad1eb46`
- closeout: `agent/recovery/native-repro-closeout-20260824-r1` at `e2d0b3670534d51af61bcd7bb2160fb279378127`
- PR #19: OPEN, draft, unmerged; do not amend, rebase, ready, merge, or close it

DELTA BRANCH AND DELIVERY

- review delta branch: `agent/recovery/native-repro-delta-fixes-20260824-r1`
- delta commit/tree: `bff2852af3536d0d9e8badc3e5e2ad024f299278` / `603791eee595dac4ec8c9f177d53842695b3932f`
- delta commit URL: `https://github.com/cosmosapjw-quantum/bass/commit/bff2852af3536d0d9e8badc3e5e2ad024f299278`
- artifact branch/head: `artifact/native-repro-bundle-20260824-r2` / `61045b6e5a0d7b026437e0d3586df66706578161`
- artifact commit URL: `https://github.com/cosmosapjw-quantum/bass/commit/61045b6e5a0d7b026437e0d3586df66706578161`
- artifact path: `repro/native/BASS-NATIVE-DELTA-20260824T092016Z`
- closeout branch: `agent/recovery/native-repro-closeout-20260824-r2`; obtain its exact commit and unique draft-PR URL with the mandatory first-action readback because those identities cannot be embedded in the commit they identify
- canonical branch remains the PR base; neither delta nor closeout is promoted authority

R2 ARTIFACT

- archive filename: `BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz`
- archive size/SHA-256: `175949544` / `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`
- deterministic second-build SHA-256: `ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca`
- content manifest SHA-256: `61e4216d23ec33949e621b78ea2da1a755cd2d154741532b298a63ac48d4f91a`
- bundle manifest SHA-256: `d7cf9758afc1c8395f5f7bcca0b8f38cb788640a340edb42bce379f75ccfba8f`
- bundle manifest sidecar SHA-256: `94dca1d4a35200ac33223ade4fbf9f82d26b935ff0c598a925a23be044510ae6`
- reassembler SHA-256: `8510e3ace35793443160b0f219c0ba63b4bbf1a66212ffc8b3f42b026cebaa53`
- part count/caps: `21`, each at most `8388608`, archive at most `268435456`, at most `32` parts
- remote verification: normal push PASS; local/remote commit exact; fresh shallow clone PASS; ordered reassembly PASS; XZ PASS; 8,592-file content manifest PASS

ORDERED PARTS — ORDER IS AUTHORITATIVE

```text
0000  8388608  01b8007c25ab89c42d37547507bab820e2caff7c10955b4cf434078c09ba5050  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0000
0001  8388608  4d1dac7f9d5a821ddd036d11176250f9857c6c6b654d1a09d16d1c6634ec3e3c  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0001
0002  8388608  c02460702682e04547cfdf2b87e829b41c948d6b8fabbb3dea07de1155209dce  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0002
0003  8388608  69044145a8f104440720bdfd7996c04e64e39a20d2a0b4fd2713ad1148270edd  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0003
0004  8388608  36148cf8b99a1db6172ac71722d6a3d7d82c99ecd7dfb68966bbfb8a3cf7d218  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0004
0005  8388608  30303ebfe519845de35e201cb86ce1cad56776f44cd13157ec136e1139c318e6  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0005
0006  8388608  95188938b0904325ffffdf7eb523da219c82891060dfe57b8db00b7fe3ce03df  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0006
0007  8388608  dd75bf0f2be0ecb93a9e258b2e95be63e8ffb341cc8ddcb8b81f783cb7db83fa  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0007
0008  8388608  bdd2d90d1e2d94b734e9c4bd20c899a24761debeaa83f5da4908b5c7f79b325f  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0008
0009  8388608  a64652540db575238550344ed78b741edacca7ed8b468edb2e5457f1bcdc3702  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0009
0010  8388608  f66b45475ad1637c0a4890a654c1a22782c4a343f151d5f023ae923459740a52  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0010
0011  8388608  25a26908f5b13df36b0974ad5caf34888d0a0e38843a75690b678469f308ee99  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0011
0012  8388608  bc5c05f4257103b3b0c828985f51ed496ef74284939f58cae90b1a22957ec5bc  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0012
0013  8388608  823aff5d5f91331f2554668b397b0676d18e928bc65c2993388ab89ca614dd81  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0013
0014  8388608  f7b6bf334605063a992c4aff61c91b462f0dadc1e15b46fda2ad1df8b10af4db  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0014
0015  8388608  c1d0777ce5bc6574057cb702945ccfed9689b2fc203f7eff3cbcae4c8f2c6b56  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0015
0016  8388608  aa9a08ccb01b36b85f7af6da3e7d93b182e03f9a93fcbc936e136453ad6a531c  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0016
0017  8388608  f9b01c2f5c784a3f5fb105cf0499eff9924cbe5b839f129d40dd79cba2d98d38  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0017
0018  8388608  5021ea78a8321842f1d54faea1b898d8a24c11b925232e00d5b925fe861add1c  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0018
0019  8388608  9aa07c9d3562604d42892aaa377d784fd52955ab4d307952ca172960ee228e98  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0019
0020  8177384  ae66d41f59836f1abf19e2b5a6728c6a24fa9d08557cba203292954844130449  BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz.part-0020
```

AUTHENTICATED REASSEMBLY AND RESTORE

```bash
git clone --depth 1 --branch artifact/native-repro-bundle-20260824-r2 \
  https://github.com/cosmosapjw-quantum/bass bass-native-artifact-r2
cd bass-native-artifact-r2/repro/native/BASS-NATIVE-DELTA-20260824T092016Z
test "$(git rev-parse HEAD)" = 61045b6e5a0d7b026437e0d3586df66706578161
sha256sum -c BUNDLE_MANIFEST.sha256
mkdir reconstructed
python3 reassemble_bundle.py \
  --manifest BUNDLE_MANIFEST.json \
  --parts-dir parts \
  --output reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz
printf '%s  %s\n' \
  ef0f35b76ab4ef4877ed577afe391ed677a7a6767bcbc64db62dd853d757afca \
  reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz \
  | sha256sum -c -
mkdir reconstructed/extracted
tar -xJf reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz \
  -C reconstructed/extracted

export BASS_CARGO_BIN="$(rustup which --toolchain 1.94.1 cargo)"
export BASS_RUSTC_BIN="$(rustup which --toolchain 1.94.1 rustc)"
reconstructed/extracted/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z/scripts/restore_and_verify.sh \
  --repo-url https://github.com/cosmosapjw-quantum/bass \
  --source-commit bff2852af3536d0d9e8badc3e5e2ad024f299278 \
  --expected-tree 603791eee595dac4ec8c9f177d53842695b3932f \
  --bundle reconstructed/BASS_NATIVE_REPRO_BASS-NATIVE-DELTA-20260824T092016Z.tar.xz \
  --dest /tmp/bass-native-r2-verified-restore \
  --python /usr/bin/python3.12
```

The destination must not already exist. The script fails closed on repository URL, commit/tree/anchor, lock/config, exact vendor/wheelhouse sets and hashes, nonregular files, host Cargo overrides/config, tool versions, Cargo tests, wheel, import, and deterministic call.

TOOLS AND ABI

- rustc: `rustc 1.94.1 (e408947bf 2026-03-25)`
- cargo: `cargo 1.94.1 (29ea6fb6a 2026-03-24)`
- rustfmt: `rustfmt 1.8.0-stable (e408947bfd 2026-03-25)`
- clippy: `clippy 0.1.94 (e408947bfd 2026-03-25)`
- Python: `CPython 3.12.3`, SOABI `cpython-312-x86_64-linux-gnu`
- maturin: `1.14.1`
- OS/kernel/glibc: `Ubuntu 24.04.4 LTS`, `Linux 7.0.0-29-generic x86_64`, `2.39`
- CPU/compiler/linker: `AMD Ryzen 9 5900X 12-Core Processor`, `GCC 13.3.0`, `GNU ld 2.42`
- native wheel: `bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl`, `1049130` bytes, SHA-256 `b58fe7400c51cf0016b877a681758ebb9896d07cfb3f80be7ca82df64b734d10`

AUTHORITY AND CODEGEN HASHES

- historical formula-authority label: `3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361`; bytes `ABSENT`, mapping `UNMAPPED`
- historical scalar-only generated label: `ea1b0bbf981a28ecaf1a2db09fe59c8f41e124c2e1451145833ea1bfcf4b1cde`
- current Type-II composed bundle: `a8e9154044e399e1b0f9eb700020f689593183d64ea6861ec674b8786f853bfe`
- Type-II manifest file: `5a8f05b917a7134584052167d5ece0c787a1f2683f347316ec6260844a5d19f4`
- coefficient generator/table: `94fbac7190ea0a03fed01be686f365bd8b0a95b017c5bbf71fbc11a174c90d9a` / `bbde0a4ee583ba013a81742843b889191303f927072d3874ebb8a9ea28803665`
- PSTF generator/table: `08324163ef3dfed192ec503c4d5ac072de43b0b2974852aa793b255b8e2e169b` / `34dbffaf24196ce656659f5f718b7ff5328904892e4d5b88d061953a215ba808`
- Riemann/thermo generated: `ab2bc8b338411a9195c9bffd591081a0fb64707c3a79158f3f3446edf6d46dec` / `cb14b504f7a74d83b8bd22277a50fc20c5f4df91f5cc2b01979a85b1f070cdb6`
- authority-chain/codegen result: `5da4898cc4f4d777b56599cf43dd094bc08f8b4cd6546e3477ebd8af0228994a` / `04788c2217858c0ce016c99f8cfe79f6596bc2cf5a72586df5560aac8a7c22ca`
- packaged evidence-reuse map: `2d052f757a1da6c5aebb2d38123de225be97282e2ab9639a8f5dd8f606ac16dd`

REUSED PASS RECEIPTS

R1 predates the formal receipt-key schema. Do not invent historical keys. Import the following as `LEGACY_R1_RECEIPT`, anchored to r1 `TEST_MATRIX.json` SHA-256 `5a8a60df5cfd23fa27de80eefc039a433ff96ff1a83c7d8e443437d50b7b17c9`, `FINAL_RESULT.md` `c85010137d05c00c6d0a35b1c0dfc817a67f3116bf9bd974b14af6985202edbd`, `FINAL_INDEPENDENT_REVIEW.md` `5fdf2214f48cb4b4755e54874ce69aaf5b54948ac90b56b77a2d64595617a7f2`, canonical source/tree, Rust 1.94.1, and the exact commands/environments in the artifact evidence map:

- Cargo vendor/checksum/config/lock integrity and offline metadata: REUSED because Cargo.toml/lock/config/vendor/toolchain/crate-root/offline dimensions are unchanged; r2 independently proved 176 directories, 8,397 files, and exact receipt hashes without fetch/vendor.
- background/classification/constraint: REUSED, `174 passed`; lane-relevant Python/scientific source, fixtures, equations, tolerances, references, seeds, grids, ABI, and backend paths unchanged.
- E1–E4: REUSED, `74 passed plus 46 subtests`; lane-relevant electron source/fixtures unchanged.
- r1 deterministic archive/push/readback: retained only as immutable r1 lineage, not as proof of r2.

FORMAL DELTA RECEIPT KEYS

```text
DELTA-TYPEII-BIND-001                 PASS                         211aea74a84015da6a1792a053f7253587323a92e94765ab3e39765f35b203cd
DELTA-TYPEII-REMAP-001                PASS                         360a052d6abf6b159c4dbde791d76b77d85010d6bb126260c9d952d10803a819
DELTA-TYPEII-MANIFEST-001             PASS                         14079ea5487290fc2791eb2bd456d74ac17c4ee4bb3f7bb575e65079c04049bd
DELTA-COEFF-CODEGEN-001               PASS                         eba7608848a5deee50744f18afedaf029a57ae556323dcba53f03891541543f6
DELTA-PSTF-CODEGEN-001                PASS                         fbb39c0a7c48b1de71a9a5dc57b9e18b85876fc47756e2615f520f6572cf00d2
DELTA-GENERATED-RUSTFMT-001           PASS                         6fcc5113cff4ea824bca14c7ad96bb733c0d53d89c98ab160fd58105fd12767e
DELTA-CARGO-FMT-001                   PASS                         0cf49585ff603c8aec8ba87e54b2cda34f2a4b233495e6867afb6d9d9e83456b
DELTA-CARGO-CLIPPY-001                PASS                         533b49c95f6d8339be5c8e3d37f312659d3426dc87f92b874dbb15d780fb026e
DELTA-CARGO-WORKSPACE-TESTS-001       PASS_WITH_LATER_FOCUSED_CLOSURE  9dd7eaf245a1d5073711c5c0d35eaf8e776ad078d4b9d7727755293e6b9cf0f3
DELTA-QSPHERE-RUST-001                PASS                         cd0642e758f328e2edd8fc8e5586fafe728298092ac1722dc96f311c3631611f
DELTA-NATIVE-WHEEL-BUILD-001          PASS                         c2c0dc8b53e0aff608c211647aaba497b153d56cecb86de8764dc247a0c69f12
DELTA-NATIVE-IMPORT-001               PASS                         cf80096ca1da6fd6fdd9587e1762cb1998ad3860942d7a0221c9cd40c7738e0b
DELTA-QSPHERE-PYTHON-001              PASS                         d1c35abd7b9d9188270771e6838113fda1baf56cc37e51549c096f5be7b9cb5f
DELTA-NATIVE-DIFFERENTIAL-001         PASS                         f885795660bc59829471f894b00415891950d3f32137adf8544f8450268ff1d7
DELTA-REUSED-R1-DEPENDENCIES-001      PASS                         3978eb5c4ba9121fa0654ebe264cbadbd36172e0de7c762108066a57171644a9
DELTA-R5B-HYBRID-DIAGNOSTIC-001       DIAGNOSTIC_INCONCLUSIVE      b3ba15ea09206f4d912439592c3119a4ce51bf36508c6502582f1621abfeec66
DELTA-R5B-NALGEBRA-BUILD-001          PASS_EXPERIMENT_ONLY         b13f0fd461829620a1089e913404733173bf61f5633bfa41f0f479903200ec7f
DELTA-R5B-NALGEBRA-PARITY-001         FAIL_EXPERIMENT_REJECTED     b5b9644b31d860df006cebfa84d47df36ed07b831648aad0ff33d2ad3e3a0a85
```

The earlier report-only native key strings `2d4d5a2a2e24f6b404621e4375ffcc24a4d6e11fce05c51b0a239addb078fb1f`, `ae35754ef14480003dbb16894a6c6b7e953201e0bd0dc9564dba9f86ad39cfbd`, and `515b91a339500321f84cb9030bbb77fb1791e4a6789a40541501a2baefb87c07` are non-authoritative annotations because their canonical material was not retained; use only the replacement keys above.

FIXED / STILL RED

- PASS: FMT-001, CLIPPY-001, TYPEII-BIND-001, CODEGEN-BYTE-001, GEN-MANIFEST-001, COEFF-DRIFT-001, PSTF-PROV-001, QSphere review boundary, Type-II legacy-count claim correction.
- PASS: Python/SymPy→Rust generation for Type-II, coefficients, PSTF, Riemann, and thermo under generator-owned contracts. No final byte drift remains; this is not formula or xAct authority.
- PASS: offline final wheel, independent import/backend/call, QSphere fail-closed boundary, native differential 112, fresh restored Cargo workspace 123.
- BLOCKED R5B-001: canonical True-frozen q absolute difference `2.6915318931952648e-17`; discarded candidate closes only this node.
- BLOCKED R5B-002: canonical True-ratio_scalar q absolute difference `5.3830637863905295e-17`; unchanged under candidate.
- BLOCKED formula bytes: historical label exists but source bytes are absent/unmapped.
- OPEN project Wolfram replay; no xAct-to-Rust connection.
- NOT_RUN: full collection/full suite and M11; background/E1–E4 are reused, not rerun.

COMMANDS ACTUALLY RERUN AND CHANGED PRECONDITIONS

- `generate_typeii_fixture.py --write/--verify/--check`: receipt input changed to authoritative B1, then dependent manifest hashes changed; both smallest rebind cycles PASS and fixture output bytes remained identical.
- `pytest -q compiler/validation/test_typeii_polarized_remap.py`: remap reduction implementation changed; 8 PASS.
- `pytest -q compiler/tests/test_rust_typeii_lowering.py compiler/tests/test_rust_typeii_polarized_lowering.py`: manifest ownership/generator changed; 8 PASS.
- four repository generators plus `pytest -q tests/test_codegen_reproducibility.py`: generator/checked bytes changed; 8 PASS. Riemann/thermo numerical expressions stayed unchanged except formatter attributes/lint ownership.
- `cargo fmt --all -- --check`: tracked Rust/generator format contracts changed; PASS.
- `cargo clippy --workspace --all-targets --locked --offline -- -D warnings`: lint-root source changed; PASS.
- `cargo test --workspace --locked --offline`: semantic Rust changed, then new r2 delivery materialization required a fresh gate; final archive restore reports 123 PASS.
- final focused `kinetic::sphere::tests`: review repaired public short-input behavior; 5 PASS before the later fresh full workspace gate.
- offline `python -m maturin build --release --locked --offline`: final reviewed native source and empty Cargo home/target changed; PASS.
- fresh no-index import/backend/deterministic call and QSphere probes: final wheel changed; PASS.
- `PYTHONPATH=. python -m pytest -q tests/test_rustcore_differential.py`: changed native/generated/common bindings required this smallest common closure; 112 PASS.
- exact two R5b nodes ran once only after a disposable nalgebra-LU precondition change; 1 PASS/1 FAIL, candidate rejected. Controls/group/full suite were not run after required failure.
- hardened restore ran for staging and again for the final part-reassembled archive because archive materialization/path is a distinct delivery-key dimension; both PASS exact dependency checks/Cargo 123/native call.
- two deterministic archive builds, 21-part split, local reassembly, normal push, SHA readback, fresh shallow clone, remote reassembly/XZ/content manifest: PASS.

DELIBERATE NON-RERUNS

Do not rerun the 1,849-test collection, 1,833-pass feasible suite, background/classification/constraint, E1–E4, native differential, full Cargo workspace, artifact readback, M11, or Wolfram unless a recorded lane-relevant key changes or the user explicitly requests it. The r2 delivery gate has already run full Cargo 123 and fresh remote artifact readback.

WOLFRAM WORK-MODE RECEIPT

- receipt: `WOLFRAM-WORKMODE-20260824-R1`
- kernel: Wolfram Language 15.0.1 Linux x86-64
- xAct archive SHA-256: `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`
- xPerm 1.2.4 / xTensor 1.3.0 load: PASS
- dummy-index canonicalization residual: `0`
- abstract 3D PSTF projector: idempotence/traces/symmetries residuals `0`, rank `5`
- xAct probe source/result SHA-256: `c69d45eba977d5c61719b425a7ae43e6bce1a6793831648f1643514a85d10553` / `769181d3cb9151ab0167bcc2f09d9ca4b76a65b97b74d8e8f24514c1c798003d`
- PSTF probe source/result SHA-256: `1ae0d7f3d2a4d2e51cd846ba7baa635d1c5290e13514265304f1eca79413f93d` / `dacf3f7b8d4bb33533b3c739480102a8a9b5378b7b7e131728ac65ff0ab1532c`
- project driver/formula bytes: absent; project replay OPEN
- do not run Wolfram locally; export newly found driver/formula bytes with hashes to ChatGPT Work mode

PHYS-MATH LEDGER

- PASS: metric signature `(-,+,+,+)`, units unchanged, signs/normalization unchanged, exact PSTF indices/projectors, boundary/initial inputs unchanged.
- NOT_TESTED: conservation/positivity and analytic-regime claims outside impacted delta.
- CONCERN P1: R5b strict parity.
- NOT_TESTED P0: project formula authority due absent bytes/driver.
- overall: CONCERN; plot lane NOT_APPLICABLE; no new scientific dataset or figure.

PHYS-MATH-CODE LEDGER

- PASS: Type-II equation→generator/code scope, actual native runtime path, CPython ABI, generated provenance, QSphere regression boundary, no silent fallback.
- CONCERN P1: Python/Rust parity only for the two R5b nodes and their cancellation sensitivity; the separate 112-case native differential PASS does not close them.
- CONCERN P2: missing R5b acceptance contract; broad suites intentionally not rerun.
- NOT_TESTED P0: xAct-to-Rust provenance.
- overall: CONCERN.

CARGO BUNDLE DECISION

`NEW_IMMUTABLE_R2_PUSHED_AND_REMOTE_READBACK_PASS`. R1 vendor/config/lock and Python wheelhouse bytes were reused exactly; no network `cargo fetch` or `cargo vendor` ran. R2 was mandatory because native/generated source and the native wheel changed. Never alter r1 or r2; a future payload change requires r3.

FORBIDDEN CLAIMS

No full solver readiness, numerical maturity, publication readiness, performance, xAct-to-Rust replay, production collision wiring, scientific-authority promotion, formula authority, tolerance/reference change, canonical-source promotion, main merge, or PR merge/ready transition without explicit user approval.

EXACTLY ONE NEXT ACTION

Ask the user for the scientific acceptance decision for R5b: must authority retain the current relative comparison of cancellation-derived endpoint error scalars, or may it use a scientifically justified state/residual parity contract? Do not implement a tolerance/reference change. Do not start `BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING` until both engineering RED entries are closed.
