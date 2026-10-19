# 복사해서 사용할 Codex 인계

아래 블록 전체가 작업 지시다. 과거의 NOT_RUN 표시보다 최신 실제 source/receipt를 따른다.
Native source 게시 commit과 클라우드 객체는 PUBLICATION_CLOSEOUT.json의 후속 마감값으로 고정한다.

```text
$physmath-research-loop로 BASS 연구를 이어서 수행하라.
저장소 https://github.com/cosmosapjw-quantum/bass
Draft PR https://github.com/cosmosapjw-quantum/bass/pull/174
브랜치 research/bass-isotropy-checkpoint-recovery-20261018
연구 경로 research/bass_isotropy_response_20261018/

먼저 Dropbox /BASS_BACKUPS와 Google Drive /BASS_BACKUPS의 새 실행결과를 현재 GitHub HEAD/PR174 최신 댓글과 대조하라.
README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, S3_THEORY_KO.md,
S3_RESULTS_KO.md, NATIVE_ADAPTER_KO.md, 각 실행 receipt와 독립 review를 읽어라.
Drive ZIP 업로드 서비스가 멈춰 native-document Base64 carrier가 사용될 수 있다.
Carrier이면 manifest 순서로 텍스트를 직접 읽고 원 ZIP bytes/SHA를 복원·검증하라. 사용자에게 ZIP 다운로드를 시키지 마라.

고정 identity:
- 최초 검증 P2 구현 930406550ce6d4d1b2e87f016c5c18fba48c4ccd
- 2026-10-18 마감 a9c3e495fb460b3ec25bfa297b89c8fbd09c07fc
- 부모 PR173 4e2d1fa820d6f7baae1069b615fb82a08d53403b
- 원 REI source 0e25846433170d0f420c4cda44a0bedbf02cd177
- S2 Rust5 실행 게시 87149cdb673c250ccbb36dda5d43a38f0f7dd7b7
- S3 유도/P24 캠페인 게시 a7938ad51ad0fa324c5cb680dddb5fbfc7ed218e
- 검증된 native61-input SHA256 16a5efa08f31b9ef7cdabe5158f3e654586d25097be5f3aab19c88fdb6b23d23
- native raw JSONL SHA256 a552cfa04fe2bd1c4141191da24e9417da0121a05597f4daa121a51cbe7022ff

완료 증거를 이유 없이 반복하지 마라:
PR173 native58/negative5, 기존 Python15, 기존 Rust5, 새 Python14,
새 Rust P24 16, CLI valid1/negative7, Python/Rust 같은 입력43, 최종 reuse guards13,
native 새 테스트7/실제20행/runner regressions6, 초기 P2 preflight는 완료됐다.
S3는165rule 중146측정·19구체적 지지실패,1606response points를 저장했다.
이론 D의0~3차 전개·양의 반례·exact support1023개도 검산했다.
저장 측정 recovery의 F1/F2는 수정 및 독립 검토로 닫았다.
현재 native 범위는 sandbox에서 실제 실행됐으며 NCP 미실행 의무가 아니다.

물리: non-tilted axisymmetric Bianchi I, signature(-,+,+,+),
a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H.
새로 선언된 등방 source만 보정하라. 기존 광자장·물리적 비등방 source를 재가중/초기화하지 마라.
Reflection parity, 양의 weights, source frame 및 고정 spectral owner를 유지하라.
각 birth/cohort의 weights를 이후 수송에서 고정하라. Angular refinement와 moment 제약의 효과를 분리하라.
P2=P4=0이어도 P6/고차 응답은 남는다. Rank1 float ambiguity는 unresolved이며 음수weights/tolerance완화로 우회하지 마라.

다음 실제 미완료 의무 중 필요한 범위부터 진행하라:
(1) 저장 R,D kernel과 raw measurements에서 finite-d continuum error/고차 moments 및 source-age 합성 오차의 명확한 기준을 유도.
(2) exact rank1 지지의 입력 certificate와 실행 경로 설계.
(3) 고정 spectral owner의 source-panel/energy-bin refinement를 angular 변화와 분리하고 잔차5.369926725506957e-12를 설명.
(4) 검증된 birth cohorts를 합성한 history와 Einstein/shear feedback은 별도 후속 단계.
P6 제약 알고리즘, source-history 실행, spectral convergence가 이미 완료됐다고 가정하지 마라.

새 소스 변경 때문에 제한 native 재검증이 실제로 필요할 때만 준비된 runner를 사용하라.
연구 경로에서:
python3 run_native_adapter.py --out /absolute/new/bass_s3_native_output --workers 4 --timeout 1800
Runner는 고정57개 owner 파일을 자동 취득/검증하고 표준 라이브러리 Rust로 컴파일한다.
기존 checkout은 --rei-repo, 검증 가능한 staging은 --owner-root, compiler는 --rustc로 지정할 수 있다.
이미 완료된 같은20행을 인계 확인만을 위해 재실행하지 마라.

기존 owner 작업을 보존하고 추가workers16 / RAM16GiB / disk4GiB / 개별job1800초를 상한으로 둬라.
NCP가 필요한 새로운 작업은 여기서 코드·설정·입력·원래 gate를 완성한 뒤 compile/작은수정/실행만 남겨라.
명령·환경·source/commit·종료코드·stdout/stderr·자원·raw 결과·feasibility/수치/구현/환경 실패를 반환하고
단계별 DAG, GitHub 게시, 양쪽 백업 및 확인한 readback 범위를 갱신하라.
사용자에게 과거 대화, 파일 첨부, ZIP 다운로드, 사전 명령 실행을 요청하지 마라.
충분한 별도 검증 없이 REI production/full EoR/merge로 확대하지 마라.
```
