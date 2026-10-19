# 새 대화 handoff — S8 실제 완료와 S9 사용자 요청

## 먼저 읽을 상태

이 문서를 담은 commit, PR174의 최신 HEAD/comments, 관련 GitHub와 Dropbox/Google Drive의 BASS_BACKUPS 및 관련 결과 폴더를 대조한다. 새 실행결과를 발견하면 우선 반영하고 이미 완료한 입력을 단순 복구 목적으로 재실행하지 않는다. 사용자에게 과거 대화·ZIP다운로드·파일첨부·사전명령을 요청하지 않는다.

```text
Repository: https://github.com/cosmosapjw-quantum/bass
PR: https://github.com/cosmosapjw-quantum/bass/pull/174 (draft/unmerged)
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
S8 source/prereg: 4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613
S8 resume source/prereg: 2e6b4a150559b0bea52938896a901f6d438f3582
Fixed REI source: cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177
SourceID: MD14_Z002_FESC_BB50K_13P6_100_V1
Original implementation: 930406550ce6d4d1b2e87f016c5c18fba48c4ccd
Original closeout: a9c3e495fb460b3ec25bfa297b89c8fbd09c07fc
Parent PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
```

## 이미 완료된 작업

S2 Rust5, S3 P2/P4 유도·양의 projection·반례·수치캠페인, native adapter, S6와S7의 제한된 실제 실행은 재사용한다. S6 rate38/344FAIL과44/238constraint악화, S7 support 및 원 exact momentFAIL은 역사로 보존한다.

S8은 전체 초기 signed-shear tangent를 실제8개 적분으로 검증해 최종10/10gatePASS했다. 원래7개 raw생성 뒤 numpy.bool 직렬화에서 exit1; source/raw/failure를 보존하고 별도2e6복구로 gauge1개만 실행했다. Historical rerun0. Richardsonjoint1.0230572e-10; birth kernel-shift, mu_b, alpha_b 생략control3/3거부. LinearizedHamiltonian1.0489192e-14. 기존 stock hash불변.

Native GL64/128/256 ×prior/P2/P24 ×b0=.6/.9를 실제18개 시도해17측정, n2566개targetPASS, 낮은해상도8개targetFAIL, b9_n64_P24의INNER_P2_PRECISION_LIMIT 1개가 있다. 이 지지는STRICT_INTERIOR이며 음의해/허용오차완화없이실패를남겼다. 기존n32stock은원별도block을보존하고 새gridblock을합산했다. 고정 owner57파일불변. ActualMD14energy-supply/Einsteinfeedback와fullreactivehistory는여전히미실행이다.

주요 입력:

```text
README_KO.md
DAG.json
RETURN_TO_CHATGPT.json
PUBLICATION_CLOSEOUT.json
THEORY_KO.md
angular_balance.py
balance.rs
test_properties.py
NEW_THREAD_HANDOFF_KO.md
S8_RESULTS_KO.md
S8_TANGENT_THEORY_KO.md
S8_TANGENT_RESULTS_KO.md
S8_NATIVE_REFINEMENT_KO.md
evidence_s8_tangent/resume_r2/RETURN_S8_TANGENT_R2.json
evidence_s8_native/run01/RETURN_NATIVE_ANGULAR_REFINEMENT.json
evidence_s8/figures/run01/FIGURE_AUDIT08_07.json
delivery/s8/S8_STAGE0_CLOUD_READBACK.json
delivery/s8/S8_STAGE1_CLOUD_READBACK.json
delivery/s8/S8_STAGE2_CLOUD_READBACK.json
```

## S9의 현재 사용자 요청과 실행 순서

physmath-research-loop1.0.0의 이론10단계·코딩10단계를 적용한다. S8 과학 실행의 기존1.3.0provenance를 바꾸지 않는다. 새 관련 backup/GitHub intake가 우선이며, cosmosapjw-quantum/vigilode의 최신 실제 implementation·PR·benchmark를 읽는다. Rust의 특화 package를 조사하고 실제BASS문제에적용하는코드·경량검증까지진행한다. 새결과를확인하기전solver선택이나benchmarkPASS를가정하지않는다.

기존 owner checkout/branch를 건드리지 않고 격리된 새 작업 경로에서 코드·사전등록을 준비한다. Native source와 spectral owner는 위 고정 commit을 유지한다. New-birth snapshot과 기존 photon stock의 변화가 혼합되지 않도록 API를 설계한다. 시간의존RHS라면 analytic JVP뿐 아니라 explicit time partial도 확인한다. 적분기의 cache는 새 birth가 생기는 불연속에서 유효한지 검증한다. NCP에는 준비된 code의 compile/작은 수정/실행만 남도록 이곳에서 가능한 구현과 검증을 완료해push한다.

S8만을 완료하기 위한 NCP의무는 없다. 기존native실행을 독립재현할 필요가 실제생겼을 때에만 아래 준비된명령을 사용할 수 있다. 결과를덮어쓰지않는새out을지정한다. JSONreceipt의integrityfalse/finestaccuracytrue/precisionfailure를 함께읽고exitcode를전체PASS로바꾸지않는다.

```bash
python3 research/bass_isotropy_response_20261018/run_s8_native_refinement.py \
  --prereg research/bass_isotropy_response_20261018/evidence_s8_native/PREREGISTRATION.json \
  --publication-receipt research/bass_isotropy_response_20261018/delivery/s8/NATIVE_PUBLICATION.json \
  --out /tmp/bass_s8_native_independent_reproduction \
  --workers 4 --timeout 1800
```

원 owner를검증가능한로컬복사에서읽으려면 --owner-root, 기존git소유자작업을읽기만하려면 --rei-repo, compiler를명시하려면 --rustc를사용한다. 의존성준비가필요하면현재manifest를검증한다. Source변경시옛prereg의hashgate실패는정상이며새계약과게시후변경입력만실행한다.

## 유지할 물리·자원·게시 계약

```text
non-tilted axisymmetric Bianchi I; signature(-,+,+,+)
a_perp=a exp(-b); a_parallel=a exp(2b); s=dot b
Sigma=sqrt(3)|s|/H
새 명시적 isotropic birth angular quadrature만 보정
기존 photon/physical anisotropic stock 초기화·재보정 금지
positiveweights/reflection/sourceframe/fixedspectralowner 유지
support infeasibility와 numericalprecision failure를 구분
음의weights와 tolerance완화로 우회 금지
P2/P4일치만으로 continuum/nativefinite-bin/history 승인 금지
추가workers<=16; RAM16GiB; disk4GiB; 각job1800초
기존owner작업보존; REIproduction/fullEoR/merge 자동확대 금지
```

매단계 결과·source·실패·DAG·게시·두cloudidentity를 남긴다. GoogleDrive는전체rawZIP의bytes/SHA/CRC/manifest/Gitblobreadback, Dropbox는freshproviderwholeobjecthash/size의실제증거범위를구분한다. FinalS8postuploadreceipt는PRcomment와다음S9checkpoint에보존한다. 최신HEAD는이문서의containingcommit과PRreadback으로확인하고과학source4508/복구2e6과구별한다.
