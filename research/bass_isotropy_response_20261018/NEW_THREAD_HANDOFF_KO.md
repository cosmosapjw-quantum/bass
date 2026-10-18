# 새 ChatGPT 대화: BASS 등방 source 구적 연구 재개

$physmath-research-loop로 다음 작업을 이어서 진행해줘. 본문에 필요한 맥락이 있으므로 과거 대화나 사용자의 파일 다운로드를 요구하지 마. 연구 이전에 백업에서 더 새로운 실행결과가 있는지부터 확인해.

BASS repository: https://github.com/cosmosapjw-quantum/bass
재개 branch: research/bass-isotropy-checkpoint-recovery-20261018
연구 경로: research/bass_isotropy_response_20261018/
부모 PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
원본 native REI source: 0e25846433170d0f420c4cda44a0bedbf02cd177

Dropbox /BASS_BACKUPS와 Google Drive /BASS_BACKUPS에서 새로운 이 연구 결과를 확인하고, GitHub 최신 HEAD/PR와 대조해. README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, THEORY_KO.md, angular_balance.py, balance.rs, test_properties.py, CODEX_HANDOFF_KO.md 및 최신 게시 영수증을 읽어. 원래 아카이브의 과거 상태 문장보다 최신 실행 영수증을 우선하되 원본을 고치지 마.

완료된 사실: PR173은 실제 원래 native SourceLedger 58행과 5개 negative control을 로컬 Ubuntu에서 측정했다. 별개인 S2 등방 source 보정은 양의 KL 최소변경으로 P2=0을 강제하는 Python 코드이며, 15개 테스트가 복구 후 다시 통과했다. 원본 Rust 후보 balance.rs에는 5개 테스트가 작성돼 있지만 이 checkpoint에서 컴파일은 NOT_RUN이다. 새 native 결과가 발견되면 먼저 반영하고 이미 끝난 실행을 반복하지 마.

과학 scope는 non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H다. 보정 대상은 새 isotropic source의 angular quadrature이지 기존 광자장이나 물리적으로 비등방인 source가 아니다.

다음 S3의 첫 연구는 현재 P2=0 조건과 이후 collisionless shear response 정확도의 차이를 직접 유도·검산하는 것이다. Exact ray kernel R(d,mu)=sqrt(exp(2d)(1-mu^2)+exp(-4d)mu^2), D(d,mu)=[exp(-4d)mu^2-exp(2d)(1-mu^2)/2]/R에서 d=b(x)-b(u)다. D의 d=0 미분을 Legendre 다항식으로 분해하고, P2-only 보정의 잔류 P4가 응답에 어떤 영향을 주는지 평가해. 이 확장의 기호검산·캠페인·P4 알고리즘은 아직 완료되지 않았으므로 기존 PASS를 상속하지 마.

원래 source frame ray map와 양의 weights, reflection parity, 고정 spectral owner를 보존하고, angular refinement와 새로운 moment constraint를 따로 비교해. 지지점이 부족해 양의 moment 해가 없을 때는 정확한 feasibility 이유를 내고 음의 가중치·tolerance 완화로 우회하지 마. P2 또는 P4의 일치만으로 continuum angular accuracy나 실제 finite-bin source photon/energy ledger를 승인하지 마.

여기서 가능한 유도·Python 경량검증·코드 수정을 진행하고, native 실행이 필요하면 컴파일/작은 수정/실행만 남도록 코드를 준비해 push해. 매 단계 실제 백업·게시·DAG 상태를 남겨. 코딩은 테스트와 실제 종료코드를 기록하고 결과·수치적 오차·runtime·전송 문제를 구분해. NCP는 필요한 경우에만 인가된 경로로, 추가 worker16/RAM16GiB/disk4GiB/job1800초 상한과 기존 owner 작업을 보존하는 조건으로 써.

마지막에는 결과·근거 수준·남은 의무, GitHub commit/PR, Dropbox·Google Drive 재다운로드 해시와 함께 복사 가능한 NCP 및 다음 대화 handoff를 본문에 제공해. 이번 연구가 충분히 검증되기 전 REI native production이나 full EoR로 확대하지 마.
