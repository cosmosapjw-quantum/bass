# R113-CLOUD: Lie 대수로 생성한 1+3 PSTF 엔진과 비섭동 배경 C_lm^XY

기준 커밋: BASS `4062672` (R112), REC `3752213` (R112), REI `503508f` (R112 pin),
htt_base 기록 `e810a4f7`. 이론 루프는 `THEORY.md` (Phase 1-10), 수치 결과는
`RESULTS/*.json`, 검증은 `_rustcore` 테스트이다. 이 문서의 수치는 모두 해당
파일 또는 테스트 출력에서 옮겼다. 사실, 해석, 미해결 항목을 절로 나누었다.

## 0. 요약 (사실)

- 하나의 코드 경로가 모든 Bianchi family를 다룬다. Hubble-normalized Lie data
  (Sigma, N, A, Omega)에서 photon generator의 type 상수 (R~, U, Z, omega; L <= 2
  Y_LM 계수, Dossier II `ii:hodge_potentials`)를 만들고, 그 상수가 spin-harmonic
  hierarchy (s = 0, +-2)의 Gaunt 커널 (Wigner 3j)에 곱해진다. type별 파일은 없다.
  12 family + FLRW + 예외형 VI*_{-1/9}, 임의 SO(3) 회전 (off-axis) 데이터가 같은
  식으로 들어간다.
- 복사장 표현이 두 가지다. `rays` (R109-R112 기본값, TSV 출력 byte-identical)와
  `harmonic` (새 Lie spin-harmonic PSTF 경로). 둘 다 같은 Thomson/recoil 충돌, Einstein
  feedback (Gauss/Codazzi), congruence Lie update, SDIRK2, line-of-sight replay를
  쓰므로 임의 l까지 모든 m의 T/E/B a_lm과 C_l^XY (TT, TE, TB, EE, EB, BB)를 낸다.
- 무충돌 질량 0 중성미자 (`--neutrino-fraction`), radiation energy frame과 local
  boost / global tilt 보고, `--observer-frame normal|host|spectator|radiation|radiation-total`.
- REC `matched_history`: implicit matched-differential hydrogen step (D9).
  BASS에서 `--recombination matched`로 켜면 수송된 하늘이 x_e를 되먹인다.
- 검증: BASS `cargo test --release --locked` 218 passed / 0 failed, REC 129 passed
  (새 2개 포함), R112 레거시 CLI 20개 출력 byte-identical (V1). REI는 바꾸지 않았다
  (pin `503508f`에서 `cargo test --release --locked --lib --tests` 271 passed).

## 1. 출발점 (R112까지의 개발 상태)

- BASS `_rustcore/homogeneous_sky`: ray 기반 Lagrangian 하늘, recoil Thomson 셀
  (BE/SDIRK2), 두 dust stream (Codazzi coflow, 질량 비 f_b), Lambda, congruence Lie
  update, 충돌 기록과 backward-characteristic replay (R110), REC material-frame
  bridge (R112). type 정보는 `kinetic/lie_history`의 canonical 대각 표와 각 ray의
  characteristic 적분 안에 흩어져 있었다.
- REC: 방향성 하늘의 pointwise HYREC-2 TLA source (R110), 두 온도와 proper-time
  matched RHS (R112). 적분된 history는 없었다 (R110 T1 HOLD).
- REI: R110 `bass_ionization`이 REC(z > 20) + AX08(4..20) + continuation(z < 4)을
  BASS `--ionization` 표로 쓴다. R113 목표에 필요한 REI 코드 변경은 없었다.
- 빈 곳: Lie 대수에서 바로 생성되는 보편 커널, PSTF/spin-harmonic 계층, 중성미자,
  frame 보고, 하늘에 반응하는 recombination.

## 2. 이론 루프 (THEORY.md 요약)

- D1 type 상수: C^k_ij = eps_ijl N^lk + A_i delta^k_j - A_j delta^k_i, Jacobi N A = 0.
  불변량은 N의 rank/inertia, A = 0 여부, h = A^2/(n2 n3); congruence update가 type과
  h를 보존한다.
- D2 generator 잠재량: R~ = -Sigma:ee, U = -1/2 Sigma:ee - A.e,
  Z = -1/2 N_TF:ee - Omega.e, omega = Omega.e + N_TF:ee - tr N/6.
  V = grad U + J grad Z. 모두 L <= 2.
- D3 정확한 spin-harmonic 계층 (bolometric carrier k = 4):
  da^h_lm/deta = sum [k R~_LM G^h - U_LM K_grad^h - Z_LM K_J^h + i h omega_LM G^h] a^h_l'm' - k a.
  등방 부분 -k a는 지수로 정확히 처리한다. Galerkin 절단.
- D4 표현 무관 양 (moments, C_l), D5 harmonic 경로 충돌: 격자 합성 -> R109/R110
  BE/SDIRK2 + recoil -> 분석. 정지 전자에서는 PSTF BE 닫힌 꼴과 같다.
- D6 시간 분할과 기록 (replay가 두 경로 모두에 적용), D7 중성미자와 Bianchi I
  1차 법칙 Sigma' = -Sigma - (8/5) Omega_coll Psi, Psi' = Sigma.
- D8 energy frame beta(1 - f.beta) = f - P beta; local boost = 관측자 대 radiation
  energy frame, global tilt = 물질 stream 대 normal/radiation frame.
- D9 matched implicit recombination (REC):
  x_{n+1} - x_n = dx_ref + d eta [r_ani(x_{n+1})/(gamma H) - r_ref/H_ref].
- Phase 10 closeout에 구현과 계약의 차이 3개를 기록했다 (root finder, BASS coupling
  범위, BASS FLRW gate가 배경 절단 오차 차수라는 점).

## 3. 구현 (코딩 루프)

| 위치 | 내용 |
|---|---|
| `src/geom/lie.rs` | `LieData`, canonical algebra (모든 family, scale, 회전), 불변량/분류, Y_LM 계수, `photon_potentials` |
| `src/kinetic/wigner.rs` | log-factorial Racah 3j, Gaunt triple (G, K_grad, K_J) |
| `src/kinetic/spin_sht.rs` | s = 0, +-2 Gauss-Legendre ring SHT, Stokes 변환 (HEALPix 부호) |
| `src/kinetic/lie_hierarchy.rs` | 커널 표, RHS, RK4 substep + 정확한 등방 감쇠 |
| `src/homogeneous_sky/field.rs` | `Route::{Rays, Harmonic}`, `HarmonicSky`, `Field` (photons/neutrinos 공통) |
| `src/homogeneous_sky/frames.rs` | energy frame, 상대 속도 |
| `src/homogeneous_sky/solve.rs` | `solve_general(.., &SolveOptions {route, neutrino_fraction, recombination})`; 레거시 진입점은 기본값으로 위임 |
| `src/homogeneous_sky/{ionization,material}.rs` | `xe_at`, `cells_with_offset`, `rate_at` |
| `examples/homogeneous_sky.rs` | `--route`, `--harmonic-lmax/-ntheta/-nphi`, `--neutrino-fraction`, `--observer-frame`, `--recombination matched --t-unit-k T [--recombination-stop-eta E]`; `lie_constants.tsv`, `species.tsv`, `recombination.tsv`, run.txt frame 키 |
| REC `src/matched_history.rs` | `anisotropic_peebles_rate`, `isotropic_peebles_rate`, `MatchedStep`, `implicit_matched_step` (Illinois regula falsi, [0, 1-1e-12]) |

BASS는 REC를 `05db5451a97c66b9a87de98ae35b88ab820d368f`로 다시 pin했다
(`Cargo.toml`, `Cargo.lock`, `src/microphysics/tests.rs`의 고정 테스트). REI pin은
`503508f` 그대로다.

## 4. 검증 V1-V13

| ID | 시험 | 합격선 | 측정 |
|---|---|---|---|
| V1 | R112 CLI 6건 (VII_h recoil, VIII Lie IC, LoS+SDIRK2+congruence+Lambda, tracer V, IX active, HYREC) 20개 TSV | byte-identical | 20/20 (REC 재pin과 coupling 이후 재확인) |
| V2 | 회전된 canonical 데이터의 분류와 h, 잠재량의 pointwise 값 | type 일치, <= 2e-15 | 회전된 14 경우 (I-IX, VI*, VI_h/VII_h는 h 두 값) 분류 일치, Jacobi < 1e-15, h 1e-12; VI*: h = -1/9 (1e-15); Liouville 계수와 1e-15 |
| V3 | 계층 행렬 대 `advance_ray` 유한차분 generator (IX, VIII, VII_h:0.6, VI*, 회전된 V) | <= 1e-6 | 1.13e-7, 1.18e-7, 1.16e-7, 1.44e-7, 1.21e-7 (FD 간격 절반에 1.13e-7 -> 2.81e-8, 즉 FD 오차) |
| V4 | 닫힌 극한: 강체 회전, N = n_c I 위상, type V +-A/3 혼합 | <= 1e-13 | 통과 |
| V5 | spin SHT 왕복, `sky_spectrum` E/B와 일치 | 2e-13 / 1e-13 | 통과 |
| V6 | 정지 전자 harmonic 충돌 대 PSTF BE 닫힌 꼴 | < 2e-13 | 3.28e-14 |
| V7 | harmonic 대 rays (13 경우) | L, 격자에 따라 감소 | 5.1절: 차이는 L 무관, 시간 간격 절반마다 1/4 |
| V8 | harmonic replay 대 직접 출력 (l <= 4) | 감소 | 5.1절: 직접 대 replay 차이는 rays 대 harmonic 차이와 같은 크기 |
| V9 | Bianchi I 무충돌 stress 대 D7 ODE (Sigma_0 = 1e-3) | < 1e-2 | rays 5.87e-5, harmonic(10) 5.87e-5 |
| V10 | boost된 등방 하늘의 energy frame | 1e-12 | 통과 |
| V11 | 중성미자 분할이 기하를 바꾸지 않음; FLRW+중성미자 H = e^{-2 eta} (eta = 0.5에서 e^-1), 등방 유지 | 1e-11 / 1e-12 | 분할 차이 1.13e-14 (rays), 1.76e-14 (harmonic) |
| V12 | REC: FLRW 항등식, d eta = 1e-4 ... 50 | 1e-14 | 통과. BASS (적분된 배경): 최종 offset -1.09e-9, -2.74e-10, -6.88e-11 (24/48/96 step), 비 3.97, 3.99 (2차) |
| V13 | REC: 비등방 하늘, [0,1] 안, 1차 수렴, stiff 극한 | 비 1.7-2.3 | 통과. BASS Bianchi I (Sigma 0.01, beta 1e-3): rays 1.62418e-7, harmonic(8) 1.62418e-7 (상대 6e-9), 24 step 1.60188e-7 |

추가: `stop_eta` 이후 offset 고정과 그 이전 동일성 테스트, x_e > 1 (헬륨 전자) 표에서
기준 수소가 완전 이온화된 동안 응답 0 테스트, V7-lite (기울어진
class B VII_h, l <= 3: L = 8과 16에서 5.58e-6, shear 차이 2.7e-9).

## 5. 수치 결과

### 5.1 cross-route atlas (`RESULTS/CROSS_ROUTE_ATLAS.json`)

설정: duration 0.3, recoil, tau 0.2, dust 0.3, f_b 0.157, f_nu 0.3, SDIRK2,
congruence, shear 0.05, 기울어진 dust, 관측자 boost, LoS l <= 32 (과표본 격자).

- 24 step에서 harmonic(L = 8..24) 대 rays(24x52), l <= 4: FLRW 1e-12, I 4.8e-9,
  VII_0 4.7e-9, IX 6.3e-9, II 2.1e-7, VIII 2.6e-7, VI_0 2.5e-6, III 3.5e-6,
  IV 3.5e-6, V 4.2e-6, VII_h 5.8e-6, VI_h 6.7e-6, VI* 7.9e-5. L에 무관하다.
- 시간 refinement 24 -> 192 step: 경로 차이 V 4.18e-6 -> 6.53e-8, VII_h 5.77e-6 ->
  9.01e-8, VI* 7.89e-5 -> 1.23e-6, VIII 2.63e-7 -> 4.11e-9; 매 절반마다 비 4.0.
  두 이산화가 같은 연속해로 2차 수렴한다.
- LoS l <= 32 harmonic(24) 대 rays: VI* 1.9e-7, 나머지 <= 5.1e-8. type과 h는
  보존된다 (VII_h 0.25 -> 0.2499999999999998, VI*_{-1/9} 유지).

### 5.2 절단 연구 (`RESULTS/TRUNCATION_STUDY.json`)

duration 1.2, 96 step, tau 0.4, 큰 shear, LoS l <= 32 (64x128).

- VII_h(shear 0.18), IX(0.25): L = 16에서 자기 변화 9e-11, 9e-13; rays와 LoS 차이
  5.0e-7, 3.6e-8 (L >= 8부터 일정).
- VI*(shear 0.2, focusing): L = 8은 양성 guard로 fail closed ("invalid radiation
  integral or negative transverse eigenvalue"); L = 12, 16, 24, 32, 48의 l <= 4 rays
  차이 9.0e-3, 1.6e-3, 7.1e-5, 6.8e-5, 6.8e-5, 자기 변화 L = 32에서 9.4e-6, 48에서
  4.4e-8. focusing family는 L ~ 24-32가 필요하다. 시간: L = 48에서 11 s.

### 5.3 z = 1100 -> 0 장기 시연 (`RESULTS/LONG_EPOCH_DEMO.json`)

VII_h (h = 1/4, |N|, |A| ~ 1e-2, shear 1e-4), HYREC x_e 표, f_b 0.157, 기울기
1e-4, 중성미자 (N_eff 3.046 비율), Lambda, SDIRK2, congruence, baryon 동행 관측자,
768 step, LoS l <= 64 (96x192).

- 시간: rays 21.8 s, harmonic16 23.6 s, harmonic16 1536 step 44.4 s.
- 경로 차이 (LoS l = 2..64) 9.05e-9, l = 1 2.3e-9; 시간 간격 절반 변화 4.4e-5.
- tau = 1.12424, H_final/H_emit = 4.2649e-5, max|Gauss| 6.0e-4 (768) -> 1.5e-4 (1536),
  Codazzi <= 4e-12. type VII_h, h 0.25 -> 0.25000000000000283.
- frame: radiation energy frame beta_x = 1.906e-5, host stream 4.1e-8, host 관측자의
  radiation frame 대비 local boost -1.90e-5.
- C_2^TT = 8.26e-10, C_10 = 2.6e-19; l >~ 30은 a_lm 반올림 바닥 (~1e-32).

### 5.4 matched recombination 시연 (`RESULTS/RECOMBINATION_DEMO.json`)

같은 종(species) 설정에서 `--recombination table` 대 `matched` (rays, harmonic16).

| 경우 | delta x_e 최대 (eta <= 1) | 최종 | 경로 차이 | tau 변화 | C_l 상대 변화 (l = 2) TT / EE | 시간 table / matched |
|---|---|---|---|---|---|---|
| long_small (5.3과 같음) | 2.56e-8 at eta 0.128 (x_e 0.032, 7.9e-7) | 2.82e-8 at z = 0 (x_e 1.76e-4, 1.6e-4) | 7.4e-16 | +8.0e-7 | -6.9e-7 / +5.5e-6 | 24 s / 125 s (harmonic16 155 s) |
| window_strong (shear 1e-2, beta 1e-3, eta <= 0.5) | 3.17e-7 at eta 0.027 (x_e 0.108, 2.9e-6) | 3.10e-8 | 2.0e-15 | +6.1e-6 | -3.8e-6 / +2.1e-5 | 1.5 s / 13 s (harmonic16 17 s) |

C_l 변화는 C_l >= 1e-20 (a_lm 바닥보다 1e12 위)인 l에서만 셌다 (long_small l <= 10,
window_strong l <= 6). 늦은 시기 long_small offset은 VII_h 곡률 때문에 H가 평탄
FLRW 기준과 달라지는 데서 온다.

## 6. 해석과 한계

- 결과는 하나의 결정론적 배경 history가 만드는 비섭동 C_lm^XY template이다.
  원시 섭동, ensemble 공분산, family attribution, 보정된 p-값은 없다.
- 수송은 bolometric (주파수 적분)이다. 스펙트럼 왜곡은 없고, material 하늘의
  온도는 bolometric 세기의 1/4승이다 (스펙트럼이 섞이면 근사).
- harmonic 경로는 Galerkin 절단이다. focusing이 강한 VI*류는 L ~ 24-32가 필요하고,
  L이 부족하면 양성 guard로 실패한다 (조용히 틀린 답을 내지 않는다). 움직이는 전자의
  충돌은 (L+3)x(2L+6) 격자에서 pseudo-spectral로 처리한다 (정지 전자에서만 정확).
- matched recombination은 수소만, collapsed Peebles TLA, Compton 물질 온도, 헬륨
  전자는 표 그대로 (수소 비율 min(x_e, 1-1e-12); 기준 수소가 완전 이온화된 동안 응답 0), 1차 분할 (offset이 한 step 늦게 Thomson 셀에 들어감)이다. 모든
  방향의 Sobolev 팽창이 양수여야 하며 아니면 fail closed. 비용은 576 방향에서 table
  대비 약 5배다. REI `bass_ionization` 표를 쓸 때는 재이온화 구간 앞에서
  `--recombination-stop-eta`로 멈춘다 (TLA closure에는 이온화 광원이 없다).
- HYREC 표가 z = 1100에서 시작하므로 tight-coupling 시대는 들어 있지 않다.
  시연에는 재이온화가 없다 (REI 표를 쓰지 않았다).
- 장기 적분의 Gauss 제약 표류는 O(d eta^2)이다 (768 step에서 6e-4).
- htt_base `CLAUDE.md` 1절의 coverage envelope (full-mode LoS는 FLRW, I, V, IX;
  나머지는 축 정렬 부분집합; off-axis는 fail closed)은 htt_base Python/PSTF 소유
  dispatch의 경계다. 이 BASS native 결과는 그 경계를 바꾸지 않는다. 바꾸려면 소유
  dispatch와 scientific contract를 갱신하는 별도 작업이 필요하다.

## 7. 재현

```
cargo test --release --locked --manifest-path _rustcore/Cargo.toml
cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example homogeneous_sky --example sky_covariance
B=_rustcore/target/release/examples/homogeneous_sky
python3 research/r113_cloud_universal_lie_sky/run_cross_route_atlas.py --binary $B --work NEW_DIR --out NEW.json
python3 research/r113_cloud_universal_lie_sky/run_truncation_study.py --binary $B --work NEW_DIR --out NEW.json
python3 research/r113_cloud_universal_lie_sky/run_long_demo.py --binary $B --repo . --work NEW_DIR --out NEW.json
python3 research/r113_cloud_universal_lie_sky/run_recombination_demo.py --binary $B --repo . --work NEW_DIR --out NEW.json
```

REC: `cargo test --release --locked` (`rust/rec_microphysics`). JSON의
`binary_sha256`은 빌드 경로에 따라 다르다. 5.1-5.3의 JSON은 recombination coupling
이전 빌드로 만들었다. 이후 변경은 `--recombination matched` 없이는 동작하지 않으며,
최종 빌드로 atlas 3건 (VII_h harmonic24, VI* rays 24x52, IX harmonic8)의 모든 TSV가
byte-identical임을 확인했다.

## 8. 미해결 (다음 라운드 후보)

헬륨과 물질 온도를 matched step의 진화 변수로, offset의 Strang 분할, 스펙트럼
수송, REI 표와 결합한 재이온화 구간 검증, harmonic 경로의 Gaunt-정확 이동 전자
충돌, matched step 비용 절감 (방향 rate의 x 의존 부분 분리), z_emit >= 1600 표로
tight-coupling 시작.
