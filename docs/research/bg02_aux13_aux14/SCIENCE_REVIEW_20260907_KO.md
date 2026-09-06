# BG02 AUX13/AUX14: 관측 결과 수용과 Jacobi/frame 후속 유도

날짜: 2026-09-07. 주 대화에서 수행한 과학적 결과 검토 및 직접 유도다. 새로운 AUX 실행, native xAct 실행, production source 수정 또는 전체 solver 수용 기록이 아니다.

## 1. 이번에 실제로 확인한 실행 증거

반환 publication: `892d8f33951a8d6bd7f785502a864c0f3688f162`.
Evidence root: `artifacts/handback/bg02_aux13_aux14/20260906T144626Z/`.

- [주 대화 handoff](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/CHATGPT_HANDOFF_KO.md)
- [실제 final JSON](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/original/execution/aux-final-original.json)
- [실제 process receipt](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/original/execution/process.json)
- [stdout](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/logs/original.stdout.log)
- [stderr](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/logs/original.stderr.log)
- [실행 driver](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/original/driver/BASS_AUX13_AUX14_V1.wls)

Actual historical execution: 2026-09-06T14:03:16.742099Z to 14:03:20.362978Z; reported monotonic elapsed 3.608719873940572 s. Wolfram 15.0.0 Linux x86-64. The subprocess wrapper observed exit 1 without timeout; the driver independently emitted exit_code 1 and FAIL_AUXILIARY. These are a real previous local run, not a new execution in the reviewing main thread. The later Git-first publication reused this run rather than rerunning it.

주 대화에서 final JSON의 17개 required/observed IDs와 모든 행, stdout의 17개 TestEvaluated 사건 및 실제 Failure, process receipt, 비어 있는 stderr, 전체 driver와 실제 EinsteinProjection 함수를 직접 읽었다. GitHub가 반환한 Geometry tree의 3개 blob과 EinsteinProjection blob은 고정 control의 4개 blob과 일치한다. 원본 driver Git blob도 `8255b580026bd44ead4798c5e8d2be4367495261`로 반환 receipt와 일치한다. 실행 전후 source hash는 원본 final JSON에서 동일하다. 이는 원격 Git object/본문 및 실행 기록 대조이며, 주 대화에서 ZIP 전체나 모든 파일의 SHA-256을 새로 계산했다는 주장은 아니다.

Execution source: historical control `f2f05d37cdc6476154869067b1d41436af8248b6`, tree `8a1d6fbb0c039fe7bd0e29f79cb4e581e4b70688`의 네 파일 source subset. Publication commit은 execution source가 아니다. Native xAct가 아니다.

### Exact observed outcomes

| TestID | 실제 결과 |
|---|---|
| AUX13_CLASS_B_DIVERGENCE | Success, vector 0 |
| AUX13_STORAGE_ORDER_PARITY | Success, vector 0 |
| AUX13_ISOTROPIC_DIVERGENCE | Success, vector 0 |
| AUX13_EXCEPTIONAL_DETERMINANT | Success, scalar 0 |
| AUX13_FULL_MOMENTUM_WITNESS | Success, vector 0 |
| AUX13_SHEAR_NORM_SURVIVAL | Success, scalar 0 |
| AUX13_HAMILTONIAN_CONSUMER_SURVIVAL | Success, scalar 0 |
| AUX13_MOMENTUM_CONSUMER_SIGN | Failure, nonzero polynomial below |
| AUX14_SPATIAL_RICCI | Success, 3x3 zero matrix |
| AUX14_NONZERO_HAMILTONIAN | Success, scalar 0 |
| AUX14_ACTUAL_RATE_VALUES | Success, vector 0 |
| AUX14_JACOBI_VECTOR_DERIVATIVE | Success, vector 0 |
| AUX14_CURVATURE_DERIVATIVE | Success, scalar 0 |
| AUX14_SHEAR_NORM_DERIVATIVE | Success, scalar 0 |
| AUX14_DIRECT_HAMILTONIAN_DERIVATIVE | Success, vector 0 |
| AUX14_PROPAGATION_RATE_SEPARATION | Success, vector 0 |
| AUX14_FERMI_ALIGNMENT_COUNTEREXAMPLE | Success, scalar 0 |

16 Success / 1 Failure / 미평가 0. 17개 모두 actual_messages `{}`, expected_messages `HoldForm[{}]`. RuntimeFailures `{}`. JSON의 Outcome은 InputForm을 거친 문자열이므로 내부 따옴표를 포함한다. `HoldForm[0]` 등 원본 표현을 임의로 실패/미평가로 재분류하지 않는다. Raw failure type is SameTestFailure, not MessageFailure.

판정: **이 고정 source에 대한 제한된 AUX 실행 증거를 수용하며 HISTORICAL_CONFLICT_REPRODUCED로 해석한다. 원본 mathematical status는 FAIL_AUXILIARY로 유지한다.** Historical control은 GREEN이 아니다. Driver 수정은 관측된 필요가 없고 원본을 다시 실행할 필요도 없다.

## 2. 관측된 부호 결함의 수학적 위치

Signature (-,+,+,+), epsilon_123=+1, positive K_ab=H_geom h_ab+sigma_ab, q_a=-h_a{}^c T_cd n^d, kappa_G=8 pi G/c^4를 유지한다. 점은 tau=ct에 대한 정상방향 미분이며 H_geom, sigma, a^B, n^B는 길이의 역수다.

구조상수와 Koszul 연결에서 얻는 homogeneous STF divergence를 C_i=D^j sigma_ij라고 하자. a-aligned full-transverse frame에서

C1 = -3 A Sigma11 + N23(Sigma11+2 Sigma22) + (N33-N22)Sigma23.

실제 raw residual은

```
-6*av$11104*s11$11104 + 2*n23$11104*s11$11104
+4*n23$11104*s22$11104 -2*n22$11104*s23$11104
+2*n33$11104*s23$11104
```

이다. Module suffix를 설명용 기호로만 치환하면 정확히 2 C1다. 원본 로그/JSON의 suffix를 수정하지 않는다.

E_ab=G_ab+Lambda g_ab-kappa_G T_ab와 M_a=-h_a{}^c n^d E_cd에서, positive K의 Codazzi 관계를 쓰면

M_a=-D^b K_ab+D_a K-kappa_G q_a.

Homogeneity에서는 D_a K=0이므로 M_i=-C_i-kappa_G q_i다. 실행된 consumer의 actual source는 `divKv-gradKv-kgv qv`이고, driver가 검사하는 값은 `MomentumProjection[...] + C1 + kg*q1`이므로 실제 residual 2 C1와 직접 연결된다. 연결 생성·배열 adapter·C1 발산 검사들은 별도로 Success였다. 따라서 이번 비영점은 연결 계산 전체의 실패가 아니라 historical MomentumProjection의 기하학적 부호와 정합적이다. 물질항을 함께 뒤집을 근거는 없다.

일반 component 식의 필요한 형태는 `-divKv+gradKv-kgv qv`다. 다만 원래 17개 검사는 GradientK=0만 넣으므로 general nonzero-gradient slot은 이번 실행으로 검증되지 않았다. 이전 owner amendment가 이미 준비되어 있으므로 여기서 새로운 production sign patch를 복제하지 않는다.

## 3. 실제로 확인된 AUX14와 검증 범위

Driver의 고정 fixture는

```
a = (1,0,0)/ell
N = [[0,0,0],[0,2,3],[0,3,0]]/ell
Sigma = [[0,0,1],[0,0,0],[1,0,0]]/ell
H_geom = 1/ell
rho=p=q=pi=Lambda=0, ell>0
```

이다. Source 함수 호출에서 아래 기대식과의 실제 residual이 0이었다.

```
R3ij = [[-22,0,0],[0,-6,8],[0,8,2]]/ell^2
R3 = -26/ell^2
sigma_ij sigma^ij = 2/ell^2
Hres = -11/ell^2
(F_trace,F_ADM,F_Ray) = (1/6,17/3,-5/3)/ell^2
(dHres_trace,dHres_ADM,dHres_Ray) = (33,66,22)/ell^3
```

여기서 source에 쓰인 `sigma2`는 sigma_ij sigma^ij이며 그 절반이 아니다. 세 rate는 off-shell에서 서로 다르며, 이 fixture에서는 dHres=(-3,-6,-2)*H_geom*Hres를 각각 만족한다. 하나의 공통 off-shell propagation oracle로 세 rate를 대체할 수 없다.

이는 단일 비영점 homogeneous fixture의 실제 symbolic component validation이다. aDot/nDot 및 scalar-curvature derivative는 driver가 별도로 조립하므로 BASS production Jacobi RHS 전체의 실행 증거가 아니다. Hamiltonian norm-survival은 driver가 공급한 norm에 대한 scalar consumer의 반응이며 production state ingestion/serialization/norm reduction의 end-to-end 검증은 아니다. Full abstract 4-projection bridge, native17, all-family evolution, finite-time constraint stability, arbitrary rank, finite electron tilt, observable/statistics/provider/RF04는 수용하지 않는다.

## 4. 이어서 직접 유도한 결과: frame-covariant Jacobi 보존

이 절은 이번 주 대화의 **직접 유도**이며 새 CAS/수치 실행 결과가 아니다. 기존 fixture 검사의 해석을 보강한다. 아래 식을 새로운 AUX15나 production implementation으로 등록하지 않는다.

a=a^B, N=n^B=N^T, Sigma=sigma=Sigma^T, tr(Sigma)=0로 쓰자. R(tau) in SO(3)가 공간적으로 일정한 성분 frame 변환이고 W=dot(R) R^T라고 정의한다. W^T=-W다. 이 정의는 frame rotation의 성분 작용을 고정하며 normal vorticity나 local observer boost를 뜻하지 않는다.

Geodesic-normal Fermi 식과 그 시간 의존 proper-frame 변환은

```
aDot = -H a - Sigma a + W a
NDot = -H N + Sigma N + N Sigma + [W,N]
```

이다. Fermi frame은 W=0이다. j=N a라 놓고 곱을 미분하면

```
jDot = NDot a + N aDot = (-2 H I + Sigma + W) j.
```

그러므로 정확한 연속식에서 j=0의 초기자료는 j=0에 남는다. 이 보존은 Hamiltonian 또는 matter field equation을 추가로 사용하지 않는다.

Class B의 rank(N)=2, a!=0, Na=0, Delta!=0 영역에서

```
r = a^T a
Delta = ((tr N)^2 - tr(N^2))/2
h = r/Delta
```

를 정의한다. Delta는 a-aligned frame의 det(N_perp)와 같지만 위 식은 alignment를 요구하지 않는다. Rank 2에서 `adj(N)=Delta*a*a^T/r`이며

```
rDot = -2 H r - 2 a^T Sigma a
DeltaDot = -2 H Delta + 2 tr(N) tr(Sigma N) - 2 tr(Sigma N^2)
         = -2 (H + a^T Sigma a/r) Delta
hDot = (rDot*Delta-r*DeltaDot)/Delta^2 = 0.
```

두 번째 줄은 adj(N)=N^2-(tr N)N+Delta I 및 tr(Sigma)=0로부터 따른다. Rotation commutator는 trace에서 사라진다. 따라서 h=-1/9는 frame-covariant Jacobi 흐름에서 보존된다. 이 정리는 a=0 또는 Delta=0에서 h를 정의하지 않으며, 수치 timestep의 보존을 자동 보장하지도 않는다. Dimensionful 식은 H로 나누지 않는다.

### 기존 fixture에서의 정렬 강제 오류: 비영점 반례

기존 AUX14 fixture를 같은 Fermi 식에 넣으면 직접 계산으로

```
aDot_F = (-1,0,-1)/ell^2
NDot_F = [[0,3,0],[3,-2,-3],[0,-3,0]]/ell^2
jDot_F = (0,0,0)
rDot = -2/ell^3
DeltaDot = 18/ell^3
hDot = 0
```

를 얻는다. 여기서 aDot_F의 세 번째 성분만 0으로 clamp하고 NDot_F를 그대로 쓰면

```
aDot_clamped = (-1,0,0)/ell^2
jDot_clamped = (0,3,0)/ell^3 != 0.
```

가 된다. 이는 a-alignment를 수동 삭제로 유지하는 조작이 단순 frame 선택이 아니라 Jacobi 제약을 깨는 변경일 수 있음을 보이는 직접 유도된 반례다. 실제 production에 이 clamp 버그가 존재한다고 관측한 것은 아니다.

같은 순간의 올바른 frame 선택 예는

```
W = [[0,0,-1],[0,0,0],[1,0,0]]/ell
```

이다. 그러면

```
aDot_aligned = aDot_F + W a = (-1,0,0)/ell^2
NDot_aligned = NDot_F + [W,N] = -N/ell
jDot_aligned = 0.
```

Sigma 및 다른 tensor/PSTF 성분에도 같은 frame 작용을 해야 한다. Sigma에는 `[W,Sigma]`가 추가되며, ray/polarization 계수도 동일한 frame으로 변환해야 한다. N만 diagonal/aligned하게 만들고 shear나 polarization를 삭제하는 규칙은 도출되지 않는다. W와 기존 Omega_triad의 부호 adapter를 정의 없이 동일시하지 않는다.

## 5. 원전 대조와 두 가지 감사

SciSpace로 van Elst–Uggla의 원전을 찾고 arXiv `gr-qc/9603026` 본문을 확인했다. 인쇄 p.34의 Eqs. (4.229)–(4.231)는 PDF screenshot으로 확인했다. 이는 normalized A,N의 Jacobi evolution과 A_beta N^{alpha beta}=0를 표시한다. Section 3 Eqs. (3.1)–(3.2)는 parsed text로 확인했다: partial_0=3 e_0/Theta, A=a/Theta, N=n/Theta, Sigma_paper=sigma/Theta. Fermi rotation 0과 Theta=3H로 위 dimensionful aDot/NDot를 얻는다. h 보존 및 clamp 반례는 본 노트의 직접 행렬 유도이며 원전이 이 fixture를 검사했다는 주장이 아니다.

Primary reference: H. van Elst and C. Uggla, General Relativistic 1+3 Orthonormal Frame Approach Revisited, arXiv:gr-qc/9603026; published DOI 10.1088/0264-9381/14/9/021. https://arxiv.org/pdf/gr-qc/9603026

PHYS-MATH 검토: normal signature/K/q/Codazzi 부호, sigma2의 factor 2, ell 차원, on/off-shell 구분, Na=0/rank 2/Delta!=0 조건, time-dependent frame 변환을 점검했다. Mathematical residual 차원은 L^-2, Jacobi derivative는 L^-3다.

PHYS-MATH-CODE 검토: 실제 source consumer와 driver 입력/예상값/ActualOutput을 대조했다. 추가 새 source 오류는 관측하지 않았다. 확인된 제한은 GradientK=0, test-supplied norm, driver-supplied Jacobi rates, 한 AUX14 fixture라는 점이다. 이는 같은 작성자의 순차 검토이며 independent reviewer PASS가 아니다.

주 대화의 Container 및 Python은 ClientError로 계산/파일 실행 결과를 제공하지 못했다. 따라서 새 CAS 계산·plot·local SHA 재계산은 없다. Exact symbolic 결과를 임의의 expected-number plot으로 바꾸지 않았다. Numerical plotting과 time-integration validation은 수행하지 않았다.

## 6. 결론과 다음 최소 과학적 작업

원래 historical AUX13/AUX14 관측 작업은 **반환 evidence 검토까지 완료**했다. 다시 runtime 접근성 문서 작성이나 같은 원본 재실행으로 돌아가지 않는다. 관측된 16/1은 잘못된 source를 GREEN으로 만드는 결과가 아니라, 소비 함수 부호를 구체적으로 분리한 실제 재현이다.

다음은 기존에 준비된 repaired candidate의 source를 읽어 동일 AUX suite와 비교하는 일이다. 후보로 기록된 commit `e404f914c0817b4c2ab3a0ff4632a8457e026fde`, parent `3c36458a8dbc9fe4092a24d5a09203327877f8d8`, tree `e2fc64860631e781082cceb3bef5b24fb8a06084`는 이번 주 대화 GitHub commit GET에서 404였다. 이는 현재 경로로 그 commit을 읽지 못했다는 뜻이지 사용자 로컬에서 소실됐다는 뜻이 아니다. 후보의 bytes를 추정하거나 historical source에 새 patch를 만들어 대체하지 않는다.

별도 native17/capture 수리·예산과 독립된 read-only candidate AUX 비교만 다음 대상으로 삼는다. Local Codex는 필요한 candidate source/dependency와 기존 driver를 읽고 보존된 historical 결과를 재사용한다. 상세 실행·Git-first 반환 범위는 `docs/codex_handoff/bg02_aux13_aux14/CANDIDATE_AUX_COMPARISON_KO.md`에 둔다. Candidate 비교는 아직 실행되지 않았다.
