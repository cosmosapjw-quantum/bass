# BASS KM-2E: 쌍방향 광자–전자 bulk 운동량 교환의 실제 계산

2026-10-30 · 독립 Draft PR #276. Immutable parent PR274 HEAD 8993bdf97c5aca2961a7d2e1df08bd4119899670. 상위 BASS DAG 9/15 (21 edges), KM-2 PARTIAL, 새 상위 완료 노드 0. 원본 코드와 기존 PR은 수정·병합하지 않았음.

## 1. 새로운 물리

이전 KM-2D는 외부에서 전자 beta(u)를 정했다. KM-2E는 기존 원본 BASS KM2A P8 편광 Thomson 충돌 및 KM1 noncommuting Bianchi-I 기하·스크린을 유지하면서, 동일한 전자 normal-tetrad beta를 원래 광자 충돌 4-force의 반작용으로 직접 결정한다. 전체 2×2 편광 coherency per ray를 유지하고, moment-only closure로 대체하지 않는다.

계량 (-,+,+,+), u=t/Tstar, beta=v_e/c, p=gamma beta, gamma=sqrt(1+p.p), zeta=n_lab(u)/n_lab(0), B=H I+sigma. M0=m_e c² n_lab(0). 전자 고유 밀도와 proper-time Thomson rate는 n_rest/n_rest0=zeta gamma0/gamma, nu(u)=nu0 zeta gamma0/gamma, nu0 Tstar=1.3.

새 self-consistent 냉물질 동역학:
- Jq' = original KM1 photon transport + original KM2A collision with instantaneously determined beta and nu.
- zeta'=-3H zeta (전자 정상시각 입자수 보존).
- p'=-B p-F_gamma_sp/(M0 zeta), where F_gamma is original covariant expected_fourforce(T_gamma,beta,nu) and electrons receive its opposite.
- Electron R=M0 zeta gamma, Q=M0 zeta p, P=R beta beta^T.

정확한 전자 정상계 에너지·운동량 항등식:
R'=-3H R-B:P-F_gamma0;
Q'=-(4H I+sigma) Q-F_gamma_sp;
beta'=-(I-beta beta^T)(B beta+F_gamma_sp/R).
Stateless Wolfram algebra yielded {0,{0,0,0},{0,0,0}} for these three checks. 두 서로 다른 matter-state 표현 p 및 beta의 실제 DOP853 full-photon coupled ODE를 독립 수행하여 확인하였다.

광자+전자 total normal E=rho_gamma+R, Q=q_gamma+Q_e, P=P_gamma+P_e:
E'=-3H E-B:P+deltaF_quad0;
Q'=-(4H I+sigma)Q+deltaF_quad_sp.
Finite raw P8 quadrature deltaF_quad=actual_raw_photon_force-covariant_photon_force. 이것은 이산 소스 오차로 실제 평가 및 별도 적분하며 0으로 강제하지 않는다. 팽창 Bianchi I에서 total normal-frame E는 일반적으로 보존상수가 아니다.

## 2. 동결 입력과 적용 범위

원래 BASS KM2D noncommuting prescribed Bianchi I, 동일 P8 Hermitian S+iA, 원래 angular ray 초기값, beta(0)=(0.30,-0.40,0.20), u∈[0,.25], normal optical depth proper nu0=1.3. Electron inertia initial ratio R_e0/rho_gamma0=0.75 는 고정된 무차원 장난감 물질 매개변수이며 실제 우주론의 전자 풍부도로 보정한 값이 아니다. n_theta=8/12, n_phi=2n_theta. Electron pressureless cold coherent fluid only; thermal electron distribution, frequency redistribution, Einstein metric feedback are not solved.

Immutable original Git blobs verified in CI:
- KM2D accelerating_tilt.py: b599d3842e843d8de1de1499b73e6849374bf8f8.
- KM2C curved_tilt.py: 05aade3aab7e9a32c11608882c943e4d3cb6f379.
- KM2A tilted_collision.py: 92660768f4719d78261fed1cb44f186d2821629d.
- KM1 source_memory.py: 9d500e36fefaa4ddc22300a2f03d9eb9cfe98403.

## 3. 실제 물리 생성 데이터

Science CI #41024984181 SUCCESS, actual 12/12 scoped pytest PASS, source identities pinned. 최초 실행 #41024863016은 진공 사후검증에서 abs(list)라는 Python TypeError로 FAIL했지만 두 격자의 물리 진화 출력은 이미 정상 생성되었다. 정확히 한 자료형 라인만 numpy array로 고쳐 #41024984181에서 동일 물리/허용오차로 재실행 성공했다. 초기 실패가 과학적인 zero-mode나 모델 붕괴를 의미하지 않음.

n_theta=12 physical full radiation+electron, u=0 and .25:
- photon rho_gamma: 39.011102627687464 → 25.93676528739797.
- electron R: 29.25832697076559 → 21.069728580543945.
- total E: 68.26942959845306 → 47.00649386794191.
- beta: (.30000000000000004,-.4000000000000001,.20000000000000004) → (.30263682182917695,-.37610163603062824,.1710105346084685).
- electron number zeta(.25)=.7340476693497661; rest density ratio=.7482368208304584; nu(.25)=.9727078670795961.

Photon-recoil removed (intentional NONCONSERVATIVE control) yields beta(.25)=(.29862543376462564,-.372192401113588,.16865127556191967). Actual two-way recoil beta difference vector (+.004011388064551313,-.003909234917040261,+.002359259046548823), length .006077783731735933, about 1.19% of final |beta|. n_theta8↔12 endpoint beta max difference 1.2745219601928426e-9. This is observed numerical angular agreement, not rigorous angular continuum enclosure.

At n_theta12 the independent GL24 integral of the original covariant photon force yields:
Integral F_gamma^mu du =
(-.10480372898007803,-.12940191983350166,+.13388820743622423,-.07858910082654896).
Electron receives exactly the opposite fourforce. This is directly constructed new reciprocal momentum transfer; it was not present in externally prescribed KM2D.

Total E change=-21.262935730511145.
Integrated geometric work=-21.262935730510016.
Integrated raw-P8-force-gap energy=-1.4104060947018781e-12.
Independent GL24 endpoint total-E closure absolute=2.877698079828406e-13, total-Q closure max abs=1.794120407794253e-13. No fake flat-space conservation in expanding geometry.

Numerical physics controls:
- Independently evolved p-based vs beta-based electron+photon state: beta max diff 4.957145804951324e-14; photon J max diff 7.416289804496046e-13.
- Matter mass shell maximum residual 3.3306690738754696e-16; force electron orthogonality 1.7319479184152442e-14; physical screen transverse leak 2.998e-12.
- The raw angle P8 vs covariant force normalized max gap n_theta8=7.689104559375128e-8, n_theta12=2.8793296667029348e-11. All quadrature defects remain separate from photon–matter interaction.
- Independent flat-geometry total photon+electron E drift 1.4210854715202004e-14; total Q drift 2.4868995751603507e-14.
- Vacuum nu0=0 test: photon collision force exactly zero; electron number-density relation correct.
- Tests reject tampered source Git blob and unphysical electron inertia or velocity.

## 4. 검증·증거와 한계

Actual GitHub Actions run 41024984181 SUCCESS 12/12 tests. Source+physics program under research/dual_lane_km2e_20261030/coupled_electron_photon.py, test_coupled_physics.py, package_artifacts.py. Original KM2C source and parent KM2D input have immutable byte identities; full source included in S0/S1/S2 archives. Scientific numerical outputs include full gamma, density, radiation E/P/Q, electron E/P/Q, source M, five epochs and 24 integration rows, physical JSON and CSV.

Model-level interpretation: homogeneous electron cold-dust bulk momentum and photon stress exchange on an externally prescribed noncommuting Bianchi-I background. This is not Einstein–Boltzmann self-consistent geometry; electron pressure, heating, thermal/recoil Compton frequency changes, generic inhomogeneity, multi-ion plasma and independent distinct-author review remain NOT_RUN. Stochastic CMB covariance and observations are not inferred. Neither finite-grid continuum angular certification nor whole-program formal correctness has been established.

## 5. 실제 백업 및 재현

Immutable original science-head SHA 72541334c3bb27356da5613e19ee7b70391db763; physical CI 41024984181.
S0 GitHub artifact 12963430650, 35,234 bytes, SHA256 9335544251b8ffd1fcbe70fa9f0307b0301cb49c863536d3363f3f9e54d3cfdd, Drive ID 1ajsbGLvK4dj8B__43i588qZ_lZJVW2e1.
S1 GitHub artifact 12962294552, 109,114 bytes, SHA256 fdcdd26ce0f5c477207e30a585776a0cb30663089032ed55882326f2fe62df6a, Drive ID 13GcMs7b23jLUPKJsRF0E5EAh2agKCswO.
S2 GitHub artifact 12962484177, 164,216 bytes, SHA256 449a42e54b6f38a139af9627f66fcccc338cd725d7840753b861928ca1858536, Drive ID 1nmc85KMl5LMxpkJCipNoXz8UXbqyXIFz.
All three Google Drive complete-byte downloads SHA256 MATCH the GitHub original ZIP, outer/inner ZIP CRC and 10/16/16 source member SHA manifest PASS. ChatGPT Library folder /BASS_KM2E_20261030/ stage archives upload ACK. Dropbox upload remains BLOCKED_NOT_UPLOADED because its source_file is host-injected, not accepted from this tool invocation. No false Dropbox receipt.

S0 source/theory Git checkpoint 38d36060197fed5d31699a28a6d1c8073d0ac0c3, initial code f9ba406b29764df0540818e2e641dd13b0f9cc35, tests 9b0c0da80f5ed073fcb377d97247c47f28c67c5f, targeted control repair 72541334c3bb27356da5613e19ee7b70391db763. Final report/receipt HEAD CI must be checked separately; do not claim it before observing its actual success.

Upper BASS DAG 9/15 (21 edges), KM2 PARTIAL, zero new upper completed nodes. production_ready=false; merge_ready=false; auto_next=false. Independent distinct-author R6/C9 and native subagent NOT_RUN. STOP_AFTER_ONE_BOUNDED_UNIT.
