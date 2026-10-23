# 다음 연구: G1B 이후 결합 오차 전달 G1C

최신 DELIVERY_FINAL.json과 PR의 마지막 전달 댓글이 archive ID 및 최종 publication identity를 소유한다. 이 문서는 자기 commit SHA를 소급 삽입하지 않는다.

```text
$physmath-research-loop로 BASS background G1C를 이어가라.
repo: cosmosapjw-quantum/bass
branch: research/background-kinetic-g1b-20261023
unit: research/background_kinetic_g1b_20261023/
parent G1A PR183: ce59a3fd50139a0414d77d5fc493df9d45cd5f49

최신 branch/PR와 DELIVERY_FINAL.json, REPORT_KO.md, THEORY.md,
DAG.json, RESULTS.json, SCIENCE_MANIFEST.json을 먼저 읽어라.
Git selected source와 full raw archive를 구분하고, 없는 raw는
DELIVERY_FINAL의 Drive/Dropbox ID로 직접 복구하라.

완료한 G1B는 새 정상18IVP=계획16+half-step2다.
별도 초기 RHS 실패1은 pi 대칭성 floating-point 표현 문제였고 보존했다.
G1A의18개와 이번18개를 같은 캠페인으로 합치지 마라.
source8+최종driver5=고유13 pytest items다. 중복 GREEN 호출을 합산하지 마라.
고정상태6개/고유60moment + 민감한Planck 참조1개, MP55 LRS oracle,
그림3세트와 범례1회 교정은 같은 source면 다시 실행하지 마라.
verify_saved.py는 저장 hashes/배열만 읽는다.

새 smooth FD는 momentum-decoupled1/(exp(q)+1)이다.
원 vendor/freestream의 clipped finite-node source와 다르다.
Z_m은 모든 grid에 같은 continuum값이며 rho를 사후 재정규화하지 않는다.
Planck는mass0이고 qbar=I3/I2, number weights로 N^a,T^ab radial을 정확히
축약한다. I4/full spectrum/energy-dependent collision을 보존하지 않는다.
선택 curved grid는massive32radial×392angular + photon392다.
강한 frozen-state군에는radial48,angular3200이 필요했다.
두 설정을 정의역 구분 없이 교체하지 마라.

signature(-,+,+,+), kappa=8piG/c^4, tau=ct/L,
q=cp/(k_B T_ref), G1A의Class-B logweight와 local boost Jacobian을 유지한다.
현재moment와reaction-rate, totalgas와electron pi를 혼합하지 마라.
core constraint와kinetic constraint 및rho/flux ledger mismatch를 모두 감시한다.
새 symmetric_bridge는여섯 대칭성분을 한 번 합산하며 vendor는변경하지 않았다.
허용오차를 늘리거나 positivity/density projection으로 숨기지 않았다.

다음 G1C: source error가 self-consistent geometry/moment error로 전달되는
bounded-domain 안정성 계약을 유도하고 저장 이력에서 residual/sensitivity
추정 경로를 검증하라. 현재Q48tail bound는COMMON prescribed field에서만
유효하므로 전체 coupled trajectory certificate로 승격하지 마라.
검증된 Lipschitz/enclosure가 없으면 empirical bound와 분리하라.
일반 smooth tilted IC, collision/emitter four-force, production/restart와
전역 parameter/time 범위는 별도 의무다.

현재 runtime을 실제 probe하고 과거 실패를 상속하지 마라.
최신 병렬 source delta는 조회하되 변경없는 계산은재사용한다.
native_subagent와fresh independent model review는 이전 단위에서NOT_RUN이었다.
단계별실제게시/백업/정확한claim gate를갱신하고merge/production을하지마라.
```
