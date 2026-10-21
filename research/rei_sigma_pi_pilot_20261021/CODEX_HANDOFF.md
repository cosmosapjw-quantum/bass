# Codex handoff — 독립 matter/radiation 729-case pilot

**상태 기준: 2026-10-21. PILOT01의 81 cases와 PILOT02의 729 cases 모두 완료됐다.**
PILOT02는 243 groups 모두 PASS, 729 unique cases, 누락 0, 초기 상태를 포함한 47,385 history rows다.
최초 3-case group을 재사용한 전체 실행은 242 PASS + 1 SKIPPED_PASS로 완료됐다.
이 문서는 실제 summary, CSV 및 receipt를 확인해 갱신한 운영 인수인계다.
최종 결과 게시 commit은 아래 PR의 최신 branch head와 최종 delivery receipt에서 확인한다.

## 기준 위치와 commit

| 항목 | 기준 |
|---|---|
| BASS draft PR | https://github.com/cosmosapjw-quantum/bass/pull/176 |
| REI draft PR | https://github.com/cosmosapjw-quantum/rei_bianchi/pull/213 |
| 양쪽 공통 branch | `research/rei-sigma-pi-pilot-20261021` |
| 연구 경로 | `research/rei_sigma_pi_pilot_20261021` |
| PILOT02 실행 source | BASS `82372ed8db68085868603d4267a630ed9cde6abb` |
| PILOT01 실행 source | BASS `003550e04e8d6c316be422f8ac6a15df284e49a5` |
| 불변 물리 owner | REI PR141 C15 `80825585f9fe31d2ee0d5af545ada3fa1f52be72` |
| 기존 완료 데이터 | `results/pilot81_v2/aggregate` |
| 신규 실행 데이터 | `results/split729` |

실행 source commit과 최종 결과를 게시한 branch head는 서로 다른 식별자다.
최신 head는 실제 PR/branch readback 및 `delivery/`의 receipt와 대조한다.
완료 결과의 출처를 설명할 때 실행 source commit을 최신 문서 commit으로 바꾸지 않는다.

## 그대로 복사할 작업 지시

```text
$physmath-research-loop를 이어서 사용하라. 사용자의 최신 요청은 물질과 복사의
비등방 응력 pi_ab를 독립적으로 취급하는 것이다. 기존 81-case 결과와 새 (Sigma, Pi_m, Pi_r) 729-case 완료 결과를 보존하고,
실제 데이터의 분석·시각화와 남은 연구 과제에 기여한다.
다른 Codex 세션이나 작업이 있다는 이유만으로 멈추지 말고, 실제 가용 자원에서
독립 작업을 나눠 수행한다. 상세 성능 benchmark는 요청되지 않았다.

1. 현재 상태와 먼저 읽을 자료

- BASS PR176: https://github.com/cosmosapjw-quantum/bass/pull/176
- REI PR213: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/213
- 공통 branch: research/rei-sigma-pi-pilot-20261021
- 공통 경로: research/rei_sigma_pi_pilot_20261021
- PILOT02 실행 source: 82372ed8db68085868603d4267a630ed9cde6abb
- PILOT01 실행 source: 003550e04e8d6c316be422f8ac6a15df284e49a5
- REI 물리 owner: 80825585f9fe31d2ee0d5af545ada3fa1f52be72

REPORT_KO.md, RESEARCH_DECISIONS.md, DAG.json, SPLIT_CONTRACT.json,
README_SPLIT.md, physics/SPLIT_THEORY.md, physics/SPLIT_INITIAL_REVIEW.json,
physics/SPLIT_CODE_REVIEW.json, delivery/를 먼저 읽는다. 새로 생긴 최종 execution
summary, 독립 결과 검토와 최종 delivery receipt를 함께 확인한다.
이미 확인한 전체 inventory를 처음부터 다시 수행하거나, 오래된 NOT_RUN을
완료 receipt보다 우선하지 않는다.

PILOT01은 완료:
- 81 unique cases, 27 groups, case마다 64 steps, 초기 상태를 포함한 5,265 rows.
- results/pilot81_v2/aggregate에 CSV, 요약, 그림과 provenance가 있다.
- 첫 group은 worker 폭 1에서 완료됐고, 폭 8의 후속 실행에서 재사용됐다.
- 27 output files와 55 bound source/input files의 hash 검증이 완료됐다.
- 최초 NumPy bool JSON export 실패 기록은 보존돼 있다. export만 수정한 v2가
  성공 결과다. 실패 scope를 성공으로 덮어쓰지 않는다.
- 기존 S12 NCP 17 jobs도 이미 완료돼 있다. 이 작업을 다시 queue에 넣지 않는다.

PILOT02도 완료:
- 독립 signed Sigma, signed Pi_m, signed Pi_r의 9 x 9 x 9 = 729 unique cases.
- 3 cases/group, 총 243 groups가 모두 PASS이며, 각 case는 64 steps다.
- 첫 group 3 cases를 폭 1에서 완료했고, 전체 실행은 242 PASS + 1 SKIPPED_PASS다.
- aggregate status는 COMPLETE, missing cases는 0, history rows는 실제 47,385다.
- results/split729/aggregate에 cases.csv, history.csv, summary.json 및
  sigma_pi_split_slices / sigma_pi_split_components의 PNG·PDF·provenance가 있다.
- 완료 수량은 execution summary, 243 attempt receipts와 실제 CSV에서 확인했다.
  원래 worker gates는 aggregate에서 모두 PASS로 기록돼 있다.
- 완료 scope와 bound input을 보존한다. 64 cores를 채우기 위한 재실행은 하지 않는다.
- 추후 새 작업에서도 coordinator lock을 존중하고 실행기를 중복 launch하지 않는다.

2. 물리 정의와 분해

- 기하: non-tilted LRS Bianchi I. 일반 비-LRS 방향 자유도는 포함하지 않는다.
- sigma_ab = diag(-s,-s,2s), s = db/dt.
- 기본 norm은 sqrt(A_ab A^ab / 2), Frobenius norm은 이 값의 sqrt(2)배다.
- Sigma_h = sqrt(3) |s| / H.
- D = P_parallel - P_perp [Pa], pi_ab = diag(-D/3,-D/3,2D/3).
- kappa_time = 8 pi G/c^2 = 3 * C15.KAPPA.
- Pi_h = kappa_time |D| / (sqrt(3) H^2).

독립 성분은 다음과 같다.
- D_m = Pi_massive: 선택한 massive nonbaryonic Vlasov species의 응력이다.
  기존 owner의 H/He gas와 나머지 cold matter는 isotropic이므로 pi_ab = 0이다.
- D_r = Pi_gamma + Pi_nu + Pi_UV: photon, massless neutrino, 실제 evolving UV다.
- D_total = D_m + D_r를 먼저 더한 다음 total norm을 계산한다.
- Pi_m + Pi_r는 component norm의 합이며, 일반적으로 total norm이 아니다.
- 각 성분의 signed D, signed Pi, norm 및 work = 2 s D를 보존한다.
- 모든 history row의 실제 상태에서 성분을 다시 계산한다. 초기 분해를 복사하지 않는다.

초기 grid:
- |Sigma_h|: 0, 0.0005, 0.001, 0.002, 0.004.
- |Pi_m,h|와 |Pi_r,h| 각각: 0, 0.00005, 0.0001, 0.0002, 0.0004.
- 0의 sign은 0, 양의 크기는 두 sign을 모두 사용하므로 각 signed 축은 9점이다.
- massive seed alpha_m은 radiation seed alpha_r와 독립이다.
  gamma와 nu만 alpha_r를 공유한다. 두 P2 family는 각각 -1 <= alpha <= 2다.
- nominal initial cancellation은 81 cases: 두 성분이 모두 0인 9개와,
  0이 아닌 반대 부호 성분이 상쇄되는 72개다.
- total cancellation은 초기 조건이다. 두 성분의 진화가 다르므로 이후에도
  total이 0이라고 가정하지 않는다. 작은 raw residual을 clip하지 않는다.
- Pi < 3e-13의 orientation은 component별, total별로 unresolved라고 표시한다.

범위:
- a = 0.1999 -> 0.2, mean z = 4.00250125 -> 4.
- 초기 T = 12,000 K, x_HII = 0.4, x_HeII = 0.5.
- massive fraction = 0.1, m/T = 30, L = 8, native source grid = 8 x 8.
- 기존 MD14 source와 Grackle Case-A owner를 유지한다.
- 모든 물리 stress, Thomson, compression 및 predictor-corrector feedback이 켜져 있다.
- 원래 number/energy/monopole gate와 source identity를 유지한다.
- full stellar/emitter + escape Q^a closure, cold z20-to4, 일반 비-LRS,
  시간/각도/스펙트럼 수렴은 아직 해결되지 않았다. preliminary conditional response다.
- warm 10,000~24,000 K rate table을 8 K까지 외삽하지 않는다.

3. 확인된 cancellation 결과

- initial signed Sigma=0, Pi_m=+4e-4, Pi_r=-4e-4인 split_0079에서
  final signed Sigma=-4.795410954946239e-11,
  final signed Pi_total=-1.9176362919464883e-7이다.
- 반대 부호 입력 split_0078에서는 final signed Sigma=+4.79541095518866e-11,
  final signed Pi_total=+1.917636292007428e-7이다.
- 두 성분 norm의 초기 합은 약 8e-4지만, signed tensor의 초기 합은 nominally 0이다.
  실제 raw Pi_total은 약 1e-18 규모로 남아 있으며 clip하지 않았다.
- 서로 다른 massive/radiation 진화로 초기 상쇄가 유지되지 않는 조건부 응답이다.
  이는 full convergence나 thermochemical detection의 입증이 아니다.
- 온도·이온화 응답의 분해와 수치적 검출 가능성은 계속 열린 과제다.

4. 병렬 실행과 NCP

- 이번 pilot의 실제 실행 환경은 ChatGPT sandbox의 8 CPU / 8 GiB다.
  이 lane에서 새 pilot을 NCP에서 실행했다고 주장하지 않는다.
- NCP target은 64 CPU / 128 GiB다. shared_executor는 profile 상한뿐 아니라
  affinity, cgroup quota, sampled CPU 사용량과 남은 memory를 함께 따른다.
- numerical library thread는 worker당 1, group당 timeout은 최대 1,800 s다.
- scope disk 4 GiB와 filesystem free 256 MiB reserve는 새 작업 admission 조건이다.
  hard output quota가 아니며, 이미 실행 중인 작업의 출력은 완료될 수 있다.
- 384 MiB/group은 admission estimate다. 과거 RSS telemetry가 불완전하므로
  measured peak RAM이나 speedup으로 해석하지 않는다.
- 준비된 source/rate/radial/angular 객체는 group 안의 3 cases에서 재사용한다.
  243 groups 전체를 관통하는 persistent process pool이라고 주장하지 않는다.
- source/input/toolchain identity와 worker 수는 분리된다. 같은 scope에서 완료한
  정확한 PASS는 출력 hash를 검증한 뒤 건너뛴다. CPU를 채우려고 반복 계산하지 않는다.
- 다른 process를 종료하거나, 타 세션 checkout을 전환하거나, working tree를 수정하지 않는다.

기존에 승인된 SSH 경로:
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p22

이 sandbox에는 해당 key가 없다. 새 executor에서 실제 접근 가능성을 확인하되,
key 값을 출력하거나 복사하지 않는다. 사용자가 이미 승인한 범위의 read-only 확인과
독립 작업은 계속 진행한다. 현재 접근하지 못한 NCP 실행은 완료로 기록하지 않는다.

현재 실행 manifest에는 이 host의 절대경로와 toolchain version이 들어 있다.
다른 host에서 그대로 실행하거나 경로만 치환하지 않는다. 먼저 source/input hashes,
새 host의 toolchain, 완료 case/receipt inventory 및 남은 작업을 대조하는 admission
migration을 수행한다. 필요하면 실제 미완료 cases에 대한 새 manifest를 만들고,
기존 immutable manifest와 receipt를 보존한다. 경로가 바뀌었다는 이유만으로 이미
완료한 81 또는 729 cases를 새 미완료 작업으로 취급하지 않는다.
완료 결과의 CSV/JSON/그림 소비와 재시각화에는 재적분이 필요 없다.

5. 게시, 백업, DAG

- 각 실제 단계의 source/result commit, DAG 상태, PR 게시, backup receipt를 갱신한다.
- GitHub draft PR 게시와 기존 /BASS_BACKUPS 백업 흐름은 승인돼 있다. merge하지 않는다.
- delivery/STAGE3_DELIVERY.json: 기존 81-case 결과 백업의 복구가 완료됐다.
  4개의 독립 PART ZIP을 원격에서 full GET해 SHA256, provider block hash,
  ZIP CRC 및 총 454 payload files를 확인했다. 상태는
  RECOVERED_SPLIT_BACKUP_FULL_REMOTE_GET_VERIFIED다.
- Stage3 최초 unsuffixed ZIP은 INVALID_ARCHIVE_DO_NOT_RESTORE다. 원인은 UNKNOWN이며
  실패 증거로 보존돼 있다. 복원에는 검증된 4개 PART ZIP을 사용한다.
- Stage3 outer index는 upload ACK와 metadata 검증 수준이며 full GET은 하지 않았다.
- delivery/STAGE4_DELIVERY.json: 새 split source 8 files의 업로드 ACK와 원격 metadata
  확인은 완료됐다. 로컬 CRC/hash 검증은 PASS지만 독립 remote full GET은 하지 않았다.
- Stage3은 기존 81-case payload, Stage4는 split source package다. 둘 다 새 729-case
  runtime 결과를 포함하지 않는다. 신규 결과 백업·게시의 완료 여부는 별도의 최종
  delivery receipt와 최신 PR/branch에서 확인하고, 검증 수준을 구분해서 설명한다.

6. 바로 다음 작업

- 완료한 81 및 729 cases를 먼저 소비한다. 실행 대기 상태로 되돌리지 않는다.
- 최종 독립 결과 검토와 source/input/output hash 기록을 확인하고, component 분해와
  cancellation 그림을 실제 데이터에 근거해 해석한다.
- 신규 729-case 결과의 최종 게시와 백업은 최신 PR/branch 및 delivery receipt로 확인한다.
  이미 완료된 항목을 반복 업로드하거나 중복 계산하지 않는다.
- 실제로 남은 새 science를 대상으로 다음 연구 루프를 정한다. 상세 benchmark는 추가하지 않는다.
```

## 완료 데이터 재집계와 그림 재생성

다음 명령은 연구 경로에서 실행한다. **기존 raw/aggregate를 소비하며 물리 적분을 하지 않는다.**
신규 split 실행도 완료됐으므로 아래 명령으로 기존 결과를 재집계·재시각화할 수 있다.
현재 그림을 보존해야 하면 --out을 새로운 분석 경로로 지정한다.

```bash
python3 split_sweep.py aggregate \
  --manifest results/split729/inputs_manifest/manifest.json \
  --scope results/split729/scope \
  --out results/split729/aggregate

python3 split_plot.py \
  --aggregate results/split729/aggregate \
  --out results/split729/aggregate/sigma_pi_split

python3 plot_pilot.py \
  --aggregate results/pilot81_v2/aggregate \
  --out results/pilot81_v2/aggregate/sigma_pi_pilot

python3 plot_pilot.py \
  --aggregate results/pilot81_v2/aggregate --response \
  --out results/pilot81_v2/aggregate/sigma_pi_response
```

`split_plot.py`는 `_slices`와 `_components`의 PNG/PDF 및 provenance를 만든다.
압축 배포본에 `history.csv.gz`만 있다면 원래 CSV bytes로 먼저 복원한다.

## 실제 새 미완료 작업이 있을 때만 사용할 실행 형식

현재 81 및 729 cases는 완료됐으므로 두 manifest를 다시 실행할 필요가 없다.
다음은 별도로 승인된 **새 미완료 science manifest**의 실행 형식이다.
이전 완료 cases를 새 pending 목록에 넣지 않으며, 다른 host로 옮길 때는 위의
admission migration을 먼저 수행한다.

```bash
python3 shared_executor.py NEW_PENDING_MANIFEST.json \
  --scope NEW_PENDING_SCOPE \
  --profile sandbox --max-workers 8 \
  --resource-wait-s 300 --max-scope-gib 4
```

실제 NCP에서 사용할 때의 형식은 다음과 같다.

```bash
python3 shared_executor.py NEW_PENDING_MANIFEST.json \
  --scope NEW_PENDING_SCOPE \
  --profile ncp --max-workers 64 \
  --resource-wait-s 300 --max-scope-gib 4
```


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
