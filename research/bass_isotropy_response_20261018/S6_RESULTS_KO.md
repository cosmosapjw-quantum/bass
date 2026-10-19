# S6 실행 결과

2026-10-19. 유도는 [S6_THEORY_KO.md](S6_THEORY_KO.md)에 있다. 물리 범위와 고정 조건은
S3와 같다. 기존 S2/S3/native 증거는 다시 실행하지 않았다. 새 실행은 아래 표의 것뿐이다.

## 0. 시작 대조

Dropbox `/BASS_BACKUPS`와 Drive 폴더 `1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y`의 최신 객체는
`BASS_PR174_CLOUD_RECOVERY_20261019_3694d6e1.zip`(164979 bytes, 양쪽 2026-10-19 08:24–08:25Z)이었다.
GitHub branch HEAD와 PR174 head는 `3694d6e14cad12c37c52413061381046798a7bfc`, 마지막 댓글은
`#issuecomment-6263061438`이었다. 그 뒤의 새 실행결과나 source 변경은 없어서 완료된 캠페인을
반복하지 않았다. 기록: [evidence_s6/INTAKE.json](evidence_s6/INTAKE.json).

## 1. 실행 목록과 판정

| 단계 | 명령(연구 경로) | 결과 | 시간 / peak RSS |
|---|---|---|---|
| S6a r1 | `python3 run_s6_finite_d.py --out evidence_s6/finite_d_r1 --workers 10` | **FAIL**: 사전 gate G5 | 11.0 s / 29.5 MB |
| S6a r2 | 같은 명령, `--out evidence_s6/finite_d_r2`, 산술 여유 추가 후 | **FAIL**: G5 (G1–G4 PASS) | 12.8 s / 28.5 MB |
| S6a held-out | `python3 run_s6_refinement_holdout.py --out evidence_s6/refinement_holdout` | PASS | 3.9 s / 39.6 MB |
| S6c native | `python3 run_spectral_refinement.py --out <scratch>/spectral_run01 --workers 4 --timeout 1800` | PASS(사전등록 gate 전부) | 18.6 s / 335 MB |
| S6d 시도0 | `python3 run_s6_source_age.py --out evidence_s6/source_age` | **구현 실패**: receipt의 numpy bool JSON 직렬화 | 20.3 s |
| S6d | 수정 후 같은 명령 | PASS | 17.6 s / 75 MB |
| 테스트 | `python3 -m unittest -v test_s6` | 18 PASS | 27 s |

Worker는 최대 10, native thread는 1이었다. RAM 16GiB, disk 4GiB, 개별 job 1800초
상한을 넘지 않았다. Native output은 11896560 bytes였고 owner source와 build는 연구 트리 밖에 두었다.

## 2. S6a: 유한 d 오차와 고차 moment

저장된 `ANGULAR_CAMPAIGN.json`(SHA256 `01f3d130…f03d`, 게시값과 일치)의 146 rule,
1460 certificate point를 다시 최적화하지 않고 평가했다.

| Gate | 기준(사전) | 실제 |
|---|---|---|
| G1 series=direct | ≤1e-24 | 1.09e-28 |
| G2 저장 A_error 재현 | ≤1e-14 | 2.22e-16 |
| G3 상한이 실제값 포함 | 전부 | 전부 |
| G4 L=100 tail | ≤1e-20 | 1.005e-22 |
| G5 refinement 비율 | n≥16, \|E\|≥1e-11에서 0.7–1.4 | **38/344 실패**, 범위 0.408–1.096 |

G5 실패는 모두 b=0.6, 0.8, 1.0이고 \(2n\ln\rho_*\le6.38\)인 pre-asymptotic 영역이었다.
더 빠른 수렴은 없었다(최대 1.096). 이 결과는 수정하지 않고 실패로 보존한다.
그 뒤 \(2n\ln\rho_*\ge10\) 기준을 데이터에서 정했으므로, 겹치지 않는 grid
(b=-0.5, 0.5, 0.7, 0.9; n=12…192; d=±0.05, ±0.15)에서 사전 gate로 다시 검사했다.
52 rule 측정, support 실패 8개(P2 mean 3, P24 mean 3, upper 2)를 따로 기록했다.
점근 30쌍의 비율은 0.781–1.005, 전체 100쌍 최대 1.075로 PASS였다.
Pre-asymptotic 최솟값은 0.432였다.

**제약 효과(고정 ray).** 잡음 위 238쌍에서 P2→P24가 오차를 줄인 경우 194,
늘린 경우 44였다. 변화는 (S6.1)로 ℓ=4 목표항과 ℓ≥6 부수항으로 정확히 나뉜다
(분해 잔차 최대 3.5e-18). 부수항은 목표항의 최대 47%였다. 악화 44쌍 중 33쌍은
P2 rule에서 ℓ=4 항이 ℓ≥6 항과 반대 부호로 상쇄하던 것을 P4 제약이 제거한 경우다.
예: b=-0.2, n=16, d=0.2에서 \(|E|\)가 9.77e-8에서 3.09e-7로 커졌다.

**제약만의 보장.** (S6.4) 표처럼 d=0.2에서 P2/P4만 0인 rule의 최악 오차는 7.47e-2이고
1e-6을 보장하려면 P2…P24가 필요하다. 저장 rule의 실제 오차가 작은 것은 refinement가
고차 \(M_\ell\)을 줄였기 때문이다.

## 3. S6b: exact rank1 certificate

`rank1_certificate.project_rank1(mu, prior, cert)`가 실행 경로다. 기존
`angular_p24.project`는 바꾸지 않았고 여전히 `FEASIBILITY_UNRESOLVED_RANK1`를 반환한다.
테스트 결과:

- GL4, `z_quadratic=[3,-30,35]`: GL weight와 최대 차이 1.67e-16, moment 잔차 ≤3.6e-17.
- `z=(0,3/5)`, `[0,-3,5]`: (5/18, 4/9, 5/18).
- 정확한 거절: 비호환 `z=(1/6,1/2)` → `INFEASIBLE_P24_RANK1_EXACT`, mean 위반,
  중근, 단위구간 밖, 차수, 비정수/bool, schema, 1e-9 섭동 ray → `RANK1_BINDING_NO_ROOT`,
  rank≠2 → `RANK1_CERT_SUPPORT_RANK`.

Native grid는 서로 다른 z가 4개 이상이라 rank1이 생기지 않는다. Rust/native 경로는 만들지 않았다.

## 4. S6c: spectral 잔차와 panel/bin refinement

Python replica(`spectral_residual.py`)는 저장된 native run01의 값
5.369704680902032e-12를 bit 단위로 재현했다. 그 뒤 native 실행 전에
[PREREGISTRATION.json](evidence_s6/spectral/PREREGISTRATION.json)에 cps별 예측과 gate를 기록했다.
고정 owner 57개 파일을 무변경 컴파일하고, n_mu=8, b=0.3, P2P4에서 cps∈{4,8,16,32,64},
n_energy∈{24,48,96,192} 20행과 cps=64에서 angular만 바꾼 6행을 측정했다.

| cps | 예측 probe 잔차 | Simpson32 기준 오차 | GL8 오차 |
|---:|---:|---:|---:|
| 4 | 1.40168e-9 | -1.40168e-9 | -6.2e-17 |
| 8 | 8.62470e-11 | -8.62471e-11 | -9.2e-17 |
| 16 | 5.36970e-12 | -5.36972e-12 | 2.1e-17 |
| 32 | 3.35287e-13 | -3.35371e-13 | -1.4e-17 |
| 64 | 2.10942e-14 | -2.09752e-14 | 5.0e-17 |

- Native와 예측의 최대 차이 2.22e-16(gate 1e-15).
- 두 배 refinement 비율 16.25, 16.06, 16.02, 16.06(gate 15–17).
- 같은 cps에서 bin 수에 따른 spread ≤2.22e-16, cps=64에서 angular spread 0.
- Photon 상대차 최대 4.44e-16, ledger gate 1e-11 통과, 미분 식 차이 최대 1.30e-10.

따라서 5.369926725506957e-12는 Simpson 기준값의 절단 오차와 그 1 ulp 변동이다.
Native source deposition의 energy는 40자리 기준과 1e-16 이내다. 이 결과는 source
deposition 범위이며 transport, absorption, history의 spectral 수렴을 인증하지 않는다.

## 5. S6d: source-age 합성

처방된 기하 \(b=0.15\sin2x+0.1x\), source \(j=\exp[-((u-0.4)/0.2)^2]\)(u∈[0,0.8])에서
cohort K∈{16,…,128}, n∈{8,16,32}, prior/P2/P24를 합성했다. 거절 0.

- Complex-step 보존식 \(dU/dx+4U+2b'\Delta P\)의 최대 상대 잔차 2.99e-15(gate 1e-12).
- 출생시간 midpoint 오차의 두 배 비율 3.90–4.03(gate 3.5–4.5), x=1에서 ΔP 오차
  5.0e-7(K=16)→8.1e-9(K=128).
- x=1, K=128의 angular 성분 \(\delta\mathcal A\): n=8에서 prior −1.05e-3, P2 −3.09e-4,
  P24 −1.18e-4; n=16에서 −2.3e-7, −1.0e-7, −5.5e-8; n=32에서 1e-15 수준.
- P2 rule에서 S3 선도식 \(\tfrac{36}{35}\sum wM_4d\)는 부호와 크기 순서는 맞지만 실제
  angular ΔP를 1.33–2.08배 과소평가했다(n=8, 16). 유한 d 합성에는 정확한 kernel을 쓴다.
- 음성 대조: 관측 시점 rule로 survivor를 재가중하면 보존식 잔차가 1e-6 이상으로 커진다.

Einstein 결합 실행은 하지 않았다. (S6.7)은 owner의 섭동 진단과 계수가 일치함을 확인했고
실행 계약은 [COUPLED_FEEDBACK_CONTRACT.json](evidence_s6/COUPLED_FEEDBACK_CONTRACT.json)에 있다.

## 6. 실패 분류

| 분류 | 사례 | 처리 |
|---|---|---|
| 사전 수치 gate 실패 | S6a G5(38/344) | 보존. 별도 held-out으로 점근 주장만 검사 |
| feasibility | held-out support 실패 8 | 구체적 실패로 기록. 우회 없음 |
| 구현 | S6d 시도0 JSON bool | 수정 후 재실행. 실패 출력 보존 |
| 테스트 설계 | k₂ 기대값, L=80 절단, 30자리 잡음 | 테스트와 상한(산술 여유) 수정 |
| 환경 | 없음 | — |

## 7. 남은 의무

Einstein/shear 결합 실행, native source-age 합성, transport/absorption을 포함한 spectral 수렴,
|b|≳0.6에서 native angular 해상도 부족의 실제 영향 측정이 남았다.
REI production/full EoR/merge는 승인하지 않았다.
