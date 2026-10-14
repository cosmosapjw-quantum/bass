# FA03-R7: 고정 36-ray detector의 수치 접선 계수 전파 인증

2026-10-14 Asia/Seoul. 이번 선택은 FA03-R7이다. 부모 R6의 source·detector·R5 여섯 moment 구조를 유지하고 남아 있던 **수치 Taylor 계수 오차** 하나를 실제로 감싼다. R8–R10 및 원 I–VII 전체 재편집은 실행하지 않았다. 원 21개 이론 단위와 D9.1, SOURCE_CLOCKS·ABUNDANCE_MODEL은 불변이다.

## 1. 명확한 정확해와 참조의 정의

부모 commit은 `20e6152b158c151cb014e21768857b25cd427f96`이며 원 R5는 `3348fc73f59022c5ab2ec00474d36bbcac54f5ec`다. b453 FA02 두 매개변수 family를 사용한다. 같은 날짜 72569 세 매개변수 family는 사용하지 않는다. Signature(-,+,+,+); Kasner p=(2/3,2/3,-1/3), x=t/t_o in[1/2,1], detector energy e=E_w/E_* in[49/50,51/50], zero incoming coherency다. Material은 normal-comoving이고 observer passive boost를 physical tilt로 바꾸지 않는다.

고정 observer는 chi=1/125, psi=1/100, cap radius delta=1/50이다. 이번 인증의 detector는 **정확한 GL3 × 12 등간격 azimuth의 유한 양의 quadrature**다. GL nodes t=(-sqrt(3/5),0,sqrt(3/5))에 대해

    cos r_i = 1-(1+t_i)sin²(1/100), phi_j=pi*j/6.               (R7.1)

각 azimuth당 weights는 (5/216,1/27,5/216)이며 36개 합은 정확히1이다. 이 정의의 irrational nodes를 interval로 계산한다. 원 binary64 cap nodes와 exact-real nodes는 동일 bytes가 아니다. 아래 residual은 exact-real coefficients를 사용하므로 이 차이도 참조 오차에 포함한다. 연속 cap 적분과 이 유한 detector 사이의 오차는 **null**이다.

원래 길이당 opacity와 source normalization은 유지한다. x-방정식은 무차원이다. 원 detector 물리 단위로 돌아갈 때는 c t_o E_*² j_*(e_+-e_-)를 곱한다. c를1로 설정하지 않는다. 새로운 hbar나 k_B가 이 수동 전달 방정식에 나타나지 않는다고 natural units를 채택한 것은 아니다.

각 ray에서 S0,S1,S2,V0,V1,W0는 부모의 exact energy moment 계다. V는 epsilon 1차 derivative, W는 2차 derivative이며 W/2가 Taylor coefficient다. 연속 energy 적분을 quadrature로 대체하지 않고 exact rational m_j를 쓴다. 유한 epsilon의 전체 spectrum을 six-moment system으로 잘랐다는 주장이 아니다.


구체적으로 K3=diag(.4,.4,.8), P3의 yz block=[[.7,.1+.05i],[.1-.05i,.3]]이고 나머지 source entries는0이다. P=Sigma^T P3 Sigma, H=Sigma^T K3 Sigma/2, Omega=.3 ehat_1 J2, J2=[[0,-1],[1,0]]다. L_G X=GX+XG^T, A_H X=HX+XH^T라 쓰면 실제 계는

    S_j'=(m_(j+3)+.1*m_(j+4)*k)P-L_G S_j, j=0,1,2,
    V_j'=-L_G V_j-A_H(k S_(j+1)-S_j), j=0,1,
    W_0'=-L_G W_0-2 A_H(k V_1-V_0).

모든 초기값은0이며 m_j=(e_+^(j+1)-e_-^(j+1))/[(j+1)(e_+-e_-)]다. k는 국소 rest energy와 observer energy의 비이고 photon wavevector와 다른 스칼라다. 모든 source·absorption 계수는 이 x-clock 식의 무차원화된 값이다.

## 2. 한 번 생성한 고정 cubic reference

원 여섯 행렬 RHS를 RK4, 64steps로 한 번 실행하여 65개 node 및 그 node의 binary64 RHS slope를 저장했다. Source나 IC를 바꾸지 않았다. 기존 R5/R6 전체 suite와 observer jet campaign은 반복하지 않았다.

`reference64.npz` SHA256은 `bf1141893d81825daa2acbfcfc74325fb6c8a124e3869003ef4f1f7b81339f42`다. 저장된 실수 Stokes 값과 slope를 **정확한 dyadic 데이터**로 간주한다. Slope가 true solution derivative라고 가정하지 않는다. 셀 z=(x-x_i)/h in[0,1], h=1/128에서

    Yhat(z)=Y_i+z(a+z(b+zc)),
    a=h d_i, b=3(Y_(i+1)-Y_i)-h(2d_i+d_(i+1)),
    c=2(Y_i-Y_(i+1))+h(d_i+d_(i+1)).                          (R7.2)

인접 셀은 같은 node·slope로 연결된다. Initial reference는 정확히0이다. Cubic의 계수 조립은 interval arithmetic으로 이루어져 반올림을 포함한다.

## 3. Hermitian trace norm과 셀 전체 residual

Hermitian 2×2 matrix를

    F=1/2 [[I+Q,U-iV],[U+iV,I-Q]]

로 쓰면 eigenvalues는 (I±sqrt(Q²+U²+V²))/2이므로

    ||F||_1=max(|I|,sqrt(Q²+U²+V²)).                          (R7.3)

이 식은 PSD 여부와 무관하게 error/residual Hermitian matrix에도 성립한다. 각 component interval의 absolute upper endpoint와 outward sqrt로 trace norm을 위에서 감싼다. 별도 Wolfram algebra가 Stokes loss/rotation 부호 및 이 eigenvalue 식을 확인했다.

Residual은 normalized coordinate의

    r(z)=dYhat/dz-h f(x_i+hz,Yhat(z)).                         (R7.4)

이다. midpoint interval Taylor jet로 c0,c1,c2를 구하고 **base z in[0,1]의 별도 interval jet**로 r^(3)/3!의 모든 값의 enclosure를 얻는다. 이를 M3로 묶으면

    r(z)=c0+c1(z-1/2)+c2(z-1/2)²+R3(z),
    ||R3(z)||_1 <= M3 |z-1/2|³,
    integral_0^1||r||_1 dz <= b0+b1/4+b2/12+M3/32.            (R7.5)

b_k는 midpoint coefficient norm upper다. 1,1/4,1/12,1/32는 정확한 적분가중치다. 64×36=2304개 셀 전부에 이 계산을 실행했으며 각 셀의 여섯 bound와 그 합을 저장했다. 이후 endpoint는 exact Fraction으로 추출하여 유리수로만 조립했다. Stokes 각 component의 전체 derivative enclosure를 쓰므로 표본 사이를 추정한 것이 아니다.

반례 r(z)=z(z-1/2)(z-1)는 z=0,1/2,1에서 모두0이지만 r(1/4)=3/64, integral|r|=1/32다. 따라서 세 점 residual0을 셀 전체 residual0으로 바꾸는 검증기는 이번 기준을 만족하지 못한다.

## 4. 비가환 전달의 수축성과 누적 오차

실수 ray/screen에서 H=(Sigma^T K3 Sigma)/2는 PSD이고 ||H||2<=.4이다. G=H+Omega, Omega^T=-Omega이므로 d||U v||²/dx=-2(Uv)^T H(Uv)<=0. 순서화된 전파자 U는 spectral norm에서 수축하고, T(X)=UXU^T는 trace norm에서 수축한다. 서로 다른 x의 G가 commute한다는 전제는 없다. 이 결론은 xAct의 추상 quadratic-form 항등식과 별도로 양성 조건으로 증명했다.

각 residual norm의 전체 셀 합을 rho_Sj,rho_Vj,rho_W라 하자. Normalized residual을 적분했으므로 rho 앞에 h를 또 곱하지 않는다. 모든 ray에서 k<=17/10, ||{H,X}||1<=4||X||1/5이며 전체 길이는1/2이다. Duhamel 식과 삼각부등식으로 전구간 sup error가

    dSj <= rho_Sj,
    dVj <= rho_Vj+(2/5)[(17/10)dS_(j+1)+dSj], j=0,1,
    dW  <= rho_W +(4/5)[(17/10)dV1+dV0].                      (R7.6)

를 만족한다. W식의2를 유지한다. 이전 셀에서 들어오는 오차를0으로 reset하지 않고 **전체 누적 rho**를 쓰므로 error memory가 보존된다. Initial reference0이 아니면 initial error도 같은 전파식에 추가해야 한다. HE51에서의 gas/photon carried-memory 구조를 방법상 참고했지만 warm source의 계수·box·반경을 수입하지 않았다.

양의 detector weights를 곱해 합하면 exact finite-detector coefficient error bounds가 된다. 수치 upper의 짧은 outward 표시:

|state|uniform forward radius|
|---|---:|
|S0|<6.144e-9|
|S1|<6.147e-9|
|S2|<6.151e-9|
|V0|<2.847e-8|
|V1|<2.848e-8|
|W0|<6.471e-8|

정확한 유리수 endpoints는 `evidence/CERTIFICATE.json`에 있다. |epsilon|<=.1일 때

    d_polynomial <= dS0+|epsilon|dV0+epsilon² dW0/2
                 <9.313e-9.                                 (R7.7)

이는 계산 전에 고정한1e-7보다 작다. Threshold를 넓히지 않았다. R6의 exact opacity-only remainder와 합치면 동일한 고정 유한 detector의 exact solution에 대해

    ||J_36(epsilon)-[Shat0+epsilon Vhat0+epsilon² What0/2]||1
       <= d_polynomial + .000474318003101184 |epsilon|³
       <4.84e-7, for |epsilon|<=.1.                          (R7.8)

R6는 exact Taylor coefficients를 전제로 했고 R7이 그 numerical coefficient error를 추가했다. 이것이 이번 계산의 새 닫힘이다. Joint chi/psi/epsilon response, continuum angular integral, 실제 원자 opacity calibration에는 이 마지막 수치를 전용하지 않는다.

## 5. 구현의 신뢰 경계와 실제 확인

실제 mpmath1.3.0 iv 50decimaldigits의 +,-,*,/,sqrt,exp,log,sin,cos,pi와 degree3 Taylor recurrence를 사용했다. 일반 arbitrary-precision point arithmetic을 outward interval이라고 표시하지 않았다. 라이브러리 전체 형식검증은 하지 않았으며 공식 docs의 experimental interval support 경고를 유지한다. 사용한 primitive/rational powers와 interval Taylor의 coefficient는 독립 mp80 derivative point checks로 검사했다. 이것은 library 전체의 proof가 아니라 지정 primitive를 신뢰하는 재현 가능한 계산이다.

새94개 조건은 exact residual/cascade 재조립,36ray identity·weights, 별도 Stokes norm/eigensolve, selected exact-source/parent comparisons, domain rejection, missed-residual/memory controls를 포함한다. 원식과 별도 표현의 point 최대차는6.661338147750939e-16이다. 이 point 비교로 전체 time certificate를 대신하지 않았고 interval result가 본래 근거다. Unit tests22개(별도 milestone21+Jet1), actual native milestone18conditions도 별도 파일에 있다. Counts는 독립 심사 수가 아니다.

Actual local Wolfram15.0.0/xTensor1.3.0의4tensor residual은0이고 raw submitted code와 출력·exit0의 bytes를 회수했다. Cloud Wolfram15.0.1은 Stokes4zeros, 적분가중치, residual 반례, eigenvalues를 반환했다. Same-author 검증이며 외부 독립 reviewer/native subagents는 NOT_RUN이다.

## 6. 문헌과 다음 단계

Jawecki,Auzinger,Koch, arXiv:1809.03369는 nonexpansive matrix exponential의 defect/error integral 구조를 제공한다. 그 Krylov-specific theorem을 여기로 그대로 인용하지 않고 위6-state time-dependent Duhamel bound를 직접 유도했다. SciSpace는 Estep1995,Neumaier1994 등 primary method discovery에 사용했고, 실제 구현 근거는 위 식과 코드다. 공식 mpmath contexts 문서 https://mpmath.org/doc/1.3.0/contexts.html 를 읽었다. 이 URL의 rendered heading은1.2.0으로 나와 runtime version1.3.0과 구분했다.

R7의 선택된 검증 목표는 scoped complete다. 다음 FA03-R8은 이 수치 계수와 기존 exact remainder를 범위에 맞게 판정·통합하는 단계이며 아직 실행하지 않았다. Continuous cap quadrature를 필요로 하는 새로운 claim은 별도 changed obligation으로 남는다.
