# BASS CE1-AA | 원래 연속 6-cell source의 두 번째 Gram 모드: 192비트 검증된 각도값

2026-10-30 KST · 하나의 제한된 실제 물리 결과 연구 단위 · BASS 상위 DAG **9/15**, 21 edges, CE1 PARTIAL.

## 이전 연구를 종합하되 중복하지 않은 기여

- #271는 원본 Rust 6개 경로의 총 10,086개 두 시점 K4 물리 레코드를 생성했지만 DOP853 오차와 Rust 평가의 MPFR 구간 인증을 남겼다.
- #270는 원본 6-cell continuum source에 대한 ℓ=4 source-only 오차를 직접 상계했다. source-only(동일 geometry) K4 delta ε: GL6 1.40028378356226026324×10^-7, GL8 4.847799002584115677×10^-9.
- #272는 원본 Rust Gram λ2 약 3.7866×10^-5로 관찰했지만 binary64 중심 오차 때문에 연속 source의 λ2>0을 인증하지 않았다.

**이번 CE1-AA의 새 물리 결과:** 원래 DOP853의 저장된 정확한 binary64 로그 척도인자 41개 각각을 *고정된 기하학 입력*으로 놓고, 원래 저장 GL6/GL8 ray/mass를 바꾸지 않은 192-bit `libmpfr` RNDD/RNDU angular energy, a40,a42,a44를 직접 산출했다. 모든 시점쌍 2×41²=3,362개의 K4δ에 바깥쪽 반올림 구간을 생성했다. Python `mpmath` 95자리로 별도의 식에서 6개 원본 상태를 교차검증했다.

## 실증된 수치 및 수학적 하계

| 인증 대상 | GL6 / 216 rays | GL8 / 384 rays |
|---|---:|---:|
| 저장 GL source λ2 근사 (41 epoch) | 3.786611468×10^-5 | 3.786611328×10^-5 |
| 검증된 저장 source λ2 엄격 하계 | >3.786×10^-5 | >3.786×10^-5 |
| PR270 source-only K4 error ε | 1.4002837836×10^-7 | 4.8477990026×10^-9 |
| Weyl operator perturbation ≤41ε | 5.74116×10^-6 | 1.98760×10^-7 |
| **원래 연속 six-cell source의 λ2 엄격 하계 (이 41개 저장 geometry 상태에서만)** | **>3.2118836487×10^-5** | **>3.7661240240×10^-5** |
| 인증 오차를 처음 넘어선 누적 표본 시각 | 15번째 u=.028 | 3번째 u=.004 |

**엄밀한 부등식:** 두 source의 실대칭 Gram K와 G 간의 41² 원소별 상계 ε로 `||K-G||₂≤41ε`; 따라서 Weyl `λ2(G)≥λ2(K)−41ε`. 저장 GL의 **정확한** Gram S=X^T X가 PSD, `tr S_lower>3L`이고, MPFR192 interval의 `det(S-LI)_upper<0`이므로 λ2(K)>L, `L=float64(3.786e-5)`로 통제한다. 두 채널에서 det upper는 약 −1.027×10^-13, trace lower는 약 0.443832 >3L이다. 원래 연속-cell source의 동일한 41개 로그척도 상태 K4에 대해 위 하계가 성립한다. 세 번째 고유모드에 대한 인증은 이 부등식으로 자동으로 도출되지 않는다.

**시간별 인증 시작점은 물리적 onset이나 검출 시간이 아니다.** 원래 모드의 존재는 처음 2개 표본부터 수치적으로 나타나지만 Weyl source bound가 더 커서 조기 인증되지 않는다. GL6에서 u=.028, GL8에서 u=.004는 각 구적의 보수적 source error를 넘어선 *첫 증명 가능 시점*이다.

## MPFR 연산과 실제 물리 자료

- `source/mpfr192_sky.py`: original binary64 ray/mass를 정확한 53-bit dyadic input으로 MPFR192에 넣고 exp, sqrt, π, 음수 곱셈 등 모든 산술의 내부 하한·상한을 RNDD(3)/RNDU(2)로 분리. 비단위 저장 ray를 임의 재정규화하지 않는다. `mpfr_number_p` 유한값 guard 포함.
- JSON에는 각각의 192-bit MPFR **16진수 mantissa + exponent**와 보수적 outward-binary64 endpoint를 모두 보존하고, 원래 DOP853 CSV에 있던 binary64 E,a와 interval의 차이도 실제로 측정해 기록했다.
- `source/interval_k4_spectrum.py`: 82개 원본 기하학 상태의 직접 source 평가를 2×41² K4 interval CSV와 2×41 누적 Gram 고유모드 물리 데이터로 변환. 정확한 유리수 source epsilon과 부등식의 양성/부호를 검사하고 모든 prefix 결과 저장.
- 각 상태의 `alpha` binary64 outward interval 폭 최대 2.78×10^-17, 전체 K4 double outward interval 폭 최대 1.74×10^-18. 이는 MPFR192 내부 연산을 이중으로 외향 변환한 결과이며, 53-bit 결과만으로 192-bit precision을 주장한 것은 아니다.
- `tests/test_mpfr192_physics.py`: source SHA, negative multiplication, π/√2, full K4 symmetry, prefix certification, tampered binary source 거부, 각각 초기/중기/종기 95자리 mpmath 독립 식, isotropic scaling, non-unit ray 보존 등 19/19 scoped tests PASS.

## 남은 과학적 의무

여기서 '연속 source'는 **입력 기하학적 상태가 정확히 주어졌을 때 적분하는 원래 여섯 angular cell distribution**이다. DOP853가 만든 41개의 상태가 실제 연속 Einstein–Vlasov 시공간 해를 감싼다는 **IVP 인증을 수행하지 않았다**. 따라서 진짜 우주의 시간진화/실제 관측 CMB/ensemble covariance/thermal temperature/polarization/likelihood/일반 Bianchi로 옮겨가지 않는다. PR270 조건부 원본 source bound와 직접 MPFR 평가 구현의 신뢰 범위도 명시적으로 보존한다. 독립 작성자 R6/C9, 전체 코드 형식검증 NOT_RUN. 생산/병합 false, AUTO_NEXT false.

**다음 단일 과학단위 (별도 승인 실행):** 원래 41개 DOP853 상태의 진짜 ODE 오차를 검증할 수 있도록 step별 dense-output coefficients를 원본 재생성 경로로 정확히 보존하고, verified Taylor-model/interval residual, knot jump, initial/source gap의 별도 전파를 구현한다. 그 후에만 본 192-bit source 및 Gram 하계를 실제 연속 Einstein–Vlasov 해로 옮길 수 있다.

## 주요 문헌

Lee, Nungesser, Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, GRG 52 (2020), DOI:10.1007/s10714-020-02699-7 (비등방성 장기 거동의 원전이며 이 작은 시간구간 인증의 증거 자체는 아님). Neher, Jackson, Nedialkov, *On Taylor Model Based Integration of ODEs*, SIAM JNA 45 (2007) DOI:10.1137/050638448 (남은 연속 궤적 검증에 관한 수치해석 원전).
