# BASS FA03 / REI 이론 증보

최신 b453 FA02 백업을 복원하여 비회색 흡수의 정확한 band-derivative six-matrix system과 observer mixed response를 구성했다. 기존 I–VII dossier의 교체본이 아니라 R5 구성적 결과와 검산 capsule이다.

핵심 결과는 `manuscripts/FA03_KO.md`와 `manuscripts/REI_THEORY_KO.md`에 있다. FA03는 same-cap/local-rest-energy opacity slope와 균일 quadratic remainder `1250 ||h||inf^3`를 준다. REI는 isotropic scalar의 O(q) 소거 조건, 허용되는 O(q^3) odd response, 다섯 case 분석식, proper-clock 변환, 초기 등방 effective-radiation의 `|delta_s|/H < 2.61e-5` diagnostic bound를 준다. 이 상계는 full coupled geometry 또는 abundance error bound가 아니다.

검산: 실제 local Wolfram15.0.0+xTensor1.3.0의 10개 exact zero; cloud Wolfram15.0.1의 moment/stress/bound 계산; FA03 11개와 prescribed-background REI 10개 경량 기준 충족. xAct 원격 파일은 실제 bytes를 옮겨 SHA를 확인했다. Cloud xAct load failure, TDD 최초 실패, JSON numpy-bool 직렬화 실패도 보존했다. Full chemistry histories, atomic solve, independent scientific review는 이 스레드에서 실행하지 않았다.

실제 REI 2026-10-14 16:38:35 KST snapshot은 AX06 scoped pilot 완료, AX07/08 READY, AX11/12 PENDING이었다. 이 상태는 기존 Codex가 달성했다. 이 스레드의 theory-ready overlay는 canonical state나 active working tree를 수정하지 않는다. 현재 상태는 언제나 자신의 최신 STATE가 우선한다.

`contracts/INPUT_IDENTITY.json`은 다른 두 FA02 archive와 frozen contracts를 구분한다. `contracts/THEORY_DAG_OVERLAY.json`은 새 theory 결과와 실행 자료가 아직 필요한 항목을 분리한다. `CODEX_HANDOFF_KO.md`를 실제 실행 세션에서 소비한다. `CROSS_REPO_REUSE_KO.md`는 HE/CR/HH/observer 반환의 실제 소비 범위를 기록한다.

원문 수학 증보와 수치 evidence는 분리했다. 기존 이론 전용 dossier 본문에 실제 runtime 결과를 삽입하지 않았다. `SHA256SUMS.json`과 `python code/verify_capsule.py`로 데이터를 다시 계산하지 않고 capsule을 검증할 수 있다.

최초 checkpoint RUN_NOTE.md는 진행 중 snapshot이므로 최종 상태는 이 README/CLAIMS/검산 receipts를 따른다. 게시·백업 결과는 이 archive와 분리된 publication receipt가 최종 권위다. 로컬 artifact 생성만으로 원격 upload/restore 또는 과학적 admission을 주장하지 않는다.
