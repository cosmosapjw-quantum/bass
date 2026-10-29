# BASS CE1-P · Native Rust comoving photon source bridge | 최종 연구 보고서

**2026-10-29 · 범위 제한 완료, 상위 DAG 9/15, CE-1 PARTIAL**

## 1. 원본과 변경 경계

기준 저장소는 `cosmosapjw-quantum/bass`이며, 부모 Draft PR #256의 고정 HEAD는 `3a7a38f9615f100fddda0379bd3d6ec359ccc586`이다. CE1-P는 독립 자식 Draft PR #257 (`research/bass-ce1p-native-rust-comoving-20261029-r1`)에서만 작업하였다. 부모 PR, main, BASS 원본 `_rustcore/src/kinetic/comoving.rs`는 변경하지 않았다. 원본 Rust 모듈의 Git blob은 `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`이다.

새 Rust 과학 진단기는 `research/ce1p_20261029/rust_comoving_stress.rs` (Git blob `2726a1336a6584f3820289a9ea47f1beca3295dc`)이고, 독립 Python 대조기는 `research/ce1p_20261029/compare_rust_to_ce1.py` (Git blob `cff82535d13be36258b3843340989120d0a531ea`)이다. Rust 진단기는 직접 `#[path="../../_rustcore/src/kinetic/comoving.rs"]`을 참조하고 **원래 BASS `Frame::apply/det/step`를 직접 실행**한다. 별도 대체 구현이나 Python만의 surrogate가 아니다.

원본 보호 물리: 양의 연속 각도 셀과 양의 저장된 이진 ray·mass, 질량 없는 무충돌·반사대칭·세 방향 팽창 대각 Bianchi-I, Λ=0, 계량 부호 `(-,+,+,+)`, `u=t/Tstar`, 원래 6개 각도 셀, shear `(0.2,-0.13,-0.07)`, `u∈[0,0.08]`, RK4/Hermite 4개 패널, MPFR192, 원래 정확도 문턱 `max_i |Δh_i| < 10^-5`. CE1-M의 384-ray 상계 `9.411551484445186e-6`는 그대로 선행 연구 근거를 재사용하며 **이번 CE1-P에서 Rust로 새로 인증하지 않았다**.

## 2. 실제 수학적 계산과 네이티브 BASS Rust

`ell_i=ln a_i`, `M=diag(exp(-ell_i))`, 공변 광선 방향 `n_a`, 양의 저장 질량 `w_a`, `q_a=M n_a`, `v=det(M)`로 둔다. 현재 저장 source의 부피가중 에너지와 방향 압력은

```
E_Q = v * sum_a w_a * |q_a|
P_Qi = v * sum_a w_a * q_ai^2 / |q_a|
J_ij = -(1+2*delta_ij)*P_i
       + v * sum_a w_a*q_ai^2*q_aj^2/|q_a|^3
```

이다. 임의 고정 양의 source에서 `sum_i P_i=E_Q`, `sum_j J_ij=-4P_i`, 공통 로그스케일 변환 `P_i(ell+s1)=exp(-4s)P_i(ell)`을 계산적 불변량으로 검증하였다. 실제 `Frame::step`는 정상 고유시간 `u`가 아니라 e-fold 시간 `tau`의 `dM/dtau=-(I+Sigma)M`을 구현하므로, 그 native self-test는 별도 e-fold 시간 계약으로 검산했다.

이 Rust 코드는 binary64 진단기다. 외향 MPFR192 interval 계산을 대체하지 않으며, 엄밀한 전 구간 인증이나 production 계산코드라고 주장하지 않는다.

## 3. 실제 실행과 CI 증거

이번 턴에 업로드된 오프라인 Rust 1.94.1을 격리 경로에 설치했으며 로컬 `rustc 1.94.1`, Python 3.13.5, C++ g++14.2.0 실행을 확인했다. 로컬 과거 BASS 오프라인 번들의 `comoving.rs` Git blob `25669ec464ab279e1a4d2421400a8ed135ae9638`은 최신 GitHub blob과 다르다. 따라서 로컬 전체 Rust 모듈의 바이트 동일성은 **주장하지 않는다**. 핵심 Frame 공식은 대조했다.

**독립적인 현재-head 검증:** GitHub Actions [CE1-P #40884723128](https://github.com/cosmosapjw-quantum/bass/actions/runs/40884723128) 성공. 실제 워크플로에서 `rustc +1.94.1`, 현재 Git blob 검사, 현재 `_rustcore/src/kinetic/comoving.rs` 직접 컴파일 후 다음 로그를 얻었다.

```
CE1P_RUST_SELFTEST_4_PASS
CE1P_NATIVE_REJECTS_BAD_RAYS_4_PASS
CE1P_RUST_BASS_COMOVING_STRESS_AND_JACOBIAN_DIFF_PASS
83 passed in 18.03s
```

고정 및 허용된 변형 양의 입력에서 저장 광선수 6·24·96·384, source 설정 24개, 광학/기하 상태 96개를 서로 독립적인 Rust 및 Python 구현으로 계산했다. 원본 refinement8 ray/mass 바이트 SHA가 CE1-M 기록과 일치한다.

| 검사 | 관측 최대 절대 차이/잔차 |
| --- | ---: |
| Rust↔Python E | 3.219646771412954e-15 |
| Rust↔Python P | 1.6653345369377348e-16 |
| Rust↔Python analytic J | 5.551115123125783e-16 |
| 질량 없는 trace sum P - E | 3.9968028886505635e-15 |
| Jacobian row sum sum_j J_ij +4P_i | 6.661338147750939e-16 |

원본 양의 저장 source를 훼손하는 4종 입력도 native 경로에서 거부되었다. 실행시간 가속 비교는 이번에 수행하지 않았으며 384-ray 허용 결과에서 4배 speedup을 주장하지 않는다.

## 4. 백업 및 판정

- **S0 Git:** `8b74a37368688ac56ba3964433140d309e00feab`; ZIP 9,765 bytes, SHA256 `a5e754d2d941835054d43ba6aee41a8823dc7c0b85a202c32d7f1cfd6c5a0e4d`; [Drive S0](https://drive.google.com/file/d/12G8DS2mwtACeR9g4m7B3i9hBbtxuPGVb/view) 원본 전체 바이트 readback match.
- **S1 Git:** `1a73ee9b6e6dd895ade51d68ba3bebbe3ea9e4cc`; ZIP 18,948 bytes, SHA256 `4a6007d5665178f867f274639f606ba7ddf6b66c61075598e4e7d144fd5fe1b0`; [Drive S1](https://drive.google.com/file/d/1QbbaqIffYbCdgXtKzVc_7SLqxw_Vbkfv/view) 원본 전체 바이트 readback match.
- Dropbox 원본 ZIP 업로드는 `fileParam` 인자 타입 불일치 및 Library read-only로 **BLOCKED**. 대신 `/BASS_BACKUPS/`에 [Dropbox Paper S0](https://www.dropbox.com/scl/fi/whll86g8yqjwqh9frrytu/BASS-CE1-P-20261029-S0-Rust-native-source-and-proof-checkpoint.paper?rlkey=4tnuj6h6zh7lk5ed8i0gis40m&dl=0), [Dropbox Paper S1](https://www.dropbox.com/scl/fi/sfy0kfihh1uy1efdb4py5/BASS-CE1-P-20261029-S1-native-Rust-CI-and-differential-evidence.paper?rlkey=h29q1xxytuhlcnn6t7t6dui3u&dl=0) **텍스트 체크포인트를 실제 생성하고 readback 검증**했다. 이는 ZIP 바이트 이중백업이 아니다.
- **S2:** 최종 보고서/다음 handoff/기계 판독 DAG와 S0/S1 ZIP을 포함하는 S2 ZIP을 create-only로 게시한다. S2 Git/Drive/Dropbox Paper 영수증은 최종 delivery receipt에서 따로 고정한다.

**최종 과학 판정:** `COMPLETE_SCOPED_NATIVE_BASS_RUST_DIFFERENTIAL`, upper DAG **9/15**, CE-1 **PARTIAL**, `production_ready=false`, `merge_ready=false`, `auto_next=false`. 실제 독립 인간 저자 R6/C9, formal Rust/CPython/MPFR 프로그램 증명, 재연결한 native Rust 자체의 MPFR192 outward interval 인증, 본격적인 polarized Boltzmann 등은 NOT_RUN/NOT_ADMITTED.

**다음 단일 과학 작업:** 이미 검증된 binary64 BASS native source E/P/J 계산기에 **동일 물리 입력의 방향성 구간 오차 계약을 연결할 수 있는 검증 가능한 Rust/native 수치 어댑터**를 설계·구현하여 기존 CE1-M MPFR192 외향 인증을 침범하지 않는 이중 구현 parity를 확립한다. 생산 승격이나 sibling PR 병합은 별도 검증 이후 판단한다.
