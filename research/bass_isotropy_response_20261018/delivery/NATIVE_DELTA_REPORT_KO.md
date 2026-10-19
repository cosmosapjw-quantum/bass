# S3 native 통합: 구현·실행·게시 범위

## 이번 단계의 실제 진척

| 항목 | 이번에 완료한 변경 또는 측정 | 저장 증거와 승인 범위 |
|---|---|---|
| 정확한 native owner | REI `0e25846433170d0f420c4cda44a0bedbf02cd177`의 57개 파일, 614313 bytes를 취득하고 Git blob SHA와 SHA256를 검증했다. | `../native_owner_manifest.json`; 원 owner 파일은 수정하지 않았다. |
| 새 source adapter | 원 native `inject`를 빈 임시 state에 호출한 뒤 새 birth의 number와 energy_ref만 `alpha_j/q_j`로 배율하고 old state에 transactional 합산한다. | `../native_adapter.rs`; 명시된 non-tilted local isotropic 새 source의 opt-in 경로다. |
| 기존 상태·spectral owner 보호 | old anisotropic stock 보존, zero birth bitwise 보존, 원 ray별 spectral support와 number/energy의 공통 배율, source 선언 및 frame 거절을 검사했다. | `../evidence_native_s3/run01/changed_native_tests.stdout`; 새 native tests 7개가 통과했다. |
| P4와 native 전단 응답 | 원 native ray geometry와 finite-bin birth를 사용해 P2/P2P4 × angular refinement를 분리한 20행을 측정했다. | `../evidence_native_s3/run01/NATIVE_ADAPTER.jsonl`; kinematic collisionless 국소 응답의 제한된 검증이다. |
| Transfer ledger | 비어 있지 않은 old stock에서 `inventory_after - inventory_before`를 새 birth ledger와 대조했다. | 최대 상대 잔차 photons `8.627859456293078e-14`, energy `1.4367906288760241e-13`; 기준 `1e-11`이다. |
| 재현 runner와 parser | Python stdlib runner가 정확한 owner를 자동 취득·검증한 뒤 rustc로 컴파일한다. Parser/source-identity regression 6개가 통과했다. | `../run_native_adapter.py`, `../test_native_adapter.py`; parser의 synthetic rows는 native 측정 증거에 포함하지 않는다. |
| 저장 증거·게시 범위 | 원 run01과 저장본, source snapshot, owner manifest 및 aggregate를 읽어 대조하고 아래 manifest를 작성했다. | `NATIVE_EVIDENCE_READBACK.json`, `native_publish_manifest.json`; 이 마감 readback에서는 소스 변경이나 테스트 재실행을 하지 않았다. |

완료된 PR173 원래 58행 캠페인과 PR174 기존 Rust 5개 검사를 이 native
캠페인에 포함하거나 다시 실행하지 않았다. 먼저 실행했던 새 adapter P2
preflight 1건은 `../evidence_native_s3/p2_preflight/`에 원 상태로 남긴다.
그 receipt의 `P24=NOT_RUN_PENDING_MODULE`은 preflight 당시 상태이며,
이후 run01의 P2P4 완료 여부를 덮어쓰는 현재 상태 표시는 아니다.

## P4 제약과 angular refinement를 분리한 결과

다음 표는 source birth `b=-0.3`, energy bin 96, 고정 spectral panel 조건이다.
`G(d)=Delta(d)/U_birth`이고 평균 scale factor를 고정한다.
`G'(0)=-8/5-(10/7)m2_E+(36/35)m4_E`의 예측값과 native central difference를
별도로 기록했다. Central difference의 `h=1e-5`이다.

| native rays | 제약 | 실제 birth energy P4 | 실제 energy moments 식의 G'(0) | native central G'(0) |
|---:|---|---:|---:|---:|
| 8 | P2 | `-7.753410240674052e-2` | `-1.679749362475506` | `-1.6797493625837951` |
| 8 | P2P4 | `1.1453158283861235e-16` | `-1.5999999999999994` | `-1.6000000001301484` |
| 16 | P2 | `-4.305257650834903e-4` | `-1.600442826501228` | `-1.6004428265520239` |
| 16 | P2P4 | `1.0121544585286615e-15` | `-1.5999999999999985` | `-1.6000000000504557` |
| 32 | P2 | `-2.535081622537971e-9` | `-1.6000000026075163` | `-1.600000002654368` |
| 32 | P2P4 | `-6.994022049639098e-16` | `-1.600000000000001` | `-1.600000000047188` |

같은 8-ray support에서 P2P4 제약을 추가하면 잔류 P4에 의한 국소 slope
편향이 사라진다. P2-only의 ray 수를 늘리는 별도 축에서도 잔류 P4가 줄어든다.
이 두 관찰은 continuum angular accuracy나 유한 d에서의 전 응답 정확도를
승인하지 않는다. 20행 전체에서 central derivative와 실제 energy moments
예측의 최대 차이는 `1.3014900268615293e-10`이었다. 허용 기준은 미리 정한
절대 `1e-8`이며, angular moment 기준 `3e-15`와는 다른 검사다.

Photon emissivity에 대한 최대 상대 차이는 `2.220446049250313e-16`, 고정
source-cell mean energy에 대한 최대 상대 차이는 `5.369926725506957e-12`였다.
후자는 이 고정 owner quadrature 사이의 진단값으로 남긴다. 총량을 재정규화하거나
허용오차를 넓히지 않았으며, 이 측정만으로 finite-bin spectral 수렴을 인증하지 않는다.

## 실패 종류와 실행 한도

최종 run01의 여섯 native 관련 명령은 모두 exit 0이고 최종 상태는
`PASS_NATIVE_ADAPTER_SCOPED`이다. Rust compile stderr는 dead-code warning을
포함하며 그대로 보존했다. 아래 거절은 새 native tests에서 의도한 결과였다.

| 조건 | 검증된 거절 또는 결과 |
|---|---|
| physically anisotropic 또는 미선언 source | `ANGULAR_SOURCE_DECLARATION_REQUIRED`; old state 보존 |
| 다른 source frame | `ANGULAR_SOURCE_FRAME_REQUIRED`; old state 보존 |
| native 8-ray, birth b=0.9의 P2-infeasible support | `INFEASIBLE_ANGULAR_SUPPORT`; partial mutation 없음 |
| 음의 weight | 오류 반환 및 old state 보존 |
| 음의 source dt | 원 owner의 `AXBI_COVARIANT_SOURCE_DT`; old state 보존 |

별도 저자가 작성한 P24 모듈을 native integration 담당자가 검토한 결과는
`../evidence_native_s3/INDEPENDENT_P24_NATIVE_REVIEW.json`이다. 이 검토는
adapter 자체에 대한 독립 검토가 아니다. Affine-compatible rank1 support의
`FEASIBILITY_UNRESOLVED_RANK1`은 구현 한계로 남고, 수학적 infeasibility로
바꾸어 부르지 않는다.

Native run의 실제 elapsed time은 14.96158348699828초, child peak RSS는
339804 KiB, 생성 파일은 16409633 bytes였다. Source fetch workers 4,
native thread 1, RAM 16GiB, disk 4GiB, job 1800초 상한 안에서 실행했다.
NCP 실행과 REI production/full EoR 실행은 하지 않았다.

## 게시할 파일과 재개할 의무

`native_publish_manifest.json`은 BASS repository root 기준의 모든 게시 대상
path, bytes, SHA256와 역할을 기록한다. Native source/runner/test/owner manifest,
두 projection dependency, 본 문서, native 설명 문서와 raw evidence를 포함한다.
기존 `balance.rs`는 이미 게시된 dependency이므로 재게시 변경을 요구하지 않는다.
Raw 원 owner staging, compiler toolchain, 실행 binary, rlib, Python cache,
기존 PR173 evidence는 새 게시 범위에서 제외한다. Manifest 자신의 hash는
자기참조를 피하려고 포함하지 않으며 최종 Git tree와 외부 backup receipt가 고정한다.

남은 연구 의무는 continuum angular accuracy와 더 높은 moments, source-age 및
reactive history, native finite-bin spectral refinement, Einstein feedback이다.
Production/full EoR 승인은 별도 gate로 남는다. NCP에서 재현이 필요할 때는
이미 준비된 `run_native_adapter.py`가 정확한 owner 취득, 컴파일, 작은 수정 후
실행과 receipt를 맡도록 사용한다. 완료된 run01을 이유 없이 반복하지 않는다.
