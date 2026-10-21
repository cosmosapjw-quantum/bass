# 다음 대화 스레드에 복사할 재개문

아래 블록 전체를 새 대화에 붙여 넣어줘. 코드 실행용 전체 명령은
같은 경로의 CODEX_HANDOFF.md에 있어.

```text
$physmath-research-loop를 사용해 BASS/rei_bianchi ACCEL02의 후속 작업을 이어줘.
SciSpace, Exa, Wolfram은 다음 구체적 이론 의무에 필요할 때 실제로 사용해.

먼저 이 대화 이후 다른 대화/브랜치/repo/백업에 새 실행 결과가 생겼는지
delta를 확인해. 완료된 조사와 검증은 재사용하고, 새 결과의 source/input/
model lineage를 확인해 같은 물리 결과인지 구별해. 미게시·접근 불가 자료까지
전수 확인했다고 표현하지 마. Stage별 backup/publication/DAG 상태를 계속 남겨.

기준:
- BASS PR178: https://github.com/cosmosapjw-quantum/bass/pull/178
- REI PR215: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/215
- branch: research/rei-sigma-pi-native-moments-20261021
- path: research/rei_sigma_pi_native_moments_20261021
- 검증된 실행 소스 Stage B:
  BASS 7fe0e25a28c0e48110c522378e203ffb934cc504
  REI 231df3ab717dbc112f63b77953f64def08e9bcb5
- 이후 Stage C/최종 receipt commit은 같은 branch의 문서·delivery 보충이다.
  현재 정확한 published head와 backup은 delivery/를 먼저 읽어.

읽기 순서:
REPORT_KO.md, DAG.json, SCOPED_DECISION.json, CODEX_HANDOFF.md,
evidence/INDEPENDENT_REVIEW.json, delivery/FINAL_PUBLICATION.json,
delivery/STAGEC_BACKUP_VERIFIED.json. 이어서 실제 새 의무의 소스만 읽어.
원본 기준은 BASS176/REI213의 research/rei_sigma_pi_pilot_20261021이고,
ACCEL01은 BASS177/REI214의 research/rei_sigma_pi_acceleration_20261021이다.

기존 warm pilot은 729 cases, 243 groups PASS, 누락 0, history 47,385행 완료다.
matter/radiation pi_ab를 독립 설정했다. a=0.1999→0.2, non-tilted LRS,
L 8, source 8×8, massive fraction 0.1, mass/T 30의 conditional 결과다.
Half-contraction norm과 signed component를 사용하며 D_m+D_r를 먼저 더한
뒤 total norm을 취한다. 초기 total stress가 0이어도 다른 성분 진화로 이후
stress와 작은 shear가 생긴다는 원 관찰과 그림을 재사용한다.
완료 729나 상세 benchmark를 다시 돌리지 마.

ACCEL02에서 끝낸 것:
- 원 96×32 quadrature를 그대로 두고 16개 반사쌍으로 묶는 C++17 fused
  three-moment kernel, Neumaier 보상합, ctypes, 기존 exact cache 연결.
- 선택적 BackendSpec, 명시적 target build, 별도 source/binary identity,
  기존 shared_executor의 pending만 실행·부분 완료·재개.
- Wolfram으로 parity, ∂xJ0=-3J0-J1, ∂bJ0=-2J2, work=2sD 확인.
- 140 kernel점 최대 energy-scaled 오차 3.0017696087628955e-16;
  3 미분점 최대 잔차 3.730718793634552e-12; 고정 기준 모두 PASS.
- 5 original/native 쌍 각 2 step, 원 8 gate 및 signed 성분/work 비교 PASS.
- 기존 worker 검사 9 PASS, 실제 native worker 1 solve+같은 case 1 reuse.
- 1 compile, solver 합계 11회, benchmark 0, 원 729 재실행 0.
- fresh Astra 1회 독립 심사 PASS_SCOPED_LOCAL_NUMERICAL_EQUIVALENCE,
  차단 결함 0·수정 0. 새 scope 없이 심사나 기존 suite를 반복하지 마.

Local native backend ID:
b0508de09a21c9da3ef5564e2cb63359d6263d2e68b2527b12971ef7b2ff6845
Science context ID:
f5ab253bfd65a3af5b62dcc236cddb18e702b368b7e87e6213943617c1aab398
NCP의 새 compiler/library/receipt에 따라 backend ID가 달라질 수 있다.
그 자체를 물리적 FAIL로 해석하지 마.

이번 조사에서 새 C21M 98/98 NCP 및 125좌표 그림도 확인했지만 PR147
collisionless z20→4 별도 모형이다. C15 warm 729 증거와 합치지 마.
두 설명 문서의 run identity 불일치는 실제 raw identity와 분리해 기록했다.
CSV byte 차이는 LF/CRLF로 설명된다. 자세한 근거는 intake/에 있다.

NCP target은 64 CPU/128 GiB다. 이 대화의 실제 환경은 8 CPU/8 GiB였고,
현재 live NCP 여유량은 직접 관측하지 못했다. C21M의 과거 19:50:11 KST
receipt의 64 affinity CPU/61 worker/약 80.20 GiB available은 현재 할당이 아니다.
다른 세션이 돌고 있다는 이유로 중지하지 말고 실제 가용 자원에 맞춰 작업을 분할해.
numeric threads 1, production max workers 64를 상한으로 두고 기존 scheduler로
관측·admission해. 다른 작업의 프로세스나 tracked checkout을 변경하지 마.

바로 이어갈 실행:
1. 새 NCP 반환 결과가 있으면 먼저 수용·재사용 여부를 판단한다.
2. 없으면 CODEX_HANDOFF.md에 따라 기존 repo Git 객체의 세 research 경로를
   고유 실행 폴더로 export해 target-local compile과 작은 5 case 2 step 확인을
   수행할 수 있다. 새 clone/worktree나 공유 branch checkout은 필요 없다.
3. default 729 plan은 pending 0/no-work가 정상이다. 새 production sweep은
   사용자가 정한 case 범위를 명시적으로 받아 pending만 실행한다.
4. 원 729 고정 aggregator에 custom 2 step 결과를 넣지 말고, 새 grid용
   expected-case 집계/plot 일반화가 필요하면 별도 다음 단위로 계약을 고정한다.

남은 물리 범위: full EoR, 일반 non-LRS, full Q^a closure, 시간/radial/angular
수렴. 이번 kernel 140점 PASS를 이 범위의 증명으로 확대하지 마. measured speedup
또는 guaranteed SIMD도 주장하지 마.

매 새 단계에서 증거·DAG node·실제 게시 commit·실제 backup ACK를 함께 남겨.
최종 standalone ZIP에는 소스와 작은 검증 자료가 있고 원 47,385행 history 전체는
포함하지 않는다. history는 원 Stage 5 index/hash/locator로 복원한다.
Codex handoff와 다음 대화 재개문도 복사 가능한 형태로 갱신해.
```


## Final delivery status / 최종 전달 상태

ACCEL02의 과학·구현·검토·인계는 `SCOPED_COMPLETE`다. Stage C 본문은
BASS `f94bad85fc913a5be7478251bc85457e6fafdb98`,
REI `369fd5007f7236e2bbb22e1bbe8ff0f1ceee2d5c` content commit에 게시됐다.
기존 Stage B code pin과 고정 과학 계약은 그대로 유지한다.

Dropbox의 5,514,078-byte Stage C ZIP을 **한 번의 전체 GET**으로 내려받아
size·SHA256·Dropbox block hash·ZIP CRC·263개 exact member를 모두 확인했다.
실제 영수증은 `delivery/STAGEC_PUBLICATION.json`, `STAGEC_BACKUP.json`,
`STAGEC_BACKUP_VERIFIED.json`, `FINAL_PUBLICATION.json`에 있다.
Stage A/B는 각각 provider object·size 확인이며, 전체 GET 검증은 Stage C에
한 번 수행한 것으로 구분한다.

불변 ZIP은 자체 provider ACK보다 먼저 만들어졌다. 최종 영수증과 이 상태
보충은 뒤따르는 Git closeout commit에 기록한다. ZIP을 재생성하거나 자기
hash를 재귀적으로 넣지 않는다. 최종 영수증의 Git commit은 이 파일을 포함하는 commit으로 확인한다.
위 content commit은 과학·인계 본문의 게시점이며 실행 코드 pin과 구분한다.

남은 NCP target-local compile·자원 확인·명시된 pending 실행은 별도 후속
작업이다. 이번 단위의 실패나 미완료 과학 검증으로 계산하지 않는다.
