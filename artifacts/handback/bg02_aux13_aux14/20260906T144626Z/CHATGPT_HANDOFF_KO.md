# AUX13/AUX14 — Git-first 주 대화 반환

**완료: 유효한 기존 실행 재사용 / HISTORICAL_CONFLICT_REPRODUCED.**
Git-first 인계 bd612d9fa53815b1c72242ba509e0c890d7b2b17 및 R2 자동 수리 계약을 적용했다. 목표는 historical control의 기존 17개 AUX 검사를 실제 consumer에서 관측하고 정확히 반환하는 것이다.

- 실제 원본 결과: **16 Success / 1 Failure / 미평가 0**, 정확한 17개 ID와 event/final JSON 일치.
- 유일한 실패: `AUX13_MOMENTUM_CONSUMER_SIGN`. 원본 출력은 `-6 av s11 + 2 n23 s11 + 4 n23 s22 - 2 n22 s23 + 2 n33 s23`이다. 이는 원문 C1 식의 두 배라는 해석과 일치한다. 원본 held 표현과 Module suffix는 JSON에 그대로 있다.
- 프로세스: **exit 1**, timeout 없음, 3.609초. Wolfram `15.0.0 for Linux x86 (64-bit) (May 26, 2026)`. 이 값들은 원본 실행에서 관측했다.
- 테스트 actual messages는 17개 모두 `{}`, expected messages는 `HoldForm[{}]`; runtime failures `{}`, stderr 0 bytes. 관측된 harness 결함 없음.

**수정·재실행 판단:** driver·실행·수집 수리가 필요한 결함은 확인되지 않았다. 개정 인계에 따라 완전한 기존 결과를 재사용했다. 원본 AUX 총 1회, 이번 추가 실행 0회, repair·회귀·수리 target 재검증 0회이다. 이는 수리 금지나 소모 예산 때문에 중단한 결과가 아니다. 관측된 control의 부호 Failure를 그대로 반환하는 완료 조건을 충족했다.

**Identity:** control `f2f05d37cdc6476154869067b1d41436af8248b6`, tree `8a1d6fbb0c039fe7bd0e29f79cb4e581e4b70688`. 네 scientific blob 4/4 일치; source와 원본 driver 전후 및 현재 bytes 일치. Driver SHA-256 `5f80ed5d691bdf4466b60920ce98029ea092666c3831b7998b4787eb8e80c516`. 원문 두 댓글은 새로 읽은 bytes도 기존과 같다.

**Inherited / new:** 기존 로컬 ZIP `ee8c0e8d74e841eb28c98b889b6ee4699f63907d2814ab97f6c6d721c99008fb`를 새로 hash/CRC/manifest 검증했다. 최초 실패의 raw logs·명령·receipts·source·driver를 `original/`에 bytes 그대로 보존했다. 과거 ZIP 자체를 중첩하지 않았다. 현재 게시 산출물은 원본 결과의 읽기 가능한 Git 사본과 Git-first handoff다. R2 문서는 provenance/에 역사적 기록으로 보존한다. 별도로 없던 `0661dd...` ZIP의 manifest는 계승하지 않았다.

**남은 blocker:** 없음. Scientific source/driver/기존 evidence 및 runtime 설정은 수정하지 않았다. 별도 work thread, capture-six/native17, repaired candidate, AUX15는 사용하지 않았다. 원본 실행 wrapper의 과거 one-shot 동작은 보존된 실행 기록이며 최신 수리 권한을 제한하지 않는다.

**주 대화의 다음 최소 조치:** `RETURN_STATUS.json`의 per-ID 결과와 `original/execution/aux-final-original.json`의 Failure를 검토하여 과학적 수용을 판정한다. Production source 수정이 필요하면 별도 범위를 정한다. 이 반환은 scientific/provider/RF04 admission 또는 독립 감사 PASS를 주장하지 않는다.

검토 파일:

- [결과 JSON](RETURN_STATUS.json) · [원본 final JSON](original/execution/aux-final-original.json) · [per-TestID 결과](original/execution/per-test-results.json)
- [원본 stdout](logs/original.stdout.log) · [원본 stderr](logs/original.stderr.log) · [process receipt](original/execution/process.json) · [raw events](original/execution/test-events-original.log)
- [원본 driver](original/driver/BASS_AUX13_AUX14_V1.wls) · [외부 wrapper](original/execution/launch_once.py) · [source identity](original/identity/before.json) · [실행 후 identity](original/identity/after.json)
- [재사용 검증](EVIDENCE_REUSE_CHECK.json) · [게시 intake](PUBLICATION_INTAKE.json) · [manifest](MANIFEST.json) · [SHA256SUMS](SHA256SUMS)

ZIP은 보조 로컬 백업이며 위 개별 파일로 검토할 수 있다. 게시 commit은 execution source가 아니다. Publication commit/tree와 실제 원격 readback은 push 후 최종 출력 및 PR #131 연결 댓글에서 제공한다.
