# NCP SSH 접속을 반영한 복사 가능한 인계 프롬프트

2026-10-21 KST 계약 변경: 접속 방식은 사용자 지정 SSH, 상태는 `SSH_AUTHORIZED_NOT_TESTED`다. 이번 편집에서 실제 연결·컴파일·계산은 하지 않았다. 다음 블록은 이후 실행 담당자에게 주는 지시다.

```text
$physmath-research-loop로 BASS의 완료된 S9/S10/S11/S12 증거를 재사용하라. 이번에는 아래 사용자 지정 SSH 경로로 NCP에 접속하고, 준비된 S12 17job 중 실제 미실행 부분만 이어라.

ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22

Repo: https://github.com/cosmosapjw-quantum/bass
Draft PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
접속 계약: NCP_ACCESS_CONTRACT.json
완료 S12 배송 기준 HEAD: 5718499408a121f32b3c755781c79e2167f9d6e7
완료 S12 배송 댓글: https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6303812301
새 접속 계약의 containing HEAD/readback은 PR174 최신 amendment 댓글과 actual Git ref에서 확인하라.

키 경로는 SSH를 실행하는 호스트의 기존 로컬 파일 경로다. 키 내용을 출력·복사·업로드하지 말고 기본 host-key 검증을 유지하라. 사용자에게 과거 대화·ZIP 다운로드·파일 첨부·키 업로드·사전 명령 실행을 요구하지 마라. Desktop Commander의 과거 quota/no-retry는 그 서비스의 이력으로 보존하되, 사용자가 명시적으로 승인한 이 SSH 경로의 금지로 해석하지 마라. 해당 서비스 재시도나 추측한 다른 접속 경로는 사용하지 마라.

먼저 최신 GitHub HEAD/댓글, 관련 branch와 접근 가능한 대화·Dropbox/Drive /BASS_BACKUPS에서 새 실제 결과를 read-only로 대조하라. Drive folder ID는1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y다. NCP_ACCESS_CONTRACT.json, README_KO.md, DAG.json, RETURN_TO_CHATGPT.json, PUBLICATION_CLOSEOUT.json, CLOUD_READBACK_KO.md, S12_RESULTS_KO.md 및 NEW_THREAD_HANDOFF_KO.md·CODEX_HANDOFF_KO.md 전체를 읽어라.

지정 SSH 접속 후 실제 host identity, affinity/cgroup CPU quota, 가용RAM/disk, 기존 owner 작업과 이미 존재하는 source/run receipt를 먼저 읽어라. 접속 또는 자원은 실제 관측 전까지 성공으로 쓰지 마라. 접근이 불가능하면 실제 SSH 원인을 기록하고 NOT_RUN을 유지하라.

Original REI owner: 0e25846433170d0f420c4cda44a0bedbf02cd177
Rust science source: f4cd0d53760783e6a58c3b0a98c64311ca489d28
C8 execution source: 8247645d04695bdbfa48eb2fe74757dacf7d2636
Result/review: fd8a9aafeaaf29afeab04e9d2876db087e90d24b
SCIENCE_BINDING SHA256: 061f9570d7d5254b97060da2599efdd95a5f993f1cbeb3d2791ed4551a6abf5f
DELIVERY_BINDING SHA256: e64930abc75d02e3b2b9d5b85a9c37e2f33e057f47c2474c1dec320d8fb3485a
JOB_TEMPLATE SHA256: 8c5725a8f71b36fcf13721fcf1bde76f6c1db066d59e873fbea113e7e464deb7

고정17job은 build1+새 extended history14+64pack serial/parallel 비교1+ensemble1이다. 봉인109파일과 입력·gate를 유지하라. CODEX_HANDOFF_KO.md의 단일 launch.py 명령을 실제 NCP 전용 경로에 적용하라. 사용자에게 선행 compile을 시키지 마라. matching PASS는 exact artifact/source/input/binary/dependency identity를 대조해 재사용하고 실패 raw는 보존하라. 완료된 옛 캠페인·short histories·native compile-only·자동 최적화 cycle을 재시작하지 마라.

NCP workers≤64/RAM≤128GiB는 요청 상한이다. 실제 affinity/quota/가용자원/owner load를 따라라. 전용 disk scope≤4GiB, job≤1800초, nested numeric thread1, 기존 owner 작업 보존. 최초 봉인 manifest의 width·경로·identity를 resume에서 유지하고 자원이 줄면 admission을 보류하라. Sandbox 상한16worker/16GiB를 유지하고 sandbox에서 ncp profile을 실행하지 마라.

Non-tilted axisymmetric Bianchi I,(-,+,+,+),a_perp=a exp(-b),a_parallel=a exp(2b),s=dot b,Sigma=sqrt(3)|s|/H를 유지하라. 새 명시적 등방 birth quadrature만 보정하고 기존 photon field·physical anisotropic stock·이전 birth weights·positive weights·reflection parity·source frame·고정 owner를 보존하라. 원 native16birth는 birth13 이후 fixed-support infeasibility로 제외한다. 음수 weights·tolerance 완화·임의 support 변경으로 우회하지 마라. P2/P4/P6 일치나5.369926725506957e-12의 제한 source-deposition 결과를 continuum/full native finite-bin/full spectral-history 완료로 확대하지 마라.

S10 closed2.973배/FLRW4.115배는 고정 workload 결과다. closed-small 이득 불확실성, changing n16/cohort2의0.9498173837599284배 회귀, S11 P246 bias 악화를 보존하라. 실제 MD14/native Einstein·shear shared-Q, evolving reactive full finite-bin, 더 넓은 angular 고차moment와 native/reactive/moving-event/donor-normalization tangent 의무는 남아 있다. REI production/full EoR/merge로 확대하지 마라.

매 단계 DAG·source/result/review·게시·백업/readback을 남겨라. 원 S10 양쪽 완료와 S12 Dropbox8ZIP+finalJSON 완료를 재사용하라. 새 Drive는 여전히 pending이며 불확정 write를 재시도하지 마라. 이 SSH 변경은 Drive 권한/상태 변경이 아니다. 17job 뒤에 새 자동 연구 cycle을 시작하지 마라.
```
