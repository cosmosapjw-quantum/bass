# ACCEL03 standalone restore

This frozen checkpoint includes repository-backed source, compact stored evidence,
figures and handoffs from four lanes under research/: the original pilot,
ACCEL01 acceleration, ACCEL02 native moments, and ACCEL03 sweep analysis.
Restore the ZIP at a directory root retaining these research/ paths. Build
products, Python caches, locks, signed URLs, private intake download archives
and original checkout-status contents are excluded.

## What is actually present

ACCEL03 includes the selected portable NCP5 plan/manifest and five successful
receipt/result pairs under results/inputs/ncp5, the original two-step saved
outcomes, aggregate case/history/diagnostic tables, response raw checks, point
tables and PNG/PDF figures. The 729 cohort is archived endpoint reuse with no
available intermediate history in this analysis. Historical toolchain/backend
cohorts remain separate; restoration does not imply all rows ran natively.

The original 47,385-row pilot history is not locally present and is not claimed
in this ZIP. Its existing recovery index is:

`/BASS_BACKUPS/BASS_REI_PILOT_STAGE5_SPLIT729_DATA_20261021_INDEX.json`

Read the original pilot delivery/STAGE5_DATA_DELIVERY.json and its handoffs for
that separate raw-data restore. Old pilot81 history, where present, is distinct
from the absent split729 history.

## Executable handoff and admission

Read FROZEN_CONTRACT.md, SCOPED_DECISION.json, REPORT_KO.md,
evidence/CONTROLLER_ADMISSION.json and evidence/INDEPENDENT_REVIEW.json in the
ACCEL03 lane, then follow CODEX_HANDOFF.md. The commands use saved results and
the retained quadrature; no trajectory solve, native rebuild or benchmark is
required for this unit. New data work requires an explicit new user scope.
The recorded target resource observation is historical, not a current NCP
capacity measurement.

Before a new unit, read current source/result/provider evidence first. Preserve
raw historical pending statuses as records of their creation time; current
admission is the controller decision. Do not repeat the closed independent
review or automatically rerun completed sweeps.

## Immutable checkpoint and later receipts

Stage A/B actual publication and provider ACK/size receipts are included.
The Stage C ZIP is frozen before its own publication/provider acknowledgement;
it truthfully contains the delivery-in-progress snapshot. Its actual final
publication, one full-GET size/SHA256/Dropbox-block-hash/CRC/exact-member
verification and receipt closeout are written later in their containing Git
commit. Do not rebuild this ZIP to insert its own acknowledgement or hash.
Resolve final receipt publication through the repository branch/PR head.

The BASS canonical ACCEL01 base documentation remains the restore input;
historical REI-specific handoff wording can differ without a science mismatch.
No dependency lane is modified or newly republished by this ACCEL03 checkpoint.


## 최종 전달 상태

ACCEL03은 `SCOPED_COMPLETE`다. Stage C 과학·인계 본문은 BASS
`9074a788ca6f26384356c6fa57a695dc6f307fc6`, REI
`e4defc4f303203232223ecabe004252761145844`에 실제 게시됐다. 실행 코드의
Stage B pin은 BASS `b0ea16c9172c8b1553cbdb35cb03460160db1412`, REI
`39ae7c843ea2d1adf580aff44aebfdedea7e33aa`로 유지한다.

7,286,437-byte Stage C ZIP은 한 번의 전체 GET으로 SHA256
`049af2b058d83c997c03c092e6ec90ab0f3411c45118719b75bf3f7dc27a04e4`,
size·Dropbox block hash·ZIP CRC·379개 exact member를 확인했다. Stage A/B는
provider ACK·size 확인이며, 전체 GET 검증은 Stage C에 한 번 수행했다. 실제
영수증은 `delivery/FINAL_PUBLICATION.json`과 `STAGEC_BACKUP_VERIFIED.json`이다.

불변 ZIP은 자체 ACK보다 먼저 만들어졌고 최종 영수증은 뒤따르는 Git commit에
있다. 최종 영수증의 게시점은 이 파일을 포함하는 Git commit으로 확인한다.
자기 commit SHA를 본문에 재귀적으로 넣거나 ZIP을 다시 만들지 않는다.
`STAGEC_PACKAGE.json`의 생성 당시 상태는 그대로 보존한 역사적 helper 영수증이다.

NCP5 실행과 그 과학 판정은 이미 완료됐다. ACCEL03 안에 추가 실행·과학 검증은
필요 없다. 이후에는 새 사용자 범위 또는 실제 새 반환 자료의 증거를 먼저 읽고
필요한 최소 작업을 정한다. 완료된 독립 검토나 원 sweep을 반복하지 않는다.
