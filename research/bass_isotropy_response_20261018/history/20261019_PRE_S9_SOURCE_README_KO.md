# BASS isotropy / shear response — S8 완료, S9 연계 연구 시작

[S8 실제 결과](S8_RESULTS_KO.md) · [전체 tangent](S8_TANGENT_RESULTS_KO.md) · [native refinement](S8_NATIVE_REFINEMENT_KO.md) · [DAG](DAG.json) · [RETURN](RETURN_TO_CHATGPT.json) · [Codex 인계](CODEX_HANDOFF_KO.md)

## 현재 결과

S8의 닫힌 manufactured donor 모형에서 전체 출생 기억 tangent를 실제 검증했다. 계획된 8개 적분은 원래 7개 이력의 재사용과 아직 실행되지 않았던 gauge 1개로 완료했고 최종 10개 gate가 통과했다. 원래 JSON 직렬화 exit1은 별도 실패 기록으로 보존했다. Richardson joint(h,b,y) 최대 오차는 1.0230572e-10, birth geometry·direction·weight 항을 각각 생략한 3개 control은 모두 거부됐다.

Native 새 birth의 angular grid를 GL64/128/256으로 세밀하게 하고 각 grid에서 prior/P2/P2P4를 비교했다. 18개 입력 중17개를 측정했고 n256의6개 target이 모두1e-6를 만족했다. 낮은 해상도의8개 목표 미달과 b0=0.9,n64,P2P4의 STRICT_INTERIOR 지지에서 발생한 INNER_P2_PRECISION_LIMIT 1개를 유지한다. 이 수치 실패를 support infeasibility라고 부르지 않는다.

원 REI spectral owner57파일과 기존 n32 photon stock을 보존했다. 새 moment matching, 이 표본의 angular accuracy, native ledger, full reactive spectral/history 보존은 서로 다른 판정이다.

## Source와 게시

- Repository: https://github.com/cosmosapjw-quantum/bass
- Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
- Branch: research/bass-isotropy-checkpoint-recovery-20261018
- S8 original source/prereg: 4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613
- S8 serializer recovery source/prereg: 2e6b4a150559b0bea52938896a901f6d438f3582
- Final S8 metadata identity: 이 문서를 담은 commit과 PR174의 게시 후 closeout comment.
- Fixed spectral owner: cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177

S2의 원 Rust5테스트, S3 유도·양의 P2/P4 알고리즘·캠페인, native adapter, S6와S7의 실제 실행은 완료 증거를 재사용했다. [이전 README](history/20261019_PRE_S8_FINAL_README_KO.md)에 옛 단계의 설명을 그대로 보존했다.

## 다음 사용자가 요청한 작업

S9에서는 관련 GitHub와 cloud backup에서 새 실행결과를 먼저 확인한다. 특히 cosmosapjw-quantum/vigilode의 현재 source와 최신 benchmark를 실제 읽고, 현재 문제에 유용한 Rust package/API를 적용하는 코드와 경량 비교를 준비한다. 새 S9 실행은 별도 사전등록·게시·백업 순서로 기록한다. S8 수치 실패나 미실행 native full feedback를 완료했다고 가정하지 않는다.

## 고정 계약

Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H. 새 명시적 isotropic birth angular quadrature만 보정한다. 양의 weights, reflection parity, source frame을 지키고 기존 physical anisotropic photon stock을 초기화하지 않는다. 양의 해가 없는 support는 witness를 남긴다. 음의 weights나 tolerance 완화로 우회하지 않는다.

추가 worker16, RAM16GiB, disk4GiB, 각 job1800초가 상한이다. 기존 owner 작업을 보존하고 REI production/full EoR/merge를 자동 승인하지 않는다. S8 범위는 샌드박스에서 실제 완료했고 NCP 실행은 필요하지 않았다. 새 관련 결과를 확인하기 위해 사용자에게 과거 대화·ZIP·첨부·사전 명령을 요청하지 않는다.

![S8 요약](evidence_s8/figures/run01/S8_SUMMARY_180mm.png)
