# S8: 원본 spectral owner를 유지하는 native angular refinement

## 상태와 출발점

**새 native angular support 확장 코드와 개발 검증을 준비했다. 18개 과학 case는 아직 실행하지 않았다.**
S8 사전등록·코드의 Git 게시, 두 클라우드 백업과 readback은 root가 수행하고,
그 게시 증거를 runner가 확인한 뒤 과학 캠페인을 실행한다.

이 작업은 `physmath-research-loop` plugin **1.3.0**, 선택 범위 **C2–C9**를 따른다.
`SKILL.md`, `references/POLICY_INTEGRATION.md`, `references/CODING_LOOP.md`를 읽었다.
기본 구현 검증과 `/root/s6_rank1`의 한 번의 독립 검토로 범위를 묶는다.
첫 탐색에서 읽은 사용자 저장 skill의 내장 규약 1.0.0 대신, 명시적으로 선택된
plugin 1.3.0의 단계 경계를 적용했다.

연구 이전 새 실행결과 확인은 root의 fresh Git/PR 및 두 `/BASS_BACKUPS` intake를 재사용한다.
이 단위에서는 이미 완료된 S7 native R1/R2를 다시 실행하지 않는다.
원래 physical execution의 게시 커밋은
[`2865f60bf0a247eaab4997c222ad82ae22a4c8fa`](https://github.com/cosmosapjw-quantum/bass/commit/2865f60bf0a247eaab4997c222ad82ae22a4c8fa),
R2 exact observer의 게시 커밋은
[`c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a`](https://github.com/cosmosapjw-quantum/bass/commit/c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a)다.

재사용 raw의 decoded SHA-256:

```text
4b544414a434abfb56edbf38c89807aa221b3083185bcfc2499e9f53f6db8122
```

Runner는 S7 원래 raw·분석·receipt와 R2 분석·receipt의 다섯 hash를 확인한다.
`n_mu=32`, `b0=.6,.9`, prior/P2/P24의 여섯 case만 baseline 표에 가져온다.
그중 네 case에는 실제 측정값이 있고 두 case에는 구체적인 feasibility 실패가 있다.
완료된 출처와 숫자는 [S7 보고서](S7_NATIVE_COHORTS_KO.md),
[S7 R2 분석](evidence_s7_native/revalidate_r2/ANALYSIS_R2.json)에 보존되어 있다.

## 1. Owner의 32-ray 제한과 공개 API를 통한 확장

고정 owner는
[`cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/0e25846433170d0f420c4cda44a0bedbf02cd177)이다.
`native_owner_manifest.json`의 원래 57개 파일은 수정하지 않는다.

`axbi_sources.rs`에서 `AxbiSource::new`가 호출하는 내부 `angular(n)` 함수는
8/16/32만 허용한다. 그러나 `AxbiSource`는 `Clone`을 제공하고
`angular_cells: Vec<AngularCell>`을 공개한다. `CovariantTransport::new`는
angular 배열의 비어 있음만 검사하며, 32개 상한을 두지 않는다.
`cell_count`, `ray_geometry`, `inventory`, `add_delta`, `inject`는 실제 배열 길이와
ray-major indexing `ray*n_energy+bin`을 사용한다.

새 `native_angular_refinement.rs`의 `refined_source`는 다음 순서로 동작한다.

1. 원래 `AxbiSource::new(nH0,.2,32,32)`로 source를 만든다.
2. source를 clone하여 private `nH0`, escape fraction과 모든 spectral data를 유지한다.
3. 새 locally isotropic birth라는 명시적 declaration을 확인한 뒤 공개 angular 배열만 바꾼다.
4. 양의 Gauss–Legendre 64/128/256 배열을 넣고 원래 `CovariantTransport`를 구성한다.
5. 모든 spectral cell의 하한·상한·평균 에너지·photon fraction, normalization diagnostics와
   tail fraction을 `f64::to_bits`로 비교한다. source rate도 같은 방법으로 비교한다.

Source rate의 시간 의존성, blackbody source-cell normalization, spectral GL8 적분,
energy-bin 경계와 native deposition 함수는 원래 owner가 계산한다.
고정된 `native_adapter.rs`, `balance.rs`, `balance_p24.rs`에도 수정이 없다.

새 GL 함수는 원래 owner와 같은 Legendre recurrence, Newton 시작점, 최대 32회 반복,
`2*EPSILON` 정지 기준과 좌우 mirror assignment를 사용한다. 새 함수로 만든 32개
node/weight가 원래 owner의 32개와 **bit 단위로 일치함을 개발 테스트에서 확인했다**.
32개에서의 이 검사는 generator compatibility 검사이며 S7 physical case의 재실행이 아니다.
새 support는 finite, strictly sorted, `|nu|<1`, strictly positive weights,
reflection parity와 normalization을 검사한다.

Gauss 규칙의 양의 weights와 degree `2n−1` polynomial exactness는
[DLMF §3.5(v)](https://dlmf.nist.gov/3.5#v)의 구성 성질이다.
실제 finite-d response의 정확도는 아래 별도 kernel reference 비교로 측정한다.

## 2. 고정 reference support와 birth source frame

물리는 non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`이며

\[
a_\perp=a e^{-b},\qquad a_\parallel=a e^{2b},\qquad
s=\dot b,\qquad \Sigma=\sqrt3|s|/H
\]

를 유지한다. 고정된 isotropic reference geometry의 ray cosine을 `nu`라고 하자.
원래 characteristic transport로 얻는 birth-frame cosine과 Jacobian은

\[
R_b(\nu)=\sqrt{e^{2b}(1-\nu^2)+e^{-4b}\nu^2},\qquad
\mu_b=\frac{e^{-2b}\nu}{R_b(\nu)},\qquad
\frac{d\mu_b}{d\nu}=R_b^{-3}
\]

다. Reference weight `q_i=w_i/2`에 Jacobian을 한 번 적용한 native prior는

\[
q_i^{\rm birth}=\frac{q_iR_b(\nu_i)^{-3}}
 {\sum_jq_jR_b(\nu_j)^{-3}}.
\]

Python observer는 저장된 reference nodes/weights를 독립 NumPy GL 규칙과 비교하고,
실제 저장 reference nodes에서 위 식을 계산하여 birth `mu`와 native prior를 확인한다.
따라서 다른 구현에서 얻은 근의 마지막 bit 차이가 큰 Jacobian을 통해 확대되는 문제와
실제 source-frame 불일치를 구별한다. 같은 `n,b0,birth index`의 prior/P2/P24 case는
**동일한 reference support와 동일한 실제 birth node bytes**를 사용해야 한다.

P2와 P24의 KL projectors는 같은 support에서 실행한다. 새 caller의 내부 정지 허용오차는
`1e-15`이고, 저장 binary64 `mu,alpha`의 수용 기준은 기존과 같은

\[
\left|\sum_i\alpha_iP_2(\mu_i)\right|\leq\frac3{10^{15}},\qquad
\left|\sum_i\alpha_iP_4(\mu_i)\right|\leq\frac3{10^{15}}
\]

다. P4 조건은 P24에만 적용한다. Observer는 `Fraction`으로 원래 unnormalized sum을
정확히 계산하며 normalization은 별도 gate로 검사한다.
역사적 S7 `n=32`의 내부 tolerance는 `3e-15`였다는 사실을 baseline에 그대로 남긴다.
따라서 refinement 비교에는 이 공개된 새 내부 수치 margin 차이가 있지만, 모든 새
order에서 prior/P2/P24의 물리적 acceptance 기준과 source/spectral inputs는 같다.

## 3. 기존 stock과 새 photon block의 실제 보존

기존 32-ray stock은 원래 32-ray transport와 state에 남긴다.
polar ray `0,31`에는 각각 `q=5 eV`, `.0025 photon/H`,
near-equatorial ray `15,16`에는 각각 `q=40 eV`, `.001 photon/H`를 둔
S7의 동일한 anisotropic control 입력을 사용한다.

Refined birth를 이 기존 mesh에 deposit하지 않는다. 각 새 cohort는 새 native transport에
태어나고, 관측 시각에는 각각 원래 owner의 `inventory`와 stress 식으로 계산한
`N/H`, `U/H`, `DeltaP/H`를 block 단위로 더한다. 동일한 관측 geometry와 per-H
normalization에서 collisionless radiation stress-energy는 이렇게 선형으로 합산된다.

기존 stock의 전체 `number`, `energy_ref`, `support_lo`, `support_hi`를 field-major
binary64 bit 배열로 비교한다. Sparse bit snapshot과 FNV-1a64 digest를 raw에 남기고,
Python은 전체 3,072-cell 배열을 복원하여 SHA-256을 계산한다.
입력 네 delta의 정확한 byte 배열, 실행 전/후 identity와 S7의 관측 `N/U/stress`까지 비교한다.

새 refined mesh에는 별도의 synthetic anisotropic control을 둔다.
이 control에 native birth를 순차적으로 주입하여 독립적으로 만든 빈-state birth의
cell별 합과 비교하고, birth가 닿지 않은 기존 cell의 네 bit 값이 같은지 확인한다.
P2/P24 adapter의 한 increment 합은 exact cell equality를 요구한다.
원래 prior는 source panels를 순서대로 더하므로 기존과 같은 `1e-11` ledger 기준으로
floating-point association 차이를 판정한다. 이 control은 기존 32-ray stock의 remesh가 아니다.

새 source의 실제 native photon/energy 증가량, native `SourceLedger`, combined block sum,
동일 mesh control의 증가분은 모두 별도 비교된다. Birth weights와 실제 photon/energy
angular fractions도 각각 저장한다. P2/P4가 맞는 angular weights만으로 finite-bin photon/energy
보존 판정을 대신하지 않는다.

Native stock은 per-H이므로 collisionless energy 식은

\[
U_H'+U_H+2b'\Delta P_H=0
\]

다. 물리 density로 바꿀 때 `nH0/a^3`을 곱하면 `U'+4U+2b'DeltaP=0`을 얻는다.

## 4. 사전등록할 18개 새 case와 판정

| 축 | 고정값 또는 새 값 |
|---|---|
| 초기 누적 `b0` | `.6`, `.9` |
| 새 angular order | `64`, `128`, `256` |
| 같은 support의 rule | prior, P2, P24 |
| Birth 수와 시각 | 16개, `u=.8*(j+.5)/16` |
| 이력 | `a=exp(x)/21`, `b=b0+.2x`, `H=1e-16/s` |
| 관측 시각 | `x=1` |
| Source panels | 각 segment 32개 |
| Native energy bins | 96개, `q=.01..5000 eV` |
| 독립 continuum angular reference | GL128/GL256 |

S7 baseline의 source-age/bins/panels를 고정하므로 새 캠페인에서 birth-time나 spectral
resolution을 동시에 바꾸지 않는다. 별도 physical-source-frame grid 방식도 이 matrix에 섞지 않는다.

관측량은 **새 photon만의**

\[
A_{\rm new}=\Delta P_{\rm new}/U_{\rm new}
\]

이며 기존 stock의 에너지가 angular 오차를 희석하지 않는다.
각 실제 birth의 native `U_birth`에 `exp(u−1)`을 곱하고 R/D kernel을 적분하여
같은 birth grid의 continuum angular reference를 구성한다.
GL128/GL256 차이는 `U_ref`로 나누어 `1e-12` 이하를 요구한다.

모든 새 order의 `|A_new−A_ref|<=1e-6` 여부를 기록한다.
캠페인의 finest-order accuracy gate는 **n256의 여섯 case**에 적용한다.
더 낮은 order에서 목표를 넘는 값은 `lower_resolution_target_failures`로 유지한다.
양의 해가 없는 case는 실제 birth index/time/support와 독립 feasibility witness를 남기고
다음 고정 case로 진행한다. 수치 solver failure도 feasibility와 분리하여 기록한다.

Exact birth moments, 양성·parity, source frame, 원래 source rate, photon source amount,
native R/D 대응, per-H continuity와 기존 stock/finite-bin ledger가 integrity 판정 대상이다.
새 angular 정확도의 success는 이번 고정된 collisionless source-age/bins/panels 범위에 관한 결과다.
전체 reactive history와 native Einstein feedback은 별도 미완료 의무로 남긴다.

## 5. 실제 개발 검증과 실행 경계

[RUST_DEV.json](evidence_s8_native/RUST_DEV.json): 새 Rust 테스트 **6개 PASS**.
원래 S7 실행의 SHA-bound owner rlib를 재사용하여 새 테스트만 컴파일했다.
Compile 1.5793 s, tests 0.00793 s였고 기존 21개 projector tests는 filter되어 실행하지 않았다.

- 원래 GL32 generator의 bit identity.
- GL64/128/256 양성·대칭과 native 마지막 ray indexing.
- Spectral 변경과 physically anisotropic declaration 거부.
- Campaign 밖의 synthetic `b0=.4` 한 birth에서 내부 margin과 기존 block 보존.
- Signed zero를 포함한 기존 state bit 차이 검출.
- 과거 n32 physical case와 잘못된 case 입력 거부.

[PYTHON_GUARDS.json](evidence_s8_native/PYTHON_GUARDS.json): 새 Python guard **10개 PASS**.
18개 matrix의 축 분리, S7 baseline hash reuse, 사전등록의 gate/source-key/margin 변경,
게시 receipt substitution, BLAS 32→1 강제 제한, 새 support, source-frame/Jacobian,
failure witness, 기존 stock의 input/before/after bytes, nonfinite/truncated output을 검사했다.
전체 Python guard 실행은 0.3249 s였다.

독립 검토자는 원래 owner의 공개 API, source clone/각도 배열 교체, old32 별도 transport,
per-H kernel, 새 photon만의 A와 exact old-input 검증을 확인했다.
검토 중 구체적인 판정 분류 하나를 교정했다. Feasibility witness가 검증된
`FINEST_ORDER_UNAVAILABLE`는 scientific target 미가용이며 integrity failure에 포함하지 않는다.
`PROJECTION_NUMERICAL_FAILURE`와 exact moment 초과는 계속 integrity failure다.
Matrix, 입력과 모든 tolerance는 동일하다.

[CLASSIFICATION_GUARD.json](evidence_s8_native/CLASSIFICATION_GUARD.json)에
이 변경을 검증한 새 targeted guard **1개 PASS**, 0.1242 s를 남겼다.
변경과 무관한 앞의 10개 guard 근거는 재사용하므로 총 11개 guard의 근거가 있다.
최종 사전등록은 [PREREGISTRATION.json](evidence_s8_native/PREREGISTRATION.json)이다.
분류 교정 전의 미게시 초안은 `PREREGISTRATION_PREPUBLICATION_CLASSIFICATION.json`에
보존했으며 현재 runner의 source hash와 일치하지 않아 실행 계약으로 채택되지 않는다.
현재 **scientific campaign: NOT_RUN; 코드·검증·사전등록 준비 완료**다.

## 6. 게시 후 native 실행 명령

정상 BASS Git checkout의 저장소 루트에서 다음 명령을 사용한다.
Runner가 committed prereg, 정확한 source hashes와 S7 재사용 증거를 먼저 확인한다.

```bash
python3 research/bass_isotropy_response_20261018/run_s8_native_refinement.py \
  --prereg research/bass_isotropy_response_20261018/evidence_s8_native/PREREGISTRATION.json \
  --out /tmp/bass_s8_native_refinement_run01 \
  --workers 4 \
  --timeout 1800
```

출력 경로가 존재하면 덮어쓰지 않는다. 정확한 원래 owner를 이미 가지고 있으면
`--owner-root /existing/path/rei_0e258464`를 추가할 수 있고, 기존 REI Git clone에서는
`--rei-repo /existing/path/rei_bianchi`로 고정 커밋의 blob만 읽을 수 있다.
두 옵션이 없으면 runner가 원래 manifest-pinned source를 출력 디렉터리 안으로 확보한다.
Compiler는 `PATH`의 `rustc` 또는 `--rustc /existing/path/rustc`를 사용한다.

현재 API-backed workspace에서 실행할 때는 root가 준비한 독립 Git readback receipt를
`--publication-receipt`로 제공한다. 그 receipt의 path는 정확히
`research/bass_isotropy_response_20261018/evidence_s8_native/PREREGISTRATION.json`이어야 한다.

Native thread 1, BLAS thread 1, staging worker 최대 4, RAM 16 GiB, disk 4 GiB,
job 최대 1,800 s를 유지한다. 최대 16개 n256 cohort의 네 cell 배열은 약 12 MiB다.
주요 반환 파일은 `NATIVE_ANGULAR_REFINEMENT.jsonl`, `ANALYSIS.json`,
`REUSED_S7_BASELINE.json`, `RETURN_NATIVE_ANGULAR_REFINEMENT.json`이며 compile/run 로그도 남긴다.
Native source extension의 실제 과학 결과는 이 게시 후 실행으로 채운다.
