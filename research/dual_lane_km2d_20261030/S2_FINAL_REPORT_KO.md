# BASS KM-2D | 가속 전자 4-속도와 Bianchi I 편광 광자 기억 진화

**2026-10-30 · 상위 DAG 9/15, KM-2 PARTIAL · 한정 과학 유닛 완료(실제 실행).** 원본 BASS PR273의 고정 HEAD \`48e6c979c49a49ff6854a9555fe97a9690d86d16\`에서 독립 Draft PR274를 구성했다. Main, CE1-AA 원본, KM2C 및 형제 PR은 변경하지 않았다. 과거 CE1-AA \`h<1e-5\`는 다른 무충돌 여섯-cell 파일럿의 고정 목표이며 KM2D로 전이하거나 새 정확도 게이트로 재사용하지 않았다.

## 1. 질문과 보호된 물리

기존 KM-2C는 **고정된 전자 \(\beta\)** 및 처방된 Bianchi I 기하하에서 광자의 정상 스크린 수송, 정확한 순간 Thomson 충돌, 전체 초기 각도장을 유지하는 Volterra memory를 증명·검산했다. 본 실험은 **오직** 외부 전자 속도 \(\beta(u)\)를 시간에 따라 변화시키고 정상계 에너지 교환의 도함수를 정식화한다. 광자의 전자계 소스 \(\boldsymbol M_e\)는 여전히 원본 전체 \(\boldsymbol J\)에서 계산하며, 9변수 Markov closure나 저차 편광 모멘트 절단이 아니다.

계량 signature \((-+++)\), 광자 전파 방향 n, normal proper \(u=t/T_\star\). \(\beta=v_e/c\), \(\nu_0=n_e^\star\sigma_T c\), 코드 \(\nu=\nu_0T_\star=1.3\). 출발 \(P8\) real symmetric + antisymmetric \(S+iA\)는 Hermitian 물리 coherency. 원본 raw angular GL weights를 재정규화하거나 충돌 인자 \(D=\gamma(1-\beta\cdot n)\)를 두 번 곱하지 않는다. 원본 KM1의 noncommuting prescribed Bianchi-I \(H(u),\sigma_{ij}(u)\)는 Einstein equation의 해라는 주장을 하지 않는다.

실험의 전자 시간 이력:
\[
\beta(u)=(.30,-.40,.20)+u(.20,-.10,.12),
\quad 0\le u\le .25,\quad
\nu=1.3.
\]
처음과 끝의 속도가 광속 미만이며, timelike velocity ball의 볼록성에 의해 전체 affine 구간에서도 \(|\beta|<1\). 전자 EOM, ionization, 재결합, Thomson 열적/스펙트럼 domain 유효성은 미검증.

## 2. 유도한 정확한 이동 전자 소스와 가속 work

원본 KM2-C 정상 스크린 \(E_q(u)\), 기하학적 redshift \(\mu_q(u)\), raw angular weights \(w_q\)를 그대로 사용한다. 각 \(u\)에서 순간 부스트 \(S_{\beta(u)}\), \(D_q(u)\)를 새로 계산하되, 광자는 전자 프레임이 아니라 **normal-transported** 스크린의 \(X_q\)에서 표현한다. 따라서 전자계 부스트의 도함수를 광자 수송에 허위로 더하지 않는다.

\[
M_e(u)=\sum_q w_q\mu_q^4D_q^2 F_qX_qF_q^T,\quad
X_q'=-\nu D_q X_q+\frac{3\nu}{8\pi\mu_q^4D_q^3}F_q^TM_eF_q,
\quad F_q=S_{\beta(u)} E_q .
\]
이로부터 \(\tau_q(u)=\int_0^u\nu D_q(s)ds\)인 비마르코프 Volterra 방정식을 얻는다. 본 실험의 \`VolterraHistory\`는 원본 KM2-C의 독립 causal collocation을 호출하며 직접 Boltzmann IVP의 RHS나 source histories를 요구하지 않는다.

정상계 에너지와 flux \(T^{00}=\rho,\ T^{0i}=q_i\), \(\pi=T^{ij}-\rho\delta_{ij}/3\). \(\mathcal C=\gamma(\rho-\beta\cdot q)\)는 고정 \(\beta\)의 편광 Thomson collision-only 불변량이지만, \(\beta'\ne0\)이면 시간의존 tetrad에서 보존량이 아니다. 원래 instantaneous cold Thomson 강제항의 정확한 \(F^0=\beta\cdot F^{\rm spatial}\)을 사용하면
\[
\boxed{\mathcal C'
=-4H\mathcal C-\gamma\sigma:\pi
+\gamma\beta\cdot(\sigma q)
+\gamma^3(\beta\cdot\beta')(\rho-\beta\cdot q)
-\gamma\beta'\cdot q.}
\]
앞의 세 항은 기존 KM2-C 기하 work, 마지막 둘은 전자 frame-acceleration work다. Wolfram에서 원본 \(C(t)\)의 chain rule과 \(\rho',q'\)를 대입한 상징 잔차가 0이었다. 수치 비교에서는 이산 GL 각도 적분 때문에 남는 \(\gamma(F^0-\beta\cdot F)\)를 따로 계산하고 숨기지 않는다.

## 3. 실제 계산: source-memory 시간 수렴

[Actions #41009224680](https://github.com/cosmosapjw-quantum/bass/actions/runs/41009224680)의 **실제 BASS source-bound direct vs unknown-source Volterra** 물리 계산 완료. 초깃값·기하·광자 각도 원본 출처는 모두 동일하며 \(n_\theta=8,n_\phi=16\), 고정 source에 시간 패널만 바꾸었다.

| 패널 | 최대 \(|\Delta M_{ab}|\) | 최대 \(|\Delta J_{ab}|\) |
|---:|---:|---:|
| 8 | \(8.949428753624034\times10^{-9}\) | \(1.123389736790159\times10^{-8}\) |
| 16 | \(5.595888197262866\times10^{-10}\) | \(7.021174752708248\times10^{-10}\) |
| 32 | \(3.517097724170526\times10^{-11}\) | \(4.395328545570010\times10^{-11}\) |

원본 source와 angular grid 고정 상태의 오차 감소율은 \(p_{8\to16}=3.99936,\ p_{16\to32}=3.99191\)로 **이 실험에 한정된 관측 4차 시간 수렴**이다. Angular quadrature continuum error나 일반 time integration theorem은 아니다. 32패널의 최대 endpoint source consistency residual은 \(8.88\times10^{-15}\), source collocation matrix condition ≤1.0062.

## 4. 실제 새로운 물리: 외부 전자 가속도의 일

\(n_\theta=12,n_\phi=24\) 별도 angular control, 원본 full normal-carrier direct IVP, 시간 GL24 별도 quadrature:
\[
\mathcal C(0)=29.914517816823203,\quad
\mathcal C(.25)=19.589457930324535,\quad
\Delta\mathcal C=-10.325059886498668.
\]
직접 결과와 독립 기하/가속 work 분해:
\[
\begin{aligned}
\int_0^{.25}\mathcal W_{\rm geom}du&=-10.010380457942462,\\
\int_0^{.25}\mathcal W_{\rm accel}du&=-0.31467942854342584,\\
\int_0^{.25}\mathcal W_{\rm coll,GL}du&=-1.2898249590732633\times10^{-11}.
\end{aligned}
\]
세 항 합과 실제 \(\Delta\mathcal C\)의 차이는 **\(1.18528\times10^{-13}\)**. 가속항을 생략하면 \(0.3146794285433073\)의 분명한 물리 오차(전체 \(|\Delta\mathcal C|\)의 약 **3.05%**)가 생긴다. \(F^\mu\) 대 원본 공변 Thomson 예측의 최대 정규화 차이는 \(1.48624\times10^{-11}\), 이동 전자 탄성조건 위반은 \(1.14211\times10^{-11}\), 미분 항등 상대잔차 \(1.32\times10^{-15}\)다. 전자 자체의 Euler/energy equation은 풀지 않았다. \(\mathcal C\)는 관측자 선택에 따른 조합이며 가속항은 photon energy creation 또는 전체 물질+광자 에너지 보존의 증거가 아니다.

추가 source-null initial carrier 실험: \(n_\theta=10\), β(0)=0, \(I_{30}=.1\), 처방된 noncommuting 기하 및 시간변화 전자. \(\|M(0)\|=6.24076\times10^{-17}\)이지만 \(\|M(.15)\|=5.69645\times10^{-5}\). 이것은 초기 source만으로 radiation memory를 절단할 수 없음을 보여준다. 이 반응을 가속도 단독의 원인으로 식별하지 않으며, 기하 변화도 함께 있다.

## 5. 구현·검증·정확한 실패 분류

원본 \`research/dual_lane_km2c_20261028/code/curved_tilt.py\` blob \`05aade3aab7e9a32c11608882c943e4d3cb6f379\`, 원본 \`vendor/tilted_collision.py\` blob \`92660768f4719d78261fed1cb44f186d2821629d\`, 원본 \`vendor/source_memory.py\` blob \`9d500e36fefaa4ddc22300a2f03d9eb9cfe98403\`는 immutable input으로 검사하고 **전혀 편집하지 않았다**. \`research/dual_lane_km2d_20261030/accelerating_tilt.py\`에만 시간가변 beta evaluator, 원본 inherited direct/Volterra 결합, 정확한 가속 work 및 24시점 원시 물리 데이터 경로를 신설했다. 소스 변환·정규화·투영·허용오차 확장은 수행하지 않았다.

GitHub Actions #41009224680 **SUCCESS, 12/12 scoped pytest PASS**, Python compileall PASS. 상호 독립적인 direct와 Volterra 알고리즘, fixed-beta old KM2C 회귀, full ray optical depth, 진공, source-null, velocity timelike/clock guard, source SHA mutation, 물리 force and work tests 모두 실제 실행되었다. Test 재호출이 다른 저자의 모델-independent 검증은 아니다. 별도 독립 저자 R6/C9 및 native subagent 모두 NOT_RUN.

## 6. 단계별 실제 저장

S0 Git checkpoint \`29894ccba2a67e6dde7914d1e7841576a2870fbe\`, source+theory ZIP; S1 program Git \`e2d77d9b2993beff4cb118ee97ad2100362e9d01\` 및 tests \`c44177ac685d06dcbc46ca41765d0861341f226d\`; verified science workflow HEAD \`c4628bc9e84d4be451c88fd6aab82a1c4ab46c6d\`. CI #41009224680 S0/S1/S2 artifacts #12956837485/#12957245361/#12956559058. 각 아카이브의 ZIP CRC 및 **9/9,14/14,14/14** payload member SHA256 PASS. GitHub raw outer ZIP을 Google Drive \`/BASS_BACKUPS/\`에 create-only 업로드했고 **S0/S1/S2 각각 전체 raw byte 재다운로드 SHA256 exact match**.

| 단계 | 외부 ZIP bytes | 외부 ZIP SHA256 | Drive ID |
|---|---:|---|---|
| S0 | 29,508 | \`7a2cb1fdc6fec02901c2332cd19d8503365f754c7340fab1fb894fdb72c1e3d2\` | \`1Vjuu6UwZ33Oqlw8vtUmPt0SCSfmQVet4\` |
| S1 | 51,438 | \`8f06770c3ef98e394a0b4a1741abcb5f010e9e4c52c9dafdab6d556804e8d24c\` | \`1-6e8NzPonfCcCT7dlloLl8Q0Kj-Npy_K\` |
| S2 | 62,412 | \`dd0cc169e4cd2532d19c4a70b2069270e62959c049cd590299dc8366a0d886cc\` | \`16VDTtS-vDh7EGEX23Y4GfzsrpzEcfN8W\` |

ChatGPT Library \`/BASS_KM2D_20261030/\`에도 세 파일 실제 업로드 ACK (라이브러리 독립 원본 바이트 readback은 NOT_RUN). Dropbox \`/BASS_BACKUPS\` 새 ZIP은 ChatGPT fileParam source injection 불가능으로 **BLOCKED_NOT_UPLOADED**이며 이중 공급자 성공으로 주장하지 않는다.

## 7. 판정과 다음 미완료 물리

KM-2D scoped physical science: **implementation-verified + numerically checked**, 조건부 비평형 Thomson 기하 결합, 원본 KM2C 계보 연결. **Upper KM-2=PARTIAL; BASS upper DAG 9/15 (21 edges), 새 상위 노드 0**. 실제 자기일관 electron acceleration/continuity + matter stress-work opposite exchange, generic Bianchi tilted geometric propagation, spectral-domain certification, generalized positivity, production Rust, 독립 리뷰는 미검증. \`production_ready=false\`, \`merge_ready=false\`, \`auto_next=false\`. STOP_AFTER_ONE_BOUNDED_UNIT.
