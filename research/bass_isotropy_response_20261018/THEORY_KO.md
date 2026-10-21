# 이론 문서 안내: S1 보존 및 완료된 S3

2026-10-19의 새 collisionless derivative/P4 유도와 양의 P2/P4 feasibility는
[S3_THEORY_KO.md](S3_THEORY_KO.md), 실제 수치 결과는 [S3_RESULTS_KO.md](S3_RESULTS_KO.md)를 따른다.
아래 원문은 2026-10-18 S1의 이력이다. 원문 말미의 NOT_RUN은 해당 S1 시점의 상태다.

---

# BASS LRS: 양의 이산 source-isotropy 보정과 방향 지지 조건

기준: BASS PR172 b163c5a08fe105c9df1d32f8e7d538e514ee9d16; native REI snapshot 0e25846433170d0f420c4cda44a0bedbf02cd177. 2026-10-18 신규 백업 조사에서 PR172 게시 보충본 이후의 native 측정은 확인하지 못했다. 조사 범위는 Dropbox/Google Drive BASS_BACKUPS이며 전체 개인 파일 탐색으로 확대하지 않았다.

## 정의와 정확한 지지 조건

서명 (-,+,+,+); ds²=-c²dt²+a²[e^(-2b)(dx²+dy²)+e^(4b)dz²]; x=ln(a/a_ref). 기준 방향 mu0의 현재 방향은 mu=mu0 e^(-2b)/R, R²=e^(2b)(1-mu0²)+e^(-4b)mu0², dmu/dmu0=J=R^-3. 기준 GL weights w_i>0의 source-frame prior는 q_i=w_i J_i/sum(wJ). 이는 sum q_i=1만 보장하고 sum q_i P2(mu_i)=0은 보장하지 않는다. 기존 광자장의 응력은 보정 대상이 아니다.

p_i=P2(mu_i), alpha_i>0, sum alpha=1에 대해 sum alpha_i p_i=0이 존재하는 필요충분조건은 min(p)<0<max(p)다 (모든 p가 0인 퇴화 경우는 별도 처리). 필요성은 convex combination이며, 충분성은 음/양 지지 사이의 조합에 나머지 점의 충분히 작은 양의 질량을 분배하면 된다. 닫힌 convex hull 끝점에서는 양의 일부 지지가 사라져야 하므로 엄격한 양성 계약에 부적합하다.

mu²=mu0²/[exp(6b)(1-mu0²)+mu0²]에서 p=0의 경계는 b=(1/6)ln[2mu0²/(1-mu0²)]. 따라서 짝수 GL_n의 qmin=min mu0²,qmax=max mu0²에 대해 b_min=(1/6)ln[2qmin/(1-qmin)], b_max=(1/6)ln[2qmax/(1-qmax)]이며 b_min<b<b_max가 정확한 full-positive feasibility domain이다. GL8의 값은 -0.4440698522273823,0.5275272066474278; GL16은 -0.6675463126414686,0.7551653071651082; GL32는 -0.8941410839612827,0.9828495026975167. 이것은 해당 고정 ray mesh에만 대한 정리이며 Bianchi I 물리 전체에 대한 no-go가 아니다.

## 최소 relative-entropy 변경

min_alpha sum alpha_i log(alpha_i/q_i) subject to sum alpha=1,sum alpha p=0을 사용한다. 이는 알려진 convex information projection이며 새 entropy closure 정리라고 주장하지 않는다. 정상조건으로 alpha_i(lambda)=q_i exp(lambda p_i)/Z(lambda). m(lambda)=sum alpha_i p_i의 미분은 Var_alpha(p)>0이다. 지지 조건 아래 m(-infty)=pmin<0<m(+infty)=pmax이므로 유일한 finite lambda가 존재한다. bracketed bisection은 convex optimizer 의존성 없이 안정적으로 구현된다. 보정된 합과 P2 residual을 종료조건으로 사용하며 infeasible 경우 tolerance 완화나 음의 weights로 우회하지 않는다.

Reflection-even prior 및 +/- ray pairs에서 p가 동일하므로 parity가 유지되고 dipole은 0이다. 그러나 P4와 이후 자유수송의 모든 고차 moment는 제약하지 않는다. 한 개 moment를 맞춘 결과를 continuum angular convergence로 승격할 수 없다. 주어진 수치 집합에서 KL-optimal이라는 사실은 전체 복사전달 오차가 최적이라는 뜻도 아니다.

## Source ownership 및 spectral 한계

factorized birth distribution dN(E,mu)=phi(E)dE alpha(mu)의 angular 부분에만 적용하면 number,energy monopoles는 유지되고 DeltaP/U=sum alpha p=0이다. 원래 native energy-panel/bin 교집합은 ray별로 다를 수 있어 실제 유한 구적은 factorization을 완전히 보존하지 않는다. 따라서 적용 후보는 신규 등방 source에만 opt-in으로 둔다. 기존 stock을 재가중하지 않으며 native source deposition의 scalar photon/energy ledger까지 실제 검증하지 않고 production adoption을 허가하지 않는다. Python predictor 실험은 N,U의 native finite-bin 잔차도 함께 기록한다. 이미 비등방 source인 경우 target0 보정 금지.

## 근거와 계산

광자 ray map 원전: Fleury, Pitrou & Uzan, Phys Rev D91,043511 (2015), arXiv:1410.8473. 일반 relative-entropy 원전: Friedlander & Gupta, IEEE Trans Inf Theory52(1),238-245 (2006), DOI10.1109/TIT.2005.860448. 본문 지지 경계와 BASS 적용은 직접 유도했다. Wolfram은 ray Jacobian, p=0 경계, 3점 exponential family의 variance 미분 항등식에 {0,0,0}을 반환했다. xAct·native Rust·NCP·독립 외부 심사는 이번 S1에서 NOT_RUN이다.
