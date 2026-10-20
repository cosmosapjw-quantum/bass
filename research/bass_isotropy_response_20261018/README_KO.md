# BASS isotropy / shear response — S9 실제 8개 history 완료

[S9 결과](S9_RESULTS_KO.md) · [S9 이론](S9_THEORY_KO.md) · [DAG](DAG.json) · [RETURN](RETURN_TO_CHATGPT.json) · [새 대화 인계](NEW_THREAD_HANDOFF_KO.md) · [Codex/NCP 인계](CODEX_HANDOFF_KO.md) · [재현 HOWTO](s9_vigilode/HOWTO_KO.md)

## 현재 결과와 게시 상태

2026-10-20에 현재 GitHub와 Dropbox·Drive의 최신 백업을 대조해 S6–S8 완료 근거를 재사용했고, 그 뒤에 남아 있던 **S9 고정 8개 history를 한 번 실행해 8/8 완료, 140개 gate assertion 통과**를 얻었다. 140은 사례별 판정 항목의 합계이며 독립적인 테스트 140회를 뜻하지 않는다. 독립 이론·수치 검토와 구현·기록 검토는 각각 `PASS_SCOPED`다. S9의 NCP 재실행 의무는 없다.

| 식별 항목 | 실제 값 |
|---|---|
| 실행한 S9 source | `4b30957cb008aad8019bb1a673937fc67bd017e8` |
| Source tree | `8e4abf3820d06bae6cbec307e4f69de74195d14b` |
| 사전등록 SHA256 | `7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507` |
| 현재 결과 publication | a40311796f9aac5ea5e0e58c630bee2a78443353; 원격 tree/blob readback 완료 |
| 현재 결과 ZIP의 Drive·Dropbox readback | `PENDING` — 실제 업로드·검증 후 최종 배송 영수증으로 갱신 |

Source 사전등록 자체는 실행 전에 두 provider에서 확인했다. [현재 cloud intake](evidence_s9/resume_20261020/CURRENT_CLOUD_INTAKE.json)를 우선 읽고 현재 결과 ZIP의 배송 상태와 이전 source 백업의 완료 상태를 구분한다. 최신 위치는 [PR174](https://github.com/cosmosapjw-quantum/bass/pull/174), [PUBLICATION_CLOSEOUT](PUBLICATION_CLOSEOUT.json), [CLOUD_READBACK](CLOUD_READBACK_KO.md)에서 확인한다.

## 실제 실행과 검증

현재 Rust 1.94.1로 `cargo build --locked --bin bass-s9-vigilode`를 새로 실행했고 exit 0을 확인했다. 새 binary SHA256은 `69de3e8739488524cdbe53f9e4bd71f8125717138bf06085b5f51a082060582f`다. 고정 source 13개와 input 3개, 원 VigilODE 178개 source 및 balance owner를 유지했다. 과거 `verified_prior_build` 영수증은 당시 기록으로 보존하며 현재 실행은 `fresh_build`다.

- [현재 build/attestation](evidence_s9/resume_20261020/runtime/PREPARATION_RETURN.json)
- [실행 전 publication gate](evidence_s9/SOURCE_PUBLICATION_GATE.json)
- [실제 8개 campaign return](evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json)와 각 case의 `RAW.json`, `PROCESS.json`, `ASSESSMENT.json`
- [결과 집계](evidence_s9/RESULT_SUMMARY_20261020.json), [수치·물리 해석](S9_RESULTS_KO.md)
- [독립 dual 검토 receipt](evidence_s9/resume_20261020/science_review/DUAL_REVIEW_RECEIPT.json), [독립 검토 보고](evidence_s9/resume_20261020/science_review/INDEPENDENT_S9_ACTUAL_REVIEW_KO.md)
- [최종 그림과 08→07 검수](evidence_s9/figures_20261020/final/FIGURE_AUDIT08_07_KO.md)

고정 VigilODE `a21d573980f66fe02891bd216153443b5352f921`의 실제 `mf_into_ls` workspace와 `SmallProblem<4>`가 같은 manufactured closed donor/cohort 모델을 적분했다. 각 arm의 세 tolerance에서 closed history 3개, fine analytic FLRW control 1개를 실행했다. 새 birth의 b(u)는 현재 해에서 얻고, 각 birth에서 새 immutable bank와 driver/workspace로 재시작했다. 기존 S8 primal 153개 출력은 비교 전용으로 재사용했다.

Fine closed history의 최대 |h−h_ref|는 MF `1.4327428132787645e-13`, Small+clock `1.7108536809473662e-13`이다. 각 arm의 rtol=1e-8과 1e-10 observation 배열은 동일하고 accepted step도 218개로 같다. rtol=1e-12에서는 305개다. 이는 이번 출력·사건 schedule에서의 plateau이며, 이 세 점으로 형식적인 수렴차수를 추정하지 않았다. Reference는 이미 검증한 S8 수치해이며 오차의 엄밀한 enclosure를 제공하지 않는다. 시간은 단일 실행의 환경별 진단값이다.

## 재사용하는 S6–S8 근거

S6 finite-d certificate, Python exact rank1 certificate, 고정 owner source-deposition spectral refinement 및 처방 기하 source-age 합성을 재사용한다. 원 G5 rate 38/344 실패와 P4 제약 44/238 악화는 그대로 보존했다. `5.369926725506957e-12`는 Simpson-32 기준 절단 오차와 1 ulp 변동으로 설명됐으며 source deposition 범위다.

S7의 manufactured donor–Einstein/shear 결합 및 native 제한 검증, S8의 birth-memory tangent 10/10 gate와 native 18 attempt/17 measured를 재사용한다. S8 n256의 6개 target 통과, 낮은 해상도 8개 목표 미달, STRICT_INTERIOR 지지의 `INNER_P2_PRECISION_LIMIT` 1개를 구분한다. 과거 직렬화·정밀도·support·exact-moment 실패는 각 원 receipt에 남는다.

## 다음 연구와 고정 조건

다음 작업은 실제 MD14 공급부를 연결할 때의 source time·stress·energy bridge와 native Einstein/shear feedback이다. 물리/공변 체적, 시간 변수, 방출·흡수 및 에너지 공급 소유권과 응력 정규화를 먼저 명시하고, 실제 native owner 반환을 보존식과 연결할 새 입력·코드·gate를 완성한다. P6 제약 알고리즘은 미구현이며 full reactive spectral/history 수렴, native finite-bin photon/energy 보존, 새 client의 full parameter tangent도 미완료다.

Non-tilted axisymmetric Bianchi I, (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H를 유지한다. 새 명시적 isotropic birth quadrature만 보정하고 기존 photon·physical anisotropic stock을 초기화하거나 재가중하지 않는다. 양의 weights, birth weights, reflection parity, source frame, REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`를 유지한다. 실패를 음수 weights나 gate 완화로 우회하지 않는다.

새 NCP 캠페인이 필요할 때는 여기에서 source·입력·gate를 먼저 완성하고 새 실행에 필요한 컴파일·작은 호환 수정·실행만 남긴다. 기존 owner 작업과 실행 중 job을 보존하며 추가 worker≤16, RAM≤16 GiB, disk≤4 GiB, 개별 job≤1800초를 적용한다. REI production/full EoR/merge는 별도의 충분한 검증을 필요로 한다.

## 현재 사용자 추가 요청 — 최적화 연구

2026-10-20부터 [S10 최적화 계약과 단계 기록](S10_OPTIMIZATION_KO.md)에 따라 외부 문헌/코드 재사용, allocation/cache/SIMD/병렬화 설계·구현과 정확도 대비 성능을 조사한다. 이전 실제 MD14 physical closure의 의무는 남겨둔다. S9 결과 archive는 Dropbox에서 전체 원격 ZIP·SHA/CRC/manifest123개를 검증했고, Drive 업로드/readback은 아직 미완료다. [현재 부분 배송 영수증](delivery/s9/S9_STAGE1_CLOUD_READBACK.json)을 확인한다.
