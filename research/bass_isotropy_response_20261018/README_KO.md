# BASS S3: 탄생 등방성과 이후 전단 응답의 분리

2026-10-19 S3 직접 유도·양의 P2/P4 구현·165 rule 캠페인·43개 Python/Rust 비교가 완료됐다.
P2=0 이후 A'(0)=-8/5+(36/35)M4이며, P2=P4=0이어도 A''(0)=16/7+(216/77)M6다.
전체 유도는 [S3_THEORY_KO.md](S3_THEORY_KO.md), 실제 결과와 실패는 [S3_RESULTS_KO.md](S3_RESULTS_KO.md)에 있다.

기존 balance.rs의 작성된5개 테스트를 원본 무변경으로 실제 실행해 통과했고 S2 commit은
`87149cdb673c250ccbb36dda5d43a38f0f7dd7b7`이다. 기존 Python15 및 PR173 native58/negative5는 재사용했다.
S3 새 Python14, Rust16, CLI negative7, 동일-input43, 최종 reuse-guard13이 통과했다.

새 native adapter도 sandbox에서7개 테스트·20행을 실행했다. 독립 검토와 별도 게시를 이어서 마감한다.
현재 상태는 DAG/RETURN_TO_CHATGPT를 따르며, publication receipts는 각 단계 게시·백업 뒤 추가한다.
원본 과거 문서는 history/에 보존한다.

non-tilted axisymmetric Bianchi I, signature(-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b),
s=dot b, Sigma=sqrt(3)|s|/H를 유지한다. 새 명시적 등방 source만 보정하며, 원 spectral owner와
기존 photon stock/물리적 비등방 source를 보존한다. Continuum/production/full EoR 승인은 없다.
