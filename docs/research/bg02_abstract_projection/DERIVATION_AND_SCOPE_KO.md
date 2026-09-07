# BG-02: SC 이후 추상 곡률 블록에서 네 Einstein projection으로

날짜: 2026-09-07. 현재 단계: `BG02_ABSTRACT_CURVATURE_BLOCK_CONTRACTION_V1`.
이번 산출물은 직접 유도와 미실행 xTensor 코드다. 기존 SC/AUX 결과를 재사용하며, 새로운 native PASS나 일반 BG-02 bridge 완료를 선언하지 않는다.

## 1. 선행 증거와 실제 미완료 경로

수용된 SC source: `b074e206fd6fe640b6eecb703befcb9bd72467cf`.
SC publication: `8799219233186ff30b57adedbbdf2027e1c6cf60`, tree `6cb0dda1026a4f20bfa5cd59c9e3ba37347893eb`.
SC19/19, shape 회귀 5/5와 현지 실제 figure 기록은 재사용한다. 이를 새 실행으로 세지 않는다.

이번 GitHub 재조회에서 PR131은 OPEN/DRAFT/UNMERGED, head `f2f05d37cdc6476154869067b1d41436af8248b6`다. 이는 이후 evidence branch들의 완료 결과를 반영한 최신 scientific source라는 뜻이 아니다. PR 최근 댓글은 SC 반환 `5566129212`였다.

실제로 읽은 코드의 경계:
- `Geometry/Abstract1Plus3.wl`: abstract 등록과 projector/kinematic 검사. 함수가 스스로 `ABSTRACT_1PLUS3_REGISTRATION_ONLY_NO_COMPONENT_OR_CURVATURE_PROOF`로 범위를 제한한다. GitHub content 전체/후속 관련 본문으로 읽은 범위에 기반하며 다른 미조회 branch에 대한 부재 단정은 아니다.
- `research/diagnostics/bg02_b0_20260905/native/calibrate.wls`: 특정 exponential Bianchi-V의 xCoba 성분 calibration. 새 코드로 복제하거나 기존 suite를 재실행하지 않는다.
- candidate snapshot의 `EinsteinProjection.wl`: `EinsteinResidualTensor`는 여전히 component-formula association이고 native tensor API가 아니라고 명시한다.

따라서 선택한 한 단계는 generic tensor curvature block의 contraction을 실제 abstract-index 코드로 연결하는 것이다. 새로운 scalar fixture 모음, RHS, integration, chart module을 더 만드는 단계가 아니다.

## 2. 정의, 가정, 원전 표기 adapter

서명 (-,+,+,+), n.n=-1, h_ab=g_ab+n_a n_b, epsilon123=+1.
정상 합동은 hypersurface-orthogonal이며

```
K_ab = h_a^c h_b^d nabla_c n_d = Hgeom h_ab + sigma_ab
nabla_a n_b = K_ab - n_a A_b
A_a = n^c nabla_c n_a
T_ab = rho n_a n_b + n_a q_b + n_b q_a + p h_ab + pi_ab
E_ab = R_ab - g_ab R/2 + Lambda g_ab - kappaG T_ab
kappaG = 8 pi G/c^4, Hgeom = H_time/c.
```

A는 normal acceleration이며 Bianchi aB가 아니다. 공간 tensor는 n에 직교한다. K는 대칭, sigma와 pi는 spatial symmetric trace-free다. hypersurface normal에서 D_[a A_b]=0인 국소 영역을 사용한다. 시간/공간 미분을 수치적으로 근사하지 않는다. 이 단계의 generic spatial derivative jets는 곡률 항등식 검사에만 쓰이며 비균질 우주론의 forward evolution을 새로 구현하지 않는다.

곡률 convention을 X_abcd=g(e_a,R(e_c,e_d)e_b), R(X,Y)=nabla_X nabla_Y-nabla_Y nabla_X-nabla_[X,Y]로 쓴다. Ricci_ab=g^cd X_acbd다. 기존 BASS의 별도 B_abcd=<R(e_a,e_b)e_c,e_d>와는 X=-B (같은 배열 슬롯)이며 Ricci를 무조건 부호 반전하지 않는다. AP00은 actual xTensor의 metric contraction convention을 독립적으로 확인한다.

LL_ab := (L_n K)_ab, DK_abc := D_a K_bc, Z_ab := spatial Ricci_ab라고 하자. 모든 낮은 인덱스 Lie tensor는 spatial이다. D_a A_b는 DA_ab로 표기한다.

차원: K,Hgeom,sigma,A는 L^-1; LL,DK,DA,Z,X,E,Lambda는 L^-2; rho,p,q,pi는 에너지 밀도; kappaG*matter는 L^-2. c=1을 가정하지 않는다. boundary/initial evolution problem을 풀지 않는 국소 항등식이다.

## 3. 기하학적 입력: 세 곡률 블록

공간 X,Y에 대해 nabla_X Y=D_X Y+K(X,Y)n, nabla_X n=K(X), nabla_n n=A를 사용한다. 이 분해를 R의 정의에 대입하고 tangential/normal part를 분리하면 다음 블록이 나온다. 첫 두 식은 Gauss와 Codazzi이고, 세 번째는 normal Ricci relation이다.

```
U_abcd = X3_abcd + K_ac K_bd - K_ad K_bc
B_bcd  = n^a h_b^e h_c^f h_d^g X_aefg = D_d K_bc - D_c K_bd
Q_ab   = n^c n^d h_a^e h_b^f X_cedf
       = -LL_ab + K_ac K^c_b + D_a A_b + A_a A_b.
```

예를 들어 mixed 식은 metric compatibility로 g(n,R(X,Y)Z)=-g(Z,R(X,Y)n)를 쓰고, R(X,Y)n의 spatial part를 (D_X K)(Y)-(D_Y K)(X)로 전개하여 부호를 고정한다. Q에서는 projected covariant dotK와 LieK 사이의 2 K.K 항을 유지한다.

공간 차원은 3이므로 Weyl tensor가 없고 intrinsic Riemann은

```
X3_abcd = h_ac Z_bd - h_ad Z_bc - h_bc Z_ad + h_bd Z_ac
          - (tr Z)/2 (h_ac h_bd-h_ad h_bc)
```

로 표현할 수 있다. 이는 abstract curvature algebra의 표현이지 새로운 Bianchi Ricci 계산기가 아니다. 실제 nB/aB로 Z를 계산하는 기존 geometry owner를 대체하지 않는다.

## 4. 하나의 곡률 tensor에서 contraction

블록으로부터 전체 X를 독립적으로 조립한다:

```
X_abcd = U_abcd
 -n_a B_bcd+n_b B_acd-n_c B_dab+n_d B_cab
 +n_a n_c Q_bd-n_a n_d Q_bc-n_b n_c Q_ad+n_b n_d Q_ac.
```

원래 블록을 재projection하여 회복되는지, 두 반대칭·pair symmetry·첫 Bianchi 항등식이 성립하는지를 먼저 검사한다. 이후 Ricci=g^cd X_acbd와 R=g^ab Ricci_ab를 계산하며, 네 projection 기대식을 Ricci의 입력으로 사용하지 않는다.

k=trK, k2=tr(K.K), L=trLL, z=trZ, a2=A.A, d=trDA라고 쓰면 직접 contraction은

```
R_nn = -L+k2+d+a2
R_an (spatial a) = D^b K_ab-D_a k
R_ab (spatial) = Z_ab+LL_ab+k K_ab-2(K.K)_ab-DA_ab-A_a A_b
R = z+k^2-3 k2+2 L-2(d+a2).
```

이로부터 네 projection은

```
Hres = (z+k^2-k2)/2 - Lambda-kappaG rho
M_a = -D^b K_ab+D_a k-kappaG q_a
P = h^ab E_ab/3
  = -z/6-2 L/3-k^2/6+5 k2/6+2(d+a2)/3+Lambda-kappaG p
S_ab = E_<ab>
  = Z_<ab>+LL_<ab>+k K_<ab>-2(K.K)_<ab>
    -DA_<ab>-(A A)_<ab>-kappaG pi_ab.
```

재구성 E_ab=Hres n_a n_b+n_a M_b+n_b M_a+P h_ab+S_ab를 실제 computed projections로 확인한다. 여기서 M의 정의가 -h E n이라는 점이 mixed 재구성의 부호를 결정한다. 이 분해는 1+3+1+5=10개의 symmetric rank-two 성분을 보존한다.

## 5. 이번에 명시한 Lie trace 문제

L_n h^ab = n^a A^b+n^b A^a-2K^ab이고 K_ab는 spatial이므로,

```
L_n k = (L_n h^ab)K_ab+h^ab L_n K_ab
      = -2 k2+L
L = L_n k+2 k2 = 3 L_n Hgeom+6 Hgeom^2+2 sigma2.
```

따라서 L을 단순히 3 L_n Hgeom으로 치환하면 안 된다. 이 올바른 관계를 위 P에 넣으면

```
P = -R3/6-2 L_n Hgeom-3 Hgeom^2-sigma2/2
    +2(D.A+A2)/3+Lambda-kappaG p
```

가 되어 기존 source와 연결된다. 잘못된 trace adapter를 같은 projected tensor에 대입한 차이는

```
P_wrong-P_correct = 4 k2/3
                 = 4 Hgeom^2 + (4/3) sigma2.
```

sigma=0, Hgeom=1/ell이면 4/ell^2라는 비영점 반례가 된다. 실제 native AP12는 computed P에 두 adapter를 각각 적용하여 이 차이를 평가한다. 이 노트의 값은 직접 유도된 기대값이며 새 실행에서 관측된 결과가 아니다.

## 6. 실제 consumer의 두 제곱항 의미를 구분

K.K의 PSTF는 2 Hgeom sigma+(sigma.sigma)_PSTF다. 따라서

```
(L_n K)_PSTF = (L_n sigma)_PSTF+2 Hgeom sigma
S_ab = Z_<ab>+(L_n sigma)_<ab>+Hgeom sigma_ab
       -2(sigma.sigma)_<ab>-DA_<ab>-(A A)_<ab>-kappaG pi_ab.
```

또 projected covariant derivative와 Lie derivative는

```
(L_n sigma)_PSTF = dotSigma_PSTF+2Hgeom sigma+2(sigma.sigma)_PSTF
```

이므로 source의 두 shear-rate 표현이 다른 derivative kind라는 사실과 일치한다.

실제 `SpatialPSTFProjection`의 이름이 `SigmaQuadratic`인 입력 슬롯은 해당 registry 식에 맞추면 `(K.K)_PSTF`를 받아야 한다. 반면 `ShearLieRate`에서 같은 문자열 슬롯은 `(sigma.sigma)_PSTF`를 뜻한다. 이번 코드의 consumer adapter는 앞의 값을 명시적으로 공급한다. 이것은 슬롯 의미의 모호성을 노출하는 것이지, 검증된 SC/AUX에서 새로운 source bug를 관측했다는 주장은 아니다. source를 임의로 rename하거나 기존 payload를 바꾸지 않았다.

## 7. 코드·검사와 현재 검증 수준

새 파일은 `research/diagnostics/bg02_abstract_projection_20260907/` 아래의 AbstractProjection.wl, projection_tests.wl, run_projection.wls다. AP00--AP12는 13개의 별도 exact test ID다. old AUX, SC, native17 또는 capture6와 count/예산을 공유하지 않는다.

코드는 xTensor DefTensor/MakeRule/ContractMetric/ToCanonical을 통해 abstract indices를 실제 contraction하며, LieDToCovD로 inverse-projector Lie identity도 전개한다. component arrays, coordinate metric, Table로 나열한 family 결과는 사용하지 않는다. 원래 Gauss/Codazzi/Ricci 블록은 **전제**이고, Riemann[CD]의 정의에서 그 블록을 도출하는 모든 native differential step이 구현됐다고 쓰지 않는다.

현재 분류:
- 네 projection 및 Lie trace 변환: 직접 유도.
- 새 native xTensor 코드와 tests: 작성·정적 검토, **PREPARED_UNEXECUTED**.
- 같은 본문을 두 번 쓴 scalar self-subtraction이 아니라 독립 curvature assembly -> contraction -> BASS consumer 비교 경로.
- 전체 general native BG-02 bridge: 아직 미완료. 이 조건부 contraction과 curvature-definition-to-blocks 단계는 별도다.

주 대화의 실제 Container/Python 호출은 ClientError로 출력 전에 실패했다. 새 AP 평가 0, 새 native PASS 0, 새 그림 0이다. 이미 수용한 SC 그림은 재사용하며, abstract identity를 확인한 척 하기 위해 기대값 곡선을 새로 그리지 않았다. 수학/코드 검토는 같은 작성자의 순차 검토이며 제3자 독립 감사로 표시하지 않는다.

## 8. 원전과 문서 검토의 범위

SciSpace에서 Chan Park, *A Covariant Approach to 1+3 Formalism*, arXiv:1810.06293을 찾고 arXiv parsed full text의 Eqs. (15),(17),(20),(114)--(122)를 읽었다. 저자의 dot은 L_u에 대한 Lie derivative이므로 프로젝트의 projected-covariant dot과 동일시하지 않는다. 저자의 u->n, gamma->h, Theta_ab->K_ab, Theta->3Hgeom, P_a->q_a, S_ab->p h_ab+pi_ab로 대응시키고 G,c,Lambda를 명시적으로 복원한다. 이번 screenshot 세 요청은 cache miss로 실패했으므로 원문 이미지에서 수식을 대조했다고 주장하지 않는다.

https://arxiv.org/abs/1810.06293
https://arxiv.org/pdf/1810.06293
https://xact.es/Documentation/HTML/HTMLLinks/xTensorRefGuide.nb_5.html
https://xact.es/Documentation/HTML/HTMLLinks/xTensor/DummyIn.nb.html

프로젝트 source:
https://github.com/cosmosapjw-quantum/bass/blob/8799219233186ff30b57adedbbdf2027e1c6cf60/artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/source/wolfram/BASS/Kernel/Background/EinsteinProjection.wl
https://github.com/cosmosapjw-quantum/bass/blob/f2f05d37cdc6476154869067b1d41436af8248b6/wolfram/BASS/Kernel/Geometry/Abstract1Plus3.wl

현재 projection의 의미/계수 authority는 기존 candidate owner다. 원격 historical registry의 이전 momentum 문자열을 새 authority로 소비하지 않는다. Atlassian은 DAG/범위 동기화 자료로만 사용했다.

## 9. 다음 최소 행동

다음은 공급한 세 AP 코드 파일의 실제 local xTensor 실행·범위 내 수리·Git-first 반환이다. SC/AUX를 다시 돌리지 않는다. 이를 통과해도 `PASS_CONDITIONAL_ABSTRACT_CONTRACTION_ONLY`만 허용한다. 일반 native bridge를 닫으려면 이후 actual curvature definition에서 블록 관계까지의 native 연결을 별도로 검증해야 한다. 기존 capture/native 실행의 소모 예산을 재생성하지 않는다.
