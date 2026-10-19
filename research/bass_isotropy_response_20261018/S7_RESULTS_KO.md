# S7 종합 판정: 결합 응답과 native 정확도

2026-10-19. S7의 제한된 연구 루프를 실제 완료했다. **원래 coupled R1/R2 FAIL 보존, R3 한 이력 수리 PASS, native integrity PASS와 high-b angular accuracy FAIL**을 구별한다. 모든 원시 데이터와 원래 판정은 단계별로 보관한다.

## 1. Intake와 새로 수행한 범위

연구 전 양쪽 `/BASS_BACKUPS`, GitHub HEAD와 PR174 댓글을 확인했다. 사용자 기준 a9c3e495보다 뒤의 S6 science04a3a851/closeouta9704c6f를 발견했다. Drive raw ZIP927047bytes, SHA256 `93ae03207b9c1fcccba56b4ec6cd22408f9f03fb7a86e5dec72fe62793915ea1`, manifest86/86과 Git blobs가 일치했다. Dropbox는 이번 최신 metadata와 이전 raw readback 영수증을 대조했다. 완료된 S2 Rust5/S3 P24/S5 native/S6 캠페인은 반복하지 않았다.

이번에 새로 수행한 것은 SciSpace·Exa 문헌 탐색과 두 primary paper 확인, Wolfram 대수식 확인, 독립 Fraction28/Decimal5 검산, 닫힌 donor·Einstein history36입력+7benchmarks, 고정 native owner의51입력, exact observer 재분석, 한 이력의 수치 수리, 단계별 게시·백업·인계다.

## 2. 이론 결과와 해석

F=〈R〉, G=〈D〉, A=G/F, M_l=〈P_l〉이다. 기존 S3의 직접 유도를 재사용했다.

\[
D(0)=P_2,\quad D'(0)=-\frac85-\frac{10}{7}P_2+\frac{36}{35}P_4,
\]
\[
D''(0)=\frac{16}{7}+\frac{12}{7}P_2-\frac{216}{77}P_4+\frac{216}{77}P_6.
\]

M2=0과 continuum 첫 shear response 일치는 다른 조건이다. M2=M4=0 이후에도 A''(0)=16/7+(216/77)M6이므로 고차 응답은 남는다. Constraint와 angular refinement를 분리해야 한다.

새 S7은 energy-density convention k=8πG/(3c²), L0=Λc²/3에서

\[
H^2=s^2+k(U_d+U_\gamma)+L_0,\qquad \dot s=-3Hs+k\Delta P,
\]
\[
\dot H=-H^2-2s^2-\frac{k}{2}U_d-kU_\gamma+L_0,
\]
\[
\dot U_d=-3HU_d-Q,\qquad\dot U_\gamma=-4HU_\gamma-2s\Delta P+Q
\]

를 구성했다. H는 constraint로 반복 덮어쓰지 않고 Raychaudhuri 식으로 독립 진화했다. C=H²−s²−k(Ud+Uγ)−L0이면 Cdot=−2HC다. Donor 손실을 생략하고 photons에만 Q를 더하면 Cdot+2HC=−kQ의 결함이 생긴다. 실제 MD14 coupling에는 에너지 공급을 포함하는 closure가 필요하다.

Radiation-only, 이산 stress-isotropic equilibrium에서 q=s/H에 대한 선형화는

\[
\frac{d}{dx}\binom q{A}=\begin{pmatrix}-1&1\\-\kappa&0\end{pmatrix}\binom q{A},
\quad\kappa=\frac85-\frac{36}{35}M_4.
\]

z=μ²∈[0,1], Ez=1/3과 양성으로 1/9≤Ez²≤1/3이므로 −7/18≤M4≤7/12, 1≤κ≤2다. 고유값은 −1/2±i√(4κ−1)/2다. P4 일치는 국소 주파수를 continuum3√15/10으로 맞춘다. 일반 잔류 M4의 nonlinear spectrum 캠페인은 실행하지 않았다.

[상세 이론](S7_COUPLED_THEORY_KO.md)에 문헌 convention mapping, birth-memory tangent 계약과 독립 검산을 실었다. 원논문 [Lee–Nungesser–Tod](https://arxiv.org/abs/1911.04937), [Calogero–Heinzle](https://arxiv.org/abs/0911.0667)를 확인했으며 서로 다른 extrinsic-curvature 부호를 변환했다. Full tangent solver 실행은 남은 의무다.

## 3. 실제 coupled 결과와 exact 수리

| 검사 | 실제 결과 |
|---|---:|
| Main | 36시도,28완주,8 support 실패 |
| 독립 benchmarks | 7이력 |
| Hamiltonian 최대 relative residual | 6.2780232e−14 |
| 개별 cohort energy identity | 3.4734871e−15 |
| Birth event energy jump | 3.2020143e−16 |
| Source-frame GL128/256 차이 | 4.5449755e−16 |
| Nonlinear−linear 오차비 | 3.9907757,3.9953428 |
| Continuous isotropic donor midpoint 오차비 | 4.0000262,4.0000066,4.0000016 |

기존 isotropic stock과 양의 physical anisotropic stock을 보존하고 신규 birth만 보정했다. K/angular n/제약의 효과를 분리했다. GL128/256 일치는 기록 구간의 reference 비교이며 전역 continuum bound가 아니다. Duhamel 일치는 측정한 두 nonlinear 해의 일관성 identity이며 full tangent의 독립 예측 검증이 아니다.

R2는 원래 trajectory를 재실행하지 않고1968birth rule/56old-stock digest와41원시JSON을 검증했다. Float observer가 거절한 세 birth는 exact로 통과했지만, 640 constrained birth를 모두 확인하자 다른 하나가 실제 실패했다. M2는640/640, P24 M4는255/256 PASS였다.

실제 초과는 b03_n32_P24_K64,birth50,u=0.6312500000000001,b_u=0.3310282262303169에서 M4=−3.0005964896306507e−15였다. 고정 gate3/10^15를5.9648963e−19 초과했다. 양의 support는 feasible하므로 `EXACT_BINARY64_BIRTH_MOMENT_EXCESS`로 분류했다.

R3는 **기존 P24 API의 내부 atol만1e−15**로 지정한 별도 runner를 준비해 게시·readback 뒤 해당 한 history의64개 birth 전체를 다시 계산했다. 최종 exact gate3/10^15는 유지했다. 64/64 PASS, 최대 exact moment9.6095162e−16, 최대 Hamiltonian5.3718201e−14였다. 원래 이력 대비 최대|δh|2.2204460e−16, |δ(s/H*)|2.0816682e−17이며 old-stock digest도 같았다. 원본 R1/R2 FAIL은 보존한다. 다른 grid/history에 대한 margin 일반화는 검증하지 않았다.

## 4. Native 결과: 보존과 정확도는 별도

원본 rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177의57파일을 그대로 컴파일했다. Source ID는 MD14_Z002_FESC_BB50K_13P6_100_V1이며 원래 spectral source/atomic cross sections를 유지했다. 51입력 중42측정,9 support 실패다. R2 exact constrained births808/808 PASS,42개 기존 physical metrics와9 support failure가 원래와 동일했다.

b0=0.6,n_mu=32,같은16 births에서 최종 A_native−A_ref는 prior−1.4285450283e−2, P2−3.3193236042e−3, P24 **−9.9452975659e−4**였다. P24는 개선했지만1e−6 목표에는 FAIL이다. Source-panel 확장 row에서도 같은 failure가 확인되어 두 FAIL row로 보존했다.

b0=0.6,n16 P24의 upper-hull second-z-moment 상한0.18387221855는 필요한1/5보다 작다. b0=0.9,n32 P2는 u=0.425에서 max z=0.33047219616<1/3이 되어 실패했다. 음의 weights와 tolerance 완화로 우회하지 않았다.

Native per-H quantity는 eV/H이므로 continuity는 U_H′+U_H+2b′ΔP_H=0이다. Density 변환의 nH0/a³까지 포함하면4U 항이 된다. 최대 continuity residual4.96754e−13, 새 birth ledger8.87550e−15, slab photon/energy ledger3.03628e−16이었다.

최종 한 번의 frozen-opacity BE slab에서 흡수 전 inventory로 정규화한 merged-cohort response error:

| energy bins | photon | energy |
|---:|---:|---:|
|24|−1.140556308e−3|−1.286162302e−3|
|48|−2.183527676e−5|−2.420791700e−5|
|96|−5.096022564e−7|−5.698246120e−7|
|192|−2.070984137e−8|−1.105225461e−8|

Fine-bin192는 사전1e−4 목표를 통과했다. Bin96 고정/source panels8→64에서는 오차가 거의 유지되어 이 경우 bin representation 문제가 구별된다. Old-stock 보존은 별도로 검사했고 흡수 slab은 누적 **새 cohort**에 적용했다. 전체 old+new reactive history 검증으로 확대하지 않는다.

## 5. 실패 분류와 남은 의무

| 분류 | 보존한 결과 | 다음 조건 |
|---|---|---|
| 양의 angular support 부재 | Coupled8,native9 | Support/refinement 변경과 제약 추가를 분리 |
| Float false rejection | Coupled3 births,native1 birth | Exact dyadic 재판정,원 raw·판정 유지 |
| 실제 수치 초과 | Coupled R2 M4한 건 | R3 한 이력 수리완료,다른 입력은 별도 검증 |
| Angular accuracy 부족 | Native high-b두 row | 1e−6 기준 유지,grid/refinement 연구 |
| Coarse spectral representation | Slab coarse bins의 유의한 오차 | Fine-bin 및 full history 검증 |
| 미실행 의무 | Full tangent,native Einstein feedback,evolving reactive history | 새 코드·물리 계약 필요 |

S6 비구간 수치 인증과38/344 pre-asymptotic rate FAIL도 원 범위로 유지한다. REI production/full EoR/merge 승인은 없다.

## 6. 게시·자원·재개

과학 입력2865f60b → 실제 결과/R2계약c689dcf1 → exact증거/R3계약f993bf71 순서다. 각 새 실행은 해당 source/prereg의 원격 readback 뒤 시작했다. R2는 사후 observer 수정이며 새 물리 예측으로 재분류하지 않는다. 최종 metadata identity는 이 파일의 containing commit과PR174 closeout에 기록한다.

실제 native job27.36초,coupled20.15초,R3한 이력3.17초였다. 가장 큰 기록 child RSS337564KiB, 추가 stagingworker4/계산1thread였다. Worker≤16/RAM16GiB/disk4GiB/job1800초 상한을 유지했다. 이 샌드박스에서 완료했으므로 현재 S7 실행을 NCP 의무로 남기지 않는다.

[DAG](DAG.json),[RETURN](RETURN_TO_CHATGPT.json),[cloud](CLOUD_READBACK_KO.md),[Codex handoff](CODEX_HANDOFF_KO.md),[새 대화 handoff](NEW_THREAD_HANDOFF_KO.md)를 따른다. 새 연구 전에 두 클라우드의 새 실행과 GitHub HEAD/PR 댓글을 다시 확인한다.
