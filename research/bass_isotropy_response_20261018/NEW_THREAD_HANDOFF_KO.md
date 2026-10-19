# 새 대화 handoff — S9 고정 source와 미실행 8개 history

## 현재 source와 상태

```text
Repository: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
S8 original source: 4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613
S8 resume source: 2e6b4a150559b0bea52938896a901f6d438f3582
S8 final publication: 276172ca6cac9cf6b38561fdf9ba0103e1beb9cf
S8 final PR comment: 6268573867
S9 source publication: 이 문서의 containing commit; actual hash is recorded after push/readback.
S9 preregistration SHA256: 7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507
VigilODE source: a21d573980f66fe02891bd216153443b5352f921
VigilODE result publication: ac1cd2a4738c2441c92e5fdae5f70aba35e53544 (PR71)
Fixed REI spectral owner: 0e25846433170d0f420c4cda44a0bedbf02cd177
SourceID: MD14_Z002_FESC_BB50K_13P6_100_V1
Parent PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
```

S8의 최종 게시와 네 단계 이중백업은 완료했다. S9의 intake·이론·구현·독립 callback·개발 검증도 완료했다. **S9 실제8개 history는 NOTRUN**이며, 이 source/prereg의 GitHub 게시·Dropbox·Drive readback이 아직 필요하다. 게시되기 전 source hash나 실행 PASS를 만들어 쓰지 않는다.

처음 읽을 근거는 `README_KO.md`, `DAG.json`, `RETURN_TO_CHATGPT.json`, `PUBLICATION_CLOSEOUT.json`, `S9_THEORY_KO.md`, `S9_THEORY_PACKAGE_REVIEW_KO.md`, `s9_vigilode/HOWTO_KO.md`, `s9_vigilode/PREREGISTRATION.json`이다. 관련 새 결과는 `evidence_s9/intake/PUBLIC_RELATED_INTAKE.json`을 기준으로 이후 GitHub HEAD/PR·관련 backup 결과와 대조한다. 이 공개 receipt의 SHA는 `9bfb913a76b27949108b7e825053989f1c6f053872bb2bb256565ac2144e3c73`다. 사용자에게 과거 대화·ZIP다운로드·파일첨부·사전명령을 요청하지 않는다.

## 이미 완료한 검증과 적용 패키지

Rust adapter 계약검사5, num-dual 독립 단위검사9, runner guard10이 통과했다. 실제 callback은190query/38bank-state/5bank를 비교했고 max scaled JVP error는4.2848454134986243e-16이다. 원 AD cargo exit101은 rustdoc PATH 문제로 기록하고 별도 doctest0으로 해소했다. 이들을 단순 회복 목적으로 재실행하지 않는다.

실제 VigilODE `mf_into_ls` workspace와 `SmallProblem<4>`에 analytic RHS/JVP/Ft를 연결했다. Matrix-free arm은 [h,b,y], small arm은 [h,b,y,x]와 xprime=1이다. Fixed birth마다 새 immutable bank/driver/workspace로 재시작하고, b(u)는 실제 적분 상태에서 계산한다. 기존 S8 primal153행은 비교 전용이며 future birth geometry를 solver input에 넣지 않는다.

Exact P2/P4 admission은 num-rational0.4.2/num-bigint0.4.6/num-integer0.1.46를 사용하고 gate3/10^15를 유지한다. num-dual0.15.1은 독립 개발 checker에 적용했다. 각도 해상도와 moment constraint는 S9에서 바꾸지 않는다.

RUNNER01 stale binary attestation과 RUNNER02 RAW/observer failure receipt 문제는 [CLOSEOUT](evidence_s9/runner_review/CLOSEOUT.json)에서 닫혔다. Test-only prepare는 binary를 attest하지 않는다. 정확한 locked binary build 또는 명시적인 verified_prior_build만 campaign에서 수용한다. PROCESS를 먼저 저장하고 RAW/observer 실패를 분류하며 원 raw/log를 보존한다.

현재 준비 receipt는 `evidence_s9/vigilode_intake/guarded_preparation/PREPARATION_RETURN.json`, SHA `671818a3c3761594cb21bbbb933bd9ed6e5bf764fb7ceda720b45eee7e5c44f1`다. Binary SHA `69d884d67d0eb61bd6d4f52b5cfd079c07aa82c35a27272de608b93f16fb4823`, lib SHA `204d3fa9dd4a5ed8400410ff1035c4771e11d6ff50d5267a3756a740cf9b731b`를 보존한 genuine prior build이며 새 compile을 했다고 표시하지 않는다.

## 다음 실행

1. 이 고정 source/prereg을 게시하고 실제 commit/tree/blob을 readback한다.
2. Dropbox와 Google Drive 백업의 실제 identity를 검증한다.
3. 확인한 결과로 `evidence_s9/SOURCE_PUBLICATION_GATE.json`을 작성한다. Schema는 `BASS_S9_CAMPAIGN_AUTH_V1`이며 실제 source commit, prereg SHA, source_publication_readback/dropbox_readback/drive_readback를 담는다.
4. `s9_vigilode/campaign.py`의 고정8개 history를 새 output directory에서 실행한다. 두 solver arm 각각3개 tolerance의 closed history와 fine FLRW control1개다.
5. Raw·PROCESS·ASSESSMENT·CAMPAIGN_RETURN의 실제 성공/실패, DAG, source를 게시하고 이중백업한다.

현재 샌드박스에서 가능한 고정 캠페인은 이어서 실제 실행한다. NCP가 필요한 경우의 명령은 아래와 같으며, 기존 owner 작업을 보존하는 새 checkout/task directory를 사용한다.

```bash
python3 s9_vigilode/prepare.py \
  --work-dir /scratch/bass_s9_runtime \
  --jobs 2 --test --build

python3 s9_vigilode/campaign.py \
  --binary /scratch/bass_s9_runtime/target/debug/bass-s9-vigilode \
  --preparation-receipt /scratch/bass_s9_runtime/PREPARATION_RETURN.json \
  --publication-receipt evidence_s9/SOURCE_PUBLICATION_GATE.json \
  --output-dir /scratch/bass_s9_results
```

명령의 cwd는 BASS lane이다. 기존 검증된 source/vendor를 재사용하는 옵션, compiler 선택, build receipt reuse 및 결과 읽기는 HOWTO를 따른다. 동일 output 디렉터리를 덮어쓰지 않는다. 변경된 source는 새 prereg/source 게시 후 필요한 입력만 실행한다.

## 보존하는 결과와 미해결 의무

S8 tangent10/10gatePASS·원 serialization exit1·기존7+gauge1 구조를 보존한다. Native18attempt/17measured/n2566PASS/낮은해상도8FAIL/STRICT_INTERIOR precision1FAIL도 구분한다. S6 rate38/344FAIL·44/238constraint악화, S7 support·exact moment 실패를 삭제하지 않는다.

Non-tilted axisymmetric Bianchi I; (-,+,+,+); a_perp=a exp(-b); a_parallel=a exp(2b); s=dot b; Sigma=sqrt(3)|s|/H. 새 isotropic birth quadrature만 보정하고 기존 photon·physical anisotropic stock을 초기화하지 않는다. 양의 weights/reflection/source frame/fixed spectral owner를 유지한다. Feasibility와 numerical precision을 구분하고 음의 weights·tolerance완화·oracle birth b로 우회하지 않는다.

추가worker<=16, RAM16GiB, disk4GiB, 각job1800초; 기본 campaign worker1/build2. Solver-local JVP는 full parameter tangent의 검증과 별개이며, continuum angular accuracy·native finite-bin/history 보존·실제 MD14 에너지 공급/Einstein feedback·full reactive chemistry는 후속 의무다. REI production/full EoR/merge를 자동 승인하지 않는다. Final에는 실제 source/commit/PR, 실패 종류, 두 cloud readback 범위와 복사 가능한 인계를 본문에 출력한다.
