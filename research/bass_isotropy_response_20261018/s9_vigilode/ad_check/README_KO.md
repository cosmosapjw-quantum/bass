# S9의 독립 num-dual callback oracle

`num-dual 0.15.1` 원본을 사용해 고정 cohort bank의 primal RHS를 방향 자동미분한다. 실제 production의 해석적 JVP 또는 `partial_t` 구현을 dual 함수 안에서 호출하지 않는다. source-frame 방향, birth 좌표와 energy, weights는 고정하며 새 ODE history나 KL projection은 실행하지 않는다.

패키지 원본은 `vendor/num-dual-0.15.1`에 있고, 공식 tag는 `v0.15.1`, commit은 `c5f544267ffebf5c50fbd0f016533f75ca84dd0e`이다. 양쪽 upstream license와 원본 31개 파일의 Git blob/SHA256 증빙을 보존했다. `default-features=false`이며 lock에 실제 필요한 dependency는 `num-dual 0.15.1`, `num-traits 0.2.19`, `autocfg 1.5.1` 세 개뿐이다.

## 테스트와 빌드

checker를 upstream의 workspace 밖에 두기 위해 **`checker/Cargo.toml`**을 사용한다. 원본 upstream manifest는 바꾸지 않는다. 일반 Cargo cache가 준비된 NCP에서는 다음 명령을 실행할 수 있다.

```bash
cargo test --locked --manifest-path checker/Cargo.toml -j 1 -- --nocapture --test-threads=1
cargo build --locked --manifest-path checker/Cargo.toml --bin bass-s9-ad-check -j 1
```

제공된 offline vendor를 사용할 때의 복사 가능한 sandbox 명령은 다음과 같다. 환경이 달라지면 도구 경로와 vendor 경로를 해당 runtime으로 지정한다.

```bash
BASS_AD_ROOT=/workspace/scratch/f49816986ef8/bass/research/bass_isotropy_response_20261018/s9_vigilode/ad_check
BASS_AD_CARGO=/tmp/rei_run15_salvage/recovery/toolchain/prefix/bin/cargo
BASS_AD_RUSTC=/tmp/rei_run15_salvage/recovery/toolchain/prefix/bin/rustc
BASS_AD_RUSTDOC=/tmp/rei_run15_salvage/recovery/toolchain/prefix/bin/rustdoc
BASS_AD_VENDOR=/workspace/scratch/f49816986ef8/vigilode_reference/vendor
env RUSTC="$BASS_AD_RUSTC" RUSTDOC="$BASS_AD_RUSTDOC" "$BASS_AD_CARGO" test \
  --offline --locked --manifest-path "$BASS_AD_ROOT/checker/Cargo.toml" \
  --target-dir /tmp/bass_s9_ad_target -j 1 \
  --config 'source.crates-io.replace-with="supplied-vendor"' \
  --config "source.supplied-vendor.directory=\"$BASS_AD_VENDOR\"" \
  -- --nocapture --test-threads=1
```

9개 단위 검산은 세 bank, signed shear, 여러 \(b\), 다섯 상태 방향을 사용한다. ordinary binary64 callback 비교 gate는 실행 전에 `5e-13`으로 고정했고 angular moment gate를 바꾸지 않는다. 결과와 source hash는 연구 lane의 `evidence_s9/theory_review/`에 있다.

## 실제 adapter와의 비교

```bash
python compare_callbacks.py \
  --adapter /workspace/scratch/f49816986ef8/s9_runtime/target/debug/bass-s9-vigilode \
  --oracle /tmp/bass_s9_ad_target/debug/bass-s9-ad-check \
  --output-dir /tmp/bass_s9_fresh_callback_comparison
```

output directory는 반드시 새로운 경로여야 한다. helper는 입력·사전 기준·실제 Rust 출력·AD 출력·각 subprocess log·실패 receipt를 보존한다. 다섯 고정 bank의 190 query vector, 서로 다른 38 bank/state point를 대조한다. 마지막 두 bank는 같은 state/time에서의 donor-transfer event 앞/뒤이다. 세 `partial_t=0` 대조와 한 stale pre-birth `partial_t` 대조가 기준을 위반해야 성공이다. 이 helper는 기존 history를 재실행하지 않는다.

## 공개 Rust API와 텍스트 입력

`FrozenBank { cohorts, donor_amplitude, cosmological_constant }`와 `Cohort {u,b_birth,energy_birth,mu,alpha}`를 만든다. 여기서 `donor_amplitude=donor0*exp(-decay_lambda*exposure)`이고 interval 안에서 고정이다.

```rust
let check = bank.oracle(x, [h, b, y], time_seed, [vh, vb, vy])?;
// check.rhs, check.jvp, check.partial_t, check.total_direction
```

`directional_ad`는 저장된 birth data를 고정한 local JVP이다. S8 전체 parameter tangent의 birth-memory 미분과 구분한다. API는 모든 alpha의 양성, 정확한 reflection, 유효한 h/시간/ray domain을 검사한다. 정규화나 moment를 고의로 깨뜨린 음성 대조도 관측해야 하므로 이 oracle은 source를 다시 정규화하거나 projection하지 않는다.

binary는 다음 텍스트를 받아 JSONL을 쓴다. 기존 출력 파일이 있으면 실패한다.

```text
CASE case_id x h b y donor_amplitude Lambda time_seed vh vb vy
COHORT u b_birth energy_birth
RAY mu alpha
RAY mu alpha
END_COHORT
END_CASE
```

ray는 저장된 reflection pair 전체를 나열한다. 실제 callback 비교 script가 이 protocol의 입력을 자동 생성한다. new-source admission과 native finite-bin conservation은 production adapter 및 별도 raw evidence의 의무로 유지한다.
