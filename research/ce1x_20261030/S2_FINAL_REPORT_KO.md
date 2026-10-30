# BASS CE1-X · 원본 여섯 셀의 4극 이상 각도 에너지 교차상관 인증

**2026-10-30 KST · 실제 실행 완료(범위 제한), 상위 DAG 9/15, CE-1 PARTIAL.**

## 1. 원본 계약과 재개 위치
- 부모: PR #268 고정 HEAD `c4d303ebd8294df8a4b564b140b88fc8e57b0e67`; 형제 PR #269의 기하 도함수 공식은 read-only 연구 근거로 사용함. 기존 어느 PR도 merge하거나 수정하지 않았음.
- 원본 물리: 여섯 양의 exact-binary angular cell SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`, 여덟 반사, 질량 없는 무충돌 전체 팽창 대각 Bianchi-I Λ=0, signature(-,+,+,+), u=t/Tstar∈[0,.08], 초기 shear(.2,-.13,-.07), 원래 기하 h 오차 문턱 1e-5, MPFR192 시간 인증. 본 단위의 `K_4^δ`는 **에너지 적분 normal-frame 하늘의 결정론적 두 시점 harmonic Gram kernel**이며 열역학적 CMB 온도, 확률적 cosmic variance, 관측 likelihood가 아님.

## 2. 압력-only 인증으로 해결되지 않았던 l=4 source
- PR #269의 중요한 반례: 양의 구면 분포 `U±∝1±η P4(n_z)`는 같은 E/P를 갖지만 `a40`은 서로 다르다. 따라서 PR #264의 압력 source 상계만으로 l=4을 인증하는 것은 불가능하다.
- 본 연구는 Condon-Shortley의 살아남는 세 실수 성분 `a40,a42,a44`의 정확한 양의 6-cell 원본 measure 적분을, n_x²,n_y²,n_z²의 다항식 × `r^(1-2m)` (`m=0,1,2`) 형태로 새로 구성했다.
- 참조 donor `research/ce1v_20261030/donor/ce1u_cert_source.py` (Git blob `0e8ef8375cf5f26a9a020d6ec878e4b77b5d0560`)의 exact-rational Machin π 및 integer-isqrt √2를 사용하여 **0차 포함 680개 모멘트(총 14차까지)**를 실제로 평가했다. 저장 GL ray/mass는 이상적인 GL node가 아니라 **저장 binary64의 정확한 dyadic rational**이며 비단위 ray의 `Σ w|Σn_i²-1|` 보정도 포함한다.
- `B=23/25`, `q=1/11`, `K=12`의 `(1+X)^β` 전개와 양의 tail bounds, `β∈{1/2,-1/2,-3/2}`을 적용해 원래 `0≤ell_i≤.08` 전체에서 source 오류 상계를 얻었다. 엄밀한 값은 `l4_source_and_transfer.json`의 exact Fraction 및 소수점 27자리 **올림** 표현으로 보존된다.

| 양의 저장 ray 수 | E source 상계 | a40 source 상계 | a42 source 상계 | a44 source 상계 | 두 시점 K4δ source-only 상계 |
|---|---:|---:|---:|---:|---:|
| GL6 · 216 | 2.00985e-13 | 1.99819e-11 | 3.05686e-11 | 4.47227e-10 | **1.40028378356226e-7** |
| GL8 · 384 | 1.15393e-13 | 1.25596e-11 | 1.53746e-11 | 1.26032e-11 | **4.84779900258412e-9** |

## 3. 근사 시공간 경로를 새로 MPFR192 인증하여 결합
- 해당 GitHub run은 부모의 저장 결과를 그냥 복사하지 않고 동일 GL6·GL8 물리 source를 유지한 채 **별도의 4/8/16패널 RK4/Hermite 6개**를 생성, 모든 시간 패널의 `residual_taylor_mpfr` 4계 majorant와 이진 Hermite knot jump, 원래 초기조건 차이를 MPFR192 양의 Dini 비교로 다시 포위했다.
- 새로 생성된 `path.coefficients` SHA256을 그대로 native Rust 호출 전후 검사하여 **신규 경로와 해당 MPFR192 인증의 byte identity를 같은 CI 내부에서 확인**했다. 과거 CI 경로가 새 경로와 같다는 허위 주장은 하지 않는다.
- `E≥3/5`, `4π<13`, `max|Y_4m|<1`, `|∂_ell_j K4δ|<41`을 사용해 모든 두 시점 `u,v∈[0,.08]`에 대해
```
|K4δ_continuum_exact(u,v) − K4δ_stored_RK4_Hermite(u,v)|
 ≤ epsilon_K4_source + 246 * epsilon_ell_MPFR192_full_path .
```
이는 PR #269의 **별도 DOP853** 물리 이력에 대한 인증이 아니다.

| 패널 | GL6 두 시점 K4δ 총 상계 | GL8 두 시점 K4δ 총 상계 |
|---|---:|---:|
| 4 | **5.128578180031384e-5** | **5.115059888204371e-5** |
| 8 | **6.433727404227464e-6** | **6.298544496523813e-6** |
| 16 | **9.206325465513986e-7** | **7.854496482066573e-7** |

GL6에서는 16패널 시점에 전체 상계 중 약 15.21%가 source-only 상계이며, GL8에서는 약 0.62%다. 따라서 높은 kernel 정확도가 실제로 필요하다면 패널 수와 양의 ray 해상도를 함께 결정해야 한다. 기존 원래 **h 오차 허용 1e-5**는 이미 4패널에서 충족하므로 이를 새 K4 목표로 오인해 gate inflation을 하지 않는다.

## 4. 원본 BASS native Rust를 실제 사용한 독립 수치 검산
- BASS 현재 원본 `_rustcore/src/kinetic/comoving.rs` Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`. Github runner Rust 1.94.1로 `research/ce1r_20261030/sky_time_derivative.rs`를 실제 컴파일하고 원본 `Frame::apply/det/phys_dirs`를 호출한다.
- 저장 GL6/GL8 각각 N4/N8/N16 경로 ×41고유시간, 총 **246개 Rust 다극 스냅샷**에서 `a40,a42,a44`, E, `K4δ(0,.08)`을 계산, 독립 NumPy 양의 angular polynomial 구현과 최대 **7.216449660063518e-15** 차이. GL6/GL8 교차차이는 모든 N에서 두 개의 엄밀한 continuum 상계 합 이하임을 독립 수치 반례 검색으로 검산. Rust binary64 결과를 MPFR192 증명이라고 주장하지 않음.

## 5. 실행·증거·정책
- [GitHub Actions #40991211526](https://github.com/cosmosapjw-quantum/bass/actions/runs/40991211526) **SUCCESS**, scoped **13/13 pytest PASS**, 6개 실제 재실행된 MPFR192 시간 carrier, 680 exact-rational moments×2 GL source, original Rust 246 snapshots PASS.
- Stage S0 Git `aa0e56059a63dd8c500a3345b071c52353ccc8f3`; S1 Git source+tests commit `8c522d93d385d0c33a66654bfcc010e61d38931e` + original Rust code; S2 최종 보고서·handoff·machine DAG를 새로 게시한다.
- 검증된 S0/S1/S2 GitHub artifact ID 각각 `12948688644`, `12949203100`, `12949780334`. 각 ZIP CRC+payload SHA256 및 S0/S1 내부 checkpoint byte identity 통과.
- Drive S0 `1Pl3J15u35zJ796s1jaHlDel_Ri_SNf4M`, S1 `1pyATHMw9E4XiV609WqyMnV5Aj3ngPbSN`, S2 `17CG3O3UBE4lB1gkNmFqF2CYKeO7DYKd0`; **전체 바이트 SHA256 재다운로드 모두 일치**. Dropbox `/BASS_BACKUPS/BASS_CE1X_{S0,S1,S2}_20261030_*.zip` provider content hash·크기 모두 일치, 전체 바이트 재다운로드 NOT_RUN.
- **상위 DAG 9/15 (21 edges), CE1 PARTIAL**; `production_ready=false`, `merge_ready=false`, `auto_next=false`. 실제 별도 저자 R6/C9, 전체 MPFR/Rust compiler 형식증명, tilt/Thomson/polarization, cosmological observation likelihood NOT_RUN. 부모/형제/main 불변, Draft와 독립 백업만 보존.

**다음 단위:** 수학적으로 닫힌 l4 source/geometry 예산을 실제 지정된 관측량이나 분명한 tolerance에 적용하거나, 남아 있는 상위 DAG 물리 노드와 원격 독립 저자 검토를 진행한다. 물리적 이유 없이 네 패널 이상의 적분을 자동 채택하거나 검증된 DOP853 이력과 RK4 경로를 혼동하지 않는다.
