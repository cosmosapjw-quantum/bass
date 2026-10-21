# 다음 대화 스레드용 handoff prompt

아래 내용을 새 대화에 복사한다. branch의 최종 commit과 백업 hash는
delivery의 실제 ACK를 먼저 읽어 확인하도록 작성했다.

~~~~text
$physmath-research-loop의 ACCEL04 → PHYS04 → PILOT04 결과를 이어서 사용해줘.
이미 완료한 계산을 반복하지 말고, 내가 지정하는 다음 연구 범위에 집중해줘.

기준:
- BASS: https://github.com/cosmosapjw-quantum/bass/pull/180
- REI: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/220
- branch: research/rei-hheli-compact-pilot-20261022
- path: research/rei_hheli_compact_pilot_20261022
- physical source base:
  ee7e9ae76c852079ce86cdd5165624ab2b7fc7a9c672016501ed5da5fb4341d3
- immutable REC119 donor:
  a949529872eb5ba0e20c7e206fe893e5d544e48c

먼저 REPORT_KO.md, FROZEN_CONTRACT.md, THEORY_KO.md, DAG.json,
LOOP_RECORD.json, CODEX_HANDOFF.md, evidence/ROOT_ADMISSION_C.json,
evidence/independent_review/ 및 delivery/를 읽어줘.
delivery/FINAL_PUBLICATION.json과 STAGEC_BACKUP_VERIFIED.json에서 실제
commit, 백업 ID·크기·SHA256·GET 검증 상태를 확인해.
접근 가능한 새 branch/repo/대화/백업 결과가 생겼는지부터 비교하고,
접근하지 못한 범위는 명시해줘.

완료 데이터:
- non-tilted LRS Bianchi I, z=20→2.
- 125개 grid + 초기 matter/radiation 응력 상쇄 2개 = 127 cases.
- 사례당 193개 시점, 본 history 24,511행, retained gate 13개 모두 PASS.
- 추가 unchanged full62 oracle 2개와 33↔62 paired check도 PASS.
- authoritative raw: results/pilot_v2, results/full62_oracles.
- PNG/PDF 4종: Sigma/Pi time evolution, 21-state isotope/ion,
  cancellation, parameter-sweep slices.
- 기본 run_pilot.py는 pilot_v2를 가리키며, 127개 완료 자료 재사용과
  새 integration 0회를 확인했음.
- 큰 aggregate CSV/NPZ는 전체 C 백업에 있고, 개별 raw에서 재생성 가능.
- 첫 실행의 NumPy bool JSON 저장 오류 원본은 별도 보존했으므로
  성공한 결과와 혼동하지 말 것.

물리 범위:
Full Frobenius Sigma=|sqrt(6)s/H|,
Pi_A=|sqrt(6)kappa_t p_A/H²|를 사용해.
matter/radiation signed stress를 독립 초기화하고 합한 뒤 total norm을
취한다. 기존 half-contraction 값은 full/sqrt(2)다.
pi_m은 별도 collisionless 비바리온 massive 성분,
pi_r=photon+neutrino이며 common-T 바리온은 pi_b=0이다.
상태는 n, H1 I–II, D I–II, T I–II, He3 I–III, He4 I–III,
Li6 I–IV, Li7 I–IV의 21개이며 electron은 charge 합으로 얻는다.
초기 n=T=0이다.

Photo/RR/DR과 전자밀도→Thomson feedback을 포함하지만,
지정 T(z)와 5–200 eV 외부 UV의 test-fluid preliminary 모형이다.
CI/CX, 분자, secondary electron, 열핵반응, full thermal/radiative Q^a,
isotope-specific rates 및 분해능 수렴은 완료되지 않았다.
33상태 축약은 짝수 LRS 부분공간과 동위원소 전자율·초기분율 동일성에
한정되므로, 확장 물리에서는 적용 여부를 다시 판정해야 한다.

주요 관찰:
초기 total stress가 상쇄되어도 성분의 다른 진화로 total stress와 shear가
생겼다. z=2에서 두 상쇄 사례의 signed shear는 약 ∓5.083e-5,
q≈0.7378이다. 초기 Sigma 0–0.6과 P_m/P_r의 독립적인 부호 범위를
포함한 가시적인 sweep을 완료했다.
이를 full closure나 global convergence의 증명으로 확대하지 말 것.

실제 실행은 8 CPU quota / 8 GiB 샌드박스, 4 workers, 수치 thread 각 1개다.
NCP target 64 CPU / 128 GiB는 목표이며 현재 live 가용량은 그 서버에서
확인해야 한다. 다른 Codex 세션이 있다는 이유만으로 중지하지 말고,
실측 CPU/memory와 peer reservation 안에서 작업을 나눠줘.
상세 성능 benchmark는 필요 없다.

매 새 단계마다 백업·게시·진척·다음 DAG 노드를 함께 기록하고,
가능한 코드 수정과 가벼운 실제 검증을 여기에서 끝내 push해줘.
기존 warm729(243 groups PASS, 47,385행, a=.1999→.2)도 보존해줘.
이번에 내가 지정하는 다음 연구 범위부터 새 계약으로 시작해줘.
~~~~

