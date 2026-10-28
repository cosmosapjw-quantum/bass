# BF3-D 종료 인계

REPO=cosmosapjw-quantum/bass
BRANCH=research/bass-bf3d-local-lapse-source-20261028
PR=226
PARENT=5461d50b3f187b4736b62e0f9ecb3e85e413aaee
VERIFIED_CODE_COMMIT=b93731b94cb9a66a5face69c4164243aebff1100
CI_RUN=40659768531
STATUS=COMPLETE_SCOPED_STATIC_LAPSE_INVERSE_FIELD_COLLISIONS
UPPER_DAG=8/15
UPPER_BF3=PARTIAL
NEXT=BF3-E_ONLY
AUTO_NEXT=false
PRODUCTION_READY=false

현재 branch HEAD, README_KO.md, RESULTS_SUMMARY.json, DAG_STATE.json, PRESERVATION.json 및 full ZIP의 REPORT_KO.md/DAG_UPDATED.json을 읽어라. 이후 docs-only final commit과 실행된 code commit을 구별한다. S0/S1/S2의 백업은 새로운 과학노드가 아니다.

실제 package 진입점은 bianchi.nonperturbative.lapse_field이다. Explicit backend='python_oracle'. N=exp(epsilon cos x),Y=N4 W, physical J=N^-4 EYE^T, coordinate collision rate=N*n_e_star*sigma_T*c*Tstar를 유지한다. Local source는 최종x의 최종 방향에서 적분하며 global phase-volume Jacobian을 곱하지 않는다. Source-null tail은.1cosx P4(mu)의 Legendre 진폭이다.

12unique tests와 full-checkout CI, installed-wheel numerical equilibrium PASS. 주 science1회,direct11/split7/inverse-ray6/Hamiltonian1,old/current science replay0. Strang64 physical carrier/source 차이8.48e-7/2.59e-6,관측2차. 공간/각도오차는 별도. Legendre label만 정정했고 모든 수치값과 pre-label 증거를 보존했다. Native/독립모델심사 NOT_RUN.

다음 BF3-E는 같은 lapse에서 independent unknown retarded local-source memory의 제한된 절편이다. 실제 inverse position/direction/screen,coordinate opacity,whole initial carrier를 유지한다. Continuum transfer와 fixed finite interpolation/Galerkin 문제를 동일시하지 말고 시간/공간/각도오차를 구별한다. Stationary N^-4와 local non-equilibrium clock, periodic Killing energy, wrong-Jacobian 대조를 재사용한다. Einstein/matter/native/tilt/spectral/general positivity는 별도 의무다. 다음노드 자동실행이나 merge는 하지 않는다.

재현은 repo에서 OPENBLAS_NUM_THREADS=1 python -m pytest tests/nonperturbative/test_lapse_field.py -q. ZIP에서는 PYTHONPATH=package python -m pytest tests/test_lapse_field.py -q; python verify_saved.py는 저장증거만 검사한다. verify_bf3d.py는 scientific campaign이므로 자동 replay하지 않는다. Runtime 상태는 매 턴 실제 probe로 판정한다.
