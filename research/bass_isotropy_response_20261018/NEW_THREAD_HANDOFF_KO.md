# 새 대화용 복사 인계

```text
$physmath-research-loop를 사용해 BASS의 다음 이론 연구와 샌드박스 경량 코딩을 이어서 수행해줘.
과거 대화·ZIP 다운로드·파일 첨부·사전 명령 실행을 사용자에게 요청하지 마.

Repo https://github.com/cosmosapjw-quantum/bass
Draft PR174 https://github.com/cosmosapjw-quantum/bass/pull/174
Branch research/bass-isotropy-checkpoint-recovery-20261018
Path research/bass_isotropy_response_20261018/
원 REI owner 0e25846433170d0f420c4cda44a0bedbf02cd177
부모 PR173 4e2d1fa820d6f7baae1069b615fb82a08d53403b
과거 P2 구현930406550ce6d4d1b2e87f016c5c18fba48c4ccd, 과거 마감a9c3e495fb460b3ec25bfa297b89c8fbd09c07fc.
새 S2 게시87149cdb673c250ccbb36dda5d43a38f0f7dd7b7, 새 S3 게시a7938ad51ad0fa324c5cb680dddb5fbfc7ed218e.
최신 native source 및 최종 마감 commit은 현재PR와 PUBLICATION_CLOSEOUT.json/최신댓글에서 직접 확정해.
검증된 native61-input SHA256=16a5efa08f31b9ef7cdabe5158f3e654586d25097be5f3aab19c88fdb6b23d23.

먼저 Dropbox /BASS_BACKUPS 및 Google Drive /BASS_BACKUPS에서 새 실행결과를 읽고 GitHub HEAD/PR와 대조해.
Drive에는 binary upload 서비스 정지에 대한 정확한 ZIP bytes의 Base64 문서 carrier가 있을 수 있어.
그 경우 문서의 manifest대로 직접 읽고 decode/SHA 검증해. 사용자에게 파일 전달을 요청하지 마.
README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json,
THEORY_KO.md, S3_THEORY_KO.md, S3_RESULTS_KO.md, NATIVE_ADAPTER_KO.md,
CODEX_HANDOFF_KO.md, 실제 source/receipt/independent review를 읽어.

완료: 기존 Python15 및 PR173 native58/negative5 재사용; 원 balance.rs5실행PASS;
새 S3 Python14/Rust16/CLI valid1+negative7/동일입력43/최종reuse guards13 PASS;
165rule 중146측정과19실제support실패,1606response points;
D의0~3차 Legendre 유도와1023 exact-support검산;
원 owner에 새 native source adapter를 실제 연결한 tests7+20측정행+runner6 PASS.
독립 Python/Rust/native 검토 완료. NCP는 실행하지 않았으며 현재 native 검증은 sandbox에서 끝났어.
새 결과가 없거나 관련 source가 바뀌지 않았다면 이미 끝난 캠페인을 반복하지 마.

핵심 유도: F=<R>, G=<D>, A=G/F, M_l=<P_l>.
D'(0)=-(8/5)P0-(10/7)P2+(36/35)P4.
M2=0이면 A'(0)=-8/5+(36/35)M4.
M2=M4=0이어도 A''(0)=16/7+(216/77)M6.
P4 제약과 angular refinement는 서로 다른 효과이며 continuum accuracy를 자동 보증하지 않아.
Native에서는 birth-energy 정규화 G'를 측정했으며 ledger와 source-cell energy 진단을 별도로 확인했어.

미완료: finite-d continuum angular error/고차 moments, exact rank1의 실행 certificate,
고정 spectral owner refinement 및 에너지 상대차5.369926725506957e-12 설명,
실제 source-age 합성과 coupled Einstein/shear feedback. P6 제약이나 history 실행이 완료됐다고 가정하지 마.

Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b),
s=dot b, Sigma=sqrt(3)|s|/H를 유지해. 새 명시적 등방 source angular quadrature만 보정하고
old photons 및 물리적 anisotropic source를 초기화/재가중하지 마. Birth weights, 양의weights,
reflection parity, source frame, 고정spectral owner를 유지해. 불가능한 support는 구체적 실패로 남기고
음의weights·허용오차 완화로 우회하지 마. P2/P4 일치만으로 전체 native finite-bin 보존을 승인하지 마.

가능한 유도·코드·경량 테스트는 여기서 수행하고 단계별 DAG·게시·이중 백업/readback을 남겨.
새 native 실행이 필요하면 NCP에는 compile/작은수정/실행만 남겨. 기존 owner 작업을 보존하고
추가worker16 / RAM16GiB / disk4GiB / 개별job1800초 상한을 지켜.
최종본문에 실제결과·실패종류·남은의무·source/commit/PR·cloudreadback과 갱신한 두 복사prompt를 출력해.
충분한 별도 검증 없이 REI production/full EoR/merge로 확대하지 마.
```
