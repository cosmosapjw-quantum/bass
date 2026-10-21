# ACC02 백업 변경분 수용 기록

기준 시각은 ACCEL01 종료 **2026-10-21 08:34:13 UTC**다. 이 기록은 이후에 바뀐 백업을 읽은 결과이며 새 과학 계산·테스트·벤치마크·업로드·원 repo 수정은 수행하지 않았다. 기계 판독 결론과 전체 식별자는 `BACKUP_DELTA.json`, 상세 제공자 관측은 `BACKUP_PROVIDER_EVIDENCE.json`에 있다.

## 1. C21M의 새 98-case 실행을 별도 결과로 수용

새 Dropbox 객체 `id:BSpOijBcT10AAAAAAD_gNg`는 17,911,591 B의 `BASS_CR_C21M_NCP98_RAW_AND_ANALYSIS_20261021T1109Z_ee62f86.tar.gz`다. 한 번 내려받은 archive SHA256은 `e9baa6bab57790d29a0dfb06747a3304f0449a48e7dfc2d14c6630849f9c1d0a`이며, Dropbox의 4 MiB 블록 해시 및 크기와 일치한다. Drive에도 ID `1gFttuaFMkAd5Azb0STftc4HA_myEryrq`로 같은 이름·크기의 객체가 있다. Drive의 내용 bytes는 이 intake에서 내려받지 않았다.

이 결과의 실제 시작 시각은 receipt의 **10:50:11 UTC**다. Dropbox 서버 수정 시각은 **10:54:59 UTC**, Drive 수정 시각은 **10:55:02.841 UTC**다. 이름의 `1109Z`는 실행 시각의 근거로 사용하지 않는다.

| 식별 항목 | 고정 근거 |
|---|---|
| 과학 content commit | `659c94312eb9c12ebb987de934459c12a63d67b0` |
| 실행 시 document base | `b78a943e5d7ae341bbfe84f742a06a4ac36d0e43` |
| REI physics source | `3b85dedce84d37b3e165da00685a8a984950aafe` |
| Run ID | `c21m_ncp_refinement98_z20_z4_20261021` |
| 실제 raw run identity | `7f89b12adbeee64a70832e633ae563584bc2a68f6ac433dc56f759a1946eb718` |
| Grid SHA256 | `768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04` |
| Raw MANIFEST SHA256 | `3ca2c66c19399480d1538385b79f09fc2ed5cc5b9be3cd6e9fbc6be5e8e1ce23` |

98개의 COMPLETE seal, RESULT, history NPZ를 archive 안에서 읽어 byte hash를 대조했다. **요청 case 집합 98개와 seal 집합이 일치하고, 98개 모두 COMPLETE이며, raw identity·RESULT 해시·history 해시가 모두 일치**한다. 저장된 campaign 분석은 기존 26개 + 새 98개 + 기존 C21L 중심 1개를 결합한 **125개 좌표**다. 이 intake는 기존 26개와 중심의 원 데이터를 다시 내려받거나 적분하지 않았다.

그림·분석의 물리 범위는 **non-tilted collisionless LRS Bianchi I, z=20→4, FP64 40-state/101시점**이다. Signed full-Frobenius 좌표 `S0, Pm0, Pr0`를 사용하며 matter와 radiation 초기 stress가 독립적이다. Photons와 massless neutrinos가 모두 포함된다. 이는 C15 warm 729 pilot의 `a=0.1999→0.2`와 다른 source/input/result 계열이다. **두 결과를 합쳐 C15의 범위를 확장하거나 수렴·full EoR·일반 비-LRS·full Q^a closure 증거로 표시하지 않는다.** 원래 729-case 데이터와 ACCEL01의 검증된 Stage C는 재사용하며 재실행·재다운로드하지 않았다.

선택 추출한 실제 preliminary plot은 다음 경로에 있다.

```text
C21M_selected/research/cr_c21m_independent_stress_20261021/analysis_campaign125_20261021/campaign_endpoints.png
C21M_selected/research/cr_c21m_independent_stress_20261021/analysis_campaign125_20261021/campaign_endpoints.pdf
```

PNG/PDF의 SHA256은 저장된 OUTPUT_MANIFEST와 정확히 일치한다. 이 intake의 그림 확인은 byte identity까지이며 별도 시각 재심사는 수행하지 않았다.

## 2. 과학 결과와 메타데이터 불일치를 구분

`NCP98_EXECUTION_RECEIPT.json`과 `NCP98_INDEPENDENT_REVIEW.json`에는 실제 raw identity와 다른 suffix가 기록돼 있다. 두 문서의 값은 `7f89b12adbeee64a70832e633ae563584bc2a68f6ac2a60139b98efacb01c05a`다. Raw MANIFEST, run SUMMARY, 분석 INPUT_SOURCES, 모든 COMPLETE/RESULT가 같은 실제 identity를 사용하므로 수용 기록은 이 raw identity에 결속한다. 다른 세션의 문서·repo를 고치지는 않았다. 원 담당자의 별도 provenance 정정 대상으로 남긴다.

분석 OUTPUT_MANIFEST 7개 중 **6개는 크기와 SHA가 정확히 일치**한다. CSV는 archive에서 100,645 B·126 LF이고 manifest에는 100,771 B가 기록돼 있다. 메모리에서 LF만 CRLF로 바꾸면 **manifest의 크기와 SHA256까지 정확히 재현**된다. 따라서 차이는 줄바꿈 포장으로 제한된다. 원본 bytes는 그대로 보존했으며 ‘7개 raw bytes 모두 일치’라는 주장은 채택하지 않는다. 상세 결과는 `C21M_ARCHIVE_INTEGRITY.json`에 있다. 이 차이로 과학적 실패를 추론하지 않는다.

08:47 시점의 C21LM document closeout도 85,325 B의 작은 ZIP만 내려받아 29개 payload SHA/크기와 ZIP CRC를 확인했다. 당시의 `NCP98 NOT_RUN`은 그 시점의 정확한 상태였고, 위 10:50:11 실행 증거가 이후 상태를 대체한다. 과거 문서를 소급 변경하지 않는다.

## 3. 자원 및 백업 상태의 실제 변경

C21M run의 역사적 resource snapshot에는 CPU affinity 64개, coordinator CPU 0, 보호 CPU 55와 관측상 바쁜 CPU 56을 제외한 **worker 61개**가 기록돼 있다. 당시 가용 메모리는 **86,109,442,048 B ≈ 80.20 GiB**, 관측 총량/상한은 **135,050,526,720 B ≈ 125.78 GiB**다. 이 snapshot은 10:50:11 실행의 기록이고 현재 live capacity·예약량이 아니다. 이 source에서 디스크 여유 공간은 관측하지 않았다. 성능 비교나 speedup 추정은 하지 않는다.

ACCEL01 Drive A의 이전 미확인 제출과 구별되는 **후속 retry 객체**가 확인됐다. 새 reconciliation은 10:39:15.864 UTC에 ID `1GK5AjCvmbnVdDwDMRmz-_OhVReBE5sxn`을 반환받았다고 기록하며, 이번 직접 metadata 조회에서도 정확한 파일명과 **248,613 B**를 확인했다. 원래 629.9초 중단된 요청의 완료 여부와 중복 객체 유무는 여전히 미확정이다. Drive bytes 전체 GET과 provider MD5 확인은 없다. B/C는 새 reconciliation 기준 NOT_ATTEMPTED다. `DRIVE_A_METADATA_RECOVERY.json`이 이 차이를 보존한다.

신규 checkpoint에는 이전 Stage B/C에서 성공한 Dropbox 경로를 사용할 수 있다. `mcp__codex_apps__dropbox_upload_file`의 `source_file`에 고정 ZIP의 절대 로컬 경로 문자열을 전달하고 `/BASS_BACKUPS/<고유 파일명>`에 한 번 제출한다. ACK를 즉시 저장한 뒤 `get_file_metadata`와 `download_link` metadata의 크기·블록 해시로 확인한다. 오래 멈춘 이력이 있는 upload-status poll은 사용하지 않는다. 최종 단계의 full GET과 SHA/CRC/member 검증 방식은 기존 `source_intake/stagec_dropbox_verify.py`에 있으나 ACCEL01 고정 값을 새 단계에 그대로 사용해서는 안 된다. 서명 URL이나 자격 정보는 인계 기록에 포함하지 않는다.

조회 범위는 Dropbox 두 개 알려진 폴더의 direct-child snapshot, C21M/RUN20/ACCEL02/PHYS filename 검색, Drive의 알려진 bass_cr 폴더와 두 개 실제 file ID다. Dropbox 날짜 필터가 과거 결과도 반환해 서버 수정시각으로 다시 분류했다. PHYS 검색은 요청 1000에 100개를 반환했으므로 계정 전체 완전성을 주장하지 않는다. 새 RUN20/PHYS75+ 실행 증거는 이 조회에서 수용하지 않았고, 과거 REI ACCEL02 이름은 이번 ACC02와 구분했다. 대량 NCP rescue shard는 내려받거나 재조립하지 않았다.
