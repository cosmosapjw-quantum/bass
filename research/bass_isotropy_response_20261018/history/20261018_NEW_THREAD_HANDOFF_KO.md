# 새 ChatGPT 대화: BASS PR174 이후 연구 재개

$physmath-research-loop로 BASS 이론 연구와 샌드박스 경량 코딩을 이어서 수행해줘. 사용자에게 과거 대화, ZIP 다운로드, 첨부나 사전 명령 실행을 요구하지 마.

Repository: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
검증된 구현 commit: 930406550ce6d4d1b2e87f016c5c18fba48c4ccd
연구 폴더: research/bass_isotropy_response_20261018/
부모 PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
원본 REI source: 0e25846433170d0f420c4cda44a0bedbf02cd177

연구 전에 Dropbox /BASS_BACKUPS와 Google Drive /BASS_BACKUPS의 새 결과를 확인하고 GitHub 최신 HEAD/PR와 대조해. README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, THEORY_KO.md, angular_balance.py, balance.rs, test_properties.py와 최신 PR 댓글을 읽어. 원래 아카이브의 과거 상태는 보존하되 최신 실제 실행 영수증을 상태 기준으로 사용해.

완료: PR173은 원래 native SourceLedger58행과 5개 negative control을 사용자 Ubuntu에서 실행했다. 별개인 P2-only KL source 보정은 Python15개 테스트가 통과했다. PR174 게시와 기존 양쪽 클라우드의 28개 payload readback은 완료됐다. 미완료: 새 balance.rs의 5개 테스트 실행, P4/후속 전단응답 연구, 보정된 native source 도입. 새 native 결과가 있으면 먼저 반영하고 이미 완료한 연구·실행을 반복하지 마.

물리 scope는 non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H다. 보정 대상은 새 isotropic source의 양의 angular quadrature뿐이며 기존 광자장이나 물리적으로 anisotropic인 source를 초기화하지 않아.

다음 S3의 첫 작업은 P2=0과 이후 collisionless shear response 정확도가 다른 조건인지 직접 유도·검산하는 것이다. R(d,mu)=sqrt(exp(2d)(1-mu^2)+exp(-4d)mu^2), D(d,mu)=[exp(-4d)mu^2-exp(2d)(1-mu^2)/2]/R, d=b(x)-b(u)에서 d=0 미분을 Legendre 다항식으로 전개하고 잔류 P4의 영향을 독립적으로 확인해. 이 유도·수치 캠페인·P4-constrained 알고리즘이 이미 검증됐다고 가정하지 마.

양의 weights, reflection parity, source frame 및 고정 spectral owner를 보존하고 angular refinement와 moment constraint를 따로 시험해. 양의 해가 없는 지지는 구체적인 feasibility 실패로 남기며 음의 weights나 tolerance 완화로 우회하지 마. P2/P4 일치만으로 continuum accuracy 또는 native finite-bin photon/energy 보존을 승인하지 마.

여기서 가능한 유도·코드·경량 테스트를 직접 완료하고 매 단계 실제 백업·게시·DAG 진척을 남겨. 네이티브 계산이 필요하면 NCP에는 컴파일·작은 수정·실행만 남도록 준비해 push해. 기존 owner 작업은 보존하고 추가 worker16/RAM16GiB/disk4GiB/job1800초를 상한으로 둬. 마지막에는 실제 결과, 실패 종류, 남은 의무, 해시·PR과 복사 가능한 Codex/NCP 및 새 대화 handoff를 본문에 제공해. REI production이나 full EoR로 자동 확대하지 마.
