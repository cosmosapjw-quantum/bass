# BASS CE1-R | 공변 광자 sky Liouville 고유시간 진화와 ℓ=4 구적 병목의 Rust 실측

**연구 단위:** CE1-R. **날짜:** 2026-10-30. **신규 Draft PR:** #261 (`research/bass-ce1r-liouville-rust-sky-20261030-r1`). **부모:** PR #259 (`e963b3cff4a6f91d4060e05080d1e6e2667e001b`), 물리 시간 이력 PR #258 (`0656e98989750de4ea19c510ff2052654aaa3eda`), 별도 검증된 Rust E/P/J PR #257 (`baa29ff5b5d0384f62e2627ebc8b37d34d7aa26b`). 세 부모/형제 및 main은 변경·병합하지 않았다. 원 BASS `comoving.rs`의 Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84` 보존.

## 1. 사용자가 잠근 물리 모형 및 실행 경계

원래 exact-binary64 여섯 양의 angular cell, 여덟 부호 반사, 질량 없는 무충돌·정규 관측자·세 방향 팽창 대각 Bianchi I, Λ=0, 부호 `(-,+,+,+)`. `u=t/Tstar`, `ell_i=ln a_i`, `h_i=Tstar H_i`, 초기 shear `(0.2,-0.13,-0.07)` 및 `[0,0.08]`의 41개 고유시간 표본은 PR #258에 귀속. 기존 CE1-M 384-ray 네 RK4/Hermite 패널의 **별도** MPFR192 `max|Δh|<=9.411551484445186e-6<1e-5`를 유지하지만, 이 연구의 도함수/sky에 대한 새로운 MPFR 인증으로 재사용하지 않는다. 본 연구의 sky는 **energy-integrated unpolarized normal-frame angular observable**이며 실제 CMB 열역학적 T, Q/U, tilt, recombination, likelihood가 아니다.

## 2. 이론 R단계: 원본 BASS Rust 프레임과 Liouville 전파

Spatial Killing에서 공변 `q_i` 보존. `M=diag(exp(-ell_i))`, `r=|Mq|`, 입사 sky `s=-Mq/r`, `W=det(M)*r*dE0`, `θ=Σ h_i`, `H_s=Σ h_i s_i²`으로부터

`ds_i/du=(H_s-h_i)s_i`, `dW/du=-(θ+H_s)W`,

`da_lm/du = ∫ W [-(θ+H_s)Y*_lm(s) + ∇_S Y*_lm(s)·ds/du]`.

원래 연속 angular cell source의 brightness `U`에는 특성곡선/약한 의미에서 `∂_u U+(ds/du)·∇_S U=-4 H_s U`가 성립한다. 불연속 셀 경계에서는 고전적 전역 매끄러움, 저장 ray에서는 pointwise brightness 함수를 주장하지 않는다. 극점에서 `atan2` 분할을 피하려고 Condon–Shortley Cartesian polynomial `Y*_lm=N_lm(-1)^m (d_z^mP_l(z))(x-i y)^m`의 정확한 곱 미분을 ℓ≤4에 사용했다.

검증될 모멘트 식:

`E'=-θE-Σh_iP_i`, `P'_i=-(θ+2h_i)P_i+Σ_j h_jR_ij`, `R_ij=∫W s_i²s_j²`;

`a'_20=√(5/(16π))(3P'_3-E')`, `a'_22=√(15/(32π))(P'_1-P'_2)`;

`C'_ℓ=2 ReΣ_m a*_lm a'_lm/(2ℓ+1)`.

Rust CLI `research/ce1r_20261030/sky_time_derivative.rs`는 **실제 BASS 원본 `_rustcore/src/kinetic/comoving.rs`의 `Frame::apply`, `Frame::det`, `phys_dirs`를 직접 참조**하며 변환 스케일/방향을 독립 연산한다. `Frame::step`의 e-fold τ를 고유시간 u로 잘못 사용하지 않는다. 부정 질량, 비유한·영 ray, 비단위 방향, 유효하지 않은 h/ell/time은 입력 단계에서 거부한다.

## 3. 실제 Rust/C6–C8 검증

현재 로컬 Python3.13 및 사용자 제공 Rust1.94.1 배포본으로 컴파일한 실제 실행파일이 selftest를 통과했다. **로컬로 추출한 과거 BASS comoving.rs는 Git blob `25669ec464ab279e1a4d2421400a8ed135ae9638`로 현재 HEAD와 바이트가 다르므로** 첫 로컬 합성시험은 조건부이다. 원격 GitHub Actions는 HEAD 파일을 원래 Git blob에 pin하고 Rust1.94.1로 재컴파일하였다.

- **원격 native CI 1:** [#40908995659](https://github.com/cosmosapjw-quantum/bass/actions/runs/40908995659) SUCCESS. 기존 PR #259 실제 384/1,536-ray, GL24 3,456-ray, GL40 9,600-ray, 각각 고정 41 고유시간 기록에서 Python-independent Scipy `sph_harm_y`, 순간 방향미분, 기존 5점 시간미분, 4계 압력 모멘트 및 quadrupole derivative 정합성 검사 모두 PASS. 164 실제 이력 행의 도함수 CSV/JSON과 합성 대조를 GitHub Actions artifact #12912957334로 확보.
- **원격 native CI 2:** [#40909891131](https://github.com/cosmosapjw-quantum/bass/actions/runs/40909891131) SUCCESS. 추가로 같은 **GL40 배경 **(`ell,h`) 아래 384/1,536-ray source만 치환한 비자가일관적 통제계산을 41개 시간에서 수행하여 총 246개 실제 이력 행(각 41 × 6)과 별도 합성 행을 확보. Artifact #12912164871, 직접 다운로드 ZIP byte SHA-256 `af019744f71903bb44c7ef44363ff946650839bbbaedd5c3c65ebe234f86426e`, 14 파일, CRC PASS. 문서용 결과/원시 도함수 CSV 재현 가능.
- 네 자가일관 채널에서 SciPy 방향 도함수와 Rust 도함수 최대 차이 `4.410229959006529e-10` (GL24); 원래 저장 41점 harmonics의 5-point 도함수와 최대 `1.7611245795023933e-10` (ref8); GL40 에너지 연속식 잔차 최대 `7.860379014346108e-14`, 압력미분 모멘트 잔차 최대 `1.0735856648125264e-13`. 원래 저장 harmonics와 새 Rust A_lm 값 최대 `1.25e-16`. 41점 `C_l'`의 composite Simpson 적분과 저장된 처음/끝 `C_l` 차이는 ℓ=2 최대 `1.12e-13`, ℓ=4 최대 `1.21e-15`. 그 목적은 물리 코드 반례 탐색과 고유시간 연결 확인이며 **엄밀한 전 구간 interval error certificate가 아니다**.

## 4. 새 과학 결과: 고차 각도 다극의 시간미분에서 source aliasing

`u=0.08`에서 GL40 (연속 6-cell의 **수치** 구적) 기준 `C'_2=-0.0011371442391815186`, `C'_4=-0.00014789130274602826`.

| 채널 |  `C'_2` | `C'_4` | GL40 대비 `C'_4` 상대 차이 |
|---|---:|---:|---:|
| stored f=8, 384 rays | -0.001137150787827793 | -0.000170048075377858 | 14.9818% |
| stored f=16, 1536 rays | -0.001137145885940285 | -0.000153228024091811 | 3.60854% |
| GL24, 3456 rays | -0.001137144239181607 | -0.000147891302746046 | 약 1e-13 relative |
| GL40, 9600 rays | -0.001137144239181519 | -0.000147891302746028 | 수치 기준 |

`C'_2`는 384-ray에서도 GL40 상대 차이 약 `5.75885e-6`(약 0.000576%)이다. 그러나 같은 해상도에서 `C'_4`는 14.98%다. source 구적 오차와 서로 다른 Einstein 기하 이력의 기여를 분리하기 위해 **GL40의 동일한 (ell_i,h_i)만 고정**하고 stored f=8/f=16 source를 끼워 넣었다.

| `C'_4` 차이(GL40 기준) | source만의 기여 | 다른 배경 이력의 기여 | 총 차이 |
|---|---:|---:|---:|
| f=8 | -2.215675885293769e-5 | -1.377889241507141e-11 | -2.215677263183011e-5 |
| f=16 | -5.336717455987515e-6 | -3.889795386832762e-12 | -5.336721345782901e-6 |

source에 대한 부호 있는 비율은 각각 **99.9999378%, 99.9999271%**이다. 따라서 이 고정된 모델/시점에서는 고차 다극 시간미분에서 **주요 오차 원인이 각도 source 구적**이라고 강하게 지목할 수 있다. 이는 엄밀한 연속체 상계가 아닌 GL40 numerical reference에 대한 비교이며, hybrid background 동작은 자가일관적 Einstein–Vlasov 새 해가 아니다. 다른 배경에서 이 비율이 유지된다는 일반 명제도 아니다.

## 5. 음성 결과, 제한 및 후속 연구 방향

- `C_l^U`는 **normal-frame energy-integrated sky**의 2차 통계. 유효한 CMB 템플릿/temperature/Q/U/likelihood가 아니다.
- 현재 실행은 binary64 Rust 실행과 독립 SciPy 비교다. CE1-M의 MPFR192 geometry certificate를 sky derivative에 자동 전파하지 않는다.
- 오차 15%는 정규화 및 동기화된 표본의 상대 차이이다. 실제 고정 물리계는 원래 anisotropic sky를 이미 갖는다. 원격 GPU 또는 병렬 성능 향상을 측정하거나 주장하지 않는다.
- 실제 외부 **distinct-author R6/C9**와 완전한 Rust/Cargo/native wheel production admission은 NOT_RUN. 사용자에게 약속된 상위 DAG는 **9/15**, CE-1 PARTIAL, 21 edges, `production_ready=false`, `merge_ready=false`, `auto_next=false`.

**다음 진짜 미완료 한 단위 제안:** CE1-S, Rust 기반 ℓ=4 시간도함수의 각도 셀별 적응형 구적 또는 cellwise a posteriori error estimator 연구. 원래 여섯 물리 셀과 source mass·proper-time h_i를 고정하고, 실제 GL24/GL40 수치값에만 의존하는 재보정 대신 **양의 셀 measure에 대해 분명한 angular error budget을 이론부터 유도**할 것. 동일 물리 정확도에서 rays/시간을 실제 측정하지 않으면 속도 향상은 주장 금지.

### 단계별 Git·Drive·Dropbox

S0 이론 및 로컬 합성 native: Git `c65deacf42fec0728e63e2b1ef7ca2c3dbb44940`, Drive ID `1fF5a8Arwao06bI8fE0O43Sp8ln2k5f-N`, Dropbox ID `id:BSpOijBcT10AAAAAAEHV4Q`, ZIP SHA `8bdd2683313606191542897ddd64df948592c177fa0bdd8119af2bc3d1ee14ea`.

S1 Rust 코드·실제 CI 계약: Git `950cf4ba2aca7130c6266298c870aed1a0b7db02`, Drive ID `11hm52bWPMFIF5GLr2-Q__d38yPPJBv4g`, Dropbox ID `id:BSpOijBcT10AAAAAAEHV5g`, source ZIP SHA `954245e4e5717c9705a568fcc9a65b5ace9b635c1155cd206f5ed6d9e62753b5`.

S2 최종 산출물 ZIP·Drive·Dropbox의 실제 object ID와 SHA는 본 보고서 게시 후 **PR 설명 및 `DELIVERY_RECEIPTS.json` 최종 영수증**을 참고해야 한다. 어떤 단계에서도 `9/15`를 임의로 `10/15`로 승격하지 않았다. Google Drive S0/S1 full-byte SHA256 readback MATCH, Dropbox provider content hash+size MATCH. S2도 별도 검증 예정이다.
