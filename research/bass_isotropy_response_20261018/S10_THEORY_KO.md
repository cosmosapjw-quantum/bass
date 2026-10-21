# S10 — 정확한 연산 재사용과 최적화의 수학적 경계

이 문서는 S9의 같은 frozen cohort 함수값을 계산하는 비용을 줄이기 위한 유도다. 새로운 continuum 또는 P6 admission 결과가 아니다. 원 source `4b30957cb008aad8019bb1a673937fc67bd017e8`, fixed spectral owner `0e25846433170d0f420c4cda44a0bedbf02cd177`, metric/출생/양의 weight 계약은 유지한다.

## 1. 정확한 kernel과 부호 검산

한 immutable cohort에서 \(d=b-b_{\rm birth}, z=\mu^2\)로 놓고
\[
a=e^{2d}(1-z),\quad c=e^{-4d}z,\quad R=\sqrt{a+c},\quad N=c-a/2,\quad D=N/R
\]
를 쓴다. 원 energy/pressure의 ray 합은 \(F=\langle R\rangle,G=\langle D\rangle\), cohort amplitude는 \(E_{\rm birth}e^{-4(x-u)}\)다. 미분하면
\[
R_b=-2D,\qquad D_b=\frac{-4c-a}{R}+\frac{2N^2}{R^3}
=-\frac{a^2/2+7ac+2c^2}{(a+c)^{3/2}}.
\]
또 \(q=c/(a+c)\in[0,1]\)이면
\[
D_b=-R\left(\frac12+6q-\frac92q^2\right),\qquad
\frac12\le\frac12+6q-\frac92q^2\le\frac52.
\]
따라서 양의 weight와 amplitude에서 \(-\tfrac52E\le\partial_b\Pi\le-\tfrac12E\)가 exact real arithmetic에서 성립한다. \(q=2/3\)에서 상계, \(q=0\)에서 하계다. 이 부호·크기 관계는 별도의 미분 검산으로 유용하다. `evidence_s10/WOLFRAM_KERNEL_IDENTITIES.json`은 실제 Wolfram 호출의 두 항등식 차이 0, 미분 차이 0, 부등식 위반 영역 False, reflection 차이 0을 보존한다.

원 식을 마지막 식으로 바꾸면 같은 실수 함수지만 binary64의 계산 그래프는 바뀐다. 이번 첫 구현은 원 괄호와 나눗셈 순서를 유지한다. CAS의 0을 floating-point bit identity·오차 보증·가속 측정으로 사용하지 않는다.

## 2. 할당 제거가 보존해야 할 것

원 code는 각 ray의 세 항을 `Vec<[f64;3]>`에 쌓은 뒤 각 성분을 Neumaier 합산한다. 세 `(s,c)` accumulator를 두고 각 ray를 원래 순서로 넣으면 각 성분의 연산 의존 관계를 그대로 유지할 수 있다. 성분 간 연산을 교차 배치하는 것만으로 성분 내부의 덧셈 순서는 달라지지 않는다. cohort 합도 같은 구조다.

계약은 단순히 합산 알고리즘 이름을 유지하는 데 그치지 않는다. `w*n/r`는 `(w*n)/r`, `2*n*n`은 `(2*n)*n`, `r*r*r`는 `(r*r)*r`라는 원 연산을 보존한다. Neumaier의 분기·괄호·마지막 `s+c`도 같다. FMA/reciprocal approximation/fast-math와 parallel horizontal reduction은 포함하지 않는다. compiler와 target의 실제 결과는 별도 비교로 검증한다.

## 3. 준비 데이터와 overflow 범위

\(\mu^2\)와 \(1-\mu^2\)는 동일한 binary64 연산으로 birth 이후 한 번 준비할 수 있다. 이는 원 \(\mu,\alpha\)를 바꾸지 않는 파생 표현이다. 양의 birth weights, reflection, source frame과 old physical anisotropic stock의 digest는 그대로 둔다.

반대로 \(e^{2(b-b_0)}\)를 \(e^{2b}e^{-2b_0}\)로 분리하거나 amplitude의 \(e^{-4(x-u)}\)를 절대 시간 지수들의 곱으로 바꾸면, 원 차이는 작아도 개별 지수가 overflow할 수 있다. 이번 준비 데이터는 원 차이 기반 exponent를 유지한다. 큰 공통 \(x,u\) 또는 \(b,b_0\)에 대한 probe로 이 경계를 확인한다.

## 4. Cache의 정확성 조건

한 bank는 cohort 데이터와 donor/exposure/Λ를 가진 불변 함수 소유자다. 동일 bank에서 `x,h,b,y`의 네 `to_bits()`가 모두 같을 때만 성공한 evaluation을 재사용한다. 근접한 상태를 같은 것으로 취급하지 않는다. signed zero를 구분하고, NaN·비유한 값·비양의 h의 원 domain failure를 유지한다.

`J`를 저장하면 방향 벡터마다 원 순서로 `Jv`를 새로 계산한다. 저장 대상이 `Jv`라면 v도 key에 들어가야 하므로 이번 구현은 J 계수만 재사용한다. RHS와 JVP의 제한된 slot을 분리해 다른 stage의 RHS가 base Jacobian을 계속 밀어내지 않게 한다. 새 birth/segment는 새 immutable owner와 새 cache를 만든다. 같은 수치 상태를 가진 다른 bank에서도 과거 cache는 적용되지 않는다.

이는 동일 함수 평가의 memoization이다. 다른 state의 Jacobian 재사용·Krylov tolerance 변경·적분 차수 변경은 포함하지 않는다. cache hit/miss와 실제 full evaluation 수를 기록해 단순 wall time 외에 원인을 검증한다.

## 5. SIMD, 병렬화와 성능 해석

독립 ray들의 sqrt/div/mul을 SIMD lane에서 계산한 뒤 원 ray 순서로 scalar Neumaier에 넣는다. stable `std::arch`, 실제 필요한 CPU feature의 runtime guard, scalar fallback과 남은 tail을 명시한다. 최종 horizontal sum을 바꾸지 않는다. LLVM의 floating reduction 설명과 Rayon의 순서 미지정 reduction 계약은 [R2 원 source 목록](evidence_s10/r2/REUSE_SOURCES.json)에 있다.

Rayon의 bounded pool은 독립 history에만 쓴다. 한 history 내부의 births와 bank 교체는 순차 관계를 유지한다. 각 worker가 별도 solver/bank/cache를 소유하고 결과는 입력 index 순서로 모은다. 따라서 병렬 throughput과 단일 history latency를 구별할 수 있다.

커널이 baseline 시간의 비율 \(f\)를 차지하고 그 커널을 \(S_k\)배 가속하면, overhead가 없을 때 전체 가속의 모델은 \(S_{\rm total}=1/[(1-f)+f/S_k]\)다. 이는 조건부 비용 모형이며 현재 f의 측정값이 아니다. P24 projection, exact certificate, event 처리, serialization이 남으면 kernel 배수만큼 전체 history가 빨라지지는 않는다. 준비 비용과 저장량도 함께 보고한다.

## 6. 판정 경계

첫 실험은 baseline, stream, prepared, cache, simd, simd_cache를 같은 release profile과 입력에서 비교한다. 과학 gate는 원 S9와 동일하다. 원순서 보존으로 주장한 bit identity가 실패하면 그 후보는 실패로 보존하고, 사후 tolerance 완화로 채택하지 않는다. 물리적 source-age 구성과 기존 birth data를 변경해 성능을 얻는 변경도 허용하지 않는다.

P6, 넓은 continuum angular certificate, full native finite-bin reactive history와 실제 MD14 donor/Einstein closure는 계속 별도 미완료 과학 의무다.
