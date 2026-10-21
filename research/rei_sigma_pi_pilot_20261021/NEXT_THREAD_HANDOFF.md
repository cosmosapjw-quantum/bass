# 다음 대화 스레드 handoff

**2026-10-21 상태: 기존 81-case pilot과 독립 matter/radiation 729-case pilot 모두 완료.**
신규 pilot은 243 groups 모두 PASS, 729 unique cases, 누락 0, 실제 47,385 history rows다.
아래 블록을 다음 대화에 그대로 붙여 넣으면 된다. 최종 결과 게시 commit과 신규 결과
백업 상태는 PR의 최신 branch head 및 최종 delivery receipt에서 확인한다.

```text
$physmath-research-loop를 이어서 사용해줘. 최신 요청은 matter와 radiation의
비등방 응력 pi_ab를 독립적으로 다루는 것이야. 기존 81-case pilot은 완료했고,
새 (Sigma, Pi_m, Pi_r) 독립 pilot 729 cases도 실제로 완료했어.
완료 데이터를 보존하면서 결과 해석과 남은 연구에 기여해줘.
이미 조사한 내용을 처음부터 반복하거나 완료한 계산을 CPU 채우기용으로 다시 돌리지 말아줘.
상세 성능 benchmark는 필요 없어. 다른 Codex 작업이 돌아가도 실제 가용 자원에서 계속 분담해줘.

기준 자료:
- BASS PR176: https://github.com/cosmosapjw-quantum/bass/pull/176
- REI PR213: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/213
- 공통 branch: research/rei-sigma-pi-pilot-20261021
- 공통 경로: research/rei_sigma_pi_pilot_20261021
- 새 split 실행 source: BASS 82372ed8db68085868603d4267a630ed9cde6abb
- 기존 81-case 실행 source: BASS 003550e04e8d6c316be422f8ac6a15df284e49a5
- 불변 물리 owner: REI 80825585f9fe31d2ee0d5af545ada3fa1f52be72 (PR141 C15)
- 실행 source commit과 최종 결과 게시 commit은 구별하고, 최신 PR/receipt를 실제로 읽어줘.

현재 상태:
- PILOT01: 81 cases, 27 groups, 64 steps, 초기 포함 5,265 history rows 완료.
  results/pilot81_v2/aggregate에 실제 CSV/JSON, overview/response 그림과 provenance가 있어.
  최초 NumPy bool export 실패는 보존하고, export 수정 후 v2에서 완료했어.
- PILOT02도 완료: 각 signed 축 9점의 9 x 9 x 9 = 729 unique cases,
  3 cases/group, 243 groups 모두 PASS, 64 steps, 실제 history rows 47,385야.
  Aggregate status는 COMPLETE이고 missing cases는 0이야.
- 첫 group 3 cases를 먼저 완료했고, 전체 실행은 242 PASS + 1 SKIPPED_PASS로 끝났어.
- results/split729/aggregate에 CSV/summary와 sigma_pi_split_slices 및
  sigma_pi_split_components의 PNG/PDF/provenance가 있어.
- 완료한 scope와 bound source/input을 보존하고 81 또는 729 cases를 다시 돌리지 말아줘.
- 기존 S12 NCP 17 jobs 역시 완료됐어. 오래된 NOT_RUN으로 되돌리지 말아줘.

물리 정의:
- non-tilted LRS Bianchi I, sigma_ab = diag(-s,-s,2s), s = db/dt.
- 기본 half-contraction norm: Sigma_h = sqrt(3)|s|/H,
  Pi_h = (8 pi G/c^2)|D|/(sqrt(3)H^2), D = P_parallel - P_perp.
- C15.KAPPA = 8 pi G/(3c^2)이므로 위 Pi에는 3*C15.KAPPA를 사용해.
  Frobenius norm도 따로 저장하며 half norm의 sqrt(2)배야.
- matter D_m = Pi_massive. 이 owner에서 gas와 나머지 cold matter는 isotropic이라 pi_ab=0이야.
- radiation D_r = Pi_gamma + Pi_nu + Pi_UV. nu는 massless이고 UV는 현재 상태에서 계산해.
- D_total = D_m + D_r를 먼저 더한 다음 norm을 취해. Pi_m + Pi_r를 total로 쓰면 안 돼.
- alpha_m과 alpha_r는 독립이고, gamma와 nu만 같은 alpha_r를 공유해.
  두 초기 P2 family는 각각 -1 <= alpha <= 2의 양의 분포야.
- 초기 cancellation 81 cases 중 72개는 0이 아닌 반대 부호 응력의 상쇄이고,
  9개는 두 성분이 모두 0인 경우야. 초기 상쇄가 이후에도 유지된다고 가정하지 않아.
- signed components, work=2sD, 작은 raw residual을 보존하고,
  Pi<3e-13의 orientation은 각 성분과 total별로 unresolved라고 표시해.

실제 cancellation 결과:
- initial signed Sigma=0, Pi_m=+4e-4, Pi_r=-4e-4인 split_0079에서
  final signed Sigma=-4.795410954946239e-11,
  final signed Pi_total=-1.9176362919464883e-7이야.
- 반대 부호 split_0078에서는 각각 +4.79541095518866e-11,
  +1.917636292007428e-7이야.
- 초기 component norm 합은 약 8e-4지만 tensor total은 nominally 0이야.
  약 1e-18의 실제 raw residual은 보존했어.
- 성분의 다른 진화로 초기 상쇄가 깨지는 조건부 응답이야.
  full convergence나 thermochemical detection까지 입증한 것으로 해석하지 말아줘.

범위와 해석:
- a=0.1999 -> 0.2, mean z=4.00250125 -> 4의 짧은 warm conditional pilot이야.
- 초기 T=12,000 K, x_HII=0.4, x_HeII=0.5; massive fraction=0.1, m/T=30,
  L=8, native 8x8 source, 모든 물리 stress/Thomson/compression/feedback on이야.
- 기존 Einstein shear, gamma/nu Boltzmann, massive Vlasov, H/He owner를 재사용해.
- full stellar/emitter 및 escape Q^a closure, cold z20-to4, 일반 비-LRS 방향,
  시간/각도/스펙트럼 수렴은 아직 열려 있어. full-EoR 결과로 부르지 말아줘.
- warm 10,000~24,000 K rate table을 8 K로 외삽하지 말아줘.

HPC 운영:
- 현재 실제 실행은 ChatGPT sandbox의 8 CPU / 8 GiB야. 이 lane의 NCP 실행 주장은 없어.
- NCP target 64 CPU / 128 GiB profile은 실제 affinity/cgroup/spare capacity를 따르도록 돼 있어.
- numerical threads=1, group timeout<=1,800s, scope disk 4 GiB admission cap과
  filesystem free 256 MiB reserve가 있어. 실행 중 출력의 hard quota는 아니야.
- 다른 process를 종료하거나 타 세션 working tree/checkout을 바꾸지 말아줘.
- 기존 승인 SSH: ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p22
  이 sandbox에는 key가 없어. 새 executor의 실제 접근 가능성을 확인하되 key를 출력/복사하지 말아줘.
- 다른 host의 절대경로/toolchain 때문에 실행 manifest를 바로 재사용할 수는 없어.
  source/input hash, 완료 receipt와 실제 pending cases를 확인하는 admission migration부터 해줘.
  경로를 바꿨다는 이유로 완료 cases를 신규 미완료로 취급하지 말아줘.
- 완료 데이터의 분석과 그림 재생성에는 NCP 접속이나 재적분이 필요 없어.

게시와 백업:
- 각 단계의 DAG, source/result commit, PR 게시와 backup receipt를 갱신해줘.
- draft PR 게시와 기존 /BASS_BACKUPS 백업 흐름은 승인돼 있어. merge는 하지 않았어.
- delivery/STAGE3_DELIVERY.json: 기존 81-case 백업 복구 완료.
  독립 4개 PART ZIP의 remote full GET, SHA256, provider block hash, CRC와
  454 payload files가 검증됐어. outer index는 ACK/metadata만 확인했어.
- 최초 Stage3 unsuffixed ZIP은 invalid이며 복원에 쓰면 안 돼. 원인은 UNKNOWN이고
  실패 증거로 보존했어. 검증된 4개 PART ZIP을 사용해줘.
- delivery/STAGE4_DELIVERY.json: 새 split source 8 files는 upload ACK와 원격 metadata
  확인까지 완료했어. 로컬 CRC/hash는 PASS지만 remote full GET은 하지 않았어.
- Stage3과 Stage4는 새 729-case runtime 결과를 포함하지 않아. 신규 결과의 최종
  게시·백업 receipt를 따로 확인하고, ACK와 full remote verification을 구분해줘.
- 조사 범위는 6개 repo의 branch/PR catalog와 관련 source/result/backup이야.
  Personal Context service error와 Drive atomic 1,000-item cap이 있어
  모든 대화와 계정 전체를 완전 조사했다고 주장하지 않았어.

먼저 REPORT_KO.md, RESEARCH_DECISIONS.md, DAG.json, CODEX_HANDOFF.md,
SPLIT_CONTRACT.json, README_SPLIT.md, physics/, evidence/, delivery/를 읽어줘.
완료한 729-case coverage와 original gates는 실제 summary/CSV에서 확인했어.
최종 독립 결과 검토, hash 기록, component/cancellation 그림, 신규 결과의 게시·백업
receipt를 함께 확인하고 남은 작업에 기여해줘. 이미 완료된 계산이나 게시를 반복하지 말아줘.
```

## 이미 있는 데이터로 그림 다시 만들기

연구 경로에서 실행한다. Split aggregate는 이미 생성돼 있다. 기존 그림을 보존하려면
--out을 새로운 분석 경로로 지정한다.

```bash
python3 split_plot.py \
  --aggregate results/split729/aggregate \
  --out results/split729/aggregate/sigma_pi_split

python3 plot_pilot.py \
  --aggregate results/pilot81_v2/aggregate --response \
  --out results/pilot81_v2/aggregate/sigma_pi_response
```

위 명령은 기존 CSV에서 그림을 만들며 새로운 물리 적분을 실행하지 않는다.
압축 배포본은 `history.csv.gz`를 먼저 원래 `history.csv`로 복원한다.
새 host의 실행 재개 절차와 pending-only NCP 명령 형식은 `CODEX_HANDOFF.md`에 있다.


## 최종 Stage5 데이터 백업과 복원

729-case 원자료 백업은 **완료**됐다. `delivery/STAGE5_DATA_DELIVERY.json`의
상태는 FULL_REMOTE_GET_AND_EXACT_ALL_PATHS_REASSEMBLY_VERIFIED다.
18개 독립 ZIP과 INDEX를 모두 원격 full GET했고, 원격 사본만으로 원본
1,715개 파일/423,198,268 bytes를 재조립해 각 SHA256이 일치했다.
ZIP 총합은 47,297,026 bytes이며 source/figures/docs는 이 data snapshot에 포함하지 않는다.

```text
Dropbox INDEX:
/BASS_BACKUPS/BASS_REI_PILOT_STAGE5_SPLIT729_DATA_20261021_INDEX.json
file_id: id:BSpOijBcT10AAAAAAD_fdA
SHA256: df7ddc6648b06b775c105c7c85cd7ccc4f5827284eb95b7f631d91cd79b13340
history.csv SHA256:
139f3f75f535116483ff05dd96933611ac15896ce125c78d9394eb983bb58332
```

INDEX와 PART01..18.zip을 같은 디렉터리에 두고 PART01에서
RESTORE_STAGE5_SPLIT729_DATA.py를 꺼낸다. ZIP들을 하나로 이어붙이지 않는다.
다음 명령은 물리 적분 없이 bytes만 검증·복원한다.

```bash
python3 RESTORE_STAGE5_SPLIT729_DATA.py \
  --index BASS_REI_PILOT_STAGE5_SPLIT729_DATA_20261021_INDEX.json \
  --verify-only

python3 RESTORE_STAGE5_SPLIT729_DATA.py \
  --index BASS_REI_PILOT_STAGE5_SPLIT729_DATA_20261021_INDEX.json \
  --destination /tmp/rei_split729_restored_20261021
```

Destination은 비어 있어야 한다. 복원 파일은 그 아래
`research/rei_sigma_pi_pilot_20261021/results/split729/`에 생긴다.
Git의 결과 tree에는 729-case의 큰 history.csv 대신 backup pointer와
집계·그림을 게시한다. Plot만 다시 만들려면 코드 checkout에서 복원된 aggregate
경로를 `--aggregate`에 지정하면 된다. 계산 manifest의 옛 절대경로를
수정하거나 재적분할 필요는 없다. 최종 게시 head와 문서/그림 backup은
별도의 FINAL_PUBLICATION_RECEIPT와 Stage6 receipt를 따른다.
