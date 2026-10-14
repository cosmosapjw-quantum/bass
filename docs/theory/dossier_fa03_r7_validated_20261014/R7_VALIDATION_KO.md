# FA03-R7: 유한 각도 검출기의 시간·반올림 구간과 실제 수치 다항식의 오차

2026-10-14, Asia/Seoul. 선택 단계 FA03-R7 및 명시된 REI 분석 공급 작업. 기준은 PR145 commit `20e6152b158c151cb014e21768857b25cd427f96`와 실제 원본 ZIP SHA256 `c040514105fa856b05a8792a628e441a2ad73c991cc253b94b7646425d8bb0e8`이다. R6를 다시 수행하지 않고, R6가 명시적으로 남긴 **정확한 Taylor 계수와 실제 계산된 계수 사이의 오차**를 한 고정 detector에서 닫는다. R8–R10의 실행 또는 독립 심사를 주장하지 않는다.

## 1. 검증 대상과 동일성

Signature는 (-,+,+,+). 원 Kasner 지수 (2/3,2/3,-1/3), 무차원 시간 x=t/t_o in[1/2,1], zero incoming coherency, normal-rest source/absorber, projected-e2 observer analyzer를 그대로 둔다. 물리 intensity의 복원 계수 `c t_o E_*^2 j_*(e_+-e_-)`도 불변이다. c=1로 바꾸지 않았으며 새 무차원 알고리즘에서 h는 proper time이 아니라 x의 step이다.

고정 observer는 **정확한 십진수** chi=.008, psi=.010, cap radius delta=.020rad다. Detector energy e=E_w/E_* in[.98,1.02]는 연속 band로 정확히 적분한다. Opacity는 `[1+epsilon(ek-1)] K0`, k=E_rest/E_w이고 |epsilon|<=.1이다. K0=diag(.4,.4,.8), half absorption H=Sigma^T K0 Sigma/2, rotation Omega=.3 ehat_1 J2, G=H+Omega다. Epsilon으로 rotation이나 source를 바꾸지 않는다. Source P3는 e2/e3 block [[.7,.1+.05i],[.1-.05i,.3]]이며 PSD, trace1이다. 정확한 plateau 다항식 branch를 사용한다.

검증하는 관측량은 **GL3×등간격12phi의 36-ray 유한 검출기**다. 연속 cap integral 자체를 인증하지 않는다. GL t=-sqrt(3/5),0,+sqrt(3/5), phi=j*pi/6, j=0..11에서

    ell1=1-(t+1)sin(delta/2)^2,
    (ell2,ell3)=sqrt(1-ell1^2)(cos(phi),sin(phi)),
    m=R3(psi)ell,
    L=cosh(chi)+sinh(chi)m1,
    n=((sinh(chi)+cosh(chi)m1),m2,m3)/L.

각 ring의 ray당 가중치는 5/216,1/27,5/216로 양수이며 정확히 합1이다. 이 대수적 GL node와 sin/cos/exp의 평가를 interval로 감싼다. 저장된 binary64 node를 수학적 GL node와 동일하다고 가정하지 않는다.

## 2. 기존 여섯 행렬계와 새 계산 표현

m_j=<e^j>는 원 finite band의 정확한 유리수 moment이고, {H,X}=HX+XH^T, L_G X=GX+XG^T로 쓴다.

    S_j'=(m_(j+3)+.1*m_(j+4)*k)P-L_G S_j, j=0,1,2,
    V_j'=-L_G V_j-{H,k S_(j+1)-S_j}, j=0,1,
    W_0'=-L_G W_0-2{H,k V_1-V_0}.                   (R7.1)

모든 초기값은0. W0는 epsilon에 대한 실제 이차 미분이며 Taylor coefficient W0/2와 다르다. Epsilon=0에서의 정확한 미분 closure이며, finite-epsilon spectrum의 여섯 moment exact closure가 아니다. 이번에는 observer derivative를 추가 인증하지 않고 S/V/W의 값을 검증한다.

각 Hermitian 행렬을 (F11,F22,ReF12,ImF12) 네 실수로 나타내면 y in R^24의 선형 비자율 초기값 문제

    y'=A(x)y+b(x)                                      (R7.2)

가 된다. G=[[g11,g12],[g21,g22]]의 loss를 직접 쓰면

    (-GF-FG^T)11=-2g11*F11-2g12*ReF12,
    (-GF-FG^T)22=-2g22*F22-2g21*ReF12,
    Re(...12)=-g21*F11-g12*F22-(g11+g22)*ReF12,
    Im(...12)=-(g11+g22)*ImF12.                        (R7.3)

이 새24성분 표현은 parent의 행렬 RHS와 별도로 구성했다. 3시간×4ray, 임의 비가환 Hermitian 입력에서 최대 entry 차이는2.6645352591003757e-15였다. 이는 finite-point 구현 비교이며 뒤의 interval tail 증명을 대신하지 않는다.

## 3. 복소 시간 영역을 명시한 Cauchy 상계

실수 step 시작 x_j in[1/2,1]의 복소 disk |z-x_j|<=R=1/8을 사용한다. |z|<=9/8, Re z>=3/8이다. 같은 실제 ray family에서 |n3|<.021이고

    v^2=1+(z^2-1)n3^2,
    |v^2-1|<=((9/8)^2+1)(.021)^2<.001.              (R7.4)

따라서 v의 원 branch는 이 disk에서0을 만나지 않는다. z^(-2/3)도 Re z>0에서 분석적 branch로 이어진다. ehat=(n1,n2,z n3)/v의 Hermitian norm은

    ||ehat||_2^2 <= [1+((9/8)^2-1)(.021)^2]/.999 <1.001^2.

정규화된 real kk=(-n2,n1,0)/sqrt(n1^2+n2^2)는 ehat와 직교한다. Screen B=[kk,ehat×kk]의 두 column도 Hermitian orthogonal이며 ||B||2<=1.001이다. Observer map C는 real orthogonal 상수이고 Sigma=B C이므로 같은 상계가 유지된다. 이때

    ||P||1 <=1.001^2,
    ||H||2 <=.4*(1.001)^2 <.402,
    ||Omega||2 <=.3*1.001 <.301,
    ||G||2 <.703,
    |k| <=exp(.02)*(3/8)^(-2/3)*1.001 <2.             (R7.5)

P의 복소시간 연장은 Sigma^T P3 Sigma다. 복소시간에서 positivity를 가정하지 않고, 양쪽 spectral norm과 고정 P3의 trace norm을 사용했다. Source cutoff 자체의 복소 해석성을 가정하지 않으며 실제 물리구간에서 쓰는 plateau polynomial만 연장한다.

여섯 행렬 공간에 max block trace norm을 쓰면 W행까지 포함하는 operator bound와 forcing bound는

    ||A|| <=2*.703+4*.402*(2+1)=6.23<7,
    ||b|| <=(1.02)^6*(1+2/10)*(1.001)^2
           =52894493918669403/39062500000000000 <2.  (R7.6)

각4성분의 복소 절댓값이 y_max 이하라면 trace norm<=sqrt(12)y_max<5y_max다. Step의 incoming interval 전체를 포함하는 y_max를 선택한다. Disk의 각 반경을 따라 선형 integral equation에 norm을 취하면

    sup_disk ||y|| <= exp(7R)(5*y_max+2R)
                    <3(5*y_max+1/4)=M_j.            (R7.7)

행렬을 시간마다 commute한다고 하지 않는다. Local existence와 analyticity는 nonsingular coefficient를 가진 유한차원 선형 ODE에서 얻는다. 이전 셀의 error를0으로 재설정하는 first-cell 가정도 없다.

## 4. 실제 interval Taylor recurrence와 tail

A=sum A_n s^n, b=sum b_n s^n, y=sum y_n s^n, s=x-x_j로 놓으면

    y_(n+1)=[b_n+sum_(k=0)^n A_k y_(n-k)]/(n+1).     (R7.8)

Coefficient 계산은 사칙연산·exp/log/sqrt와 exact series product를 사용한다. 일반 a(s)^r는 a*y'=r*y*a'에서 얻는 recurrence로 계산하므로 float 미분을 쓰지 않는다. 실제 실행은 p=20, h=1/64, 총32steps이고 h/R=1/8이다. 각 성분에서 Cauchy bound는

    |tail_j| <= M_j (h/R)^(p+1)/(1-h/R).              (R7.9)

검사한 elementary interval 연산으로 생성한20차 polynomial을 Horner로 평가한 뒤 ±tail_j interval을 더한다. 다음 step은 **이 전체 outgoing interval**을 incoming으로 사용한다. 이 절차는 time truncation, elementary arithmetic rounding, 들어오는 enclosure의 폭을 함께 포함한다. Interval coefficient를 계산한 뒤 가운데값만 다음step으로 넘기는 절차가 아니다.

실제 runtime은 mpmath1.3.0 iv65decimaldigits다. 정확한 반환 endpoint는 dyadic Fraction으로 추출해 JSON에 분자·분모를 저장한다. mpmath는 interval 지원을 experimental로 명시한다. 본 결과의 신뢰 경계는 사용한 기본 arithmetic/exp/log/sqrt/sin/cos 구현과 검토한 recurrence이며, 라이브러리 전체의 formal verification이나 외부 독립 과학심사까지 주장하지 않는다. 공식 문서: https://mpmath.org/doc/1.3.0/contexts.html . Cauchy/validated Taylor의 방법론 배경은 Eble–Neher2003 DOI10.1145/838250.838252, Neher–Jackson–Nedialkov2007 DOI10.1137/050638448이며 이 특정 상수는 직접 유도했다.

## 5. 실제36ray 결과와 원 수치 출력의 오차

36ray별 endpoint를 모두 저장했고, exact positive weights로 Fraction 합산했다. 최종24real component 중 최대 반경은

    max radius =3.303729497659651e-17 <3.31e-17.       (R7.10)

`evidence/CERTIFICATE.json`의 lo/hi 분자·분모가 정식 결과다. 아래 midpoint display 자체를 exact center 또는 outward endpoint라고 하지 않는다.

|state|I|Q|U|V|
|---|---:|---:|---:|---:|
|S0|.49584821384013933|.22868586857262346|.06572664654452998|-.04854092023442185|
|V0|-.009092488135838081|-.0017671505583921343|-.0015479987237513799|.0010431176075043531|
|W0|.00036359396936452664|-.00004640150342894543|.00008523581748314068|-.000044269686063740844|

Stokes convention은 I=F11+F22,Q=F11-F22,U=2ReF12,V=-2ImF12로 원본을 보존한다. V0의 I upper endpoint도 엄밀히0보다 작다. 이는 정확히 지정한 finite detector/model의 slope 부호이며 physical continuous-cap calibration 결과가 아니다.

Parent R5 `fa03_jet.npz`의 고정64-step RK4 baseline coefficients를 **다시 실행하지 않고** 읽어 interval과 뺐다. Hermitian difference의 trace norm은

    ||D||1 <=sqrt[2d11^2+2d22^2+4du^2+4dv^2]         (R7.11)

로 감싼다. 구간 component의 최대 절댓값을 넣고 sqrt를 outward 계산했다. S0,V0,W0의 upper는 각각6.247219347916289e-12,1.2222572532170155e-11,7.617717084837892e-12다. 이는 새 exact-decimal GL target과 옛 binary64 candidate 사이의 **총 차이 상계**이며 RK4 time error만 따로 분리한 수치가 아니다. 옛 parameter/node rounding도 포함한다.

## 6. 정확한 계수 정리에서 실제 수치 다항식으로

R6가 증명한 opacity-only remainder coefficient는 C=926402349807/1953125000000000이다. Fixed real observer에서

    ||J(eps)-J0-eps*V0-eps^2*W0/2||1<=C|eps|^3.     (R7.12)

이를 동일 positive finite quadrature에 적용할 수 있다. 이제 근사계수 j0,v,w에 대해 정식으로

    error <= E0+|eps|EV+eps^2*EW/2+C|eps|^3.         (R7.13)

|eps|<=.1 전체에서 부모의 저장 RK4 coefficient 다항식은4.7432551066637056e-7 이하, 새 interval의 **exact-rational midpoint** coefficient 다항식은4.743180031668196e-7 이하다. 새 midpoint coefficient contribution만은6.563559837008499e-17 이하이고, 양쪽 모두 짧은 outward bound **4.75e-7 미만**으로 닫힌다. Exact-fraction midpoint를 부동소수점으로 변환한 사용자는 그 추가 rounding을 따로 더해야 한다.

새로 닫힌 것은 수치계수·time·elementary rounding을 포함한 finite angular detector의 (R7.13)이다. Continuous cap quadrature error, observer derivative의 numerical enclosure, unknown empirical provider error와 실제 물질 feedback은 null 또는 기존 상태 그대로다. Joint observer/epsilon perturbation에는 원 R5 joint bound의 별도 계약을 사용한다.

## 7. 실행 증거와 종료

기본 interval helper7tests, PL reference helper15tests, 실제 parent RHS/native-slice bridge11conditions, 36ray 저장 결과 조립8conditions가 통과했다. Actual remote Wolfram15.0.0+xTensor1.3.0은 quadratic residual cubic항, 그 error forcing부호, adjoint pairing, paired source cancellation의4잔차를0으로 반환했다. Cloud15.0.1은 복소영역7부등식과 block/source 상계2조건, tail합 및 ln(a) 곡률식을 반환했다. Undefined-symbol 경고를 보존했다. 같은 작성자와 여러 arithmetic/표현 경로이며 external independent review가 아니다.

처음36ray를 한꺼번에 돌린 command와 한5ray block이 도구 실행한도에서 끊겼다. 전자는 unsaved ray결과를 완료로 세지 않았고, 이후 각ray를 즉시 저장했다. 두 번째는 저장된15..18을 보존하고 누락19만 재개했다. Model, p20/32step 최종설정 또는 scientific threshold를 낮추지 않았다. Failure logs와 작은 초기 p14 pilot은 별도로 남겼다. Parent chemistry/atomic/native/HPC 및 불변 PNS/AP suite는 실행하지 않았다.

판정은 **R7_COMPLETE_SCOPED_VALIDATED_FINITE_DETECTOR**. R8은 이 결과를 보존한 상태로 ready이며 미실행이다. 새1–10루프를 자동 시작하지 않는다.
