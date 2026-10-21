## S12 NCP 준비 17-job 실행 및 독립 receipt 검토 — scoped PASS

사용자가 승인한 SSH 경로로 실제 NCP에 접속했습니다. 첫 원격 행동은 host identity, CPU affinity/cgroup quota, 가용 RAM/disk, owner process, checkout 및 기존 receipt의 read-only 대조였습니다. 기존 owner 작업은 변경하거나 종료하지 않았습니다.

### 고정 identity와 실행

- PR source HEAD: `106a0153bf113fa4f0beea9743e84a744b65f424`; sparse dedicated checkout clean.
- Owner/source/C8/result identities 및 SCIENCE_BINDING, DELIVERY_BINDING, JOB_TEMPLATE SHA는 승인 계약과 일치.
- 109개 sealed source/input files의 bytes, SHA256 및 Git blob identity가 일치.
- 최초 manifest는 그대로 유지: SHA256 `ef4d8210e43341ba3cbb2dbe2ee81cfe1894a1356473851e01d17205b56b2965`; width 63; 17 jobs.
- Actual first launch: build 1 + extended histories 14 + ensemble 1 PASS. case_parallel warm-up은 `can't start new thread`로 실패했고, 해당 raw/attempt를 보존했습니다.
- Read-only 자원/owner 재대조 후 동일 manifest와 width로 resume했습니다. 16개 기존 exact PASS를 재사용하고 case_parallel만 실행했습니다. 최종 launch PASS, 실패 job 0. 추가 campaign, native compile-only, 자동 optimization cycle은 실행하지 않았습니다.
- 성공 return ZIP: 157,420,884 bytes; SHA256 `eb522092a7e466d95d87797795fb080583dc0b987555dcaba00ea2fd62813709`; 9,901 payloads / 532,721,885 uncompressed bytes. 모든 payload SHA/CRC가 확인됐고 첫 실패 attempt와 두 launch records가 포함됐습니다.

### 관측 결과와 claim ceiling

- 14/14 extended-history jobs 및 30/30 aggregate checks PASS. Ensemble은 manufactured fixed k16/n64 범위에 한정됩니다. 11 full cases와 3 omission controls를 구분했고 controls의 48 internal numeric gate failures는 보존했습니다.
- 64-pack serial/parallel 출력 64/64 identity; 9 measured pairs, median speedup 17.896596287463947, IQR [16.77145413460518, 18.56328984384657]. 63 workers는 요청값이며 측정된 concurrent peak는 53–61입니다.
- Fresh independent Astra read-only review: **scoped PASS**, receipt/identity mismatch 없음. Reviewer는 1,152 core subprocess receipts/stdout bytes, 4,769 declared artifacts, 35 acceptance pointers를 확인했습니다.
- 이 PASS는 지정된 manufactured-history gates, core serial/parallel identity/benchmark 및 bundle completeness만 다룹니다. Native/full spectral-history 또는 continuum convergence, 새 독립 physics 검증, checkpoint resume, REI production/full EoR 또는 merge admission을 뜻하지 않습니다. 기존 native16 fixed-support infeasibility, S10/S11 workload 회귀와 bias, MD14/native shared-Q/reactive full finite-bin 및 tangent 의무는 계속 미완료입니다.

### 백업/readback

Dropbox `/BASS_BACKUPS/BASS_S12_NCP_EXECUTION_20261021_8247645d_eb522092.zip` 업로드 완료 (157,420,884 bytes). 단일-use download readback의 크기와 SHA256이 local return ZIP과 정확히 일치합니다. Google Drive는 PENDING_NO_WRITE_OR_RETRY로 유지했습니다. 기존 SSH 계약 backup의 valid R2 ZIP을 유지하며 22-byte 빈 ZIP은 제외합니다.

Raw return archive and receipts remain the execution record; this comment records the scoped result and independent review.
