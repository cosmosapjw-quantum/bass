# FA03-R6: 수동 opacity 나머지와 실제 REI 비교 좌표

2026-10-14. 부모3348fc73f59022c5ab2ec00474d36bbcac54f5ec의 b453 두 observer 매개변수 family를 고정한 작성자 R6 검토다. 원 식의 현재 범위 차단 오류는 발견되지 않았다. 외부 독립 심사와 native subagents는 NOT_RUN이다. 원 SOURCE_CLOCKS/ABUNDANCE/21-node DAG 및 D9.1을 변경하지 않는다.

## 비회색 미분과 새 나머지

x=t/t_o in[1/2,1], e=E_w/E_* in[.98,1.02], k=E_rest/E_w에서 F'=B-L_G F-epsilon A_e F, A_e X=(ek-1)(HX+XH^T), H=Sigma^T K0 Sigma/2, G=H+Omega다. Epsilon은 흡수만 변경하며 ray/source/initial slice/analyzer는 고정한다. 원 여섯 행렬의 epsilon=0 moment closure, W의 factor2 및 observer mixed term e*k_alpha를 실제 noncommuting tensor/energy projection으로 확인했다. Finite epsilon의 전체 spectrum closure라고 주장하지 않는다.

Real observer |chi|,|psi|<=.02, cap<=.02, |epsilon|<=.1에서 .96<ek<1.66, ||H||2<=.4, 1+epsilon(ek-1)>.934이다. 회색 순서화된 전파자 T0로 (Kf)(x)=integral T0(x,u) A_e(u) f(u)du를 정의하면 exact Duhamel identity에서

    F(epsilon)=F0-epsilon K F0+epsilon^2 K^2 F0-epsilon^3 K^3 F(epsilon)

를 얻는다. 행렬의 commutation이나 Neumann 급수 가정을 사용하지 않는다. Real passive propagator의 trace-norm 수축성과 zero IC에서 ||F(epsilon,x)||1<=B(x-1/2), B=77335533/62500000, ||A_e||<=alpha=66/125다. 세 ordered integrals와 source의 한 적분을 합하면

    ||R_epsilon,2||1 <= B*alpha^3*(1/2)^4*|epsilon|^3/24
                     =0.000474318003101184*|epsilon|^3.

따라서 |epsilon|<=.1에서4.75e-7 미만이다. 이것은 fixed real observer의 epsilon-only Taylor remainder이며 joint observer/epsilon bound1250||h||infinity^3를 대체하지 않는다. Exact Taylor coefficients와 exact cap/band average에 대한 식이다. 실제 numerical coefficient/integration error 및 empirical provider error는 별도이며 null이다. 물리 normalization에는 원 c*t_o*E_*^2*j_*(e_+-e_-)를 유지한다.

새 FA03 검사19+mixed2, 유리수 domain5, 실제 Wolfram15.0.0+xTensor1.3.0의6zero를 저장했다. 별도4-vector normal screen과 observer screen의 field discrepancy<6.67e-16, energy projection<1.36e-15, mixed chi/psi discrepancy<6.11e-11/<4.01e-12다. Epsilon=+-.1의 직접 잔차는약1.96e-9..4.10e-9로 위 상계 안이다. 이는 점 검산이며 numerical continuum certificate가 아니다.

## 실제 REI native 자료의 좌표 구별

10:32:07UTC의 실제 owner head는ab60f87beaf2ee87b7fb60ba4b07b10a11c0c15a였다. ZERO zbar20->4는 owner의 conditional scoped 심사를 받았고 signed family와refinement는 미완료였다. 이후 live runtime 상태는 여기서 단정하지 않는다. 이 supplier는 REI solver를 실행하거나 active source/STATE/supervisor를 변경하지 않았다.

기존 ZERO/PLUS partial history.csv의 SHA를 확인하고 마지막12행씩만 소비했다. 두 terminal native nodes는 같은 a=.08873654701704167이지만 PLUS-ZERO time은-171173626754s다. 같은a에서 delta xHII=-1.2567578673e-6, delta T=-.02654202245K다. 같은 elapsed proper time에서는 ZERO의 두 인접 native rows 사이의 PL 참조로 delta xHII=+2.3443161256e-6, delta T=+.06490733918K다. 같은좌표가 다른 observable임을 보여주는 finite-reference 사실이며 물리적 부호 검출은 아니다. 두 경우 모두 paired refinement error는 unknown이다. 범위 밖 PLUS extrapolation은 거절했다.

Xi=(1-theta)Xi_node+theta Xi_next의 true-error radius는 실제 node radii와 같은-coordinate curvature M2가 있을 때만 (1-theta)d_i+theta*d_next+M2*h^2*theta*(1-theta)/2로 bound한다. Missing node/curvature error는0이 아니라null이다. Shared weights는 선형 보존식을 보존하지만 ne=nH*xe 및 EOS와 같은 비선형 derived columns는 재구성 계약이 따로 필요하다.

Five-case 순서[-q,-q/2,0,q/2,q]의 scaled contrasts C1=q*A1hat,C2=q^2*A2hat,C3=q^3*A3hat의 weights는 [1,-8,0,8,-1]/6, [-1,16,-30,16,-1]/6, [-2,4,0,-4,2]/3이다. 동일 additive bias는 행합0으로 상쇄된다. 실제 각 node error<=d의 deterministic radius multiplier는3,32/3,4이며 stochastic covariance를 가정하지 않는다. Exact +/-shear symmetry도 강제하지 않는다.

## 즉시 소비

response.py는 full capsule의 실제 검증된 코드와 동일한 bytes다. Standard-library unit tests21개 및 실제 native slice21조건을 통과했다. Tests, native24rows, exact CAS inputs/outputs, proof 전문, raw logs, source/parent archives와 verifier는 아래 pinned ZIP에 있다. Public Git에 private native rows를 게시하지 않는다.

현재 REI supervisor를 재시작하지 않는다. 현재 owner가 실제source/config/clock/normalization 및 비교coordinate를 bind한 뒤 response.py를 별도 AX11 analysis에 import한다. 각refinement level에서 먼저 common-coordinate pairing 후 scaled contrast를 계산한다. Supplier 준비는 완료됐지만 canonical AX11이나 scientific admission을 승격하지 않는다. 실제full family+baseline및두refinement가 다음 입력이다. CR/RCT/HH OFF와optional observer tail의 비차단 상태를 유지한다.

다음 BASS 선택 단계는FA03-R7이며 미실행이다. 변경 없는 원 R5/PNS/AP 검산을 반복하지 않는다. 상세증명은 full archive의 manuscripts/R6_REVIEW_KO.md와 manuscripts/REI_RESPONSE_KO.md, 인계는 CODEX_HANDOFF_KO.md다.

문헌 맥락: Fleury–Pitrou–Uzan2015 arXiv1410.8473의 Bianchi I optics, Gammie–Leung2012 doi10.1088/0004-637X/752/2/123의 covariant coherency, Carlin–Blanes–Casas2025 doi10.33232/001c.133661의 noncommuting transfer를 확인했다. 새 명시적 상계는 직접 유도이며 문헌 우선권 주장이 아니다. HE50 첫-cell residual와CR61 same-grid paired comparison의 구분을 재사용하되 그 source-specific 숫자는 cold AXBI에 이식하지 않았다.
