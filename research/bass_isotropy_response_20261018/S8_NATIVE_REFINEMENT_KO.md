# S8: 원본 spectral owner를 유지하는 native angular refinement

## 상태와 출발점

**S8 사전등록·게시·이중 백업 확인 후 새 native 18개 case를 한 번 실행했다. 17개 측정 완료,
1개 수치 solver 실패를 보존했으며 n256의 여섯 angular 정확도 목표는 모두 통과했다.**
전체 상태는 `COMPLETED_WITH_RETAINED_FAILURES`다. 실패한 지지는 해당 birth에서
`STRICT_INTERIOR`로 판정되어, 양의 해가 없는 지지와 구별된다. 원래 owner, projectors,
입력과 허용오차는 변경하지 않았고 S7 native case를 다시 실행하지 않았다.
실제 결과와 실패의 범위는 아래 7절에 기록한다.

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

## 4. 사전등록한 18개 새 case와 판정

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
이 개발 검증을 닫고 소스를 동결할 때의 상태는 **scientific campaign: NOT_RUN**이었다.
아래의 실제 과학 실행은 Git 게시와 두 클라우드 readback을 마친 뒤 별도로 수행했다.

## 6. 완료된 native 실행의 선택적 재현 명령

이미 완료된 18개 case를 별도 환경에서 재현할 필요가 있을 때만 다음 명령을 사용한다.
이 명령은 아직 준비되지 않은 solver 수리나 새 물리 캠페인을 실행하는 명령이 아니다.
정상 BASS Git checkout의 저장소 루트에서 runner가 committed prereg, 정확한 source hashes와
S7 재사용 증거를 먼저 확인한다. 사전등록 게시 커밋은
`4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613`이다.

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
Git에 보존하는 실제 run01 raw는 lossless `.jsonl.gz`이며 원본 크기와 SHA-256은
`RAW_STORAGE.json`에 기록한다. 새 재현 실행은 별도 출력 폴더에 uncompressed raw를 생성한다.


## 7. 실제 S8 결과: 18회 시도, 17개 측정과 한 수치 실패

### 게시·출처와 실행 횟수

실행 전에 코드와 사전등록을
[`4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613`](https://github.com/cosmosapjw-quantum/bass/commit/4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613)에
게시했다. 실제 Git raw readback receipt는
[delivery/s8/NATIVE_PUBLICATION.json](delivery/s8/NATIVE_PUBLICATION.json)이다.
Root는 실행 전에 공통 S8 archive 123,122 B의 SHA-256
`ae0ccedaaccc25044f77fa28129b9b1cfc9dd699674aa4dc204c6454dabcae71`에 대해
Drive 파일 `1VS_Z1G2VeWgtWLrmmS6yV1CPeZNXdrpw`의 raw byte equality·CRC·35개 manifest entry를
확인했고, Dropbox `id:BSpOijBcT10AAAAAAD_Q0A`의 전체 object provider hash가 일치함을 확인했다.
두 readback의 범위를 같은 종류의 raw 검증으로 합쳐 서술하지 않는다.
이들은 실행 전 사전등록 package의 증거이며, 결과 package의 게시·백업은 root의 별도 마감 기록에 남긴다.

실제 실행은 2026-10-19 12:05:51 UTC에 시작한 **한 번**의 runner 호출이다.
새 18개 matrix를 모두 시도했고, 이전 S7 여섯 baseline의 결과와 실패 witness는 읽어서 재사용했다.
원래 owner 57개 파일, 614,313 B가 manifest의 Git blob SHA와 SHA-256에 모두 일치했다.
원래 owner의 새 compiled rlib SHA도 S7에서 보존한 rlib SHA와 일치했다.

- [ANALYSIS.json](evidence_s8_native/run01/ANALYSIS.json): 18행, 17개 측정,
  `integrity_gates_pass=false`, `finest_accuracy_targets_pass=true`.
- [RETURN_NATIVE_ANGULAR_REFINEMENT.json](evidence_s8_native/run01/RETURN_NATIVE_ANGULAR_REFINEMENT.json):
  실제 명령·compiler·owner/source hashes·자원·실패 상태.
- [REUSED_S7_BASELINE.json](evidence_s8_native/run01/REUSED_S7_BASELINE.json):
  이전 n32 여섯 case의 네 측정값과 두 feasibility 실패, 원본 다섯 hash.
- [NATIVE_ANGULAR_REFINEMENT.jsonl.gz](evidence_s8_native/run01/NATIVE_ANGULAR_REFINEMENT.jsonl.gz):
  측정 17개 history의 birth arrays와 한 실패 witness를 포함한 lossless raw.

### Angular refinement와 같은 지지의 moment constraints

아래 값은 모두 **새 photon만의** `A_new−A_continuum`이다.
새 order의 source-age 16개, source panels 32개와 energy bins 96개는 고정했다.
`n32 재사용`의 내부 solver tolerance는 과거의 `3e-15`, 새 n64/128/256 caller는 `1e-15`다.
같은 새 order의 prior/P2/P24는 동일한 실제 birth nodes를 사용한다.

| `b0` | `n_mu` | prior | P2 | P24 |
|---:|---:|---:|---:|---:|
| .6 | 32 재사용 | −1.42854503e−2 | −3.31932360e−3 | −9.94529757e−4 |
| .6 | 64 | −5.54277108e−5 | −2.39845873e−5 | −1.07574584e−5 |
| .6 | 128 | −4.00270511e−10 | −2.94852837e−10 | −2.11994686e−10 |
| .6 | 256 | −4.82947016e−15 | −6.80011603e−16 | −5.41233725e−16 |
| .9 | 32 재사용 | −1.92174229e−1 | feasibility 실패 | feasibility 실패 |
| .9 | 64 | −3.77152347e−2 | −7.38944896e−3 | 수치 solver 실패 |
| .9 | 128 | −5.08184116e−4 | −1.80448252e−4 | −6.91949951e−5 |
| .9 | 256 | −3.81421485e−8 | −2.42497906e−8 | −1.52591818e−8 |

사전등록한 n256 여섯 case는 모두 `|A_new−A_continuum|<=1e-6`을 충족했다.
측정된 더 낮은 order의 여덟 case는 같은 정확도 목표를 넘어서 그 목록을 그대로 보존했다.
`b0=.9,n128`에서는 P24가 같은 지지의 prior와 P2보다 오차를 줄이지만,
P2/P4를 함께 맞추어도 오차 `6.9195e-5`가 남는다. 따라서 **moment 일치와 finite-d
continuum angular 정확도는 이번 실제 native 결과에서도 서로 다른 판정**이다.
새 support를 n256으로 확장한 효과는 같은 n의 제약 변경 효과와 표에서 분리되어 있다.

GL128/GL256 continuum angular reference 차이의 최대 상대값은 `5.70155571e-15`로
고정 reference gate `1e-12`를 통과했다. 실제 native finite-bin inventory와 같은 birth
weights의 discrete R/D kernel 사이 최대 상대차는 `3.66854800e-16`이었다.
이 비교는 이번 고정된 collisionless geometry와 source-age grid에 대한 결과다.
새로운 birth-time refinement, spectral continuum limit나 full reactive history의 승인을 뜻하지 않는다.

### 양성·moments·old stock·native finite-bin 보존

측정된 17개 history의 272개 birth가 검증되었다. 그중 제약을 적용한 11개 history,
**176개 birth**는 저장 binary64 `mu,alpha`에서 정확한 유리수로 계산한 고정
`3/10^15` moment gate를 모두 통과했다. P2-only의 최대 exact `|M2|`는
`1.02137530e-15`; 측정된 P24의 최대 exact `|M2|`, `|M4|`는 각각
`1.71546970e-16`, `1.06468440e-15`였다. 양의 weights, reflection parity,
normalization과 source-frame binding도 측정된 모든 history에서 통과했다.
실패한 history의 완료되지 않은 birth나 최종 native inventory에는 이 결론을 확장하지 않는다.

| 실제 검산 항목 | 최대 관측값 | 고정 gate 또는 결과 |
|---|---:|---|
| Native photon increment ledger 상대차 | 9.32531819e−16 | 1e−11 PASS |
| Native energy increment ledger 상대차 | 1.14197951e−15 | 1e−11 PASS |
| 원래 SourceLedger와 inventory 상대차 | 1.26565425e−14 | 1e−11 PASS |
| Native inventory와 discrete R/D kernel 상대차 | 3.66854800e−16 | 3e−14 PASS |
| 독립 native block 합의 상대차 | 1.92586937e−16 | 1e−11 PASS |
| Per-H energy continuity 상대잔차, 두 h의 최댓값 | 5.34180741e−13 | 1e−11 PASS |
| 기존 n32 관측값과 S7 값의 상대차 | 0 | 동일 |
| Spectral cell 및 source-rate bit 비교 | 차이 0 | 측정 17개 PASS |

기존 anisotropic n32 stock은 별도 original transport에서 유지되었다.
17개 측정 history의 전체 old-state input/before/after byte SHA-256은 모두
`79a81384cf24516c9fa93802145a5e864a95da3d2ee6e02187374badc9d155de`다.
Survivor state를 초기화하거나 refined angular mesh로 옮기지 않았다.
측정값은 각 native block을 같은 관측 geometry에서 계산한 뒤 더한 것이며,
새 refined source를 기존 old mesh로 deposit한 것으로 해석하지 않는다.
같은 refined mesh의 별도 incremental control도 기존 cell 보존과 native photon/energy
증가량 검사를 통과했다. 이 실제 ledger 근거는 moment 일치와 독립적으로 확인했다.

### 보존한 수치 실패와 정확한 미완료 범위

유일한 solver 실패는 `b9_n64_P2P4`의 0-based birth index 11,
`u=0.5750000000000001`, `b=1.0150000000000001`에서 발생한
`INNER_P2_PRECISION_LIMIT`이다. 저장된 지지의 독립 geometry 판정은 다음과 같다.

| Geometry 증거 | 값 |
|---|---:|
| 서로 다른 `z=mu²` 개수 | 32 |
| `z_min` | 1.344039330644834e−6 |
| `z_max` | .6195099475928701 |
| lower moment hull | .13915063382600582 |
| upper moment hull | .20650293123166497 |
| `1/5 − lower` | .060849366173994196 |
| `upper − 1/5` | .006502931231664955 |

따라서 이 실패 witness는 **STRICT_INTERIOR**이며 구체적 feasibility 실패가 아니다.
원래 `balance_p24.rs`의 `solve_p2`는 outer caller tolerance를 8로 나눈
`inner_tol=1.25e-16`을 요구한다. 해당 error는 `lo+(hi−lo)/2`가 `lo` 또는 `hi`로
반올림되어 더 이상 표현 가능한 중간 `lambda2`가 없을 때 반환된다.
즉 내부 P2 기준을 만족하기 전에 이분법이 binary64 배수의 machine-resolution 한계에 도달한 것이다.
원래 raw는 마지막 bracket의 수치값을 기록하지 않으므로 특정 endpoint 잔차나 최종
해의 moment 값을 추정해서 채우지 않는다.

정확한 최종 수용 기준 `3/10^15`도, 새 caller의 `1e-15`도 변경하지 않았다.
원래 projectors와 spectral owner를 수정하지 않았고 음의 weights로 우회하지 않았다.
이번 선택 범위에서 같은 기준을 만족하는 작은 안정화 수리가 증명되지는 않았다.
이에 따라 새 solver나 동일 case 재실행을 추가하지 않고 **18회 원래 시도와 한 수치 실패**를 보존했다.
해당 history는 최종 native photon/energy inventory가 없고, 그 이후 birth의 결과도 미측정이다.

남는 bounded 의무는 원래 projectors를 보존한 opt-in 수치 안정화의 별도 설계·개발 검증과
사전등록이다. 필요시 실패 case만 다루고 기존 17개 결과는 SHA-bound reuse해야 한다.
이 후속 solver 수리 및 one-case resume 코드는 현재 준비·실행된 것으로 표시하지 않는다.
이와 별개로 native Einstein coupling, 전체 reactive source history, 새로운 birth-time/spectral
refinement와 production admission에는 독립 검증이 남는다.

### 실제 자원과 원본 증거 보존

| 실행 항목 | 실제 값 |
|---|---:|
| 전체 runner elapsed | 21.88629078 s |
| Original owner compile | 10.49045561 s |
| 새 Rust probe compile | 1.73804291 s |
| 새 18개 native case 실행 | 5.58904673 s |
| Child peak RSS | 337,388 KiB |
| Python peak RSS | 56,064 KiB |
| 실행 중 output disk 사용량, build 포함 | 15,317,948 B |
| Staging workers / native threads / BLAS threads | 4 / 1 / 1 |

Rust는 `1.94.1`, NumPy는 `2.3.5`였다. RAM 16 GiB, disk 4 GiB, 개별 job 1,800 s와
추가 worker 상한을 충족했다. Rust compiler와 native 실행은 모두 exit 0이며,
Python runner는 기록된 과학적 실패 때문에 최종 exit 2를 반환했다.

원래 JSONL은 5,090,460 B다. Gzip 959,031 B로 저장한 뒤 decode하여 **모든 raw byte가
동일함**을 확인했다. Compiled binaries/rlib와 uncompressed 사본은 scratch에 보존하고
Git와 cloud archive 대상에서는 제외했다. 실행 receipt 자체는 변경하지 않았다.
[RAW_STORAGE.json](evidence_s8_native/run01/RAW_STORAGE.json)에 포장 방식과 양쪽 digest를 기록한다.

| 증거 | SHA-256 |
|---|---|
| 사전등록 | `df1752714e285ffff797e531fc4c5104e9b129266458f746ff0741a3aeff225c` |
| 원래 raw JSONL | `e72fe3952929f63333872627e0d76e30c489c9e7f8f141d4fd79ca28f3a26e09` |
| Lossless gzip | `fdc70eaaea45804aa16e60bba495b283eb5e4a18a576f52d5519bfd5a1f05839` |
| Analysis | `cf3fa36149abc99f816344003caeab01a4ad89b919307e76d28532f373f894f5` |
| 실제 execution receipt | `b61e44a9f6f0a2a6d048fec79163a9341cd1bc3f531a22c4562de9ddb80549c1` |

`REI_production`, `full_EoR`, `native_Einstein_feedback`, `full_reactive_history`,
`continuum_spectral_accuracy`는 모두 **false**로 남긴다.
