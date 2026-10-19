# S7 실제 결합 실행과 R2 exact moment 재분석

작성일: 2026-10-19. 범위는 non-tilted axisymmetric Bianchi I의 **양의 manufactured donor + collisionless radiation + Λ**이다. 새 출생 cohort의 angular rule을 고정한 뒤 실제 전단과 Hubble 변수를 함께 진화시켰다. 실제 MD14 emissivity의 에너지 공급 성분이나 native spectral owner의 전체 Einstein 결합은 이 실행에 포함하지 않았다.

**최종 판정은 FAIL이다.** 최초 36개 main history 시도에서 28개를 완주하고 8개에서 양의 support feasibility 실패를 얻었다. 완주한 history의 보존·양성·반사 대칭·기존 stock 불변성은 통과했다. R2에서 모든 1,968개 birth rule의 원래 digest를 대조하고 실제 binary64 입력의 Legendre moment를 유리수로 계산한 결과, 640개 constrained birth 중 하나의 \(P_4\) residual이 고정 gate \(3\times10^{-15}\)를 넘었다. 해당 실패를 tolerance 변경이나 음의 weight로 우회하지 않았다.

## 1. 실행과 재분석의 서로 다른 identity

| 항목 | 실제 identity와 결과 |
|---|---|
| 최초 source/prereg 게시 | commit 2865f60bf0a247eaab4997c222ad82ae22a4c8fa, tree acfd07e6064859ad2ba849c6da004696e6a98d23 |
| 최초 prereg SHA-256 | 70e0a1d87b87c34aae15a6d00831d2e2bb69c22045b815fb775b108d0f628a1b |
| 최초 실제 실행 | 2026-10-19 10:06:48–10:07:09 UTC, 36 main + 7 independent benchmark histories |
| 최초 판정 | FAIL: 26 history gate 통과, 2 float moment observer 실패, 8 feasibility 실패 |
| R2 분석 source/prereg 게시 | commit c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a, tree 4ff555e870c250982a1d6f765f3f73eb17cb2158 |
| R2 prereg SHA-256 | c24ee865b4457398cb5d67dddbddfc2ef796d98665fe55416838ea5da4e9ebc4 |
| R2 실제 재분석 | 2026-10-19 10:25:03–10:25:15 UTC, 기존 28개 history의 frozen birth rule 재구성 |
| R2 판정 | FAIL: 27 history gate 통과, 1 exact moment 실패, 기존 8 feasibility 실패 유지 |
| R2 결과 SHA-256 | 762c2079e84bccf72deb2feabaecf3a00e6d8c5bfc1899ab261c8e104c8d195c |

R2는 ODE, benchmark, Duhamel 적분을 다시 실행하지 않았다. 최초 실행의 41개 JSON 파일 전체는 원래 SHA-256과 일치한다. 모든 ray 재구성은 분석용이며 기존 trajectory를 변경하지 않았다. Original run01 FAIL 기록과 R2 FAIL 기록을 각각 보존한다.

실행과 검증의 원본은 다음 파일에 있다.

- [최초 실행 receipt](evidence_s7_coupled/run01/RETURN_S7_COUPLED.json)
- [최초 process receipt](evidence_s7_coupled/RUN01_PROCESS.json)
- [R2 분석 receipt](evidence_s7_coupled/revalidate_r2/RETURN_S7_COUPLED_REANALYSIS.json)
- [R2 process receipt](evidence_s7_coupled/REANALYSIS_R2_PROCESS.json)
- [원본 41개 파일 manifest](evidence_s7_coupled/REVALIDATION_ORIGIN.json)
- [정확한 실패 witness와 분류](evidence_s7_coupled/EXACT_MOMENT_FAILURES_R2.json)

## 2. 실제 진화시킨 닫힌 모델

Convention은 metric signature \((-,+,+,+)\),
\(a_\perp=a e^{-b}\), \(a_\parallel=a e^{2b}\),
\(s=\dot b\), \(\Sigma=\sqrt3|s|/H\)를 유지한다.
\(k=8\pi G/(3c^2)\), 임의 기준 \(H_*>0\)에 대해

\[
x=\ln(a/a_{\rm ref}),\quad h=H/H_*,\quad y=s/H_*,
\quad E_d=kU_d/H_*^2,\quad E_\gamma=kU_\gamma/H_*^2,
\quad \Pi=k\Delta P/H_*^2,\quad L=\Lambda c^2/(3H_*^2)
\]

를 사용했다. 저장된 y와 Pi는 각각 \(s/H_*\), \(k\Delta P/H_*^2\)이며 차원이 있는 s나 압력으로 직접 해석하지 않는다.

\[
b'=\frac yh,\qquad
y'=-3y+\frac{\Pi}{h},\qquad
h'=\frac{-h^2-2y^2-E_d/2-E_\gamma+L}{h}.
\]

Hubble 변수 h는 일반 Raychaudhuri 식으로 독립적으로 진화한다. 초기화에서 한 번 constraint를 맞춘 뒤 h를 constraint의 제곱근으로 다시 대입하지 않았다.

\[
C=h^2-y^2-E_d-E_\gamma-L,\qquad C'=-2C
\]

가 event 사이에서 성립한다. Photon에만 에너지를 넣고 donor 손실을 생략하는 negative control은 Hamiltonian 검사를 실패시킨다. 유도와 독립 검토는 [S7_COUPLED_THEORY_KO.md](S7_COUPLED_THEORY_KO.md)에 있다.

기존 stock은 source-frame GL128 isotropic energy 0.16과, 양의 물리적 anisotropic 분포
\(\alpha_i\propto w_i[1+0.4P_2(\mu_i)]\)의 energy 0.04이다. 이 두 stock은 projection 대상이 아니다. 모든 old/born cohort는 출생 좌표 u, 당시 b, energy, ray 방향, weight, role을 포함한 digest로 동결했다.

신규 cohort만 source-frame의 prior, P2, P24 중 지정된 rule을 출생 때 구성한다. 출생 뒤에는

\[
E_k=w_k e^{-4(x-u_k)} F_k(b-b_k),\qquad
\Pi_k=w_k e^{-4(x-u_k)} G_k(b-b_k)
\]

를 사용하며 방향과 weight를 수정하지 않는다. \(F'_k=-2G_k\)이므로 각 cohort의
\(E_k'+4E_k+2(y/h)\Pi_k=0\)을 별도 complex-step 미분으로 검사했다.

Donor는 초기 0.7, Λ는 0.1, \(y_0=0.08\), \(b_0=0.3\), \(\lambda=0.7\)을 기본값으로 사용했다. 출생 구간은 \(0<x<0.8\), 관측 끝은 1.2이다. K개 midpoint event에서

\[
u_j=(j+\tfrac12)\Delta x,\quad
E_d^- = E_{d0} e^{-3u_j-\lambda j\Delta x},\quad
w_j=E_d^-\,[1-e^{-\lambda\Delta x}],
\]

\[
E_d^+=E_d^-e^{-\lambda\Delta x},\qquad
E_\gamma^+=E_\gamma^-+w_j
\]

를 적용했다. h, b, y는 event에서 연속이고 총 전달 energy는 보존된다. 작은 양수의 계산에는 expm1을 사용하며 weight를 clamp하지 않는다. \(\lambda=0\)에서는 zero-weight cohort를 생성하지 않는다.

## 3. 독립 축과 실행 비용

Main 36개 입력은 다음과 같이 사전 등록했다.

- Source-frame GL128을 고정한 birth refinement: K=16, 32, 64, 128, 256.
- K=64의 angular 비교: \(b_0=0.3,0.7,0.9\), n=8, 16, 32, prior/P2/P24.
- 각 b의 GL128 reference와, \(b_0=0.3\)의 source-frame GL64/256 reference refinement.

이 축은 K를 바꿔 얻는 출생 시각 오차, n을 바꿔 얻는 angular refinement 효과, 같은 n에서 새 moment 제약의 효과를 분리한다. \(b_0=0.7,0.9\)는 고정 coordinate-grid가 source-frame으로 변환될 때의 support stress이다. 물리적인 누적 shear displacement \(d=0.9\)를 진화시킨 실험으로 부르지 않는다.

별도 benchmark 7개는 radiation-only의 작은 anisotropy 3개와 isotropic continuous-donor 수렴 4개다. 이미 완료된 S3/S6 캠페인은 다시 실행하지 않았다.

| 실행 | 실제 solver/분석 시간 | 최대 RSS | 결과 디렉터리 파일 합계 |
|---|---:|---:|---:|
| 최초 main+benchmark | 20.1458 s | 91,788 KiB | 6,199,564 bytes, 41 files |
| R2 분석만 | 10.7153 s | 106,580 KiB | 9,389,071 bytes, 29 files |

실행기는 worker 1과 BLAS/OMP/MKL thread 1을 지정하며, RAM 16 GiB, disk 4 GiB, job 1800초 상한을 유지한다. 실제 NCP 작업은 사용하지 않았다. Main solver는 DOP853, rtol \(5\times10^{-13}\), atol \(5\times10^{-15}\), max_step 0.08이다.

기존 source stage의 핵심 테스트 16개가 통과했고, R2에서는 ODE를 다시 풀지 않는 observer/reuse guard 4개를 추가 실행하여 통과했다. 네 검사는 실제 false-failure witness의 exact 통과, 진짜 threshold 초과의 거절, 바뀐 cohort digest 거절, 바뀐 raw byte 거절이다. 서로 다른 source identity와 실행 로그를 합쳐 단일 반복 실행으로 부르지 않는다.

## 4. 보존 검사의 실제 수치

다음은 최초 실행에서 얻고 R2에서 raw identity를 확인해 재사용한 결과다.

| 검사 | 실제 최대 residual | 사전 gate |
|---|---:|---:|
| 독립적으로 진화한 Hamiltonian relative residual | \(6.2780232\times10^{-14}\) | \(10^{-11}\) |
| 개별 cohort energy identity relative residual | \(3.4734871\times10^{-15}\) | \(10^{-11}\) |
| 출생 event total energy relative jump | \(3.2020143\times10^{-16}\) | \(10^{-13}\) |
| 두 결합 history의 Duhamel identity absolute residual | \(7.1991024\times10^{-17}\) | \(2\times10^{-11}\) |
| 같은 K에서 source-frame GL128/256의 저장 관측량 최대 차이 | \(4.5449755\times10^{-16}\) | \(2\times10^{-11}\) |

완주한 28개 history에서 positive background, positive stock, 정확한 reflection parity, old/born stock 불변성 및 donor endpoint 검사가 통과했다. R2는 56개 old stock과 1,968개 birth rule의 전체 cohort digest를 다시 맞췄다. 포함된 birth ray의 최소 weight는 \(5.6394509\times10^{-5}>0\)다.

GL128/256 일치 수치는 이 시험 구간의 두 reference 사이 차이다. 연속 angular 적분의 전역 error bound, native finite-bin photon/energy 보존, 긴 source-age와 큰 finite-d 정확도의 승인이 아니다.

## 5. Float observer 실패와 실제 exact 실패를 구별한 결과

최초 observer는 binary64로 Legendre 다항식을 계산하고 NumPy dot을 적용했다. Projector와 observer 사이의 곱셈 순서 및 합산 차이 때문에 \(3\times10^{-15}\) 부근에서 verdict가 달라졌다. R2는 **같은 저장 binary64 μ, α**에 대한

\[
M_\ell=\sum_i \alpha_i P_\ell(\mu_i)
\]

를 Fraction으로 정확히 계산한다. Gate는 정확한 유리수 \(3/10^{15}\)다. 정규화는 별도 기존 조건을 유지하며, normalized moment도 진단용으로 남긴다. P2 모드에서는 M4에 gate를 적용하지 않는다.

| case, birth index | 최초 float moment | exact moment | R2 판정 |
|---|---:|---:|---|
| b03_n8_P2, 43: M2 | \(+3.0078026\times10^{-15}\) | \(+2.9895564\times10^{-15}\) | float false failure 해소 |
| b03_n32_P24, 27: M4 | \(-3.0045411\times10^{-15}\) | \(-2.9847515\times10^{-15}\) | float false failure 해소 |
| b03_n32_P24, 62: M4 | \(-3.0166841\times10^{-15}\) | \(-2.9763594\times10^{-15}\) | float false failure 해소 |
| b03_n32_P24, 50: M4 | \(-2.9854591\times10^{-15}\) | **\(-3.0005965\times10^{-15}\)** | **새로 드러난 exact 실패** |

세 개의 최초 경고만 확인하면 마지막 실패를 발견하지 못한다. R2는 모든 birth를 확인했기 때문에 float observer가 통과시킨 진짜 초과도 찾아냈다. M2 제약 640개는 모두 통과했으며, P24의 M4 제약 256개 중 255개가 통과하고 1개가 실패했다.

실패한 birth는
\(u=0.6312500000000001\),
\(b_u=0.3310282262303169\),
digest 84b55ba5aa06b5ac408994e0a94b51fcfba72fc5f33bb66ea32a60951ac22954이다.
정확한 초과량은 \(5.964896306508056\times10^{-19}\)다.
양의 weight, 반사 대칭, 정규화는 유지되므로 이는 support의 기하학적 infeasibility가 아니라 **EXACT_BINARY64_BIRTH_MOMENT_EXCESS**로 분류한다.

R2에서 새 weight나 더 엄격한 projector stopping rule을 도입하지 않았다. 그 변경은 별도 source identity와 사전 등록, 새로운 실행의 의무를 만든다. 현재 tiny residual을 근거로 gate를 확대하거나 전체 campaign을 PASS로 부르지 않는다.

## 6. Angular refinement와 P4 제약의 서로 다른 효과

다음은 \(b_0=0.3\), K=64를 고정하고 source-frame GL128 history와 비교한 저장 시각 전체의 \(\max|\delta y|\), 즉 \(\max|\delta s|/H_*\)다. 원래 trajectory를 그대로 재사용했다.

| n | prior | P2 | P24 |
|---:|---:|---:|---:|
| 8 | \(3.8168832\times10^{-4}\) | \(1.3776628\times10^{-5}\) | \(9.9626324\times10^{-7}\) |
| 16 | \(1.8180868\times10^{-6}\) | \(1.2918672\times10^{-7}\) | \(1.5308470\times10^{-8}\) |
| 32 | \(1.5153773\times10^{-11}\) | \(1.9433040\times10^{-12}\) | \(4.4984589\times10^{-13}\) |

같은 n에서 P4 제약을 추가한 경우와 n 자체를 늘린 경우 모두 이 입력에서는 오차를 줄였다. 위의 작은 \(\delta y\)가 moment admission 실패를 취소하지 않는다. 특히 n=32 P24 trajectory는 비교 데이터로 보존하지만 R2 exact moment gate는 실패다. 이 표를 모든 b나 긴 history의 정확도 보장으로 일반화하지 않는다.

양의 support를 찾지 못한 입력은 다음과 같다. 실패 당시의 b, μ 전체, P2 범위, P24 feasibility witness를 각 원본 failure JSON에 저장했다.

| 초기 b | n | mode | 구체적 실패 |
|---:|---:|---|---|
| 0.7 | 8 | P2 | INFEASIBLE_ANGULAR_SUPPORT |
| 0.7 | 8 | P24 | INFEASIBLE_P24_MEAN |
| 0.7 | 16 | P24 | INFEASIBLE_P24_UPPER |
| 0.9 | 8 | P2 | INFEASIBLE_ANGULAR_SUPPORT |
| 0.9 | 8 | P24 | INFEASIBLE_P24_MEAN |
| 0.9 | 16 | P2 | INFEASIBLE_ANGULAR_SUPPORT |
| 0.9 | 16 | P24 | INFEASIBLE_P24_MEAN |
| 0.9 | 32 | P24 | INFEASIBLE_P24_UPPER |

같은 source-frame GL128에서 K를 늘린 endpoint 차이의 비는 h, y, radiation energy, Pi, Sigma에서 약 4에 접근한다. 예를 들어 y의 K=16/32/64 triple, 32/64/128 triple, 64/128/256 triple 비는 4.0001165, 4.0000290, 4.0000073이다. 이 main coupled birth refinement는 사전 등록상 diagnostic이며 실행 뒤 새 통과 gate를 만들지 않았다.

## 7. 독립 benchmark와 선형 응답의 한계

### 7.1 실제 결합 radiation-only 선형 극한

Donor, Λ, 신규 출생이 없는 radiation-only 모델에서
\(q=y/h\), \(\mathcal A=\Pi/E_\gamma\)를 두면 등방 상태 주위의 독립 1차식은

\[
\frac{d}{dx}\begin{pmatrix}q\\\mathcal A\end{pmatrix}
=\begin{pmatrix}-1&1\\-8/5&0\end{pmatrix}
\begin{pmatrix}q\\\mathcal A\end{pmatrix}.
\]

고유값은 \(-1/2\pm3i\sqrt{15}/10\)이다. 이 matrix exponential과 exact nonlinear kernel의 결합 history를 비교했다. 초기 \(q_0=\mathcal A_0=\epsilon\), 양의 physical distribution \(1+5\epsilon P_2\)를 사용했다.

| ε | max absolute nonlinear–linear error | error/ε² |
|---:|---:|---:|
| 0.01 | \(3.8870332\times10^{-5}\) | 0.3887033 |
| 0.005 | \(9.7400442\times10^{-6}\) | 0.3896018 |
| 0.0025 | \(2.4378494\times10^{-6}\) | 0.3900559 |

오차비 3.9907757, 3.9953428은 사전 gate [3.5,4.5] 안에 있다. 이는 작은 anisotropy에서 실제 결합식을 구별하는 독립 물리 benchmark다. Source-age projection의 birth geometry 미분까지 포함한 full tangent 검증으로 확대하지 않는다. 문헌 mapping과 독립 유도는 이론 문서 §5.2에 있다.

### 7.2 Isotropic continuous-donor 기준식

등방 모델의 연속 donor source contribution은

\[
E_\gamma(x)=e^{-4x}\left[E_{\gamma0}
+\lambda E_{d0}\frac{\exp[(1-\lambda)\min(x,0.8)]-1}{1-\lambda}\right].
\]

Discrete midpoint source contribution과 연속 source contribution의 정확한 비는

\[
\frac{1-\lambda}{\lambda}
\frac{\sinh(\lambda\Delta x/2)}
{\sinh((1-\lambda)\Delta x/2)}
=1+\frac{2\lambda-1}{24}\Delta x^2+O(\Delta x^4).
\]

\(\lambda=1/2\)의 우연한 exact endpoint 상쇄를 피하여 0.7을 사용했다. K=16,32,64,128에서 실제 radiation energy의 연속 기준식 대비 오차는 각각
\(1.5192256\times10^{-7}\),
\(3.7980390\times10^{-8}\),
\(9.4950818\times10^{-9}\),
\(2.3737695\times10^{-9}\)이다. 오차비 4.0000262, 4.0000066, 4.0000016은 사전 gate를 통과했다. 별도 discrete exact energy와 independently evolved h의 최대 relative 차이는 \(1.1398371\times10^{-15}\)다.

### 7.3 측정한 forcing과 완전한 tangent의 구별

두 nonlinear coupled history의 차이는 정확히

\[
\delta y(x)=\int_0^x e^{-3(x-v)}
\left[\frac{\Pi_a(v)}{h_a(v)}-\frac{\Pi_b(v)}{h_b(v)}\right]\,dv
\]

를 만족한다. 여기서는 같은 초기 y를 사용했다. 이 Duhamel 일치는 적분·저장의 수치 일관성 검사다.
측정한 \(\delta\Pi\)를 reference h로 나눈 항만 적분하는 근사는 h 응답을 생략한다. \(b_0=0.3,n=8\) P2에서 실제 endpoint \(\delta y=-9.4835753\times10^{-6}\), 해당 근사와의 차이는 \(1.1834101\times10^{-10}\)이고 first-H 보정 뒤에는 \(2.8395474\times10^{-12}\)다.

그러나 \(\delta\Pi\) 자체를 두 결합 trajectory에서 측정했으므로 이것은 prescribed-background source forcing의 독립 예측이 아니다. \(\delta b(x)\), birth \(\delta b(u)\), 변하는 source-frame μ, projection α의 미분과 기억항을 포함한 full tangent solver는 남은 의무다.

## 8. 남은 의무와 실행 가능한 handoff

1. Exact M4 residual 실패를 유지한 채, 더 엄격한 **내부** projector 정지 조건 또는 exact-aware projection 방법을 별도 source/prereg로 설계·시험한다. Admission gate \(3/10^{15}\), 양성, parity는 변경하지 않는다. 현재 R2는 observer만 수정했고 이 알고리즘 개선은 아직 실행하지 않았다.
2. 양의 해가 없는 8개 support에는 angular support refinement가 필요하다. Moment constraint 추가와 refinement 효과를 계속 따로 측정한다.
3. Actual owner emissivity를 결합하려면 에너지 공급 성분을 포함한 closure, source/frame/spectral provenance, finite-bin photon·energy 수송 검산이 추가로 필요하다. 고정 spectral owner는 rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177이다.
4. Coupled full tangent의 birth geometry/weight derivative와 긴 source-age·큰 finite-d angular 정확도 의무를 완료하지 않았다. Native lane의 별도 finite-bin/큰 b 실패 판정도 이 결과로 대체하지 않는다.

다음 명령은 원래 실행을 다시 수행하지 않고 이미 게시된 R2 source로 원본 artifact를 검증·재분석하는 재현용이다. 현재 세션에서는 이미 수행했으므로 같은 일을 반복할 필요가 없다. Output은 기존 디렉터리를 덮어쓸 수 없고, Git readback 또는 remote readback receipt를 반드시 요구한다.

~~~bash
python run_s7_coupled.py \
  --prereg evidence_s7_coupled/PREREGISTRATION_R2.json \
  --prereg-commit c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a \
  --publication-receipt delivery/s7/COUPLED_PUBLICATION_R2.json \
  --revalidate-existing evidence_s7_coupled/run01 \
  --out evidence_s7_coupled/revalidate_r2_new
~~~

후속 source를 수정하면 기존 prereg 검증이 실패하도록 준비되어 있다. 새 알고리즘의 source/prereg를 먼저 게시·readback한 다음 필요한 변경 history만 새 실행으로 남겨야 한다. 현재 FAIL 상태에서 REI production, full EoR 또는 merge를 승인하지 않는다.
