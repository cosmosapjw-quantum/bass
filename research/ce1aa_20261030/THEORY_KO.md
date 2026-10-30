# BASS CE1-AA | 원래 연속 6-cell source의 조건부 두 번째 시간적 하늘 모드 인증

2026-10-30 KST · S0 이론 연구 · 상위 BASS DAG **9/15**, 21 edges, CE1 PARTIAL

## 동일한 물리 모델과 출처
- 원본 `cosmosapjw-quantum/bass`, PR #271 물리 DOP853 41 표본, PR #270 원본 연속-cell 대 GL6/GL8 `ell=4` source-only 상계, PR #272 Rust Gram 스펙트럼. 세 PR 모두 수정·병합하지 않는다.
- 원본 six angular cells binary64 SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`; 원본 BASS Rust `comoving.rs` Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`.
- 양의 반사짝수, 질량 없는 무충돌 복사, 대각 팽창 Bianchi I, Λ=0, signature (-,+,+,+), `u=t/Tstar∈[0,.08]`, shear(0.2,-0.13,-0.07), 원래 GL6(216)·GL8(384) ray/mass를 저장 binary64 값 그대로 정확한 이진유리수로 해석한다.
- **관건:** 41개의 DOP853 저장 `ell_i(u_j)`는 이 실험의 엄밀하게 고정된 입력이다. **그 숫자가 진짜 Einstein–Vlasov ODE 해를 에워싼다는 인증은 이 실험의 결과가 아니다.** 이 기하학적 상태들의 연속 원래 source에 대한 수학적 정리를 증명한다.

## 구성적 모멘트 유도

`b_i=exp(-2ell_i)`, `V=exp(-Σell_i)`, `r²=Σ b_i n_i²`, `x=b_x n_x²/r²`, `y=b_y n_y²/r²`, `z=b_z n_z²/r²`. Stored GL ray는 단위 구면의 반올림 오차가 있을 수 있으므로 **재정규화하지 않는다**. 양의 가중치 `w`를 모두 저장 이진유리수 그대로 쓴다. 원자측도 합 기호를 `Σw`라 하면

```
E=V Σw r
C40=3/(16 sqrt(pi)), C42=3/8 sqrt(5/(2pi)), C44=3/16 sqrt(35/(2pi))
a40=C40 V Σw r (35z²-30z+3)
a42=C42 V Σw r (x-y)(7z-1)
a44=C44 V Σw r (x²-6xy+y²)
alpha4m=(4pi/E) a4m
X(u)=(alpha40,sqrt(2)alpha42,sqrt(2)alpha44)/3
K4delta(u,v)=X(u).X(v), S41=Σ_j X(u_j)^T X(u_j).
```

비편광 `ell=4` 하늘의 두 시점 Gram `K=XX^T`와 3×3 `S=X^T X`의 비영 고유값이 일치한다. `S`는 실대칭 양의 준정부호다. 원래 반사짝수 분포의 `m=0, ±2, ±4`만 살아남으므로 rank≤3. 이는 확률 ensemble covariance가 아니라 특정 고정된 normal-observer bolometric angular-energy 하늘의 결정론적 구성이다.

## 새 검증 가능한 두 번째 모드 정리

`L>0`인 *정확히 지정된 binary64 수*에 대해 **직접 원본 저장-source MPFR192 RNDD/RNDU** 3×3 Gram 구간을 구한다. 만약

```
tr(S)_lower > 3L,
det(S-LI)_upper < 0,
```

가 모두 성립하면 `λ1≥tr(S)/3>L`이고 세 고유값이 실수이므로 `det(S-LI)<0`는 `λ3<L<λ2`를 뜻한다. 따라서 **저장 GL source의 정확한 실수 계산에서 `λ2>L`**.

원래 PR #270은 동일 로그 척도 인자 `ell`와 동일 ray source에 대해 매 두 시점 `|K4_cont−K4_GL|≤epsilon_K`를 엄밀하게 위로 묶는다. 41×41 원소별 bound와 유도된 2-norm ≤41ε_K, Weyl 부등식으로

```
lambda2_cont_original_source_on_fixed_41_geometry_states > L−41 epsilon_K.
```

이 조건은 **연속 original six-cell angular source를 저장된 41개 binary64 DOP853 상태에 두었을 때**의 수학적 정리다. 실제 연속 Einstein–Vlasov 시공간에서 진화한 두 번째 고유모드의 interval certificate는 아직 아니다.

## 수치 인증 범위

- 연산기는 실제 `libmpfr.so.6` 192-bit, `mpfr_set_d` (입력 exact), `mpfr_exp`, `mpfr_sqrt`, `mpfr_const_pi`, `mpfr_add/sub/mul/div`를 각각 RNDD(3), RNDU(2) 방향으로 계산한다. 출력은 원래 192-bit base16 mantissa+exponent와 추가 외향 binary64 endpoints를 모두 보존한다.
- 원본 양의 GL ray와 mass의 SHA256 및 41개 저장 상태 CSV SHA256을 fail-closed 검사한다. 기하학적 상태는 오차범위가 아니라 정확한 지정입력이다. 모든 비단위 ray norm은 그대로 포함한다.
- `L=3.786e-5`를 exact-binary64로 사용한다. GL6,GL8 둘 다 `det(S-LI)_upper<0`, `tr(S)_lower>3L`.
- 원래 PR270 `K4` source-only 상계 GL6 `1.40028378356226026324e-7`, GL8 `4.847799002584115677e-9`를 Weyl로 전파한다.
- 41회적 full Gram의 continuum source λ2 lower: GL6 **3.2118836487394732965e-5**, GL8 **3.7661240240894051301e-5**. 전체 원래 물질 source의 구간 인증이지만 **41 DOP853 geometry state 자체에 조건부**다.
- 누적 41접두 구간에서는 첫 `λ2_GL > k eps_source`가 인증되는 GL8 `u=.004`(3개 표본), GL6 `u=.028`(15개 표본). 이것은 물리적 모드가 처음 발생하는 시간이 아니라 **더 높은 GL order에서 인증 오차를 처음 넘어가는 시점**이다.

## 엄밀성 경계와 다음 연구

원래 PR #268/270의 MPFR192 RK4/Hermite 4/8/16 panel geometry certificate가 이 저장된 DOP853 41상태를 인증하는 것은 아니다. 지금의 MPFR192는 **고정 binary64 기하 상태에서의 angular source + Gram 계산**을 인증한다. `DOP853` continuous dense polynomial residual 구간, initial/boundary/knot state error, 전체 `ell`-trajectory enclosure는 NOT_RUN. 형식적 Python/libmpfr 전체 프로그램 검증, genuinely distinct-author R6/C9, 관측 likelihood, thermal CMB/polarization, 다른 Bianchi family도 NOT_RUN.

상위 DAG 9/15; CE1 PARTIAL, production_ready=false, merge_ready=false, auto_next=false. 연구 단위는 한 번에 한 개로 중단한다.

## 원전

- Ho Lee, Ernesto Nungesser, Paul Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, GRG 52 (2020), DOI 10.1007/s10714-020-02699-7. 장기 등방화 논문으로 이번 finite-time 구간 정리 자체의 원전은 아니다.
- Neher, Jackson, Nedialkov, *On Taylor Model Based Integration of ODEs*, SIAM JNA 45 (2007), DOI 10.1137/050638448. 앞으로 남은 DOP853 진정한 IVP 경로 인증 방법론의 참고문헌이다.
