# CE1-Y 물리 연구보고서 | 원본 GL source에서 RK4/Hermite와 DOP853 두-시점 K4 하늘의 차이

**과학적 범위:** CE1-X PR #270 CI #40991211526의 원본 BASS native Rust / MPFR192 출력을 보존하여 실측된 GL6/GL8 자체 결합 Einstein–Vlasov 물리 경로를 *가상의 닫힘 없이* 별도 DOP853 저장 이력과 비교한다. 위상공간 angular cell과 초기 조건은 그대로 유지한다.

## 데이터 획득과 코드 연결

CE1-X의 원본 six-cell source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. BASS native Rust 물리 raw CSV 6개, PR270 original CI artifact #12949780334 내부 S2.zip에서 읽음. 각각에 원래 `u=t/Tstar` 41개, `E, Eprime, a_4m, (da_4m/du)`가 포함된다. 대조 DOP853 CSV 2개는 PR264의 이미 검증된 자기 결합 Einstein–Vlasov 이력이며 원본 SHA256 GL6 `6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489`, GL8 `1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502`와 byte-for-byte 같다. 새 source나 모델 파라미터를 만들지 않았다.

## 물리 이론

`alpha_4m(u) = (4π/E(u)) a_4m(u)`와

`K4delta(u,v)=1/9 Σ_{m=-4}^4 alpha_4m(u) conjugate(alpha_4m(v))`

로 두 시점 deterministic bolometric angular-energy kernel을 정의한다. 서로 같은 comoving normal observer tetrad axes로 비교하고, 원래 반사짝수 sky이므로 m=0,±2,±4만 남는다. Rust 원본의 모든 complex m 값을 직접 사용해 source에 대한 방위각 기울기를 보존하며, 독립적으로 `a40, a42, a44` 실수 대칭식으로 같은 값을 재검사한다.

`∂u K4delta = (1/9) Σ alpha'_4m(u) conj(alpha_4m(v))`, `alpha'_4m=(4π/E)[a'_4m-(E'/E)a_4m]`. 검산 대상으로 복소 켤레 대칭, Gram positive semidefinite, diagonal `K4delta(u,u)=C4delta(u)`, `|r4|<=1`, `D4²=C4δ(u)+C4δ(v)-2K4δ(u,v)>=0`를 사용했다.

## 실수치 신규 물리 데이터

6개 실제 원본 Rust RK4/Hermite 경로(2 GL sources × 3 panel counts)에 대해 각 41×41의 모든 두 시점 커널을 생성했다. 총 **10,086개의 물리 시간쌍** 및 조건부 source/geometry 경계 항목과 DOP853 동일-source 경험적 잔차. 원본 수치 경로를 재적분하거나 보간된 플루이드 closure를 만든 것은 아니다.

| Original source | panels | K4delta(0,.08) on original BASS Rust sky | max over (u,v) |K4delta_RK4 - K4delta_DOP853| | PR270 source+geometry exact-real functional bound |
|---|---:|---:|---:|---:|
| GL6 216 rays | 4 | 0.010792679530641270 | 3.6157428e-11 | 5.12857818e-5 |
| GL6 216 rays | 8 | 0.010792679535671585 | 2.3019555e-12 | 6.43372740e-6 |
| GL6 216 rays | 16 | 0.010792679535979706 | 1.4896938e-13 | 9.20632547e-7 |
| GL8 384 rays | 4 | 0.010792679541569098 | 3.6157497e-11 | 5.11505989e-5 |
| GL8 384 rays | 8 | 0.010792679546598918 | 2.3022660e-12 | 6.29854450e-6 |
| GL8 384 rays | 16 | 0.010792679546907028 | 1.4879764e-13 | 7.85449648e-7 |

**검증 출처의 단위:** 맨 마지막 열의 `exact-real` 조건부 수학 경계는 CE1-X의 소스+기하학적 ODE 차이를 바탕으로 한 연구 결과이며, 원본 BASS Rust binary64 sky 계산치와 정확한 수학적 GL sky 사이의 계산기 반올림 오차를 완전히 포함했다고 재해석하지 않는다. DOP853 결과의 **최대 차이는 오직 empirical numerical comparison**, 별도 DOP853 IVP outward certificate가 존재하지 않는다. 둘을 더해 DOP853 true-sky interval을 만든다는 주장은 금지한다.

`K4` 에너지적분 sky는 CMB blackbody T, polarization Q/U, ensemble covariance 또는 실제 서로 다른 광원뿔의 관측 likelihood가 아니다.

## 실측 과학 검증

`python -m pytest -q tests/test_ce1y_physical.py`: **19 passed**; 
`python -m compileall -q source tests`: 성공. 원본 2개 DOP853 CSV SHA, 6개 원래 Rust 결과와 source/path SHA identity, complex m parity, 더미 source tamper reject, 41×41 Gram/PSD, 정규화 common intensity rescaling, time derivative 직접 계산 및 5-point check, RK4-vs-DOP 실제 matrix 독립 재계산을 실시했다. 높은 정밀도 수치 일치는 엄밀한 DOP853 시간적분 인증을 대신하지 않는다.

## DAG와 다음 과학

Original BASS upper DAG **9/15**, 21 edges, CE1 PARTIAL, scope-specific R/C **18/20**. Truly independent authors R6 and C9 **NOT_RUN**, native subagents **NOT_EXPOSED**. production_ready=false, merge_ready=false, no_merge=true, auto_next=false. BASS 예산이나 허용 오차를 수정하지 않았다.

다음 연구는 완전한 interval sky error를 위해 원래 Rust harmonic evaluate에 대한 directed MPFR192 outward evaluator (구면조화각 m=4 포함)와 *해당 저장 DOP853 경로 자체에 대한* a-posteriori residual과 interval ODE enclosure를 실제로 실행하는 것. 추가 empirical RK4 panels는 이제 선행 결과를 중복한다.
